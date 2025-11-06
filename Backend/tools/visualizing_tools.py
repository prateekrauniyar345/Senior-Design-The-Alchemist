import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from langchain.tools import tool
from datetime import datetime
from ..models.plot_visualization_model import PandasDFInput
import json  

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

# Define directories
ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = ROOT / "contents" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

@tool
def pandas_hist_plot(file_path: str, plot_title: str = None) -> str:
    """
    Creates a histogram plot showing element distribution from mineral data.
    
    Args:
        file_path: Path to the JSON file containing mineral data
        plot_title: Optional custom title for the plot
        
    Returns:
        Success message with plot file path or error message
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check if 'results' key exists
        if 'results' not in data:
            return f"Error: 'results' key not found in {file_path}"
        
        # Create DataFrame from the 'results' array
        df = pd.DataFrame(data['results'])
        
        if df.empty:
            return "Error: The data file is empty."
        
        # Check if 'elements' column exists
        if 'elements' not in df.columns:
            return f"Error: 'elements' column not found in data. Available columns: {list(df.columns)}"
        
        # Flatten the list of elements and count occurrences
        all_elements = []
        for elements_list in df['elements']:
            if isinstance(elements_list, list):
                all_elements.extend(elements_list)
        
        if not all_elements:
            return "Error: No elements found in the data."
        
        # Count element frequencies
        element_counts = pd.Series(all_elements).value_counts()
        
        # Take top 20 elements
        top_elements = element_counts.head(20)
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        bars = plt.bar(range(len(top_elements)), top_elements.values, 
                      color='steelblue', edgecolor='black')
        
        # Customize the plot
        plt.xlabel('Elements', fontsize=14, fontweight='bold')
        plt.ylabel('Frequency', fontsize=14, fontweight='bold')
        
        # Set title
        if plot_title:
            plt.title(plot_title, fontsize=16, fontweight='bold', pad=20)
        else:
            plt.title('Top 20 Elements Distribution in Mineral Dataset', 
                     fontsize=16, fontweight='bold', pad=20)
        
        plt.xticks(range(len(top_elements)), top_elements.index, 
                  rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on top of bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"mineral_elements_histogram_{timestamp}.png"
        plot_path = PLOTS_DIR / plot_filename
        
        # Save the plot
        plt.savefig(plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return f"Success: Histogram created and saved to {plot_path}"
        
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in {file_path}: {str(e)}"
    except Exception as e:
        return f"Error creating histogram: {str(e)}"