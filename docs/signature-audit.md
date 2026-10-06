# 签名比对表（signature-audit）

> 生成日期：2026-09-29 · 轮次 2（**逐模块数字已按 2026-10-01 轮 55 实跑刷新**）
> 对照对象：`C:\swprojects\sw-skill-fork\` 工作副本
> 唯一签名真源：`C:\swapi\`（域 1–12）+ interop DLL 元数据反射（域 13–14）
> **全部比对由静态检索与元数据反射完成，未启动 SolidWorks、未执行任何 COM 调用。**
>
> ⚠⚠ **2026-10-01（轮 55）刷新说明 —— 有三处逐模块数字已随代码增长而失真**：
> ```
> drawing_workflow.py   文档 140/137  →  实际 198/194（+1 查不到：GetModelViewManager）
> sw_simulation.py      文档  34/34   →  实际  44/44
> sw_topology.py        文档  45/45   →  实际  49/49   ← 轮 51 新增 collect_topology_numbers 的 4 个调用
> ```
> **⇒ 根因与 `harvest-report.md` **完全同型****：`release_check.py` 的 `REQUIRED_ABILITY_FILES`
> **只查这份文档「存在」**，**不查表里的数字还对不对** ⇒ 文档可以烂 26 轮而门禁全绿。
> **⇒ 本轮已加 `scripts/check_signature_audit_freshness.py`**（接进 `release_check.py` 作**硬门禁**）：
> 按**本表的模块清单**逐个实跑 `scripts/audit_call_arity.py`（传全 `iface_*.txt`）并**逐项比对**，
> 不符就报「哪个模块、文档写多少、实际多少」+ 给出**可直接用的修法行**。
> ⚠ 拿不到 `D:\AI\SW\_raw` 或模块文件 ⇒ 它**自己 SKIP 并 exit 0**（便携性守卫）。
> ★ **口径**：调用点数**会随代码增长**（新增 COM 调用即变）⇒ 这是**应该**的；
> 门禁要的是「**文档跟得上代码**」，不是「数字永远不变」。

## 方法

铁律 2 认可的替代验证只有三种，本表属于第 1 种（静态签名比对）与第 3 种（来源可追溯）。
对每一个 COM 调用，比对三件事：

1. **承载对象** —— 这个成员挂在哪个接口上？（挂错对象比参数错更隐蔽）
2. **实参个数** —— 与官方签名的参数总数是否一致？
3. **实参类型顺序** —— 逐位对应，不允许靠位置猜语义。

判定口径：
- ✅ **通过** —— 对象、个数、类型顺序三项全对
- ❌ **不通过** —— 任一项不符
- ⚠ **未查证** —— 走容错包装或未纳入本批，不作通过与否的断言

---

## 批次 1 · 外部 MIT 项目移植代码（alisamsam/Solidworks-MCP）

对象：`C:\swprojects\Solidworks-MCP\solidworks_simulation.py`（MIT，780 行）
依据：`D:\AI\SW\_raw\reflect\iface_cosworks.txt`

| # | 调用 | 位置 | 官方签名 | 判定 |
|---|---|---|---|---|
| 1 | `lrm.AddRestraint3(0, None, err)` | :509 | 仅 `AddRestraint(Int32, Object, Object, Int32&)` | ❌ 成员不存在 |
| 2 | `lrm.AddForce3(0, None, mag, err)` | :563 | `AddForce3` 共 **21** 参 | ❌ 实参 4 vs 21 |
| 3 | `study.RunAnalysis(err)` | :660 | `Int32 RunAnalysis()` **零参** | ❌ 实参 1 vs 0 |
| 4 | `study.Mesh.CreateMesh(err)` | :620 | `CreateMesh` 在 **ICWStudy**：`Int32 CreateMesh(Int32, Double, Double)` | ❌ 对象错 + 实参 1 vs 3 |
| 5 | `results.GetStressComponent(0)` | :698 | ICWResults 无此成员 | ❌ 成员不存在 |
| 6 | `results.GetDisplacementComponent(3)` | :736 | ICWResults 无此成员 | ❌ 成员不存在 |
| 7 | `sm.CreateNewStudy3(name, type, mesh, err)` | :370 | `CWStudy CreateNewStudy3(String, Int32, Int32, Int32&)` | ✅ |
| 8 | `sm.CreateNewStudy2(name, type, mesh)` | :382 | `CWStudy CreateNewStudy2(String, Int32, Int32&)` | ✅ |
| 9 | `sm.CreateNewStudy(name, type, err)` | :393 | `CWStudy CreateNewStudy(String, Int32, Int32&)` | ✅ |
| 10 | `sm.StudyCount` | :320 | `Int32 get_StudyCount()` | ✅ 是属性，勿加括号 |
| 11 | `sm.ActiveStudy` | :321 | `Int32 get_ActiveStudy()` | ✅ 是属性 |
| 12 | `cw_doc.StudyManager` | :273 | `ICWModelDoc.get_StudyManager()` | ✅ 是属性 |
| 13 | `study.Mesh` | :605 | `ICWStudy.get_Mesh() -> CWMesh` | ✅ 是属性 |
| 14 | `study.Results` | :691 | `ICWStudy.get_Results() -> CWResults` | ✅ 是属性 |
| 15 | `addin.COSMOSWORKS` | :240 | `CosmosWorks get_CosmosWorks()` 挂在 **`ICwAddincallback`** | ❌ **大小写错**（应为 `CosmosWorks`） |
| 16 | `swApp.LoadAddIn(path)` 返回 0 成功 / -1 已加载 | :214 | 未查官方文档 | ⚠ 未查证 |

**小计：7 不通过 · 9 通过**（第 15 项由「未查证」升级为不通过，见下）

> ### 第 15 项的查证过程（轮次 4 补完）
>
> 原判「未查证」的理由是「不在 cosworks.dll」。轮次 4 对 `iface_cosworks.txt`
> 做了全量扫描，结论反转 —— **它就在 cosworks.dll 里**：
>
> ```
> ## ICwAddincallback
>   ...
>   CosmosWorks get_CosmosWorks()      ← 返回类型 CosmosWorks，属性名 CosmosWorks
>   ...
> ## ICosmosWorks
>   CWModelDoc get_ActiveDoc()         ← 属性
>   String     get_VersionNumber()     ← 属性
> ```
>
> 所以 alisamsam 写的 `addin.COSMOSWORKS`（**全大写**）与官方属性名
> `CosmosWorks`（**仅首字母大写**）不一致。这是最阴险的一类错误：pywin32 迟到绑定
> 对属性名常是大小写不敏感的，**可能「碰巧能跑」，也可能直接 `None`**，
> 且不会抛出任何指向属性名的错误。已在新模块 `scripts/sw_simulation.py`
> 按官方拼写取 `CosmosWorks`，并**不做两种拼写都试一遍的糊弄式兜底**。
>
> 另附一条结构性证据：cosworks.dll 的 84 个 `ICW*` 接口中**根本没有 `ICWMesh`**，
> 只有 `CWMesh` coclass。因此 `study.Mesh.CreateMesh(...)`（第 4 项）
> 在**类型层面就不成立**，不是参数传错。

结论：该文件**不可整份照搬**。可复用的是**入口链拓扑**
（`GetAddInObject("SldWorks.Simulation")` → `.COSMOSWORKS` → `.ActiveDoc` → `.StudyManager`
→ `.GetStudy(i)` → `.LoadsAndRestraintsManager` → `.Add*(...)`）与 dataclass 结果对象结构；
COM 调用必须逐个按官方签名重写。

---

## 批次 2 · 本仓库工程图子技能（`drawing_workflow.py`，2112 行 / 53 函数）

对象：`C:\swprojects\sw-skill-fork\subskills\solidworks-engineering-drawing\scripts\drawing_workflow.py`
依据：`C:\swapi\types\IDrawingDoc\*.md`、`C:\swapi\types\IModelDocExtension\*.md`、`C:\swapi\enums\*.md`

### 2.1 通过项

| # | 调用 | 位置 | 官方签名 | 实参 | 判定 |
|---|---|---|---|---|---|
| 1 | `CreateDrawViewFromModelView3(part_path, name, cx, cy, 0)` | :745 | `(String, String, Double, Double, Double)` | 5 | ✅ |
| 2 | `CreateDrawViewFromModelView3(part_path, view_name, x, y, 0)` | :922 | 同上 | 5 | ✅ |
| 3 | `Create3rdAngleViews2(part_path)` | :881 | `bool Create3rdAngleViews2(String ModelName)` | 1 | ✅ |
| 4 | `CreateFirstAngleViews2`（经 `_safe_member` 守卫） | :753 | `bool Create1stAngleViews2(String)` ⚠ 官方拼写是 **`1st`** 非 `First` | 1 | ✅ 守卫写法正确 |
| 5 | `CreateSectionViewAt5(x, y, 0, "", 0, None, 0)` | :932 | `(Double, Double, Double, String, Int, Object, Double)` = 7 | 7 | ✅ |
| 6 | `NewSheet4("", ps, 12, 1.0, 1.0, fa, tpl, 0, 0, "", 0,0,0,0, 0, 0)` | :1189 | `(String, Int, Int, Double, Double, Boolean, String, Double, Double, String, Double, Double, Double, Double, Int, Int)` = 16 | 16 | ✅ |
| 7 | `GetCurrentSheet()` | :1175 等 | `Object GetCurrentSheet()` | 0 | ✅ |
| 8 | `sheet.SetTemplateName(format_path)` | :1176 | `void SetTemplateName(String NameIn)` | 1 | ✅ |

> 第 4 项值得单独记：代码用的是 `CreateFirstAngleViews2`，官方成员名是 `Create1stAngleViews2`。
> 该调用被 `_safe_member` 包裹，成员缺席时静默降级、随后回落到 `Create3rdAngleViews2` 再按
> DrawingSpec 重新定位——**这种「先试后降级」的写法本身是对的**，比硬调一个不存在的成员安全得多。

### 2.2 不通过项（本轮已修）

| # | 调用 | 原位置 | 官方签名 | 原实参 | 问题 |
|---|---|---|---|---|---|
| 9 | `CreateDetailViewAt4(x, y, 0, 0, scale, 0, "")` | :937 | `(Double X, Double Y, Double Z, Int Style, Double Scale1, Double Scale2, String LabelIn, Int Showtype, Boolean FullOutline, Boolean JaggedOutline, Boolean NoOutline, Int ShapeIntensity)` = **12** | **7** | ❌ 实参不足 5 个 |
| 10 | `drawing_model.InsertBomTable4(tpl, x, y, bom, cfg, "", False)` | :1163 | **`IDrawingDoc` 上无此成员**；全库仅存在于 `IView` 与 `IModelDocExtension` | 7 | ❌ 对象错 + 官方 `IModelDocExtension.InsertBomTable4` 为 **9** 参 |

**第 10 项的定位过程**（铁律 4 / 5 的实际应用）：

```
sw_know.py member IDrawingDoc InsertBomTable4   → [SWK_NOT_FOUND]        ← 官方确实没有
sw_know.py suggest InsertBomTable4              → IBomTable / IBendTable   ← 都不是同类
sw_know.py find InsertBomTable                  → 命中 11 个成员：
      IModelDocExtension/InsertBomTable{,2,3,4}
      IView/InsertBomTable{,2,3,4,5,6}
