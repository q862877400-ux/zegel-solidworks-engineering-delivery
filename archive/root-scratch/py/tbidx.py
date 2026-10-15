import sys, os
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
B = Path(r"D:\SOLIDWORKS Data")
idx = B / "browser" / "ToolboxFiles.index"
print("  ToolboxFiles.index:", idx, "存在=", idx.is_file(),
      "大小=", idx.stat().st_size if idx.is_file() else "-")
if idx.is_file():
    raw = idx.read_bytes()[:220]
    print("  头 40 字节:", raw[:40])
    print("  是否文本:", all(32 <= b < 127 or b in (10,13,9) for b in raw))
# 目录结构样本
br = B / "browser"
g = br / "GB" if (br/"GB").is_dir() else None
if g:
    print()
    print("  GB 标准下的一级目录（样本 12 个）:")
    subs = sorted([d for d in g.iterdir() if d.is_dir()])
    for d in subs[:12]:
        n = sum(1 for _ in d.rglob("*.sldprt"))
        print("    %-38s %4d 个" % (d.name, n))