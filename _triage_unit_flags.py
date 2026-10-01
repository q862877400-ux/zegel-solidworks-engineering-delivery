import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\tools")
import re
ROOT = Path(r"C:\swprojects\sw-skill-fork")
LENGTH_WORDS = ("radius", "diameter", "depth", "thickness", "distance", "width", "height",
                "length", "offset", "spacing", "pitch", "cx", "cy", "cz", "dx", "dy", "dz",
                "x1", "y1", "z1", "x2", "y2", "z2", "x_mm", "y_mm", "z_mm", "size")

for stem in ("sw_costing", "sw_jlcfa_gui", "sw_jlcfa_select", "sw_view"):
    p = ROOT / "scripts" / (stem + ".py")
    text = p.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text)
    print("── %s" % stem)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        args = [a.arg for a in node.args.args]
        hit = [x for x in args
               if any(w == x.lower() or x.lower().endswith("_" + w) for w in LENGTH_WORDS)]
        if hit:
            doc = ast.get_docstring(node) or ""
            first = doc.strip().splitlines()[0] if doc.strip() else "(无 docstring)"
            print("    %-28s 形参=%s" % (node.name, args))
            print("        命中词=%s" % hit)
            print("        doc: %s" % first[:84])
    #: 文件里有没有"屏幕坐标"/"像素"之类字样
    for kw in ("屏幕", "像素", "pixel", "screen", "窗口"):
        if kw in text:
            print("    ⚑ 文件里出现 %r ⇒ 可能是**屏幕坐标**而非长度" % kw)
            break
    print()
