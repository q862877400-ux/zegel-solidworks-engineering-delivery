# api-04-assembly.md —— 装配域官方契约抄录（Explode / Pattern / Lightweight / Interference / Mate）

> 抄录员立场：只抄亲手读到的东西。查不到 = 写「查不到」。不给建议、不下结论。
> 抄录日期：本次会话。全部来源为本机离线源，未联网。

---

## 0. 来源核对与本文件的读法

| 来源 | 本次是否命中 | 说明 |
|---|---|---|
| `C:\swapi\types\<接口>\<成员>.md` | **命中**（精确签名 + `## Remarks` + `## Examples` 链接的唯一来源） | 本文件第 1–5 项里的「签名 / Remarks / 废弃链」全部逐字出自这里 |
| `C:\swapi\examples\*.md` | **命中**（官方例子调用序） | 每条例子文件自带 `**Source**: sldworksapi/<原名>.htm` |
| `C:\swapi\enums\*.md` | **部分命中** | 命中 `swMateType_e` `swMateAlign_e` `swAddMateError_e` `swDistanceMateArcConditions_e` `swMateWidthOptions_e` `swComponentResolveStatus_e` `swComponentSuppressionState_e` `swExplodeDirectionIndex_e` |
| `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` | **★未命中成员参考页** | 该目录共 11 579 个文件，逐个点名核对：`AddMate5_Method.htm` / `IToolsCheckInterference3_Method.htm` / `CreateExplodedView_Method.htm` / `SetSuppression2_Method.htm` / `ExplodeStep_Property.htm` —— **全部不存在**；该目录下非 `*Example*` 的 `.htm` 只有 `ApiHelp.css`、宏菜单类、快捷键类话题。⇒ **CHM 解包里没有本域成员的参考页**，「说明与 See Also」在这条路上对本域**查不到** |

**每个成员的五项编号含义**：① 精确签名（含参数个数）· ② `## Remarks` 逐字摘录 · ③ 官方例子调用序（逐字 + 例文件名）· ④ 签名里出现的枚举（成员与数值）· ⑤ 废弃链（Obsolete 的后继；官方没写就写「查不到」）。
**每节末两行**：`前置一句话` = ② 里关于前置/选区/mark 的那一句；`配方一句话` = ③ 的调用序压缩。

---

## 1. 爆炸视图 Explode

### 1.1 `IAssemblyDoc` 侧

#### `IAssemblyDoc.CreateExplodedView`
1. **签名**（**0 参数**）：`System.bool CreateExplodedView()`
2. **Remarks 逐字**：「Call this method multiple times to add multiple explode views to the active assembly configuration.」「Perfect explode views often require user interaction. This method attempts to create a perfect explode view based on the current mate conditions.」
   〔`C:\swapi\types\IAssemblyDoc\CreateExplodedView.md`〕
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` 〔Source: `sldworksapi/Create_Exploded_Views_Example_VB.htm`〕
   > `' Create five exploded views` / `For i = 0 To 4` / `swAssembly.CreateExplodedView` / `Next i` / `vViewName = swAssembly.GetExplodedViewNames` / `Debug.Print "Number of exploded views created:  " & swAssembly.GetExplodedViewCount`
   > `Call swAssembly.ShowExploded2(True, sViewName)` → `Call swAssembly.ShowExploded2(False, sViewName)` → `swAssembly.ViewExplodeAssembly` → `swAssembly.ViewCollapseAssembly`
   例子前置注释原文：「' Preconditions: Open an assembly document.」
4. **枚举**：签名无枚举形参。**查不到**（例子里的 `GetExplodedViewCount` / `GetExplodedViewNames` 均已 Obsolete，官方例子本身用的是旧名）。
5. **废弃链**：本成员**无 Obsolete 标记**（逐字 grep `Obsolete` 无命中）。

**前置一句话**：零参数、无选区要求，但必须处在「活动的装配配置」上，且官方明说「perfect 爆炸视图常需用户交互」。
**配方一句话**：`For i=0 To 4 : swAssembly.CreateExplodedView : Next` → `GetExplodedViewNames` → `ShowExploded2(True,name)` → `ViewExplodeAssembly` / `ViewCollapseAssembly`。

#### `IAssemblyDoc.AutoExplode`
1. **签名**（**0 参数**）：`System.bool AutoExplode()`
2. **Remarks 逐字**：「This method creates only one exploded view per assembly configuration. To create multiple exploded views, use [[IAssemblyDoc::CreateExplodedView]].」「It is difficult to get the exploded view perfect without some user interaction. However, this method makes an attempt based on the current mate conditions.」
   〔`C:\swapi\types\IAssemblyDoc\AutoExplode.md`〕
3. **官方例子调用序**：**查不到** —— `Create_Exploded_Views_Example_VB.md` 全文只调 `CreateExplodedView`，未调 `AutoExplode`；本仓 `C:\swapi\examples\` 中按 `Explod|Mate|Interferen|Light` 过滤的文件名里也没有以 `AutoExplode` 为题的例子。
4. **枚举**：无。**查不到**（无枚举形参）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：无显式前置；官方只写「每个装配配置只能建一个爆炸视图，要多个请用 `CreateExplodedView`」。
**配方一句话**：查不到（无官方例子）。

#### `IAssemblyDoc.ShowExploded2`
1. **签名**（**2 参数**）：`System.bool ShowExploded2( System.bool ShowIt, System.string ExplodeViewName )`
2. **Remarks 逐字**：**该文件的 `## Remarks` 段为空** —— `C:\swapi\types\IAssemblyDoc\ShowExploded2.md` 摘录不到任何句子。**查不到**。
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md`
   > `For i = 0 To UBound(vViewName)` / `sViewName = vViewName(i)` / `Call swAssembly.ShowExploded2(True, sViewName)` / `Next i`（随后同一循环改为 `Call swAssembly.ShowExploded2(False, sViewName)`）
4. **枚举**：无枚举形参。`System.bool ShowIt` 逐字是布尔；`System.string ExplodeViewName` 取自 `GetExplodedViewNames` 返回的数组元素（例子逐字：`sViewName = vViewName(i)`）。
5. **废弃链**：**无 Obsolete 标记**；但它是 `IAssemblyDoc::ShowExploded` 的后继（见 §7）。

**前置一句话**：`ExplodeViewName` 必须先用 `GetExplodedViewNames`（旧名）/ `GetExplodedViewNames2` 取到；官方 `## Remarks` 本体**查不到**。
**配方一句话**：`Call swAssembly.ShowExploded2(True, sViewName)`（隐藏则把 `True` 换 `False`）。

#### `IAssemblyDoc.ShowExploded`
1. **签名**：见 §7 Obsolete 总表（本成员**已 Obsolete**，签名在 `C:\swapi\types\IAssemblyDoc\ShowExploded.md` 的 `**Signature**` 行，本节未逐字摘录）。
2. **Remarks 逐字**：**未读** —— 只在本轮做了 Obsolete 行扫描，未读其 `## Remarks`。**查不到（未抄）**。
3. **官方例子调用序**：**查不到** —— `Create_Exploded_Views_Example_VB.md` 只用 `ShowExploded2`。
4. **枚举**：**查不到（未抄）**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::ShowExploded2]].`

**前置一句话**：查不到（未抄）。
**配方一句话**：查不到（已被 `ShowExploded2` 取代，官方例子只用后者）。

#### `IAssemblyDoc.ViewExplodeAssembly`
1. **签名**（**0 参数**）：`void ViewExplodeAssembly()`
2. **Remarks 逐字**：「Use this method with [[IAssemblyDoc::ViewCollapseAssembly]] to toggle the display of the exploded assembly view.」
   〔`C:\swapi\types\IAssemblyDoc\ViewExplodeAssembly.md`〕
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` → 「`swAssembly.ViewExplodeAssembly`」（其后紧跟一行 `Stop`）。
4. **枚举**：无。**查不到**（无枚举形参）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；官方要求与 `ViewCollapseAssembly` 成对使用以「toggle 显示」。
**配方一句话**：`swAssembly.ViewExplodeAssembly` ⇄ `swAssembly.ViewCollapseAssembly`。

#### `IAssemblyDoc.ViewCollapseAssembly`
1. **签名**（**0 参数**）：`void ViewCollapseAssembly()`
2. **Remarks 逐字**：「Use this method with [[IAssemblyDoc::ViewExplodeAssembly]] to toggle the display of the exploded assembly view.」
   〔`C:\swapi\types\IAssemblyDoc\ViewCollapseAssembly.md`〕
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` → 「`swAssembly.ViewCollapseAssembly`」（例子的最后一行调用）。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；须与 `ViewExplodeAssembly` 配对。
**配方一句话**：`swAssembly.ViewCollapseAssembly`（例子中在 `ViewExplodeAssembly` 之后）。

#### `IAssemblyDoc.GetExplodedViewConfigurationName`
1. **签名**（**1 参数**）：`System.string GetExplodedViewConfigurationName( System.string ExplodedViewName )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空** —— `GetExplodedViewConfigurationName.md` 摘录不到句子。**查不到**。
3. **官方例子调用序**：**查不到** —— `Create_Exploded_Views_Example_VB.md` 未调本成员。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：形参名逐字是 `ExplodedViewName`（爆炸视图名，非配置名）；官方 `## Remarks` **查不到**。
**配方一句话**：查不到（无官方例子）。

#### `IAssemblyDoc.GetExplodedViewCount2`
1. **签名**（**1 参数**）：`System.int GetExplodedViewCount2( System.string ConfigurationName )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` 里用的是**旧名**「`Debug.Print "Number of exploded views created:  " & swAssembly.GetExplodedViewCount`」——**带 `2` 的版本在官方例子中查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**；是 `GetExplodedViewCount` 的后继（§7）。

**前置一句话**：形参是**配置名**（`ConfigurationName`），逐字与 `GetExplodedViewNames2` 一致。
**配方一句话**：`GetExplodedViewNames2(ConfigurationName)` → 长度；官方例子只示范旧名 `GetExplodedViewCount`。

#### `IAssemblyDoc.GetExplodedViewNames2`
1. **签名**（**1 参数**）：`System.object GetExplodedViewNames2( System.string ConfigurationName )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` 用旧名「`vViewName = swAssembly.GetExplodedViewNames`」，随后「`For i = 0 To UBound(vViewName)` / `sViewName = vViewName(i)`」—— 返回值是**数组**，用 `UBound` 取上界。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**；是 `GetExplodedViewNames` / `IGetExplodedViewNames` 的后继（§7）。

**前置一句话**：形参是**配置名**；返回数组，用 `UBound(vViewName)` 遍历（例子逐字）。
**配方一句话**：`vViewName = swAssembly.GetExplodedViewNames`(旧名) → `For i = 0 To UBound(vViewName) : sViewName = vViewName(i)`。

#### `IAssemblyDoc.GetExplodedViewCount` / `GetExplodedViewNames`
1. **签名**：见 §7（两者均已 Obsolete；签名逐字位于 `C:\swapi\types\IAssemblyDoc\GetExplodedViewCount.md` 与 `…\GetExplodedViewNames.md` 的 `**Signature**` 行，**本节未逐字摘录**）。
2. **Remarks 逐字**：**未读**。**查不到（未抄）**。
3. **官方例子调用序**：`Create_Exploded_Views_Example_VB.md` —— 「`swAssembly.GetExplodedViewCount`」与「`vViewName = swAssembly.GetExplodedViewNames`」（**两个旧名都在官方例子里出现**）。
4. **枚举**：**查不到（未抄）**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::GetExplodedViewCount2]].` / `Obsolete. Superseded by [[IAssemblyDoc::GetExplodedViewNames2]].`

**前置一句话**：查不到（未抄）。
**配方一句话**：官方例子示范的正是这两个**已废弃**名：`swAssembly.GetExplodedViewCount`、`swAssembly.GetExplodedViewNames`。

### 1.2 `IExplodeStep` 侧（25 个成员全部抄录）

> 取用入口（来自 `CreateExplodedView.md` 的 See Also，逐字）：`[[IConfiguration::AddExplodeStep2 Method ()]]`、`[[IConfiguration::AddRadialExplodeStep Method ()]]`。

#### `IExplodeStep.ExplodeDistance`
1. **签名**（属性，**0 参数**）：`System.double ExplodeDistance {get; set;}`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Get_Explode_Step_Example_VB.md` 只打印 `swExplodeStep.Name` / `GetNumOfComponents` / `IsSubAssemblyRigid`，**未读 `ExplodeDistance`** —— **查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：无显式前置（官方 `## Remarks` 为空）；爆炸步对象由 `swConfiguration.GetExplodeStep(0)` 取得（见下节配方）。
**配方一句话**：`Set swConfiguration = swConfigurationMgr.ActiveConfiguration` → `Set swExplodeStep = swConfiguration.GetExplodeStep(0)` → 读写 `.ExplodeDistance`。

#### `IExplodeStep.ExplodeStepType`
1. **签名**（属性，**0 参数**）：`System.int ExplodeStepType {get;}`（**只读**，无 `set`）
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到** —— `Get_Explode_Step_Example_VB.md` 未读本属性。
4. **枚举**：返回 `System.int`，但**本仓 `C:\swapi\enums\` 里没有 `swAssemblyExplodeStepType_e` 这个文件** —— 逐字 grep 全部 `*.md` 匹配 `swAssemblyExplodeStepType` **零命中** ⇒ **枚举数值查不到**。（该名字在 `DivergeDirection.md` / `DivergeFromAxis.md` / `ReverseRotationDirection.md` / `ReverseTranslationDirection.md` / `RotateAboutEachComponentOrigin.md` / `RotationAngle.md` / `GetSubAssemblyExplodeSteps.md` 的 Remarks 里被点名引用，但**枚举页查不到**。）
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：只读；它是 `DivergeDirection` / `DivergeFromAxis` / `ReverseRotationDirection` / `ReverseTranslationDirection` / `RotateAboutEachComponentOrigin` / `RotationAngle` / `GetSubAssemblyExplodeSteps` 七个成员的**有效性开关**（逐字：「This property is valid only if … ExplodeStepType is set to swAssemblyExplodeStepType_…」）。
**配方一句话**：先 `swConfiguration.GetExplodeStep(0)` 再读 `.ExplodeStepType`；枚举值查不到。

#### `IExplodeStep.GetComponent`
1. **签名**（**1 参数**）：`System.object GetComponent( System.int Index )`
2. **Remarks 逐字**：「Before calling this method, call [[IExplodeStep::GetNumOfComponents]] to get a valid value for Index.」
   〔`C:\swapi\types\IExplodeStep\GetComponent.md`〕
3. **官方例子调用序**：**查不到** —— `Get_Explode_Step_Example_VB.md` 只调 `GetNumOfComponents`，未调 `GetComponent`。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 官方逐字「Before calling this method, call GetNumOfComponents to get a valid value for Index」。
**配方一句话**：`.GetNumOfComponents` → 循环 `For i = 0 To (n-1)` → `.GetComponent(i)`。

#### `IExplodeStep.GetComponentName`
1. **签名**（**1 参数**）：`System.string GetComponentName( System.int Index )`
2. **Remarks 逐字**：「Before calling this method, call [[IExplodeStep::GetNumOfComponents]] to get a valid value for Index.」
   〔`C:\swapi\types\IExplodeStep\GetComponentName.md`〕
3. **官方例子调用序**：**查不到**（同上，例子未调本成员）。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 与 `GetComponent` 同一条逐字前置 —— 先 `GetNumOfComponents`。
**配方一句话**：`.GetNumOfComponents` → `.GetComponentName(i)`。

#### `IExplodeStep.IGetComponent`
1. **签名**（**1 参数**）：`Component IGetComponent( System.int Index )`
2. **Remarks 逐字**：「Before calling this method, call [[IExplodeStep::GetNumOfComponents]] to get a valid value for Index.」
   〔`C:\swapi\types\IExplodeStep\IGetComponent.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**（与 `GetComponent` 并存，官方未把它标 Obsolete）。

**前置一句话**：★ 逐字同句：先 `GetNumOfComponents` 取合法 `Index`。
**配方一句话**：查不到（官方例子只用 `GetComponent`/`GetNumOfComponents`）。

#### `IExplodeStep.GetComponents`
1. **签名**（**0 参数**）：`System.object GetComponents()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：无显式前置；官方 `## Remarks` 为空。`SetComponents` 的 Remarks 提示其对「选中列表最后一个组件」敏感（见 §1.2 SetComponents）。
**配方一句话**：查不到。

#### `IExplodeStep.SetComponents`
1. **签名**（**1 参数**）：`void SetComponents( System.object Components )`
2. **Remarks 逐字**：「Modifying components during editing of this regular explode step modifies the rotational axis if:」「- the rotational axis was not provided during creation,」「- and -」「- the component to which it referred (the last component in the selection list) was removed during editing.」「In that case, a rotational axis using the last selected component in the selection list is created.」
   〔`C:\swapi\types\IExplodeStep\SetComponents.md`〕
3. **官方例子调用序**：**查不到** —— 官方例子目录内没有设爆炸步组件的例子。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 官方唯一的前置是**条件式**：「during editing of this **regular** explode step」且「rotational axis was **not** provided during creation」——否则会改动旋转轴。
**配方一句话**：查不到（官方例子未示范）。

#### `IExplodeStep.GetComponentXform`
1. **签名**（**0 参数**）：`System.object GetComponentXform()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**（`Get_Explode_Step_Example_VB.md` 未调）。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：无显式前置；`GetSpecificComponentXForm` 的 Remarks 逐字说「For regular explode steps, this method works just like `GetComponentXform`」。
**配方一句话**：查不到。

#### `IExplodeStep.IGetComponentXform`
1. **签名**（**0 参数**）：`System.double IGetComponentXform()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：无显式前置；官方 `## Remarks` 为空 ⇒ **查不到**。
**配方一句话**：查不到。

