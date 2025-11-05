# import pandas as pd
# # Set matplotlib to use non-interactive backend before importing pyplot
# # This is critical for running matplotlib in threads/async contexts
# import matplotlib
# matplotlib.use('Agg')  # Use Anti-Grain Geometry (AGG) backend - no GUI required
# import matplotlib.pyplot as plt
# from pathlib import Path
# import logging
# from typing import Optional
# import json

# # Setup logging
# logger = logging.getLogger(__name__)

# # Get paths properly
# HERE = Path(__file__).resolve()
# ROOT = HERE.parents[1]  # Backend directory
# PLOTS_DIR = ROOT / "contents" / "plots"

# def pandas_hist_plot_function(file_path: str, plot_title: Optional[str] = None) -> str:
#     """
#     Create histogram plot from collected mineral data and save to plots directory
    
#     Args:
#         file_path: Path to the JSON file containing mineral data
#         plot_title: Optional custom title for the plot
        
#     Returns:
#         str: Success/failure message with plot file path
#     """
#     try:
#         # Ensure plots directory exists
#         PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        
#         # Read the JSON data
#         df = pd.read_json(file_path)
        
#         if 'results' not in df.columns or df['results'].empty:
#             return "Failed: No 'results' data found in the JSON file"
        
#         # Normalize the nested JSON structure
#         df_normalized = pd.json_normalize(df['results'])
        
#         if 'elements' not in df_normalized.columns:
#             return "Failed: No 'elements' data found in the mineral records"
        
#         # Explode the DataFrame to have each element on a separate row
#         df_exploded = df_normalized.explode('elements')
        
#         # Remove null values
#         df_exploded = df_exploded.dropna(subset=['elements'])
        
#         if df_exploded.empty:
#             return "Failed: No element data to plot"
        
#         # Count the frequency of each element
#         element_counts = df_exploded['elements'].value_counts()
        
#         # Select the top 20 elements for better visualization
#         top_elements = element_counts.head(20)
        
#         # Create the plot
#         plt.figure(figsize=(12, 8))
#         # plot the bar plot
#         ax = top_elements.plot(kind='bar', color='skyblue', edgecolor='navy', alpha=0.7)
        
#         # Customize the plot
#         title = plot_title or 'Top 20 Elements Distribution in Minerals'
#         plt.title(title, fontsize=16, fontweight='bold', pad=20)
#         plt.xlabel('Chemical Elements', fontsize=12, fontweight='bold')
#         plt.ylabel('Frequency Count', fontsize=12, fontweight='bold')
#         plt.xticks(rotation=45, ha='right')
#         plt.grid(axis='y', alpha=0.3)
        
#         # Add value labels on top of bars
#         for i, v in enumerate(top_elements.values):
#             ax.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
        
#         plt.tight_layout()
        
#         # Save the plot
#         plot_filename = f"elements_histogram_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png"
#         plot_path = PLOTS_DIR / plot_filename
        
#         plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
#         plt.close()  # Close the figure to free memory
        
#         logger.info(f"Successfully created plot: {plot_path}")
        
#         return f"Success: Plot saved to {plot_path}. Found {len(element_counts)} unique elements, showing top 20."
        
#     except FileNotFoundError:
#         error_msg = f"Failed: Data file not found at {file_path}"
#         logger.error(error_msg)
#         return error_msg
#     except json.JSONDecodeError:
#         error_msg = f"Failed: Invalid JSON format in {file_path}"
#         logger.error(error_msg)
#         return error_msg
#     except Exception as e:
#         error_msg = f"Failed to create plot: {str(e)}"
#         logger.error(error_msg)
#         return error_msg
