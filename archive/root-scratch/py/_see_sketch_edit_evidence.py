import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\output\sketch-edit-evidence.json")
if p.is_file():
    d = json.loads(p.read_text(encoding="utf-8"))
    print("  顶层键: %s" % list(d.keys()))
    for k, v in (d.get("checks") or {}).items():
        ok = v.get("ok") if isinstance(v, dict) else v
        det = v.get("detail") if isinstance(v, dict) else ""
        print("   %s %-46s %s" % ("✓" if ok else "**✗**", k[:46], str(det)[:80]))
    print()
    print("  verdict = %s · passed = %s/%s" % (d.get("verdict"), d.get("passed"), d.get("total")))
else:
    print("  ⚠ 证据文件不在: %s" % p)
    print("  ⇒ 候选位置:")
    for f in sorted(Path(r"D:\AI\SW\output").glob("*sketch*")):
        print("     %s" % f.name)
