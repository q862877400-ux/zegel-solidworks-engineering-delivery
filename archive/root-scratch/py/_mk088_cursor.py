import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           508 🎯 **Spec Kit `088`：「一次性查」的盲区用****负例证实****；轮询成为默认（一处改动覆盖 34 个调用点）**（轮 168）——
               动机：轮 167 把 `residual_dialogs` 默认值改成了轮询，★ 但「**改了**」≠「**改对了**」（事实 62）
               ⇒ 本轮**制造出那个盲区并当场对比两种查法**。
            509 ★★★ **证伪实验**（`tools/verify_modal_polling_catches_async_dialog.py`）：
               ```
               ② **只查一次**（紧接触发 COM 调用）⇒ **0** 个框   ← ★★★ **漏了**（= 改之前 34 个调用点的形态）
               ③ **轮询 1.5 秒**                    ⇒ **1** 个框   ← ★★★ **抓到了**
               ④ 点掉 1 个 · 后台退出码 0
               ⇒ ★ 同一个弹窗、同一时刻附近，两种查法给出**相反结论** —— 本会话**最干净的一次负例证明**
               ```
            510 ⚠⚠ **实验第一版设计错了，如实记**：我把「一次性」写成了「**1.2 秒内循环查 19 次**」
               ⇒ **那本身就是轮询** ⇒ 命中 **14/19** ⇒ **没造出盲区**
               ⇒ ★ 我按判据**如实报了「本实验没造出盲区（不是"修好了"）」**，
                 然后才把对照组改成「**真的只查一次**」。
               ⇒ ★ 可复用的教训：**做「A 会不会漏」的实验时，对照组 A 必须真的是 A** ——
                 「重复查很多次」不是「只查一次」，把两者混起来会让实验**自动通过**（假阴性）。
            511 ★ **落地（一处改动覆盖 34 个调用点）**：
               ```
               residual_dialogs(pid=None, *, settle_seconds=1.0, poll_ms=200)
                 · 默认 settle_seconds=1.0 ⇒ **轮询**（34 个调用点全部受益，**不必改 34 个文件**）
                 · 默认 pid=None          ⇒ **自己从 COM 派生**（零硬编码）
                 · 要「只看此刻一眼」时显式传 settle_seconds=0.0（**保留可证伪性**）
                 · 取**整个窗口期内见过的最大值**（弹窗可能已被别人点掉，但「**弹过**」这个事实更重要）
               ```
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ 那 34 个调用点在**发现对话框**时，是否会让检查**失败**（而不只是打印）—— **未核**；
                 ⚠ 轮询让每个冒烟**多花约 1 秒**（安全换速度，接受）；⚠ 只处理 `#32770`；
                 ⚠ 「默认按钮是安全的」这个假设仍未验证（事实 107）。
               下轮候选：① **核那 34 个调用点发现对话框时会不会让检查失败**（否则"查到"仍是软信号）；
               ② 扫别处是否还有别的形态硬编码；③ 回到 `SetSymbolXml` 或「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+508 ", before, re.M):
    print("  游标 508 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+511 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 511 行已存在 ✓")
