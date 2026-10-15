import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
t = p.read_text(encoding="utf-8")

DETECT = '''

_EMPTY_STUB_CACHE: dict = {}


def is_empty_stub(module: str, name: str) -> str:
    """\u2605\u2605 \u7b2c\u4e94\u5c42\u8bc1\u636e\uff08\u8f6e 399\uff09\uff1a**\u7a7a\u5b9e\u73b0\uff08\u5b58\u6839\uff09\u68c0\u6d4b**\u3002

    \u2605 \u771f\u4f8b\uff1a`sw_part.hole_wizard` **\u6709\u540d\u5b57\u3001\u6709\u53c2\u6570\u3001\u6709\u6587\u6863\u4e32**\uff0c
    \u2605\u2605 \u800c\u51fd\u6570\u4f53\u53ea\u6709\u4e00\u4e2a `pass` \u2014\u2014 \u2605 \u6302\u51fa\u53bb**\u5fc5\u7136\u4ec0\u4e48\u90fd\u4e0d\u53d1\u751f**\uff0c
    \u2605 \u800c\u4e14\u6bd4 `spline` \u90a3\u79cd\u201c\u4f1a\u62a5\u9519\u201d\u7684\u66f4\u7cdf\uff1a\u5b83**\u9759\u9ed8\u6210\u529f**\u3002

    :returns: \u7a7a\u5b58\u6839\u7684**\u539f\u56e0**\uff1b\u975e\u7a7a\u5b58\u6839\u56de**\u7a7a\u5b57\u7b26\u4e32**\u3002
    """
    key = (module, name)
    if key not in _EMPTY_STUB_CACHE:
        reason = ""
        path = ROOT / "scripts" / (module + ".py")
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:                                      # noqa: BLE001
            tree = None
        if tree is not None:
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    body = [b for b in node.body
                            if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant)
                                    and isinstance(b.value.value, str))]     #: \u2605 \u5254\u6389 docstring
                    if not body:
                        reason = "\u51fd\u6570\u4f53\u53ea\u6709 docstring\uff08\u8fde `pass` \u90fd\u6ca1\u6709\uff09"
                    elif all(isinstance(b, ast.Pass) for b in body):
                        reason = "\u51fd\u6570\u4f53\u53ea\u6709 `pass`\uff08**\u7a7a\u5b9e\u73b0** \u2014\u2014 \u8c03\u4e86\u4ec0\u4e48\u90fd\u4e0d\u4f1a\u53d1\u751f\uff09"
                    break
        _EMPTY_STUB_CACHE[key] = reason
    return _EMPTY_STUB_CACHE[key]
'''

if "is_empty_stub" not in t:
    t = t.replace("\ndef classify(", DETECT + "\n\ndef classify(", 1)
    OLD = '    wrapper = exposed_by_wrapper(name)'
    NEW = ('    stub_reason = is_empty_stub(module, name)\n'
           '    if stub_reason:\n'
           '        return "\u4e0d\u505a", stub_reason\n'
           '    wrapper = exposed_by_wrapper(name)')
    t = t.replace(OLD, NEW, 1)
    p.write_text(t, encoding="utf-8")
    print("  已加第五层证据（空存根检测）")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:70]))
