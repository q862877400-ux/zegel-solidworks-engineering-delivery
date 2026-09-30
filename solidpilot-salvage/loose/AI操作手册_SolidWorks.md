# AI 操作手册 · SolidWorks 执行层（2026-09-27 实测固化）

> **这份文档是给 AI 读的，不是给人读的。**
> 组织原则：**按任务查表，不按发现顺序读**。每条都是"症状 → 原因 → 确切做法"。
> 所有结论都有实测数字支撑；没有实测的推断一律标注 `⚠推断`。
> 人类可读的长版在 `AI建模操作手册.md`；本文件是**操作层速查**，两者不重复叙述。

---

## 0. 三十秒决策树：现在该做什么

| 你要做的 | 直接跳到 | 前置条件 |
|---|---|---|
| 启动环境 | §1 | 无 |
| 往装配体里插零件 | §3.1 | 无 |
| 爆炸图 / 旋转动画 | §4 | 无 |
| 导出 AVI | §4.3（**本机不可用**） | 无 |
| 造标准件（螺母/螺钉/垫圈/型材/螺纹） | §5 | 无 |
| 拓扑优化 | §6 | **HKCU 注册项必须存在**（§1.3） |
| 查 SolidWorks 官方 API 签名 | §2.1 | 无 |
| 调用报错了 | §7 | 无 |
| 判断某个调用能不能用 | §8 硬边界表 | 无 |

---

## 1. 环境

### 1.1 启动（⚠ 顺序不可反）

```
① 编译执行层（有代码改动时）→ $env:TEMP\swprobe\build.ps1
② 启动 SolidWorks → Invoke-CimMethod Win32_Process Create
③ 等 comAttached
```

**为什么必须先编译再启 SW**：执行服务一重启，SW 侧的 Simulation add-in 就会失联
（`GetAddInObject` 返 null、`LoadAddIn` 返 -1）。**顺序反了拓扑工具就废**。

```powershell
# ② 必须用 WMI，不能用 Start-Process
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = '"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"' }
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = '"C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\bin\Debug\SolidworksExecution.exe"' }

# ③ 用 /health 的 comAttached 判断就绪，不要用 MainWindowTitle
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy
Invoke-RestMethod "http://localhost:5000/health" -TimeoutSec 20
# 期望：status=UP, comAttached=True
```

### 1.2 三条环境铁律

| 铁律 | 内容 | 违反后果 |
|---|---|---|
| **WMI 派发** | 启 SW / 执行服务一律用 `Invoke-CimMethod` | `Start-Process` 派生的进程在宿主 kill-on-close Job object 内，**DSH 宿主一重启就被一起带走**（本项目已因此白跑 3 次） |
| **标题不可信** | `MainWindowTitle` 长期为空是常态，COM 早已挂上 | 白等 190 秒 |
| **代理绕过** | `[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy` | 所有 localhost 调用 502/连不上 |

### 1.3 Simulation add-in 注册（拓扑功能的前提）

```powershell
New-ItemProperty -Path 'HKCU:\Software\SolidWorks\AddinsStartup' `
                 -Name 'SldWorks.Simulation.19' -Value 1 -PropertyType DWord -Force
