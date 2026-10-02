import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\docs\gate-classification.json")
d = json.loads(p.read_text(encoding="utf-8"))
lst = d["classification"]
if any(it.get("runner") == "_run_undefined_names_gate" for it in lst):
    print("already")
else:
    lst.append({
        "gate": "check_undefined_names.py",
        "runner": "_run_undefined_names_gate",
        "kind": "hard",
        "reason": (
            "**\u786c\u95e8\u7981**\uff1a\u5224\u300c\u4e00\u4e2a\u540d\u5b57\u5728**\u6574\u4e2a\u6587\u4ef6\u91cc\u4ece\u672a\u88ab\u7ed1\u5b9a**\u300d"
            "\u800c\u5b83**\u5728\u8fd9\u91cc\u88ab\u8bfb\u53d6** \u21d2 **NameError \u9690\u60a3**\u3002"
            "\u2605\u2605 \u4e0e\u8bed\u6cd5\u95e8\u7981**\u4e92\u8865**\uff1a\u540e\u8005\u53ea\u5224\u201c\u80fd\u4e0d\u80fd `ast.parse`\u201d\uff0c"
            "\u672c\u9053\u5224\u201c\u8bfb\u5230\u7684\u540d\u5b57\u6709\u6ca1\u6709\u88ab\u7ed1\u5b9a\u8fc7\u201d\u3002"
            "\u2605 \u89e6\u53d1\u5b83\u7684\u662f**\u8f6e 403 \u771f\u673a\u6293\u5230\u7684\u771f bug**\uff1a`export_to_image` \u91cc\u7528\u4e86 "
            "`out_i4()` \u800c `sw_export.py` **\u6f0f\u4e86\u5bfc\u5165** \u21d2 \u4e00\u8c03\u5c31 "
            "`NameError: name 'out_i4' is not defined`\uff08\u2605 \u800c**\u5f53\u65f6 19 \u9053\u95e8\u7981\u5168\u7eff**\uff09\u3002"
            "\u2605\u2605 \u672c\u9053**\u7b2c\u4e00\u6b21\u8dd1\u5c31\u6293\u5230 31 \u5904**\uff087 \u4e2a\u540d\u5b57 / 23 \u4e2a\u6587\u4ef6\uff09\uff0c"
            "\u5176\u4e2d `dismiss_residual_dialogs` **21 \u5904**\uff088 \u4e2a tools \u6587\u4ef6\u6ca1\u5bfc\u5165\u5c31\u7528\uff09\u00b7 "
            "`time` 3 \u5904 \u00b7 `SW_PID` 1 \u5904 \u2014\u2014 \u2605 \u5168\u662f\u540c\u4e00\u79cd\u5f62\u6001\uff1a**\u6539\u540d\u4e4b\u540e\u6ca1\u8ddf\u7740\u6539**\u3002"
            "\u26a0 \u5b83\u7528**\u4fdd\u5b88\u5224\u636e**\uff08\u5224\u201c\u6574\u4e2a\u6587\u4ef6\u90fd\u6ca1\u7ed1\u5b9a\u8fc7\u201d\uff09\u21d2 \u5b81\u53ef\u6f0f\u3001\u4e0d\u8981\u566a\u97f3\uff1b"
            "\u201c\u8fd0\u884c\u671f\u52a8\u6001\u6ce8\u5165\u5168\u5c40\u201d\uff08`globals().update(...)`\uff09\u4e0e `import *` \u7684\u6587\u4ef6**\u6574\u4efd\u8df3\u8fc7**"
            "\uff08\u771f\u4f8b\uff1a`mcp-server/server.py` \u7684 `globals().update(exports)` \u2014\u2014 \u4e0d\u8df3\u8fc7\u4f1a\u5728\u90a3\u4e00\u4e2a\u6587\u4ef6\u4e0a"
            "\u5047\u9633\u6027 **300+ \u5904**\uff09\u3002"
            "\u2605 \u5df2\u767b\u8bb0\u635f\u574f\uff08\u2605 WARN \u4e0d\u62e6\uff09\uff1a`scripts/sw_selection_tx.py`\u3002"
        ),
    })
    d["classification"] = lst
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\u5df2\u767b\u8bb0\u5206\u7c7b\uff1a\u73b0 %d \u6761" % len(lst))
