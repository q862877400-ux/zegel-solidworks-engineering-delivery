import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOTS = [Path(r"C:\swprojects\sw-skill-fork"), Path(r"D:\AI\SW\docs")]
PAT = re.compile(r"get_\*|get_\* 系列|全都返回数值数组|都是数值数组", re.I)
for root in ROOTS:
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in (".py", ".md", ".yaml", ".json", ".txt"):
            continue
        if any(x in p.parts for x in (".git", "node_modules", "__pycache__", "resources")):
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, l in enumerate(t.splitlines(), 1):
            if PAT.search(l) and "数值数组" in l:
                print("  %-52s L%-5d %s" % (str(p)[-52:], i, l.strip()[:96]))
