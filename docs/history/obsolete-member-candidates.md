# 「官方已废弃但我方仍在调」的成员 —— 复核台账

> 来源：`tools/probe_obsolete_members.py`（2026-10-01 轮 110，Spec Kit `029`）
> ⚠⚠ **这不是门禁的判据，是人工复核清单** —— 理由见文末「为什么不能做成门禁」。

## 一、怎么产生的
```
1. 抽代码里 `get_com_member(<目标>, "<成员>")` 的**成员名** —— 共 429 个；
2. 去 `C:\swapi\types\**\<成员>.md` 找同名官方文档；
3. 文档正文带 `Obsolete` 的 ⇒ 列出，并把 `Superseded by` 指向谁一起打出来。
⇒ 命中 **38** 个候选。
```

## 〇、⚑ 已处置（2026-10-01 轮 111）
**`sw_sketch.py` 的 6 个 `ISketch` 取法已改用后继**：
```
GetLines         → GetLines2(swCrossHatchFilter_e)   ⚠ 唯一带参的后继
GetArcs          → GetArcs2()
GetEllipses      → GetEllipses3()
GetParabolas     → GetParabolas2()
GetSketchPoints  → GetSketchPoints2()
GetUserPoints    → GetUserPoints2()
```
⚠ **换完仍未在真机上验过**（等级仍是 `stitched`）—— 换的是**入口名**，不是"测过了"。
★ 复跑 `tools/probe_obsolete_members.py`：**这 6 个已不再出现在候选里**。

## 〇之二、⚑ 另两条真候选：**查清了，决定「不换」**（2026-10-01 轮 112）

`029` 查出 8 条真候选，`030` 换掉 6 条。**剩下这 2 条经查证后决定保留旧名** ——
**不是因为懒，是因为后继不是"换个名字"。**

### ① `GetBodies2` → `GetBodies3`
```
旧:  Object GetBodies2(Int32 BodyType)                        1 参
新:  Object GetBodies3(Int32 BodyType, **out Object** BodiesInfo)  2 参（**含 out**）
```
官方还说 `GetBodies3` **支持轻量化零部件**（旧的不支持）—— 所以它**确实更好**。
⚠ **但它的第二个参数是 `out`**。而本机后端（pywin32 迟到绑定）对 `Object&` 类参数
**已有两次失败记录**（**已知事实 47**：`ISketchedBendFeatureData.AccessSelections` /
`SetFixedFace` 在 20+ 种形态下全部失败，且**换 `comtypes` 或进程内 C++ 才可能解决**）。
⇒ **不换**。⚠ **未实测** —— 这是**依据已知事实 47 的判断**，不是本轮跑出来的结论。

### ② `AddMate5` → `CreateMate`
```
旧:  Mate2 AddMate5(Int32, Int32, Boolean, Double×8, Boolean, Boolean, …)   **~18 个位置参数**
新:  Object CreateMate(**Object MateData**)                                  **1 个数据对象**
```
官方：`MateData` 是 `IMateFeatureData` 的**派生接口对象**
（`ICoincidentMateFeatureData` / `IAngleMateFeatureData` / `ICamFollowerMateFeatureData` …）。
⇒ 这**不是换名，是换调用范式**：从"传一串位置参数"变成"先造一个数据对象再传进去"。
⚠ 本仓库**目前没有任何 `IMateFeatureData` 的构造代码** ⇒ 换了要**新写一套**，
且**没有真机验证手段**（建配合会改装配体）。
⇒ **不换**。

### 结论
```
8 条真候选： 6 条**已换**（030）· 2 条**查清后决定不换**（**本轮**，理由如上）
⇒ 台账里这一档**已全部处置完毕**（不再是"待办"）
```
---

## 二、★ 已核实**为真**（我们确实在调官方已废弃的入口）


| 成员 | 官方文档所在接口 | 后继 | 我们在哪用 | 依据 |
|---|---|---|---|---|
| ~~`GetLines`~~ **已改** | `ISketch` | `ISketch::GetLines2` | `sw_sketch.py` | 该模块 docstring 明写「**ISketch 完整封装**」，来源块也引 `ISketch 段` |
| ~~`GetArcs`~~ **已改** | `ISketch` | `ISketch::GetArcs2` | `sw_sketch.py` | 同上 |
| ~~`GetEllipses`~~ **已改** | `ISketch` | `ISketch::GetEllipses3` | `sw_sketch.py` | 同上 |
| ~~`GetParabolas`~~ **已改** | `ISketch` | `ISketch::GetParabolas2` | `sw_sketch.py` | 同上 |
| ~~`GetSketchPoints`~~ **已改** | `ISketch` | `ISketch::GetSketchPoints2` | `sw_sketch.py` | 同上 |
| ~~`GetUserPoints`~~ **已改** | `ISketch` | `ISketch::GetUserPoints2` | `sw_sketch.py` | 同上 |
| `AddMate5` | `IAssemblyDoc` | `IAssemblyDoc::CreateMate` | `sw_assembly_doc.py` | 模块名即 `assembly_doc` |
| `GetBodies2` | `IComponent2` | `IComponent2::GetBodies3` | `sw_assembly.py` / `sw_geometry_selectors.py` / `sw_hole_features.py` / `sw_review.py` | 调用目标是**装配体零部件** |

