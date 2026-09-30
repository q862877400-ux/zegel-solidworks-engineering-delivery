# A9 求解步：七次真机尝试的完整记录（2026-10-01）

**结论先行**：**网格已跑通（8,000→7,219 个单元，1 秒）；求解仍卡在材料赋值。**
真因在第八次尝试时由官方 **VB6 类型库 CHM** 定性（见 §二之补）。

---

## 一、确证事实（每条都有真机证据，可重跑）

| # | 事实 | 证据 |
|---|---|---|
| 1 | **零件确实是 100×60×20 mm** | `GetBodyBox` 返回 `X[-0.05,0.05] Y[-0.03,0.03] Z[-0.02,0]`（API 单位=米）⇒ 0.1×0.06×0.02 m |
| 2 | **文档长度单位 = `swUnitsLinear = 0`** | `GetUserPreferenceIntegerValue(46)` |
| 3 | **`CreateMesh(0, 0, 0)` → 返回码 5** | `swsStudyErrorSpecifyPositiveValue` ⇒ **尺寸/容差必须为正** |
| 4 | **`CreateMesh(0, 0.2467, 4.9339)` → 返回码 0（Succeeded）** | 但产出 **19,539,399 单元 / 26,717,520 节点**，耗时 **222–230 秒** |
| 5 | **`CreateMesh()`（零参）→ 失败** | `DISP_E_PARAMNOTOPTIONAL`（「非选择性的参数」）⇒ 三个参数**都必需** |
| 6 | **网格设置的真宿主是 `ICWMesh`，不是 `ICWStudy`** | `study.Mesh` 可读 `MesherType`/`AutomaticTransition`/`ElementSize`/`Tolerance`/`ElementCount`/`NodeCount`；在 **study 上**访问这些属性一律 `<unknown>.xxx` |
| 7 | **默认值** | `MesherType=2`（`swsMesherTypeAlternateCB` = 文档说的 Blended curvature-based）· `AutomaticTransition=False`（**默认就是关的**）· `ElementSize=0` · `Tolerance=0` · `Quality=1` · `AutomaticLooping=False` |
| 8 | **`GetDefaultElementSizeAndTolerance(0, &size, &tol)` 对本零件返回 size≈4.9339 / tol≈0.2467** | 传第 1 参 `0` = `swsUnitSI` |
| 9 | **`MeshAndRun()` 返回 None**（且耗时 0 秒） | 与 `RunAnalysis` 同现象 |
| 10 | **`RunAnalysis()` 返回 19** | `swsRunAnalysisErrorMaterialNotDefined` —— 但本脚本**已赋材料**（`SetFavLibraryMaterialToSelectedEntities` 返回 0）⇒ 该 19 与材料赋值**并存**，需进一步区分 |

**枚举真源**：`D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt`
```
swsMesherType_e:  Standard=0  Alternate=1  AlternateCB=2
swsMeshType_e:    Solid=0  MidSurface=1  Surfaces=2  Mixed=3  Beam=4
swsUnit_e:        SI=0  English=1  Metric=2
swsStudyMeshError_e:  Succeeded=0  ...  SpecifyPositiveValue=5  ...
swsRunAnalysisError_e: Successful=0  ...  MaterialNotDefined=19  ...
```

---

## 二、⚠ **未解的核心问题**：`size` 的真实量纲/语义

**反推**：19,539,399 个单元 ⇒ 单元体积 = 1.2e5 mm³ ÷ 1.954e7 = **0.00614 mm³** ⇒ 边长 **≈0.183 mm**。

**传入值是 4.9339** ⇒ 实际单元比传入值小 **≈27 倍**。

**三个候选单位都解释不了这个 27 倍**：
| 假设 | 期望单元数 | 实得 | 结论 |
|---|---|---|---|
| size 是毫米（4.93 mm） | ≈1000 | 19.5M | ✗ 差 19,500 倍 |
| size 是米（4.93 m） | ≈0（比零件大） | 19.5M | ✗ 方向相反 |
| size 是微米 | 海量 | 19.5M | 量级不符 |

