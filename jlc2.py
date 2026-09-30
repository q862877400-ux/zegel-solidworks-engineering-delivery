import sys, zipfile, json, re
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1")
M = B / "ForFaceSelector" / "model"
zips = sorted(M.glob("*.zip"))
print("  model/ 下 zip:", len(zips))
other = [p for p in B.rglob("*.zip") if p.parent != M]
print("  其它位置的 zip:", len(other), "->", [str(p.relative_to(B))[:50] for p in other[:5]])
print()
print("  ★ 抽几个看内部文件名（能不能看出型号）:")
for z in zips[:6]:
    with zipfile.ZipFile(z) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        sz = sum(i.file_size for i in zf.infolist() if not i.is_dir())/1e6
        print("    %s.zip" % z.stem)
        for n in names[:3]:
            print("        %-70s %6.1f MB" % (n[:70], sz))
# 有没有非 model 位置的分类信息文件
print()
print("  ForFaceSelector 下的非模型文件:")
for p in sorted((B/"ForFaceSelector").iterdir()):
    if p.is_file(): print("    %-40s %8.1f MB" % (p.name, p.stat().st_size/1e6))