# 回滚 = 删掉这个值（会同时让 topology_optimize 完全不可用）
```

**为什么必须**：`ISldWorks.LoadAddIn("...\Simulation\cosworks.dll")` 恒返
`swUnknownError(-1)`，`GetAddInObject` 恒 `null`。因为 Simulation **不是 `.sldaddon`**
（整个安装树无任何 `.sldaddon`；`HKLM\SOFTWARE\SolidWorks\AddInsStartup` 里原本只有
SOLIDWORKS Inspection），而是独立 COM InProcServer32，**必须加载进 SLDWORKS.exe 进程内**。

| 项 | 值 |
|---|---|
| CLSID | `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}` |
| DLL | `...\SOLIDWORKS\Simulation\cosworks.dll` |
| ProgID | `SldWorks.Simulation.19`（无版本：`SldWorks.Simulation`） |
| 官方示例用的 id | **`CosmosWorks.CosmosWorks`**（也能用） |
| ThreadingModel | `Apartment` |

### 1.4 楔死后的恢复

四个调用会**永久**阻塞服务线程（§8 表）：`CreateMesh` / `RunAnalysis` / `MeshAndRun` /
`AddRestraint` / `IModelDoc2.SelectAt`。

```powershell
Get-Process SolidworksExecution, SLDWORKS | Stop-Process -Force
Start-Sleep -Seconds 8
# 若有 0MB 僵尸 SLDWORKS 单独清掉，否则新实例卡在 splash 不加载
# 再用 WMI 派发两者 → 24~40s 后 comAttached 恢复
```
**恢复后模型状态完好**：`analyze_model(mass_properties)` 与基线一致（主轴壳体 220823 mm³）。

### 1.5 长时调用的正确测法

完整跑一遍可能超过 REST 客户端超时，客户端拿不到响应会**误判成失败/卡死**：

```powershell
# 短超时 fire-and-forget 发出，再轮询服务端是否完成
$sv0 = (Invoke-RestMethod "http://localhost:5000/api/tool/state").stateVersion
# ... 用 8s 超时 POST /api/tool/execute ...
while (((Invoke-RestMethod "http://localhost:5000/api/tool/state").stateVersion) -le $sv0) { Start-Sleep 5 }
```
⚠ **这招对"真阻塞"无效**——`stateVersion` 纹丝不动才是楔死的判据。

---

## 2. 查 API 真相

### 2.1 官方文档（最优先）

本机 `help.solidworks.com` / `my.solidworks.com` **直连 403**，用 Jina Reader 绕过：

```powershell
(Invoke-WebRequest "https://r.jina.ai/https://help.solidworks.com/2019/English/api/swsimulationapi/Create_Topology_Study_Example_VB.htm" -UseBasicParsing).Content
```

**官方 VBA 示例是最快的答案来源**。`Create Topology Study Example (VBA)` 一页就给出了
`GetAddInObject`、`CreateNewStudy3`、`GetStudy(1)`、`Array(GetSelectedObject6)`、
`SetMassPreference`/`SetValue`/`GetMassConstraint` 全部正确写法。
**我曾在本机反射里绕了 6 圈，这一页全有。**（Exa MCP 免费额度已耗尽返 429，
用内置 `web_search` 找链接 + Jina 读正文。）

本机还有 **29,650 页**官方文档全文检索：`C:\Users\Zegel\solidpilot-mcp\swdoc.ps1`

### 2.2 反射 interop

```powershell
$dll = "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.<name>.dll"
$a = [System.Reflection.Assembly]::LoadFrom($dll)
$a.GetType('SolidWorks.Interop.<ns>.<Iface>').GetMembers()
```

`cosworks`（拓扑/仿真）有 **615 个导出类型**；`swmotionstudy`（Motion）有
`api\swmotionstudyapi.chm`；`sldworks` 主体。**枚举值一律以反射为准**，网上抄的经常错。

---

## 3. 建模操作

### 3.1 插入零件（`insert_standard_part` / `insert_component`）

| 事实 | 值 |
|---|---|
| `AddComponent5` 的配置选项 | **必须 `0`**（`swAddComponentConfigOptions_CurrentSelectedConfig`） |
| 传 `2` 会怎样 | `NewConfigWithAsmStructure`——"新建带装配结构的新配置"。空装配体必失败；有配置时成败**取决于当前配置状态** ⇒ 表现为**间歇性 null** |
| x/y/z 的含义 | **零件【中心】**，不是原点（官方原文 "X coordinate of the component center"） |
| 要不要预加载 | **不要**。手册旧版"三步顺序缺一步就挂"已被实测推翻 |

```vb
' 直接插入即可（修复后 15/15 成功）
insert_standard_part file=<path> origin_x=<x> origin_y=<y> origin_z=<z> center_offset_x=<dx> ...
```

### 3.2 headless 选面（可用）

```csharp
// 面：SelectByID2 按"光标下是什么"命中，面有面积所以能命中
var on = face.GetClosestPointOn(px, py, pz) as double[];   // 投影一点到面上，保证落在面上
bool ok = modelDoc.Extension.SelectByID2("", "FACE", on[0], on[1], on[2], false, 0, null, 0);
// 必须校验选中的是面
int t = selMgr.GetSelectedObjectType2(1);   // 2 = swSelFACES
```

⚠ `IFace2.GetBox()` 返回 `object`(SafeArray)，要 `as double[]` 才能索引。
⚠ 包围盒中心只对**平面**落在面上，所以用 `GetClosestPointOn` 而不是包围盒中心。
⚠ `ILoop2.Select` 会选中**边**（`swSelEDGES=1`）而非面——**静默选错类型**。

`swSelectType_e`：`0` None / `1` Edges / `2` Faces / `3` Vertices / `4` DatumPlanes / `5` DatumAxes

### 3.3 headless 选实体（可用）

```csharp
// AddSelectionListObject 对 SOLIDBODY 选不中，要用 SelectByID2 + 实体名
var bn = (body as IBody2).Name;
modelDoc.Extension.SelectByID2(bn, "SOLIDBODY", 0, 0, 0, false, 0, null, 0);
```

### 3.4 `ISelectionMgr` 的两个坑

1. **`DeSelect` 的索引参数是 `Object` 不是 `int`**。传 int 封送失败，异常若被空 catch 吞掉
   ⇒ **选择从未被清空**，材料步骤残留的实体混进面数组（表现：count 比预期多 1）。
   写法：`selMgr.DeSelect((object)si)`，索引从 `GetSelectedObjectCount()` 递减到 **1**。
2. 只有两个 Add 方法：`AddSelectionListObject(单个, selData)`、`AddSelectionListObjects(数组, selData)`。
   对**面**无效，对**顶点**也无效（见 §8）。

### 3.5 ⚠ interop 的"空壳接口"陷阱（通用，影响所有对象）

SolidWorks interop 里存在**同名的空壳接口**：`Xxx` 与 `IXxx` 都存在、都 `IsInterface=True`，
但**其中一个声明 0 个方法**。转错就静默得到一个什么都没有的对象，
表现为"方法调用没反应"或"属性读出来是 null"——**不报错，所以极难发现**。

```powershell
# 用这个判断一个接口是不是空壳
$t = [Reflection.Assembly]::LoadFrom($dll).GetType('SolidWorks.Interop.sldworks.IVertex')
$t.GetMethods().Count     # 18  ← 真的
$t2 = ...GetType('SolidWorks.Interop.sldworks.Vertex')
$t2.GetMethods().Count    # 0   ← 空壳
```

**已确认的空壳/实壳配对**：`IVertex`(18 方法) ↔ `Vertex`(0)、
`ICWTopologyStudyManager`(实) ↔ `CWTopologyStudyManager`(coclass)、
`IMotionStudy`(实) ↔ `MotionStudy`。

**规矩**：从 `object` 转型时，**永远转 `I` 开头的那个**，并对每个新类型先验一次
`GetMethods().Count`，为 0 就说明转错了。

---

## 4. Motion（运动仿真）

### 4.1 入口与签名（**本机官方 CHM 核对，勿凭记忆**）

```
modelDoc.Extension.GetMotionStudyManager()          → IMotionStudyManager
  CreateMotionStudy()                                → IMotionStudy   ← 【零参数】
  GetMotionStudy(name) / ActivateMotionStudy(name) / GetMotionStudyCount() / DeleteMotionStudy(name)
