import sys, os
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
B = Path(r"D:\SOLIDWORKS Data")
if not B.is_dir():
    print("  D:\\SOLIDWORKS Data 不存在"); raise SystemExit(1)
print("  存在:", B)
ver = B / "ToolboxVersion.dat"
if ver.is_file():
    print("  ToolboxVersion.dat:")
    for l in ver.read_text(encoding="utf-8", errors="replace").splitlines()[:6]:
        print("    " + l.strip())
br = B / "browser"
if br.is_dir():
    stds = sorted([d.name for d in br.iterdir() if d.is_dir()])
    print()
    print("  browser/ 下的标准目录 (%d 套):" % len(stds))
    print("    " + ", ".join(stds))
    n = sum(1 for _ in br.rglob("*.sldprt"))
    print()
    print("  全库 .sldprt 数量 =", n)
    print()
    print("  ★ 你问的三类，逐一实查：")
    for kw, label in (("ball screw","丝杆"), ("leadscrew","丝杆"),
                      ("linear","直线导轨"), ("rail","导轨"), ("guide","导轨")):
        hits = [str(p.relative_to(br)) for p in br.rglob("*.sldprt")
                if kw in p.name.lower()]
        print("    %-12s (%-6s) 命中 %d" % (label, kw, len(hits)))
    al = [str(p.relative_to(br)) for p in br.rglob("*.sldprt")
          if "aluminum" in str(p.parent).lower() or "aluminium" in str(p.parent).lower()]
    print("    铝型材       命中 %d  例: %s" % (len(al), al[0] if al else "-"))