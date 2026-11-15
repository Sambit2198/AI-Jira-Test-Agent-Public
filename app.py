
import sys
import runpy
from pathlib import Path

# Add the project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Launch the existing Streamlit application.
APP_FILE = PROJECT_ROOT / "web_app" / "app.py"

runpy.run_path(
    str(APP_FILE),
    run_name="__main__"
)
