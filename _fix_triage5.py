import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
src = p.read_text(encoding="utf-8")

#: \u2460 \u522b\u540d\u8868\uff1a\u52a0 `create_static_study`\uff08\u2605 \u4f9d\u636e\u5df2\u6838\uff1a\u5305\u88c5\u8c03\u7684\u5c31\u662f\u5b83\uff09
OLD = '''    ("sw_export", "export_to_image"):'''
NEW = '''    #: \u2605\u2605 2026-10-03\uff08\u8f6e 438\uff09\u65b0\u589e \u2014\u2014 \u2605 \u4f9d\u636e\u5df2\u6838\uff1a
    #:   `sw_simulation.create_study_report` **\u8c03\u7684\u6b63\u662f** `create_static_study`\uff08\u5df2\u8bfb\u6e90\u7801\uff09\uff0c
    #:   \u2605 \u800c\u5b83\u5c31\u662f\u5de5\u5177 `solidworks_simulation_create_study` \u7684 function\u3002
    ("sw_simulation", "create_static_study"):
        "solidworks_simulation_create_study\uff08\u2605 \u5b83\u7684 function `create_study_report` **\u8c03\u7684\u6b63\u662f** "
        "`create_static_study`\uff09",
    ("sw_export", "export_to_image"):'''
if "create_study_report" not in src:
    src = src.replace(OLD, NEW, 1)
    print("\u2460 \u5df2\u52a0 create_static_study \u522b\u540d")

#: \u2461 `select_face_at` \u21d2 **\u4e0d\u505a**\uff08\u2605 \u88f8\u5750\u6807 \u21d2 \u89c4\u5219 3 \u7981\u6b62\u628a\u5b83\u505a\u6210\u5de5\u5177\uff09
OLD2 = "KNOWN_DEAD_ENDS: dict[tuple[str, str], str] = {"
NEW2 = '''#: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 438\uff09**\u4e00\u6761\u6709\u539f\u5219\u7684"\u4e0d\u505a"** \u2014\u2014
#:   \u2605 \u6709\u4e9b\u51fd\u6570**\u672c\u6765\u5c31\u4e0d\u80fd**\u505a\u6210\u5de5\u5177\uff1a**\u5b83\u7684\u7b7e\u540d\u662f\u88f8\u5750\u6807**\u3002
#:   \u2605\u2605 \u4f9d\u636e\uff1a**\u89c4\u5219 3**\uff08\u672c\u4ed3\u4e94\u7edf\u4e00\u4e4b\u4e00\uff09\u2014\u2014\u300c**\u58f0\u660e\u5f0f `selection`\uff0c\u7981\u88f8\u5750\u6807**\u300d\uff1b
#:     \u2605 \u800c `tool_registry` \u5df2\u6709\u5bf9\u5e94\u95e8\u7981\uff08`_BARE_COORD_NAMES` + `_looks_like_coord_component`\uff09
#:     \u21d2 \u2605 \u5373\u4f7f\u628a\u5b83\u6302\u4e0a\uff0c**\u58f0\u660e\u4e5f\u4f1a\u8fc7\u4e0d\u4e86\u95e8\u7981** \u2713
#:   \u2605\u2605 \u6545\u5b83\u4e0d\u662f"\u8be5\u6302"\uff0c\u800c\u662f"\u4e0d\u505a"\uff08\u2605 \u800c\u7406\u7531\u662f**\u89c4\u5219**\uff0c\u4e0d\u662f"\u6211\u4eec\u6ca1\u529f\u592b"\uff09\u3002
CANNOT_BE_A_TOOL_WHY: dict[tuple[str, str], str] = {
    ("sw_simulation", "select_face_at"):
        "\u2605\u2605 \u5b83\u7684\u7b7e\u540d\u662f**\u88f8\u5750\u6807**\uff08`(model, x, y, z)`\uff09\u21d2 **\u89c4\u5219 3 \u7981\u6b62**"
        "\u628a\u5b83\u505a\u6210\u5de5\u5177\uff08\u2605 \u800c `tool_registry` \u7684\u58f0\u660e\u95e8\u7981**\u4f1a\u76f4\u63a5\u62e6\u4f4f**\uff09\u3002"
        "\u2605 \u5b83\u4ecd\u662f**\u5185\u90e8\u52a9\u624b**\uff08\u2605 \u591a\u5904\u8c03\u7528\uff09\u2014\u2014\u2605 \u53ea\u662f**\u4e0d\u80fd\u5bf9\u5916\u66b4\u9732**\u3002",
}


KNOWN_DEAD_ENDS: dict[tuple[str, str], str] = {'''
if "CANNOT_BE_A_TOOL_WHY" not in src:
    src = src.replace(OLD2, NEW2, 1)
    print("\u2461 \u5df2\u52a0 CANNOT_BE_A_TOOL_WHY")
#: \u2605 \u63a5\u8fdb classify\uff08\u2605 \u4e0e\u5176\u5b83"\u4e0d\u505a"\u540c\u7ea7\uff09
OLD3 = """    std_reason = is_empty_stub(module, name)"""
NEW3 = """    _cant = CANNOT_BE_A_TOOL_WHY.get((module, name))
    if _cant is not None:
        return "\u4e0d\u505a", _cant
    std_reason = is_empty_stub(module, name)"""
if "CANNOT_BE_A_TOOL_WHY.get" not in src:
    if OLD3 in src:
        src = src.replace(OLD3, NEW3, 1)
        print("\u2462 \u5df2\u63a5\u8fdb classify\uff08stub_reason \u90a3\u884c\uff09")
    else:
        OLD4 = """    stub_reason = is_empty_stub(module, name)"""
        src = src.replace(OLD4, NEW3.replace("std_reason", "stub_reason"), 1)
        print("\u2462 \u5df2\u63a5\u8fdb classify\uff08stub_reason \u90a3\u884c\uff09")
p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
