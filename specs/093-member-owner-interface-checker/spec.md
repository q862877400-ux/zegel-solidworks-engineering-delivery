# 093 · 新检查器：用出厂反射判「成员该在哪个接口」—— 命中 20 处，但抓不到它自己的动机

**Status**: Implemented（轮 173）· ⚠ **诊断工具，不接门禁**

## 一、动机（接轮 172）
轮 172 查出 `mold_evidence` 从**错的接口**读（成员在 `I*FeatureData` 上）。
★ 仓库**已有** `check_interface_member_ownership.py`，⚠ 但它只覆盖
「`data = CreateDefinition(<CONST>)` ⇒ `data.X`」**那一条路径**
⇒ ★★ **「从某个管理器直接取成员」这种形态它看不见** ⇒ 本轮补这个盲点。

## 二、判据（**可核验**，零启发式）
```
① 反射 `_raw/reflect_sldworks/iface_sldworks.txt` 有 `## <Iface>` 分段
   ⇒ 直接解析出 **接口名 → 成员名集合**（**1032 个接口 / 16732 个成员**）
② `X = get_com_member(<owner>, "<Member>")` ⇒ 由 `<owner>` 的接口查 `Member` 的**返回类型**
   ⇒ 得到 `X` 的接口（★ 返回类型就在反射行首：`FeatureManager get_FeatureManager()`）
③ `get_com_member(X, "<Member2>")` ⇒ `Member2` **完全不在** `X` 接口的谱系里 ⇒ **报**
```

## 三、★★★ 我一个人在这一处**连踩两个假阳性**
```
第一版：**113** 处
  根因① 反射里**属性带 `get_` 前缀**，而代码写不带前缀 ⇒ 属性读**全被误报**
第二版：**47** 处
  根因② 推不出接口时落到了 **`IObject` 兜底** ⇒ ★ **兜底值必然不在成员谱系里 ⇒ 必报**
第三版：**20** 处（去掉兜底：**推不出就留白、不检查**）
⇒ ★ 教训：**「推不出」不许用兜底值代替** —— 兜底会把「我不知道」变成「它有错」。
```

## 四、★★ 20 处高度可信（**独立于我的记忆**的两个佐证）
| 命中 | 实际在 | 佐证 |
|---|---|---|
| `IModelDoc2.GetBodies2` | `IPartDoc` / `IComponent2` | ★ **轮 161 真机踩过** |
| `ISketch.GetSketchSegments2` | 反射里**没有** | ★ **轮 162 真机踩过** |
| `IModelDoc2.GetSheetNames` | `IDrawingDoc` | — |
| `IModelDoc2.AddMate5` | `IAssemblyDoc` | — |
| `IPartDoc.GetTitle` | `IModelDoc` / `IModelDoc2` | — |

★ 并**核实**了判据本身：`FeatureByName` **确实不在 IModelDoc2 上**
（反射里只在 `IAssemblyDoc` / `IComponent2` / `IDrawingDoc` / `IPartDoc`）⇒ **不是解析漏了**。

## 五、⚠⚠⚠ 关键局限：**它抓不到它自己的动机**
```
`mold_evidence(model)` 的 owner 是**形参** ⇒ 静态推不出接口 ⇒ 被「留白」排除
⇒ ★★ **检查器抓不到 `mold_evidence`**（而那正是写它的起因）
```
★ 可补的两条路（**未做**）：① **docstring 的 `:param` 说明**；② **从调用点推**。

## 六、判据
| ID | 判据 |
|---|---|
| SC-9301 | ★★★ **反射给接口→成员表**（1032 接口 / 16732 成员），零启发式 |
| SC-9302 | ★★ 用**返回类型**推变量接口（反射行首）|
| SC-9303 | ★★★ **连踩两个假阳性并都修掉**（`get_` 前缀 · `IObject` 兜底）—— 如实记 |
| SC-9304 | ★★ 20 处命中**含两个真机踩过的坑** ⇒ 判据可信的独立佐证 |
| SC-9305 | ★★ **核实判据本身**（`FeatureByName` 确实不在 IModelDoc2）|
| SC-9306 | ⚠⚠⚠ **如实记「抓不到形参 owner」这个关键局限**（含动机本身）|
| SC-9307 | ⚠ **不接门禁**（判据未证到那个程度）· 检查量为 0 时非 0 退出（事实 46）|

## ⚠ 明确记下的限度
* ⚠ **抓不到形参 owner**（`mold_evidence` 就是这种）⇒ **动机未被覆盖**；
* ⚠ 20 处里仍有需**逐条真机核**的（如 `model` 到底是不是 `IModelDoc2` ⇒ `FeatureByName` 那处）；
* ⚠ **不接门禁** —— 判据还没证到能当门禁的程度（事实 53 同族：**证据进文档，不进工具**）；
* ⚠ 没有真机验证那 20 处（本轮**只做静态**）。
