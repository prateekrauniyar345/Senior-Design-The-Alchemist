import os
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import from our Backend package
from .api import get_geomaterial_api
from .utils import MindatAPIException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
        title="LLM-Driven Smart Agents for User-Friendly Access to an Open Data Portal", 
        description="A FastAPI application with Agentic Capabilities to facilitate user-friendly access to an open data portal using Large Language Models(GPT-4o).",
        version="0.0.1"
    )

# Mount the Static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# templates directory for rendering HTML files
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# default route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# about route
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


# privacy policy route
@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

# terms of service route
@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    return templates.TemplateResponse("terms_of_service.html", {"request": request})



@app.get("/api/mindat/geomaterials")
async def test_mindat_search(
    ima: str = Query(..., description="Search query for minerals"),
    
):
    """Test Mindat API search functionality"""
    print( "Received search request:", ima)
    try:
        geo_api = get_geomaterial_api()
        
        # Create simple test params (you'll need to adjust based on your model)
        test_params = {"ima": ima}
        print("Using test params:", test_params)
        response = geo_api.client.get_data_from_api(geo_api.endpoint, test_params)
        
        return {
            "success": True,
            "query": ima,
            "total_results": response.get("count", 0),
            "results": response.get("results", [])
        }
        
    except MindatAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")




if __name__ == "__main__":
    # uvicorn is used to run the FastAPI app
    import uvicorn 
    # run the app with reload option for development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
