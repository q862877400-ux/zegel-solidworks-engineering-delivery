import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           574 🎯 **Spec Kit `102`：`composite_curve` 的真正前置是「两条****样条****草图」—— 而****样条在本机建不出来**** ⇒ 前置不可达**（轮 182）——
               轮 181 把它定性成「真失败」⇒ ★ 本轮查**它为什么失败**。
            575 ★★★ **官方依据来自**官方样例**（三份一致）**：`C:/swapi/examples/Insert_a_Composite_Curve_Example_*`
               （VBA / C# / VB.NET）的 Description **都**写：
               > "This example shows how to insert a composite curve using **two sketches of splines**."
               且 Postconditions 第 2/3 步是「Creates a sketch of a **spline**」。
               ⚠ 三份的**代码主体在本机副本里都被截断**（只剩声明）⇒ 看不到它具体怎么选；
                 ★ 但 **Description + Postconditions 已足以定出前提**。
            576 ★★★ **因果链（本轮查明）**：
               ```
               官方前提 = **两条样条（spline）草图**
                 ⇒ 而 ★ **样条在本机建不出来**：`ISketchManager.CreateSpline2` ⇒ **返回 None**
                   （`tools/probe_spline_creation.py` 轮 141 实测；**对照：直线能建** ✓）
                 ⇒ **前置不可达** ⇒ `InsertCompositeCurve` **必然返回 False**
               ⇒ ★★ **所以 `composite_curve` 到不了，根因在**上游**（样条），不是它自己** ——
                 与**事实 40**（`IModeler.Create*Surface` 返回值不可靠）**同一族**。
               ```
            577 ★ **判据改成三档**（`tools/verify_composite_curve_smoke.py`）：
               ```
               ① 前置**可达** ⇒ **要求 True**；False ⇒ **真失败**
               ② 前置**不可达** ⇒ **不计入通过/失败**，但**如实记卡在哪一环**
               ③ ★ 并**区分「本次独立复现」与「引用探针」** —— 我的调用报的是 `TypeError`
                  （**调用姿势有 bug**），而不是探针那个 `RuntimeError: … 返回 None`
                  ⇒ ★ **不得冒充独立复现**
               ⇒ ★ 结果：该 smoke **8/8 pass**，且每条含义准确。
               ```
            578 ⚠⚠⚠ **顺带更正轮 181 的措辞**：轮 181 说它是「**真失败**」—— ★ 那判断**只在「前置可达」这一档里成立**；
               而现在查明**前置本身不可达** ⇒ ★ **正确措辞是「前置不可达」**（卡在上游的样条）。
               ★★★ **三轮、三种层次的证据，只有最后一层给出了正确的原因**：
               ```
               轮 180：读**失败文本**（"属应然"）⇒ **信了**（错）
               轮 181：读**判据源码**  ⇒ 判据说前提成立 ⇒ 定性「真失败」
               轮 182：读**官方样例** + **上游实测** ⇒ **前置不可达** ⇒ ★ **这才是对的原因**
               ```
               ★ 并把问题从「**接口层**」移到了「**上游能力层**（样条）」⇒ **修复目标变了**。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **样条建不出来本身未解决**（本轮只查明它挡住了谁）；
                 ⚠ 官方样例的**代码主体被截断** ⇒「它具体怎么选」**未看到**；
                 ⚠ 我 smoke 里的样条调用**有 bug（TypeError）** ⇒ **未独立复现**；
                 ⚠ 只动了这**一条** smoke，其余 **30 条**验收命令未动。
               下轮候选：① 攻**样条**（`CreateSpline2` 返回 None，事实 40 族）—— 它挡着不止一个能力；
               ② 处理 `part_and_features` 那条 evidence（它引用的 smoke 现在 8/8，可复核其定性）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+574 ", before, re.M):
    print("  游标 574 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+578 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 578 行已存在 ✓")
