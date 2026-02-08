# Backend/mcp_server.py
import sys
import os

# Add the parent directory to sys.path to allow imports from the Backend package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from Backend.tools import collect_geomaterials, collect_localities, network_plot, histogram_plot, heatmap_plot


# Initialize the Server
mcp = FastMCP("Mindat Master Server")


# Register the Tools
mcp.tool(collect_geomaterials)
mcp.tool(collect_localities)
mcp.tool(network_plot.func)
mcp.tool(histogram_plot.func)
mcp.tool(heatmap_plot.func)

# Run the Server
if __name__ == "__main__":
    mcp.run(
        transport="http", 
        host="0.0.0.0", 
        port=8005,
    )