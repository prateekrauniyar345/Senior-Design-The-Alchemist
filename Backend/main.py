import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from .models import User, Message, Session, AgentOutput, AgentTask, DataArtifact, Visualization, AgentRun
from .routers import default_router, mindat_router, agent_router
from fastapi.middleware.cors import CORSMiddleware

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


# Include Routers
app.include_router(default_router, prefix="/api")
app.include_router(mindat_router, prefix="/api")
app.include_router(agent_router, prefix="/api")   


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allowing all origins for now. 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




if __name__ == "__main__":
    # uvicorn is used to run the FastAPI app
    import uvicorn 
    # run the app with reload option for development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
