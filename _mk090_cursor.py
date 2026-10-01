import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           517 🎯 **Spec Kit `090`：迁移后****逐个真机跑****：15/15 零破坏，两个 fail 都能说出出处**（轮 170）——
               动机：轮 169 迁了 34 个脚本的收尾（只查 → **查+点掉**）但**只抽样跑了 2 个** ⇒ 记为"未查证"
               ⇒ 本轮把被迁的 **15 个 `verify_*`** 逐个真机跑（`tools/run_migrated_verify_smokes.py`）。
            518 ★★ **结果**：
               ```
               pass **13** · fail **2** · 没有 verdict **0** · 共 15
               ★ 收尾行**都还在**: **15/15**             ⇒ 迁移后收尾确实在跑
               ★ 收尾报「扫了 N 个窗口」且 N>0: **15/15** ⇒ **口径没有串**（0 就说明又串了，见事实 109）
               收尾兜底（settle_residual_dialogs）⇒ 发现 0 · 点掉 0 · 扫了 188
               ```
            519 ★★★ **两个 fail 都是**既有**的（**不是**本轮引入）**：
               * `verify_gtol_smoke` **3/5** —— **轮 166 已知**（`IGtolFrame.AddIndicator` **20 组全不成**）；
               * `verify_in_context_reference_smoke` **9/12** —— **轮 162 已知**（在上下文编辑链未打通）。
               ⇒ ★★★ **「两个 fail 都能一句话说出出处」这件事本身就是**基线可信**的证据** ——
                 与「多了几个说不清的失败」正好相反（后者通常意味着**改动引入了问题**）。
               ⇒ ★ 可操作的判据：**跑完批量，先问「每个 fail 的出处是哪一条已知事实」**。
            520 ★ **批量跑器的两个**口径**（可复用）**：
               ```
               ① 「收尾行还在不在」—— 迁移最容易悄悄删掉的就是收尾；
               ② 「收尾报的窗口数是不是 0」—— 专门抓事实 109 那种「位置串了」的误报。
               ```
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ 只跑了 `verify_*`（15 个）；**17 个 `probe_*` 与 2 个 `diag_*` 未逐个跑**
                 （探针不设 verdict，优先级低）；⚠ `verify_gtol_smoke` / `verify_in_context_reference_smoke`
                 的 fail **仍未解决**（本轮只确认「不是迁移造成的」）。
               下轮候选：① 回到 `AddIndicator`（轮 166 的 20 组全不成，看换 `SetSymbolXml` 能否绕）；
               ② 回到在上下文链（轮 162 的 `SketchUseEdge3` 静默无效）；③ 扫别处是否还有别的形态硬编码。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+517 ", before, re.M):
    print("  游标 517 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+520 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 520 行已存在 ✓")
