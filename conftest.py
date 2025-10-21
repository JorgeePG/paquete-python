import sys
from pathlib import Path

# Add src/t8-client to Python path
src_path = Path(__file__).parent / "src" / "t8-client"
sys.path.insert(0, str(src_path))
