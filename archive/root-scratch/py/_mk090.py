import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 110 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 110 | " + "".join([
    "**迁移后逐个真机跑：15/15 零破坏，而 2 个 fail 全是**早已记录在案**的** —— ",
    "2026-10-01（轮 170）。轮 169 迁了 34 个脚本的收尾（只查 → 查+点掉），但**只抽样跑了 2 个**；",
    "本轮把被迁的 **15 个 `verify_*`** 逐个真机跑（`tools/run_migrated_verify_smokes.py`）：",
    "```",
    "pass **13** · fail **2** · 没有 verdict **0** · 共 15",
    "★ 收尾行**都还在**: **15/15**            ⇒ 迁移后收尾确实在跑",
    "★ 收尾报「扫了 N 个窗口」且 N>0: **15/15** ⇒ **口径没有串**（0 就说明又串了，见事实 109）",
    "收尾兜底（settle_residual_dialogs）⇒ 发现 0 · 点掉 0 · 扫了 188",
    "```",
    "★★ **两个 fail 都是**既有**的**（**不是**本轮引入）：",
    "* `verify_gtol_smoke` **3/5** —— **轮 166 已知**（`IGtolFrame.AddIndicator` 20 组全不成）；",
    "* `verify_in_context_reference_smoke` **9/12** —— **轮 162 已知**（在上下文编辑链未打通）。",
    "⇒ ★★★ **「两个 fail 都能一句话说出出处」** 这件事本身就是**基线可信**的证据 ——",
    "与「多了几个说不清的失败」正好相反（后者通常意味着改动引入的）。",
    "★ 批量跑器的两个**口径**值得复用：",
    "① **「收尾行还在不在」**（迁移最容易悄悄删掉的就是收尾）；",
    "② **「收尾报的窗口数是不是 0」**（专门抓事实 109 那种「位置串了」的误报）。",
    " | `tools/run_migrated_verify_smokes.py`；`D:/AI/SW/output/migrated-verify-smokes.json`；",
    "事实 62 / 109 |",
])
if "| 110 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 110")
else:
    print("  已有 110")

# ── Spec Kit 090 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\090-migrated-smokes-all-run")
S.mkdir(parents=True, exist_ok=True)
spec = """# 090 · 迁移后逐个真机跑：15/15 零破坏，两个 fail 都能说出出处

**Status**: Implemented（轮 170）

## 一、动机（补上轮欠的账）
轮 169 迁了 34 个脚本的收尾（只查 → **查+点掉**），但**只抽样跑了 2 个** ⇒ 记为"未查证"。
★ 本轮把被迁的 **15 个 `verify_*`** 逐个真机跑（`tools/run_migrated_verify_smokes.py`）。

## 二、结果
```
pass **13** · fail **2** · 没有 verdict **0** · 共 15
★ 收尾行**都还在**: **15/15**             ⇒ 迁移后收尾确实在跑
★ 收尾报「扫了 N 个窗口」且 N>0: **15/15** ⇒ **口径没有串**（0 就说明又串了，见事实 109）
收尾兜底（settle_residual_dialogs）⇒ 发现 0 · 点掉 0 · 扫了 188
```

## 三、★★ 两个 fail 都是**既有**的，不是本轮引入
| 脚本 | 结果 | 出处 |
|---|---|---|
| `verify_gtol_smoke` | **3/5** | **轮 166 已知**（`IGtolFrame.AddIndicator` 20 组全不成）|
| `verify_in_context_reference_smoke` | **9/12** | **轮 162 已知**（在上下文编辑链未打通）|

> ★★★ **「两个 fail 都能一句话说出出处」这件事本身就是**基线可信**的证据** ——
> 与「多了几个说不清的失败」正好相反（后者通常意味着改动引入了问题）。

## 四、★ 批量跑器的两个**口径**（可复用）
```
① 「**收尾行还在不在**」—— 迁移最容易悄悄删掉的就是收尾；
② 「**收尾报的窗口数是不是 0**」—— 专门抓事实 109 那种「位置串了」的误报。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9001 | ★★ 被迁的 **15 个 `verify_*`** **逐个**真机跑（不是抽样）|
| SC-9002 | ★ 收尾行 **15/15 都还在** ⇒ 迁移没删掉收尾 |
| SC-9003 | ★★ 收尾**口径** 15/15 正常（不是 0）⇒ 抓的是事实 109 那类误报 |
| SC-9004 | ★★★ **两个 fail 都能一句话说出出处**（轮 166 / 轮 162）⇒ 基线可信 |
| SC-9005 | 事实 110 入库 |

## ⚠ 明确记下的限度
* ⚠ 只跑了 **`verify_*`**（15 个）；**17 个 `probe_*` 与 2 个 `diag_*` 未逐个跑**（探针不设 verdict，优先级低）；
* ⚠ 每个脚本自己管收尾；本跑器**只读它们的输出**，只在最后做一次兜底点掉；
* ⚠ `verify_gtol_smoke` 与 `verify_in_context_reference_smoke` 的 fail **仍是已知未解问题**，本轮**没有**解决它们。
"""
plan = """# 090 · Plan

## 步骤
1. 轮 169 迁了 34 个脚本但只抽样跑 2 个 ⇒ 记为"未查证"
2. ★ 列出被迁的 `verify_*`（**15 个**）
3. ★ 写批量跑器（顺序执行，COM 单实例）⇒ 逐个真机跑
4. ★★ 两个**新口径**：收尾行还在不在 · 收尾报的窗口数是不是 0
5. ⇒ **13 pass / 2 fail**，而两个 fail **都能说出出处**（轮 166 / 轮 162）
6. 事实 110 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 抽样跑 2 个就当"迁好了" | ★ 逐个跑（本轮）|
| 只数 pass/fail，不看收尾 | ★ **两个口径**专盯收尾 |
| 把既有的 fail 当新问题 | ★ **逐个 fail 说出出处**，说不出就是新问题 |
| COM 并发 | ★ **顺序执行**（事实 24）|
"""
tasks = """# 090 · Tasks（全部完成，轮 170）

- [x] T-9001 列出被迁的 `verify_*`（15 个）
- [x] T-9002 逐个真机跑 `→ 验收:` `python tools/run_migrated_verify_smokes.py`
  （**13 pass · 2 fail · 收尾 15/15**）
- [x] T-9003 两个 fail 逐一说出来处（轮 166 / 轮 162）
- [x] T-9004 事实 110
- [x] T-9005 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 090 · Converge

**Converged**: 2026-10-01（轮 170）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9001 逐个真机跑 | ✅ 15 个 |
| SC-9002 收尾行都在 | ✅ 15/15 |
| SC-9003 收尾口径正常 | ✅ 15/15 |
| SC-9004 两个 fail 说出出处 | ✅ 轮 166 / 轮 162 |
| SC-9005 事实 110 | ✅ |

## 二、★★★ 「能说出出处」是基线可信的证据
```
2 个 fail：verify_gtol_smoke 3/5（轮 166 已知）· verify_in_context_reference_smoke 9/12（轮 162 已知）
⇒ ★ 与「多了几个说不清的失败」正好相反 —— 后者通常意味着**改动引入了问题**。
⇒ 这给了一个可操作的判据：**跑完批量，先问"每个 fail 的出处是哪一条已知事实"**。
```

## 三、未查证
* ⚠ 只跑了 `verify_*`（15 个）；17 个 `probe_*` 与 2 个 `diag_*` **未逐个跑**；
* ⚠ `verify_gtol_smoke` / `verify_in_context_reference_smoke` 的 fail **仍未解决**（本轮只确认"不是迁移造成的"）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
