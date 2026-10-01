import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
t = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py").read_text(encoding="utf-8")
i = t.find("def call_com_member")
print("── call_com_member ──")
print(t[i:i + 700])