**⇒ 未解。** 可能的方向（**均未验证，不当作结论**）：
1. `CreateMesh` 的第 1 参不是 meshType 而是别的（如 mesherType 或 quality）
2. `size` 与 `tolerance` 的**位置**与我假设的相反
3. 曲面/混合网格被误启用（`MeshType` 读到 0 = Solid，但研究默认可能不同）
4. `GetDefaultElementSizeAndTolerance` 的返回单位与 `CreateMesh` 的入参单位**不是同一个**

**⇒ 下一轮该做的（**不是再试参数**）**：找 `CreateMesh` 的**官方参数名**。
`cworksapi.chm`（2790 页）里没有该方法的独立页；用户手册里 `CreateMesh` 命中都在
网格 PropertyManager 的**界面**说明里。**可能要去 `C:\swapi` 查，或从 VB6 CHM
（`cworksapivb6.chm`，1.8 MB）取参数名。**

---

## 三、七次尝试的时间线（每次都换了**假设**，不是换参数）

| # | 假设 | 做法 | 结果 |
|---|---|---|---|
| 1 | 网格太细 | `CreateMesh(0, 0.00025, 0.005)`（自以为是 5 mm） | 网格器 3000+ s CPU 未完成 |
| 2 | 更粗就好 | `CreateMesh(0, 0.00075, 0.015)`（15 mm） | 内存涨到 **25 GB** |
| 3 | 拓扑研究的问题 | 换**静力学**研究，`(0, 0.0005, 0.004)` | 20 GB / 1170 s |
| 4 | 显式参数的问题 | **零参** `CreateMesh()` | ✗ 参数必需 |
| 5 | **查文档**（此前一直没读用户手册，解包 2052 页） | 得知默认 BCB、`Global Size` 只对 Standard 有效、`Automatic transition` 会炸单元 | 假设更新 |
| 6 | 在 study 上设 mesher/transition | ✗ **属性不在 study 上** | 查反射 ⇒ 宿主是 `ICWMesh` |
| 7 | 在 `study.Mesh` 上设，用**官方建议值** | `CreateMesh(0, 0.2467, 4.9339)` → 返回 0，但 **19.5M 单元** | **单位/语义疑点** |

**⚠ 第 5 步是本轮唯一的方法论收获**：前 4 次都是「换参数」，按纪律**两次失败就该停下查文档** ——
我第 5 次才做。**代价是前 4 次浪费的时间。**

---

## 四、对 capabilities 的影响（**等级不动**）

`topology_optimization` **维持 `stitched`**。本记录不改变结论，只把「为什么未验」写清楚。

## 五、副作用（已清理）

- 每次尝试都以 `Stop-Process` 停掉 `cwbcbfmesh` 并确认内存回落（最后一次 40.7 GB 可用）
- 所有脚本都**不保存**文档（`CloseDoc` 前未 `SaveAs`）
- 新增探针脚本 7 个，都在 `D:\AI\SW\`（工作区，非代码副本）

---

## 二之补 · **第八次尝试：问题解决**（2026-10-01）

### 转折点：解包 **VB6 版 API CHM**

`lang\english\api\cworksapivb6.chm`（**1.8 MB / 3000 页**）——
与之前读的两种源都不同，它**每个方法一页，含参数名**：

```
CosmosWorksLib~CWStudy~CreateMesh.html
  Public Function CreateMesh( _
      ByVal NUnits As Long, _          ' ← 第 1 参 = 单位（swsUnit_e）
      ByVal DElementSize As Double, _  ' ← 第 2 参 = 单元尺寸
      ByVal DTolerance As Double _     ' ← 第 3 参 = 容差
  ) As Long
