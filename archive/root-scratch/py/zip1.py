import sys, zipfile, io
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
z = Path(r"C:\Users\Zegel\Downloads\嘉立创FA零件库插件纯净版-v2.4.0-20260819-4.zip")
print("  zip:", z.name, "%.0f MB" % (z.stat().st_size/1e6))
zf = zipfile.ZipFile(z)
names = zf.namelist()
print("  条目数:", len(names))
tops = sorted({n.split("/")[0] for n in names if n.strip()})
print("  顶层:", tops[:10])
ext = Counter(Path(n).suffix.lower() for n in names if not n.endswith("/"))
print("  扩展名 top:")
for e, c in ext.most_common(12):
    print("    %-10s %6d" % (e, c))
print()
print("  路径样本:")
for n in [x for x in names if not x.endswith("/")][:10]:
    print("    " + n[:96])