#### `IExplodeStep.GetSpecificComponentXForm`
1. **签名**（**1 参数**）：`System.object GetSpecificComponentXForm( System.int Index )`
2. **Remarks 逐字**：「Before calling this method, call [[IExplodeStep::GetNumOfComponents]] to get a valid value for Index.」「For regular explode steps, this method works just like [[IExplodeStep::GetComponentXform]] to get the transformation of the entire explode step. This method also works for radial explode steps by getting the transformation of an individual radial explode component.」
   〔`C:\swapi\types\IExplodeStep\GetSpecificComponentXForm.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 逐字「Before calling this method, call GetNumOfComponents」；普通步取整步变换、径向步取单组件变换。
**配方一句话**：`.GetNumOfComponents` → `.GetSpecificComponentXForm(i)`。

#### `IExplodeStep.GetExplodeDirection`
1. **签名**（**1 参数**，带 **1 个 out**）：`System.object GetExplodeDirection( out System.int ExplDirIndex )`
2. **Remarks 逐字**：「This method is not valid for subassembly explode steps.」
   〔`C:\swapi\types\IExplodeStep\GetExplodeDirection.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：out 形参 `ExplDirIndex` 对应 `swExplodeDirectionIndex_e`（数值见 §8；该枚举页逐字把它写作「Explode direction manipulator options when creating or editing an explode step」，并注明 `-1` 用于 `[[IExplodeStep::SetExplodeDirection]]` 保持当前枚举值）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 有效性限定逐字：「**not valid for subassembly explode steps**」（子装配爆炸步不能用）。
**配方一句话**：查不到（官方例子未示范）。

#### `IExplodeStep.SetExplodeDirection`
1. **签名**（**2 参数**）：`void SetExplodeDirection( System.object ExplodeDirection, System.int ExplDirIndex )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：`System.int ExplDirIndex` → `swExplodeDirectionIndex_e`：`swExplodeDirectionIndex_Unknown = -1`（逐字注释「Use in [[IExplodeStep::SetExplodeDirection]] to continue using the current enumerator value」）、`swExplodeDirectionIndex_XAxis = 0`、`swExplodeDirectionIndex_YAxis = 1`、`swExplodeDirectionIndex_ZAxis = 2`。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：官方 `## Remarks` 为空 ⇒ **查不到**；但 `swExplodeDirectionIndex_e` 页逐字把 `-1` 定义成本方法的「沿用当前枚举值」。
**配方一句话**：查不到。

#### `IExplodeStep.GetRotationAxis`
1. **签名**（**1 参数**，带 **1 个 out**）：`System.object GetRotationAxis( out System.int RotAxisIndex )`
2. **Remarks 逐字**：「This method is not valid for subassembly explode steps.」
   〔`C:\swapi\types\IExplodeStep\GetRotationAxis.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：out 形参 `RotAxisIndex` 对应的枚举名**查不到** —— `RotAxisIndex` 与 `swExplodeDirectionIndex_e` 不同名，本仓 `C:\swapi\enums\` 无对应文件，**数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 与 `GetExplodeDirection` 同一条逐字前置：「not valid for subassembly explode steps」。
**配方一句话**：查不到。

#### `IExplodeStep.SetRotationAxis`
1. **签名**（**2 参数**）：`void SetRotationAxis( System.object RotationAxis, System.int RotAxisIndex )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：`RotAxisIndex` 的枚举名**查不到**（无对应 enum 文件）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：官方 `## Remarks` 为空 ⇒ **查不到**。
**配方一句话**：查不到。

#### `IExplodeStep.GetNumOfComponents`
1. **签名**（**0 参数**）：`System.int GetNumOfComponents()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Get_Explode_Step_Example_VB.md` 逐字：
   > `Debug.Print "Number of components that move in this explode step: " & swExplodeStep.GetNumOfComponents`
   例子前置逐字：「' 1. Open an assembly document with an explode view.」
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 它本身就是 `GetComponent` / `GetComponentName` / `IGetComponent` / `GetSpecificComponentXForm` 四个成员被逐字点名的**前置**。
**配方一句话**：`Set swExplodeStep = swConfiguration.GetExplodeStep(0)` → `swExplodeStep.GetNumOfComponents`。

#### `IExplodeStep.Name`
1. **签名**（属性，**0 参数**）：`System.string Name {get; set;}`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Get_Explode_Step_Example_VB.md` → 「`Debug.Print "Name of explode step: " & swExplodeStep.Name`」
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；例子是在取得 `swExplodeStep` 之后读的。
**配方一句话**：`swConfiguration.GetExplodeStep(0)` → `swExplodeStep.Name`。

#### `IExplodeStep.DivergeDirection`
1. **签名**（属性，**0 参数**）：`System.object DivergeDirection {get; set;}`
2. **Remarks 逐字**：「This property is valid only if:」「- [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_Radial,」「- and -」「- the selected entity creates an angle with the explode direction.」「If you set this property to a valid diverge direction entity, then [[IExplodeStep::DivergeFromAxis]] is automatically set to true.」「If you set this property to Nothing or null, then IExplodeStep::DivergeFromAxis is automatically set to false.」
   〔`C:\swapi\types\IExplodeStep\DivergeDirection.md`〕
3. **官方例子调用序**：**查不到** —— 例子里没有出现 `Diverge` 字样。
4. **枚举**：引用的 `swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Radial` —— ★ **枚举数值查不到**（`C:\swapi\enums\` 无该枚举文件）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 三个条件同时成立才有效：① `ExplodeStepType == swAssemblyExplodeStepType_Radial`；② 「the selected entity creates an angle with the explode direction」（**需要先有被选实体**）；③ 设成有效值会自动把 `DivergeFromAxis` 置 `true`，设成 Nothing/null 会置 `false`。
**配方一句话**：查不到（无官方例子）。

#### `IExplodeStep.DivergeFromAxis`
1. **签名**（属性，**0 参数**）：`System.bool DivergeFromAxis {get; set;}`
2. **Remarks 逐字**：「This property is valid only if [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_Radial.」「If you set this property to false, then [[IExplodeStep::DivergeDirection]] is automatically set to nothing or null.」「If you want to set this property to true, then you must first set IExplodeStep::DivergeDirection to a valid diverge direction entity.」
   〔`C:\swapi\types\IExplodeStep\DivergeFromAxis.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Radial` —— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 官方逐字给出**双向依赖**：「想置 `true` 必须先给 `DivergeDirection` 一个有效实体」；置 `false` 会把 `DivergeDirection` 清空。
**配方一句话**：查不到（顺序约束已知，官方例子没有）。

#### `IExplodeStep.RotationAngle`
1. **签名**（属性，**0 参数**）：`System.double RotationAngle {get; set;}`
2. **Remarks 逐字**：「If [[IExplodeStep::AutoSpaceComponentsOnDrag]] is set to true, then this property is automatically 0.0.」「If [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]]:」「- swAssemblyExplodeStepType_Radial, then this property sets the degree of rotation of components about their origins.」「- swAssemblyExplodeStepType_Translate, then this property sets the degree of rotation of components about the rotation axis.」
   〔`C:\swapi\types\IExplodeStep\RotationAngle.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e`（`swAssemblyExplodeStepType_Radial` / `swAssemblyExplodeStepType_Translate`）—— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 若 `AutoSpaceComponentsOnDrag == true` 则本属性被**自动置 0.0**；含义随 `ExplodeStepType` 在「绕各自原点」与「绕旋转轴」之间切换。
**配方一句话**：查不到。

#### `IExplodeStep.AutoSpaceComponentsOnDrag`
1. **签名**（属性，**0 参数**）：`System.bool AutoSpaceComponentsOnDrag {get; set;}`
2. **Remarks 逐字**：「If this property is set to true, then, by default, [[IExplodeStep::RotateAboutEachComponentOrigin]] is false and [[IExplodeStep::RotationAngle]] is 0.0.」「If you set this property to false during editing of this step, then you must re-set the values for IExplodeStep::RotateAboutEachComponentOrigin and IExplodeStep::RotationAngle.」
   〔`C:\swapi\types\IExplodeStep\AutoSpaceComponentsOnDrag.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 编辑已有爆炸步时若把它从 `true` 改成 `false`，官方要求**必须重设** `RotateAboutEachComponentOrigin` 与 `RotationAngle`。
**配方一句话**：查不到。

#### `IExplodeStep.ReverseRotationDirection`
1. **签名**（属性，**0 参数**）：`System.bool ReverseRotationDirection {get; set;}`
2. **Remarks 逐字**：「This property is valid only if [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_Translate.」
   〔`C:\swapi\types\IExplodeStep\ReverseRotationDirection.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Translate` —— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 单一有效性条件：`ExplodeStepType == swAssemblyExplodeStepType_Translate`。
**配方一句话**：查不到。

#### `IExplodeStep.ReverseTranslationDirection`
1. **签名**（属性，**0 参数**）：`System.bool ReverseTranslationDirection {get; set;}`
2. **Remarks 逐字**：「This property is valid only if [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_Translate.」
   〔`C:\swapi\types\IExplodeStep\ReverseTranslationDirection.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Translate` —— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 同上：`ExplodeStepType == swAssemblyExplodeStepType_Translate`。
**配方一句话**：查不到。

#### `IExplodeStep.RotateAboutEachComponentOrigin`
1. **签名**（属性，**0 参数**）：`System.bool RotateAboutEachComponentOrigin {get; set;}`
2. **Remarks 逐字**：「If [[IExplodeStep::AutoSpaceComponentsOnDrag]] is set to true, then this property is automatically false.」「This property is valid only if [[IExplodeStep::ExplodeStepType]] is set to [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_Translate.」「If this property is set to true, then the rotation axis is automatically populated.」
   〔`C:\swapi\types\IExplodeStep\RotateAboutEachComponentOrigin.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_Translate` —— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 置 `true` 会**自动填入旋转轴**；`AutoSpaceComponentsOnDrag == true` 时被自动置 `false`。
**配方一句话**：查不到。

#### `IExplodeStep.IsSubAssemblyRigid`
1. **签名**（**0 参数**）：`System.bool IsSubAssemblyRigid()`
2. **Remarks 逐字**：「See the SOLIDWORKS Help for more information about flexible and rigid subassemblies.」
   〔`C:\swapi\types\IExplodeStep\IsSubAssemblyRigid.md`〕
3. **官方例子调用序**：`Get_Explode_Step_Example_VB.md` → 「`Debug.Print "Is the sub-assembly rigid? " & swExplodeStep.IsSubAssemblyRigid`」
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：官方把语义细节外链给 SOLIDWORKS Help（**本机该 Help 的对应页本轮未查 ⇒ 查不到**）。
**配方一句话**：`swConfiguration.GetExplodeStep(0)` → `swExplodeStep.IsSubAssemblyRigid`。

#### `IExplodeStep.GetSubAssemblyExplodeSteps`
1. **签名**（**0 参数**）：`System.object GetSubAssemblyExplodeSteps()`
2. **Remarks 逐字**：「A subassembly explode step is created when you click **Reuse Subassembly Explode** on the Explode PropertyManager. This method retrieves the nested explode steps of the subassembly.」「This method is valid only if [[IExplodeStep::ExplodeStepType]] returns [[swAssemblyExplodeStepType_e]].swAssemblyExplodeStepType_SubAssembly.」
   〔`C:\swapi\types\IExplodeStep\GetSubAssemblyExplodeSteps.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swAssemblyExplodeStepType_e.swAssemblyExplodeStepType_SubAssembly` —— **数值查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 步的来源逐字是 PropertyManager 上点「**Reuse Subassembly Explode**」；有效性由 `ExplodeStepType == swAssemblyExplodeStepType_SubAssembly` 决定。
**配方一句话**：查不到。

---

## 2. 组件阵列 Pattern

#### `IAssemblyDoc.DissolveComponentPattern`
1. **签名**（**0 参数**）：`System.bool DissolveComponentPattern()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空** —— `DissolveComponentPattern.md` 摘录不到句子。**查不到**。
3. **官方例子调用序**：**查不到** —— 本仓 `C:\swapi\examples\` 里按 `Pattern` 过滤无阵列相关例子（目录过滤 `Explod|Interferen|Mate|Light|Component` 的结果中没有 pattern 例子）。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**（逐字 grep `Obsolete` 在该文件零命中）。

**前置一句话**：零参数；官方 `## Remarks` 为空 ⇒ 选什么、mark 多少**查不到**。
**配方一句话**：查不到（无官方例子）。

#### `IAssemblyDoc.InsertDerivedPattern`
1. **签名**（**0 参数**）：`System.bool InsertDerivedPattern()`
2. **Remarks 逐字**：「Use [[IModelDocExtension::SelectByID2]] to select the components, which must be ordered:」「- seed component = 1」「- pattern feature = 6」
   〔`C:\swapi\types\IAssemblyDoc\InsertDerivedPattern.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：逐字 `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[IDerivedPatternFeatureData]].` —— ★ 官方**没有点名单个后继成员**，只指向 `IFeatureManager::CreateFeature` + `IDerivedPatternFeatureData`；按本文件纪律记为「**后继 = 该两处（官方原文如此，非单一成员）**」。

**前置一句话**：★★ 逐字顺序 + mark：`SelectByID2` 先选**种子组件 mark=1**，再选**阵列特征 mark=6**。
**配方一句话**：查不到（官方例子无）；官方自己已把这条路标 Obsolete。

---

## 3. 轻化 Lightweight

### 3.1 `IAssemblyDoc` 侧

#### `IAssemblyDoc.MakeLightWeight`
1. **签名**（**0 参数**）：`void MakeLightWeight()`
2. **Remarks 逐字**：「The purpose of this method is to support recording macros. You should use [[IComponent2::GetSuppression]] or [[IComponent2::SetSuppression2]] to get or set a component to lightweight.」「This method sets the current selected components to lightweight, which is suitable for recording and running macros. IComponent2::GetSuppression and IComponent2::SetSuppression2 operate on the component itself.」
   〔`C:\swapi\types\IAssemblyDoc\MakeLightWeight.md`〕
3. **官方例子调用序**：**查不到** —— 官方轻化例子 `Set_All_Assembly_Components_Lightweight_or_Resolved_Example_VB.md` 走的是 `swChildComp.SetSuppression2(...)`，**未调 `MakeLightWeight`**。
4. **枚举**：无枚举形参；作用范围由**当前选区**决定。**查不到**。
5. **废弃链**：**无 Obsolete 标记**（但官方逐字说它「purpose is to support recording macros」，并把推荐路径指向 `IComponent2::GetSuppression` / `SetSuppression2`）。

**前置一句话**：★ 零参数、**作用于当前选中的组件**；官方逐字声明它的目的是「support recording macros」。
**配方一句话**：官方轻化配方走的是 `SetSuppression2`（见 §3.2 与下方 `Set_All_Assembly_Components_Lightweight_or_Resolved_Example_VB.md` 逐字行）。

#### `IAssemblyDoc.LightweightAllResolved`
1. **签名**（**0 参数**）：`System.bool LightweightAllResolved()`
2. **Remarks 逐字**：「If no components are selected, then this method is applied to this assembly document.」「Suppressed components are ignored.」
   〔`C:\swapi\types\IAssemblyDoc\LightweightAllResolved.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 无选区时作用于**整份装配文档**；**被抑制的组件被忽略**。
**配方一句话**：查不到。

#### `IAssemblyDoc.ResolveAllLightweight`
1. **签名**（**0 参数**）：`System.bool ResolveAllLightweight()`
2. **Remarks 逐字**：「If no components are selected, then this method is applied to this assembly document.」「Suppressed components are ignored.」
   〔`C:\swapi\types\IAssemblyDoc\ResolveAllLightweight.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 与 `LightweightAllResolved` 同：未选则全装配生效，抑制件忽略。
**配方一句话**：查不到。

#### `IAssemblyDoc.ResolveAllLightWeightComponents`
1. **签名**（**1 参数**）：`System.int ResolveAllLightWeightComponents( System.bool WarnUser )`
2. **Remarks 逐字**：「The assembly must be open in its own window. Call [[ISldWorks::ActivateDoc2]] or [[IModelDoc2::Visible]] to ensure that it is. If the assembly is only open as a reference in another document, then this method returns swComponentResolveStatus_e.swResolveNotPerformed.」
   〔`C:\swapi\types\IAssemblyDoc\ResolveAllLightWeightComponents.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：返回 `System.int`，由 `swComponentResolveStatus_e` 逐字点名：`swResolveOk = 0`、`swResolveAbortedByUser = 1`、`swResolveNotPerformed = 2`、`swResolveError = 3`（逐字描述「3 = Not used」）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 装配必须**在自己的窗口里打开**（`ISldWorks::ActivateDoc2` 或 `IModelDoc2::Visible`）；仅作为参考打开时返回 `swResolveNotPerformed`。
**配方一句话**：查不到（返回码口径已知，调用序无例子）。

#### `IAssemblyDoc.ResolveOutOfDateLightWeightComponents`
1. **签名**（**0 参数**）：`System.bool ResolveOutOfDateLightWeightComponents()`
2. **Remarks 逐字**：「You must select a lightweight component before using this method. If the lightweight component and any of its lightweight subcomponents are out-of-date, then this method resolves them. If your selection is invalid, then this method returns false.」
   〔`C:\swapi\types\IAssemblyDoc\ResolveOutOfDateLightWeightComponents.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 逐字「You must **select a lightweight component** before using this method」；选区无效即返回 `false`。
**配方一句话**：查不到。

#### `IAssemblyDoc.GetLightWeightComponentCount`
1. **签名**（**0 参数**）：`System.int GetLightWeightComponentCount()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；官方 `## Remarks` 为空 ⇒ **查不到**。
**配方一句话**：查不到。

#### `IAssemblyDoc.HasUnloadedComponents`
1. **签名**（**0 参数**）：`System.bool HasUnloadedComponents()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**（但 `GetUnloadedComponentNames.md` 的 Remarks 反向点名它：「To get whether an assembly has hidden or suppressed unloaded components, call [[IAssemblyDoc::HasUnloadedComponents]]」）。
3. **官方例子调用序**：`Get_Visibility_of_and_Resolve_Lightweight_Components_Example_VB.md` 与 `Get_Whether_Components_Are_Loaded_Example_VB.md` 的文件名指向本主题，**本轮未逐字读其代码 ⇒ 查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；它是 `GetUnloadedComponentNames` 逐字指定的「有无隐藏/抑制未加载组件」判据。
**配方一句话**：查不到（未逐字读该例代码）。

#### `IAssemblyDoc.GetUnloadedComponentNames`
1. **签名**（**4 个 out 参数**，0 个入参）：`System.object GetUnloadedComponentNames( out System.object UnloadedComponentPathNames, out System.object UnloadedComponentReferencedConfigurationNames, out System.object ReasonForUnloadingComponents, out System.object DocTypes )`
2. **Remarks 逐字**：「This method is useful when the assembly document was opened with **[[Quick View/Selective open]]** or **Do not load hidden components**.」「To get whether an assembly has hidden or suppressed unloaded components, call [[IAssemblyDoc::HasUnloadedComponents]].」
   〔`C:\swapi\types\IAssemblyDoc\GetUnloadedComponentNames.md`〕
3. **官方例子调用序**：**查不到**（本轮未逐字读该例代码）。
4. **枚举**：无枚举形参；4 个 out 数组分别是路径名 / 引用配置名 / 卸载原因 / 文档类型。**查不到**（官方未给这些数组的枚举口径）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 典型场景是装配以「Quick View/Selective open」或「Do not load hidden components」方式打开。
**配方一句话**：查不到。

#### `IAssemblyDoc.OpenCompFile`
1. **签名**（**0 参数**）：`void OpenCompFile()`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[ISldWorks::ActivateDoc2]] and [[ISldWorks::OpenDoc6]].`

**前置一句话**：查不到（已废弃，官方把它让给 `ISldWorks::ActivateDoc2` + `ISldWorks::OpenDoc6`）。
**配方一句话**：查不到。

### 3.2 `IComponent2` 侧

#### `IComponent2.GetSuppression2`
1. **签名**（**0 参数**）：`System.int GetSuppression2()`
2. **Remarks 逐字**：「The difference between this method and the now obsolete IComponent2::GetSuppression is that this method returns an error code (5 = swComponentSuppressionState_e.swComponentInternalIdMismatch) if there is an internal ID mismatch.」「Use this method to determine if the component is suppressed, lightweight, or fully resolved. It is critical to know the component's suppression state because lightweight and suppressed components contain only a small subset of data compared to a fully resolved component. For more information, see [Work With Lightweight Components](<../../docs/Programming with the SOLIDWORKS API/Lightweight Components.md>).」
   〔`C:\swapi\types\IComponent2\GetSuppression2.md`〕
3. **官方例子调用序**：`Set_All_Assembly_Components_Lightweight_or_Resolved_Example_VB.md` 逐字：
   > `nRetVal = swChildComp.SetSuppression2(swComponentSuppressionState)` / `Debug.Print sPadStr & swChildComp.Name2 & " <" & swChildComp.ReferencedConfiguration & "> --> " & swChildComp.GetPathName`
   （例子里**没有**读 `GetSuppression2` 的行 ⇒ 只读方向的例子**查不到**。）
4. **枚举**：返回 `System.int`，由 `swComponentSuppressionState_e` 逐字点名：`swComponentSuppressed = 0`、`swComponentLightweight = 1`、`swComponentFullyResolved = 2`、`swComponentResolved = 3`、`swComponentFullyLightweight = 4`、`swComponentInternalIdMismatch = 5`。
5. **废弃链**：**无 Obsolete 标记**；是 `GetSuppression` 的后继（§7）。

**前置一句话**：零参数；官方用它区分 suppressed / lightweight / fully resolved，并强调轻化件与抑制件**只含一小部分数据**。
**配方一句话**：`Set swRootComp = swConfig.GetRootComponent3(True)` → 递归 `ProcessComponent`：`vChildCompArr = swComp.GetChildren` → `swChildComp.SetSuppression2(state)` → 递归自身。

#### `IComponent2.SetSuppression2`
1. **签名**（**1 参数**）：`System.int SetSuppression2( System.int State )`
2. **Remarks 逐字**：「SOLIDWORKS does not allow suppressing components while a PropertyManager page is open.」
   〔`C:\swapi\types\IComponent2\SetSuppression2.md`〕
3. **官方例子调用序**：`Set_All_Assembly_Components_Lightweight_or_Resolved_Example_VB.md` 逐字（**完整调用序**）：
   > `If nResponse = vbYes Then` / `nSuppressState = swComponentLightweight` / `Else` / `nSuppressState = swComponentFullyResolved` / `End If`
   > `Set swConfig = swConfigMgr.ActiveConfiguration` / `Set swRootComp = swConfig.GetRootComponent3(True)` / `swFeatMgr.EnableFeatureTree = False`
   > `ProcessComponent swApp, swModel, swRootComp, nSuppressState, " "` / `swFeatMgr.EnableFeatureTree = True`
   > 递归体内：`vChildCompArr = swComp.GetChildren` / `For Each vChildComp In vChildCompArr` / `Set swChildComp = vChildComp` / `nRetVal = swChildComp.SetSuppression2(swComponentSuppressionState)` / `ProcessComponent swApp, swModel, swChildComp, swComponentSuppressionState, sPadStr + " "` / `Next vChildComp`
4. **枚举**：形参 `State` → `swComponentSuppressionState_e`（值见上）。例子逐字用了 `swComponentLightweight`（1）与 `swComponentFullyResolved`（2）。
5. **废弃链**：**无 Obsolete 标记**；是 `SetSuppression` 的后继（§7）。

**前置一句话**：★★ 逐字「SOLIDWORKS does not allow suppressing components **while a PropertyManager page is open**」。
**配方一句话**：`ActiveConfiguration` → `GetRootComponent3(True)` → 关 `FeatureTree.EnableFeatureTree` → 递归 `GetChildren` + `SetSuppression2(state)` → 复原。

#### `IComponent2.GetSuppression` / `SetSuppression`
1. **签名**：逐字分别为 `System.int GetSuppression()` 与 `System.int SetSuppression( System.int State )` 〔`C:\swapi\types\IComponent2\GetSuppression.md` / `…\SetSuppression.md`〕
2. **Remarks 逐字**：`GetSuppression.md`：「Use this method to determine if the component is suppressed, lightweight, or fully resolved. It is critical to know the component's suppression state because lightweight and suppressed components contain only a small subset of data compared to a fully resolved component. For more information, see [Work With Lightweight Components](<../../docs/Programming with the SOLIDWORKS API/Lightweight Components.md>).」；`SetSuppression.md` 的 `## Remarks` **为空**。
3. **官方例子调用序**：**查不到**（例子只调 `SetSuppression2`）。
4. **枚举**：`swComponentSuppressionState_e`（同上）。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IComponent2::GetSuppression2]].` / `Obsolete. Superseded by [[IComponent2::SetSuppression2]].`

**前置一句话**：查不到（已 Obsolete；`SetSuppression` 的 `## Remarks` 为空）。
**配方一句话**：查不到（官方轻化例子已改用 `SetSuppression2`）。

