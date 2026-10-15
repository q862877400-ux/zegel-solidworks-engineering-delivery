"""★ 给那 15 个漏了 `inject` 的 ToolSpec 补上（★ 显式清单，不用遍历）。"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\mcp-server")
#: ★ **显式清单**（★ 与本轮扫描的输出一一对应 —— 事实 61：不拿遍历当清单）
TARGETS = [
    "solidworks_drawing_list_sheets", "solidworks_drawing_get_current_sheet",
    "solidworks_drawing_list_views", "solidworks_custom_property_get",
    "solidworks_custom_property_list", "solidworks_sketch_start", "solidworks_sketch_end",
    "solidworks_sketch_add_line", "solidworks_sketch_add_circle",
    "solidworks_sketch_add_rectangle", "solidworks_extrude_boss", "solidworks_extrude_cut",
    "solidworks_extrude_midplane", "solidworks_chamfer", "solidworks_fillet",
]
NOTE = ("        #: ★ 2026-10-03\uff08\u8f6e 461\uff09**\u8865\u6f0f\u6389\u7684 inject** \u2014\u2014 "
        "\u771f\u673a\u8bc1\u636e\uff1a\u672a\u58f0\u660e\u6ce8\u5165\u65f6\u5305\u88c5\u62ff\u5230 0 \u4e2a\u5b9e\u53c2 \u21d2\n"
        "        #:   `TypeError: \u2026 missing 1 required positional argument: 'model'`\u3002"
        "\u540c\u65cf `solidworks_part_bounding_box` \u5199\u7740 `inject='model'` \u2713")

fixed, skipped = [], []
for t in TARGETS:
    hit = None
    for p in sorted(R.glob("tool_specs_batch*.py")):
        src = p.read_text(encoding="utf-8")
        if '"%s"' % t in src or "'%s'" % t in src:
            hit = p
            break
    if hit is None:
        skipped.append((t, "找不到 decl"))
        continue
    src = hit.read_text(encoding="utf-8")
    #: \u2605 \u5728\u8be5 spec \u7684 `function=` \u884c\u4e4b\u540e\u63d2 `inject="model",`
    m = re.search(r'(name="%s",.*?\n)(\s*)(module=.*?function="[^"]+",\n)' % re.escape(t), src, re.S)
    if not m:
        skipped.append((t, "没匹配到 name/function 块"))
        continue
    if 'inject=' in m.group(0):
        skipped.append((t, "已经有 inject"))
        continue
    indent = m.group(2)
    ins = m.group(1) + m.group(2) if False else m.group(1)
    #: \u2605 \u5b9e\u9645\u63d2\u5728 function \u884c\u4e4b\u540e
    start, end = m.span(3)
    new = src[:end] + indent + 'inject="model",\n' + NOTE + "\n" + src[end:]
    try:
        compile(new, str(hit), "exec")
    except SyntaxError as e:
        skipped.append((t, "语法坏: %s" % e))
        continue
    hit.write_text(new, encoding="utf-8")
    fixed.append((t, hit.name))

print("  \u2605 \u5df2\u8865 inject\uff1a**%d** \u4e2a" % len(fixed))
for t, f in fixed:
    print("      %-50s %s" % (t, f))
if skipped:
    print("  \u2605 \u8df3\u8fc7\uff1a%d" % len(skipped))
    for t, why in skipped:
        print("      %-50s %s" % (t, why))
#: \u2605 \u56de\u8bfb\uff08\u4e8b\u5b9e 48 \u5b9a\u5219\u2461\uff09
import importlib
sys.path.insert(0, str(R))
import register_capabilities as RC
importlib.reload(RC)
have = {s.name for s in RC.all_specs() if (getattr(s, "inject", "") or "") == "model"}
print("  \u56de\u8bfb\uff1a\u73b0\u5728 inject='model' \u7684\u5171 **%d** \u4e2a\uff1b15 \u4e2a\u76ee\u6807\u90fd\u5728\uff1a%s" % (
    len(have), all(t in have for t in TARGETS)))
