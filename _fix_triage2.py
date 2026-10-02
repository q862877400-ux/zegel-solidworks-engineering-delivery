import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "tools" / "triage_real_gaps.py"
src = p.read_text(encoding="utf-8")

OLD = '''    own = ROOT / "scripts" / (module + ".py")
    for f in (ROOT / "scripts").glob("*.py"):
        if f == own:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:                                          # noqa: BLE001
            continue
        if name in text:
            return True
    return False'''
NEW = '''    #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 432\uff09**\u5224\u636e\u6536\u7d27\u4e3a"\u771f\u7684\u88ab\u8c03\u7528"** \u2014\u2014
    #:   \u2605 \u7b2c\u4e00\u7248\u7528\u7684\u662f**\u5b50\u4e32\u51fa\u73b0**\uff08`if name in text`\uff09\uff0c\u2605 \u800c\u5b83**\u592a\u5bbd**\uff1a
    #:     \u6ce8\u91ca / \u5b57\u7b26\u4e32 / \u522b\u540d\u90fd\u7b97"\u51fa\u73b0" \u21d2 \u628a\u771f\u7f3a\u53e3\u541e\u6389\u3002
    #:   \u2605\u2605 \u800c**\u672c\u4ed3\u7684\u8d1f\u4f8b\u5b88\u536b\u5f53\u573a\u6293\u5230\u5b83**\uff1a
    #:     `tests/test_real_gap_triage_contract.py::test_wrapper_rule_does_not_swallow_real_gaps`
    #:     \u65ad\u8a00 `sw_part.linear_pattern` \u5fc5\u987b\u662f\u300c\u8be5\u6302\u300d\uff0c\u2605 \u800c\u5b83\u88ab\u5224\u6210\u4e86\u300c\u5185\u90e8\u4ef6\u300d\u3002
    #:   \u21d2 \u2605 \u6b63\u89e3\uff1a**\u7528 AST \u627e `ast.Call`**\uff08\u2605 \u5373"\u771f\u7684\u88ab\u8c03\u7528"\uff09\u2014\u2014 \u2605 \u4e0e**\u4e8b\u5b9e 51**\uff08\u5224\u636e\u8981\u8d34\u5408\u4ee3\u7801\u7684\u7ec4\u7ec7\u5355\u5143\uff0c
    #:     \u4e0d\u8981\u6309\u6587\u672c\u5339\u914d\uff09**\u540c\u65cf**\u3002
    own = ROOT / "scripts" / (module + ".py")
    import ast as _ast                                            # noqa: PLC0415
    for f in (ROOT / "scripts").glob("*.py"):
        if f == own:
            continue
        try:
            tree = _ast.parse(f.read_text(encoding="utf-8"))
        except Exception:                                          # noqa: BLE001
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call):
                continue
            func = node.func
            #: \u2605 \u4e09\u79cd\u5199\u6cd5\uff1a`name(...)` \u00b7 `mod.name(...)` \u00b7 \u522b\u540d\u540e\u7684 `name(...)`
            if isinstance(func, _ast.Name) and func.id == name:
                return True
            if isinstance(func, _ast.Attribute) and func.attr == name:
                return True
    return False'''
if "ast.Call" not in src:
    src = src.replace(OLD, NEW, 1)
    p.write_text(src, encoding="utf-8")
    print("  已把判据收紧为 AST 找调用")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