#### `IComponent2.IsLoaded` / `IComponent2.IsGraphicsOnly`
1. **签名**：逐字 `System.bool IsLoaded()` / `System.bool IsGraphicsOnly {get;}` 〔`C:\swapi\types\IComponent2\IsLoaded.md` / `…\IsGraphicsOnly.md`〕
2. **Remarks 逐字**：两文件 `## Remarks` **均为空**。**查不到**。
3. **官方例子调用序**：**查不到**（本轮未逐字读 `Get_Whether_Components_Are_Loaded_Example_VB.md`）。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**（两者都不在 §7 清单里）。

**前置一句话**：查不到（官方 `## Remarks` 为空）。
**配方一句话**：查不到。

#### `IComponent2.IsSuppressed`
1. **签名**（**0 参数**）：`System.bool IsSuppressed()`
2. **Remarks 逐字**：「The suppression state of a component can vary based on the active configuration. You might want to use [[IComponent2::GetSuppression]], which returns the specific suppression state of the component.」
   〔`C:\swapi\types\IComponent2\IsSuppressed.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：官方提示它**随活动配置变化**，推荐改用 `GetSuppression` 取具体状态值。
**配方一句话**：查不到。

#### `IComponent2.IsHidden`
1. **签名**（**1 参数**）：`System.bool IsHidden( System.bool ConsiderSuppressed )`
2. **Remarks 逐字**：「The state of this component can vary based on the active configuration.」＋ 一张真值表（逐字列名 `ConsiderSuppressed` / `Component`，行如「True / Hidden / Unsuppressed / True / True」），以及「**NOTE:** For [lightweight](<../../docs/Programming with the SOLIDWORKS API/Lightweight Components.md>) components, IsHidden returns True if ConsiderSuppressed is True.」
   〔`C:\swapi\types\IComponent2\IsHidden.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无枚举形参；返回值含义由官方真值表逐字给出。**查不到**（无枚举）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 对**轻化件**逐字注明：「IsHidden returns True if `ConsiderSuppressed` is True」；另附「Shown / Suppressed ⇒ `IsHidden=True` 而 `ConsiderSuppressed=False`」等真值表。
**配方一句话**：查不到。

#### `IComponent2.GetHiddenUnloadedChildrenCount`
1. **签名**（**0 参数**）：`System.int GetHiddenUnloadedChildrenCount()`
2. **Remarks 逐字**：「You can open an assembly with all components hidden except those that you select. The selected components are loaded lightweight. All other components become hidden and are not loaded into memory. This method returns the number of unloaded hidden children of this component. This method does not return the number of suppressed unloaded children components. Call [[IComponent2::GetUnloadedComponentNames]] for that type of related information.」
   〔`C:\swapi\types\IComponent2\GetHiddenUnloadedChildrenCount.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ 它**只数隐藏未加载子件**，**不含抑制未加载子件**（后者走 `GetUnloadedComponentNames`）。
**配方一句话**：查不到。

#### `IComponent2.HasUnloadedComponents` / `IComponent2.GetUnloadedComponentNames`
1. **签名**：逐字 `System.bool HasUnloadedComponents()` / `System.object GetUnloadedComponentNames( out System.object UnloadedComponentPathNames, out System.object UnloadedComponentReferencedConfigurationNames, out System.object ReasonForUnloadingComponents, out System.object DocTypes )` 〔`C:\swapi\types\IComponent2\HasUnloadedComponents.md` / `…\GetUnloadedComponentNames.md`〕
2. **Remarks 逐字**：`GetUnloadedComponentNames.md`：「This method is useful when the assembly document was opened with **[[Quick View/Selective open]]**.」「To get whether a component has hidden or suppressed children components, call [[IComponent2::HasUnloadedComponents]].」；`HasUnloadedComponents.md` 的 `## Remarks` **为空**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：装配以「Quick View/Selective open」打开时有用；两者签名与 `IAssemblyDoc` 同名成员**逐字一致**。
**配方一句话**：查不到。

---

## 4. 干涉检查 Interference

### 4.1 `IAssemblyDoc` 侧入口

#### `IAssemblyDoc.InterferenceDetectionManager`
1. **签名**（属性，**0 参数**）：`InterferenceDetectionMgr InterferenceDetectionManager {get;}`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：`Run_Interference_Detection_Example_VB.md` 是对应例子，**本轮未逐字读其代码 ⇒ 查不到**。
4. **枚举**：返回 `InterferenceDetectionMgr`（接口，详见 §4.2）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数、只读属性；官方 `## Remarks` 为空 ⇒ 取该对象前需要什么**查不到**。
**配方一句话**：查不到（未逐字读 `Run_Interference_Detection_Example_VB.md`）。

#### `IAssemblyDoc.ClearanceVerificationManager`
1. **签名**（属性，**0 参数**）：`System.object ClearanceVerificationManager {get;}`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：返回类型是 `System.object`（**不是**命名接口）⇒ 实际类型**查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：零参数；返回类型只写作 `System.object`，**未给接口名** ⇒ 查不到。
**配方一句话**：查不到。

#### `IAssemblyDoc.ToolsCheckInterference`
1. **签名**（**0 参数**）：`void ToolsCheckInterference()`
2. **Remarks 逐字**：「Opens the Interference Detection PropertyManager.」
   〔`C:\swapi\types\IAssemblyDoc\ToolsCheckInterference.md`〕
3. **官方例子调用序**：**查不到**（官方例子 `Check_Interference_using_AssemblyDoc_ToolsCheckInterference2_Example_VB.md` 用的是 `ToolsCheckInterference2`）。
4. **枚举**：无。**查不到**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::ToolsCheckInterference2]].`

**前置一句话**：零参数；唯一作用是**打开 PropertyManager 对话框**。
**配方一句话**：查不到（官方例子改用了 `ToolsCheckInterference2`）。

#### `IAssemblyDoc.ToolsCheckInterference2`
1. **签名**（**3 入参 + 2 out**，共 **5 个形参**）：`void ToolsCheckInterference2( System.int NumComponents, System.object LpComponents, System.bool CoincidentInterference, out System.object PComp, out System.object PFace )`
2. **Remarks 逐字**：「This method returns:」「- an empty array of faces for components that have coincident faces that touch.」「- an array of components for components that touch.」「For each face that intersects, there is a corresponding component.」「**NOTE:** The obsolete method, IAssemblyDoc::ToolsCheckInterference, displays the Interference Detection PropertyManager, but this method does not.」
   〔`C:\swapi\types\IAssemblyDoc\ToolsCheckInterference2.md`〕
3. **官方例子调用序**：`Check_Interference_using_AssemblyDoc_ToolsCheckInterference2_Example_VB.md` 逐字：
   > 例子前置注释：「' 2. Select at least two interfering components.」
   > `nSelCount = swSelMgr.GetSelectedObjectCount` / `ReDim CompArray(nSelCount - 1)` / `For i = 0 To (nSelCount - 1)` / `Set CompArray(i) = swSelMgr.GetSelectedObjectsComponent2(i + 1)` / `Next i`
   > `vCompArray = CompArray` / `swAssy.ToolsCheckInterference2 nSelCount, (vCompArray), bCoincidentInterference, vIntCompArray, vIntFaceArray`
   > `If (IsEmpty(vIntCompArray) = True) And (IsEmpty(vIntFaceArray) = True) Then` / `Debug.Print " No contact"` / `Exit Sub`
   > 面分支：`swModel.ClearSelection2 True` / `Set swFace = vIntFaceArray(i)` / `Set swEnt = swFace` / `Set swComp = swEnt.GetComponent` / `bRet = swEnt.Select4(True, swSelData)` / `Debug.Assert bRet`
   > 组件分支：`Set swComp = vIntCompArray(i)` / `bRet = swComp.Select2(True, 0)` / `Debug.Assert bRet`
4. **枚举**：形参 `CoincidentInterference` 是 `System.bool`（例子逐字 `Const bCoincidentInterference As Boolean = False`）；**没有枚举形参**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 例子前置逐字「Select at least two interfering components」；组件数组由 `ISelectionMgr::GetSelectedObjectCount` + `GetSelectedObjectsComponent2(i+1)` 组装（★ 注意例子的索引是 **`i + 1`**）。
**配方一句话**：`GetSelectedObjectCount` → `ReDim CompArray(n-1)` → `GetSelectedObjectsComponent2(i+1)` → `vCompArray = CompArray` → `swAssy.ToolsCheckInterference2 nSelCount, vCompArray, bCoincident, vIntCompArray, vIntFaceArray` → `IsEmpty(...)` 判空 → 分别 `swEnt.Select4(True, swSelData)` / `swComp.Select2(True, 0)`。

#### `IAssemblyDoc.IToolsCheckInterference2`
1. **签名**（**5 个形参**）：`void IToolsCheckInterference2( System.int NumComponents, ref Component LpComponents, System.bool CoincidentInterference, out System.object PComp, out System.object PFace )` ★ 注意形参类型是 **`ref Component`**，比 `ToolsCheckInterference2` 的 `System.object` 更窄。
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**（例子只调 `ToolsCheckInterference2`）。
4. **枚举**：无。**查不到**。
5. **废弃链**：逐字 `Obsolete. See [[IAssemblyDoc::IToolsCheckInterference3]].`

**前置一句话**：查不到（已 Obsolete，`## Remarks` 为空）。
**配方一句话**：查不到。

#### `IAssemblyDoc.IToolsCheckInterference3`
1. **签名**（**5 个形参**）：`void IToolsCheckInterference3( System.int NumComponents, ref Component2 LpComponents, System.bool CoincidentInterference, out System.object PComp, out System.object PFace )` ★ `ref Component2`（`IToolsCheckInterference2` 是 `ref Component`）。
2. **Remarks 逐字**：「This method returns:」「- an empty array of faces for components that have coincident faces that touch.」「- an array of components for components that touch.」「For each face that intersects, there is a corresponding component.」
   〔`C:\swapi\types\IAssemblyDoc\IToolsCheckInterference3.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：无。**查不到**。
5. **废弃链**：★★ 逐字只有 `Obsolete.` —— **官方没有点名后继** ⇒ 按纪律记为「**查不到（官方未写后继）**」。（★ 注意它自己被 `IToolsCheckInterference2.md` 逐字指向为「See [[IAssemblyDoc::IToolsCheckInterference3]]」，但那是**反向**指针，不构成 `3` 的后继。）

**前置一句话**：与 `ToolsCheckInterference2` 同口径（空面数组 / 组件数组）；但 `ref` 形参类型是 `Component2`。
**配方一句话**：查不到（官方例子只调 `ToolsCheckInterference2`）。

### 4.2 `IInterferenceDetectionMgr`（22 个成员全部抄录）

> ★ 共性前置（逐字，逐字出现在 `CreateFastenersFolder` / `IgnoreHiddenBodies` / `IncludeMultibodyPartInterferences` / `MakeInterferingPartsTransparent` / `ShowIgnoredInterferences` / `TreatCoincidenceAsInterference` / `TreatSubAssembliesAsComponents` 七个成员的 `## Remarks` 里，文字完全一致）：
> 「Currently, the value set for this property:」「- exists only while the InterferenceDetectionMgr object is in scope; i.e., setting this property is temporary.」「- does not persist across SOLIDWORKS Design sessions.」「- does not persist into the next invocation of interference detection in the user interface.」

