import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import Base, engine
from .models import User, Message, Session, AgentOutput, AgentTask, DataArtifact, Visualization, AgentRun
from .core import create_app
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = create_app()

# templates directory for rendering HTML files
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

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
