import json
from pathlib import Path
import getpass

path = Path("_charly_secrets/charly_users.json")
data = json.loads(path.read_text(encoding="utf-8"))

system_user = getpass.getuser()

print("System user:", system_user)
print("Keys in charly_users.json:", list(data.keys()))

if system_user in data:
    print("✅ MATCH OK")
    print("Username usado para API:", data[system_user]["username"])
else:
    print("❌ NO MATCH")