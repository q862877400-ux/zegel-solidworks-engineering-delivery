import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           512 🎯 **Spec Kit `089`：「查到了」≠「处置了」—— 34 个脚本只检测模态框、****不点掉******（轮 169）——
               动机：核上轮标为「未核」的那一项（34 个调用点发现对话框时会不会让检查失败）。
            513 ★★★ **审计结果（真缺陷）**：
               ```
               35 个脚本检测模态框 ⇒ **34 个只检测、不点掉**
               ⇒ 若它真发现了弹窗，它**只打印一行**，而**弹窗还在**、COM 会话被它挡着
                 ⇒ **下一轮（或同一轮后续调用）就挂在那儿** —— 这正是轮 167 用户看到的情形
               ```
               ★ **按脚本自称的角色分类**（前缀就是角色）：`probe_`10 / `diag_`1 = **探针，只打印是对的**；
                 `verify_`5 = 验收冒烟 ⇒ ⚠ 上轮标为"未核"的那 3 处。
            514 ★★ **「判据本身也要验」的一次更正**：上轮我把「**发现对话框会不会让检查失败**」当成问题，
               本轮审计发现 —— ★ **真缺陷不是「喂不喂给 `chk`」**（那 3 处**其实都有 verdict**，
               只是判据在脚本末尾、不由 `residual_dialogs` 的结果驱动），
               而是「**发现了有没有处置**」（**34 个**）。
               ⇒ ★ 判据要先问「**我到底担心什么后果**」：担心的是**挂起**，不是「verdict 好不好看」。
            515 ★ **三条「查残留」的语义现在分清了**（同族于事实 62「绿≠对」）：
               ```
               residual_dialogs()          —— **只读**（可证伪性、测试用），默认**不点掉**
               count_residual_dialogs()    —— **只读**且只报计数（「发现」与「点掉」分开，轮 167 的教训）
               settle_residual_dialogs()   —— ★ **收尾专用：轮询 + 查到就点掉 + 三计数**（本轮新加）
               dismiss_residual_dialogs()  —— 只点掉，不报发现数
               ```
               ★ 迁移实测：**34 个脚本 = 13（赋值形态）+ 21（包装形态）** ⇒ 「**只查不点**」现在 **0 个**；
                 `git diff -U0` 审计：删 76 行 = **21+13（调用行）+ 42（插入注释块并掉的空行）** ⇒ **无意外删除**。
            516 ⚠⚠⚠ **同一轮我自己引入并修掉了一个**静默误报**（如实记）**：
               第一版迁移把 `X, Y = residual_dialogs()` 换成 `X, Y, Z = settle_residual_dialogs()` ——
               而 3 元组是 `(found, dismissed, scanned)`、旧 2 元组是 `(dialogs, all_windows)`
               ⇒ ★ **第 2 位从「扫过的窗口数」变成了「点掉的个数」** ⇒ 真机跑出来是「**扫了 0 个窗口**」（假的）。
               ★ **是靠真机跑一个被迁的脚本发现的**（不是靠读 diff）；修法：把 `scanned` 接回第 3 个名字。
               ⇒ ★ 可复用的教训：**改「返回值的个数」时，要逐个位置核对含义** ——
                 多一个返回值不是「加个变量」那么简单，**位置会串**。
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ 「默认按钮安全」这个假设仍未验证（事实 107）；⚠ 只处理 `#32770`；
                 ⚠ 迁移后**只抽样跑了 2 个**脚本（`probe_chamfer_forms` / `verify_interference_smoke`），
                 **没有逐个真机跑那 34 个**；⚠ 那 21 个包装的**上游调用点是否总调用包装**，**未核**。
               下轮候选：① 逐个真机跑被迁的脚本（或至少跑 `verify_*` 那批）；
               ② 扫别处是否还有别的形态硬编码；③ 回到 `SetSymbolXml` 或「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+512 ", before, re.M):
    print("  游标 512 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+516 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 516 行已存在 ✓")
