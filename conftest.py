import sys
from pathlib import Path

# Agregar src/t8-client al Python path
src_path = Path(__file__).parent / "src" / "t8-client"
sys.path.insert(0, str(src_path))
