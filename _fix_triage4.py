import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
src = p.read_text(encoding="utf-8")

#: \u2460 \u65b0\u589e\uff1a\u4ece `server.py` \u7684 `exports = {…}` \u8bfb\u51fa\u90a3\u534a\u8fb9\u7684 function \u540d
FUNC = '''def _server_export_functions() -> set[str]:
    """\u2605\u2605\u2605 2026-10-03\uff08\u8f6e 437\uff09**\u5206\u8bca\u7684\u7b2c\u4e8c\u4e2a\u76f2\u533a\u7684\u4fee\u6cd5** \u2014\u2014
    \u2605 `_tool_functions()` \u8bfb\u7684\u662f **ToolSpec**\uff08`register_capabilities.all_specs()`\uff09\uff0c
      \u2605\u2605 \u800c `server.py` \u91cc\u53e6\u6709\u4e00\u6279**\u975e ToolSpec** \u7684\u5de5\u5177\u58f0\u660e
        \uff08\u2605 \u5f62\u5f0f\u662f `exports = { "\u51fd\u6570\u540d": \u6a21\u5757.\u51fd\u6570, \u2026 }`\uff09
      \u21d2 \u2605 \u90a3\u4e00\u534a**\u5bf9\u5206\u8bca\u4e0d\u53ef\u89c1** \u21d2 \u628a\u5df2\u8986\u76d6\u7684\u540d\u5b57\u62a5\u6210\u8be5\u6302\u3002
    \u2605\u2605 \u800c\u5224\u636e\u662f**\u7ed3\u6784**\uff08\u2605 \u627e\u53d8\u91cf\u540d\u4e3a `exports` \u7684 dict \u5b57\u9762\u91cf\u7684**\u952e**\uff09\u2014\u2014
      \u2605 \u4e0d\u662f\u518d\u5217\u4e00\u5f20\u8868\uff08\u2605 \u5426\u5219\u53c8\u53d8\u6210\u7a77\u4e3e \u2014\u2014 \u4e8b\u5b9e 53\uff09\u3002
    """
    import ast as _ast                                            # noqa: PLC0415
    path = ROOT / "mcp-server" / "server.py"
    out: set[str] = set()
    try:
        tree = _ast.parse(path.read_text(encoding="utf-8"))
    except Exception:                                              # noqa: BLE001
        return out
    for node in _ast.walk(tree):
        if not isinstance(node, _ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, _ast.Name)]
        if "exports" not in names or not isinstance(node.value, _ast.Dict):
            continue
        for k in node.value.keys:
            if isinstance(k, _ast.Constant) and isinstance(k.value, str):
                out.add(k.value)
    return out


def _tool_functions() -> set[str]:'''
if "_server_export_functions" not in src:
    src = src.replace("def _tool_functions() -> set[str]:", FUNC, 1)
    print("\u2460 \u5df2\u52a0 _server_export_functions")

#: \u2461 \u5e76\u8fdb `_tool_functions()`\uff08\u2605 \u4e24\u4e2a return \u90fd\u8981\u5e76\uff09
OLD = """        import register_capabilities as _rc                     # noqa: PLC0415
        return {s.function for s in _rc.all_specs() if getattr(s, "function", None)}"""
NEW = """        import register_capabilities as _rc                     # noqa: PLC0415
        #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 437\uff09**\u5e76\u4e0a `server.py` \u90a3\u534a\u8fb9** \u2014\u2014
        #:   \u2605 \u5426\u5219\u5206\u8bca\u53ea\u770b\u5f97\u89c1 ToolSpec\uff0c\u2605 \u800c\u628a `batch_export_formats` \u8fd9\u7c7b
        #:     \uff08\u2605 \u5728 `server.py` \u4fa7\u58f0\u660e\u7684\uff09\u5f53\u6210\u6ca1\u6709\u5de5\u5177 \u2014\u2014 \u2605 \u4e8b\u5b9e 350 \u8bb0\u7684\u5c31\u662f\u8fd9\u4e2a\u76f2\u533a\u3002
        return ({s.function for s in _rc.all_specs() if getattr(s, "function", None)}
                | _server_export_functions())"""
if "_server_export_functions())" not in src:
    src = src.replace(OLD, NEW, 1)
    print("\u2461 \u5df2\u5e76\u8fdb _tool_functions \u7684\u4e3b\u8def")
OLD2 = """            out: set = set()
            for f in (ROOT / "mcp-server").glob("tool_specs*.py"):"""
NEW2 = """            out: set = _server_export_functions()
            for f in (ROOT / "mcp-server").glob("tool_specs*.py"):"""
if "out: set = _server_export_functions()" not in src:
    src = src.replace(OLD2, NEW2, 1)
    print("\u2462 \u5df2\u5e76\u8fdb\u5907\u7528\u8def")
p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