```
⇒ **8 条确认为真**（其中 **6 条已在轮 111 改用后继**，剩 `AddMate5` 与 `GetBodies2` **未改**）（其中最集中的一簇是 `sw_sketch.py` 的 **6 个 ISketch 取法**）
```

⚠ **它们能不能用，未知**：本台账只证「**官方标了废弃**」，**不证「跑不通」**。
`sw_sketch.py` 有测试、这些取法很可能**当前仍工作**（与已知事实 40 的情形类似：
废弃 ≠ 立刻失效）。**但在未来版本上有被移除的风险。**

## 三、已核实**为假阳性** —— 同名但**不同接口**

| 成员 | 文档在 | 我们实际用的 | 为什么误报 |
|---|---|---|---|
| `Add2` | `ICustomPropertyManager` | **`IEquationMgr.Add2`** | 同名不同接口；`IEquationMgr.Add2` **未**废弃 |
| `Delete` | `ICustomPropertyManager` | **`IEquationMgr.Delete`** | 同上 |
| `GetMassProperties` | `IModelDoc2` | **`IModelDocExtension.GetMassProperties`** | 文档的「后继」正是我们用的那个 |
| `GetRenderMaterials` / `…Count` | `IComponent2` | **`IModelDocExtension.*`** | 同上（`list_render_materials` 实测可跑，见 `012`）|
| `GetModelDoc` | `IComponent2` | 我们也调 `GetModelDoc2` | 后继已在用 |
| `GraphicsRedraw` / `GraphicsRedraw2` | `IModelDoc2` | 两个都调了 | 互为后继，**无法据此判** |
| `Name` | `IComponent2` | 我们也调 `Name2` | 后继已在用 |
| `ResumeSelectionList` | `ISelectionMgr` | 我们也调 `ResumeSelectionList2` | 后继已在用 |
| `Scale` | `IFaceHatch` | 我们也调 `Scale2` | 后继已在用 |
| `MaterialIdName` | `IModelDoc2` | 我们也调 `SetMaterialPropertyName2` | 后继已在用 |

```
⇒ **10 条已核实为假阳性**（同名不同接口 / 后继已在用）
```

## 四、已逐条核完（原「未逐条核」的 20 条 —— 2026-10-01 轮 113）

判法：把**官方文档所在接口**与**我方调用点的目标表达式**并排看。
⚠ 同一个成员常出现在**多个接口**下，只有**其中一部分**标了废弃 ——
**光看成员名判不出**，必须看我们调的是哪个接口。

### ⚠ 已核实**为真**（8 条：我们用的正是那个废弃接口）

| 成员 | 官方废弃接口 | 我方调用点（目标） | 后继 |
|---|---|---|---|
| `AutoDimension2` | `ISketch` | `sw_part.py` `active`（活动草图）| `ISketchManager::FullyDefineSketch` |
| `ExcludeFromBOM` | `IComponent2` | `sw_delivery.py` `component` | `GetExcludeFromBOM2` / `SetExcludeFromBOM2` |
| `GetDependencies2` | `IModelDoc2` | `sw_delivery.py` `model` | `IModelDocExtension::GetDependencies` |
| `GetErrorCode` | `IFeature` | `sw_sheet_metal.py` ×2 · `sw_weldment.py` `feature` | `IFeature::GetErrorCode2` |
| ★ `MoldUndercutDetect` | `IFeatureManager` | `sw_mold.py` `fm` | ★ `IFeatureManager::MoldUndercutDetect2` |
| `ReferenceType` | `IMateEntity2` | `sw_assembly.py` `mate_entity` | `IMate2Entity::Reference2` |
| `SystemValue` | `IDimension` | `sw_document_data.py` `dimension` | `IDimension::GetSystemValue3` |
| `AdvancedGraphics` | `IMaterialVisualPropertiesData` | `sw_render_material.py` `data` | （未写后继）|

### ★★ 其中一条是**活的**：`MoldUndercutDetect` 已被我包成 MCP 工具
```
2026-10-01 轮 98（Spec Kit 018）把 sw_mold.mold_undercut_detect 暴露为
  solidworks_mold_undercut_detect
而它调的 IFeatureManager.MoldUndercutDetect 官方已标 Obsolete、后继是 MoldUndercutDetect2
⇒ **我们发了一个包着废弃入口的工具**
```
⚠ **本台账只证「官方标了废弃」**，**不证它跑不通**（轮 98 的冒烟里它**确实没报错**）。
⇒ 已在 `mcp-server/tool_specs_batch9.py` 的 doc 里加了警示（**不擅自改实现** ——
换 `MoldUndercutDetect2` 要先比形状，那是另一轮的事）。

### ✅ 已核实**为假阳性**（10 条：我们用的那个接口**没**废弃）