| # | 成员 | ① 精确签名（参数个数） | ② `## Remarks` 逐字（该成员独有部分） | ③ 官方例子调用序 | ④ 枚举 | ⑤ 废弃链 | 前置一句话 | 配方一句话 |
|---|---|---|---|---|---|---|---|---|
| 1 | `CreateFastenersFolder` | `System.bool CreateFastenersFolder {get; set;}`（属性，0） | 只有上面那段**共性**七行 | `CreateFastenersFolder_Example_VB.md` **不存在** ⇒ **查不到** | 无枚举形参 | 无 Obsolete | ★ 共性：**只在 `InterferenceDetectionMgr` 对象在作用域内存在**，不跨会话、不跨下次 UI 调用 | 查不到 |
| 2 | `Done` | `void Done()`（0） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 3 | `ExportResults` | `System.bool ExportResults( System.string FileName, System.bool IncludeThumbnail )`（2） | 「This method corresponds to the **Save Results** button in the Interference Detection PropertyManager.」「Filename is a Microsoft Excel file or a ***.csv** file that contains the information presented in the Results list box …」＋列定义 `A Interference ID` / `B Interference Preview` / `C Interference volume (mm^3)` / `D Component 1 name` / `E Component 2 name` / `F Component 1 full reference` / `G Component 2 full reference`；「IncludeThumbnail is only valid if Filename is a Microsoft Excel file.」「A thumbnail is created in each row of Column B … 128X128 pixel resolution / White background / Isometric orientation」 | **查不到** | 无枚举形参 | 无 Obsolete | ★ `Filename` 必须是 Excel 或 **.csv**；`IncludeThumbnail` **仅对 Excel 有效** | 查不到 |
| 4 | `GetComponentsAndTransforms` | `System.bool GetComponentsAndTransforms( out System.object ComponentList, out System.object TransformList )`（0 入 + 2 out） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 5 | `SetComponentsAndTransforms` | `System.int SetComponentsAndTransforms( System.object ComponentList, System.object TransformList )`（2） | 「You must pass in **absolute transforms** to this method.」「If you want to transform a component incrementally before interference detection, then you must multiply that incremental transform by the component's existing transform before passing in the resultant transform.」「To produce the effect of identity transforms on components (i.e., the components do not move while participating in interference detection), the transforms for those components passed in can be null or Nothing. However, passing in null or Nothing for **all** of the transforms is interpreted as invalid input.」「**NOTE:** A null or Nothing is interpreted as the component's existing transform (i.e., an identity incremental transform).」 | `Set_Components_and_Transforms_for_Interference_Detection_Example_VB.md` 存在，**本轮未逐字读其代码 ⇒ 查不到** | 无枚举形参 | 无 Obsolete | ★ 必须传**绝对变换**；全传 null/Nothing 判为**非法输入**（部分 null 才是恒等） | 查不到 |
| 6 | `GetComponentsTransformInterference` | `System.bool GetComponentsTransformInterference( System.object Component, System.object Transform, out System.object InterferingComponent )`（2 入 + 1 out） | **`## Remarks` 为空** ⇒ **查不到** | `Detect_Interferences_Using_a_Transform_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 7 | `GetComponentsTransformInterferenceCount` | `System.int GetComponentsTransformInterferenceCount( System.int NumOfComponent, ref Component2 Component, ref MathTransform Transform )`（3） | 「Call this method **before** calling [[IInterferenceDetectionMgr::IGetComponentsTransformInterference]] to get the size of the array returned by that method.」 | **查不到** | 无 | 无 Obsolete | ★ 逐字「**Call this method before** calling `IGetComponentsTransformInterference`」以取数组长度 | 查不到 |
| 8 | `GetInterferenceCount` | `System.int GetInterferenceCount()`（0） | 「Call this method before calling [[IInterferenceDetectionMgr::IGetInterferences]] to determine the size of the array for the interferences.」 | **查不到** | 无 | 无 Obsolete | ★ 逐字「**Call this method before** calling `IGetInterferences`」以定数组大小 | 查不到 |
| 9 | `GetInterferences` | `System.object GetInterferences()`（0） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 10 | `GetInterferenceComponentCount` | `System.int GetInterferenceComponentCount()`（0） | 「Call this method before calling [[IInterferenceDectectionMgr::IGetInterferenceComponents]].」 ★★ 官方原文此处把接口名**拼错**成 `IInterferenceDectectionMgr`（少一个 `e`，逐字照抄） | **查不到** | 无 | 无 Obsolete | ★ 逐字「before calling `IGetInterferenceComponents`」 | 查不到 |
| 11 | `GetInterferenceComponents` | `System.object GetInterferenceComponents()`（0） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 12 | `IgnoreHiddenBodies` | `System.bool IgnoreHiddenBodies {get; set;}`（属性，0） | 只有**共性**七行 | **查不到** | 无 | 无 Obsolete | ★ 共性七行（临时、不持久） | 查不到 |
| 13 | `IncludeMultibodyPartInterferences` | `System.bool IncludeMultibodyPartInterferences {get; set;}`（属性，0） | 只有**共性**七行 | **查不到** | 无 | 无 Obsolete | ★ 共性七行 | 查不到 |
| 14 | `MakeInterferingPartsTransparent` | `System.bool MakeInterferingPartsTransparent {get; set;}`（属性，0） | 只有**共性**七行 | `Set_Components_Transparent_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | 无 Obsolete | ★ 共性七行 | 查不到 |
| 15 | `NonInterferingComponentDisplay` | `System.int NonInterferingComponentDisplay {get; set;}`（属性，0） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无枚举形参，**取值口径查不到**（`swInterferenceComponentDisplay_e` 一类枚举在 `C:\swapi\enums\` 无对应文件） | 无 Obsolete | 查不到 | 查不到 |
| 16 | `ShowIgnoredInterferences` | `System.bool ShowIgnoredInterferences {get; set;}`（属性，0） | 只有**共性**七行 | **查不到** | 无 | 无 Obsolete | ★ 共性七行 | 查不到 |
| 17 | `TreatCoincidenceAsInterference` | `System.bool TreatCoincidenceAsInterference {get; set;}`（属性，0） | 只有**共性**七行 | **查不到** | 无 | 无 Obsolete | ★ 共性七行 | 查不到 |
| 18 | `TreatSubAssembliesAsComponents` | `System.bool TreatSubAssembliesAsComponents {get; set;}`（属性，0） | 只有**共性**七行 | **查不到** | 无 | 无 Obsolete | ★ 共性七行 | 查不到 |
| 19 | `UseTransform` | `System.bool UseTransform {get; set;}`（属性，0） | **`## Remarks` 为空** ⇒ **查不到** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 20 | `IGetInterferences` | 见 §6 表（本轮未逐字读其签名行） | **未读** | **查不到** | **查不到（未抄）** | **无 Obsolete 标记**（不在 §7 清单里） | 查不到 | 查不到 |
| 21 | `IGetInterferenceComponents` | 见 §6 表（未逐字读） | **未读** | **查不到** | **查不到（未抄）** | **无 Obsolete 标记** | 查不到 | 查不到 |
| 22 | `IGetComponentsTransformInterference` | 见 §6 表（未逐字读） | **未读**；但被 `GetComponentsTransformInterferenceCount.md` 逐字引用为「Call this method before … to get the size of the array returned by that method」 | **查不到** | **查不到（未抄）** | **无 Obsolete 标记** | ★ 被 `GetComponentsTransformInterferenceCount` 点名为「先取长度」的那一个 | 查不到 |

> ★ 逐字文件来源：`C:\swapi\types\IInterferenceDetectionMgr\<成员>.md`（每格的 ①②④⑤ 都出自对应文件的 `**Signature**` 行 / `## Remarks` 段 / `Obsolete.` 行）。

---

## 5. 配合 Mate

### 5.1 `IAssemblyDoc` 侧

#### `IAssemblyDoc.AddMate5`（官方现行推荐路径）
1. **签名**（**15 个形参**，含 1 个 out）：`Mate2 AddMate5( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, System.bool ForPositioningOnly, System.bool LockRotation, System.int WidthMateOption, out System.int ErrorStatus )`
2. **Remarks 逐字**：「To create:」「- Standard, advanced, and mechanical mates, use [[IAssemblyDoc::CreateMate]].」「- Misaligned concentric mates, use [[IAssemblyDoc::AddConcentricMateWithTolerance]].」「- Cylindrical distance mates, use [[IAssemblyDoc::AddDistanceMate]].」「The difference between this method and the now obsolete IAssemblyDoc::AddMate4 is the WidthMateOption parameter.」「To specify a distance mate without limits, set the DistanceAbsUpperLimit and DistanceAbsLowerLimit parameters equal to the Distance parameter.」「If MateTypeFromEnum is swMateType_e.swMateDISTANCE or swMateType_e.swMateANGLE, and the mate is applied to the closest position that meets the mate condition specified by Distance or Angle, then setting Flip to true moves the components to the other possible mate position.」「To add a standard or mechanical mate:」「1. Call [[IModelDoc2::ClearSelection2]] before selecting entities to mate.」「2. Call [[IModelDocExtension::SelectByID2]] to select each entity to mate.」「If MateTypeFromEnum is… / Use selection mark… / swMateType_e.swMateCAMFOLLOWER → 8 / swMateType_e.swMateWIDTH → 16 / Other swMateType_e option → 1」「3. Call this method.」「4. Call IModelDoc2::ClearSelection2 after the mate is created.」「If entities are not preselected, then ErrorStatus is swAddMateError_e.swAddMateError_IncorrectSelections, and nothing is returned.」
   〔`C:\swapi\types\IAssemblyDoc\AddMate5.md`〕
3. **官方例子调用序**：**查不到** —— 官方例子目录里有 `Create_Standard_Mates_Example_VB.md` / `Create_Symmetric_Mate_Example_VB.md` / `Create_Width_Mate_Example_VB.md` / `Create_Limit_Angle_Mate_Example_VB.md` / `Rack_and_Pinion_Mate_Example_CSharp.md` 等，**本轮未逐字读其代码** ⇒ 逐字调用序**查不到**。
4. **枚举**：`MateTypeFromEnum` → `swMateType_e`（§8）；`AlignFromEnum` → `swMateAlign_e`（§8）；`WidthMateOption` → `swMateWidthOptions_e`（§8）；`ErrorStatus` → `swAddMateError_e`（§8）。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]` ★ 注意原文 `CreateMate.` **带一个多余的句点**（逐字照抄）。

**前置一句话**：★★ ① 先 `IModelDoc2::ClearSelection2`；② 用 `SelectByID2` 选实体，mark 逐字为 **`swMateCAMFOLLOWER`→8 / `swMateWIDTH`→16 / 其他→1**；③ 调本方法；④ 之后 `ClearSelection2`。无预选时 `ErrorStatus = swAddMateError_IncorrectSelections` 且**什么都不返回**。
**配方一句话**：查不到（未逐字读官方例子）；但官方把「标准/高级/机械配合」逐字指向 `CreateMate`，非此路径。

#### `IAssemblyDoc.AddMate3`（`AddMate5` 的 mark 表同源）
1. **签名**（**13 个形参**）：`Mate2 AddMate3( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, System.bool ForPositioningOnly, out System.int ErrorStatus )`
2. **Remarks 逐字**：「To specify a distance mate without limits, set the DistanceAbsUpperLimit and DistanceAbsLowerLimit arguments equal to the distance argument's value.」「If MateTypeFromEnum is swMateDISTANCE or swMateANGLE when the mate is applied to the closest position that meets the mate condition specified by distance or angle, then setting Flip to true moves the assembly to the other possible mate position.」「To add a mate:」「1. Call [[IModelDoc2::ClearSelection2]] before selecting entities to mate.」「2. Call [[IModelDocExtension::SelectByID2]] to select entities to mate.」「If MateTypeFromEnum is swMateCAMFOLLOWER, then use a selection mark of 8 for the cam-follower face.」「If MateTypeFromEnum is swMateWIDTH and uses tab selections, then use a selection mark of 16. If MateTypeFromEnum is anything else, then use a selection mark of 1.」「3. Call this method.」「4. Call IModelDoc2::ClearSelection2 after the mate is created.」「If nothing is preselected, then ErrorStatus is swAddMateError_IncorrectSelections, and nothing is returned.」
   〔`C:\swapi\types\IAssemblyDoc\AddMate3.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateType_e` / `swMateAlign_e` / `swAddMateError_e`（§8）。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::AddMate4]].`

**前置一句话**：★★ 与 `AddMate5` 同一条 mark 表（8 / 16 / 1），逐字原文在此处是句子形式。
**配方一句话**：查不到。

#### `IAssemblyDoc.AddMate4`
1. **签名**（**14 个形参**）：`Mate2 AddMate4( …同 AddMate3 前 12 项…, System.bool LockRotation, out System.int ErrorStatus )` ★ 逐字全文见 §8.5 引用：`Mate2 AddMate4( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, System.bool ForPositioningOnly, System.bool LockRotation, out System.int ErrorStatus )`
2. **Remarks 逐字**：「The difference between this method and the now obsolete IAssemblyDoc::AddMate3 is that this method's LockRotation parameter provides the option to lock the rotation of components in the mate.」「To specify a distance mate without limits, set the DistanceAbsUpperLimit and DistanceAbsLowerLimit parameters equal to the Distance parameter.」「To add a mate:」「1. Call [[IModelDoc2::ClearSelection2]] before selecting entities to mate.」「2. Call [[IModelDocExtension::SelectByID2]] to select each entity to mate.」「If MateTypeFromEnum is… / Use selection mark… / swMateType_e.swMateCAMFOLLOWER → 8 / swMateType_e.swMateWIDTH → 16 / Other swMateType_e option → 1」「3. Call this method.」「4. Call IModelDoc2::ClearSelection2 after the mate is created.」「If nothing is preselected, then ErrorStatus is swAddMateError_IncorrectSelections, and nothing is returned.」
   〔`C:\swapi\types\IAssemblyDoc\AddMate4.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateType_e` / `swMateAlign_e` / `swAddMateError_e`。
5. **废弃链**：逐字 `Obsolete. Superseded by IAssemblyDoc::AddMate5.`（★ 此处原文**无 `[[ ]]` 链接括号**，逐字照抄）。

**前置一句话**：★★ mark 表 8 / 16 / 1；前后各一次 `ClearSelection2`。
**配方一句话**：查不到。

#### `IAssemblyDoc.AddMate2`
1. **签名**（**12 个形参**）：`Mate2 AddMate2( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, out System.int ErrorStatus )`
   〔`C:\swapi\types\IAssemblyDoc\AddMate2.md`〕
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateType_e` / `swMateAlign_e` / `swAddMateError_e`（依形参名；**此成员自身未在 Remarks 里点名枚举 ⇒ 关联属形参名推断**）。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::AddMate3]].`

**前置一句话**：查不到（`## Remarks` 为空）。
**配方一句话**：查不到。

#### `IAssemblyDoc.AddMate`
1. **签名**（**5 个形参**）：`void AddMate( System.int MateType, System.int Align, System.bool Flip, System.double Dist, System.double Angle )` ★ 注意形参名是 `MateType` / `Align` / `Dist`（**无 `FromEnum`、无 `Abs…Limit`**）。
   〔`C:\swapi\types\IAssemblyDoc\AddMate.md`〕
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：`System.int MateType` / `System.int Align` —— 枚举**数值**见 §8（`swMateType_e` / `swMateAlign_e`），但**本成员页面本身未点名枚举 ⇒ 查不到（本成员层面）**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::AddMate3]].`

**前置一句话**：查不到（已 Obsolete，`## Remarks` 为空）。
**配方一句话**：查不到。

#### `IAssemblyDoc.CreateMate`（官方现行推荐路径）
1. **签名**（**1 个形参**）：`System.object CreateMate( System.object MateData )`
2. **Remarks 逐字**（含**★ 完整的 19 个 mate-specific 接口表**，带 `*` 号的 13 个支持「预选配合实体」）：
   「[[IMateFeatureData]] is the base interface for the following mate-specific interfaces (an asterisk indicates that pre-selection of mate entities during mate creation is supported):」
   `IAngleMateFeatureData` / `ICamFollowerMateFeatureData *` / `ICoincidentMateFeatureData *` / `IConcentricMateFeatureData *` / `IDistanceMateFeatureData` / `IGearMateFeatureData *` / `IHingeMateFeatureData *` / `ILinearCouplerMateFeatureData` / `ILockMateFeatureData *` / `IParallelMateFeatureData *` / `IPerpendicularMateFeatureData *` / `IProfileCenterMateFeatureData` / `IRackPinionMateFeatureData *` / `IScrewMateFeatureData *` / `ISlotMateFeatureData *` / `ISymmetricMateFeatureData` / `ITangentMateFeatureData *` / `IUniversalJointMateFeatureData *` / `IWidthMateFeatureData`
   「To create a standard, advanced, or mechanical mate:」「1. Use [[IAssemblyDoc::CreateMateData]] to access a MateFeatureData object.」「2. Set the general properties of the MateFeatureData object.」「3. Cast the MateFeatureData object to one of the mate-specific objects.」「4. Follow specific instructions in the Remarks of the mate-specific interface, set specific properties of the mate-specific object, and/or pre-select entities to mate for asterisked interfaces above.」「5. Call this method, passing in the mate-specific object.」「To create:」「- Misaligned concentric mates, use [[IAssemblyDoc::AddConcentricMateWithTolerance]].」「- Cylindrical distance mates, use [[IAssemblyDoc::AddDistanceMate]].」
   〔`C:\swapi\types\IAssemblyDoc\CreateMate.md`〕
3. **官方例子调用序**：**查不到**（未逐字读 `Create_Standard_Mates_Example_VB.md` 等）。
4. **枚举**：形参 `MateData` 是 `System.object`；选型靠 `swMateType_e`（传给 `CreateMateData`）⇒ 数值见 §8。
5. **废弃链**：**无 Obsolete 标记**；它是 `AddMate5` 逐字点名的后继。

**前置一句话**：★ 五步序：① `CreateMateData` 取 MateFeatureData → ② 设通用属性 → ③ 转型为 mate-specific 对象 → ④ 按该接口 Remarks 设属性并/或**预选实体（只对带 `*` 的 13 个）** → ⑤ 调本方法。
**配方一句话**：查不到（未逐字读官方例子）。

#### `IAssemblyDoc.CreateMateData`
1. **签名**（**1 个形参**）：`System.object CreateMateData( System.int Type )`
2. **Remarks 逐字**：「Type must be one of the following mate types as defined in swMateType_e:」＋逐字列出 **18 个**：`swMateANGLE` / `swMateCAMFOLLOWER` / `swMateCOINCIDENT` / `swMateCONCENTRIC` / `swMateDISTANCE` / `swMateGEAR` / `swMateHINGE` / `swMateLINEARCOUPLER` / `swMateLOCK` / `swMatePARALLEL` / `swMatePERPENDICULAR` / `swMatePROFILECENTER` / `swMateRACKPINION` / `swMateSCREW` / `swMateSLOT` / `swMateSYMMETRIC` / `swMateTANGENT` / `swMateUNIVERSALJOINT` / `swMateWIDTH`；末句「To create a mate, see the [[IAssemblydoc::CreateMate]] Remarks section.」★ 注意此处原文把接口名写成 `IAssemblydoc`（**小写 d**），逐字照抄。
   〔`C:\swapi\types\IAssemblyDoc\CreateMateData.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateType_e` —— ★ **本成员只接受 18 个子集**（缺 `swMateCOORDINATE(20)` / `swMateLOCKTOSKETCH(12)` / `swMateMAGNETIC(25)` / `swMateMAXMATES(14)` / `swMatePATH(15)` / `swMateSLIDER(23)` / `swMateUNKNOWN(7)`）⇒ **这 7 个在 `CreateMateData` 里查不到**。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★ `Type` **必须**是上列 18 个之一（逐字「must be one of the following」）；其余 7 个 `swMateType_e` 成员被本方法排除。
