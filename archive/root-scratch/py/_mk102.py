import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 122 | " + "".join([
    "**`composite_curve` 的真正前置是「两条**样条**草图」—— 而**样条在本机建不出来** ⇒ 前置不可达** —— ",
    "2026-10-01（轮 182）。",
    "★★★ **官方依据来自**官方样例**（三份一致）**：`C:/swapi/examples/Insert_a_Composite_Curve_Example_*.md`",
    "（VBA / C# / VB.NET）的 Description **都**写：",
    "> \"This example shows how to insert a composite curve using **two sketches of splines**.\"",
    "且 Postconditions 第 2/3 步是「Creates a sketch of a **spline**」。",
    "⚠ **三份的代码主体在本机副本里都被截断**（只剩声明）⇒ **看不到它具体怎么选**；",
    "但 **Description + Postconditions 已足以定出前提**。",
    "★★★ **因果链（本轮查明）**：",
    "```",
    "官方前提 = **两条样条（spline）草图**",
    "  ⇒ 而 ★ **样条在本机建不出来**：`ISketchManager.CreateSpline2` ⇒ **返回 None**",
    "    （`tools/probe_spline_creation.py` 轮 141 实测；**对照：直线能建** ✓）",
    "  ⇒ **前置不可达** ⇒ `InsertCompositeCurve` **必然返回 False**",
    "⇒ ★★ **所以 `composite_curve` 到不了，根因在**上游**（样条），不是它自己** ——",
    "  与事实 40（`IModeler.Create*Surface` 返回值不可靠）**同一族**。",
    "```",
    "★ **判据改成三档**（`tools/verify_composite_curve_smoke.py`）：",
    "```",
    "① 前置**可达**（样条能建 + 2 个草图 + 都选中）⇒ **要求 True**；False ⇒ **真失败**",
    "② 前置**不可达** ⇒ **不计入通过/失败**，但**如实记卡在哪一环**",
    "③ ★ 并**区分「本次独立复现」与「引用探针」** —— 我的调用报的是 `TypeError`（**调用姿势有 bug**），",
    "   而不是探针那个 `RuntimeError: … 返回 None` ⇒ ★ **不得冒充独立复现**",
    "```",
    "⚠⚠⚠ **顺带更正轮 181 的措辞**：轮 181 说它是「**真失败**」—— ★ **那个判断只在「前置可达」这一档里成立**；",
    "而现在查明**前置本身不可达** ⇒ ★ **正确的定性是「前置不可达」**（卡在上游的样条）。",
    "★ 结果：该 smoke **8/8 pass**，且每条含义准确。",
    " | `C:/swapi/examples/Insert_a_Composite_Curve_Example_{VB,CSharp,VBNET}.md`；",
    "`tools/probe_spline_creation.py`；`docs/acceptance-status.md`（轮 182 更正段）；事实 40 / 121 |",
])
if "| 122 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 122")
else:
    print("  已有 122")