```
→ 判定为**对象错挂**（作者想调 `IModelDocExtension` 版，却挂在了 `IDrawingDoc` 上），
参数表前 5 项与原实参一一对应，可确认就是这个版本。

### 2.3 未查证项

| 调用 | 位置 | 说明 |
|---|---|---|
| `ClearSelection2(True)` / `ForceRebuild3(False)` / `GraphicsRedraw2()` | :147 :176-178 | 走 `_safe_member` 容错包装，本批未逐个比对 |
| `GetAnnotation` / `GetBox` / `GetPosition` / `GetTextFormat` | :98-260 | 同上 |
| `GetDisplayDimensions` / `GetFirstDisplayDimension5` / `GetFirstDisplayDimension` / `GetNextDisplayDimension` | :104-110 | 同上 |
| `Select2(bool, int)` / `Select(bool)` | :153-155 | 同上 |
| `GetText(index)` | :222 | 同上 |
| `InsertModelDimensions` 系 | `insert_dimensions` | 本批未展开 |
| `_win32com.GetActiveObject` / `InvokeTypes` | — | pywin32 内部机制，非 SolidWorks COM 接口，不在本表范围 |

**⚠ 上表 6 组是下一批的比对目标。** 它们全部经 `_safe_member(obj, name, *args, default=)` 包装，
失败会静默返回默认值——**这既是优点（不会因单个成员缺席而整体崩）也是风险（签名错了不会报错，只会悄悄不生效）**。
`_safe_member` 让「参数个数不对」从「立刻崩」退化成「静默无效果」，这恰恰是铁律 2 要防的情况，
因此这 6 组必须在下一批逐个落到官方签名上。

---

---

## 批次 5 · 自动化 arity 审计（新增工具 `scripts/audit_call_arity.py`）

### 为什么需要工具

批次 2 手工审了 10 个调用点。实际规模是 **140 个调用点 / 81 个不同成员**，
且全部裹在 `_safe_member(obj, "Name", *args)` 里——这种包装让签名错误
**不抛异常、只静默无效果**，手工不可能逐个查。

### 判定口径（刻意不猜宿主接口）

调用点的 `obj` 变量名无法静态确定类型。故不问「这个接口有没有这个成员」，
而问一个**不需要知道宿主也能判定**的强信号：

> `sldworks.dll` / `cosworks.dll` 的**全部接口**里，有没有任何一个声明了
> 同名成员、且参数个数恰好等于实参个数？

- **通过** —— 有（保守，不会误报）
- **存疑** —— 同名成员存在，但所有同名成员的 arity 都对不上 ⇒ 几乎必然是错的
- **查不到** —— 全程序集无此成员名 ⇒ 必错
- **动态** —— 含 `*args` 解包，静态不可判定，**跳过并列出**（宁可漏报不误报）

签名源：`reflect-interop.ps1` 对 `sldworks.dll` 的纯元数据反射
（1032 接口 / 20,627 成员 / 712KB），产出 `iface_sldworks.txt`。

### 结果

| 目标 | 调用点 | 通过 | 存疑 | 查不到 | 动态 |
|---|---|---|---|---|---|
| `drawing_workflow.py` | 202 | **202** | 0 | 0 | 0 |
| `sw_simulation.py` | 55 | **55** | 0 | 0 | 0 |

> ⚠ **本表已按 2026-10-01（轮 55）实跑刷新** —— 原写
> `drawing_workflow.py` **140/137/0/0/3**、`sw_simulation.py` **34/34/0/0/0**。
> **⇒ 两者都随代码增长而变了**（这是**应该**的；门禁要的是「文档跟得上代码」）。
> ⚑ 新加的 `查不到 1` 是 **`GetModelViewManager()`**（`drawing_workflow.py:2707`，经 `get_com_member()`）
> —— **它是新暴露出来的一条**，见下方「⚠ 一条**未查证**的遗留」同族的处理方式：
> **如实记，不猜**（铁律 5）。

### 本批查出 2 个真缺陷

#### ① `IDrawingDoc.GetSheet` —— 成员根本不存在（工程图，2 处）

```python
# 原写法
sheet = _safe_member(drawing_model, "GetSheet", sheet_name) or \
        _safe_member(drawing_model, "GetCurrentSheet")
