import sys, re, json, subprocess
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\_tmp_mcp")
T.mkdir(exist_ok=True)
r = subprocess.run(["gh","api","repos/andrewbartels1/SolidworksMCP-python/git/trees/HEAD?recursive=1"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
try:
    tree = json.loads(r.stdout)["tree"]
except Exception as e:
    print("  拉树失败:", r.stdout[:200]); raise SystemExit(1)
py = [t["path"] for t in tree if t["path"].endswith((".py",".md")) and t.get("size",0) > 0]
print("  文件数: %d（.py/.md）" % len(py))
big = sorted([t for t in tree if t["path"].endswith(".py")], key=lambda t: -(t.get("size",0)))[:12]
for t in big:
    print("    %-58s %6d bytes" % (t["path"], t.get("size",0)))