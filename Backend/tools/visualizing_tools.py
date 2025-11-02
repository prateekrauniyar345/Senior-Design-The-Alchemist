from langchain.tools import StructuredTool
from ..collectors.plot_visualizations import pandas_hist_plot_function
from ..models.plot_visualization_model import PandasDFInput

pandas_plot = StructuredTool.from_function(
    func=pandas_hist_plot_function,
    name="pandas_plot",
    description="Create a histogram plot from a saved Mindat JSON file path. Returns the plot file path.",
    args_schema=PandasDFInput
)