**配方一句话**：查不到。

#### `IAssemblyDoc.AddConcentricMateWithTolerance`
1. **签名**（**4 入参 + 1 out**，共 5）：`Mate2 AddConcentricMateWithTolerance( System.int AlignFromEnum, System.int ConcentricPositionType, System.bool ConcentricToleranceCheck, System.double ConcentricToleranceValue, out System.int ErrorStatus )`
2. **Remarks 逐字**：「Select the two entities to mate **before calling this method**. A parent non-misaligned (i.e., standard) concentric mate must already exist between the selected entities. If a suitable parent concentric mate does not exist between the selected entities, then a standard concentric mate is created.」「**NOTE:** The typical way to add a standard concentric mate is to use [[IAssemblyDoc::AddMate5]].」
   〔`C:\swapi\types\IAssemblyDoc\AddConcentricMateWithTolerance.md`〕
3. **官方例子调用序**：`Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md` 存在，**本轮未逐字读 ⇒ 查不到**。
4. **枚举**：`AlignFromEnum` → `swMateAlign_e`；`ConcentricPositionType` → `swConcentricAlignmentType_e`（★ 该枚举**在 `C:\swapi\enums\` 无对应文件 ⇒ 数值查不到**；名字是从 `IMate2/SetMaximumMisalignedDeviation.md` 等的 Remarks 里读到的：「if [[IMate2::GetConcentricAlignmentType]] is set to [[swConcentricAlignmentType_e]].swConcentricAlignSymmetric」）；`ErrorStatus` → `swAddMateError_e`。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 逐字「**Select the two entities to mate before calling this method**」，且**父级标准同心配合必须已存在**（否则会自动先建一个标准同心配合）。
**配方一句话**：查不到。

#### `IAssemblyDoc.AddDistanceMate`
1. **签名**（**7 入参 + 1 out**，共 8）：`Mate2 AddDistanceMate( System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.int FirstArcCondition, System.int SecondArcCondition, out System.int ErrorStatus )`
2. **Remarks 逐字**：「To specify a distance mate without limits, set the DistanceAbsUpperLimit and DistanceAbsLowerLimit parameters equal to the Distance parameter.」「If the mate is applied to the closest position that meets the mate condition specified by Distance, then setting Flip to true moves the components to the other possible mate position.」「For cylindrical distance mates only, the following FirstArcCondition-to-SecondArcCondition distance combinations are possible:」＋ 8 行 `swArcCondition_*` 配对表（`Center→Center` / `Center→Minimum` / `Center→Maximum` / `Minimum→Center` / `Minimum→Minimum` / `Maximum→Center` / `Maximum→Minimum` / `Maximum→Maximum`）；「To add a distance mate:」「1. Call [[IModelDocExtension::SelectByRay]] and [[ISelectionMgr::GetSelectedObject6]] to get each mate entity. (For cylindrical distance mates, the selections must be **two cylindrical faces or one cylindrical face and one axis**.)」「2. Call [[IModelDoc2::ClearSelection2]].」「3. Call [[IEntity::Select4]] to select each entity.」「4. Call this method.」「5. Call [[IModelDoc2::EditRebuild3]] after the mate is created.」「If entities are not preselected, then ErrorStatus is swAddMateError_e.swAddMateError_IncorrectSelections, and nothing is returned.」
   〔`C:\swapi\types\IAssemblyDoc\AddDistanceMate.md`〕
3. **官方例子调用序**：`Add_Distance_Mates_Example_VB.md` / `Create_Limit_Distance_Mate_Example_VB.md` / `Add_and_Edit_Distance_Mate_Example_VB.md` 存在，**未逐字读 ⇒ 查不到**。
4. **枚举**：`AlignFromEnum` → `swMateAlign_e`；`FirstArcCondition` / `SecondArcCondition` → `swDistanceMateArcConditions_e`（§8）；`ErrorStatus` → `swAddMateError_e`。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★★ 五步序逐字：① `SelectByRay` + `GetSelectedObject6` 取每个配合实体（圆柱距离配合必须是**两个圆柱面，或一个圆柱面 + 一条轴**）→ ② `ClearSelection2` → ③ `IEntity::Select4` → ④ 调本方法 → ⑤ **`EditRebuild3`**。
**配方一句话**：查不到。

#### `IAssemblyDoc.EditMate4`
1. **签名**（**16 个形参**）：`void EditMate4( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, System.bool ForPositioningOnly, System.bool LockRotation, System.int WidthMateOption, System.bool RepairMatesWithSameMissingEntity, out System.int ErrorStatus )`
2. **Remarks 逐字**：「To edit:」「- Standard, advanced, and mechanical mates created using [[IAssemblyDoc::CreateMate]], follow the steps to edit the mate in the Remarks of the mate's feature data interface.」「- Misaligned concentric mates, use [[IAssemblyDoc::EditConcentricMate]].」「- Distance mates, use [[IAssemblyDoc::EditDistanceMate]].」「If repairing all mates missing the same mate entity, then select the following items in the following order before calling this method:」「1. Mate feature to repair.」「2. Two model items to mate (that is, two faces, edge and face, and so on). The two model items must be selected with a selection mark of **1**. See [[ISelectData]] or [[IModelDocExtension::SelectByID2]] for details on using selection marks.」「This method does not support editing **Inplace** mates.」
   〔`C:\swapi\types\IAssemblyDoc\EditMate4.md`〕
3. **官方例子调用序**：`Edit_Mate_Example_VB.md` / `Edit_Mate_Reference_Example_VB.md` / `Repair_Mates_Missing_Same_Mate_Entity_Example_VB.md` 存在，**未逐字读 ⇒ 查不到**。
4. **枚举**：`swMateType_e` / `swMateAlign_e` / `swMateWidthOptions_e` / `swAddMateError_e`。
5. **废弃链**：逐字 `Obsolete. See the Remarks in each standard, advanced, and mechanical mate's feature data interface.` —— ★ 官方**未点名单一后继成员** ⇒ 记为「后继 = 各 mate 的 feature data 接口的 Remarks（官方原文如此，非单一成员）」。

**前置一句话**：★★ 修「缺同一配合实体的所有配合」时，**选区顺序**逐字为：① 要修的**配合特征**；② 两个待配合模型项，**mark = 1**。官方另注本方法**不支持改 Inplace 配合**。
**配方一句话**：查不到。

#### `IAssemblyDoc.EditMate3` / `EditMate2`
1. **签名**（各 **14 / 13 个形参**，逐字）：
   - `void EditMate3( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, System.bool ForPositioningOnly, System.bool LockRotation, System.int WidthMateOption, out System.int ErrorStatus )`
   - `void EditMate2( System.int MateTypeFromEnum, System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.double GearRatioNumerator, System.double GearRatioDenominator, System.double Angle, System.double AngleAbsUpperLimit, System.double AngleAbsLowerLimit, out System.int ErrorStatus )`
2. **Remarks 逐字**（两者同源）：「The first selections should be the **two items that are mated** (that is, two faces, edge and face, and so on), and the third selection should be the **mate feature to be edited**. The mate feature must be selected **last**. The two mated items must be selected with a selection mark of **1**.」「…setting Flip to true moves the assembly to the other possible mate position.」「This method does not support editing **Inplace** mates.」
   〔`C:\swapi\types\IAssemblyDoc\EditMate3.md` / `…\EditMate2.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateType_e` / `swMateAlign_e` / `swAddMateError_e`。
5. **废弃链**：逐字 `Obsolete. Superseded by IAssemblyDoc::EditMate3.` / `Obsolete. Superseded by IAssemblyDoc::EditMate4.`（★ 两处原文均**无 `[[ ]]`**，逐字照抄）。

**前置一句话**：★★ 选区**顺序**逐字：先两个待配合项（**mark = 1**），**配合特征必须最后选**。
**配方一句话**：查不到。

#### `IAssemblyDoc.EditMate`
1. **签名**（**5 个形参**）：`void EditMate( System.int MateType, System.int Align, System.bool Flip, System.double Dist, System.double Angle )`
2. **Remarks 逐字**：**该文件 `## Remarks` 段为空**。**查不到**。
3. **官方例子调用序**：**查不到**。
4. **枚举**：本页未点名 ⇒ **查不到（本成员层面）**。
5. **废弃链**：逐字 `Obsolete. Superseded by [[IAssemblyDoc::EditMate2]].`

**前置一句话**：查不到（已 Obsolete，`## Remarks` 为空）。
**配方一句话**：查不到。

#### `IAssemblyDoc.EditConcentricMate`
1. **签名**（**4 入参 + 1 out**）：`void EditConcentricMate( System.int AlignFromEnum, System.int ConcentricPositionType, System.bool ConcentricToleranceCheck, System.double ConcentricToleranceValue, out System.int ErrorStatus )`
2. **Remarks 逐字**：「Select these entities before calling this method:」「- Two entities that define the misaligned concentric mate」「- Misaligned concentric mate」「A parent non-misaligned (i.e., standard) concentric mate must already exist for the selected misaligned concentric mate. If a suitable parent concentric mate does not exist, then the selected misaligned concentric mate changes to a standard concentric mate. You can also change a misaligned concentric mate to a standard concentric mate using [[IAssemblyDoc::EditMate4]].」「After calling IAssemblyDoc::EditConcentricMate, call [[IModelDoc2::EditRebuild3]].」
   〔`C:\swapi\types\IAssemblyDoc\EditConcentricMate.md`〕
3. **官方例子调用序**：`Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md` 存在，**未逐字读 ⇒ 查不到**。
4. **枚举**：`swMateAlign_e`；`ConcentricPositionType` → `swConcentricAlignmentType_e`（★ **数值查不到**，枚举文件不存在）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 选区逐字两项：**① 定义偏心同心配合的两个实体；② 偏心同心配合本身**；调完后必须 `EditRebuild3`。
**配方一句话**：查不到。

#### `IAssemblyDoc.EditDistanceMate`
1. **签名**（**7 入参 + 1 out**）：`void EditDistanceMate( System.int AlignFromEnum, System.bool Flip, System.double Distance, System.double DistanceAbsUpperLimit, System.double DistanceAbsLowerLimit, System.int FirstArcCondition, System.int SecondArcCondition, out System.int ErrorStatus )`
2. **Remarks 逐字**：「Select these entities before calling this method:」「- Two entities that define the distance mate (use [[IEntity::Select4]] with **Data = Nothing**)」「- Distance mate feature (use [[IFeature::Select2]] with **Mark = 0**)」「If the mate is applied to the closest position … setting Flip to true moves the components to the other possible mate position.」「Call [[IModelDoc2::EditRebuild3]] after calling this method.」「See [[IAssemblyDoc::AddDistanceMate]] Remarks.」
   〔`C:\swapi\types\IAssemblyDoc\EditDistanceMate.md`〕
3. **官方例子调用序**：**查不到**。
4. **枚举**：`swMateAlign_e` / `swDistanceMateArcConditions_e` / `swAddMateError_e`。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★★ 两个 mark 逐字给定：**距离配合实体用 `IEntity::Select4` 且 `Data = Nothing`；配合特征用 `IFeature::Select2` 且 `Mark = 0`**；调完 `EditRebuild3`。
**配方一句话**：查不到。

#### `IAssemblyDoc.AutoMateRepair`
1. **签名**（**0 入参 + 2 out**）：`System.int AutoMateRepair( out System.object ProcessedMates, out System.object FailedMates )`
2. **Remarks 逐字**：「Before calling this method you must:」「- ensure that the entities needed to repair the broken mates are present in the assembly」「- and -」「- **select the Mates folder in the FeatureManager design tree**.」
   〔`C:\swapi\types\IAssemblyDoc\AutoMateRepair.md`〕
3. **官方例子调用序**：`Repair_Mates_Missing_Same_Mate_Entity_Example_VB.md` 存在，**未逐字读 ⇒ 查不到**。
4. **枚举**：返回 `System.int`；`swAutoMateRepairErrors_e` **在 `C:\swapi\enums\` 存在**（本轮未逐字读其数值 ⇒ **数值查不到**）。
5. **废弃链**：**无 Obsolete 标记**。

**前置一句话**：★★ 逐字两条硬前置：① **修复所需实体必须在装配中**；② **必须选中 FeatureManager 设计树的「Mates」文件夹**。
**配方一句话**：查不到（未逐字读 `Repair_Mates_Missing_Same_Mate_Entity_Example_VB.md`）。

#### `IAssemblyDoc.IsSupportedMatesAvailable` / `IAssemblyDoc.CollectAllSupportiveMates`
1. **签名**：逐字 `System.bool IsSupportedMatesAvailable {get;}`（属性，0）与 `System.object CollectAllSupportiveMates()`（0） 〔`C:\swapi\types\IAssemblyDoc\IsSupportedMatesAvailable.md` / `…\CollectAllSupportiveMates.md`〕
2. **Remarks 逐字**：`IsSupportedMatesAvailable.md`：「Supportive mate types are as defined by [[swMateType_e]].: swMateANGLE / swMateDISTANCE / swMatePATH / swMateSLOT / swMateWIDTH」「The Mate Controller feature does not support path, width, or slot mates created with either a free or a center in slot constraint.」「If this property is true, then use [[IAssemblyDoc::CollectAllSupportiveMates]] to collect the supportive mates in this assembly.」；`CollectAllSupportiveMates.md`：「This method is valid only if [[IAssemblyDoc::IsSupportedMatesAvailable]] is true.」
3. **官方例子调用序**：`Create_Mate_Controller_Example_VB.md` / `Create_Mate_Controller_Example_CSharp.md` 存在，**未逐字读 ⇒ 查不到**。
4. **枚举**：`swMateType_e` —— 逐字只支持 **5 个**：`swMateANGLE(6)` / `swMateDISTANCE(5)` / `swMatePATH(15)` / `swMateSLOT(21)` / `swMateWIDTH(11)`（§8）。
5. **废弃链**：**无 Obsolete 标记**（两者都不在 §7 清单里）。

**前置一句话**：★ `CollectAllSupportiveMates` 逐字「**valid only if** `IsSupportedMatesAvailable` is **true**」；且 Mate Controller **不支持**带 free 或 center-in-slot 约束的 path / width / slot 配合。
**配方一句话**：查不到。

### 5.2 `IMate2` 侧（32 个成员全部抄录）

| # | 成员 | ① 精确签名（参数个数） | ② `## Remarks` 逐字 | ③ 官方例子调用序 | ④ 枚举 | ⑤ 废弃链 | 前置一句话 | 配方一句话 |
|---|---|---|---|---|---|---|---|---|
| 1 | `Type` | `System.int Type {get;}`（属性，0，只读） | `## Remarks` **为空** | **查不到** | 取值为 `swMateType_e`；`CanBeFlipped.md` 逐字「Use [[IMate2::Type]] to determine the type of mate.」 | 无 Obsolete | 查不到 | 查不到 |
| 2 | `Alignment` | `System.int Alignment {get;}`（属性，0，只读） | `## Remarks` **为空** | **查不到** | `swMateAlign_e`（本页未点名 ⇒ **查不到**） | 无 Obsolete | 查不到 | 查不到 |
| 3 | `Flipped` | `System.bool Flipped {get; set;}`（属性，0） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 4 | `CanBeFlipped` | `System.bool CanBeFlipped {get;}`（属性，0，只读） | 「Use [[IMate2::Type]] to determine the type of mate.」 | **查不到** | 无 | 无 Obsolete | ★ 逐字要先看 `Type` | 查不到 |
| 5 | `GetMateEntityCount` | `System.int GetMateEntityCount()`（0） | 「Call this method before calling [[IMate2::MateEntity]] to get the number of entities in the mate.」 | **查不到**（`Get_Mates_and_Mate_Entities_Example_VB.md` 存在，未逐字读） | 无 | 无 Obsolete | ★ 逐字「**before** calling `MateEntity`」 | 查不到 |
| 6 | `MateEntity` | `MateEntity2 MateEntity( System.int Index )`（1） | 「To get the number of entities for this mate, call [[IMate2::GetMateEntityCount]].」 | **查不到** | 无 | 无 Obsolete | ★ 先 `GetMateEntityCount` | 查不到 |
| 7 | `MaximumVariation` | `System.double MaximumVariation {get;}`（属性，0，只读） | 「This property is valid only for [[IMate2::Type]]: swMateType_e.swMateANGLE - or - swMateType_e.swMateDISTANCE」「For distance and angle mates: *Maximum_variation* = *maximum_value* - *dimension_value*」 | **查不到** | `swMateType_e` | 无 Obsolete | ★ 仅 ANGLE / DISTANCE 有效 | 查不到 |
| 8 | `MinimumVariation` | `System.double MinimumVariation {get;}`（属性，0，只读） | 「This property is valid only for [[IMate2::Type]]: swMateType_e.swMateANGLE - or - swMateType_e.swMateDISTANCE」「For distance and angle mates: *Minimum_variation* = *minimum_value* - *dimension_value*」 | **查不到** | `swMateType_e` | 无 Obsolete | ★ 仅 ANGLE / DISTANCE 有效 | 查不到 |
| 9 | `DistanceFirstArcCondition` | `System.int DistanceFirstArcCondition {get;}`（属性，0，只读） | 「This property is valid only for distance mates between: two cylindrical faces - or - one cylindrical face and one axis.」 | **查不到** | `swDistanceMateArcConditions_e`（本页未点名，**查不到本页关联**；全局数值见 §8） | 无 Obsolete | ★ 仅「两圆柱面」或「一圆柱面 + 一轴」的距离配合有效 | 查不到 |
| 10 | `DistanceSecondArcCondition` | `System.int DistanceSecondArcCondition {get;}`（属性，0，只读） | 同上逐字 | **查不到** | 同上 | 无 Obsolete | ★ 同上 | 查不到 |
| 11 | `GetForce` | `MathVector GetForce( out System.double Magnitude )`（0 入 + 1 out） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 12 | `SetForce` | `System.bool SetForce( System.double Magnitude, MathVector Direction )`（2） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 13 | `GetTorque` | `MathVector GetTorque( out System.double Angle )`（0 入 + 1 out） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 14 | `SetTorque` | `System.bool SetTorque( System.double Angle, MathVector Axis )`（2） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 15 | `LockMagneticMate` | `System.bool LockMagneticMate {get; set;}`（属性，0） | 「This property is valid only if [[IMate2::Type]] is set to [[swMateType_e]].swMateMAGNETIC.」 | **查不到** | `swMateType_e.swMateMAGNETIC = 25` | 无 Obsolete | ★ 仅 MAGNETIC 配合有效 | 查不到 |
| 16 | `HasLoadBearingFaces` | `System.bool HasLoadBearingFaces {get;}`（属性，0，只读） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 17 | `IsLoadBearingFacesBonded` | `System.bool IsLoadBearingFacesBonded {get;}`（属性，0，只读） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 18 | `HasTreatInterferenceAsShrinkFit` | `System.bool HasTreatInterferenceAsShrinkFit {get;}`（属性，0，只读） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 19 | `ForceMisalignment` | `System.bool ForceMisalignment()`（0） | `## Remarks` **为空** | **查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 20 | `RemoveMisalignment` | `System.bool RemoveMisalignment()`（0） | 「After calling this method, **one of the concentric mates may be unsolvable**.」 | `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | 无 Obsolete | ★ 官方警告：调完可能有一个同心配合变成**不可解** | 查不到 |
| 21 | `SetMaximumMisalignedDeviation` | `void SetMaximumMisalignedDeviation( System.double MaximumDeviation )`（1） | 「This method is valid only if [[IMate2::GetUseMisalignedDeviationDocumentProperty]] returns **false**. Call [[IMate2::SetUseMisalignedDeviationDocumentProperty]] to set UseDocumentProperty to false if you want to use this method…」「If [[IMate2::GetCurrentMisalignedDeviation]] is greater than the value set by this method, then **the mate fails to solve**.」「The current deviation and the maximum deviation are **cumulative** across both concentric mates in the Hole Set. For example, if …swConcentricAlignmentType_e.swConcentricAlignSymmetric, the deviation from both holes is summed before comparison with the maximum deviation.」 | **查不到** | `swConcentricAlignmentType_e.swConcentricAlignSymmetric` —— ★ **枚举数值查不到**（`C:\swapi\enums\` 无该文件） | 无 Obsolete | ★★ 必须先让 `GetUseMisalignedDeviationDocumentProperty()` 返回 `false` | 查不到 |
| 22 | `GetMaximumMisalignedDeviation` | `System.double GetMaximumMisalignedDeviation()`（0） | 同上「cumulative … summed before comparison with the maximum deviation」 | **查不到** | 同上 | 无 Obsolete | ★ 当前偏差 > 该值 ⇒ 配合解不出 | 查不到 |
| 23 | `GetCurrentMisalignedDeviation` | `System.double GetCurrentMisalignedDeviation()`（0） | 「If the current deviation of misalignment is greater than [[IMate2::GetMaximumMisalignedDeviation]], then the mate fails to solve.」＋ 同一段 cumulative 说明 | **查不到** | 同上 | 无 Obsolete | ★ 与 `GetMaximumMisalignedDeviation` 成对使用 | 查不到 |
| 24 | `GetUseMisalignedDeviationDocumentProperty` | `System.bool GetUseMisalignedDeviationDocumentProperty()`（0） | 「If this method returns false, then the maximum deviation used is returned by [[IMate2::GetMaximumMisalignedDeviation]].」 | **查不到** | 无 | 无 Obsolete | ★ 它是 `SetMaximumMisalignedDeviation` 的**门闸** | 查不到 |
| 25 | `SetUseMisalignedDeviationDocumentProperty` | `void SetUseMisalignedDeviationDocumentProperty( System.bool UseDocumentProperty )`（1） | 「If [[IMate2::GetCurrentMisalignedDeviation]] is greater than the document property value of the maximum misalignment deviation, then the mate fails to solve.」＋ cumulative 段 | **查不到** | 无 | 无 Obsolete | ★ 设为 `false` 才能用 `SetMaximumMisalignedDeviation` | 查不到 |
| 26 | `GetConcentricAlignmentType` | `System.int GetConcentricAlignmentType()`（0） | `## Remarks` **为空** | **查不到** | 返回值对应 `swConcentricAlignmentType_e`（本页**未点名** ⇒ **查不到**；名字见 #21） | 无 Obsolete | 查不到 | 查不到 |
| 27 | `SetConcentricAlignmentType` | `void SetConcentricAlignmentType( System.int PositionType )`（1） | `## Remarks` **为空** | **查不到** | 同上，**查不到** | 无 Obsolete | 查不到 | 查不到 |
| 28 | `GetLinkedMate` | `System.object GetLinkedMate()`（0） | 「This mate and its linked mate are **siblings in a Hole Set**, which is defined as two concentric mates between the same two components.」 | **查不到** | 无 | 无 Obsolete | ★ 定义逐字：Hole Set = 同一对组件之间的两个同心配合 | 查不到 |
| 29 | `GetSupplementalFaces` | `System.object GetSupplementalFaces( System.int WhichOne )`（1） | `## Remarks` **为空** | **查不到** | `WhichOne` 取值枚举**查不到** | 无 Obsolete | 查不到 | 查不到 |
| 30 | `MateLoadReference` | `MateLoadReference MateLoadReference {get;}`（属性，0，只读） | `## Remarks` **为空** | `Insert_Mate_Load_Reference_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | 无 Obsolete | 查不到 | 查不到 |
| 31 | `DisplayDimension` | 见 §7（已 Obsolete） | **未读** ⇒ **查不到（未抄）** | **查不到** | **查不到（未抄）** | 逐字 `Obsolete. Superseded by [[IMate2::DisplayDimension2]].` | 查不到 | 查不到 |
| 32 | `DisplayDimension2` | ★ **查不到** —— `C:\swapi\types\IMate2\DisplayDimension2.md` 全文 **10 行**，只有 YAML front-matter 与 `# IMate2.DisplayDimension2`，**没有 `**Signature**` 行、没有 `## Remarks`、没有 `## Examples`**（本轮用 grep `Signature|Obsolete` 零命中证实） | **查不到** | **查不到** | **查不到** | **无 Obsolete 标记**（不在 §7 清单里） | ★ 查不到（该文件是空壳） | 查不到 |