```

**⇒ 第 1 参不是网格类型；后两参的单位是【毫米】。**
**⇒ 而前七次（含本仓库既有代码）都按 `(meshType, tolerance, size)` 传 ⇒ 后两参颠倒。**

### 真机裁定（100×60×20 mm 板，SW 2026 SP4.1）

| 调用 | 返回 | 单元数 | 用时 |
|---|---|---|---|
| `CreateMesh(0, 4.9339, 0.2467)` | 0 (Succeeded) | **7,219** ✓ | **1 秒** |
| `CreateMesh(0, 0.2467, 4.9339)` | 0 (Succeeded) | **19,509,593** ✗ | 233 秒 |
| `CreateMesh(2, 0.0049339, 0.0002467)` | 抛异常 | — | — |
| `CreateMesh(0, 0, 0)` | **5** (`SpecifyPositiveValue`) | — | — |

**反推闭合**：单元体积 = 1.2e5 mm³ ÷ 1.95e7 = **0.00614 mm³** ⇒ 边长 **0.183 mm**，
与「`DElementSize` 被当成 0.2467」同量级 ⇒ **完全吻合**。
**⇒ 前四次「网格器涨到 20–25 GB、烧 1000–3000 秒」的全部现象由此解释。**

### 顺带解决的第二件事：`ICWMesh` 与 `ICWStudy` 的分工

| 接口 | 有什么 | 怎么拿 |
|---|---|---|
| **`ICWStudy`** | **`CreateMesh`** / `MeshAndRun` / `RunAnalysis` / `get_Results` / `get_Mesh` | `study` 本身 |
| **`ICWMesh`** | `ElementSize` / `Tolerance` / `Unit` / `ElementCount` / `NodeCount` / `MesherType` / `AutomaticTransition` / `GetDefaultElementSizeAndTolerance` | **`study.Mesh`** |

**⇒ 设置用 `study.Mesh`，执行用 `study.CreateMesh(...)`。** 在 study 上访问前者一律 `<unknown>.xxx`。

### 一条方法论教训（比结论更值钱）

前面多次「后台线程跑 COM + 主线程守护」的探针全部报
`AttributeError: <unknown>.CreateMesh`。根因**不是参数** —— 那是
`dynamic.py` 的 `__getattr__`（**属性查找**）失败，因为 **COM 是 STA + 线程亲和**，
跨线程访问 COM 对象成员查不到。
**⇒ 正确设计：COM 调用留在主线程，守护放旁路线程（只读内存、超阈值杀进程）。**
这几轮的 `<unknown>.CreateMesh` 全是这个原因，与 `CreateMesh` 本身无关。

### 仍未解决（下一步）

`RunAnalysis` 返回 **19**（`swsRunAnalysisErrorMaterialNotDefined`），
而材料赋值（`SetFavLibraryMaterialToSelectedEntities`）返回 0。
材料入口已在反射里找到：`ICWSolidBody.SetLibraryMaterial(String, String)` /
`get_MaterialName()` / `set_MaterialName(String)` —— **下一轮从「选实体」这个环节查**
（现在的选法是 `_select_by_id(ext, "", "SOLIDBODY", …)`，实体名传空串可能没选中）。
---

## 二之再补 · 第九次尝试：材料赋值（**仍未通，但卡点精确定位**）

### 网格已确认修好
```
CreateMesh(0, 4.9339, 0.2467) → 0，**7,310 个单元**，**耗时 0–1 秒**   ✓
（对比修之前：19,509,593 个单元 / 233 秒）
```

### 卡点：材料**从未赋上**（不是 19 的误报）
```
零件级材料（改之前）:  model.MaterialIdName = ''      ← 空
零件级材料（改之后）:  model.MaterialIdName = ''      ← 仍空
```

| 尝试的路径 | 返回 | 是否真的生效 |
|---|---|---|
| `SolidManager.SetFavLibraryMaterialToSelectedEntities(lib, mat)`（选中后再赋） | **0** | ✗ `MaterialIdName` 仍为 `''` |
| `SolidManager.SetFavLibraryMaterialToAllBodiesByCompName(lib, mat, "")` | **1** | ✗ 仍为 `''` |
| `Extension.SetMaterialPropertyName2(...)` | ✗ **成员不存在** | — |
| `SolidManager.GetSolidBodyAt(0)` | ✗ **成员不存在** | — |
| `SolidManager.SolidBodyCount` | ✗ 读不到（迟到绑定） | — |

**⇒ 得到 0 或 1 都**不代表生效** —— 与 AGENTS.md 已知事实 8
（`AddSelectionListObject` 的 bool 返回值不可信，须回读计数）同类：
**这里的返回值同样不可信，判据必须是回读 `MaterialIdName`。**

### 下一轮该做的（已定位到入口）
反射与 VB6 CHM 都指明：**材料该设在「零件」上，不在研究上**。
```
IPartDoc.SetMaterialPropertyName2(String, String, String)   ← ★ 首选（SolidWorks 本体，影响零件）
ICWSolidBody.SetLibraryMaterial(String SLibWithPathName, String SMaterialName)
ICWSolidManager.GetSolidBodyByName(String, Int32&) / GetSolidBodyAt(Int32, Int32&)
```
⚠ `ICWSolidManager` 的这些成员**在迟到绑定下读不到**（`<unknown>.SolidBodyCount`）——
本轮未查明是「名字不对」还是「该接口未暴露给 IDispatch」。
**⇒ 下一轮先试 `IPartDoc.SetMaterialPropertyName2`**（它是 SolidWorks 本体接口，
迟到绑定支持良好），并**以 `MaterialIdName` 回读为准**判定。

### 本轮的正面结论
**网格这一段是真跑通了**，且真因（参数顺序 + 毫米单位）有官方 CHM 签名页与真机数据双重支撑。
`RunAnalysis = 19` 现在有了**明确的、可验证的解释**：材料确实是空的。
---

## 二之三 · **第十次尝试：整链跑通**（2026-10-01，里程碑）

### 结果
SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板：

```
材料回读 = 'solidworks materials|AISI 1020|2'          ✓
底面 z=-0.02  SelectByID2=True  选区计数=1             ✓
顶面 z=0      SelectByID2=True  选区计数=1             ✓
夹具 → 对象=True   ·   载荷 → 对象=True                ✓
LoadsAndRestraintsManager.Count = 2                    ✓（两者都进去了）
CreateMesh = 0   单元 7,310   0 秒                     ✓
★★★ RunAnalysis = 0 (Successful)   **用时 1 秒**        ✓
★★★ study.Results 非空 = True                          ✓
     GetPlotCount = '4'
     GetPlotNames = ('品质1','应力1','位移1','应变1')     ← 四个结果图