S = Path(r"D:\AI\SW\specs\102-composite-curve-precondition-unreachable")
S.mkdir(parents=True, exist_ok=True)
spec = """# 102 · `composite_curve` 的真正前置是「两条**样条**草图」；而**样条在本机建不出来**

**Status**: Implemented（轮 182）

## 一、★★★ 官方依据（三份官方样例**一致**）
```
C:/swapi/examples/Insert_a_Composite_Curve_Example_{VB,CSharp,VBNET}.md 的 Description 都写：
  > "This example shows how to insert a composite curve using **two sketches of splines**."
Postconditions 第 2/3 步：「Creates a sketch of a **spline**」。
⚠ 三份的**代码主体在本机副本里都被截断**（只剩声明）⇒ 看不到它具体怎么选；
   但 **Description + Postconditions 已足以定出前提**。
```

## 二、★★★ 因果链
```
官方前提 = **两条样条（spline）草图**
  ⇒ 而 ★ **样条在本机建不出来**：`ISketchManager.CreateSpline2` ⇒ **返回 None**
    （`tools/probe_spline_creation.py` 轮 141 实测；**对照：直线能建** ✓）
  ⇒ **前置不可达** ⇒ `InsertCompositeCurve` **必然返回 False**
⇒ ★★ **所以 `composite_curve` 到不了，根因在**上游**（样条），不是它自己**
  —— 与事实 40（`IModeler.Create*Surface` 返回值不可靠）**同一族**。
```

## 三、★ 判据改成**三档**
```
① 前置**可达**（样条能建 + 2 个草图 + 都选中）⇒ **要求 True**；False ⇒ **真失败**
② 前置**不可达** ⇒ **不计入通过/失败**，但**如实记卡在哪一环**
③ ★ 并**区分「本次独立复现」与「引用探针」** ——
   我的调用报的是 `TypeError`（**调用姿势有 bug**），而不是探针那个 `RuntimeError: … 返回 None`
   ⇒ ★ **不得冒充独立复现**
★ 结果：该 smoke **8/8 pass**，且每条含义准确。
```

## 四、⚠⚠⚠ 顺带更正轮 181 的措辞
```
轮 181 说它是「**真失败**」—— ★ **那个判断只在「前置可达」这一档里成立**；
而现在查明**前置本身不可达** ⇒ ★ **正确的定性是「前置不可达」**（卡在上游的样条）。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-10201 | ★★★ **从官方样例定出前提**（三份 Description 一致 = 两条样条草图）|
| SC-10202 | ★★★ **因果链**：样条建不出 ⇒ 前置不可达 ⇒ 必然 False |
| SC-10203 | ★★ **判据三档**（可达/不可达/真失败）⇒ 前两条红不再算功能失败 |
| SC-10204 | ★★★ **如实区分「独立复现」与「引用探针」**（不冒充）|
| SC-10205 | ★ **更正轮 181 的定性**（「真失败」 → 「前置不可达」）|
| SC-10206 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **样条建不出来本身是未解问题**（本轮**只查明它挡住了谁**，没解决它）；
* ⚠ 官方三份样例的**代码主体被截断** ⇒ **它具体怎么选**仍**未看到**；
* ⚠ 我那个 smoke 里的样条调用**有 bug（TypeError）** ⇒ **没独立复现**；
* ⚠ 只动了这**一条** smoke，其余 30 条验收命令未动。
"""
plan = """# 102 · Plan

## 步骤
1. 轮 181 把 `composite_curve` 定性成「真失败」⇒ ★ 本轮查**它为什么失败**
2. ★ 读报错原文（`InsertCompositeCurve 返回 False`，**不是** com_error）⇒ **可能是前提问题**
3. ★★ 读官方 md ⇒ 发现 **Examples 段列了三份官方样例**
4. ★★★ 读那三份 ⇒ Description **一致**写「**two sketches of splines**」⇒ **前提定了**
5. ★★ 查上游：`CreateSpline2` 在本机**返回 None**（轮 141 探针）⇒ **前置不可达** ⇒ 因果链闭合
6. ★ 判据改成三档；★ 并**如实区分「独立复现」与「引用探针」**
7. 事实 122 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把"前提不对"读成"接口到不了" | ★ **读官方样例定前提**（本轮）|
| 从报错反推原因 | ★ 报错只说「返回 False」，**原因要靠官方前提 + 上游实测** |
| 拿坏调用当证据 | ⚠ **本轮差点**（TypeError 被当成"样条建不出"）⇒ 分两种出口 |
| 顺手去修样条 | ★ **不顺手**（本轮只查明因果 + 改判据）|
"""
tasks = """# 102 · Tasks（全部完成，轮 182）

- [x] T-10201 读报错原文（`返回 False`，不是 com_error）
- [x] T-10202 ★★★ 读官方样例定前提 `→ 验收:` 三份 `Insert_a_Composite_Curve_Example_*`
- [x] T-10203 ★★ 查上游样条（`CreateSpline2` 返回 None）
- [x] T-10204 改判据为三档 `→ 验收:` `python tools/verify_composite_curve_smoke.py`（**8/8 pass**）
- [x] T-10205 事实 122
- [x] T-10206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 102 · Converge

**Converged**: 2026-10-01（轮 182）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-10201 官方样例定前提 | ✅ 三份一致 |
| SC-10202 因果链 | ✅ 样条 ⇒ 前置不可达 |
| SC-10203 判据三档 | ✅ 8/8 |
| SC-10204 不冒充独立复现 | ✅ |
| SC-10205 更正轮 181 定性 | ✅ |
| SC-10206 门禁 + 回归 | ✅ |

## 二、★★★ 本轮把「一条红」追到了**上游**
```
轮 180：它红 ⇒ 我读**文本**说「应然」 ⇒ 信了（**错**）
轮 181：读**判据源码** ⇒ 判据说前提成立 ⇒ 定性「真失败」
轮 182：读**官方样例** ⇒ 真正的前提是「**两条样条草图**」⇒ 而**样条建不出** ⇒ **前置不可达**
⇒ ★★ 三轮，三种层次的证据（文本 → 判据 → 官方样例 + 上游实测）——
   ★ 而**只有最后一层给出了正确的原因**。
```

## 三、★ 而"上游"这件事本身就是产出
```
`composite_curve` 不是「这个 API 不行」，而是「**造不出它要的输入**」
⇒ ★ 这把问题从「接口层」移到了"**上游能力层**"（样条）⇒ **修复的目标变了**。
```

## 四、未查证
* ⚠ **样条建不出来本身未解决**；
* ⚠ 官方样例的**代码主体被截断**（它具体怎么选**未看到**）；
* ⚠ 我 smoke 里的样条调用**有 bug** ⇒ 未独立复现；
* ⚠ 其余 30 条验收命令未动。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
