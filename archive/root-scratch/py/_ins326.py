import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           326 🎯 **Spec Kit `050`：刷新 NOTICE 与审计报告 —— 并给 NOTICE 装上****机器检查******（轮 131）——
               ⚠ 「刷新」**不等于**「改一改」⇒ ★ **先复核，只改真的过时的**。
            327 ★ **复核 NOTICE 的三条可核断言 —— 三条都成立 ⇒ 一个字没动**：
               ```
               ① 「source_verified 条目数 0 ⇒ 尚未有来源派生的能力条目」 ⇒ **仍成立**（实测 0）
               ② mold_tools 的来源是 Eduardof0nt，**只取思路没抄代码** ⇒ §一.3 写得**准确且详细**
               ③ §一.4 依赖清单（含 numpy）⇒ 对得上（numpy 在 requirements-mesh/occt.txt 里）
               ```
            328 ★ **真正过时的只有 3 处**：`NOTICE 的登记历史只有 1 条`（fork 已 200+ 提交）·
               `final-audit` 的「215 次本地提交」⇒ 实际 **245** · 「31 条能力」⇒ 实际 **36**。
            329 ★★ **更重要的是装上机器检查**（A6 此前**只靠人读**）—— 5 条，其中两条最要紧：
               ```
               ② 「**能力条目里出现的每个外部 owner，NOTICE 里都必须有登记**」
                  ⇒ 把「**参考了谁就要登记谁**」从"人记得"变成"**漏了会红**"
                  ⇒ 而那正是**许可义务最容易漏的地方**
               ⑤ 「登记历史必须不止一条」—— ★ **故意指向它自己**：
                  写这条规则的动作**本身也必须被记进历史**，否则测试就红
                  ⇒ **本轮正是这样红了一次**（先 1 条 ⇒ 红 ⇒ 补历史 ⇒ 绿）
               ```
               ★★ 这种做法（**规则管到自己头上**）在本会话是**第一次**。
            330 ⚠ **一条被门禁自己写明的边界**（值得照抄）：
               `check_license_redlines` 原文：「本门禁判**声明是否自洽/越界**，**不判声明是否属实**」
               ⇒ ★ 本轮新增的 5 条**同一边界**：保证「**登记了**」，不保证「**登记属实**」。
               ★ 与 `029`/`032`（台账不做门禁）、`048`/`049`（判据的层与适用前提）**同一条脉络**：
                 **把门禁能保证的范围说清楚，不含糊。**
               ⚑ **未查证**：5 条**不保证登记属实**；`final-audit` 里「31 条存疑未定口径」是
                 **A3 口径的另一回事**，**本轮不动**；数字类断言**会随提交增长**，
                 已在更正处写明**重新数的命令**（`git rev-list --count origin/main..HEAD`）。
               许可门禁 **0 越界** · 回归 **1162 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把 `048` 的协议层检查接进常规回归（已可跑、不碰 COM）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+326 ", before, re.M):
    print("  游标 326 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+330 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 330 行已存在 ✓")
