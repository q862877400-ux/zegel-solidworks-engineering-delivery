import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u300a\u68c0\u67e5\u5668\u300b\uff1adump Add* \u4e0e Get*\uff1b\u4e14"\u7c7b\u578b\u5e93\u91cc\u6ca1\u6709"\u6539\u4e3a**\u8bf4\u660e\u800c\u4e0d\u62a5\u9519**
p = R / "tools" / "check_typelib_tables.py"
t = p.read_text(encoding="utf-8")
t = t.replace("| Where-Object { $_.Name -like 'Add*' }", "| Where-Object { $_.Name -like 'Add*' -or $_.Name -like 'Get*' }")
t = t.replace('''        ps = lib.get(n)
        if ps is None:
            bad.append(("OFFICIAL_LOAD_SIGNATURES", "类型库里没有", n))
            continue''',
              '''        ps = lib.get(n)
        if ps is None:
            #: \u2605 \u53ea\u6709 **`Add*`** \u7f3a\u5e2d\u624d\u7b97\u95ee\u9898\uff1b\u2605 \u5176\u5b83\u540d\u5b57\uff08\u5982 `Get*`\uff09
            #:   \u672c\u8eab\u5c31\u4e0d\u5728\u8fd9\u4e2a\u63a5\u53e3\u4e0a \u21d2 \u2605 **\u5982\u5b9e\u6ce8\u660e\u3001\u4e0d\u62a5\u9519**\uff08\u2605 \u907f\u514d\u5047\u9633\u6027\uff09
            if n.startswith("Add"):
                bad.append(("OFFICIAL_LOAD_SIGNATURES", "类型库里没有", n))
            else:
                skipped.append(n)
            continue''')
t = t.replace("    bad: list = []", "    bad: list = []\n    skipped: list = []")
t = t.replace('''    print("  比对三张表''', '''    if skipped:
        print("  注：%s 不在该接口上（★ 非 `Add*`）⇒ 跳过" % ", ".join(sorted(skipped)))
    print("  比对三张表''')
p.write_text(t, encoding="utf-8")
try:
    compile(t, str(p), "exec"); print("  \u2460 \u68c0\u67e5\u5668\u5df2\u4fee")
