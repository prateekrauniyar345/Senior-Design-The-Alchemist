from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from Backend.models.visualization import EmailPlotRequest, PlotActionResponse, DownloadRequest
from Backend.services.plots_services import get_plot_path, convert_to_pdf, send_email_with_attachment, PLOTS_DIR  


router = APIRouter(prefix="/plots", tags=["plots"])

# ------------------------------
# Router Endpoints
# ------------------------------
@router.get("/download/{file_name}")
async def download_plot(file_name: str, format: str = "png"):
    """
    Download a plot file in the specified format (png or pdf).
    
    Args:
        file_name: Name of the plot file (e.g., "mineral_elements_histogram_20251207_120000.png")
        format: Output format - "png" (original) or "pdf" (converted)
    
    Returns:
        FileResponse with the requested file
    """
    file_path = get_plot_path(file_name)
    
    # If requesting PDF conversion
    if format.lower() == "pdf":
        if file_path.suffix.lower() == '.html':
            # For HTML files, return as-is
            return FileResponse(
                file_path,
                media_type="text/html",
                filename=f"{file_path.stem}.html"
            )
        else:
            # Convert PNG to PDF
            pdf_buffer = convert_to_pdf(file_path)
            return StreamingResponse(
                pdf_buffer,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={file_path.stem}.pdf"
                }
            )
    
    # Return original file
    media_type = "text/html" if file_path.suffix == '.html' else "image/png"
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=file_path.name
    )


@router.post("/email", response_model=PlotActionResponse)
async def email_plot(request: EmailPlotRequest, background_tasks: BackgroundTasks):
    """
    Email a plot file to the specified recipient.
    
    Args:
        request: EmailPlotRequest containing file_name, recipient_email, subject, and message
    
    Returns:
        PlotActionResponse indicating success or failure
    """
    try:
        file_path = get_plot_path(request.file_name)
        
        # Add email sending to background tasks
        background_tasks.add_task(
            send_email_with_attachment,
            recipient=request.recipient_email,
            subject=request.subject,
            body=request.message,
            attachment_path=file_path
        )
        
        return PlotActionResponse(
            success=True,
            message=f"Email will be sent to {request.recipient_email}",
            error=None
        )
        
    except HTTPException as e:
        return PlotActionResponse(
            success=False,
            message="Failed to send email",
            error=str(e.detail)
        )
    except Exception as e:
        return PlotActionResponse(
            success=False,
            message="Failed to send email",
            error=str(e)
        )


@router.get("/list")
async def list_plots():
    """
    List all available plot files.
    
    Returns:
        List of plot file names with metadata
    """
    try:
        if not PLOTS_DIR.exists():
            return {"plots": []}
        
        plots = []
        for file_path in PLOTS_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix in ['.png', '.html']:
                stat = file_path.stat()
                plots.append({
                    "name": file_path.name,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "type": file_path.suffix[1:],  # Remove the dot
                    "url": f"/contents/plots/{file_path.name}"
                })
        
        return {"plots": sorted(plots, key=lambda x: x['created'], reverse=True)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing plots: {str(e)}")
