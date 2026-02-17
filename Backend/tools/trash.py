from pathlib import Path

# Directories
PARENT_DIR = Path(__file__).parent.resolve()
print("Parent directory of geomaterial tool:\n", PARENT_DIR)
BASE_DATA_DIR = PARENT_DIR.parent / "contents" # Adjusted to point to Backend/contents
print("Base data directory for geomaterial tool:\n", BASE_DATA_DIR)

CONTENTS_DIR = Path(__file__).resolve().parents[1] / "contents"
print("Contents directory in helpers.py is: \n", CONTENTS_DIR)