```

**对比修复前**：`RunAnalysis` 要么卡在 19（MaterialNotDefined），要么网格器涨到 20–25 GB、
烧 3000 秒 CPU。

### 两个真因

**真因 1 · 材料库名是「显示名」，不是 `.sldmat` 文件名**
VB6 类型库 CHM 给出三参数 `(ConfigName, Database, Name)` —— 我的**形式**本来就对，
错在 `Database` 的**值**：

| 库名 | 材料名 | 回读 `MaterialIdName` |
|---|---|---|
| `"SOLIDWORKS Materials"` | `"Plain Carbon Steel"` | `''` ✗ |
| `"SOLIDWORKS Materials"` | `"AISI 1020"` | `'solidworks materials\|AISI 1020\|2'` ✓ |

⇒ **`"Plain Carbon Steel"` 不在该库里**（库里是 `"AISI 1020"` 这类）。
⇒ 我先前照 `.sldmat` **文件名**传小写 `"solidworks materials"` ⇒ 静默失败。
⇒ 另：直接写 `set_MaterialIdName` 只赋**标签**、不加载材料属性 ⇒ 求解仍报 19。**不要走那条路。**

**真因 2 · 选面要用「面上的点」，不是原点**
既有 `_select_by_id(ext, "", "FACE", …)` 走 `SelectByID2("", "FACE", 0, 0, 0, …)`
—— 原点在实体**内部、不在任何面上** ⇒ **一个面都没选中** ⇒ `DispArray` 为空
⇒ Simulation 弹「**未定义载荷或规定的位移**」（用户截图确认）并显示失败。

| 调用 | 选区计数 |
|---|---|
| `SelectByID2("", "FACE", 0, 0, 0, …)` | **0** |
| `SelectByID2("", "FACE", 0, 0, -0.02, …)` | **1** ✓ |

### 第三个「返回码撒谎」
夹具/载荷未定义时 `RunAnalysis` **仍返回 0**，而研究实际失败。
⇒ **判据必须是 `study.Results` 非空 + 图数**，不是返回码。
（前两个：`AddSelectionListObject` 的 bool、`SetFavLibraryMaterial*` 的 0/1。）

### 提炼出的通用纪律（已写进代码注释）
1. **COM 返回值凡不能自证，一律以「回读」为判据**（选区计数、`MaterialIdName`、`Results`）。
2. **单位与量纲必须来自官方签名页**（VB6 CHM），不能靠「看起来合理」。
3. **来源块与 `def` 之间不要插常量** —— `check_provenance` 的 `_extend_to_code`
   会把第一个代码单元当成被说明对象（本轮**第二次**踩，说明这条该单独记）。
---

## 二之四 · **拓扑闭环：定论 —— 被许可证挡住**（2026-10-01）

### 现象
真机跑闭环时 Simulation 弹「**拓扑算例未获许可。**」（用户截图），`study.Results` 为空。

### 依据（双向确认）
1. **弹窗**：「拓扑算例未获许可。」
2. **只读核查许可证注册表** `HKCU:\Software\SolidWorks\Licenses\2026`：
   ```
   DriveWorksXpress / DFMXpress / SimulationXpress / FloXpress
   ```
   —— **全是各家的 Xpress 简化版**，**没有 `SOLIDWORKS Simulation Professional/Premium`**；
   **而拓扑优化是 Professional/Premium 才有的功能**。
3. 拓扑模块的**文件是装了的**（`Simulation\Topology\code\bin\abqsmabas*.dll`、`cwmeshadapt.dll` 等）
   ⇒ **缺的是许可，不是文件**。

### 闭环其实**只差这一步**
`probe_topology_loop.py` 的逐段输出：
```
① 单实体板 100×60×20 mm
② 材料 'solidworks materials|AISI 1020|2'                                    ✓
③ CreateNewStudy3(name, 13, 0, out_i4()) → AnalysisType == 13（入口未走降级）  ✓
④ 目标/约束 {goal:True, mass_constraint:True, mass_constraint_reused:True}     ✓
   （复用了目标自带的质量约束，避开 EndEdit 错误 7）
