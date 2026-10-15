import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 **\u5220\u6389\u6b8b\u9ab8\u672c\u4f53**
f = R / "scripts" / "sw_selection_tx.py"
if f.exists():
    f.unlink()
    print("\u2460 \u5df2\u5220 scripts/sw_selection_tx.py")
else:
    print("\u2460 (\u5df2\u4e0d\u5728)")

#: \u2461 **\u628a\u767b\u8bb0\u8868\u6e05\u7a7a**\uff08\u2605 \u800c\u4fdd\u7559\u5b83\u7684\u8bf4\u660e\uff09
g = R / "scripts" / "check_undefined_names.py"
t = g.read_text(encoding="utf-8")
i = t.find("KNOWN_BROKEN = {")
j = t.find("\n}", i)
if i > 0 and j > i:
    OLD = t[i:j + 2]
    NEW = ('#: \u2605\u2605 \u767d\u540d\u5355\uff08\u2605 **\u800c\u4e0d\u662f\u4fee\u590d**\uff09**\u73b0\u5728\u662f\u7a7a\u7684**\u3002\n'
           '#:   \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 431\uff09**\u552f\u4e00\u90a3\u6761\u5df2\u6309\u51b3\u65ad\u5220\u9664**\uff1a\n'
           '#:     `scripts/sw_selection_tx.py`\uff08\u6b8b\u9ab8\uff1a\u5f15\u7528\u7684 4 \u4e2a\u540d\u5b57\u5168\u4ed3\u4e0d\u5b58\u5728 \u00b7 \u65e0\u4eba\u5bfc\u5165\uff09\u3002\n'
           '#:   \u2605 **\u5220\u5b83\u7684\u4e09\u6761\u4f9d\u636e**\uff1a\n'
           '#:     \u2460 \u5b83\u8981\u7ba1\u7406\u7684 `AccessSelections` \u5728\u672c\u673a\u540e\u7aef\u4e0a**\u8c03\u4e0d\u901a**\n'
           '#:        \uff08**\u4e8b\u5b9e 47**\uff1a\u67b6\u6784\u6027\u9650\u5236\uff0c20+ \u79cd\u5f62\u6001\u5b9e\u6d4b\uff09\u21d2 \u2605 **\u8865\u5168\u4e86\u4e5f\u6ca1\u7528**\uff1b\n'
           '#:     \u2461 **\u65e0\u4efb\u4f55\u6a21\u5757\u5bfc\u5165\u5b83**\uff08\u5df2\u6838\uff09\u21d2 **\u5220\u5b83\u4e0d\u5f71\u54cd\u8c03\u7528\u65b9**\uff1b\n'
           '#:     \u2462 \u5b83\u7684**\u610f\u56fe**\uff08\u2605\u201c\u5f02\u5e38\u8def\u5f84\u4e5f\u91ca\u653e\u9009\u533a\u63a5\u7ba1\u201d\uff09**\u503c\u5f97\u4fdd\u7559**\n'
           '#:        \u21d2 \u2605 \u5df2\u5199\u8fdb `docs/known-facts.md`\uff08\u2605 **\u800c\u4e0d\u662f\u7559\u5728\u6b7b\u4ee3\u7801\u91cc**\uff09\u3002\n'
           '#:   \u26a0 \u2605 \u800c\u672c\u767d\u540d\u5355\u7684\u5951\u7ea6**\u4e0d\u53d8**\uff1a\u2605 **\u6bcf\u6761\u90fd\u5fc5\u987b\u6709**\u90a3\u4e2a\u6587\u4ef6\n'
           '#:     \uff08\u2605 \u5220\u4e86\u6587\u4ef6\u5c31\u8be5\u5220\u540d\u5355 \u2014\u2014 \u2605 \u90a3\u6b63\u662f\u672c\u8f6e\u53d1\u751f\u7684\u4e8b\uff09\u3002\n'
           'KNOWN_BROKEN: dict[str, str] = {}')
    t = t[:i] + NEW + t[j + 2:]
    g.write_text(t, encoding="utf-8")
    print("\u2461 \u5df2\u6e05\u7a7a KNOWN_BROKEN\uff08\u5e76\u7559\u4e0b\u5220\u9664\u7684\u4e09\u6761\u4f9d\u636e\uff09")
try:
    compile(t, str(g), "exec"); print("   ok-compile")
except SyntaxError as exc:
    print("   **\u9519 L%s**: %s" % (exc.lineno, str(exc.msg)[:70]))

