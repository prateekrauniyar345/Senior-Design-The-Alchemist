# Backend/mcp_server.py
import sys
import os

# Add the parent directory to sys.path to allow imports from the app package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print("file is : ", sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from app.tools import (
    collect_geomaterials,
    collect_localities,
    profile_sample_data
)


# Initialize the Server
mcp = FastMCP("Mindat Master Server")


# Register the Tools
mcp.tool(collect_geomaterials)
mcp.tool(collect_localities)
mcp.tool(profile_sample_data)

# Run the Server
if __name__ == "__main__":
    mcp.run(
        transport="http", 
        host="0.0.0.0", 
        port=8010,
    )