import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface_features.py")
src = p.read_text(encoding="utf-8")

#: \u2460 **\u6495\u6389\u4e0a\u4e00\u7248\u90a3\u4e2a\u5f15\u7528\u4e86\u4e0d\u5b58\u5728\u52a9\u624b\u7684\u5206\u652f**
BAD_START = "    #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 434\uff09**\u58f0\u660e\u5f0f\u5206\u652f**"
BAD_END = "    edges, mids = [], []\n    try:"
i = src.find(BAD_START)
j = src.find(BAD_END)
if i >= 0 and j > i:
    src = src[:i] + BAD_END + src[j + len(BAD_END):]
    print("  \u2460 \u5df2\u6495\u6389\u90a3\u4e2a\u574f\u5206\u652f")

#: \u2461 \u7528**\u6807\u5fd7**\u91cd\u505a\uff1a\u58f0\u660e\u5f0f\u5148\u9009\uff0c\u800c\u540e\u534a\u6bb5\u5171\u7528
OLD = """    edges, mids = [], []
    try:"""
NEW = """    #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 434\uff09**\u58f0\u660e\u5f0f\u5206\u652f** \u2014\u2014 \u2605 \u800c\u540e\u534a\u6bb5**\u4e24\u6761\u8def\u5171\u7528**\uff1a
    #:   \u2605 \u7ed9\u4e86 `selection` \u21d2 **\u7528\u5b83\u9009**\uff08\u2605 \u90a3\u662f\u89c4\u5219 3 \u8981\u6c42\u7684\u5f62\u6001\uff09\uff0c\u2605 \u800c `_declarative = True`
    #:     \u21d2 \u2605\u2605 **\u8df3\u8fc7\u540e\u9762\u90a3\u4e2a"\u6309\u70b9\u9009\u8fb9"\u7684\u5faa\u73af**\uff08\u5df2\u7ecf\u9009\u597d\u4e86\uff09\uff1b
    #:   \u2605 \u5426\u5219\u8d70**\u539f\u81ea\u52a8\u8def**\uff08\u6309\u6700\u9ad8\u4e00\u5708\u8fb9\u7684 z \u6311\uff09\u2014\u2014\u2605 **\u884c\u4e3a\u4e0d\u53d8**\u3002
    _declarative = bool(str(selection or "").strip())
    _selected_readback = 0
    if _declarative:
        from .sw_selection_spec import resolve_selection
        try:
            _selected_readback = int(resolve_selection(model, str(selection), "EDGE",
                                                       body_index=-1))
        except Exception as exc:                                   # noqa: BLE001
            return {"ok": False, "stage": "resolve_selection",
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        if _selected_readback <= 0:
            return {"ok": False, "stage": "resolve_selection", "selected": _selected_readback,
                    "error": "\u58f0\u660e\u5f0f\u9009\u62e9\u56de\u8bfb\u8ba1\u6570\u4e3a 0\uff08\u2605 \u4e8b\u5b9e 8\uff1a\u8bf7\u4ee5\u8ba1\u6570\u4e3a\u51c6\uff09"}
    edges, mids = [], []
    try:"""
if "_declarative" not in src:
    src = src.replace(OLD, NEW, 1)
    print("  \u2461 \u5df2\u63d2\u6807\u5fd7\u5f0f\u5206\u652f")

#: \u2462 **\u628a\u540e\u534a\u6bb5\u90a3\u4e24\u6bb5\u62a4\u4f4f**\uff1a\u6309 z \u6311\u8fb9 \u00b7 \u6309\u70b9\u9009\u8fb9
OLD2 = """    z = float(boundary_z) if boundary_z is not None else max(m[2] for m in mids)
    picked = [(m, e) for m, e in zip(mids, edges) if abs(m[2] - z) < 1e-9]"""
NEW2 = """    z = max(m[2] for m in mids) if not _declarative else None
    picked = [] if _declarative else [(m, e) for m, e in zip(mids, edges) if abs(m[2] - z) < 1e-9]"""
if "if not _declarative else" not in src:
    src = src.replace(OLD2, NEW2, 1)
    print("  \u2462 \u5df2\u62a4\u4f4f\u90a3\u4e24\u6bb5")
#: \u2605 \u800c `len(picked) < 3` \u90a3\u4e2a\u63d0\u524d\u8fd4\u56de\u8981**\u8df3\u8fc7**\uff08\u58f0\u660e\u5f0f\u8def\u4e0d\u9760 picked\uff09
OLD3 = """    if len(picked) < 3:
        return {"ok": False, "stage": "pick_boundary", "at_z": z,"""
NEW3 = """    if not _declarative and len(picked) < 3:
        return {"ok": False, "stage": "pick_boundary", "at_z": z,"""
if "if not _declarative and len(picked) < 3" not in src:
    src = src.replace(OLD3, NEW3, 1)
    print("  \u2463 \u5df2\u62a4\u4f4f len(picked) \u90a3\u4e2a\u8fd4\u56de")
#: \u2605 \u6309\u70b9\u9009\u8fb9\u7684\u5faa\u73af
OLD4 = """    for m, _e in picked:
        try:
            ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, MARK_BOUNDARY, callout, 0)"""
NEW4 = """    for m, _e in ([] if _declarative else picked):
        try:
            ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, MARK_BOUNDARY, callout, 0)"""
if "([] if _declarative else picked)" not in src:
    src = src.replace(OLD4, NEW4, 1)
    print("  \u2464 \u5df2\u62a4\u4f4f\u6309\u70b9\u9009\u8fb9\u7684\u5faa\u73af")
#: \u2605 \u9009\u4e2d\u8ba1\u6570\uff1a\u58f0\u660e\u5f0f\u8def**\u5df2\u6709\u56de\u8bfb**\uff08\u2605 \u4e0d\u91cd\u8bfb\uff09
OLD5 = """    selected = 0
    try:
        selected = int(get_com_member(get_com_member(model, "SelectionManager"),
                                      "GetSelectedObjectCount2", -1) or 0)
    except Exception:                                          # noqa: BLE001
        selected = 0"""
NEW5 = """    selected = _selected_readback
    if not _declarative:
        try:
            selected = int(get_com_member(get_com_member(model, "SelectionManager"),
                                          "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                      # noqa: BLE001
            selected = 0"""
if "selected = _selected_readback" not in src:
    src = src.replace(OLD5, NEW5, 1)
    print("  \u2465 \u5df2\u5904\u7406\u9009\u4e2d\u8ba1\u6570")
p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
