import os
from fastapi.templating import Jinja2Templates

# Get Backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create templates instance
templates = Jinja2Templates(directory=os.path.join(BACKEND_DIR, "templates"))

def get_templates():
    """Get templates instance"""
    return templates