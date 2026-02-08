import os
from Backend.database import Base, engine
from Backend.core import create_app
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = create_app()


# CORS Middleware - Fix for credentials mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],  # Specific origins required when using credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




if __name__ == "__main__":
    # uvicorn is used to run the FastAPI app
    import uvicorn 
    # run the app with reload option for development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
