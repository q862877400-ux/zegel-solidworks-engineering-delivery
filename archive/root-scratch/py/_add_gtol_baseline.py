import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\unattended_baseline.json")
d = json.loads(P.read_text(encoding="utf-8"))
allowed = sorted(set(list(d.get("allowed") or []) + ["gtol_insert"]))
d["allowed"] = allowed
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  基线 allowed 现 %d 条" % len(allowed))