#: \u2462 **\u90a3\u6761\u95e8\u7981\u6d4b\u8bd5**\uff1a\u53bb\u6389\u5df2\u5220\u6587\u4ef6\u7684\u65ad\u8a00\uff0c**\u4fdd\u7559\u201c\u6587\u4ef6\u5fc5\u987b\u5728\u201d\u90a3\u6761\u5951\u7ea6**
tt = R / "tests" / "test_undefined_names_gate.py"
s = tt.read_text(encoding="utf-8")
i2 = s.find("def test_known_broken_entries_are_not_gating_but_are_documented")
i3 = s.find("\ndef ", i2 + 10)
if i2 > 0 and i3 > i2:
    NEWTEST = ('def test_known_broken_entries_are_not_gating_but_are_documented() -> None:\n'
               '    """\u2605\u2605 \u24d3 `KNOWN_BROKEN` \u662f**\u767d\u540d\u5355\u800c\u4e0d\u662f\u4fee\u590d** \u2014\u2014 \u800c\u5b83\u73b0\u5728\u662f**\u7a7a\u7684**\u3002\n'
               '\n'
               '    \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 431\uff09\u552f\u4e00\u90a3\u6761\uff08`scripts/sw_selection_tx.py`\uff09**\u5df2\u6309\u51b3\u65ad\u5220\u9664**\uff1a\n'
               '      \u5b83\u8981\u7ba1\u7406\u7684 `AccessSelections` \u5728\u672c\u673a\u540e\u7aef\u4e0a**\u8c03\u4e0d\u901a**\uff08**\u4e8b\u5b9e 47**\uff09\u21d2 \u8865\u5168\u4e86\u4e5f\u6ca1\u7528\uff1b\n'
               '      \u800c**\u65e0\u4efb\u4f55\u6a21\u5757\u5bfc\u5165\u5b83**\u3002\n'
               '    \u2605 \u800c**\u672c\u6d4b\u8bd5\u4fdd\u7559\u7684\u5951\u7ea6**\uff08\u2605 \u5b83\u672c\u6765\u5c31\u5199\u7740\uff09\uff1a\n'
               '      \u24d0 \u540d\u5355\u91cc\u6bcf\u6761**\u90fd\u5fc5\u987b\u6709**\u90a3\u4e2a\u6587\u4ef6\uff08\u2605 \u5220\u4e86\u6587\u4ef6\u5c31\u8be5\u5220\u540d\u5355\uff09\uff1b\n'
               '      \u24d1 \u6bcf\u6761\u7406\u7531\u90fd\u8981\u591f\u957f\uff08\u2605 \u7a7a\u7406\u7531\u7b49\u4e8e\u9759\u9ed8\u8c41\u514d\uff09\u3002\n'
               '    """\n'
               '    for path, why in C.KNOWN_BROKEN.items():\n'
               '        assert len(why) > 60, "%s \u7684\u7406\u7531\u592a\u77ed \u21d2 \u7b49\u4e8e\u9759\u9ed8\u8c41\u514d" % path\n'
               '        assert (ROOT / path).exists(), "%s \u4e0d\u5b58\u5728\u4e86 \u21d2 \u540d\u5355\u8be5\u5220\u6389\u5b83" % path\n')
    s = s[:i2] + NEWTEST + s[i3 + 1:]
    tt.write_text(s, encoding="utf-8")
    print("\u2462 \u5df2\u6539\u90a3\u6761\u95e8\u7981\u6d4b\u8bd5")
try:
    compile(s, str(tt), "exec"); print("   ok-compile")
except SyntaxError as exc:
    print("   **\u9519 L%s**: %s" % (exc.lineno, str(exc.msg)[:70]))

#: \u2463 **\u90a3\u6761\u53d8\u7a7a\u7684\u5951\u7ea6\u6d4b\u8bd5**\uff1a\u5220\u6389\u5b83\uff08\u2605 \u7a7a\u5faa\u73af\u901a\u8fc7\u6bd4\u6ca1\u6709\u66f4\u574f\uff09
ot = R / "tests" / "test_official_names_only_contract.py"
o = ot.read_text(encoding="utf-8")
o = o.replace('OWNED = {"sw_selection_tx"}', 'OWNED: set = set()   # \u2605 2026-10-03\uff08\u8f6e 431\uff09\uff1a\u552f\u4e00\u90a3\u4e2a\uff08sw_selection_tx\uff09\u5df2\u6309\u51b3\u65ad\u5220\u9664')
i4 = o.find("def test_no_other_sw_api_helper_survives():")
i5 = o.find("\n\n\n", i4)
if i4 > 0 and i5 > i4:
    o = o[:i4] + ("#: \u2605\u2605 2026-10-03\uff08\u8f6e 431\uff09\uff1a\u539f\u672c\u8fd9\u91cc\u6709\u4e00\u6761 `test_no_other_sw_api_helper_survives`\uff0c\n"
                  "#:   \u2605 \u800c\u5b83**\u53ea**\u904d\u5386 `OWNED`\uff08\u5f53\u65f6\u53ea\u6709 `sw_selection_tx`\uff09\u3002\n"
                  "#:   \u2605 \u800c\u90a3\u4e2a\u6a21\u5757\u5df2\u5220 \u21d2 \u2605\u2605 \u5faa\u73af**\u4e3a\u7a7a** \u21d2 \u90a3\u6837\u7684\u6d4b\u8bd5\n"
                  "#:   **\u6bd4\u6ca1\u6709\u66f4\u574f**\uff08\u2605 \u672c\u4ed3\u81ea\u5df1\u7684\u89c4\u77e9\uff1a\u201c\u4e00\u4e2a\u5b58\u5728\u4f46\u6ca1\u4eba\u7528\u7684\u5b88\u536b\n"
                  "#:   \u4e0e\u6ca1\u6709\u5b88\u536b\u7b49\u4ef7\u201d\uff09\u21d2 \u2605 **\u6545\u5220\u6389\u90a3\u6761\u6d4b\u8bd5**\uff0c\u2605 \u800c\u628a\u5b83\u7684\u5951\u7ea6\n"
                  "#:   \u7559\u5728\u4e0b\u9762\u90a3\u4e9b**\u771f\u5728\u904d\u5386\u6587\u4ef6**\u7684\u6d4b\u8bd5\u91cc\u3002\n") + o[i5 + 3:]
    ot.write_text(o, encoding="utf-8")
    print("\u2463 \u5df2\u5220\u90a3\u6761\u53d8\u7a7a\u7684\u6d4b\u8bd5\uff08\u5e76\u7559\u4e0b\u7406\u7531\uff09")
try:
    compile(o, str(ot), "exec"); print("   ok-compile")
except SyntaxError as exc:
    print("   **\u9519 L%s**: %s" % (exc.lineno, str(exc.msg)[:70]))
