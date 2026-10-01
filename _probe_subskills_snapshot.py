import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
SNAP = Path(r"C:\swprojects\sw-skill-fork\apps\workbench-ui\src-tauri\resources\skill")

print("  内嵌快照在不在: %s" % SNAP.is_dir())
if SNAP.is_dir():
    n = sum(1 for _ in SNAP.rglob("*") if _.is_file())
    print("  快照文件数: %d" % n)
    ssub = SNAP / "subskills"
    print("  快照里有 subskills/: %s" % ssub.is_dir())
    if ssub.is_dir():
        snap_dirs = sorted(d.name for d in ssub.iterdir() if d.is_dir())
    else:
        snap_dirs = []
    live_dirs = sorted(d.name for d in (ROOT / "subskills").iterdir() if d.is_dir())
    print()
    print("  源 subskills/ : %d %s" % (len(live_dirs), live_dirs))
    print("  快照 subskills: %d %s" % (len(snap_dirs), snap_dirs))
    miss = sorted(set(live_dirs) - set(snap_dirs))
    print()
    print("  ★ **源里有、快照里没有**（不会随包发布）: %d %s" % (len(miss), miss or ""))
    #: 逐目录比文件数
    for d in live_dirs:
        a = sum(1 for _ in (ROOT / "subskills" / d).rglob("*") if _.is_file())
        b = sum(1 for _ in (ssub / d).rglob("*") if _.is_file()) if ssub.is_dir() else 0
        print("    %-34s 源 %3d 文件 · 快照 %3d %s" % (d, a, b, "" if a == b else "⚠ 不一致"))
