import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
t = p.read_text(encoding="utf-8")

#: \u2605 \u627e\u5230 _tool_functions \u7684\u51fd\u6570\u4f53\uff0c\u6574\u4f53\u6362\u6210"\u8bfb\u6ce8\u518c\u8868\u5bf9\u8c61"
start = t.find("def _tool_functions()")
end = t.find("\ndef ", start + 10)
if start == -1 or end == -1:
    print("  **\u672a\u5b9a\u4f4d _tool_functions**")
else:
    NEW = '''def _tool_functions() -> set[str]:
    """\u2605 \u6211\u4eec**\u5df2\u6ce8\u518c**\u6210\u5de5\u5177\u7684 function \u540d\u3002

    \u2605\u2605 \u2605 2026-10-03\uff08\u8f6e 402\uff09**\u7b2c\u4e8c\u6b21\u4fee\u6b63\uff08\u540c\u4e00\u65cf\uff09**\uff1a
      \u2460 \u6700\u521d\u626b**\u6587\u4ef6**\uff08`tool_specs*.py`\uff09\u21d2 \u9608\u6389\u672a\u6ce8\u518c\u7684\u6587\u4ef6\uff08\u8f6e 400 \u4fee\uff09\uff1b
      \u2461 \u6539\u6210\u8bfb `BATCH_MODULES` \u540e**\u4ecd\u7136\u7528\u6b63\u5219\u626b\u6e90\u7801** \u21d2 \u2605\u2605 \u53ea\u8ba4 `function="..."` \u7684\u5199\u6cd5\uff0c
         \u2605 \u800c `tool_specs_batch29.py` \u7528\u7684\u662f**\u51fd\u6570\u540d\u5217\u8868**\uff08`"apply_pressure_report",`\uff09
         \u21d2 **\u6f0f\u6389\u4e86\u5b83\u7684 4 \u6761\u4efb\u52a1\u52a0\u8f7d**\uff08\u2605 \u4e8e\u662f `add_pressure` \u7b49\u88ab\u8bef\u5224\u6210\u7f3a\u53e3\uff09\u3002
      \u21d2 \u2605 \u6b63\u89e3\uff1a**\u8bfb\u6ce8\u518c\u8868\u5bf9\u8c61**\uff08`register_capabilities.all_specs()` \u7684 `.function`\uff09\u2014\u2014
        \u2605 \u90a3\u624d\u662f**\u5b83\u4eec\u771f\u6b63\u5bf9\u5916\u66b4\u9732\u7684\u540d\u5b57**\uff0c\u2605 \u4e0e `audit_real_gaps` \u540c\u4e00\u4e2a\u53e3\u5f84\u3002
    """
    try:
        sys.path.insert(0, str(ROOT / "mcp-server"))
        import register_capabilities as _rc                     # noqa: PLC0415
        return {s.function for s in _rc.all_specs() if getattr(s, "function", None)}
    except Exception:                                           # noqa: BLE001
        #: \u2605 \u515c\u5e95\uff1a\u9000\u56de\u626b\u6e90\u7801\uff08\u2605 \u800c\u90a3\u662f\u6709\u6f0f\u6d1e\u7684 \u2014\u2014 \u6240\u4ee5\u4e0a\u9762\u90a3\u6761\u624d\u662f\u4e3b\u8def\uff09
        out: set = set()
        for f in (ROOT / "mcp-server").glob("tool_specs*.py"):
            try:
                out.update(__import__("re").findall(r'function="([A-Za-z_][A-Za-z0-9_]*)"',
                                                    f.read_text(encoding="utf-8")))
            except Exception:                                   # noqa: BLE001
                continue
        return out

'''
    t = t[:start] + NEW + t[end + 1:]
    p.write_text(t, encoding="utf-8")
    print("  已改为读注册表对象 all_specs()")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:76]))
