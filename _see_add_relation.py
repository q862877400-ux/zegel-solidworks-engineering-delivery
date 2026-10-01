import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sketch_relations.py").read_text(encoding="utf-8")
for m in re.finditer(r"(?m)^def (add_relation|list_relations|collect_relation_evidence)\s*\(([^)]*)\)", t):
    print("  %s(%s)" % (m.group(1), " ".join(m.group(2).split())[:120]))
print()
i = t.find("def add_relation")
print(t[i:i + 1100])
