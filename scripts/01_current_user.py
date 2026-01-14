import sys
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.bootstrap import Bootstrap

ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

print("\n=== CURRENT USER ===")
pprint(ctx["current_user"])