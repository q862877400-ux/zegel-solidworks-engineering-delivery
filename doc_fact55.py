"""记录：改了运行时文件后必须重跑 `sync_bundled_skill.py`（**git 不会提醒**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工作流纪律）
# 文件:   scripts/release_check.py（`find_bundled_skill_drift` 的判据）
#         scripts/sync_bundled_skill.py（**生成器**，276 个文件）
#         `.gitignore:23` —— `apps/workbench-ui/src-tauri/resources/` 被忽略
# 定位:   轮 43 修掉了**一个基线失败**（`test_release_check_passes_current_tree`）：
#         真因是**构建产物没生成**（不是代码 bug）。修完顺手记下这条纪律：
#         **改了任何运行时文件之后必须重跑同步**，否则 `release_check` 报漂移；
#         **⚠ 而快照在 `.gitignore` 里 ⇒ `git status` 看不见 ⇒ 这条纪律不会被 git 提醒。**
#         ★ 本轮还验证了改后的报错提示**是对的**：改完 `release_check.py` 再跑，
#           它立刻报 `与根 Skill 不一致: scripts/release_check.py`，而提示给的命令正是解法。
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

FACT55 = (
    "| 55 | **改了任何**运行时文件**之后必须重跑 `python scripts/sync_bundled_skill.py`** —— "
    "`release_check.py` 会比「仓库根的 Skill」与「桌面内嵌快照」"
    "（`apps/workbench-ui/src-tauri/resources/skill`），不一致就拦发布。"
    "**⚠ 而该快照在 `.gitignore:23` 里 ⇒ 它是**构建产物**、`git status` **看不见它** "
    "⇒ **这条纪律不会被 git 提醒你**。**"
    "★ 2026-10-01（轮 43）实测：修掉了一个**基线失败** `test_release_check_passes_current_tree`"
    "（回归从 **6 failed / 857 passed** 变成 **5 failed / 858 passed**）—— "
    "**真因是那一步构建没跑，不是代码 bug**；跑一次 `sync_bundled_skill.py`（276 个文件）即通过，"
    "且 `git status` **仍然干净**。"
    "★ 同轮还把报错改成**可执行**的：原来只报 "
    "`桌面内嵌 Skill 与根 Skill 不一致: <bundled-skill-missing>`（**看不出该怎么办**），"
    "现在**分开报两种情况**并各给出**可直接跑的命令**；"
    "**并且验证过它是对的** —— 改完 `release_check.py` 再跑，它立刻报 "
    "`与根 Skill 不一致: scripts/release_check.py`（**检查在尽职**），而提示给的命令正是解法。 | "
    "`scripts/sync_bundled_skill.py`；`scripts/release_check.py` 的 `find_bundled_skill_drift`；"
    "`.gitignore:23` |"
)

ROADMAP_ADD = (
    "            ⑬ ★★ **修掉一个**基线失败****（轮 43）：`test_release_check_passes_current_tree`\n"
    "               ⇒ 回归 **6 failed / 857 passed → 5 failed / 858 passed**\n"
    "               ★ 真因是**构建产物没生成**（`apps/workbench-ui/src-tauri/resources/skill` 在 `.gitignore` 里）\n"
    "               ⇒ 跑 `python scripts/sync_bundled_skill.py`（276 文件）即通过，**git 仍干净**\n"
    "               ★ 并把报错改成**可执行**的（原来 `<bundled-skill-missing>` 看不出该怎么办）\n"
    "               ★ 因此 `release_check` 现在**真的能跑到**轮 42 接的那道接口归属诊断\n"
)


def main() -> int:
    # ① AGENTS.md 事实 55
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    if any(l.lstrip().startswith("| 55 |") for l in src):
        print("  ⚠ 事实 55 已存在")
    else:
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| 54 |")), None)
        if i is None:
            print("  ✗ 找不到 | 54 | 行"); return 1
        src = src[:i + 1] + [FACT55 + "\n"] + src[i + 1:]
        f.write_text("".join(src), encoding="utf-8")
        print("  ✓ 已加已知事实 55")

    # ② ROADMAP
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = ("               ★ **它自己就在本轮抓到两处错**：① 用 `in` 判 `[HIT]` ⇒ 误报；\n"
              "                 ② 来源块写进 docstring ⇒ 来源门禁报 25 行缺出处（**已记进事实 54**）\n")
    if "修掉一个**基线失败**（轮 43）" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + ROADMAP_ADD, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ③ 落盘核对
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md | 55 |: %d 行" % t2.count("\n| 55 |"))
    print("    含「不会被 git 提醒」: %s" % ("是 ✓" if "不会被 git 提醒" in t2 else "**否**"))
    print("    ROADMAP 含「修掉一个**基线失败**（轮 43）」: %s"
          % ("是 ✓" if "修掉一个**基线失败**（轮 43）" in rt2 else "**否**"))
    ks = [k for k, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 15]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 15 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
