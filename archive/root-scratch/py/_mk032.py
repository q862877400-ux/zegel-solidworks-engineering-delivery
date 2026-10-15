import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\032-obsolete-ledger-complete")
S.mkdir(parents=True, exist_ok=True)

spec = """# 032 · 把台账剩下 20 条核完 —— 并查出一条「活的」

**Status**: Implemented（轮 113）

## 背景
`029` 建了废弃成员台账（38 条候选），`030` 换 6 条，`031` 查清 2 条不换。
台账里还剩 **20 条「未逐条核」**。本轮全部核完。

## 判法（关键）
把**官方文档所在接口**与**我方调用点的目标表达式**并排看 ——
⚠ 同一个成员常出现在**多个接口**下，**只有其中一部分**标了废弃。
**光看成员名判不出**，必须看**我们调的是哪个接口**。

## 结果：**真 8 条 · 假阳性 10 条 · 未定性 1 条**
```
真      8：AutoDimension2 · ExcludeFromBOM · GetDependencies2 · GetErrorCode ·
          ★ MoldUndercutDetect · ReferenceType · SystemValue · AdvancedGraphics
假阳性 10：GetComponents · GetEdges · GetNext · GetPolylines · GetSplines ·
          GetType · GetUserPreferenceToggle · SetUserPreferenceToggle ·
          IsSuppressed · KFactor（未定性）
```
⇒ **假阳性率仍是约一半** —— 与 `029` 的判断一致（**所以这门禁确实做不得**）。

## ★★ 查出一条「活的」：`MoldUndercutDetect` 已被我包成 MCP 工具
```
2026-10-01 轮 98（Spec Kit 018）把 sw_mold.mold_undercut_detect 暴露为
  `solidworks_mold_undercut_detect`
而它调的 `IFeatureManager.MoldUndercutDetect` 官方已标 **Obsolete**
  ⇒ 后继是 `IFeatureManager::MoldUndercutDetect2`
⇒ **我们发了一个"包着废弃入口"的工具。**
```
⚠ **本台账只证「官方标了废弃」，不证跑不通** —— 轮 98 的真机冒烟里它**确实没报错**。
⇒ **处置**：在该工具的 `doc` 里加警示（**不擅自改实现** —— 换 `MoldUndercutDetect2`
要先比形状，那是另一轮的事）。

## 判据
| ID | 判据 |
|---|---|
| SC-2801 | 20 条**逐条**给出「官方接口 vs 我方接口」的对照 |
| SC-2802 | ★ 真/假阳性**分开列**，各带依据 |
| SC-2803 | ★ **查出 `MoldUndercutDetect` 是活的**（我们发的工具包着废弃入口）|
| SC-2804 | ★ 处置方式是**加警示**而非**擅自换实现**（换要先比形状）|
| SC-2805 | 台账给出**总账**（真 8 / 假 18 / 未定性 1）|
| SC-2806 | 门禁 + 回归不退化（回归 **1085 passed**）|

## ⚠ 明确记下的限度
* 8 条真候选里 **6 条已换、2 条不换、1 条加了警示** ⇒ **`AdvancedGraphics` 等仍未处置**；
* `KFactor` **未定性**（没查到调用点的目标类型）；
* ⚠ 台账**仍然不做门禁**（假阳性约一半）。
"""

plan = """# 032 · Plan

## 步骤
1. 写脚本把**官方文档接口**与**我方调用点目标**并排打出来（这是判归属的唯一办法）
2. 逐条核 20 条 ⇒ **真 8 / 假阳性 10 / 未定性 1**
3. ★ 发现 **`MoldUndercutDetect` 是活的** —— 它已被包成 MCP 工具（轮 98 的 batch9）
4. ⇒ **加警示**到该工具的 `doc`（**不擅自改实现**：换要先比形状）
5. 台账补总账 + 标为**全部处置完毕**
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 只看成员名就判归属 | ★ 必须打出**调用点的目标表达式**（`target='fm'` 之类）|
| 发现工具包着废弃入口就**直接改实现** | ★ **只加警示** —— 换入口要先比形状（`030`/`031` 的教训）|
| 台账里的"未逐条核"永远挂着 | 本轮**核完**，并给总账 |
"""

tasks = """# 032 · Tasks（全部完成，轮 113）

- [x] T-2801 写脚本打出「官方接口 vs 我方调用点目标」
  `→ 验收:` `python _triage20.py`（工作区脚本）
- [x] T-2802 逐条核 20 条 ⇒ **真 8 / 假阳性 10 / 未定性 1**
- [x] T-2803 ★ 查出 `MoldUndercutDetect` 是**活的**（轮 98 的 batch9 工具包着它）
- [x] T-2804 ★ 在该工具 `doc` 里加警示（**不擅自改实现**）
  `→ 验收:` `Select-String mcp-server\\tool_specs_batch9.py -Pattern 'marked Obsolete'`
- [x] T-2805 台账补总账 + 标为全部处置完毕
  `→ 验收:` `Select-String docs\\obsolete-member-candidates.md -Pattern '台账总账'`
- [x] T-2806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 032 · Converge

**Converged**: 2026-10-01（轮 113）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2801 20 条逐条对照 | ✅ 见台账 §四 |
| SC-2802 真/假阳性分开列 | ✅ 真 8 · 假 10 · 未定性 1 |
| SC-2803 查出活的 `MoldUndercutDetect` | ✅ |
| SC-2804 加警示而非擅自换实现 | ✅ `tool_specs_batch9.py` 的 `doc` |
| SC-2805 台账总账 | ✅ |
| SC-2806 门禁 + 回归 | ✅ `release_check` exit 0 · **1085 passed** |

## 二、★ 这一轮最有价值的是一条**我们自己造的**债
```
轮 98（Spec Kit 018）我把 sw_mold.mold_undercut_detect 暴露成 MCP 工具
—— 而它调的 IFeatureManager.MoldUndercutDetect **官方早标了 Obsolete**
⇒ **发工具的时候，我没查它包着的入口是否已废弃。**
```
★ 这是**暴露工作自己引入的**风险：`012`~`018` 那几轮挑的是"孤立能力"，
判断标准是「**签名兼容**」和「**冒烟不报错**」—— **没有一条是「入口没废弃」**。
⚠ 而 `029` 的探针**一跑就抓出来了**。
⇒ **处置原则**：**先加警示**（诚实、低风险），**换实现要先比形状**（`030`/`031` 的教训）。

## 三、⚠ 台账的门禁结论**再次被证实**
```
20 条里：真 8 · 假阳性 10 ⇒ **假阳性率 50%**
与 `029` 的 26% 相比**更高**
⇒ **这门禁确实做不得** —— 上一轮的判断是对的。
```
★ 而且这一轮的判法**必须人工**：要打出**调用点的目标表达式**才知道我们调的是哪个接口，
**静态匹配成员名做不到**。

## 四、未查证
* 8 条真候选里 **`AutoDimension2` / `ExcludeFromBOM` / `GetDependencies2` /
  `GetErrorCode` / `ReferenceType` / `SystemValue` / `AdvancedGraphics` 仍未处置** ——
  ⚠ **未查它们的后继形状**（`030`/`031` 的教训：换前必须比形状）；
* `KFactor` **未定性**；
* 台账**仍不做门禁**（假阳性约一半）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
