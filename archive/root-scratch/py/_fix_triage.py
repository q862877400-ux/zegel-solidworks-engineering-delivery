import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "tools" / "triage_real_gaps.py"
src = p.read_text(encoding="utf-8")

#: \u2460 **\u524d\u7f00\u522b\u540d**\uff1a\u4e00\u4e2a\u5df2\u6ce8\u518c\u7684 function \u82e5**\u4ee5 `name + "_"` \u5f00\u5934** \u21d2 \u5b83\u5df2\u88ab\u5305\u88c5
OLD1 = """def exposed_by_wrapper(name: str) -> str | None:"""
NEW1 = '''def exposed_by_prefix(name: str) -> str | None:
    """\u2605 \u2605\u2605 2026-10-03\uff08\u8f6e 432\uff09**\u524d\u7f00\u522b\u540d\u89c4\u5219** \u2014\u2014 \u4e00\u4e2a**\u5df2\u6ce8\u518c**\u7684 function
    \u82e5**\u4ee5 `name + "_"` \u5f00\u5934** \u21d2 \u8bf4\u660e\u90a3\u4e2a\u88f8\u51fd\u6570**\u5df2\u7ecf\u662f\u5de5\u5177\u7684\u4e00\u90e8\u5206**\u3002

    \u2605\u2605 \u771f\u4f8b\uff08\u672c\u8f6e\u53d1\u73b0\uff09\uff1a`sw_weldment.create_structural_member` \u4e00\u76f4\u88ab\u7b97\u6210\u300c\u8be5\u6302\u300d\uff0c
      \u2605 \u800c\u5b83\u5df2\u7ecf\u88ab\u5305\u6210\u4e86 `solidworks_weldment_create_structural_member`\uff08function =
      `create_structural_member**_from_sketch**`\uff09\u21d2 \u2605 **\u540d\u5b57\u4e0d\u540c \u2260 \u80fd\u529b\u6ca1\u6709**\u3002
    \u2605 \u800c\u65e7\u89c4\u5219\uff08`exposed_by_wrapper`\uff09**\u53ea\u8bd5** `base` \u4e0e `base + "_report"` \u21d2 \u2605 \u8ba4\u4e0d\u51fa\u8fd9\u4e00\u7c7b\u3002
    """
    have = have_tool_functions()
    for base in _name_variants(name):
        for cand in sorted(have):
            if cand.startswith(base + "_"):
                return cand
    return None


def used_by_other_module(module: str, name: str) -> bool:
    """\u2605 \u2605\u2605 2026-10-03\uff08\u8f6e 432\uff09**\u8de8\u6a21\u5757\u4f7f\u7528 \u21d2 \u5185\u90e8\u4ef6**\u3002

    \u2605\u2605 \u771f\u4f8b\uff1a`sw_selection_spec.entities_as_array` \u662f\u672c\u8f6e**\u65b0\u52a0\u7684\u52a9\u624b**\uff08\u7ed9\u591a\u5b9e\u4f53\u8f7d\u8377\u88c5\u6570\u7ec4\uff09\uff0c
      \u2605 \u800c\u5b83**\u5df2\u7ecf\u88ab `sw_simulation_loads` \u5f15\u7528** \u21d2 \u2605 \u5b83\u662f**\u5185\u90e8\u4ef6**\uff0c**\u4e0d\u662f\u5f85\u6302\u7684\u80fd\u529b**\u3002
    \u2605 \u5224\u636e\uff1a\u2605 \u5728 `scripts/` \u4e0b**\u9664\u5b83\u81ea\u5df1**\u5916\u6709\u4eba\u8c03\u5b83\u3002
    """
    own = ROOT / "scripts" / (module + ".py")
    for f in (ROOT / "scripts").glob("*.py"):
        if f == own:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:                                          # noqa: BLE001
            continue
        if name in text:
            return True
    return False


def exposed_by_wrapper(name: str) -> str | None:'''
if "def exposed_by_prefix" not in src:
    src = src.replace(OLD1, NEW1, 1)
    print("\u2460 \u5df2\u52a0 exposed_by_prefix / used_by_other_module")

#: \u2461 \u628a\u4e24\u6761\u63a5\u8fdb `classify()`\uff08\u2605 \u800c\u63a5\u5728**\u65e7\u89c4\u5219\u4e4b\u540e** \u2014\u2014 \u65e7\u8bed\u4e49\u4f18\u5148\uff09
OLD2 = """    wrapper = exposed_by_wrapper(name)
    if wrapper is not None:
        return "已有", ("功能已由 `%s` 包装暴露（★ 名字不同 ≠ 能力没有）" % wrapper)"""
NEW2 = """    wrapper = exposed_by_wrapper(name)
    if wrapper is not None:
        return "已有", ("功能已由 `%s` 包装暴露（★ 名字不同 ≠ 能力没有）" % wrapper)
    #: \u2605\u2605 2026-10-03\uff08\u8f6e 432\uff09**\u524d\u7f00\u522b\u540d**\uff1a`create_structural_member` \u21d0
    #:   `create_structural_member**_from_sketch**`\uff08\u5df2\u6ce8\u518c\uff09\uff08\u2605 \u771f\u4f8b\uff09
    prefixed = exposed_by_prefix(name)
    if prefixed is not None:
        return "\u5df2\u6709", ("\u529f\u80fd\u5df2\u7531 `%s` \u5305\u88c5\u66b4\u9732\uff08\u2605 **\u524d\u7f00\u522b\u540d**\uff1a"
                             "\u88f8\u51fd\u6570\u540d\u662f\u5305\u88c5\u540d\u7684\u524d\u7f00\uff09" % prefixed)
    #: \u2605\u2605 2026-10-03\uff08\u8f6e 432\uff09**\u8de8\u6a21\u5757\u4f7f\u7528 \u21d2 \u5185\u90e8\u4ef6**\uff1a
    #:   \u2605 \u522b\u4eba\u5df2\u7ecf\u5728\u7528\u5b83 \u21d2 \u5b83\u662f\u52a9\u624b\uff0c**\u4e0d\u662f\u5f85\u6302\u7684\u80fd\u529b**\uff08\u2605 \u771f\u4f8b\uff1a`entities_as_array`\uff09
    if used_by_other_module(module, name):
        return "\u5185\u90e8\u4ef6", ("\u2605 \u5df2\u88ab `scripts/` \u4e0b**\u522b\u7684\u6a21\u5757\u5f15\u7528** \u21d2 "
                                    "\u5b83\u662f**\u5185\u90e8\u52a9\u624b**\uff0c\u4e0d\u662f\u5f85\u6302\u7684\u80fd\u529b")"""
if "exposed_by_prefix(name)" not in src:
    src = src.replace(OLD2, NEW2, 1)
    print("\u2461 \u5df2\u63a5\u8fdb classify()")

p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
