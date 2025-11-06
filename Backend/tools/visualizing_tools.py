
from ..models.plot_visualization_model import PandasDFInput
from langchain.tools import tool
from typing import Optional
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from ..models import PandasDFInput




# Directories
PARENT_DIR = Path(__file__).parent.resolve()
BASE_DATA_DIR = PARENT_DIR.parent.parent / "contents"



#####################################
# Histogram plotter tool
#####################################
@tool(
    "pandas_hist_plot_function",
    description=(
        "Create histogram plot from collected mineral data and save to plots directory.\n"
        "Input: { file_path: str, plot_title: Optional[str] }.\n"
        "Output: Success/failure message with plot file path."
    ),
    args_schema=PandasDFInput,  # using the predefined model : expects file_path and optional plot_title
    return_direct=False,
)
def pandas_hist_plot_function(file_path: str, plot_title: Optional[str] = None) -> str:
    try:
        plots_dir = BASE_DATA_DIR / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_json(file_path)

        if 'results' not in df.columns or df['results'].empty:
            return "Failed: No 'results' data found in the JSON file"

        df_normalized = pd.json_normalize(df['results'])

        if 'elements' not in df_normalized.columns:
            return "Failed: No 'elements' data found in the mineral records"

        df_exploded = df_normalized.explode('elements')
        df_exploded = df_exploded.dropna(subset=['elements'])

        if df_exploded.empty:
            return "Failed: No element data to plot"

        element_counts = df_exploded['elements'].value_counts()
        top_elements = element_counts.head(20)

        plt.figure(figsize=(12, 8))
        ax = top_elements.plot(kind='bar', color='skyblue', edgecolor='navy', alpha=0.7)

        ax.set_title(plot_title or "Top 20 Mineral Elements", fontsize=16)
        ax.set_xlabel("Elements", fontsize=14)
        ax.set_ylabel("Frequency", fontsize=14)
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_file_path = plots_dir / "mineral_elements_histogram.png"
        plt.savefig(plot_file_path)
        plt.close()

        return f"Success: Plot saved to {plot_file_path}"

    except Exception as e:
        return f"Failed to create histogram plot: {e}"