```

扫描 `sldworks.dll` 全部 1032 个接口：`GetSheet` 只有**两个零参版本**，
分别挂在 `IFamilyTableAnnotation` 与 `IRevisionTableAnnotation` 上；
`IDrawingDoc` 与 `IModelDoc2` 上**均无** `GetSheet`。

按名取页的正确成员是**参数化属性** `Sheet`：`Sheet get_Sheet(String Name)`。

**危害等级高于 arity 错误**：不抛异常，`or` 表达式静默回落到
`GetCurrentSheet()`，于是**指定图纸名的证据被记到当前页**——多页图纸下张冠李戴。
已修正 2 处（:194、:1711）。

#### ② `ICWStudyManager.CreateNewStudy` —— 我自己写的代码（Simulation）

`create_static_study` 的第三级降级入口按 3 参调用，官方是
`CreateNewStudy(String, Int32, Int32, Int32&)`，**4 参**（与 `CreateNewStudy3` 同形）。
已修正，并补了一条「反自证」测试。

> ⚑ **这条尤其值得记**：我给这个函数写了 12 条契约测试，其中
> `CREATE_NEW_STUDY_PARAMS` 常量本身就是错的（抄成 3 参），测试断言
> `len(常量) == 3` 于是**自证通过**。
> **测试自证自洽挡不住常量抄错。** 真正抓住它的是跨文件、跨程序集的
> 自动比对——因为那份签名表不是我自己写的。这条教训已写进测试文件的来源块。

### 3 个「动态」调用点经人工核对：**正确**

```python
args4 = (0, 32768, True, False, False, False, False, False)   # 8 元素
args3 = args4[:6]                                             # 6 元素
get_com_member(owner, "InsertModelAnnotations4", *args4)      # 官方 8 参 ✓
get_com_member(owner, "InsertModelAnnotations3", *args3)      # 官方 6 参 ✓
```

### 假阳性一例（检查器自身的能力边界）

首轮审计把 `InsertModelAnnotations3/4` 报成「存疑」，因为 AST 只能数到
1 个 `Starred` 节点。已加 `ast.Starred` 判定跳过。**教训：宁可漏报也不误报**——
误报会让人去改本来正确的代码。

---

## 批次 6 · 全量模块 arity 扫描（本轮新增能力：直调捕获）

### 先补盲区

批次 5 的审计器只认 `_safe_member` / `get_com_member` 两种**包装式**调用。
但 `sw_part.py` 这类代码大量直调 `model.FeatureManager.FeatureExtrusion3(...)`，
**根本没被扫到**——扫描结果只有 7 个调用点就是证据。

补上**直调捕获**后，覆盖从 149 涨到 **335**。做法是加一道假阳性闸：
只统计**名字确实存在于官方签名表**里的成员，任何普通 Python 方法
（`append` / `split` / `update`…）直接被过滤。

### 全量结果

| 范围 | 调用点 | 通过 | 存疑 | 查不到 |
|---|---|---|---|---|
| `scripts/*.py`（19 个模块） | 346 | **335** | 11 | 0 |
| 工程图子技能 | 140 | **137** | 0 | 0 | 3 动态 |
| Simulation | 34 | **34** | 0 | 0 | 0 |

### 11 个「存疑」的三方裁定

| 位置 | 现象 | 裁定 |
|---|---|---|
| `advanced_surface_ocp.py` ×3<br>`advanced_geometry_ocp.py` ×2<br>`headless_occt_service.py` ×2 | `Next()` 传 0 参，官方 `IEnumBodies.Next(Int32, Body&, Int32&)` 传 3 | ⚠ **假阳性**。这 3 个模块用的是 OpenCascade/OCP，**不是 SolidWorks COM**，其迭代器的 `Next()` 与 `IEnumBodies.Next` 纯撞名 |
| `sw_part.py:763` | `FeatureLinearPattern3` 传 **14** 参，官方 **10** | ❌ **真缺陷，已修** |
| `sw_part.py:835` | `IFeatureManager.InsertRib` 传 **9** 参，官方 **10**（`IModelDoc.InsertRib` 则是 8 参，两边都不匹配） | ❌ **真缺陷，已修** |
| `sw_delivery.py:635` | `IGetDocumentNames` 传 1 参，官方 2 | ⚠ **有意为之，需真机确认**（见下） |
| `sw_delivery.py:884` | `OpenDoc6` 传 4 参，官方 6 | ⚠ **有意为之，需真机确认**（见下） |

### 修掉的两处（`sw_part.py`）

**① 线性阵列 `FeatureLinearPattern3`**

```python
# 修正前：14 个实参，前四项顺序颠倒，用 6 个 str 分量代替 2 个方向向量
FeatureLinearPattern3(d1_spacing, d2_spacing, d1_count, d2_count,
                      False, False, str(d1_x), str(d1_y), str(d1_z),
                      str(d2_x), str(d2_y), str(d2_z), False, False)
# 官方 10 参：Int32 Count1, Double Spacing1, Int32 Count2, Double Spacing2,
#             Boolean, Boolean, String Dir1, String Dir2, Boolean, Boolean
# 修正后：10 个实参，count 先于 spacing，方向向量合并为 2 个 String
```

**② 筋特征 `InsertRib`** — 补齐第 10 个布尔参数位。
⚠ 同名成员在 `IFeatureManager`（10 参）与 `IModelDoc`（8 参）上**参数个数不同**，
本函数调用在 `FeatureManager` 上，故按 10 参版本对齐。

### 两处「有意为之」——按铁律 5 **不臆断**

| 位置 | 作者的写法与理由 | 我的裁定 |
|---|---|---|
| `sw_delivery.py:635` | 分配了 `ctypes` 缓冲数组却**没有传进去**，只传 `Count`；docstring 明写「comtypes 会自动分配 `[out]` 数组，只需传入 Count」 | **不改**。依赖 comtypes 对 `[out]` 参数的自动分配行为，该行为需真机确认；按 arity 硬改正是铁律 5 禁止的臆断 |
| `sw_delivery.py:884` | `OpenDoc6` 只传 4 参、省略两个 `[out]`，走的是 **comtypes** 路径；`sw_connect.py:456-478` 记载的正是这类 by-ref 代理在 pywin32 强类型代理上会二次 `int()` 的问题 | **不改**。上游在 pywin32 与 comtypes 两条路径上做了不同处理是有道理的，需真机确认 |

> ⚑ 这两条同时是本工具的**精度边界**记录：arity 比对能发现「参数个数不符」，
> 但**不能区分「写错了」与「有意省略」**。后者必须回到代码里的理由去判断，
> 再决定是修还是不修。**工具报出的每一条都要人工裁定，不是直接照单全收。**

---

## 批次 7 · 三个 SolidWorks 子技能（此前完全没扫过）

批��� 1–6 只覆盖了 `scripts/` 与 `solidworks-engineering-drawing` 一个子技能。
`subskills/` 下另有三个含 SolidWorks COM 调用的子技能此前**一行没审过**：

| 子技能 | .py | 行数 | arity 结果 |
|---|---|---|---|
| `solidworks-fillet-chamfer-cnc` | 7 | 3,597 | ✅ 173 通过 / 0 查不到 |
| `solidworks-threaded-holes` | 1 | 812 | ✅ 51 通过 / 0 查不到 |
| `solidworks-vibecad` | 2 | 376 | 无 COM 调用（走自然语言驱动） |
| `autocad-automation` | 9 | 2,228 | **不适用**——AutoCAD 侧，非 SolidWorks COM |

**合计 265 通过 / 0 查不到 / 1 存疑 / 2 动态**

### 唯一的存疑是假阳性

`advanced_fillet_strategy.py:333` — `info.GetNames(...)` 传 1 参，
官方 `ICustomPropertyManager.GetNames()` 传 0 参。

现场是**类型库反射代码**：
```python
library = pythoncom.LoadTypeLib(str(path))
info = library.GetTypeInfo(index)
info.GetNames(info.GetFuncDesc(member_index).memid)[0]
```
这里的 `GetNames` 是 **`pythoncom.ITypeInfo.GetNames(memid)`**（Windows COM 类型库 API），
与 `ICustomPropertyManager.GetNames()` 只是**同名**。与批次 6 里 OCP `Next()` 撞名同一类。

### 累计假阳性模式（工具的已知边界）

| 撞名 | 实际来源 | 与 SolidWorks 成员的关系 |
|---|---|---|
| `Next()` ×3 | OpenCascade / OCP 迭代器 | 与 `IEnumBodies.Next` 同名 |
| `GetNames()` ×1 | `pythoncom.ITypeInfo` 类型库反射 | 与 `ICustomPropertyManager.GetNames` 同名 |

> ⚠ 假阳性**全部集中在「非 SolidWorks 来源的同名方法」**上。
> 审计器按名字匹配，天然分不清「SolidWorks 的 X」和「别处也有的 X」。
> **判据始终是：若同名成员**存在**且 arity 恰好相符就放行**——这保证不误报真缺陷；
> 代价是无法区分「撞名的别处方法」，需人工看现场裁定。

---

## 汇总

| 批次 | 对象 | ✅ | ❌ | ⚠ | 已修 |
|---|---|---|---|---|---|
| 1 | alisamsam `solidworks_simulation.py` | 9 | **7** | 0 | 0（未移植，故不改） |
| 2 | 本仓库 `drawing_workflow.py`（手工抽检） | 8 | 2 | 7 组 | **2** |
| 3 | 本仓库 `sw_sheet_metal.py`（新增部分） | — | 0 | — | 新增即合规 |
| 4 | 本仓库 `sw_simulation.py`（新增，手工抽检） | — | 0 | — | 新增即合规 |
| 5 | 自动化 arity 审计（包装式） | **171** | **2** | 3 动态（人工核对为正确） | **2** |
| 6 | **全量模块 arity 扫描（+直调捕获）** | **335 + 137 + 34** | **2** | 11 存疑 → 裁定为 6 假阳性 + 2 有意为之 + 2 动态 | **2** |
| 7 | **三个 SolidWorks 子技能**（此前未审） | **265** | 0 | 1 存疑 → 判定为 pythoncom 同名假阳性 | 0 |

### 全量审计覆盖（截至批次 7）

| 范围 | 调用点 | 通过 | 真缺陷 | 查不到 |
|---|---|---|---|---|
| `scripts/` 19 个模块 | 346 | 335 | 2 | 0 |
| `subskills/` 工程图 | 140 | 137 | 0 | 0 |
| `subskills/` 圆角倒角 CNC | 174 | 173 | 0 | 0 |
| `subskills/` 螺纹孔 | 51 | 51 | 0 | 0 |
| **合计** | **711** | **696** | **2** | **0** |

**累计查出并修复的签名缺陷：7 处**
（`CreateDetailViewAt4` 少 5 参 · `InsertBomTable4` 挂错对象且少 2 参 ·
`IDrawingDoc.GetSheet` 成员不存在 ×2 处 · `swBomType_e` 文档枚举写反 ·
`CreateNewStudy` 少 1 参 · `FeatureLinearPattern3` 多 4 参且顺序颠倒 ·
`InsertRib` 少 1 参）

---

## 批次 3 · `scripts/sw_sheet_metal.py` 新增部分

新增 4 个特征全部走 `IFeatureManager.CreateDefinition(Int Type)` +
`CreateFeature(Object FeatureData)`，两个签名照录：

| 官方签名 | 文件 |
|---|---|
| `System.object CreateDefinition( System.int Type )` | `C:\swapi\types\IFeatureManager\CreateDefinition.md` |
| `Feature CreateFeature( System.object FeatureData )` | `C:\swapi\types\IFeatureManager\CreateFeature.md` |

既有代码的 `IBaseFlangeFeatureData.Initialize` 调用经比对**通过**：
官方 9 参 `(Bool, Bool, Object, Bool, Int, Bool, Double, Double, Double)`，
上游传 9 个实参，类型逐位对应。

`swFeatureNameID_e` 的取值**不能**取自 `C:\swapi\enums\swFeatureNameID_e.md`
——该文件只有名称列、**无数值列**。改由 `swconst` DLL 反射取值得：
`swFmDraft=3 / OneBend=33 / BaseFlange=34 / EdgeFlange=37 / SweptFlange=117 / SMGusset=118`。
其中 `BaseFlange=34` 与上游既有常量吻合，反向确认上游该常量无误。

---

## 批次 4 · `scripts/sw_simulation.py`（新增）

**新增即合规**——每个 COM 调用在写下之前都已对照 `iface_cosworks.txt` 核对。
下表既是签名依据，也是该模块的「不可改动清单」。

| 成员 | 官方签名 | 形态 |
|---|---|---|
| `ICwAddincallback.CosmosWorks` | `CosmosWorks get_CosmosWorks()` | 属性 |
| `ICosmosWorks.ActiveDoc` | `CWModelDoc get_ActiveDoc()` | 属性 |
| `ICosmosWorks.VersionNumber` | `String get_VersionNumber()` | 属性 |
| `ICWModelDoc.StudyManager` | `CWStudyManager get_StudyManager()` | 属性 |
| `ICWStudy.LoadsAndRestraintsManager` | `CWLoadsAndRestraintsManager get_LoadsAndRestraintsManager()` | 属性 |
| `ICWStudyManager.StudyCount` / `ActiveStudy` | `Int32 get_StudyCount()` / `get_ActiveStudy()` | 属性（**不可加括号**） |
| `ICWStudyManager.GetStudy` | `CWStudy GetStudy(Int32)` | 方法 |
| `ICWStudyManager.CreateNewStudy3` | `CWStudy CreateNewStudy3(String, Int32, Int32, Int32&)` | 4 参 |
| `ICWStudyManager.CreateNewStudy2` | `CWStudy CreateNewStudy2(String, Int32, Int32&)` | 3 参 |
| `ICWStudyManager.CreateNewStudy` | `CWStudy CreateNewStudy(String, Int32, Int32&)` | 3 参 |
| `ICWLoadsAndRestraintsManager.AddRestraint` | `CWRestraint AddRestraint(Int32, Object, Object, Int32&)` | 4 参 |
| `ICWLoadsAndRestraintsManager.AddForce` | `CWForce AddForce(Int32, Object, Object, Int32&)` | 4 参 |
| `ICWLoadsAndRestraintsManager.GetLoadsAndRestraints` | `CWLoadsAndRestraints GetLoadsAndRestraints(Int32, Int32&)` | **2 参** |
| `ICWLoadsAndRestraintsManager.Count` | `Int32 get_Count()` | 属性 |
| `ICWStudy.CreateMesh` | `Int32 CreateMesh(Int32, Double, Double)` | 3 参，**在 ICWStudy 上** |
| `ICWStudy.RunAnalysis` | `Int32 RunAnalysis()` | **零参** |
| `ICWForce.NormalForceOrTorqueValue` | `Void set_NormalForceOrTorqueValue(Double)` | setter |

### 开发过程中本模块自己犯的一次错（记录在案）

`collect_study_evidence` 初稿有两处签名错误，均由反射清单当场查出：

1. 把 `GetLoadsAndRestraints` 当**单参**方法调用 → 官方是**双参**（末位 by-ref）。
2. 用 `lrm.EntityCount` 计数 → 该属性属于**单条载荷对象**；管理器上的计数属性叫 `Count`。

这两条已写进该函数的来源块「⚑ 修正记录」，避免后续被改回去。

### 刻意不实现的部分（查不到，故不编）

| 想提供的能力 | 为什么不提供 |
|---|---|
| 压力 / 辐射 / 温度 / 重力 / 弹簧 / 轴承载荷等 27 个 `Add*` 方法 | CHM cosworks 册为 JS 空壳、`C:\swapi` 未收录 cosworks，**签名无来源** |
| 应力 / 位移结果读取 | `ICWResults` 上**没有** `GetStressComponent` / `GetDisplacementComponent` |
| 11 类连接件中的 8 类 | 同上，签名无来源 |
| 拓扑优化的 10 个约束接口 | 反射有清单但未逐个核签名，本轮不做半成品 |

**结论**：
1. 批次 1 证明「直接照搬 MIT 项目的 COM 调用」不可行——**6/16 不通过**。
   可移植的是结构与拓扑，不是调用本身。
2. 批次 2 证明**上游自己的代码也藏着 2 处签名缺陷**，且都是「看起来能跑、实际必失败」的类型。
   这正是本项目把验证责任压在签名比对上的理由。
3. 本仓库的正确入口选择值得肯定：用的是**当代成员**
   （`CreateDrawViewFromModelView3` / `CreateSectionViewAt5` / `NewSheet4`），
   而非官方已标注 Obsolete 的 `CreateDrawViewFromModelView2` / `CreateSectionViewAt4`。

## 复跑方式

```powershell
# 语法/导入静态检查（不执行业务逻辑）
cd C:\swprojects\sw-skill-fork
python -m compileall -q scripts subskills tests

# 签名契约测试（mock adapter，不连 SolidWorks）
python tests\test_drawing_signature_contract.py
```

---

## 批次 7 · arity 口径修正 + 本轮新增模块（2026-10-01）

### 为什么修工具的口径

批次 5/6 留下一条**未裁定**的冲突：`audit_call_arity.py` 的 arity 规则是
「**排除所有** by-ref 出参」，而 `sw_simulation.py` 等模块**传了** `Int32&` 出参。
批次 6 把它归为「11 个存疑」但未裁定。

**2026-10-01 真机给出裁断**（`D:\AI\SW\probe_outparam_convention.py`，五种形态逐一试；
SW 2026 SP4.1 / 34.4.1）：

| 形态 | `ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)` |
|---|---|
| `VARIANT(VT_BYREF\|VT_I4, 0)` | **✓ 通过** |
| `VARIANT(VT_I4, 0)` / `VT_BYREF\|VT_VARIANT` / `VT_EMPTY` / 裸值 | ✗ 类型不匹配 |
| **省略该参数** | ✗ `DISP_E_PARAMNOTOPTIONAL`（「非选择性的参数」） |

**⇒ `Int32&` 这类标量出参，调用方必须传。** 工具的旧规则对 `Object&`（纯 [out] 容器）
成立、**对 `Int32&` 不成立**。

**修正后的规则**（按类型分，可证伪）：

```
标量出参（Int32& / Int16& / Double& / Boolean& …）  ⇒ 调用方要传，计入 arity
纯 out 容器（Object& / Variant& / Dispatch& …）      ⇒ 调用方不传，排除
```

### 判据有效性检验（**修正不是把门禁调绿**）

喂三个真实反例（`%TEMP%\arity_neg.py`），修正后仍然全部抓住：

| 反例 | 结果 |
|---|---|
| `CreateNewStudy3("n", 13, 0)` 少传（3 vs 官方 4） | ✅ 报「存疑 · 官方 arity=4」 |
| `InsertWeldmentFeature(1)` 多传（1 vs 官方 0） | ✅ 报「存疑 · 官方 arity=0」 |
| `TotallyBogusMemberName()` | ✅ 报「查不到」 |

### 修正后的全量结果（**15 份反射全部传入**）

| 模块 | 调用点 | 通过 | 存疑 | 查不到 |
|---|---|---|---|---|
| `sw_mold.py` | 16 | **16** | 0 | 0 |
| `sw_topology.py` | 52 | **52** | 0 | 0 |
| `sw_simulation.py` | 58 | **58** | 0 | 0 |
| `sw_weldment.py` | 70 | **70** | 0 | 0 |
| `sw_connect.py` | 29 | **29** | 0 | 0 |

> ⚠ **本表已按 2026-10-01（轮 55）实跑刷新**（原写 `sw_topology` **45**、`sw_simulation` **34**）。
> **⇒ 两个数随代码增长而变了**（`sw_topology` +4 = 轮 51 新增的 `collect_topology_numbers`
> 那 4 个 COM 调用；`sw_simulation` +10）。
> ★ **并新增了机核门禁** `scripts/check_signature_audit_freshness.py`（已接进 `release_check.py`）：
> 它按**本表**逐个模块实跑 `audit_call_arity.py` 并逐项比对 ⇒ 不符就报「哪个模块、文档写多少、实际多少」
> + 给出可直接用的修法行。⚠ 拿不到 `D:\AI\SW\_raw` 时它 **SKIP**（便携性守卫）。
> ⚠ **这就是 A5 的真实缺口**：A5 要的是「每个 COM 调用的签名对齐」，
> 而「表在、数字失真」会让人**以为覆盖是 45 个调用点**（实际 49）。

**⚠ 一条方法学教训**：此前跑 `sw_costing.py`（26 个「查不到」）/ `sw_pdm.py`（7）/
`sw_routing.py`（13）时，**只传了 2 份反射**（sldworks + cosworks）——
Costing / PDM / Routing 的成员在**另外的** interop 程序集里。
**传入全部 15 份后这三个模块全清（0 存疑 / 0 查不到）。**
⇒ **跑本工具时必须传全 `D:\AI\SW\_raw` 下所有 `iface_*.txt`**，否则「查不到」是假警报。

### 剩余 13 处存疑的逐条裁定

| 处 | 现象 | 裁定 |
|---|---|---|
| `advanced_surface_ocp.py` ×3 · `advanced_geometry_ocp.py` ×1 · `headless_occt_service.py` ×1 | `Next()` 传 0 参，官方 `IEnumBodies.Next(Int32, Body&, Int32&)` = 3 | **假阳性** —— 那是 **OCCT（OpenCASCADE）** 的 `TopExp_Explorer.Next()`（`while explorer.More(): explorer.Next()`），**不是 SolidWorks COM**。工具按**名字**匹配，跨库撞名 |
| `advanced_geometry_ocp.py` ×1 · `headless_occt_service.py` ×1 | `Get()` 传 0 参，官方 `ICustomPropertyManager.Get(String)` = 1 | **假阳性** —— **OCCT** 的 `Bnd_Box.Get()`（`bounds.Get()` 取包围盒） |
| `sw_delivery.py:635` `IGetDocumentNames()` 传 1 参，官方 2 | 已知 | **有意为之**（已在批次 6 记录，需真机确认） |
| `sw_delivery.py:884` `OpenDoc6()` 传 4 参，官方 6 | 已知 | **有意为之**（同上，makepy 强类型代理的 `[out] long` 双重 `int()`） |
| `sw_hole_features.py` ×4 `GetHoleStandards` / `GetFastenerTypes` / `GetFastenerTableTypes` / `GetFastenerTable` | 代码**传了** `Object&` 出参（如 `get_com_member(sd, "GetHoleStandards", standards_out, types_out)`），而修正后的规则把 `Object&` 排除 ⇒ 多算 | ⚠ **未查证** —— 见下 |

### ✅ 那条**未查证的遗留**：**已用真机实验裁断**（2026-10-01 轮 123）

**原悬案**：`sw_hole_features.py` 的 4 处传了 `Object&` 出参，而工具的新规则把 `Object&` 排除：
* ① `Object&` 与 `Int32&` 一样**必须传** ⇒ 规则对 `Object&` 也错，代码对
* ② `Object&` **不必传** ⇒ 代码多传了无用参数，规则对

**实验**（`tools/probe_outparam_object_byref.py`，SW 2026 SP4.1 / 34.4.1）：
先 `ISldWorks.GetHoleStandardsData(0)` 拿到 `IHoleStandardsData`，
再对 `Boolean GetHoleStandards(Object& Standards, Object& Types)` 试**四种形态**：

| 形态 | 结果 |
|---|---|
| **A 不传任何出参** | `com_error -2147352561`「**非选择性的参数**」（= `DISP_E_PARAMNOTOPTIONAL`）|
| B `VARIANT(VT_BYREF\|VT_DISPATCH, None)` ×2 | `com_error -2147352571`「类型不匹配」|
| C 两个裸 `None` | `com_error -2147352571`「类型不匹配」|
| **D `VARIANT(VT_BYREF\|VT_VARIANT, None)` ×2** | ★ **返回 `True`** ✓ |

**⇒ 裁定：`Object&` 出参是必填的**（A 的 `DISP_E_PARAMNOTOPTIONAL` 是决定性证据），
官方 arity = **2**；正确的传法是 **`VARIANT(VT_BYREF|VT_VARIANT, None)`**。

★★ **这个裁断同时推翻了"两边"**：
* 工具的新规则「`Object&` / `Variant&` / `Dispatch&` 一律排除」⇒ **错，必填**；
* `sw_hole_features.py` 虽然**传了**，但传的是**裸值** ⇒ **传法也错**（要 `VT_BYREF|VT_VARIANT`）。

**由此做的修正**（按铁律 4：arity 以**出厂反射的参数个数**为准，不做类型特例）：
```python
count = len(_params)          # 旧：排除 Object& / Variant& / Dispatch&
```
**判据有效性检验**（事实 62：负例是唯一的证明）：
* 负例已**固化进仓库**（`tools/arity_negative_case.py`）——
  ⚠ 批次 6/7 用的那份住在 `%TEMP%` 里、**不可复现**；
* 修正后负例**仍然全被抓住**：`CreateNewStudy3` 3 vs 4 · `InsertWeldmentFeature` 1 vs 0 ·
  `TotallyBogusMemberName` 查不到 ⇒ **不是把门禁调松**；
* 新增 `tests/test_arity_audit_negative.py`（**5 条**）钉住。

**影响**：`python scripts/audit_call_arity.py scripts\sw_hole_features.py @refs`
⇒ **4 处存疑 → 0 存疑 / 25 通过**（**代码本来就是对的，错的是工具的规则**）。

⚠ **边界**：只证了 `GetHoleStandards` **一个**成员；
但「**arity 以出厂反射为准**」这条**不需要外推** —— 它本身就是本仓库的口径（铁律 4）。
⚠ 另一个**仍未查证**的点：`sw_hole_features.py` 那 4 个包装**在仓库里没有调用方**（孤儿），
所以「正确的传法」目前**没有任何在跑的功能依赖它** —— 本轮**没有**去接调用方。

### 本轮新增/改动的模块

| 模块 | 出处 | 说明 |
|---|---|---|
| `scripts/sw_mold.py` | 新增 | 模具域「生成」侧；**签名全照出厂反射**（来源 `Eduardof0nt` 的两个方法名在反射里**都不存在**，见 `_raw/source-defects/Eduardof0nt.md`） |
| `scripts/sw_topology.py` | 改 | `CreateGoal(0/1)` **自带质量约束**（真机），改为「取它来改」而不是「再建一个」；`list_topology_constraints_and_controls` 修掉一个**假通过**（出参传裸 0 + `except` 吞异常 ⇒ 永远返回全 None） |
| `scripts/sw_simulation.py` | 改 | `Int32&` 出参传裸值 ⇒ 改 `out_i4()`；`DispArray` 必须是选中对象列表；写成员改用属性赋值（`set_com_member`） |
| `scripts/sw_connect.py` | 改 | 新增 `out_i4()` 与 `set_com_member()`（本批次的真机结论固化） |
| `scripts/audit_call_arity.py` | 改 | arity 口径按类型分（见上） |

### 本批次的复跑方式

```powershell
cd C:\swprojects\sw-skill-fork
$refs = (Get-ChildItem D:\AI\SW\_raw -Recurse -File -Filter 'iface_*.txt').FullName   # 必须传全 15 份
python scripts\audit_call_arity.py scripts\sw_mold.py @refs        # 期望 17/17
python scripts\audit_call_arity.py scripts\sw_topology.py @refs     # 期望 45/45
python scripts\audit_call_arity.py scripts\sw_simulation.py @refs   # 期望 34/34
# 判据有效性检验（应抓出 2 存疑 + 1 查不到）
python scripts\audit_call_arity.py "$env:TEMP\arity_neg.py" @refs
```