> ★ 逐字文件来源：`C:\swapi\types\IMate2\<成员>.md`。

---

## 6. `IComponent2` 其余已抄成员（与装配域相关的补充）

| # | 成员 | ① 精确签名（参数个数） | ② `## Remarks` 逐字 | ③ 官方例子调用序 | ④ 枚举 | ⑤ 废弃链 | 前置一句话 | 配方一句话 |
|---|---|---|---|---|---|---|---|---|
| 1 | `IComponent2.Transform2` | `MathTransform Transform2 {get; set;}`（属性，0） | 「This property affects the underlying model geometry and the display of the component.」「**You must specify the transform in relation to the root component.** This also applies when there is an in-context edit in progress. The transform is still with respect to the root component of the active assembly document, not with respect to the root component of the edit target.」「The destination component, or any component above it in the assembly tree, is moved so that the destination component's transform is set to the desired one.」「You can call [[IModelDoc2::Rebuild]] with the swUpdateMates argument to rebuild the model after transforming a component. This is much faster than rebuilding all of the geometry … using the now obsolete IAssemblyDoc::EditRebuild.」「This property lets you **violate existing mate relationships**.」「After you change a component's transform, you can call [[IAssemblyDoc::UpdateBox]] to avoid clipping in shaded display mode.」 | **查不到** | 无 | **无 Obsolete 标记**；是 `Transform` / `GetXform` / `SetXform` / `IGetXform` / `ISetXform` 的后继（§7） | ★★ 变换必须是**相对根组件**的（in-context 编辑时也一样）；可破坏配合 | 查不到 |
| 2 | `IComponent2.Select4` | `System.bool Select4( System.bool Append, SelectData Data, System.bool ShowPopup )`（3） | `## Remarks` **为空** ⇒ **查不到** | `Check_Interference_using_AssemblyDoc_ToolsCheckInterference2_Example_VB.md` 逐字：`Set swSelData = swSelMgr.CreateSelectData` / `bRet = swEnt.Select4(True, swSelData): Debug.Assert bRet` | 无 | ★ **无 Obsolete 标记** —— 是 `Select3` / `Select2` / `Select` / `SelectByMark` 的后继，且**自身不被标 Obsolete**（§7） | ★ 官方干涉例逐字用 `Select4(True, swSelData)`（**两参**，第三参省略） | `CreateSelectData` → `swEnt.Select4(True, swSelData)` |
| 3 | `IComponent2.GetChildren` | `System.object GetChildren()`（0） | 「If this assembly component is a part document, SOLIDWORKS returns NULL.」「The typical order of calls needed in assembly traversal is: 1. [[IConfigurationManager::ActiveConfiguration]] (called only once) 2. [[IConfiguration::GetRootComponent]] (called only once) 3. IComponent2::GetChildren (called recursively)」「**You must call the IComponent2::GetChildren method recursively** because it returns only the immediate (one level) children.」「This includes suppressed, hidden, and lightweight components. Use [[IComponent2::Visible]] and [[IComponent2::GetSuppression]] to detect the component states.」「**NOTE:** Components might not be returned in the same order from call to call.」 | `Set_All_Assembly_Components_Lightweight_or_Resolved_Example_VB.md` 逐字：`vChildCompArr = swComp.GetChildren` / `For Each vChildComp In vChildCompArr` / `Next vChildComp` | 无 | **无 Obsolete 标记**；是 `IAssemblyDoc::GetFirstMember` / `IGetFirstMember` 的后继（§7） | ★★ **必须递归**（只返回一层）；顺序**不保证稳定** | `ActiveConfiguration` → `GetRootComponent3(True)` → 递归 `GetChildren` |
| 4 | `IComponent2.IGetChildrenCount` | `System.int IGetChildrenCount()`（0） | 「This method returns a **single-level** count. The [[IComponent2::GetChildren]] and [[IComponent2::IGetChildren]] **do not recurse** sub-assemblies.」 | **查不到** | 无 | **无 Obsolete 标记** | ★ 只是**单层**计数 | 查不到 |
| 5 | `IComponent2.IsPatternInstance` | `System.bool IsPatternInstance()`（0） | 「True if the component is a member of  pattern instance, false if not」 ★ 原文此处有**双空格**「of  pattern」，逐字照抄 | **查不到** | 无 | **无 Obsolete 标记** | 无前置 | 查不到 |
| 6 | `IComponent2.GetMates` | `System.object GetMates()`（0） | 「This method **eliminates iterating through the list of mates**, which can adversely affect performance when the list of mates is long.」 | `Get_Mates_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | **无 Obsolete 标记** | 无显式前置 | 查不到 |
| 7 | `IComponent2.GetSpecificTransform` | `System.object GetSpecificTransform( System.bool IgnoreExplode )`（1） | `## Remarks` **为空** ⇒ **查不到** | **查不到** | 无 | **无 Obsolete 标记** | 查不到 | 查不到 |
| 8 | `IComponent2.GetTotalTransform` | `MathTransform GetTotalTransform( System.bool IncludePresentationXform )`（1） | `## Remarks` **为空** ⇒ **查不到** | `Get_Collapsed_Transform_of_Component_in_Exploded_View_Example_VB.md` 存在，**未逐字读 ⇒ 查不到** | 无 | **无 Obsolete 标记** | 查不到 | 查不到 |
| 9 | `IComponent2.IsVirtual` | `System.bool IsVirtual {get; set;}`（属性，0） | 「When you create components in the context of an assembly, the software can save them inside the assembly file, and you can immediately begin modeling. … Also, **no In-Place mate is created**, so you can position and constrain the component however you want.」 | **查不到** | 无 | **无 Obsolete 标记**；`MakeVirtual` 的后继是 `MakeVirtual2`（§7） | ★ 虚拟件**不会自动建 In-Place 配合** | 查不到 |
| 10 | `IComponent2.IsEnvelope` | `System.bool IsEnvelope()`（0） | 「SOLIDWORKS 2001Plus FCS, Revision Number 10.0」 | **查不到** | 无 | **无 Obsolete 标记** | 查不到 | 查不到 |
| 11 | `IComponent2.Visible` | `System.int Visible {get; set;}`（属性，0） | 「This functionality is also available using [[IModelDoc2::HideComponent2]] and [[IModelDoc2::ShowComponent2]].」 | **查不到** | 无 | **无 Obsolete 标记** | 查不到 | 查不到 |
| 12 | `IComponent2.SetVisibility` | `void SetVisibility( System.int State, System.int Config_opt, System.object Config_names )`（3） | `## Remarks` **为空** ⇒ **查不到** | **查不到** | `State` / `Config_opt` / `Config_names` 的枚举名与取值 **查不到**（本页未点名） | **无 Obsolete 标记** | 查不到 | 查不到 |
| 13 | `IComponent2.SetTransformAndSolve3` | `System.bool SetTransformAndSolve3( MathTransform XformIn, System.bool ThisConfiguration )`（2） | `## Remarks` **为空** ⇒ **查不到** | **查不到** | 无 | ★ **无 Obsolete 标记** —— 是 `SetTransformAndSolve2` / `SetTransformAndSolve` / `SetXformAndSolve` / `ISetXformAndSolve` 的后继，且自身未被标 Obsolete | 查不到 | 查不到 |
| 14 | `IComponent2.SetTransformAndSolve2` | `System.bool SetTransformAndSolve2( MathTransform XformIn )`（1） | `## Remarks` **为空** ⇒ **查不到** | **查不到** | 无 | 逐字 `Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].` | 查不到 | 查不到 |

### 6.1 `IComponent2` 全量签名清单（**166 个成员**，逐字 `**Signature**` 行已逐条读过）

> 逐字文件来源：`C:\swapi\types\IComponent2\<成员>.md`。★ 本清单只抄「①签名」这一项；②③④⑤ 各项**仅在上表 14 条 + §3.2 + §7 里已抄**，其余条目的 ②③④⑤ = **查不到（本轮未逐条抄）**。

