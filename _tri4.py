import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
t = p.read_text(encoding="utf-8")

#: \u2605 \u52a0\u4e00\u4e2a\u61d2\u52a0\u8f7d\u7684"\u5df2\u6709\u5de5\u5177\u7684 function \u540d"\u96c6
LAZY = '''

_HAVE_TOOL_CACHE: set | None = None


def have_tool_functions() -> set:
    """\u2605 \u5df2\u88ab\u67d0\u4e2a ToolSpec \u58f0\u660e\u4e3a\u76ee\u6807\u51fd\u6570\u7684\u540d\u5b57\u96c6\uff08\u2605 \u61d2\u52a0\u8f7d\uff09\u3002"""
    global _HAVE_TOOL_CACHE
    if _HAVE_TOOL_CACHE is None:
        _HAVE_TOOL_CACHE = _tool_functions()
    return _HAVE_TOOL_CACHE


#: \u2605 \u7b2c\u56db\u5c42\u8bc1\u636e\uff08\u8f6e 399\uff09\uff1a**\u529f\u80fd\u5df2\u7531\u53e6\u4e00\u4e2a\u5305\u88c5\u66b4\u9732** \u2014\u2014
#:   \u2605 \u771f\u4f8b\uff08\u771f\u673a\u6838\u8fc7\uff09\uff1a`sw_part.shell` \u81ea\u5df1\u6ca1\u6709\u5de5\u5177\uff0c
#:   \u2605\u2605 \u800c `sw_part.shell_report` **\u6709**\uff08\u5de5\u5177 `solidworks_part_shell`\uff09\u3002
#:   \u21d2 \u90a3\u4e0d\u662f\u7f3a\u53e3\uff08\u2605 \u201c\u540d\u5b57\u4e0d\u540c \u2260 \u80fd\u529b\u6ca1\u6709\u201d \u2014\u2014 \u4e8b\u5b9e 311 \u540c\u65cf\uff09\u3002
_REPORT_SUFFIXES = ("_report", "2_report", "_report2")


def exposed_by_wrapper(name: str) -> str | None:
    """\u2605 \u82e5 `name` \u7684**\u5305\u88c5\u53d8\u4f53**\u5df2\u6709\u5de5\u5177 \u21d2 \u56de\u90a3\u4e2a\u540d\u5b57\uff1b\u5426\u5219 `None`\u3002"""
    have = have_tool_functions()
    for cand in (name + "_report", "create_" + name + "_report", name + "2_report"):
        if cand in have:
            return cand
    return None
'''

if "exposed_by_wrapper" not in t:
    t = t.replace("\ndef classify(", LAZY + "\n\ndef classify(", 1)
    #: \u2605 classify \u91cc\u52a0\u4e00\u6761\uff08\u2605 \u653e\u5728\u201c\u4e0d\u505a\u201d\u4e4b\u540e\u3001\u201c\u5185\u90e8\u4ef6\u201d\u4e4b\u524d\uff09
    OLD = '    if name[:1].isupper() or name.endswith(NOT_A_FUNCTION_SUFFIXES):'
    NEW = ('    wrapper = exposed_by_wrapper(name)\n'
           '    if wrapper is not None:\n'
           '        return "\u5df2\u6709", ("\u529f\u80fd\u5df2\u7531 `%s` \u5305\u88c5\u66b4\u9732\uff08\u2605 \u540d\u5b57\u4e0d\u540c \u2260 \u80fd\u529b\u6ca1\u6709\uff09" % wrapper)\n'
           '    if name[:1].isupper() or name.endswith(NOT_A_FUNCTION_SUFFIXES):')
    t = t.replace(OLD, NEW, 1)
    #: \u2605 \u4e09\u7c7b\u6539\u56db\u7c7b
    t = t.replace('    for k in ("\u8be5\u6302", "\u5185\u90e8\u4ef6", "\u4e0d\u505a"):',
                  '    for k in ("\u8be5\u6302", "\u5df2\u6709", "\u5185\u90e8\u4ef6", "\u4e0d\u505a"):')
    t = t.replace('    print("  \u4e09\u7c7b\u4e4b\u548c == total \u21d2 %s" % summary["self_check"])',
                  '    print("  \u56db\u7c7b\u4e4b\u548c == total \u21d2 %s" % summary["self_check"])')
    t = t.replace('"\u2605": "\u4e09\u7c7b\u4e4b\u548c\u5fc5\u987b == total\uff08\u2605 \u672c\u811a\u672c\u81ea\u68c0\uff09"',
                  '"\u2605": "\u56db\u7c7b\u4e4b\u548c\u5fc5\u987b == total\uff08\u2605 \u672c\u811a\u672c\u81ea\u68c0\uff09"')
    p.write_text(t, encoding="utf-8")
    print("  \u5df2\u52a0\u7b2c\u56db\u5c42\u8bc1\u636e\uff08*\u005freport \u5305\u88c5\uff09")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:70]))
