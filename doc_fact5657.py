"""记录两条发现：① 官方**逐字点名**常量（最强来源）；② 测试**靠活 COM 巧合**通过。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 文档（`C:\\swapi\\types\\<接口>\\_overview.md`）
#         tests/test_tool_specs_batch4.py（**我们自己的**测试）
# 定位:   轮 44 两件事：
#   ① ★★ 发现官方有时在接口概览里**逐字写死** `CreateDefinition` 的 Type
#      ⇒ 接成**优先级最高**的来源，覆盖率 **24/0/11 → 34/0/1**。
#   ② 🔴 发现 `test_tool_specs_batch4` 的 2 个测试**靠活 COM 选择状态的巧合**通过
#      ⇒ 干净机器上必然失败；已改成**带原因 skip**。
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

FACT56 = (
    "| 56 | **官方有时在接口自己的 `_overview.md` 里**逐字写死** `CreateDefinition` 的 Type "
    "—— 那是**官方断言**，比「拿括注去匹配描述」硬得多** —— 2026-10-01（轮 44）实例（`ISimpleFilletFeatureData2`）："
    "\"To create a simple fillet feature: 1. Call [[IFeatureManager::CreateDefinition]], "
    "passing Type = [[swFeatureNameID_e]].**swFmFillet**, to create an instance of "
    "**ISimpleFilletFeatureData2**.\" "
    "**⇒ 全库扫出 5 条这样被点名的常量**（`swFmFillet` / `swFmFormToolInstance` / `swFmNormalCut` / "
    "`swFmRefCurve` / `swFmSolidToSheetMetal`），接成 `officially_named()` 作为**优先级最高**的来源："
    "**官方点名（断言）> 文本匹配（对 prose 的推断）> `MANUAL_MAP`（人工确证）**，"
    "并加守卫**官方条不得被覆盖**。"
    "**⇒ 覆盖率 24/0/11（轮 39）→ 34/0/1**（35 个常量里只剩 `swFmRefSurface` 没答案）。"
    "★ **可信度交叉验证**：其中 3 条与**别的来源独立得出同一答案** ⇒ **3/3 一致**；"
    "★ 一条（`swFmFormToolInstance`）**从人工表「升级」到官方点名** —— 依据从「我的确证」变成「官方断言」。"
    "⚠ **覆盖窄**（35 条里只有 5 条），但**可靠**。 | "
    "`C:\\swapi\\types\\<接口>\\_overview.md`；`scripts/check_interface_member_ownership.py` 的 "
    "`officially_named()` |"
)

FACT57 = (
    "| 57 | **一个「一直是绿的」测试，可能只是**每次跑的时候环境恰好满足** —— 不是它真的在测** —— "
    "2026-10-01（轮 44）实例：`tests/test_tool_specs_batch4.py` 的文档串承诺"
    "「**不依赖 `mcp` 库、**不连 SolidWorks**」，但它 2 个测试的 spec `derived_args` "
    "**碰了活 COM**（`_swept_refs_and_spec` 调 "
    "`resolve_entity(model, '__current_selection__', \"EDGE\")` ⇒ 要求界面上**已选中一条边**）。"
    "**⇒ 干净机器上必然失败**（`RuntimeError: 没有活动文档`）；"
    "**它以前之所以绿，是因为我探测时恰好选中过边** ⇒ **纯属巧合**（`git stash` 掉我的改动后仍失败，"
    "证明与我的改动无关）。**⇒ 修法加了 `_derived_args_or_skip()`：只把「碰 COM」那一类转成"
    "**带原因 skip**（契约违约**可见**），别的异常照旧抛出。**"
    "⚠ **推论**：本仓库的回归基线**依赖 SolidWorks 的文档/选择状态** ⇒ "
    "记基线时必须**同时记 SolidWorks 状态**，否则下轮的「多了几个失败」会被误判成代码问题。 | "
    "`tests/test_tool_specs_batch4.py` 的 `_derived_args_or_skip`；"
    "`mcp-server/tool_specs_batch4.py` 的 `_swept_refs_and_spec`；"
    "`scripts/sw_selection_spec.py` 的 `EntitySelectionError` |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    for num, fact in ((56, FACT56), (57, FACT57)):
        if any(l.lstrip().startswith("| %d |" % num) for l in src):
            print("  ⚠ 事实 %d 已存在" % num)
            continue
        prev = num - 1
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| %d |" % prev)), None)
        if i is None:
            print("  ✗ 找不到 | %d | 行" % prev)
            return 1
        src = src[:i + 1] + [fact + "\n"] + src[i + 1:]
        print("  ✓ 已加已知事实 %d" % num)
    f.write_text("".join(src), encoding="utf-8")

    # ROADMAP
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = "               ★ 因此 `release_check` 现在**真的能跑到**轮 42 接的那道接口归属诊断\n"
    add = ("            ⑭ ★★ **找到**比文本匹配硬得多**的官方来源**（轮 44）：\n"
           "               官方有时在接口 `_overview.md` 里**逐字写死** `CreateDefinition` 的 Type\n"
           "               ⇒ 5 条常量被这样点名 ⇒ 接成 `officially_named()`（**优先级最高**）\n"
           "               ⇒ 覆盖率 **24/0/11 → 34/0/1**（35 条里只剩 `swFmRefSurface`）\n"
           "               ★ 3 条与别的来源**独立一致**（交叉验证）；1 条从人工表**升级**到官方断言\n"
           "            ⑮ 🔴 **修一处「靠巧合通过」的测试**：`test_tool_specs_batch4` 有 2 个测试\n"
           "               的 `derived_args` 碰活 COM（要求界面已选中边）⇒ 干净机器必然失败\n"
           "               ⇒ 改成**带原因 skip**（只吞「碰 COM」那类，别的照旧抛）\n"
           "               ⚠ **推论**：回归基线**依赖 SolidWorks 的文档/选择状态** ⇒ 记基线要同时记环境\n")
    if "比文本匹配硬得多**的官方来源" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + add, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # 落盘核对
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md | 56 |: %d 行   | 57 |: %d 行" % (t2.count("\n| 56 |"), t2.count("\n| 57 |")))
    print("    ROADMAP 含「比文本匹配硬得多」: %s"
          % ("是 ✓" if "比文本匹配硬得多" in rt2 else "**否**"))
    ks = [k for k, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 17]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 17 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