```
AddPropertyExtension :: System.int AddPropertyExtension( System.object PropertyExtension )
ComponentReference :: System.string ComponentReference {get; set;}
CustomPropertyManager :: <<该文件无 **Signature** 行 —— 查不到>>
DeSelect :: System.bool DeSelect()
DisplayTitle :: System.string DisplayTitle {get;}
EnumBodies :: EnumBodies2 EnumBodies( System.int BodyType )
EnumBodies2 :: EnumBodies2 EnumBodies2( System.int BodyType )
EnumBodies3 :: EnumBodies2 EnumBodies3( System.int BodyType, System.bool VisibleOnly )
EnumRelatedBodies :: EnumBodies2 EnumRelatedBodies()
EnumSectionedBodies :: EnumBodies2 EnumSectionedBodies( ModelView ViewIn )
ExcludeFromBOM :: System.bool ExcludeFromBOM {get; set;}
FeatureByName :: Feature FeatureByName( System.string Name )
FindAttribute :: System.object FindAttribute( System.object AttributeDef, System.int WhichOne )
FirstFeature :: Feature FirstFeature()
GetBodies :: System.object GetBodies( System.int BodyType )
GetBodies2 :: System.object GetBodies2( System.int BodyType )
GetBodies3 :: System.object GetBodies3( System.int BodyType, out System.object BodiesInfo )
GetBody :: System.object GetBody()
GetBox :: System.object GetBox( System.bool IncludeRefPlanes, System.bool IncludeSketches )
GetChildren :: System.object GetChildren()
GetConfigurationCount :: System.int GetConfigurationCount()
GetConfigurationNames :: System.object GetConfigurationNames()
GetConstrainedStatus :: System.int GetConstrainedStatus()
GetCorresponding :: System.object GetCorresponding( System.object InputObject )
GetCorrespondingEntity :: System.object GetCorrespondingEntity( System.object Entity )
GetDecals :: System.object GetDecals()
GetDecalsCount :: System.int GetDecalsCount()
GetDrawingComponent :: DrawingComponent GetDrawingComponent( View ViewIn )
GetExcludeFromBOM2 :: System.object GetExcludeFromBOM2( System.int Config_opt, System.object Config_names )
GetHiddenUnloadedChildrenCount :: System.int GetHiddenUnloadedChildrenCount()
GetID :: System.int GetID()
GetImportedPath :: System.string GetImportedPath()
GetMaterialIdName :: System.string GetMaterialIdName()
GetMaterialPropertyValues2 :: System.object GetMaterialPropertyValues2( System.int Config_opt, System.object Config_names )
GetMaterialUserName :: System.string GetMaterialUserName()
GetMates :: System.object GetMates()
GetModelDoc :: System.object GetModelDoc()
GetModelDoc2 :: System.object GetModelDoc2()
GetModelMaterialPropertyValues :: System.object GetModelMaterialPropertyValues( System.string ConfigName )
GetModelTexture :: Texture GetModelTexture( System.string ConfigName )
GetParent :: Component2 GetParent()
GetPathName :: System.string GetPathName()
GetPLMID :: System.string GetPLMID()
GetPropertyExtension :: System.object GetPropertyExtension( System.int ID )
GetReferencedDisplayStates :: System.object GetReferencedDisplayStates( System.int AssemblyDisplayStateOption, System.object AssemblyDisplayStateNames )
GetRenderMaterials :: System.object GetRenderMaterials()
GetRenderMaterials2 :: System.object GetRenderMaterials2( System.int DisplayStateOption, System.object DisplayStateNames )
GetRenderMaterialsCount :: System.int GetRenderMaterialsCount()
GetRenderMaterialsCount2 :: System.int GetRenderMaterialsCount2( System.int DisplayStateOption, System.object DisplayStateNames )
GetRepresentationParent :: System.string GetRepresentationParent()
GetSectionedBodies :: System.object GetSectionedBodies( System.object ViewIn )
GetSelectByIDString :: System.string GetSelectByIDString()
GetSmartComponentData :: System.bool GetSmartComponentData( out System.object Features, out System.object FeaturesSelected, out System.object Components, out System.object ComponentsSelected, out System.object References )
GetSpecificTransform :: System.object GetSpecificTransform( System.bool IgnoreExplode )
GetSuppression :: System.int GetSuppression()
GetSuppression2 :: System.int GetSuppression2()
GetTessNorms :: System.object GetTessNorms()
GetTessTriangles :: System.object GetTessTriangles( System.bool NoConversion )
GetTessTriStripEdges :: System.object GetTessTriStripEdges()
GetTessTriStripNorms :: System.object GetTessTriStripNorms()
GetTessTriStrips :: System.object GetTessTriStrips( System.bool NoConversion )
GetTexture :: Texture GetTexture( System.string Config_name )
GetTotalTransform :: MathTransform GetTotalTransform( System.bool IncludePresentationXform )
GetType :: System.int GetType()
GetUnloadedComponentNames :: System.object GetUnloadedComponentNames( out System.object UnloadedComponentPathNames, out System.object UnloadedComponentReferencedConfigurationNames, out System.object ReasonForUnloadingComponents, out System.object DocTypes )
GetVisibility :: System.object GetVisibility( System.int Config_opt, System.object Config_names )
GetVisibilityInAsmDisplayStates :: System.object GetVisibilityInAsmDisplayStates( System.int AssemblyDisplayStateOption, System.object AssemblyDisplayStateNames )
GetXform :: System.object GetXform()
HasAssemblyFeatures :: System.bool HasAssemblyFeatures( out System.string ConfigurationName )
HasMaterialPropertyValues :: System.bool HasMaterialPropertyValues()
HasUnloadedComponents :: System.bool HasUnloadedComponents()
IFindAttribute :: Attribute IFindAttribute( AttributeDef AttributeDef, System.int WhichOne )
IGetBody :: Body2 IGetBody()
IGetBox :: System.double IGetBox( System.bool IncludeRefPlanes, System.bool IncludeSketches )
IGetChildren :: Component2 IGetChildren()
IGetChildrenCount :: System.int IGetChildrenCount()
IGetCorrespondingEntity :: Entity IGetCorrespondingEntity( Entity PEntity )
IGetDecals :: Decal IGetDecals( System.int Count )
IGetMaterialPropertyValues2 :: System.double IGetMaterialPropertyValues2( System.int Config_opt, System.int Config_count, ref System.string Config_names )
IGetMaterialPropertyValuesForFace :: System.double IGetMaterialPropertyValuesForFace( System.object FaceIn )
IGetModelDoc :: ModelDoc2 IGetModelDoc()
IGetModelMaterialPropertyValues :: System.double IGetModelMaterialPropertyValues( System.string ConfigName )
IGetRenderMaterials :: RenderMaterial IGetRenderMaterials( System.int Count )
IGetTemporaryBodyID :: System.int IGetTemporaryBodyID()
IGetTessNorms :: System.float IGetTessNorms()
IGetTessTriangleCount :: System.int IGetTessTriangleCount()
IGetTessTriangles :: System.float IGetTessTriangles( System.bool NoConversion )
IGetTessTriStripEdges :: System.int IGetTessTriStripEdges()
IGetTessTriStripEdgeSize :: System.int IGetTessTriStripEdgeSize()
IGetTessTriStripNorms :: System.float IGetTessTriStripNorms()
IGetTessTriStrips :: System.float IGetTessTriStrips( System.bool NoConversion )
IGetTessTriStripSize :: System.int IGetTessTriStripSize()
IGetVisibility :: System.int IGetVisibility( System.int Config_opt, System.int Config_count, ref System.string Config_names )
IGetXform :: System.double IGetXform()
IListExternalFileReferences :: void IListExternalFileReferences( System.int NumRefs, out System.string ModelPathName, out System.string CompPathName, out System.string Feature, out System.string DataType, out System.int Status, out System.string RefEntity, out System.string FeatComp )
IListExternalFileReferences2 :: void IListExternalFileReferences2( System.int NumRefs, out System.string ModelPathName, out System.string CompPathName, out System.string Feature, out System.string DataType, out System.int Status, out System.string RefEntity, out System.string FeatComp, out System.int ConfigOption, out System.string ConfigName )
IMaterialPropertyValues :: System.double IMaterialPropertyValues {get; set;}
IRemoveMaterialProperty2 :: System.bool IRemoveMaterialProperty2( System.int Config_opt, System.int Config_count, ref System.string Config_names )
IsDisplayDataOutOfDate :: System.int IsDisplayDataOutOfDate()
IsEnvelope :: System.bool IsEnvelope()
ISetMaterialPropertyValues2 :: void ISetMaterialPropertyValues2( ref System.double Material_values, System.int Config_opt, System.int Config_count, ref System.string Config_names )
ISetVisibility :: void ISetVisibility( System.int State, System.int Config_opt, System.int Config_count, ref System.string Config_names )
ISetXform :: System.bool ISetXform( ref System.double XformIn )
ISetXformAndSolve :: System.bool ISetXformAndSolve( ref System.double XformIn )
IsFixed :: System.bool IsFixed()
IsGraphicsOnly :: System.bool IsGraphicsOnly {get;}
IsHidden :: System.bool IsHidden( System.bool ConsiderSuppressed )
IsLoaded :: System.bool IsLoaded()
IsMirrored :: System.bool IsMirrored()
IsNameOverridden :: System.bool IsNameOverridden()
IsPatternInstance :: System.bool IsPatternInstance()
IsRoot :: System.bool IsRoot()
IsSmartComponent :: System.bool IsSmartComponent()
IsSpeedPak :: System.bool IsSpeedPak {get;}
IsSuppressed :: System.bool IsSuppressed()
IsVirtual :: System.bool IsVirtual {get; set;}
ListExternalFileReferences :: void ListExternalFileReferences( out System.object ModelPathName, out System.object ComponentPathName, out System.object Feature, out System.object DataType, out System.object Status, out System.object RefEntity, out System.object FeatCom )
ListExternalFileReferences2 :: void ListExternalFileReferences2( out System.object ModelPathName, out System.object ComponentPathName, out System.object Feature, out System.object DataType, out System.object Status, out System.object RefEntity, out System.object FeatCom, out System.int ConfigOption, out System.string ConfigName )
ListExternalFileReferencesCount :: System.int ListExternalFileReferencesCount()
MakeVirtual :: System.bool MakeVirtual()
MakeVirtual2 :: System.bool MakeVirtual2( System.bool AlsoChildVirtual )
MaterialPropertyValues :: System.object MaterialPropertyValues {get; set;}
Name :: System.string Name {get;}
Name2 :: System.string Name2 {get; set;}
PresentationTransform :: MathTransform PresentationTransform {get; set;}
ReferencedConfiguration :: System.string ReferencedConfiguration {get; set;}
ReferencedDisplayState :: System.string ReferencedDisplayState {get;}
ReferencedDisplayState2 :: System.string ReferencedDisplayState2 {get; set;}
RemoveMaterialProperty :: System.bool RemoveMaterialProperty()
RemoveMaterialProperty2 :: System.bool RemoveMaterialProperty2( System.int Config_opt, System.object Config_names )
RemovePresentationTransform :: void RemovePresentationTransform()
RemoveTexture :: System.bool RemoveTexture( System.string Config_name )
RemoveTextureByDisplayState :: System.bool RemoveTextureByDisplayState( System.string DisplayStateName )
ReplaceReference :: System.int ReplaceReference( System.string FileName )
ResetPropertyExtension :: void ResetPropertyExtension()
SaveVirtualComponent :: System.bool SaveVirtualComponent( System.string CompPathName )
Select :: System.bool Select( System.bool AppendFlag )
Select2 :: System.bool Select2( System.bool Append, System.int Mark )
Select3 :: System.bool Select3( System.bool Append, SelectData Data )
Select4 :: System.bool Select4( System.bool Append, SelectData Data, System.bool ShowPopup )
SelectByMark :: System.bool SelectByMark( System.bool AppendFlag, System.int Mark )
SetCosmosWorksMaterial :: System.bool SetCosmosWorksMaterial( System.string ConfigName, System.int Type )
SetExcludeFromBOM2 :: System.int SetExcludeFromBOM2( System.bool Exclude, System.int Config_opt, System.object Config_names )
SetMaterialIdName :: System.bool SetMaterialIdName( System.string Name )
SetMaterialPropertyValues2 :: void SetMaterialPropertyValues2( System.object Material_values, System.int Config_opt, System.object Config_names )
SetMaterialUserName :: System.bool SetMaterialUserName( System.string Name )
SetReferencedDisplayStates :: System.bool SetReferencedDisplayStates( System.string ComponentDisplayStateName, System.int Option, System.object AssemblyDisplayStateNames )
SetSmartComponentData :: System.bool SetSmartComponentData( System.object FeaturesSelected, System.object ComponentsSelected, System.object References )
SetSuppression :: System.int SetSuppression( System.int State )
SetSuppression2 :: System.int SetSuppression2( System.int State )
SetTexture :: System.bool SetTexture( System.string Config_name, Texture TextureIn )
SetTextureByDisplayState :: System.bool SetTextureByDisplayState( System.string DisplayStateName, Texture TextureIn )
SetTransformAndSolve :: System.bool SetTransformAndSolve( MathTransform XformIn )
SetTransformAndSolve2 :: System.bool SetTransformAndSolve2( MathTransform XformIn )
SetTransformAndSolve3 :: System.bool SetTransformAndSolve3( MathTransform XformIn, System.bool ThisConfiguration )
SetVisibility :: void SetVisibility( System.int State, System.int Config_opt, System.object Config_names )
SetVisibilityInAsmDisplayStates :: System.bool SetVisibilityInAsmDisplayStates( System.int HideComponent, System.int Option, System.object AssemblyDisplayStateNames )
SetXform :: System.bool SetXform( System.object XformIn )
SetXformAndSolve :: System.bool SetXformAndSolve( System.object XformIn )
Solving :: System.int Solving {get;}
Transform :: MathTransform Transform {get; set;}
Transform2 :: MathTransform Transform2 {get; set;}
UpdateExternalFileReferences :: void UpdateExternalFileReferences( System.int ConfigOption, System.string ConfigName, System.int UpdateStatus )
UseNamedConfiguration :: System.bool UseNamedConfiguration {get;}
Visible :: System.int Visible {get; set;}
```

★ 逐字发现两处「签名行缺失」：`CustomPropertyManager.md` 的正文没有任何 `**Signature**:` 行 ⇒ **查不到**；`IComponent2` 里 **`IGetMaterialPropertyValuesForFace`** 与 `IGetTemporaryBodyID` 在同一次批量清单里出现但 **本轮未单独核对**其页面（**未抄**）。

---

## 7. 五个接口的 Obsolete 废弃链总表（逐字）

> 逐字来源：对 `C:\swapi\types\{IAssemblyDoc,IExplodeStep,IComponent2,IMate2,IInterferenceDetectionMgr}\` 下全部 `.md`（除 `_overview.md`）逐文件正则提取以 `Obsolete.` 开头的整行。
> ★ **`IExplodeStep` 与 `IInterferenceDetectionMgr` 各有 0 条 Obsolete** ⇒ 这两个接口**没有成员被官方标废弃**。

### 7.1 `IAssemblyDoc`（**70 条**）

```
AddComponent              ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponent4]].
AddComponent2             ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponent4]].
AddComponent4             ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponent5]].
AddComponents              ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponents3]].
AddMate                   ==> Obsolete. Superseded by [[IAssemblyDoc::AddMate3]].
AddMate2                  ==> Obsolete. Superseded by [[IAssemblyDoc::AddMate3]].
AddMate3                  ==> Obsolete. Superseded by [[IAssemblyDoc::AddMate4]].
AddMate4                  ==> Obsolete. Superseded by IAssemblyDoc::AddMate5.            ← 原文无 [[ ]]
AddMate5                  ==> Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]      ← 原文 CreateMate. 带多余句点
AssemblyPartToggle        ==> Obsolete. Superseded by [[IAssemblyDoc::EditAssembly]] and [[IAssemblyDoc::EditPart2]].
CompConfigProperties      ==> Obsolete. Superseded by [[IAssemblyDoc::CompConfigProperties4]].
CompConfigProperties2     ==> Obsolete. Superseded by [[IAssemblyDoc::CompConfigProperties4]].
CompConfigProperties3     ==> Obsolete. Superseded by [[IAssemblyDoc::CompConfigProperties4]].
CompConfigProperties4     ==> Obsolete. Superseded by [[IAssemblyDoc::CompConfigProperties5]].
CompConfigProperties5     ==> Obsolete. Superseded by [[IAssemblyDoc::CompConfigProperties6]].
ComponentReload           ==> Obsolete. Superseded by [[IAssemblyDoc::ComponentReload2]].
CopyWithMates             ==> Obsolete. Superseded by [[IAssemblyDoc::CopyWithMates2]].
EditMate                  ==> Obsolete. Superseded by [[IAssemblyDoc::EditMate2]].
EditMate2                 ==> Obsolete. Superseded by IAssemblyDoc::EditMate3.           ← 原文无 [[ ]]
EditMate3                 ==> Obsolete. Superseded by IAssemblyDoc::EditMate4.           ← 原文无 [[ ]]
EditMate4                 ==> Obsolete. See the Remarks in each standard, advanced, and mechanical mate's feature data interface.   ← ★ 未点名单一成员
EditPart                  ==> Obsolete. Superseded by [[IAssemblyDoc::EditPart2]].
EditRebuild               ==> Obsolete. Superseded by [[IModelDoc2::EditRebuild3]].
FeatureExtrusion          ==> Obsolete. Superseded by [[IFeatureManager::FeatureExtrusion]].
ForceRebuild              ==> Obsolete. Superseded by [[IModelDoc2::ForceRebuild3]].
ForceRebuild2             ==> Obsolete. Superseded by [[IModelDoc2::ForceRebuild3]].
ForceUpdateElectricalData ==> Obsolete. Superseded by [[IAssemblyDoc::ForceUpdateElectricalData2]].
GetExplodedViewCount      ==> Obsolete. Superseded by [[IAssemblyDoc::GetExplodedViewCount2]].
GetExplodedViewNames      ==> Obsolete. Superseded by [[IAssemblyDoc::GetExplodedViewNames2]].
GetFirstMember            ==> Obsolete. Superseded by [[IComponent2::GetChildren]].
GetPhysicalSimulationComponents ==> Obsolete. Not superseded.                          ← ★ 官方写「无后继」
GetSelectedMember         ==> Obsolete. Superseded by [[ISelectionMgr::GetSelectedObject6]].
GetSimulation             ==> Obsolete. Not superseded.                                ← ★ 官方写「无后继」
HideComponent             ==> Obsolete. Superseded by [[IModelDoc2::HideComponent2]].
IAddComponent2            ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponent4]].
IAddComponent3            ==> Obsolete. Superseded by [[IAssemblyDoc::AddComponent4]].
IAddComponents            ==> Obsolete. Superseded by [[IAssemblyDoc::IAddComponents2]].
IAddComponents2           ==> Obsolete. Superseded by [[IAssemblyDoc::IAddComponents3]].
IComponentReload2         ==> Obsolete. Superseded by [[IAssemblyDoc::ReplaceComponents]].
IComponentReload3         ==> Obsolete. Superseded by [[IAssemblyDoc::ReplaceComponents]].
IGetEditTarget            ==> Obsolete. Superseded by [[IAssemblyDoc::IGetEditTarget2]].
IGetExplodedViewNames     ==> Obsolete. Superseded by [[IAssemblyDoc::GetExplodedViewNames2]].
IGetFirstMember           ==> Obsolete. Superseded by [[IComponent2::GetChildren]].
IGetSelectedMember        ==> Obsolete. Superseded by [[SelectionMgr::GetSelectedObject6]].  ← 原文用 SelectionMgr::（无 I）
IMirrorComponents         ==> Obsolete. Superseded by [[IAssemblyDoc::MirrorComponents2]].
InsertCavity              ==> Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]].
InsertCavity2             ==> Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]].
InsertCavity3             ==> Obsolete. Superseded by [[IAssemblyDoc::InsertCavity4]].
InsertDerivedPattern      ==> Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[IDerivedPatternFeatureData]].
InsertJoin                ==> Obsolete. Superseded by [[IAssemblyDoc::InsertJoin2]].
InsertNewPart             ==> Obsolete. Superseded by [[IAssemblyDoc::InsertNewPart2]].
InsertWeld                ==> Obsolete. Do not use. Superseded by [[IFeatureManager::InsertCosmeticWeldBead]].
InsertWeld2               ==> Obsolete. Do not use. Superseded by [[IFeatureManager::InsertCosmeticWeldBead]].
IToolsCheckInterference2  ==> Obsolete. See [[IAssemblyDoc::IToolsCheckInterference3]].
IToolsCheckInterference3  ==> Obsolete.                                                         ← ★★★ 官方原文只有「Obsolete.」无后继 ⇒ 查不到
MirrorComponents          ==> Obsolete. Superseded by IAssemblyDoc::MirrorComponents2.     ← 原文无 [[ ]]
MirrorComponents2         ==> Obsolete. Superseded by [[IAssemblyDoc::MirrorComponents3]].
MirrorComponents3         ==> Obsolete. Superseded by [[IFeatureManager::CreateDefinition]], [[IFeatureManager::CreateFeature]], and [[IMirrorComponentFeatureData]].
OpenCompFile              ==> Obsolete. Superseded by [[ISldWorks::ActivateDoc2]] and [[ISldWorks::OpenDoc6]].
ReplaceComponents         ==> Obsolete. Superseded by [[IAssemblyDoc::ReplaceComponents2]].
ShowExploded              ==> Obsolete. Superseded by [[IAssemblyDoc::ShowExploded2]].
ToolsCheckInterference    ==> Obsolete. Superseded by [[IAssemblyDoc::ToolsCheckInterference2]].
ViewFeatureManagerByDependencies ==> Obsolete. Superseded by [[IFeatureManager::ViewDependencies]].
ViewFeatureManagerByFeatures ==> Obsolete. Superseded by [[IFeatureManager::ViewFeatures]].
ViewFeatureManagerFeatureDetail ==> Obsolete. Superseded by [[IFeatureManager::ShowFeatureDetails]].
```

### 7.2 `IComponent2`（**34 条**）

```
EnumBodies                        ==> Obsolete. Superseded by [[IComponent2::EnumBodies2]].
EnumBodies2                       ==> Obsolete. Superseded by [[IComponent2::EnumBodies3]].
ExcludeFromBOM                    ==> Obsolete. Superseded by [[IComponent2::GetExcludeFromBOM2]] and [[IComponent2::SetExcludeFromBOM2]].
GetBodies                         ==> Obsolete. Superseded by [[IComponent2::GetBodies2]].
GetBodies2                        ==> Obsolete. Superseded by [[IComponent2::GetBodies3]].
GetModelDoc                       ==> Obsolete. Superseded by [[IComponent2::GetModelDoc2]].
GetRenderMaterials                ==> Obsolete. Superseded by [[IComponent2::GetRenderMaterials2]].
GetRenderMaterialsCount           ==> Obsolete. Superseded by [[IComponent2::GetRenderMaterialsCount2]].
GetSuppression                    ==> Obsolete. Superseded by [[IComponent2::GetSuppression2]].
GetXform                          ==> Obsolete. Superseded by [[IComponent2::Transform2]].
IGetModelDoc                      ==> Obsolete. Superseded by [[IComponent2::GetModelDoc2]].
IGetRenderMaterials               ==> Obsolete. Superseded by [[IComponent2::GetRenderMaterials2]].
IGetXform                         ==> Obsolete. Superseded by [[IComponent2::Transform2]].
IListExternalFileReferences       ==> Obsolete. Superseded by [[IComponent2::IListExternalFileReferences2]].
ISetXform                         ==> Obsolete. Superseded by [[IComponent2::Transform2]].
ISetXformAndSolve                 ==> Obsolete. Superseded by [[IComponent2::SetTransformAndSolve2]].
ListExternalFileReferences        ==> Obsolete. Superseded by [[IComponent2::ListExternalFileReferences2]].
MakeVirtual                       ==> Obsolete. by Superseded by [[IComponent2::MakeVirtual2]].   ← 原文「Obsolete. by Superseded by」语序错，逐字照抄
Name                              ==> Obsolete. Superseded by [[IComponent2::Name2]].
ReferencedDisplayState            ==> Obsolete. Superseded by [[IComponent2::ReferencedDisplayState2]].
RemoveMaterialProperty            ==> Obsolete. Superseded by [[IComponent2::RemoveMaterialProperty2]].
ReplaceReference                  ==> Obsolete. Superseded by [[AssemblyDoc::ReplaceComponents]].   ← 原文用 AssemblyDoc::（无 I）
Select                            ==> Obsolete. Superseded by [[IComponent2::Select3]].
Select2                           ==> Obsolete. Superseded by [[IComponent2::Select3]].
Select3                           ==> Obsolete. Superseded by [[IComponent2::Select4]].
SelectByMark                      ==> Obsolete. Superseded by [[IComponent2::Select3]].
SetSuppression                    ==> Obsolete. Superseded by [[IComponent2::SetSuppression2]].
SetTransformAndSolve              ==> Obsolete. Superseded by [[IComponent2::SetTransformAndSolve2]].
SetTransformAndSolve2             ==> Obsolete. Superseded by [[IComponent2::SetTransformAndSolve3]].
SetXform                          ==> Obsolete. Superseded by [[IComponent2::Transform2]].
SetXformAndSolve                  ==> Obsolete. Superseded by [[IComponent2::SetTransformAndSolve2]].
Transform                         ==> Obsolete. Superseded by [[IComponent2::Transform2]].
```

### 7.3 `IMate2`（**1 条**）

```
DisplayDimension ==> Obsolete. Superseded by [[IMate2::DisplayDimension2]].
```

### 7.4 `IExplodeStep` / `IInterferenceDetectionMgr`

**各 0 条 Obsolete** ⇒ 官方未把这两个接口的任何成员标废弃。

### 7.5 ★ 官方「查不到后继」的三处（照纪律单列）

| 成员 | 官方逐字 |
|---|---|
| `IAssemblyDoc.IToolsCheckInterference3` | `Obsolete.` ← **后面什么都没有** ⇒ **查不到** |
| `IAssemblyDoc.GetPhysicalSimulationComponents` | `Obsolete. Not superseded.` |
| `IAssemblyDoc.GetSimulation` | `Obsolete. Not superseded.` |

另有三处官方**指向多目标而非单一成员**（不构成「查不到」，但也不是单一后继）：`EditMate4`（指向各 mate feature data 接口的 Remarks）、`InsertDerivedPattern`（`IFeatureManager::CreateFeature` + `IDerivedPatternFeatureData`）、`MirrorComponents3`（三个目标）。

---

## 8. 枚举（逐字抄 `C:\swapi\enums\*.md`）

### 8.1 `swMateType_e`（26 个成员）—— `enum_member_count: 26`
| Member | Value |
|---|---|
| swMateANGLE | 6 |
| swMateCAMFOLLOWER | 9 |
| swMateCOINCIDENT | 0 |
| swMateCONCENTRIC | 1 |
| swMateCOORDINATE | 20 |
| swMateDISTANCE | 5 |
| swMateGEAR | 10 |
| swMateHINGE | 22 |
| swMateLINEARCOUPLER | 18 |
| swMateLOCK | 16 |
| swMateLOCKTOSKETCH | 12 |
| swMateMAGNETIC | 25 |
| swMateMAXMATES | 14 |
| swMatePARALLEL | 3 |
| swMatePATH | 15 |
| swMatePERPENDICULAR | 2 |
| swMatePROFILECENTER | 24 |
| swMateRACKPINION | 13 |
| swMateSCREW | 17 |
| swMateSLIDER | 23 |
| swMateSLOT | 21 |
| swMateSYMMETRIC | 8 |
| swMateTANGENT | 4 |
| swMateUNIVERSALJOINT | 19 |
| swMateUNKNOWN | 7 |
| swMateWIDTH | 11 |

### 8.2 `swMateAlign_e`（6 个成员）—— `enum_member_count: 6`
`## Remarks` 逐字：「These values have been changed to correct improper mate alignment mapping.」

