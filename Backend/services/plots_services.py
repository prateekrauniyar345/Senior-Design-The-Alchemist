from pathlib import Path
import os
import json
from fastapi import HTTPException
from Backend.services.mindat_endpoints_services import get_locality_api
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from Backend.utils.helpers import CONTENTS_DIR


PLOTS_DIR = CONTENTS_DIR / "plots"



def get_plot_path(file_name: str) -> Path:
    """
    Get the full path to a plot file.
    Validates that the file exists and is within the plots directory.
    """
    # Remove any directory traversal attempts
    safe_name = os.path.basename(file_name)
    file_path = PLOTS_DIR / safe_name
    
    # Check if file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Plot file not found: {safe_name}")
    
    # Ensure file is within plots directory (security check)
    if not str(file_path.resolve()).startswith(str(PLOTS_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return file_path


def convert_to_pdf(image_path: Path) -> io.BytesIO:
    """
    Convert PNG/HTML image to PDF format.
    For HTML files (heatmaps), we'll return them as-is since they're interactive.
    """
    # If it's already an HTML file (heatmap), we can't convert to PDF easily
    if image_path.suffix.lower() == '.html':
        raise HTTPException(
            status_code=400, 
            detail="HTML heatmaps cannot be converted to PDF. Please download as HTML instead."
        )
    
    # Open the image
    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Calculate PDF page size based on image aspect ratio
        aspect_ratio = img_height / img_width
        
        # Use A4 landscape for wide images, portrait for tall images
        if aspect_ratio < 1:  # Wide image
            page_width, page_height = A4[1], A4[0]  # Landscape
        else:  # Tall image
            page_width, page_height = A4
        
        # Create PDF in memory
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
        
        # Calculate scaling to fit image on page with margins
        margin = 36  # 0.5 inch margin
        available_width = page_width - (2 * margin)
        available_height = page_height - (2 * margin)
        
        # Scale image to fit
        scale = min(available_width / img_width, available_height / img_height)
        new_width = img_width * scale
        new_height = img_height * scale
        
        # Center image on page
        x = (page_width - new_width) / 2
        y = (page_height - new_height) / 2
        
        # Draw image
        c.drawImage(ImageReader(img), x, y, width=new_width, height=new_height)
        
        # Add title at the top
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(page_width / 2, page_height - margin / 2, 
                          f"Mineral Data Visualization - {image_path.stem}")
        
        c.save()
        pdf_buffer.seek(0)
        
        return pdf_buffer
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting to PDF: {str(e)}")


async def send_email_with_attachment(
    recipient: str,
    subject: str,
    body: str,
    attachment_path: Path
):
    """
    Send email with plot attachment using SMTP.
    """
    # Get SMTP settings from environment
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SMTP_FROM_EMAIL", smtp_user)
    
    if not smtp_user or not smtp_password:
        raise HTTPException(
            status_code=500,
            detail="Email service not configured. Please set SMTP_USER and SMTP_PASSWORD environment variables."
        )
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Add attachment
    try:
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={attachment_path.name}'
            )
            msg.attach(part)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading attachment: {str(e)}")
    
    # Send email
    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

