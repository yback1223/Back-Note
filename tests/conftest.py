import sys
import pathlib

# Ensure project root is on sys.path for imports like `from core...` and `from repositories...`
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