| 成员 | 废弃的接口 | **我们实际用的接口** |
|---|---|---|
| `GetComponents` | `IBomTableAnnotation` | **`IAssemblyDoc`**（未废弃）|
| `GetEdges` | `ISketchText` | **`IFace2`**（未废弃）|
| `GetNext` | `IAnnotation` / `IDisplayDimension` | **`IView`**（未废弃）|
| `GetPolylines` | `IView` | **`ISketch`**（未废弃）|
| `GetSplines` | `ISketchBlockDefinition` / `IView` | **`ISketch`**（未废弃）|
| `GetType` | `ICustomPropertyManager` / `IDisplayDimension` | **`IModelDoc2`**（未废弃）|
| `GetUserPreferenceToggle` | `IModelDoc2` | **`ISldWorks`**（未废弃）|
| `SetUserPreferenceToggle` | `IModelDoc2` | **`ISldWorks`**（未废弃）|
| `IsSuppressed` | `IFeature` | **`IComponent2`**（未废弃）|
| `KFactor` | `IBendsFeatureData` / `IOneBendFeatureData` | ⚠ **未查到调用点的目标类型** ⇒ 记「未定性」|

## 四之二、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）

`032` 核出台账里还有 7 条真候选**未处置**。本轮照 `030`/`031` 的做法**先比形状**，
结论是**换不了**（**没有一条是"换个名字"**）：

| 旧（我们在用） | 官方后继 | 形状差别 | 判定 |
|---|---|---|---|
| `AutoDimension2(Int32×5)` | `ISketchManager::FullyDefineSketch(Boolean×2, Int32, Boolean, Int32, Object, Int32, Object, Int32, Int32)` | **换了对象**（`ISketch`→`ISketchManager`）且 **10 参** | **不换** |
| `GetErrorCode()` **0 参** | `IFeature::GetErrorCode2(**Boolean&**)` | 带 **BYREF out** ⇒ **已知事实 47** 的风险面 | **不换** |
| `ExcludeFromBOM`（**属性**）| `IComponent2::GetExcludeFromBOM2(Int32, Object)` | **属性→方法**，且多两个参数 | **不换** |
| `GetDependencies2(Boolean×3)` | `IModelDocExtension::GetDependencies(Int32, Int32)` | 参数**个数与类型都变**，且**换了对象** | **不换** |
| `SystemValue`（**属性**）| `IDimension::GetSystemValue3(Int32, Object)` | **属性→方法**，且多两个参数 | **不换** |
| `ReferenceType` | `IMate2Entity::Reference2` | ⚠ **出厂反射里查不到这个成员** | **不换**（无从比形状）|
| `AdvancedGraphics` | （官方**未写后继**）| — | **不换** |

★ **与 `030` 的对比**：`030` 换 6 条，是因为那几个后继是**零参直接可换**；
这 7 条**没有一条**是那个形状。
⇒ **判据不是"官方让不让你换"，是"换了之后调用形态还对不对得上"。**

⚠ **两条查不到后继**（`Reference2` / `AdvancedGraphics` 无后继）：
* `ReferenceType` 的后继是 md 里写的 `IMate2Entity::Reference2`，**出厂反射里没有这个名字**
  ⇒ 按**铁律 5**记「**查不到**」，**不猜**；
* `AdvancedGraphics` 官方**明说未写后继**。

## 四之三、**台账总账（全部处置完毕）**
```
                    条数   处置
真候选                8   6 已换（030）· 2 查清不换（031）
                         · 1 加警示（032，MoldUndercutDetect）
                         —— 注：上面 6+2 与这 1 条有交集，按"条目"去重后共 8
本轮的 7 条            7   **全部查清后不换**（形状全对不上）
假阳性               18   同名不同接口
未定性                1   KFactor
------------------------------------------------------------
⇒ **台账里再无"未处置 / 未逐条核"的条目。**
```

⚠ **它们仍是官方 `Obsolete`** ⇒ 是**已知的、有据可查的技术债**，不是"没问题了"。
## 五、⚠⚠ 为什么**不能**做成门禁
```
38 条候选里：
  · 已核实为真   8 条
  · 已核实假阳性 10 条
  · 未逐条核     20 条
⇒ **假阳性率 ≥ 26%**（10/38），且**剩余大半里还会有一批**
```
★ 这与本项目**反复出现的同一个教训**一致：
**按名字做的自动检查，假阳性太多，不能当判据。**
⇒ 所以本台账**只出清单，不拦发布**。

⚠ 真正的困难是**同名不同接口**：`GetMassProperties` 在 `IModelDoc2` 上废弃、
在 `IModelDocExtension` 上**没废弃**；光有成员名**判不出**我们调的是哪个。
（这与已知事实 36「同名接口分属不同族」是同一类问题。）

## 六、未查证
* 这 8 条**能不能跑** —— 未测（本台账只管「官方标了废弃」）；
* 剩余 **20 条未逐条核**；
* 探针只扫 `get_com_member(...)` 这一种调用形态；**其它调用形态未扫**。
---

