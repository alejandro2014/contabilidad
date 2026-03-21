import os
import sys
from pathlib import Path

PROJECT_PATH = os.getcwd()

path = Path(PROJECT_PATH)

SOURCE_PATH = os.path.join(
    path.parent, "src"
)

sys.path = [str(path.parent)] + sys.path
