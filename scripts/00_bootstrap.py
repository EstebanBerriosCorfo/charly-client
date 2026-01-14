import sys
from pathlib import Path

# ⬇️ Fuerza la carpeta donde están core/, services/, orchestration/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("PROJECT_ROOT =", PROJECT_ROOT)
print("sys.path[0]  =", sys.path[0])

from orchestration.bootstrap import Bootstrap
from pathlib import Path
from pprint import pprint

ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()
    
print("=== BOOTSTRAP OK ===")
print("System user:", ctx["system_user"])
print("Charly user:", ctx["current_user"]["email"])
print("Companies:")
pprint(ctx["current_user"]["companies"])