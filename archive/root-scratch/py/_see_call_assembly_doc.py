import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sw_assembly_doc.py").read_text(encoding="utf-8")
i = t.find("def call_assembly_doc")
print("── call_assembly_doc 的契约 ──")
print(t[i:i + 1500])
