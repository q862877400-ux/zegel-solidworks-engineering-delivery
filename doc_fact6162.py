"""记录轮 46 的两条发现（**含一条严重事故**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律记录）
# 文件:   scripts/check_env_pitfalls.py（新门禁，已接进 release_check）
#         tests/test_env_pitfalls_gate.py（7 个契约测试）
#         apps/desktop/cad_workbench/queue_worker.py · tests/test_cad_studio_cli.py（**曾被我的脚本删行**）
# 定位:   轮 46 把两类环境坑做成硬门禁；**过程中我的批量脚本造成一次删 232 行的事故**。
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

F61 = (
    "| 61 | **批量改文件的脚本必须**先证明它只做加法** —— `git diff --stat` 出现 `deletions` 就要停下查** —— "
    "2026-10-01（轮 46）**严重事故**：我用一个「括号配对 + 就地插入」的脚本同时改两个文件，"
    "结果 `apps/desktop/cad_workbench/queue_worker.py` 的 `git diff --stat` 是 "
    "**`5 insertions(+), 232 deletions(-)`** —— **`process_queue` 连同 232 行消失**；"
    "`tests/test_cad_studio_cli.py` 末尾 5 行断言被删且丢了末尾换行。"
    "**⇒ 立刻 `git checkout --` 恢复两文件，改用 `edit` 工具逐处改**"
    "（差异回到正常的 `4 ++++` / `4 ++--`）。"
    "**⇒ 三条定则：① 批量脚本跑完**先看 `git diff --stat`**，有 `deletions` 就当成自己的 bug 查；"
    "② 能用 `edit` 工具逐处改就**不要**写批量替换脚本（尤其在有来源块的仓库里）；"
    "③ 改完**回读**被改文件（事实 48 定则②）。**"
    "⚠ 同一次事故里**事实 60 又重演**：我的脚本第二次改坏了来源块的**散文** —— "
    "**因为我在**门禁里**写了剥注释/字符串的函数，却**没在修复脚本里用**。**"
    "**⇒ 定则④：写了一个好用的工具函数，就要在**所有**同类场合用它，别只用在门禁里。** | "
    "`git log --oneline -p` 里轮 46 的恢复；`scripts/check_env_pitfalls.py` 的 "
    "`strip_comments_and_strings()`（门禁里用了、修复脚本里没用）|"
)

F62 = (
    "| 62 | **一个门禁「写了」不等于它「有效」—— 负例测试是唯一的证明** —— "
    "2026-10-01（轮 46）：我为「`Path(\"<盘符>:\")` 当盘根」（事实 59）写的门禁**第一版只认字面量** "
    "`Path(\"D:\")`，而**真 bug 的形态是 `root = Path(drive)`**（`drive` 是 `for drive in (\"D:\", \"E:\")` 的循环变量）"
    "⇒ **负例测试当场失败，证明门禁抓不到它真正要抓的东西**（「一个存在但没人用的守卫与没有守卫等价」）。"
    "**⇒ 补**轻量数据流**（先找被绑定成 `\"X:\"` 的变量名，再找 `Path(<那个变量>)`）后，"
    "用**修复前的原文**验证：`git show <修复前>:scripts/cad_installation.py` ⇒ **命中 1 处**，"
    "修复后 **0 处** ⇒ **这才叫「门禁能抓到那个 bug」。**"
    "⚠ 中途还试过「要求 `/` 紧邻 `Path(drive)`」—— **也抓不到**（中间隔了十几行才 `root / \"AutoCAD 2024\"`）"
    "⇒ 最终判据改为「`Path(\"D:\")` **本身**就该报」（盘根只有 `\"D:/\"` 一种正解，报它无害）。"
    "★ **可复用的手法：用 `git show <commit>^:<path>` 取**修复前**的原文当负例输入 —— "
    "比手写一个「像 bug 的样本」硬得多。** | "
    "`scripts/check_env_pitfalls.py` 的 `find_drive_only_root`；`tests/test_env_pitfalls_gate.py`；"
    "`git show 7ffa842^:scripts/cad_installation.py` |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    for num, fact in ((61, F61), (62, F62)):
        if any(l.lstrip().startswith("| %d |" % num) for l in src):
            print("  ⚠ 事实 %d 已存在" % num)
            continue
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| %d |" % (num - 1))), None)
        if i is None:
            print("  ✗ 找不到 | %d | 行" % (num - 1))
            return 1
        src = src[:i + 1] + [fact + "\n"] + src[i + 1:]
        print("  ✓ 已加已知事实 %d" % num)
    f.write_text("".join(src), encoding="utf-8")

    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = "               ★ release_check 也 pass；四项门禁全绿\n"
    add = ("            ⑰ ★ **把两类环境坑做成**硬门禁****（轮 46）：`scripts/check_env_pitfalls.py`\n"
           "               ⇒ 查「`subprocess` 缺 `encoding=`」（事实 58）与「`Path(\"盘符:\")` 当盘根」（事实 59）\n"
           "               ⇒ 接进 `release_check.py`；契约测试 **7 个**（5 个负例/防假阳性）\n"
           "               ★★ **负例测试当场证明第一版门禁是假的**（只认字面量，真形态是 `Path(drive)`）\n"
           "                 ⇒ 补轻量数据流，并用 **`git show <修复前>:<path>`** 验证 ⇒ **命中 1 处**、修复后 0 处\n"
           "               🔴 **同轮严重事故**：我的批量脚本**删了 `queue_worker.py` 的 232 行**\n"
           "                 ⇒ `git checkout --` 恢复 + 改用 `edit` 逐处改（事实 61：批量脚本先看 `git diff --stat`）\n"
           "               ⇒ 全量回归 **868 passed / 17 skipped / 0 failed**（861 + 7 新增）\n")
    if "把两类环境坑做成" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + add, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    for n in (61, 62):
        print("    AGENTS.md | %d |: %d 行" % (n, t2.count("\n| %d |" % n)))
    print("    ROADMAP 含「把两类环境坑做成」: %s"
          % ("是 ✓" if "把两类环境坑做成" in rt2 else "**否**"))
    ks = [k for k, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 22]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 22 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
