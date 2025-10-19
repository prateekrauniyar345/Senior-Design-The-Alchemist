from langchain.tools import StructuredTool
from ..collectors.plot_visualizations import pandas_plot_function
from ..models.plot_visualization_model import PandasDFInput

pandas_plot = StructuredTool.from_function(
    func=pandas_plot_function,
    name="PandasPlot",
    description="useful for plotting the element distributions of the mineral data.",
    args_schema=PandasDFInput
)