⑤ 夹具 选区=1 ✓   ⑥ 载荷 选区=1、LoadsAndRestraintsManager.Count = 2          ✓
⑦ CreateMesh = 0，**85,748 个单元**，1 秒                                       ✓
⑧ RunAnalysis = 0，39 秒   ← **第四个「返回码撒谎」**
⑨ study.Results 非空 = False  ✗ ← 因「未获许可」
```

### 处置
按 AGENTS.md **停止条件 3**（「需要用户提供授权或接受缺口 ⇒ 停下报告」）
与 objective 的约束（「不碰只有用户能提供的东西」）⇒ **停下报告，不再硬试**。
`capabilities.yaml` 的 `topology_optimization` 维持 `stitched`，**理由现在可复核**。

### 「返回码撒谎」已累计四处（值得单独成条通用纪律）
| # | 成员 | 它撒谎的方式 |
|---|---|---|
| 1 | `ISelectionMgr.AddSelectionListObject` | 12 次全返回 false，而计数 = 12 |
| 2 | `ICWSolidManager.SetFavLibraryMaterialToSelectedEntities` | 返回 0，材料未变 |
| 3 | `ICWSolidManager.SetFavLibraryMaterialToAllBodiesByCompName` | 返回 1，材料仍未变 |
| 4 | **`ICWStudy.RunAnalysis`** | **夹具/载荷缺失时、以及许可缺失时，都返回 0** |
**⇒ 判据一律改为「回读」**：选区计数 / `MaterialIdName` / `study.Results` 非空 + 图数。