IMotionStudy
  Name (get/set)          ← 零参建完再改名
  SetDuration(sec) / GetDuration()                    ← 没有 Duration 属性
  CreateByExplode(delExisting, duration, startTime)
  CreateByCollapse(delExisting, duration, startTime)
  CreateByRotateModel(delExisting, axis, rotationCount, direction, duration, startTime)
  Calculate() / SaveToAVI(fileName, parameter)
IMotionStudyManager.CreateAVIParameter()             → IAVIParameter
```

枚举：`swAnimatorAxisOfRotation_e` X=0/Y=1/Z=2；`swAnimatorDirectionOfRotation_e` CW=0/CCW=1

### 4.2 旧的四处签名错误（已修，勿再犯）

| 旧代码 | 正确 | 症状 |
|---|---|---|
| `CreateMotionStudy(name)` | `CreateMotionStudy()` + `study.Name = name` | 找不到重载 → 抛 COM 异常 |
| `explode` 调 `CreateByCollapse` | `CreateByExplode` | 语义反了（折叠而非爆炸） |
| `CreateByRotateModel(9 个 double)` | 6 参 `(bool,int,int,int,double,double)` | 参数数与类型全错 |
| `study.Duration = x` | `study.SetDuration(x)` | 属性不存在，try-catch 静默吞掉 |

另外：`explode` **单次调用**即可，不要在 `steps` 循环里反复定义路径。

### 4.3 AVI 导出：❌ 本机不可用（但诊断已做对）

```csharp
aviParam.SaveEntireAnimation = true;   // 不设则 StartTime/EndTime 都为 0，一帧都不写
aviParam.OutputType = 1;               // swAnimationOutputType_e: AVI=1,BMP=2,TGA=3,PNG=4,JPG=5,TIF=6,MP4=7,MKV=8,FLV=9,LXO=10
                                        // ⚠ 该枚举【没有 0】，而 OutputType 是裸 Int32，默认 0 本身非法
