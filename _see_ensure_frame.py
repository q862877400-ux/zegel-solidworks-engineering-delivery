import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
i = t.find("def ensure_gtol_frame")
j = t.find("\ndef ", i + 1)
print("  ── ensure_gtol_frame 现状 ──")
print(t[i:j if j > 0 else len(t)])
