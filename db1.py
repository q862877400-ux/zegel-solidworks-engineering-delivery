import sys, zipfile
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
db = B / "DB.zip"
print("  DB.zip: %.1f MB" % (db.stat().st_size/1e6))
try:
    zf = zipfile.ZipFile(db)
except Exception as e:
    print("  打开失败:", e); raise SystemExit
names = zf.namelist()
print("  条目数:", len(names), " 是否加密:", any(i.flag_bits & 1 for i in zf.infolist()))
tops = sorted({n.split("/")[0] for n in names if n.strip()})
print("  顶层:", tops[:12])
ext = Counter(Path(n).suffix.lower() for n in names if not n.endswith("/"))
print("  扩展名:")
for e, c in ext.most_common(10): print("    %-12s %6d" % (e, c))
print()
print("  路径样本:")
for n in [x for x in names if not x.endswith("/")][:12]:
    print("    " + n[:96])