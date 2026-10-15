import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sw_sketch_edit.py").read_text(encoding="utf-8")
i = t.find("def create_sketch_chamfer")
print("── 仓库实现 ──")
print(t[i:i + 1400])
