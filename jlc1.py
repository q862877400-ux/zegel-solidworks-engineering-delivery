import sys, zipfile, io
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1")
zips = sorted(B.rglob("*.zip"))
print("  zip 总数:", len(zips))
print("  路径样本:")
for z in zips[:5]:
    print("    " + str(z.relative_to(B))[:100])
print()
ext = Counter(); total = 0; sizes = []
for z in zips[:400]:
    try:
        with zipfile.ZipFile(z) as zf:
            for i in zf.infolist():
                if i.is_dir(): continue
                ext[Path(i.filename).suffix.lower()] += 1
                total += 1; sizes.append(i.file_size)
    except Exception as e:
        ext["<无法打开>"] += 1
print("  抽 400 个 zip，内部共 %d 个文件，合计 %.1f MB" % (total, sum(sizes)/1e6))
print("  内部扩展名:")
for e, c in ext.most_common(12):
    print("    %-14s %6d" % (e, c))