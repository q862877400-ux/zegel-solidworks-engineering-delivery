import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 **\u8ba9 `check_server_side_tools.py` \u80fd\u5931\u8d25**\uff08\u2605 \u5224\u636e\uff1a**\u5de5\u5177\u540d\u4e0d\u8bb8\u91cd\u540d**\uff09
p = R / "tools" / "check_server_side_tools.py"
t = p.read_text(encoding="utf-8")
OLD = '''    print("  \\u26a0\\u2605 **\u8bda\u5b9e\u8bdd**\uff1a\u672c\u68c0\u67e5**\u53ea\u505a\u9759\u6001\u90a3\u90e8\u5206**\uff08\u2605 \u53c2\u6570\u540d\uff09\u2014\u2014")'''
#: \u2605 \u5728 `return 0` \u4e4b\u524d\u63d2\u5165\u91cd\u540d\u68c0\u67e5
OLD2 = """    print()
    print("  \u26a0\u2605 **\u8bda\u5b9e\u8bdd**"""
NEW2 = """    print()
    #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 450\uff09**\u672c\u811a\u672c\u8fdb\u95e8\u7981\u4e86** \u21d2 \u2605 \u5b83\u5fc5\u987b**\u80fd\u5931\u8d25**\u3002
    #:   \u2605 \u5224\u636e\uff08\u2605 \u9759\u6001\u3001\u53ef\u590d\u7b97\uff09\uff1a**\u4e24\u6761\u58f0\u660e\u8def\u4e0a\u7684 `solidworks_*` \u5de5\u5177\u540d\u4e0d\u8bb8\u91cd\u540d** \u2014\u2014
    #:   \u2605\u2605 \u91cd\u540d\u610f\u5473\u7740\u540e\u6ce8\u518c\u7684**\u906e\u6389**\u5148\u6ce8\u518c\u7684\uff08\u2605 \u800c\u8c03\u7528\u65b9\u770b\u4e0d\u51fa\u6765\uff09\u3002
    try:
        import sys as _s
        _s.path.insert(0, str(REPO_ROOT / "mcp-server"))
        import register_capabilities as _RC
        spec_names = {sp.name for sp in _RC.all_specs()}
    except Exception as exc:                                   # noqa: BLE001
        print("  [SKIP] \u53d6\u4e0d\u5230 ToolSpec \u4fa7\u7684\u540d\u5355\uff1a%s" % str(exc)[:90])
        return 0
    dupes = sorted(set(tools) & spec_names)
    if dupes:
        print("  \u2717 **\u91cd\u540d %d \u4e2a**\uff08\u2605 \u4e24\u6761\u58f0\u660e\u8def\u4e0a\u90fd\u6709\uff09\uff1a%s" % (len(dupes), ", ".join(dupes)))
        print("      \u2605 \u540e\u6ce8\u518c\u7684\u4f1a**\u906e\u6389**\u5148\u6ce8\u518c\u7684 \u21d2 \u2605 \u6539\u540d\u4e00\u4e2a\u3002")
        return 1
    print("  \u2713 \u4e24\u6761\u58de\u660e\u8def\u7684\u5de5\u5177\u540d**\u65e0\u91cd\u540d**\uff08ToolSpec %d + \u88c5\u9970\u5668 %d \u21d2 \u5171 %d\uff09"
          % (len(spec_names), len(tools), len(spec_names) + len(tools)))
    print()
    print("  \u26a0\u2605 **\u8bda\u5b9e\u8bdd**"""
if "\u4e24\u6761\u58de\u660e\u8def" not in t:
    t = t.replace(OLD2, NEW2, 1)
    p.write_text(t, encoding="utf-8")
    print("\u2460 \u5df2\u8ba9\u5b83\u80fd\u5931\u8d25\uff08\u91cd\u540d\u5224\u636e\uff09")
try:
    compile(t, str(p), "exec"); print("   ok-compile")
except SyntaxError as e:
    print("   **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
