import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_selection_spec.py")
lines = p.read_text(encoding="utf-8").splitlines()

#: \u2605 \u5b9a\u4f4d\u90a3\u4e2a for \u5faa\u73af\uff08L325 = index 324\uff09
start = next(i for i, l in enumerate(lines) if l.strip().startswith(
    'for _nm in ("GetSelectionPoint2", "GetSelectionPoint"):'))
end = next(i for i in range(start + 1, len(lines))
           if lines[i].strip() == "out[\"entry_used\"] = entry_used")

NEW = '''    #: \u2605\u2605\u2605\u2605 \u5b98\u65b9\u7b7e\u540d\uff08`C:\\swapi\\types\\ISelectionMgr\\GetSelectionPoint2.md`\uff09\uff1a
    #:     `GetSelectionPoint2( **Index**, **Mark** )` \u2014\u2014 \u2605 **\u4e24\u4e2a\u53c2\u6570**\uff1b
    #:     \u00b7 `Index` \u2605\u300cranges from **1** to \u2026\u300d\u21d2 \u2605 **\u7d22\u5f15\u4ece 1 \u8d77**\uff1b
    #:     \u00b7 `Mark`  \u2605 `-1` = \u5168\u90e8 \u00b7 `0` = \u65e0\u6807\u8bb0\u7684 \u00b7 \u5176\u5b83 = \u90a3\u4e2a\u6807\u8bb0\u503c\u3002
    #:   \u2605\u2605 **\u800c `GetSelectionPoint(AtIndex)` \u53ea\u6709 1 \u53c2**\uff08\u2605 \u5df2 Obsolete\uff09\u2014\u2014
    #:     \u26052026-10-03\uff08\u8f6e 397\uff09**\u771f\u673a\u6293\u5230**\uff1a\u2605 \u5148\u524d**\u7ed9\u4e24\u4e2a\u5165\u53e3\u90fd\u4f20 `(1, -1)`**
    #:     \u21d2 \u8d70\u5230 1 \u53c2\u90a3\u4e2a\u5fc5\u7136\u62a5 **`(-2147352562, '\u65e0\u6548\u7684\u53c2\u6570\u6570\u76ee\u3002')`**\uff0c
    #:     \u2605 \u800c\u90a3\u4e2a\u9519**\u6307\u4e0d\u51fa\u662f\u53c2\u6570\u4e2a\u6570\u7684\u95ee\u9898**\uff08\u2605 \u540c\u65cf\uff1a\u4e8b\u5b9e 33\uff09\u3002
    #:   \u21d2 \u2605 **\u6309\u540d\u5b57\u7ed9\u5404\u81ea\u7684 arity**\uff08\u2605 \u90a3\u6b63\u662f\u201c\u7b7e\u540d\u4e09\u6e90\u201d\u8be5\u7ed9\u51fa\u7684\u4e1c\u897f\uff09\uff0c
    #:     \u5e76\u4e14**\u4e24\u4e2a\u5165\u53e3\u7684\u62a5\u9519\u90fd\u7559\u4f4f**\uff08\u2605 \u5148\u524d\u662f\u540e\u8005\u8986\u76d6\u524d\u8005 \u21d2 \u770b\u4e0d\u5230 2 \u53c2\u90a3\u4e2a\u4e3a\u4ec0\u4e48\u5931\u8d25\uff09\u3002
    errors: list = []
    for _nm, _args in (("GetSelectionPoint2", (1, -1)), ("GetSelectionPoint", (1,))):
        cand = get_com_member(mgr, _nm)
        if cand is None:
            errors.append("%s \u4e0d\u53ef\u8fbe" % _nm)
            continue
        entry_used = _nm
        try:
            pt = cand(*_args)
        except Exception as exc:                               # noqa: BLE001
            errors.append("%s%s \u62a5\u9519\uff1a%s" % (_nm, _args, str(exc)[:130]))
            pt = None
            continue
        if pt is not None:
            break
        errors.append("%s%s \u56de None\uff08\u2605 \u9009\u4e2d\u7684\u53ef\u80fd\u4e0d\u662f\u70b9\uff09" % (_nm, _args))
    if pt is None and errors and out.get("error") is None:
        out["error"] = " \u00b7 ".join(errors)[:300]
'''

lines[start:end] = NEW.splitlines()
txt = "\n".join(lines) + "\n"
p.write_text(txt, encoding="utf-8")
try:
    compile(txt, str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
