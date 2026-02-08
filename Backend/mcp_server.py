# Backend/mcp_server.py
from fastmcp import FastMCP
from langsmith import traceable
from tools import collect_geomaterials, collect_localities, network_plot, histogram_plot, heatmap_plot


# Initialize the Server
mcp = FastMCP("Mindat Master Server")

# Adding Tracing 
# Wrap the tool functions with langsmith tracing before adding them if desired
# collect_geomaterials = traceable(collect_geomaterials) 
# collect_localities = traceable(collect_localities)
# network_plot = traceable(network_plot)
# histogram_plot = traceable(histogram_plot)
# heatmap_plot = traceable(heatmap_plot)


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