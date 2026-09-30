import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
D = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector\ForFaceSelectorData\DB")
for p in sorted(D.iterdir()):
    if p.is_dir(): continue
    with p.open("rb") as f: head = f.read(48)
    print("  %-28s %10.1f MB  头: %r" % (p.name, p.stat().st_size/1e6, head[:24]))
    if head[:15] == b"SQLite format 3":
        print("       -> ★ SQLite 数据库，可直接用 sqlite3 读")