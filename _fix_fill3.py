import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface_features.py")
src = p.read_text(encoding="utf-8")

OLD = """    if _declarative:
        from .sw_selection_spec import resolve_selection
        try:
            _selected_readback = int(resolve_selection(model, str(selection), "EDGE",
                                                       body_index=-1))
        except Exception as exc:                                   # noqa: BLE001
            return {"ok": False, "stage": "resolve_selection",
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        if _selected_readback <= 0:
            return {"ok": False, "stage": "resolve_selection", "selected": _selected_readback,
                    "error": "\u58f0\u660e\u5f0f\u9009\u62e9\u56de\u8bfb\u8ba1\u6570\u4e3a 0\uff08\u2605 \u4e8b\u5b9e 8\uff1a\u8bf7\u4ee5\u8ba1\u6570\u4e3a\u51c6\uff09"}"""
NEW = """    if _declarative:
        #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 435\uff09**\u4e0d\u91cd\u9009** \u2014\u2014 \u800c\u4ee3\u4ef7\u662f\u4e00\u6761**\u6587\u6863\u5316\u7684\u5951\u7ea6**\u3002
        #:   \u2605 \u4e0a\u4e00\u7248\u8d70 `resolve_selection`\uff08\u2605 \u5b83\u4f1a**\u91cd\u9009**\uff09\uff0c\u2605 \u800c\u5b83\u8d70\u7684\u662f
        #:     `IEntity.Select4` \u2014\u2014 \u2605\u2605 **\u800c `Select4` \u6ca1\u6709 mark \u53c2\u6570**\uff08**\u4e8b\u5b9e 32**\uff09
        #:     \u21d2 \u91cd\u9009\u540e mark \u53d8\u6210 **0**\uff0c\u2605 \u800c\u586b\u5145\u8981 **1**\uff08`MARK_BOUNDARY`\uff0c\u5b98\u65b9 Remarks\uff09
        #:     \u21d2 \u2605 \u771f\u673a\uff1a\u9009\u4e2d\u4e86 4 \u6761\u800c\u586b\u5145\u4ecd\u4e0d\u6210\uff08\u6811 `[7, 7]`\uff09\u3002
        #:   \u2605\u2605 **\u6b63\u89e3**\uff1a\u2605 **\u5c0a\u91cd\u8c03\u7528\u65b9\u5df2\u9009\u597d\u7684\u9009\u533a\uff08\u542b\u5b83\u7684 mark\uff09** \u2014\u2014
        #:     \u2605 \u800c\u90a3\u6b63\u662f\u89c4\u5219 3 \u7684\u672c\u610f\uff1a**\u9009\u62e9\u7531\u8c03\u7528\u65b9\u505a**\uff08\u2605 \u5de5\u5177\u4e0d\u8d8a\u4fe3\u4ee3\u5e96\uff09\u3002
        #:   \u2605 \u800c\u4ee3\u4ef7\uff1a\u2605 **\u8c03\u7528\u65b9\u9009\u8fb9\u65f6\u5fc5\u987b\u7528 `mark = 1`** \u21d2 \u2605\u2605 \u5df2\u5199\u8fdb\u5de5\u5177\u6587\u6863\u4e0e\u672c\u51fd\u6570\u7684 docstring \u2713
        try:
            _selected_readback = int(get_com_member(get_com_member(model, "SelectionManager"),
                                                    "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                      # noqa: BLE001
            _selected_readback = 0
        if _selected_readback <= 0:
            return {"ok": False, "stage": "selection_readback", "selected": _selected_readback,
                    "error": "\u9009\u533a\u56de\u8bfb\u8ba1\u6570\u4e3a 0\uff08\u2605 \u4e8b\u5b9e 8\uff1a\u8bf7\u4ee5\u8ba1\u6570\u4e3a\u51c6\uff09",
                    "\u2605": "\u8bf7\u5148\u9009\u4e0a\u8be5\u586b\u7684\u90a3\u4e00\u5708\u8fb9\uff0c**\u4e14\u7528 mark = 1**"
                           "\uff08\u5b98\u65b9 Remarks\uff1a\u8fb9\u754c\u8fb9\u7528 mark 1\uff09"}"""
if "不重选" not in src:
    src = src.replace(OLD, NEW, 1)
    p.write_text(src, encoding="utf-8")
    print("  已把声明式支改成\u201c不重选、尊重调用方选区\u201d")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
