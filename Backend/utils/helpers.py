from pathlib import Path
from config.mindat_config import MindatConfig
import os
from dotenv import load_dotenv
load_dotenv()


# check path for storing the samples files in directory folder
# Json files for the samples data will be saved in contents/sample_data
def check_sample_data_path() -> bool:
    current_dir = Path.cwd() # Get the current working directory
    parent_dir = current_dir.parent # Navigate to the parent directory
    sample_data_path = parent_dir / "contents" / "sample_data" # Construct the path to contents/sample_data
    if sample_data_path.exists():
        return True
    return False

def check_plots_path() -> bool:
    current_dir = Path.cwd() # Get the current working directory
    parent_dir = current_dir.parent # Navigate to the parent directory
    plots_path = parent_dir / "contents" / "plots" # Construct the path to contents/plots
    if plots_path.exists():
        return True
    return False

