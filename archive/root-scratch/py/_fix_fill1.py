import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface_features.py")
src = p.read_text(encoding="utf-8")
old_sig = """def insert_fill_surface_report(model, resolutions: int = 2, *, options: int = _SW_OPTIMIZE_SURFACE,
                               boundary_z: float | None = None) -> dict:"""
new_sig = """def insert_fill_surface_report(model, resolutions: int = 2, *, options: int = _SW_OPTIMIZE_SURFACE,
                               selection: str = "") -> dict:"""
if "selection: str = \"\"" not in src:
    src = src.replace(old_sig, new_sig, 1)
    #: \u2605 \u628a docstring \u91cc\u90a3\u6761\u6539\u6210**\u58f0\u660e\u5f0f**
    src = src.replace(
        "    :param boundary_z: \u8981\u586b\u7684**\u90a3\u4e00\u5708\u8fb9\u6240\u5728\u7684 z**\uff1b\u2605 \u7559\u7a7a = **\u81ea\u52a8\u53d6\u6700\u9ad8\u90a3\u4e00\u5708**\uff08\u2605 \u5750\u6807\u5355\u4f4d\u662f**\u7c73**\uff09\u3002",
        "    :param selection: \u2605\u2605 **\u58f0\u660e\u5f0f\u9009\u62e9**\uff08\u2605 \u8be5\u586b\u7684**\u90a3\u4e00\u5708\u8fb9**\uff09\u3002\n"
        "        \u2605 \u7559\u7a7a = **\u81ea\u52a8\u53d6\u6700\u9ad8\u90a3\u4e00\u5708**\uff08\u2605 \u4fdd\u7559\u539f\u884c\u4e3a\uff09\u3002\n"
        "        \u2605\u2605 \u2605 2026-10-03\uff08\u8f6e 434\uff09**\u539f\u6765\u8fd9\u91cc\u662f `boundary_z: float`**\uff08\u4e00\u4e2a\u88f8\u5750\u6807\uff09\n"
        "        \u2605 \u800c\u90a3**\u8fdd\u53cd\u89c4\u5219 3**\uff08\u2605 \u5b98\u65b9\u539f\u8bdd\uff1a\u5fc5\u987b\u6539\u7528**\u5177\u540d\u5b9e\u4f53 + \u58f0\u660e\u5f0f selection**\uff09\u3002", 1)
    p.write_text(src, encoding="utf-8")
    print("  \u2460 \u7b7e\u540d\u5df2\u6539\uff1aboundary_z -> selection")
else:
    print("  \u2460 (\u5df2\u6539)")

#: \u2461 \u5728"\u6536\u96c6\u8fb9 \u2192 \u6309 z \u6311"**\u4e4b\u524d**\u63d2\u4e00\u6761\u58f0\u660e\u5f0f\u5206\u652f
OLD = """    edges, mids = [], []
    try:"""
NEW = """    #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 434\uff09**\u58f0\u660e\u5f0f\u5206\u652f** \u2014\u2014
    #:   \u2605 \u82e5\u7ed9\u4e86 `selection` \u21d2 **\u7528\u5b83\u9009**\uff08\u2605 \u90a3\u662f\u89c4\u5219 3 \u8981\u6c42\u7684\u5f62\u6001\uff09\uff1b
    #:   \u2605 \u5426\u5219\u8d70**\u539f\u81ea\u52a8\u8def**\uff08\u2605 \u6309\u6700\u9ad8\u4e00\u5708\u8fb9\u7684 z \u6311\uff09\u2014\u2014\u2605 **\u884c\u4e3a\u4e0d\u53d8**\u3002
    if str(selection or "").strip():
        from .sw_selection_spec import resolve_selection
        try:
            got = int(resolve_selection(model, str(selection), "EDGE", body_index=-1))
        except Exception as exc:                                   # noqa: BLE001
            return {"ok": False, "stage": "resolve_selection",
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        if got <= 0:
            return {"ok": False, "stage": "resolve_selection", "selected": got,
                    "error": "\u58f0\u660e\u5f0f\u9009\u62e9\u56de\u8bfb\u8ba1\u6570\u4e3a 0\uff08\u2605 \u4e8b\u5b9e 8\uff1a\u8bf7\u4ee5\u8ba1\u6570\u4e3a\u51c6\uff09"}
        picked, z = [], None
        return _fill_after_selection(model, res, options, picked, z,
                                     selected=got, declarative=True)
    edges, mids = [], []
    try:"""
if "_fill_after_selection" not in src:
    src = src.replace(OLD, NEW, 1)
    p.write_text(src, encoding="utf-8")
    print("  \u2461 \u5df2\u63d2\u58f0\u660e\u5f0f\u5206\u652f")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
