import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
SNAP = ROOT / "apps" / "workbench-ui" / "src-tauri" / "resources" / "skill"

for d in sorted(x for x in (ROOT / "subskills").iterdir() if x.is_dir()):
    src = {str(p.relative_to(ROOT / "subskills")) for p in d.rglob("*") if p.is_file()}
    sd = SNAP / "subskills" / d.name
    dst = {str(p.relative_to(SNAP / "subskills")) for p in sd.rglob("*") if p.is_file()} if sd.is_dir() else set()
    miss = sorted(src - dst)
    extra = sorted(dst - src)
    if miss or extra:
        print("── %s" % d.name)
        for m in miss:
            print("    ✗ 源里有、快照无: %s" % m)
        for e in extra:
            print("    ⚠ 快照有、源里无: %s" % e)
