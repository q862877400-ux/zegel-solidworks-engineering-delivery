# 032 · 把台账剩下 20 条核完 —— 并查出一条「活的」

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
