import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\triage_real_gaps.py")
src = p.read_text(encoding="utf-8")

#: \u2460 \u52a0\u90a3\u5f20\u8868\uff08\u2605 \u653e\u5728 `PLUMBING_WHY` \u9644\u8fd1\uff09
ANCHOR = "def classify("
TABLE = '''#: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 436\uff09**\u663e\u5f0f\u522b\u540d\u8868** \u2014\u2014 \u300c**\u529f\u80fd\u5df2\u7531\u53e6\u4e00\u4e2a\u540d\u5b57\u7684\u5de5\u5177\u8986\u76d6**\u300d\u7684\u90a3\u4e00\u7c7b\u3002
#:
#: \u2605\u2605 **\u4e3a\u4ec0\u4e48\u7528\u7a77\u4e3e\u8868\u800c\u4e0d\u662f\u518d\u653e\u5bbd\u89c4\u5219**\uff1a**\u4e8b\u5b9e 53** \u2014\u2014
#:   \u300c\u540c\u4e00\u4e2a\u542f\u53d1\u5f0f\u8fde\u7eed\u4fee\u8865 \u2265 3 \u6b21\u5c31\u8be5\u505c\u4e0b\u6362\u505a\u6cd5\uff1b\u2605 \u800c**\u6700\u4f18\u6362\u6cd5\u5e38\u662f
#:   \u628a\u731c\u6d4b\u53d8\u6210\u4e00\u5f20\u7a77\u4e3e\u8868**\u300d\u3002\u672c\u6863\u7684 `exposed_by_wrapper` / `exposed_by_prefix`
#:   \u5df2\u7ecf\u662f**\u4e24\u4e2a\u542f\u53d1\u5f0f**\uff08\u2605 `name + "_report"` \u4e0e `name + "_"` \u524d\u7f00\uff09\u2014\u2014
#:   \u2605 \u800c\u8fd9\u4e09\u6761**\u540d\u5b57\u5dee\u5f97\u591a**\uff0c\u542f\u53d1\u5f0f\u518d\u653e\u5bbd\u5c31\u4f1a\u541e\u771f\u7f3a\u53e3 \u21d2 \u2605\u2605 **\u6539\u6210\u663e\u5f0f\u767b\u8bb0**\u3002
#:
#: \u2605 **\u6bcf\u6761\u90fd\u5199\u6e05\u4f9d\u636e**\uff08\u2605 \u7167 `PLUMBING_WHY` \u7684\u5148\u4f8b\uff1a\u6ca1\u4f9d\u636e\u7684\u4e0d\u8bb8\u8fdb\u6765\uff09\u2014\u2014
#:   \u2605 \u800c\u8fd9\u4e09\u6761\u7684\u4f9d\u636e\u90fd\u662f**\u771f\u673a/\u9759\u6001\u53ef\u6838\u7684**\uff1a\u90a3\u4e2a\u5de5\u5177\u7684 `function` **\u8c03\u7684\u5c31\u662f\u5b83**\u3002
ALIASED_BY_TOOL: dict[tuple[str, str], str] = {
    ("sw_export", "export_to_bmp"):
        "solidworks_export_bmp\uff08\u2605 \u5b83\u7684 function `export_bmp_report` **\u8c03\u7684\u6b63\u662f** `export_to_bmp`\uff09",
    ("sw_export", "export_to_image"):
        "solidworks_export_image\uff08\u2605 `export_image_report` **\u8c03\u7684\u6b63\u662f** `export_to_image`\uff09",
    ("sw_export", "batch_export"):
        "solidworks_batch_export_files\uff08\u2605 `batch_export` \u662f `batch_export_formats` \u7684**\u8584\u5305\u88c5**\uff0c"
        "\u800c\u540e\u8005\u5c31\u662f\u90a3\u4e2a\u5de5\u5177\u7684 function\uff1b"
        "\u26a0 \u5b83\u5728 `server.py` \u4fa7\u58f0\u660e\uff0c\u2605 \u6545 `all_specs()` **\u770b\u4e0d\u5230\u5b83**\uff09",
}


'''
if "ALIASED_BY_TOOL" not in src:
    i = src.find(ANCHOR)
    src = src[:i] + TABLE + src[i:]
    print("\u2460 \u5df2\u52a0 ALIASED_BY_TOOL")

#: \u2461 \u63a5\u8fdb classify\uff08\u2605 \u653e\u5728\u6700\u524d\uff0c\u2605 \u4e0e KNOWN_DEAD_ENDS \u540c\u7ea7\uff09
OLD = """    stub_reason = is_empty_stub(module, name)"""
NEW = """    #: \u2605\u2605 2026-10-03\uff08\u8f6e 436\uff09**\u663e\u5f0f\u522b\u540d**\uff1a\u529f\u80fd\u5df2\u7531\u53e6\u4e00\u4e2a\u540d\u5b57\u7684\u5de5\u5177\u8986\u76d6\uff08\u2605 \u800c\u542f\u53d1\u5f0f\u63a8\u4e0d\u51fa\u6765\uff09
    _alias = ALIASED_BY_TOOL.get((module, name))
    if _alias is not None:
        return "\u5df2\u6709", "\u529f\u80fd\u5df2\u7531 `%s` \u8986\u76d6" % _alias
    stub_reason = is_empty_stub(module, name)"""
if "ALIASED_BY_TOOL.get" not in src:
    src = src.replace(OLD, NEW, 1)
    print("\u2461 \u5df2\u63a5\u8fdb classify()")
p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
