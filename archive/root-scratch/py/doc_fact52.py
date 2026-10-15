"""更新「映射表」的数字：20 唯一/4 歧义 → **24 唯一/0 歧义**（并保留历史）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   scripts/check_interface_member_ownership.py（**已加三条官方文本消歧规则**）
#         `C:\\swapi\\types\\<接口>\\_overview.md` 的 Description（**消歧依据的出处**）
# 定位:   第 30 轮造的映射表是 **20 唯一 / 4 歧义 / 11 未映射**；
#         **第 39 轮把 4 条歧义全消解** ⇒ **24 唯一 / 0 歧义 / 11 未映射**。
#         三条规则都从**官方描述**读出（见提交 e4794cc），其中第 ③ 条是**弱启发式**，
#         已在代码与提交信息里明确标注。
#         ⚠ **本补丁只改数字与结论，不改判据**（判据在代码里，已提交）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

#: 追加到事实 43 那一行**同一物理行**
F43_ADD = (
    "**★ 2026-10-01 消歧完成**：4 条歧义**全部解掉** ⇒ **24 唯一命中 / 0 歧义 / 11 未映射**。"
    "三条规则**都从官方描述读出**：① **含 `group` 者是子项**（两处 `*GroupData` 的描述都写着 "
    "\"feature group\" / \"feature's cut-extrude face group\"）⇒ 排除；"
    "② 剩下的里**含 `feature` 者优先**（`ICornerReliefFeatureData` \"…relief **feature data**\" "
    "vs `ISMCornerReliefData` \"…relief **data**\"）；"
    "③ ⚠ **兜底（弱启发式）**：描述**比常量括注多出的词最少**者优先 —— "
    "`swFmLibraryFeature (library)` ⇒ `ILibraryFeatureData`（+2 词）胜过 "
    "`ILibraryFormToolFeatureData`（+4 词）。**③ 已在代码注释与提交信息里标注为弱证据。**"
)

FACT52 = (
    "| 52 | **官方接口描述里藏着**判别类型的线索**，比接口名更可靠** —— "
    "2026-10-01 用它把 `CONST → 接口` 映射表的 **4 条歧义全部消解**（20→**24** 唯一命中、0 歧义）："
    "① **`group` 是子项的标志** —— `ISMNormalCutGroupData` 的描述是 "
    "\"…a normal cut **feature's cut-extrude face group**\"、`ITabAndSlotGroupData` 是 "
    "\"…a tab and slot **feature group**\" ⇒ **它们不是 `CreateDefinition` 返回的那个类型**；"
    "② **`feature` 的有无是层级标志** —— `ICornerReliefFeatureData` 是 \"…relief **feature data**\"、"
    "`ISMCornerReliefData` 是 \"…relief **data**\"（**少了 feature**）⇒ 前者才是。"
    "⚠ **但有一处只能靠弱启发式**：`swFmLibraryFeature` 的两个候选**都**含 `feature`，"
    "最后按「描述比常量括注**多出的词最少**者优先」选了 `ILibraryFeatureData`"
    "（+2 词 vs +4 词）—— **已在代码里标注为弱证据**。"
    "**⇒ 教训：先看**官方 prose**，再看名字；prose 分不开的，明确标成弱证据而不是假装确定。** | "
    "`C:\\swapi\\types\\<接口>\\_overview.md` 的 `## Description` 段；"
    "`scripts/check_interface_member_ownership.py` 的 `build_map()` |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    lines = f.read_text(encoding="utf-8").splitlines(keepends=True)

    # ① 事实 43 追加（同一物理行）
    i43 = next((i for i, l in enumerate(lines) if l.lstrip().startswith("| 43 |")), None)
    if i43 is None:
        print("  ✗ 找不到 | 43 | 行"); return 1
    if "消歧完成" in lines[i43]:
        print("  ⚠ 事实 43 的消歧已存在")
    else:
        lines[i43] = lines[i43].rstrip("\n") + F43_ADD + "\n"
        print("  ✓ 事实 43 已追加消歧结果（同一物理行）")

    # ② 事实 52
    if "| 52 |" in "".join(lines):
        print("  ⚠ 事实 52 已存在")
    else:
        i51 = next((i for i, l in enumerate(lines) if l.lstrip().startswith("| 51 |")), None)
        if i51 is None:
            print("  ✗ 找不到 | 51 | 行"); return 1
        lines = lines[:i51 + 1] + [FACT52 + "\n"] + lines[i51 + 1:]
        print("  ✓ 已加已知事实 52")
    f.write_text("".join(lines), encoding="utf-8")

    # ③ ROADMAP 游标
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = "               ★ **来源级门禁的负例测试已跑**：种 3 个坏来源 ⇒ **三条全被点名报出**（有牙齿）\n"
    add = ("            ⑪ **`CONST → 接口` 映射表已装上并**歧义清零****"
           "（20→**24** 唯一命中 / 0 歧义 / 11 未映射）：\n"
           "               `scripts/check_interface_member_ownership.py` 现在判「成员必须在**期望的**接口上」；\n"
           "               ★ **第 29 轮抓不到的 bug 现在抓得到**（负例实验：种入⇒精确报出 / 还原⇒OK）；\n"
           "               ★ 消歧三条规则**都从官方描述读出**（`group`=子项 / `feature`=层级 / 弱兜底）\n"
           "               ⇒ **下一步**：把剩下 **11 条未映射**（`swFmFillet`/`swFmSweep`/…）想办法补上\n")
    if "映射表已装上并**歧义清零**" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + add, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ④ 落盘核对
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    事实 43 行含「消歧完成」: %s"
          % ("是 ✓" if any(l.lstrip().startswith("| 43 |") and "消歧完成" in l
                           for l in t2.splitlines()) else "**否**"))
    print("    AGENTS.md | 52 |: %d 行" % t2.count("\n| 52 |"))
    print("    ROADMAP 含「歧义清零」: %s"
          % ("是 ✓" if "歧义清零" in rt2 else "**否**"))
    ks = [i for i, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 13]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 13 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
