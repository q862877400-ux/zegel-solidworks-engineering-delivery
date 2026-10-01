"""更新映射表数字（24/0/11 → **31/0/4**，其中 7 条为**人工确证**）+ 游标 + 工具自身文档串。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   scripts/check_interface_member_ownership.py（**已加 `MANUAL_MAP`**）
#         D:\\AI\\SW\\docs\\T-040-unmapped-constants-evidence.md（7 条的证据）
# 定位:   轮 40 回退后，轮 41 **把 7 条 ★ 人工确证的映射作为显式 `MANUAL_MAP` 接进去**
#         ⇒ **31 唯一（自动 24 + 人工 7）/ 0 歧义 / 4 未映射**。
#         **⚠ 与轮 40 的关键区别：这次是**人工表 + 每条注明依据**，不是启发式硬凑。**
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
CODE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_interface_member_ownership.py")

F43_ADD = (
    "**★★ 2026-10-01 再进一步（轮 41）**：把**已逐条读官方描述确认**的 7 条写进显式的 "
    "`MANUAL_MAP` ⇒ **31 唯一（**自动 24 + 人工确证 7**）/ 0 歧义 / 4 未映射**"
    "（原 24/0/11）。**⚠ 与轮 40 那次失败的关键区别：这次是**人工表、每条在代码里注明依据**，"
    "不是启发式硬凑**（轮 40 用「名字回退」连续改 6 版都不对，已回退并记进已知事实 53）。"
    "三条设计约束：① **绝不覆盖**自动结果（只补空）；② **输出分开报**（「自动 %d + 人工确证 %d」）；"
    "③ **没有依据的不许进来**（未确证的 4 条留在 `unmapped`，按铁律 5 写「查不到」）。"
)

ROADMAP_ADD = (
    "               ★★ **再进一步（轮 41）**：把 7 条 ★ 人工确证的映射写进显式 `MANUAL_MAP`\n"
    "                 ⇒ **31 唯一（自动 24 + 人工确证 7）/ 0 歧义 / 4 未映射**\n"
    "                 ⚠ **不是启发式**（轮 40 的「名字回退」连续改 6 版都不对，已回退 —— 事实 53）\n"
    "                 ⇒ 三条约束：只补空不覆盖 / 输出分开报 / 没依据的不许进\n"
    "               ⇒ **下一步**：剩下 4 条未映射（`swFmDimPattern`/`swFmSolidToSheetMetal`/\n"
    "                 `swFmRefSurface`/`swFmFillet`）**需要人**逐条核（已列进 T-040 证据文档）\n"
)

DOC_OLD = ("       （第 30 轮实测：20 唯一 / 4 歧义 / 11 未映射）")
DOC_NEW = ("       （第 30 轮：20/4/11 ⇒ **第 41 轮：31 唯一（自动 24 + 人工确证 7）/ 0 歧义 / 4 未映射**）")


def main() -> int:
    # ① AGENTS.md 事实 43
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    i43 = next((i for i, l in enumerate(src) if l.lstrip().startswith("| 43 |")), None)
    if i43 is None:
        print("  ✗ 找不到 | 43 | 行"); return 1
    if "再进一步（轮 41）" in src[i43]:
        print("  ⚠ 事实 43 已更新")
    else:
        src[i43] = src[i43].rstrip("\n") + F43_ADD + "\n"
        f.write_text("".join(src), encoding="utf-8")
        print("  ✓ 事实 43 已追加轮 41 结果")

    # ② ROADMAP
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = "               ⇒ **下一步**：把剩下 **11 条未映射**（`swFmFillet`/`swFmSweep`/…）想办法补上\n"
    if "再进一步（轮 41）" in rt:
        print("  ⚠ ROADMAP 已更新")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + ROADMAP_ADD, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ③ 工具自身的文档串（数字过时了 —— 事实 3「文档串与代码不符比没有文档更糟」）
    t = CODE.read_text(encoding="utf-8")
    if DOC_OLD in t:
        CODE.write_text(t.replace(DOC_OLD, DOC_NEW, 1), encoding="utf-8")
        print("  ✓ 工具文档串里的过时数字已更新")
    else:
        print("  ⚠ 工具文档串未匹配（可能已更新）")

    # ④ 落盘核对
    print()
    print("  ── 落盘核对 ──")
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print("    事实 43 含「再进一步（轮 41）」: %s"
          % ("是 ✓" if any(l.lstrip().startswith("| 43 |") and "再进一步（轮 41）" in l
                           for l in t2.splitlines()) else "**否**"))
    print("    ROADMAP 含「人工确证 7」: %s" % ("是 ✓" if "人工确证 7" in rt2 else "**否**"))
    c2 = CODE.read_text(encoding="utf-8")
    print("    工具文档串含「第 41 轮」: %s" % ("是 ✓" if "第 41 轮" in c2 else "**否**"))
    ks = [i for i, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 13]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 13 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
