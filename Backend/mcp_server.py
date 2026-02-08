# server.py
from fastmcp import FastMCP
from langsmith import traceable

# Import your clean functions
from tools import collect_geomaterials, collect_localities, pandas_hist_plot, network_plot, heatmap_plot
# from tools.visualization import generate_visualization  # Future import

# 1. Initialize the Server
mcp = FastMCP("Mindat Master Server")

# 2. Add Tracing (Optional but recommended for debugging)
# Wrap the tool functions with langsmith tracing before adding them if desired
# collect_geomaterials = traceable(collect_geomaterials) 
# collect_localities = traceable(collect_localities)

# 3. Register the Tools
# FastMCP automatically reads the docstrings and type hints!
mcp.add_tool(collect_geomaterials)
mcp.add_tool(collect_localities)
mcp.add_tool(network_plot)
mcp.add_tool(pandas_hist_plot)
mcp.add_tool(heatmap_plot)

# 4. Run the Server
if __name__ == "__main__":
    mcp.run(
        transport="http", 
        host="0.0.0.0", 
        port=8005,
    )