aviParam.RendererType = 0;             // swRendererType_Solidworks_Screen
aviParam.FramePerSecond = 30;
bool saved = study.SaveToAVI(path, aviParam);   // ← 必须抓返回值
```

**实测结果**：参数全设对、`ActivateMotionStudy → True`、`Calculate → True`，
但 `SaveToAVI` **返回 `False` 且不产生文件** ⇒ **SolidWorks 渲染侧在本机不可用**，
不是调用方式错误。工具已改为如实回报 `save_to_avi_returned` / `file_on_disk` / `bytes`，
**不再无条件记成功**（静默假成功是这类 API 最常见的陷阱）。

---

## 5. 标准件生成（bd-warehouse）

**已验证可用**，许可 Apache-2.0。装在 `adapters\claude\.venv`（build123d 0.13.0 + bd-warehouse 0.3.0）。

```python
from bd_warehouse.fastener import HexNut, PlainWasher, SocketHeadCapScrew
HexNut(size="M12-1.75")                        # ← 螺母/螺钉要带螺距
PlainWasher(size="M12", fastener_type="iso7089")   # ← 垫圈【不】带螺距
SocketHeadCapScrew(size="M12-1.75", length=40)
```

**双内核交叉验证已通过**（同一 STEP 被 OCCT 与 SolidWorks 分别算体积）：

| 件 | build123d | SolidWorks | 偏差 |
|---|---|---|---|
| 六角螺母 M12 ISO4032 | 1803.1 mm³ | 1803.1 | 0.002% |
| 平垫圈 M12 ISO7089 | 863.1 mm³ | 863.1 | 0.003% |
| 内六角螺钉 M12×40 ISO4762 | 5824.8 mm³ | 5824.8 | 0.001% |

包络尺寸：螺母 20.783/18.000/10.800（对边 18 = 20.783/1.1547 六边形比）、
垫圈 24.000/24.000/2.700、螺钉 18.270/18.270/52.000（头高 12 + 长 40）。
⚠ 尺寸应与**库自己的 CSV 参数表**核对（`bd_warehouse/data/*.csv`），别拿记忆当标尺。

**嘉立创/LCSC 对机械件价值≈0**（实测：ball bearing 5/5 无 3D、linear guide 无此类目、
standoff 4/4 无模型、M3 screw 搜出全是二极管），且端点是无 SLA 的未公开内部接口、
模型不可再分发。仅"PCB + 外壳一体装配"场景值得做。

---

## 6. 拓扑优化

### 6.1 已跑通的完整链路

```
LoadAddIn(cosworks.dll)                      → 0
GetAddInObject("CosmosWorks.CosmosWorks")    → __ComObject
ICwAddincallback.CosmosWorks                 → ICosmosWorks (version=891107)
ICosmosWorks.ActiveDoc                       → ICWModelDoc
ICWModelDoc.StudyManager
  .CreateNewStudy3(name, 13, 0, out err)     → study    [13 = Topology_Static]
  .GetStudy(idx)                             → ICWStudy [idx 是 1-based!]
ICWStudy.TopologyStudyManager                → ICWTopologyStudyManager
ICWStudy.TopologyStudyOptions                → ICWTopologyStudyOptions
```

### 6.2 建约束的**唯一**正确顺序（顺序错全部返错码）

```csharp
topo.BeginEdit();                       // ← ICWTopologyStudyManager 自带 BeginEdit/EndEdit，
                                        //   与各对象自己的三段式是两回事
topo.CreateGoal(2);                     // 2 = MinimizeMass（必须先有 goal）
topo.CreateThicknessControl(out err);
topo.CreatePreservedRegionControl(out err);
topo.CreateMassConstraint(out err);
topo.CreateDisplacementConstraint(out err);
topo.EndEdit();                         // ← 到这里才算提交
```

| 错码 | 含义 | 根因 |
|---|---|---|
| `err=17` | `swsTopoErrCode_SetOperationNotSupported` | **不在 `BeginEdit/EndEdit` 会话内**（或没先 `CreateGoal`） |
| `err=13/14/15` | `OnlyOneThickness/Demold/SymmetryControlCanBeDefined` | **取到了旧的 study**（`GetStudy` 1-based + 同名 study 删不干净）⇒ **每次用唯一 study 名** |
| `err=2` | 同名冲突 | `CreateNewStudy3` 同名 ⇒ 也用唯一名 |
| `err=3/4/5/6` | `NoGoalHasBeenSet` 等 | 先 `CreateGoal` |

### 6.3 各对象的正确写法（照官方示例）

```csharp
// 质量约束：先 SetMassPreference 再设【整数百分数】，最后回取校验
mc.BeginEdit(); mc.SetName("MCP_target_mass");
mc.SetMassPreference(1); mc.SetValue(50);      // 50 = 50%，不是 0.5
mc.EndEdit();
topo.GetMassConstraint("MCP_target_mass", out err);   // 期望 err=0

// 位移约束（绕开夹具的路线）
dc.BeginEdit();
dc.SetCoordinateSystemPreference(0);           // Global
dc.SetComponent(3);                            // URES
dc.SetComparator(0);                           // IsLessThan
dc.SetValue(0.05/1000);                        // 单位【米】
dc.EndEdit();
```

枚举：`swsTopologyStudyConstraintComparator_e` 0 IsLessThan/1 IsGreaterThan/2 IsInBetween；
`swsTopologyStudyDisplacementComponentType_e` 0 UX/1 UY/2 UZ/3 URES/4-6 `_ABS`；
`swsTopologyStudyDisplacementConstraintLocationOption_e` 0 Auto/1 UserDefine

⚠ **`SetLocationPreference(Auto=0)` 不等于"求解器自动选点"**——它让约束**没有位置**，
求解器直接忽略整个 study。必须 `SetVertices(顶点数组)`。

### 6.4 材料

```csharp
// 必须先选中实体（AddSelectionListObject 对实体无效，用 SelectByID2 + 实体名）
selMgr.AddSelectionListObjects?  // ❌ 无效
modelDoc.Extension.SelectByID2(bodyName, "SOLIDBODY", 0,0,0, false, 0, null, 0);   // ✅
study.SolidManager.SetLibraryMaterialToSelectedEntities("solidworks materials", "AISI 1020");  // → 0 OK
```

`ICWModelDoc` 上**没有** Solid 成员，`SolidManager` 在 `ICWStudy` 上。
`ICWForce` 没有 `SetForceValue`，是
`ForceBeginEdit() → set_Unit → SetForceComponentValues(B1,B2,B3,D1,D2,D3) → EndEdit()`。

### 6.5 失败定位：先看网格，再看约束

`MeshAndRun()` 返回 `void` 且"正常返回"**说明不了任何事**。要自己问 study：

```csharp
bool hasMesh = (study.Mesh != null);   // CWMesh 无导出成员，只能判 null
```

| `mesh_present` | `Results` | 结论 |
|---|---|---|
| `false` | `null` | 网格问题 |
| `true` | `null` | **约束问题** |
| `true` | 有值 | 成功 |

**本机实测：`MeshType=0, mesh=PRESENT`，`Results=null`** ⇒ 网格早已建出，
缺的是**求解器可用的约束**。

`swsRunAnalysisError_e` 实测出现：`19` MaterialNotDefined、`22` AuthorizationFailed、`23` MeshNotFound。
`swsTopologyStudyError_e`：`2` 重名、`3` NoGoal、`13/14/15` OnlyOne、`17` SetOperationNotSupported。

---

## 7. 错误 → 原因速查

| 症状 | 真实原因 | 做法 |
|---|---|---|
| `ArgumentException: 未能将调用的参数 1 转换为 Xxx` | **参数 1 若是 Int32 就永不可能"无法转换"** ⇒ 这是 .NET COM 封送层的**通用兜底消息**，不代表真实原因 | 别按参数类型排查；先确认传入的 Dispatch 对象类型对不对 |
| `NO_ACTIVE_DOCUMENT` | `_solidWorks` 是服务启动时缓存的 RCW，SW 重启后失效 | 用 `SafeActiveDoc()`（从 ROT 重新获取）——**新写工具一律用它** |
| `/health` 无响应 + SW CPU 恒定 | 同步 COM 调用弹模态框 | 枚举 SW 顶层窗口找 `vis=True` 的 `#32770`；恢复见 §1.4 |
| `tool loop detected` | 同一命令重复提交 | 换措辞或合并步骤 |
| 本地 REST 502/连不上 | 走了系统代理 | 设 `DefaultWebProxy = New-Object System.Net.WebProxy` |
| `NullReferenceException` 在不需要 SW 的工具里 | 进程没开就碰 `_solidWorks` | 用 `SafeActiveDoc()` |
| 客户端超时 ≠ 失败 | REST 客户端超时 | 见 §1.5 的轮询法 |
| `csc FAILED` 但没看到错误 | 输出被过滤 | 单独跑 build.ps1 并 `Select-String 'error CS'` |

---

## 8. 硬边界（已穷尽，**不要重试**）

| 调用 | 结论 | 证据 |
|---|---|---|
| `ICWLoadsAndRestraintsManager.AddRestraint` / `AddForce` | ❌ 本机不可用 | **11 种调用形态**全被拒：`dynamic`/早绑定/显式 IDispatch × 传面或传实体 × `object[]`/`System.Array`/SafeArray/`IFace2[]` × `null`/`Type.Missing`/`DBNull` × 保留或丢弃返回值。`RefGeom=null` 在封送层失败且**挂死服务**；`Missing`/`DBNull` 到达 cosworks 内部仍失败 |
| `IModelDoc2.SelectAt(Flags, X, Y, Z)` | ⛔ **永久阻塞** | 无图形窗口时**不返回 false 而是不返回**：/health >5min 无响应、SW 内存掉到 140MB、CPU 恒定 |
| headless 选**顶点** | ❌ 本机不可用 | 见下方专条 |
| headless 选**面** | ✅ 可用 | `SelectByID2("", "FACE", GetClosestPointOn 投影点)` + 校验 `swSelFACES=2` |
| AVI 导出 | ❌ 渲染侧不可用 | 参数全对、`ActivateMotionStudy`/`Calculate` 都 `True`，`SaveToAVI` 仍返 `False` |
| `PowerShell` 做 COM | ❌ 做不到 | pwsh 7 移除了 `-ComObject`/`GetActiveObject`；PS 5.1 虽能连但 late-bound 返 `0x8002802B`，`[ISldWorks]$com` 转型抛 `InvalidCastException` ⇒ **只能写在 C# 执行层** |
| `add_drawing_view` | ❌ `VIEW_CREATION_FAILED` | SW2026 中文版已知问题，出工程图目前走不通 |
| 嘉立创 3D 库 | ⚠ 机械件价值≈0 | 见 §5 |

### 8.1 顶点选择为什么不行（根因，不是"没试对方法"）

顶层理由：**`SelectByID2` 是"光标下是什么"的命中测试**。
面有**面积**，用 `IFace2.GetClosestPointOn` 投影一个点上去就必然命中；
**顶点是零维的**，要求探针点与它**精确重合**，浮点坐标做不到 ⇒ 永远返回 `false`。

已排除的三条路（都不是方法选错）：

| 尝试 | 结果 |
|---|---|
| `ISelectionMgr.AddSelectionListObject(vertex, SelectData)` | 返回 false |
| `Extension.SelectByID2("", "VERTEX", x, y, z)` | 返回 false |
| 绕开命中测试：取**活顶点对象**再选<br>`IEdge.GetStartVertex()` → `IVertex` → `AddSelectionListObject` | **扫遍所有边，产出的顶点坐标列表为空** |

⚠ **两个 interop 类型陷阱**（都实测踩过）：
1. `IEdge.GetStartVertex()` 的返回类型是 `object`，**必须转 `IVertex` 而不是 `Vertex`**。
   两者都是接口，但 **`Vertex` 是空标记接口（`GetMethods()` → 0）**，
   `IVertex` 才有那 18 个成员（含 `GetPoint()`）。转错类型会静默得到空壳。
2. ⚠ **纯回转体零件可能根本没有顶点**：主轴壳体 Ø80×110 是
   2 平面 + 2 圆柱面 / 4 条闭合圆边，这种几何的 `GetStartVertex()/GetEndVertex()` 全返回空。
   ⇒ **对回转类零件，别指望顶点路径；用面 + 夹具。**

⇒ **结论：面能 headless 选中、顶点不能。要在无 UI 条件下给拓扑研究加约束，
只能用夹具（`AddRestraint`，本机被拒）。**

---

## 9. 验证纪律（每条都是本项目真实教训）

1. **不验证 = 没做完**。每个特征后 `analyze_model(mass_properties)`，体积对不上就当场停。
   有效实例：碟簧 `3.14523e-6` vs 理论 `3.1452e-6`。
   反例：把"理论值"自己算错（分段求和当并集），差点误判好零件为坏零件。
2. **抓返回值，不要相信"没抛异常"**。`SaveToAVI` / `AddDefaultOptimizationStudyPlot` 都是
   返回成功却什么都没做。
3. **用 `GetSelectedObjectType2` 校验选中的实体类型**。`Select()` 返回 `true` 不代表选对了
   （`ILoop2.Select` 选的是边）。
4. **改代码 → 重编 → 【重启 SW】→ 再测**。顺序反了拓扑必然失败。
5. **变体扫描里"会挂死的变体"必须排除或放最后**——一次挂死就废掉整轮实测。
6. **修法失败三次就停下质疑架构假设**，别继续猜参数类型。

---

## 10. 关键路径速查

| 内容 | 路径 |
|---|---|
| 执行层源码 | `C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\` |
| 新增工具（拓扑/Motion/标准件/BOM/LCSC） | 同上 `Services\SolidWorksService.Capability.cs` |
| 工具注册 | 同上 `Controllers\ToolController.cs` |
| 人类可读长版手册 | `C:\Users\Zegel\solidpilot-mcp\AI建模操作手册.md`（798 行） |
| 新会话提示词 | `D:\AI\SW\AI Solidworks\手册\新会话提示词_SolidWorks改造.md` |
| 官方文档全文检索（29,650 页） | `C:\Users\Zegel\solidpilot-mcp\swdoc.ps1` |
| Motion 官方 CHM（已解包 223 文件） | `C:\swmapi\` |
| 项目产物 | `D:\AI\SW\AI Solidworks\`（模型/设计/手册/截图） |
| 编译+启动一体化脚本 | `$env:TEMP\swprobe\build.ps1` |
| 直连 REST 助手 | `$env:TEMP\swprobe\call.ps1` |
| 源码+exe 备份 | `C:\Users\Zegel\solidpilot-mcp\_backup_20260927-132009\` |
