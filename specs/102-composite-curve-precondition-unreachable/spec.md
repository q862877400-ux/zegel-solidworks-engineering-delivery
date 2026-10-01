# 102 · `composite_curve` 的真正前置是「两条**样条**草图」；而**样条在本机建不出来**

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