| Member | Value |
|---|---|
| swAlignAGAINST | **Obsolete. Do not use.**（无数值） |
| swAlignNONE | **Obsolete. Do not use.**（无数值） |
| swAlignSAME | **Obsolete. Do not use.**（无数值） |
| swMateAlignALIGNED | 0 |
| swMateAlignANTI_ALIGNED | 1 |
| swMateAlignCLOSEST | 2 |

### 8.3 `swAddMateError_e`（7 个成员）—— `enum_member_count: 7`
> ★ 该文件的「Value」列装的是**描述**，数值与描述用 `=` 相连，逐字照抄。

| Member | Value |
|---|---|
| swAddMateError_ErrorUknown | 0 = Unknown error occurred（★ 官方拼写 `ErrorUknown`，少一个 n） |
| swAddMateError_IncorrectAlignment | 3 = Unknown mate alignment or mate alignment is not present in [[swMateAlign_e]] |
| swAddMateError_IncorrectGearRatios | 6 = Mate gear ratios are invalid |
| swAddMateError_IncorrectMateType | 2 = Unknown mate type or mate type not present in [[swMateType_e]] |
| swAddMateError_IncorrectSelections | 4 = Incorrect selections for mate |
| swAddMateError_NoError | 1 = Success, no error |
| swAddMateError_OverDefinedAssembly | 5 = Mate is over-defining the assembly |

### 8.4 `swDistanceMateArcConditions_e`（4 个成员）—— `enum_member_count: 4`
| Member | Value |
|---|---|
| swArcCondition_Center | 1; Cylindrical axis |
| swArcCondition_Maximum | 3; Furthest arc |
| swArcCondition_Minimum | 2; Nearest arc |
| swArcCondition_NotSet | 0 |

### 8.5 `swMateWidthOptions_e`（4 个成员）—— `enum_member_count: 4`
| Member | Value |
|---|---|
| swMateWidth_Centered | 0 |
| swMateWidth_Dimension | 2 |
| swMateWidth_Free | 1 |
| swMateWidth_Percent | 3 |

### 8.6 `swComponentResolveStatus_e`（4 个成员）—— `enum_member_count: 4`
| Member | Value |
|---|---|
| swResolveAbortedByUser | 1 = User aborted resolving the components |
| swResolveError | 3 = Not used |
| swResolveNotPerformed | 2 = Some of the components did not get resolved despite the user requesting it |
| swResolveOk | 0 = Components resolved okay |

### 8.7 `swComponentSuppressionState_e`（6 个成员）—— `enum_member_count: 6`
| Member | Value |
|---|---|
| swComponentFullyLightweight | 4 = Fully lightweight - recursively makes the component and any child components lightweight |
| swComponentFullyResolved | 2 = Fully resolved - recursively resolves the component and any child components |
| swComponentInternalIdMismatch | 5 |
| swComponentLightweight | 1 = Lightweight - makes only the component lightweight |
| swComponentResolved | 3 = Resolved - resolves only the component |
| swComponentSuppressed | 0 = Fully suppressed - recursively suppresses the component and any child components |

### 8.8 `swExplodeDirectionIndex_e`（4 个成员）—— `enum_member_count: 4`
| Member | Value |
|---|---|
| swExplodeDirectionIndex_Unknown | -1 = Use in [[IExplodeStep::SetExplodeDirection]] to continue using the current enumerator value |
| swExplodeDirectionIndex_XAxis | 0 |
| swExplodeDirectionIndex_YAxis | 1 |
| swExplodeDirectionIndex_ZAxis | 2 |

### 8.9 ★ 签名/Remarks 里出现、但 `C:\swapi\enums\` **没有对应文件**的枚举（本轮逐字 grep 确认）

| 枚举名 | 出现在哪 | 数值 |
|---|---|---|
| `swAssemblyExplodeStepType_e` | `IExplodeStep.ExplodeStepType` 返回类型 + `DivergeDirection` / `DivergeFromAxis` / `ReverseRotationDirection` / `ReverseTranslationDirection` / `RotateAboutEachComponentOrigin` / `RotationAngle` / `GetSubAssemblyExplodeSteps` 的 Remarks | ★ **查不到**（`enums\*.md` 全目录 grep `swAssemblyExplodeStepType` **零命中**） |
| `swConcentricAlignmentType_e` | `IAssemblyDoc.AddConcentricMateWithTolerance` / `EditConcentricMate` 的 `ConcentricPositionType` 语义 + `IMate2.SetMaximumMisalignedDeviation` 等 Remarks（`swConcentricAlignSymmetric`） | ★ **查不到** |
| `swAutoMateRepairErrors_e` | `IAssemblyDoc.AutoMateRepair` 返回值语义 | ★ **查不到**（文件存在，本轮未逐字读数值） |
| `swCheckInterferenceOption_e` | 文件存在（`C:\swapi\enums\swCheckInterferenceOption_e.md`），本轮未与 `IInterferenceDetectionMgr` 任一成员对上 | ★ **查不到**（未逐字读） |

---

## 9. 抄录员给出的「查不到」清单（★ 只列事实，不给建议）

1. **`swAssemblyExplodeStepType_e` 全部数值** —— 爆炸步类型判定（Radial / Translate / SubAssembly）在 `IExplodeStep` 里被 **7 个成员逐字引用**，但 `C:\swapi\enums\` 全目录 grep **零命中** ⇒ 数值**查不到**。
2. **`IToolsCheckInterference3` 的后继** —— 官方 Obsolete 行只有 `Obsolete.` 四个字，**无任何后继** ⇒ **查不到**。
3. **`IMate2.DisplayDimension2` 的签名** —— `C:\swapi\types\IMate2\DisplayDimension2.md` 全文 10 行，**只有 front-matter 与标题**，无 `**Signature**` 行、无 `## Remarks`、无 `## Examples` ⇒ **查不到**（而它的前身 `DisplayDimension` 已被标 Obsolete 指向它）。
4. **`IComponent2.CustomPropertyManager` 的签名** —— 该文件无 `**Signature**` 行 ⇒ **查不到**。
5. **`IAssemblyDoc.ClearanceVerificationManager` 的返回类型** —— 逐字只写 `System.object`，**未给接口名** ⇒ **查不到**。
6. **`IInterferenceDetectionMgr.NonInterferingComponentDisplay` 的取值口径** —— 返回 `System.int`，`C:\swapi\enums\` 无对应枚举文件 ⇒ **查不到**。
7. **本域的 CHM 参考页** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 下 `AddMate5_Method.htm` / `IToolsCheckInterference3_Method.htm` / `CreateExplodedView_Method.htm` / `SetSuppression2_Method.htm` / `ExplodeStep_Property.htm` **全部不存在** ⇒ 该源对本域的「说明与 See Also」**查不到**。
8. **官方例子未示范的成员（本轮逐字读过例子、确认其中不含该调用）**：`AutoExplode` · `DissolveComponentPattern` · `IExplodeStep.SetComponents` / `SetExplodeDirection` / `SetRotationAxis` / `RotationAngle` / `AutoSpaceComponentsOnDrag` / `DivergeDirection` / `DivergeFromAxis` / `ReverseRotationDirection` / `ReverseTranslationDirection` / `RotateAboutEachComponentOrigin` / `GetSubAssemblyExplodeSteps` · `ResolveAllLightWeightComponents` · `ResolveOutOfDateLightWeightComponents` · `IAssemblyDoc.InterferenceDetectionManager` · `ToolsCheckInterference` · `IToolsCheckInterference2` / `IToolsCheckInterference3` · `IInterferenceDetectionMgr` 全部 22 个 · `AddMate2` … `AddMate5` · `CreateMate` / `CreateMateData` · `EditMate*` · `AddConcentricMateWithTolerance` / `AddDistanceMate` · `AutoMateRepair` / `CollectAllSupportiveMates` · `IMate2` 除 `GetNumOfComponents` / `Name` / `IsSubAssemblyRigid`（走 `Get_Explode_Step_Example_VB.md`）外的全部。
   ⇒ 它们的「③ 官方例子调用序」= **查不到**。
9. **例子文件名存在但本轮未逐字读其代码**（故「③」标查不到而非「该成员无例子」）：`Run_Interference_Detection_Example_VB.md` · `Get_Visibility_of_and_Resolve_Lightweight_Components_Example_VB.md` · `Get_Whether_Components_Are_Loaded_Example_VB.md` · `Set_Components_and_Transforms_for_Interference_Detection_Example_VB.md` · `Detect_Interferences_Using_a_Transform_Example_VB.md` · `Set_Components_Transparent_Example_VB.md` · `Add_and_Edit_Misaligned_Symmetric_Concentric_Mate_Example_VB.md` · `Add_Distance_Mates_Example_VB.md` · `Create_Limit_Distance_Mate_Example_VB.md` · `Add_and_Edit_Distance_Mate_Example_VB.md` · `Create_Standard_Mates_Example_VB.md` · `Create_Symmetric_Mate_Example_VB.md` · `Create_Width_Mate_Example_VB.md` · `Create_Limit_Angle_Mate_Example_VB.md` · `Rack_and_Pinion_Mate_Example_CSharp.md` · `Edit_Mate_Example_VB.md` · `Edit_Mate_Reference_Example_VB.md` · `Repair_Mates_Missing_Same_Mate_Entity_Example_VB.md` · `Create_Mate_Controller_Example_VB.md` · `Get_Mates_Example_VB.md` · `Get_Mates_and_Mate_Entities_Example_VB.md` · `Insert_Mate_Load_Reference_Example_VB.md` · `Get_Collapsed_Transform_of_Component_in_Exploded_View_Example_VB.md` · `Add_Explode_Step_Example_VB.md` · `Add_Multibody_Part_Explode_Step_Example_VB.md` / `_CSharp.md` · `Edit_Radial_Explode_Step_Example_VB.md` · `Get_Exploded_Views_for_Configuration_Example_VB.md` · `Make_Assembly_Components_Lightweight_Example_VB.md` · `Set_Fully_Resolved_Assembly_to_Lightweight_Example_VB.md`
10. **`IAssemblyDoc` 其余未逐条抄的成员（签名只在本轮批量清单里见过名字）**：`ActivateGroundPlane` `AddComponentConfiguration` `AddComponents3` `AddPipePenetration` `AddPipingFitting` `AddPLMComponent` `AddSmartComponent` `AddToFeatureScope` `ClearanceVerificationManager` `CompConfigProperties6` `ComponentReload2` `CopyWithMates2` `DeleteSelections` `DissolveSubAssembly` `EditAssembly` `EnableAssemblyRebuild` `EnablePresentation` `ExitIsolate` `GetAdvancedSelection` `GetBox` `GetComponentByID` `GetComponentByName` `GetComponentCount` `GetComponents` `GetDragOperator` `GetDroppedAtEntity` `GetEditTarget` `GetEditTargetComponent` `GetFeatureScope` `GetFeatureScopeCount` `GetLargeDesignReviewState` `GetRouteManager` `GetSimulation` `GetVisibleComponentsInView` `GetVisibleComponentsInViewCount` `IAddComponents3` `IComponentReload2` `IFeatureByName` `IGetBox` `IGetComponents` `IGetDragOperator` `IGetEditTarget2` `IGetExplodedViewNames` `IGetFeatureScope` `IGetSelectedMember` `IGetVisibleComponentsInView` `InsertCavity4` `InsertEnvelope` `InsertImportedComponent` `InsertJoin2` `InsertLoadReference` `InsertNewAssembly` `InsertNewPart2` `InsertNewVirtualAssembly` `InsertNewVirtualPart` `InsertWeld2` `IsComponentTreeValid` `ISetComponentState` `ISetComponentVisibility` `Isolate` `IsRouteAssembly` `LargeDesignReviewTransparencyLevel` `LargeDesignReviewTransparencyLevelDynamic` `LargeDesignReviewTransparencyLevelEnabled` `MakeAssemblyFromSelectedComponents` `MakeIndependent` `MirrorComponents` `RemoveFromFeatureScope` `ReorderComponents` `ReorganizeComponents` `ReplaceComponents2` `ReplacePLMComponents` `RotateComponent` `RotateComponentAxis` `SaveIsolate` `SelectComponentsBySize` `SelectiveOpen` `SetComponentState` `SetComponentSuppression` `SetComponentTransparent` `SetComponentVisibility` `SetDroppedFileConfigName` `SetDroppedFileFeatureName` `SetDroppedFileName` `SetIsolateVisibility` `SetSpeedPakConfigurations` `SetSpeedPakToParent` `TemporaryFixGroup` `TemporaryFixGroupExit` `TranslateComponent` `UnfixComponent` `UngroupComponents` `UpdateBox` `UpdateFeatureScope` `UpdateSpeedPak` `UpdateToolboxComponent` `UseSpeedPak` `ViewFeatureManagerByDependencies` `ViewFeatureManagerByFeatures`
    —— 这 88 个成员的 **②③④⑤** 在本文件 = **查不到（本轮未逐条抄）**；① 的签名见 §7 的 Obsolete 行（其中部分）与本轮批量清单（其余）。

---

**本文件是抄录，不是建议。** 所有「查不到」都指**本机这三套离线源在本轮检索下未命中**，不代表官方 API 里一定没有该成员。
