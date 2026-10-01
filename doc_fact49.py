"""记录：`source` 提案工具 + **纠正我自己**对 `sw_weldment/sw_sheet_metal` 归属的误认。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   tools/propose_capability_sources.py（提案工具，只打印不写文件）
#         `git cat-file -e origin/main:scripts/sw_weldment.py`（**硬证据**）
# 定位:   ⚠ **本补丁的核心是**纠正我自己**：**
#         我在多轮叙述里把 `sw_weldment.py` / `sw_sheet_metal.py` 当成「我们新增的」，
#         而硬证据显示它们**上游就有**（`origin/main` 里存在）。
#         **⇒ 工具的 `upstream` 判定是对的，错的是我的假设。**
#         这也让 AGENTS.md 事实 34 那句「**该模块**原本自述未在本机实测」有了正确主语：
#         那是**上游的**自述。
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

FACT49 = (
    "| 49 | **`sw_weldment.py` / `sw_sheet_metal.py` **是上游文件**，不是我们新增的** —— "
    "硬证据：`git cat-file -e origin/main:scripts/sw_weldment.py` **通过**。"
    "⚠ **我此前在文档与叙述里把这两个当成「我们新增的」（多次），那是错的。**"
    "⇒ 影响：AGENTS.md 事实 34 那句「**该模块**原本自述未在本机实测」的**主语是上游**；"
    "`capabilities[sheet_metal]` / `[weldments]` 的 `source` 应为 **upstream**。"
    "**⇒ 教训：判断「某文件是不是我们的」必须跑 `git cat-file -e origin/main:<path>`，"
    "不能靠印象**（与已知事实 37 的「查两处才敢说不存在」同源，方向相反）。"
    "工具：`tools/propose_capability_sources.py`（该工具正是靠这条硬证据，"
    "**并且它纠正了我**）| `git cat-file -e origin/main:scripts/sw_<X>.py`；"
    "`D:\\AI\\SW\\probe_*` 系列的对照 |"
)

ROADMAP_ADD = (
    "            ⑩ **`source` 提案工具已建**（`tools/propose_capability_sources.py`，**只打印不写文件**）：\n"
    "               用「关键词（含单复数归一）→ 文件名主干 → `git ls-tree origin/main` 硬证据」\n"
    "               得出 **upstream=11 / mixed=7 / original=3 / undetermined=8**（**21/29 有证据**）；\n"
    "               ★ **并纠正了我的一个误认**：`sw_weldment.py`/`sw_sheet_metal.py` **是上游文件**\n"
    "               ⇒ **A2 的下一步**：拿这份提案逐条人工确证后写入 `capabilities[].source`\n"
)


def main() -> int:
    # ① AGENTS.md 事实 49
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")
    i = t.find("| 48 |")
    if i < 0:
        print("  ✗ 找不到 | 48 |"); return 1
    if "| 49 |" not in t:
        e = t.find("\n", i) + 1
        f.write_text(t[:e] + FACT49 + "\n" + t[e:], encoding="utf-8")
        print("  ✓ AGENTS.md 已加已知事实 49")
    else:
        print("  ⚠ 事实 49 已存在")

    # ② T-011 追加（用短行列表，不跨行拼接）
    sec = WS / "_t011_section29.md"
    DOC = WS / "docs" / "T-011-expose-capabilities-assessment.md"
    if sec.is_file():
        with DOC.open("a", encoding="utf-8") as fh:
            fh.write(sec.read_text(encoding="utf-8"))
        print("  ✓ T-011 文档已追加「二十九」")
    else:
        print("  ⚠ 找不到 _t011_section29.md")

    # ③ ROADMAP
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    if "source` 提案工具已建" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif "阻塞:" in rt:
        j = rt.find("阻塞:")
        r.write_text(rt[:j] + ROADMAP_ADD + rt[j:], encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ④ 落盘核对（事实 48 第 ② 条）
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md | 49 |: %d 行" % t2.count("\n| 49 |"))
    print("    ROADMAP 含「source` 提案工具已建」: %s"
          % ("是" if "source` 提案工具已建" in rt2 else "**否**"))
    print("    T-011 含「二十九」: %s"
          % ("是" if "二十九" in DOC.read_text(encoding="utf-8") else "**否**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