except SyntaxError as e:
    print("  \u2460 **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:70]))

#: \u2461 \u300a\u80fd\u529b\u5c42\u300b\uff1a`_REFGEOM_MEMBERS` \u6539\u4e3a**\u5e26\u4f4d\u7f6e**\uff0c`_check` \u6309\u4f4d\u7f6e\u6362
q = R / "scripts" / "sw_simulation_loads.py"
s = q.read_text(encoding="utf-8")
old = '''_REFGEOM_MEMBERS = frozenset({
    "AddForce", "AddForce2", "AddForce3", "AddPressure", "AddRestraint",
})'''
new = '''#: \u2605\u2605\u2605\u2605\u2605 2026-10-03\uff08\u8f6e 416\uff09**\u672c\u8868\u6539\u4e3a\u300c\u6210\u5458 \u2192 `RefGeom`/`RegGeom` \u7684\u5f62\u53c2\u4f4d\u7f6e\u300d**\uff08\u94c1\u5f8b 4\uff1a**\u4ee5\u51fa\u5382\u7c7b\u578b\u5e93\u4e3a\u51c6**\uff09\u3002
#:   \u2605 \u65e7\u8868\u662f\u4e00\u4e2a `frozenset`\uff0c\u2605 \u800c `_check` **\u5199\u6b7b\u4e86\u4f4d\u7f6e 2**\uff08\u7b2c 3 \u4e2a\u5b9e\u53c2\uff09\u3002
#:   \u2605\u2605 \u771f\u673a\u53cd\u5c04\uff08`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**\uff09\u7ed9\u51fa\u7684\u771f\u4f4d\u7f6e\uff1a
#:     ```
#:     AddForce(NForceType, DispArray, **RefGeom**)                      \u2192 \u4f4d\u7f6e 2
#:     AddForce2(NForceType, NSelectionType, DispArray, **RefGeom**)     \u2192 \u4f4d\u7f6e 3
#:     AddForce3(\u2026 19 \u4e2a\u2026, DispArray, **RefGeom**, PerUnitLength)         \u2192 \u4f4d\u7f6e 18
#:     AddPressure(NPressureType, DispArray, **RegGeom**)                \u2192 \u4f4d\u7f6e 2
#:     AddRestraint(NRestraintType, DispArray, **RefGeom**)              \u2192 \u4f4d\u7f6e 2
#:     AddPrescribedDisplacement(Displacements, NLengthUnit, DispArray, **RefGeom**) \u2192 \u4f4d\u7f6e 3
#:     ```
#:   \u21d2 \u2605 **\u6309\u4f4d\u7f6e\u6362\u624d\u5bf9**\uff0c\u2605 \u800c"\u4e00\u5200\u5207\u4f4d\u7f6e 2"\u4f1a\u628a `AddForce2`/`AddPrescribedDisplacement`
#:     \u7684 **`DispArray` \u5f53\u6210 `RefGeom` \u53bb\u6362** \u21d2 \u2605\u2605 \u90a3\u6bd4\u4e0d\u6362\u66f4\u574f\u3002
#:   \u2605 \u672c\u8868\u53ea\u5217**\u5df2\u4ece\u53cd\u5c04\u6838\u8fc7\u4f4d\u7f6e**\u7684\uff1b\u2605 \u8868\u5916\u7684\u4e0d\u6362\uff08\u94c1\u5f8b 5\uff09\u3002
_REFGEOM_POSITIONS = {
    "AddForce": 2,
    "AddForce2": 3,
    "AddForce3": 18,
    "AddPressure": 2,
    "AddRestraint": 2,
    "AddPrescribedDisplacement": 3,
}
#: \u2605 \u65e7\u540d\u4fdd\u7559\u4e3a\u53ea\u8bfb\u89c6\u56fe\uff08\u2605 \u4f9b\u65e2\u6709\u4ee3\u7801\u4e0e\u68c0\u67e5\u5668\u7528\uff09
_REFGEOM_MEMBERS = frozenset(_REFGEOM_POSITIONS)'''
if "_REFGEOM_POSITIONS" not in s:
    s = s.replace(old, new, 1)
    #: \u2605 `_check` \u7684\u66ff\u6362\u903b\u8f91\u6539\u4e3a**\u6309\u8868\u91cc\u7684\u4f4d\u7f6e**
    old2 = '''    if member in _REFGEOM_MEMBERS and len(tail) >= 3 and tail[2] is None \\
            and create_empty_dispatch_variant is not None:
        tail[2] = create_empty_dispatch_variant()'''
    new2 = '''    #: \u2605\u2605 2026-10-03\uff08\u8f6e 416\uff09\uff1a**\u6309\u300c\u8be5\u6210\u5458\u7684 `RefGeom` \u5728\u7b2c\u51e0\u4e2a\u5b9e\u53c2\u300d\u6362** \u2014\u2014
    #:   \u2605 \u65e7\u5199\u6cd5\u5199\u6b7b\u4e86 `tail[2]`\uff0c\u2605 \u800c\u53cd\u5c04\u8bf4 `AddForce2` \u5728 3\u3001`AddPrescribedDisplacement` \u5728 3\u3001
    #:   `AddForce3` \u5728 18 \u21d2 \u2605 \u7167\u65e7\u5199\u6cd5\u4f1a\u628a\u522b\u7684\u53c2\u6570\u5f53 `RefGeom` \u53bb\u6362\uff08\u6bd4\u4e0d\u6362\u66f4\u574f\uff09\u3002
    _pos = _REFGEOM_POSITIONS.get(member)
    if (_pos is not None and len(tail) > _pos and tail[_pos] is None
            and create_empty_dispatch_variant is not None):
        tail[_pos] = create_empty_dispatch_variant()'''
    if old2 in s:
        s = s.replace(old2, new2, 1)
        print("  \u2461 \u300a\u80fd\u529b\u5c42\u300b\u4e24\u5904\u5df2\u6539")
    else:
        print("  \u2461 **\u672a\u627e\u5230 `_check` \u7684\u66ff\u6362\u5757**")
    q.write_text(s, encoding="utf-8")
else:
    print("  \u2461 already")
try:
    compile(s, str(q), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  \u2461 **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:70]))
