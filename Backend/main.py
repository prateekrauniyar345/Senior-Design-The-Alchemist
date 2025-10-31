import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from .models import User, Message, Session, AgentOutput, AgentTask, DataArtifact, Visualization, AgentRun

Base.metadata.create_all(bind=engine)

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
# @app.get("/")
# async def root(request: Request):
#     return ({
#         "message": "Welcome to the LLM-Driven Smart Agents API!", 
#         "documentation_url": "/docs", 
#         "status": "API is running smoothly."
        
#         })
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    html = f"""
    <html>
        <head>
            <title>Service Status</title>
        </head>
        <body style="font-family:Arial,sans-serif ; background-color: black; color: white; text-align: center; padding: 50px;">
            <h2>LLM-Driven Smart Agents API</h2>
            <p style="color:green">Status: <strong>Running</strong></p>
            <p>Version: {app.version}</p>
            <p>Documentation: <a href="/docs">/docs</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html)



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

if __name__ == "__main__":
    # uvicorn is used to run the FastAPI app
    import uvicorn 
    # run the app with reload option for development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
