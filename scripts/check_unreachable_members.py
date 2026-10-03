"""★ 门禁：**别去调那些"已证到不了"的成员**（★ 名单每条带证据）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_unreachable_members.py
# 定位:   ★ 2026-10-03（轮 579）★ 把**已证到不了**的成员固化成**静态门禁**。
#
#   ★★ **为什么需要它**：本仓已有两道与"名字"有关的门禁 ——
#     · `check_member_names.py` —— ★ 判「名字在**某个**接口里存在」（★ 事实 36 说它**抓不到**"接口不对"）
#     · `check_interface_member_ownership.py` —— ★ 判「成员属于**这个**接口」
#     ★ ★★ **而两者都不判「这个名字在本机的迟到绑定下**调不调得动**」** ⚠
#     ⇒ ★ 故本门禁补的正是**那一层**：★ **一份"已证到不了"的名单 + 逐条证据**。
#
#   ★★★ **名单的每一条都来自真机证据**（★ 不许凭印象加）：
#     | 成员 | 形态 | 证据 |
#     |---|---|---|
#     | `IMathUtility.CreatePoint` / `CreateVector` / `CreateTransform` | 不带 `I` ⇒ **找不到成员** | 事实 456 |
#     | `IMathUtility.ICreatePoint` / `ICreateVector` | 带 `I` ⇒ **无法读只写属性** | 事实 456 |
#     | `*FeatureData.AccessSelections`（**部分**接口，如 `ILinearPatternFeatureData`、`IProjectionCurveFeatureData`） | ⇒ **`0x80010105`** | 事实 425/426/446 |
#     | `InsertWeldmentCutList2` | **成员不在对象上** | 事实 428 |
#
#   ★★ **而"带 `I` 前缀"这条规律本身**（事实 456）：★
#     · **不带 `I`** 的名字 ⇒ `0x80020003` **找不到成员**
#     · **带 `I`** 的名字 ⇒ `61836` **无法读只写属性**（★ 与事实 47 的"进程内 C++ 指针变体"同族）
#     ⇒ ★ 故本门禁**对 `I` 前缀的成员给"提示级"告警**（★ 不拦 —— ★ 因为个例未必不成立）。
#
#   ★ 退出码：★ 命中 **deny 名单** ⇒ 1；★ 只有提示 ⇒ 0。
#   ★ 配套负例：`tests/test_unreachable_members_gate.py`（★ 事实 62：门禁"写了"不等于"有效"）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent

#: \u2605\u2605 **已证到不了** \u2014\u2014 \u10e1\u6bcf\u6761\u5e26\u8bc1\u636e\uff08\u2605 \u4e0d\u8bb8\u51ed\u5370\u8c61\u52a0\uff09
DENY: dict[str, str] = {
    # \u2605 \u4e8b\u5b9e 456\uff08\u8f6e 578\uff0c\u771f\u673a\uff09
    "CreatePoint": "\u4e8b\u5b9e 456\uff1a`IMathUtility.CreatePoint` \u21d2 `0x80020003` \u627e\u4e0d\u5230\u6210\u5458",
    "CreateVector": "\u4e8b\u5b9e 456\uff1a`IMathUtility.CreateVector` \u21d2 `0x80020003` \u627e\u4e0d\u5230\u6210\u5458",
    "CreateTransform": "\u4e8b\u5b9e 456\uff1a`IMathUtility.CreateTransform` \u21d2 `0x80020003` \u627e\u4e0d\u5230\u6210\u5458",
    "ICreatePoint": "\u4e8b\u5b9e 456\uff1a`IMathUtility.ICreatePoint` \u21d2 `61836` \u65e0\u6cd5\u8bfb\u53ea\u5199\u5c5e\u6027",
    "ICreateVector": "\u4e8b\u5b9e 456\uff1a`IMathUtility.ICreateVector` \u21d2 `61836` \u65e0\u6cd5\u8bfb\u53ea\u5199\u5c5e\u6027",
    # \u2605 \u4e8b\u5b9e 428\uff08\u8f6e 548\uff0c\u771f\u673a\uff09
    "InsertWeldmentCutList2": "\u4e8b\u5b9e 428\uff1a\u6210\u5458**\u4e0d\u5728\u5bf9\u8c61\u4e0a**\uff08`getattr` \u56de `NoneType`\uff09",
}

#: \u2605 \u53ea\u63d0\u793a\u3001\u4e0d\u62e6\uff08\u2605 \u4e2a\u4f8b\u672a\u5fc5\u4e0d\u6210\u7acb\uff09
WARN_PREFIX_I = True

#: \u2605\u2605 **\u53d6\u8bc1\u8c41\u514d**\uff1a\u2605 \u6709\u4e9b\u7ad9\u70b9**\u6545\u610f\u53bb\u8c03**\u5b83\uff08\u2605 \u4e3a\u4e86\u62ff\u5230\u201c\u5230\u4e0d\u4e86\u201d\u7684\u8bc1\u636e\uff09
#:   \u2014\u2014 \u2605 \u800c**\u8c41\u514d\u5fc5\u987b\u5e26\u7406\u7531**\uff1b\u2605 **\u65b0\u589e\u7684\u7ad9\u70b9\u4e0d\u4f1a\u81ea\u52a8\u8fdb\u6765**\uff08\u2605 \u90a3\u624d\u662f\u95e8\u7981\u7684\u4f5c\u7528\uff09\u3002
#: \u2605 2026-10-03\uff08\u8f6e 579\uff09\uff1a**\u672c\u6761\u662f\u95e8\u7981\u7b2c\u4e00\u6b21\u8dd1\u5c31\u903c\u51fa\u6765\u7684** \u2014\u2014
#:   \u2605 \u5b83\u547d\u4e2d\u4e86 3 \u5904\uff0c\u2605 \u800c\u90a3 3 \u5904**\u6b63\u662f\u4e8b\u5b9e 428 \u7684\u53d6\u8bc1\u4ee3\u7801** \u26a0
ALLOWED: dict[tuple[str, str], str] = {
    ("scripts/sw_weldment.py", "InsertWeldmentCutList2"):
        "\u2605 **\u53d6\u8bc1\u7ad9\u70b9**\uff1a\u4e8b\u5b9e 428 \u5c31\u662f\u8dd1\u5b83\u5f97\u51fa\u7684"
        "\uff08\u2605 \u90a3\u91cc\u5fc5\u987b**\u771f\u53bb\u53d6\u4e00\u6b21**\u624d\u80fd\u8bc1\u660e\u201c\u6210\u5458\u4e0d\u5728\u5bf9\u8c61\u4e0a\u201d\uff09",
    ("tools/probe_weldment_cutlist_recheck.py", "InsertWeldmentCutList2"):
        "\u2605 **\u63a2\u9488**\uff1a\u4e13\u95e8\u590d\u67e5\u4e8b\u5b9e 428 \u7684\u90a3\u4e00\u6761",
}

#: \u2605 \u626b\u54ea\u4e9b\u76ee\u5f55
ROOTS = ("scripts", "mcp-server", "tools")

#: \u2605 **\u8fd9\u4e24\u4e2a\u6587\u4ef6\u662f\u6570\u636e\u8868 / \u672c\u8eab**\uff0c\u2605 \u4e0d\u626b
SKIP = {"sw_api_sldworks.py", "check_unreachable_members.py"}

CALL_RE = re.compile(
    r"""(?:get_com_member|call_com_member|set_com_member)\s*\(\s*[^,()]+,\s*["']([A-Za-z_][A-Za-z0-9_]*)["']"""
)


def iter_calls(path: Path):
    """★ 逐行给出 ``(行号, 成员名)``（★ 正则够用：★ 本门禁只认**调用形态**）。"""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for i, line in enumerate(src.splitlines(), 1):
        for name in CALL_RE.findall(line):
            yield i, name


def scan() -> tuple[list[tuple[str, int, str, str]], list[tuple[str, int, str]]]:
    """★ 返回 ``(deny 命中, 提示命中)``。"""
    deny_hits: list[tuple[str, int, str, str]] = []
    warn_hits: list[tuple[str, int, str]] = []
    for root in ROOTS:
        base = R / root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.name in SKIP:
                continue
            for lineno, name in iter_calls(path):
                #: \u2605\u2605 **\u5f52\u4e00\u5316\u5206\u9694\u7b26**\uff1a`str(Path)` \u5728 Windows \u4e0a\u7ed9**\u53cd\u659c\u6760**\uff0c
                #:   \u2605 \u800c `ALLOWED` \u7684\u952e\u5199\u7684\u662f**\u6b63\u659c\u6760** \u21d2 \u2605 **\u952e\u6c38\u8fdc\u5bf9\u4e0d\u4e0a**\u3001
                #:   \u8c41\u514d\u9759\u9ed8\u5931\u6548 \u26a0\uff08\u2605 **\u8f6e 579 \u8e29\u5230**\uff09
                rel = path.relative_to(R).as_posix()
                if name in DENY:
                    #: \u2605 \u53d6\u8bc1\u8c41\u514d\uff1a**\u5fc5\u987b\u5e26\u7406\u7531**\u624d\u8df3\u8fc7
                    if (rel, name) in ALLOWED:
                        continue
                    deny_hits.append((rel, lineno, name, DENY[name]))
                elif WARN_PREFIX_I and name.startswith("I") and len(name) > 1 and name[1].isupper():
                    warn_hits.append((rel, lineno, name))
    return deny_hits, warn_hits


def main(argv: list[str] | None = None) -> int:
    deny, warn = scan()
    print("\u2605 \u53ef\u8fbe\u6027\u95e8\u7981\uff08\u2605 \u540d\u5355\u6bcf\u6761\u5e26\u8bc1\u636e\uff09")
    print("   \u626b\u4e86\uff1a%s" % ", ".join(ROOTS))
    print("   \u2605 deny \u540d\u5355\uff1a%d \u6761" % len(DENY))
    print()
    if deny:
        print("   \u2605\u2605 **\u547d\u4e2d\u4e86 %d \u5904\u201c\u5df2\u8bc1\u5230\u4e0d\u4e86\u201d\u7684\u6210\u5458**\uff1a" % len(deny))
        for rel, lineno, name, why in deny:
            print("      %s:%d  `%s`" % (rel, lineno, name))
            print("         %s" % why)
        print()
    if warn:
        print("   \u2605 \u63d0\u793a\uff08\u4e0d\u62e6\uff09\uff1a\u8fd9 %d \u5904\u7528\u4e86 **`I` \u524d\u7f00\u6210\u5458**"
              "\uff08\u2605 \u4e8b\u5b9e 456\uff1a\u5b83\u4eec\u5728\u8fdf\u5230\u7ed1\u5b9a\u4e0b**\u591a\u534a\u62a5\u201c\u53ea\u5199\u5c5e\u6027\u201d**\uff09\uff1a" % len(warn))
        for rel, lineno, name in warn[:12]:
            print("      %s:%d  `%s`" % (rel, lineno, name))
        if len(warn) > 12:
            print("      \u2026\u8fd8\u6709 %d \u5904" % (len(warn) - 12))
        print()
    if not deny:
        print("   [ok] \u6ca1\u6709\u547d\u4e2d\uff08\u2605 \u800c\u8fd9\u53ea\u8bf4\u660e\u201c\u6ca1\u8c03\u90a3\u4e9b\u540d\u5b57\u201d\uff0c"
              "\u2605 **\u4e0d\u8bc1\u660e\u522b\u7684\u90fd\u80fd\u8c03**\uff09")
    if argv is not None and "--quiet" in argv:
        return 1 if deny else 0
    return 1 if deny else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
