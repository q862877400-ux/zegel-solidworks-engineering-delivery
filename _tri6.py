import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
t = p.read_text(encoding="utf-8")

OLD = '''def exposed_by_wrapper(name: str) -> str | None:
    """\u2605 \u82e5 `name` \u7684**\u5305\u88c5\u53d8\u4f53**\u5df2\u6709\u5de5\u5177 \u21d2 \u56de\u90a3\u4e2a\u540d\u5b57\uff1b\u5426\u5219 `None`\u3002"""
    have = have_tool_functions()
    for cand in (name + "_report", "create_" + name + "_report", name + "2_report"):
        if cand in have:
            return cand
    return None'''

NEW = '''#: \u2605 \u52a8\u8bcd\u5bf9\uff08\u8f6e 402\uff09\uff1a\u4f4e\u5c42\u539f\u8bed\u53eb `add_X`\uff0c\u2605 \u800c**\u5bf9\u5916\u5c01\u88c5**\u53eb `apply_X`
#:   \uff08\u2605 \u771f\u4f8b\uff1a`sw_simulation_loads.add_fixed_restraint(manager, entities, \u2026)` \u5403 **COM manager**\uff0c
#:   \u2605 \u800c `sw_simulation.apply_fixed_restraint` \u624d\u662f\u53d6 manager + \u6784\u9020\u6570\u7ec4 + \u8c03\u539f\u8bed\u7684\u90a3\u4e00\u5c42\uff0c
#:   \u2605\u2605 \u800c**\u540e\u8005\u5df2\u7ecf\u662f\u5de5\u5177**\uff09\u3002
#:   \u21d2 \u2605 \u53ea\u770b `_report` \u540e\u7f00\u4f1a**\u628a\u8fd9\u4e00\u6574\u65cf\u8bef\u5224\u6210\u7f3a\u53e3**\u3002
_VERB_PAIRS = ("apply", "create", "set", "insert", "remove")


def _name_variants(name: str) -> list:
    """\u2605 `name` \u53ca\u5176**\u52a8\u8bcd\u6362\u5199**\u7684\u5019\u9009\uff08\u2605 \u4e0d\u6539\u5176\u4f59\u90e8\u5206\uff09\u3002"""
    out = [name]
    if name.startswith("add_"):
        tail = name[4:]
        out.extend("%s_%s" % (v, tail) for v in _VERB_PAIRS)
    return out


def exposed_by_wrapper(name: str) -> str | None:
    """\u2605 \u82e5 `name`\uff08\u6216\u5b83\u7684**\u52a8\u8bcd\u6362\u5199**\uff09\u7684**\u5305\u88c5\u53d8\u4f53**\u5df2\u6709\u5de5\u5177 \u21d2 \u56de\u90a3\u4e2a\u540d\u5b57\u3002

    \u2605 \u4e24\u7c7b\u4faf\u9009\uff1a\u2460 \u540c\u540d + `_report`\uff1b\u2461 **\u52a8\u8bcd\u6362\u5199**\uff08`add_X` \u21d2 `apply_X` \u7b49\uff09+ `_report`\u3002
    """
    have = have_tool_functions()
    for base in _name_variants(name):
        for cand in (base, base + "_report", base + "2_report"):
            if cand in have:
                return cand
    return None'''

if "_VERB_PAIRS" not in t:
    t = t.replace(OLD, NEW, 1)
    p.write_text(t, encoding="utf-8")
    print("  已加动词对规则")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:76]))
