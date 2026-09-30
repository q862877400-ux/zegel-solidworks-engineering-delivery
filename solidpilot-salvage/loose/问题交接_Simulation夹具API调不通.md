# 问题交接文档：SOLIDWORKS Simulation 夹具/载荷 API 在本机调不通

> **这份文档是自包含的。** 拿到它的人不需要看任何前置对话。
> 目标：让另一个 AI（或人）接着把 `ICWLoadsAndRestraintsManager.AddRestraint` 调通。
> 日期：2026-09-27 ｜ 环境：SOLIDWORKS 2026 SP0.0（Premium，盗版安装）
> 状态：**已排除大量可能性，但未定位根因。** 下面全部是实测结论，不是猜测。

---

## 1. 一句话症状

SolidWorks Simulation 的 **夹具/载荷 API**（`ICWLoadsAndRestraintsManager.AddRestraint` 等）
**任何调用形态都抛 `ArgumentException`**，导致拓扑优化/静力学研究建好后无法附加约束，
求解器拿不到可迭代的约束 ⇒ **拿不到解**。

报错文本（中文运行时）：
```
未能将调用的参数 1 转换为 AddRestraint。
```
英文运行时：`Cannot convert argument 1 to AddRestraint.`

⚠ **这个报错文本本身是误导性的**：`参数 1` 是 `NRestraintType`，类型 `Int32`，
**永远不可能"无法转换"**。这是 .NET COM 封送层的**通用兜底消息**，不指示真实原因。
（`AddForce3` 报的是"参数 2"，同样是 `Boolean`/`Int32` 类型。）

---

## 2. 环境（全部实测）

| 项 | 值 |
|---|---|
| 操作系统 | Windows（x64） |
| SolidWorks | 2026 SP0.0 Premium，内核版本号 `34.0.0.5070` |
| interop 程序集 | `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.cosworks.dll`（615 个导出类型） |
| 原始类型库 | `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.tlb`（512 KB） |
| COM 服务器 | `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.dll`（39 MB） |
| TypeLib GUID | `{B5697F4F-C68A-4685-A7B8-478AF05EF605}\13.0\0\win64` → `cosworks.tlb` |
| Simulation CLSID | `{C8F79410-CD71-4995-969A-30AA4841B667}`（注意：请以本机注册表为准） |
| 宿主进程 | 自建的 C# 执行服务（`SolidworksExecution.exe`，.NET Framework，x64），通过 HTTP 暴露工具接口 |
| ⚠ add-in 加载 | **必须**先写注册表，否则 `LoadAddIn` 恒返 `swUnknownError(-1)`、<br>`GetAddInObject` 恒 `null`：<br>`New-ItemProperty -Path 'HKCU:\Software\SolidWorks\AddinsStartup' -Name 'SldWorks.Simulation.19' -Value 1 -PropertyType DWord -Force`<br>**服务一重启 add-in 就会失联 ⇒ 顺序必须是"先重启服务、再重启 SolidWorks"** |

---

## 3. 官方签名（从 help.solidworks.com/2021 页面提取，非猜测）

```vb
' IMotionStudy... 不相关；这里是 cosworks：
Function AddRestraint(ByVal NRestraintType As Integer, _
                      ByVal DispArray As Object, _
                      ByVal RefGeom As Object, _
                      ByRef ErrorCode As Integer) As CWRestraint   ' DispId = 3

Function AddForce(ByVal NForceType As Integer, ByVal DispArray As Object, _
                  ByVal RefGeom As Object, ByRef ErrorCode As Integer) As CWForce

Function AddForce3(ForceType, SelectionType, RefDirType, InterpolationMode, DistPercentageOpt,
                   NumOfRows, DistValue, ForceValue, NonUniformLoading, NULoadingOnBeam,
                   NonUniformLoadDistDef, NonUniformLoadDistType, Ucode, TorqueNFVal, Comps,
                   FlipOrigin, IsCurvedBeam, DispArray, RefGeom, PerUnitLength, ErrorCode)  ' DispId = 23

Function AddPressure(NPressureType, DispArray, RegGeom, ErrorCode)
```

**官方完整示例**（`Analyze Part (VB.NET)`，已抓取到
`D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\Analyze_Part_Example_VBNET.txt`）：

```vb
pointer1 = Part.Extension.GetObjectByPersistReference3(var1, longstatus)
Dim varArray1 As Object() = {pointer1, pointer2}
LBCMgr = Study.LoadsAndRestraintsManager
CWRes1 = LBCMgr.AddRestraint(0, (varArray1), Nothing, errCode)
```

**注意官方只给了 VB 示例，没有任何 C# / C++ / VB.NET 的 AddRestraint 完整示例**（已搜过），
这可能正是 C# 侧调不通的原因。

### 3.1 interop 里的 `MarshalAs` 声明（关键线索，但**已被证伪为根因**）

```
AddRestraint:
  NRestraintType  Int32    (无)
  DispArray       Object   MarshalAs(UnmanagedType.Struct)     ← 声明为"结构"
  RefGeom         Object   MarshalAs(UnmanagedType.IDispatch)
  ErrorCode       Int32&   [out]
AddForce3 的 DispArray（第 18 参）同样 Struct
AddPressure 的 DispArray 同样 Struct
```

⚠ **但 `Struct` 是 cosworks 整个程序集的通用模式**——`ComputerNames` / `StudyNames` /
`VerticesDispArray` / `MultiUniformFactors` 全部也是 `Struct`，是 tlbimp 对 `Object` 参数的
兜底选择。**不能据此断定它是原因。**（见 §5 推翻记录）

---

## 4. 已确凿的边界（**不要重复测试**）

### 4.1 走得通的部分（全部实测成功）

```
ISldWorks.LoadAddIn("...Simulation\cosworks.dll")                 → 0
ISldWorks.GetAddInObject("SldWorks.Simulation.19")               → __ComObject
ICwAddincallback.CosmosWorks (属性)                               → ICosmosWorks, VersionNumber=891107
ICosmosWorks.ActiveDoc (属性)                                     → ICWModelDoc
ICWModelDoc.StudyManager.CreateNewStudy3(name, 13, 0, out err)   → 真实 study，err=0
ICWModelDoc.StudyManager.GetStudy(idx)                            → ICWStudy  ⚠ idx 是 1-based
ICWStudy.TopologyStudyManager / TopologyStudyOptions              → 均有效
  .BeginEdit() / .EndEdit()                                       → OK / 0
  .CreateGoal(2)   // 2 = MinimizeMass                            → 0
  .CreateThicknessControl(out err)                                → err=0
  .CreatePreservedRegionControl(out err)                          → err=0
  .CreateSymmetryControl(out err)                                 → err=0
  .CreateDemoldControl(out err)                                   → err=0
  .CreateMassConstraint(out err)                                  → err=0
  .CreateDisplacementConstraint(out err)                          → err=0
  .GetMassConstraint(name, out err)                               → err=0（往返校验通过）
ICWStudy.SolidManager.SetLibraryMaterialToSelectedEntities(lib, "AISI 1020") → 0
IModelDocExtension.SelectByID2("", "FACE", x, y, z, ...)        → 选中面
ISelectionMgr.GetSelectedObjectType2(1)                            → 2 = swSelFACES
IModelDocExtension.GetPersistReference3(faceObj)                  → 成功
IModelDocExtension.GetObjectByPersistReference3(pid, out err)    → err=0，得到 __ComObject 指针
ICWStudy.CreateMesh(...) / MeshAndRun()                            → 网格建出来：mesh_present=true
```

**同一个 `ICWLoadsAndRestraintsManager` 对象上，不带几何数组的成员也正常**：
```
lrm.Count                                        → 返回 0（不是 -1）✅
lrm.GetLoadsAndRestraints(0, out err)            → err=1，**无异常**✅
   err=1 = swsLoadsAndRestraintsErrorNotFoundAtIndex（因 Count=0，是正确响应）
```

⇒ **接口是通的、类型转换是通的、属性读得到。**

### 4.2 走不通的部分

```
AddRestraint / AddForce / AddForce3 / AddPressure   → 全部抛 ArgumentException ❌
```

---

## 5. 已尝试并**失败**的 12 种调用形态（不要重试）

| # | 尝试 | 结果 |
|---|---|---|
| 1 | `dynamic` 晚绑定 | ArgumentException |
| 2 | 强类型早绑定（`Marshal.GetTypedObjectForIUnknown` → `ICWLoadsAndRestraintsManager`） | 同上 |
| 3 | 显式 IDispatch（`Type.InvokeMember`） | 同上 / 报"目标发生异常" |
| 4 | 传**实体**（SOLIDBODY）而非面 | 同上 |
| 5 | 传面数组的 `object[]` | 同上 |
| 6 | `System.Array` | 同上 |
| 7 | `Array.CreateInstance(typeof(object), n)`（真 SafeArray） | 同上 |
| 8 | `RefGeom` 传 `null` | 同上，且**会挂死服务**（见 §7） |
| 9 | `RefGeom` 传 `Type.Missing` | 同上 |
| 10 | `RefGeom` 传 `DBNull.Value` | 同上 |
| 11 | 丢弃返回值（只取 `out err`） | 同上 |
| 12 | **官方示例逐字复刻**：<br>面 → `GetPersistReference3` → `GetObjectByPersistReference3` → `object[]` → `AddRestraint(0, arr, Type.Missing, out err)` | 同上（**每个要素都对了仍失败**） |

### 5.1 四个被推翻的"根因假设"（避免别人重走）

| 假设 | 怎么被推翻 |
|---|---|
| "`MarshalAs(Struct)` 是根因" | `Struct` 是 cosworks **全程序集统一模式**（`ComputerNames`/`StudyNames` 等同样） |
| "整个接口被封 / 是许可问题" | `lrm.Count` **正常返回 0**；`GetLoadsAndRestraints` **正常返回 err=1**（不抛异常）⇒ 接口与子系统功能正常；<br>且 `swsLoadsAndRestraintsError_InvalidLicense = 7` 这个码**存在却从未出现**（许可问题会返 7，而不是抛 .NET 异常） |
| "研究类型不对"（一直在拓扑研究 type=13 试，官方示例用静力学 type=0） | 改 `study_type=0` 静力学，**同样失败** |
| "CLR 封送层拒绝（错误文本是 CLR 格式）" | ① 把 `cosworks.dll` 移出输出目录（RCW 变 `System.__ComObject`，走纯 IDispatch）**仍失败**；<br>② **临时注销注册表 TypeLib**（让 CLR 拿不到 TLB 封送规则）**仍失败**（已完整回滚注册表） |

### 5.2 也已排除

- **许可问题**（依据见上，`InvalidLicense=7` 未出现）
- **必须由 UI 发起**（子系统对纯 API 调用有正常响应）
- **元素类型**（`GetObjectByPersistReference3` 的返回值、活的对象、实体、vertex 全试过）
- **选面错误**（`GetSelectedObjectType2` 实测 = 2 = `swSelFACES`，选对了）
- ⚠ 顺带修过一个真 bug：选面后紧接 `SelectBodyArray()` 会把选择集覆盖成实体（`selectedObjectType2` 曾是 76），已修

---

## 6. 报错文本的真正含义（重要）

`未能将调用的参数 1 转换为 AddRestraint` 是 **C# runtime binder** 的消息，不是 COM 错误。
它出现在这些场景：
- `dynamic` 调用时，运行时 binder 无法把实参匹配到任何重载
- `Marshal.GetTypedObjectForIUnknown` 得到强类型 RCW 后，CLR 拿 **.NET 签名**（含 `MarshalAs`）做封送
- `Type.InvokeMember` 参数封送失败

⚠ **参数序号可能不含 `out` 参数，也可能以 0-based/1-based 混用** —— 不要被 "参数 1" 带偏去检查第一个 `Int32`。

---

## 7. ⚠ 挂死风险（务必知道）

以下调用是**同步 COM 调用，会永久阻塞宿主线程**：

| 调用 | 现象 |
|---|---|
| `AddRestraint`（`RefGeom` 传 `null`） | `/health` 持续无响应、SW 内存从 1.2 GB 掉到 229 MB、CPU 恒定 |
| `CreateMesh` / `RunAnalysis` / `MeshAndRun` | 弹模态对话框（枚举 SW 顶层窗口可见 `class='#32770' vis=True title=''`） |
| `IModelDoc2.SelectAt(Flags, X, Y, Z)` | 无图形窗口时**不返回**（看似"选不中"，其实是永久阻塞） |

⇒ 现在的实现里 `add_fixture` / `run_solve` 都默认 `false`（opt-in）。
**接手的人做实验时请在独立探针进程里做，不要直接改主服务。**

恢复：`Stop-Process` 执行服务与 SW → 等 6–10 s（若残留 0 MB 僵尸 SW 要单独清）→ 用 WMI 派发重启
（`Invoke-CimMethod -ClassName Win32_Process -MethodName Create`）→ 约 24–40 s 后 `comAttached=true`。

---

## 8. 建议的下一步（按我的判断排序）

### 8.1 ⭐ 手工构造 `DISPPARAMS` 直接 `IDispatch::Invoke`

**这是唯一还有依据的方向。** 理由：官方 VB 示例在 SolidWorks 进程内能跑通，
VB 运行时**不经过 CLR 的封送器**；而 .NET 侧无论怎么调都失败 ⇒ 合理解释是
"CLR/互操作层的封送方式与 cosworks 期望的不一致"。手工构造 DISPPARAMS 可完全绕开它。

**已探明的实现要点与坑**（`C:\Users\Zegel\solidpilot-mcp\tools\rawdispatch.cs` 已写好并编译通过）：

```csharp
// ① 基础件
oleaut32!SafeArrayCreateVector(VT_DISPATCH, 0, n)  →  SAFEARRAY*   ← 用 VT_DISPATCH，不是 VT_UNKNOWN
oleaut32!SafeArrayPutElement(psa, &i, pDispatch)                          ← 元素是 IDispatch*

// ② 关键：元素类型要跟着外层 VARIANT 走
//    官方 VB 示例里 varArray 的元素是 Face2/IDispatch，VB 运行时封成
//    SAFEARRAY(VT_DISPATCH)，外层 VARIANT.vt = VT_ARRAY|VT_DISPATCH = 0x2009
//    （不是 0x200C；元素是 VT_DISPATCH 就该配 0x2009）
//    VARIANT x64 布局：vt 在偏移 0（short），union 在偏移 8
Marshal.WriteInt16(variantPtr, 0, (short)(0x2000 | 0x0009));
Marshal.WriteIntPtr(variantPtr, 8, psa);

// ③ 取真实 IDispatch 指针（不是 IUnknown！cosworks 在 VB 示例里收的是 IDispatch）
IntPtr pUnk = Marshal.GetIUnknownForObject(faceComObject);
Guid iidDispatch = new Guid("00020400-0000-0000-C000-000000000046");
IntPtr pDisp;
Marshal.QueryInterface(pUnk, ref iidDispatch, out pDisp);

// ④ RefGeom 传手工构造的 VT_EMPTY VARIANT（对应 VB 的 Nothing）
//    ⚠ 不要传 CLR null —— CLR 会把 C# null 封成 VT_DISPATCH，而且实测会挂死服务
//    这就是为什么"传 null"是最差的选择

// ⑤ 本机 .NET 运行时【没有】Marshal.GetNativeVariantForObject（实测 MissingMethodException），
//    只能 P/Invoke oleaut32
// ⑥ Marshal.WriteInt16 第三参必须 (short) 强转 ushort

// ⑦ ⚠⚠ 参数打包顺序：按【声明顺序】填，不是逆序！
//    COM 内部会用 rgvarg 反向索引去取参，但【调用方按声明顺序填 rgvarg[0..n]】即可，
//    CLR 自己也是这么做的。按逆序填会变成
//       AddRestraint(ErrorCode, RefGeom, DispArray, NRestraintType)
//    ——症状和现在完全一样，但会把排查方向带偏。
var rgvarg = new IntPtr[4];
rgvarg[0] = <VARIANT: VT_I4, 值 0>            // NRestraintType（swsRestraintTypeFixed = 0）
rgvarg[1] = <VARIANT: 0x2009 + psa>           // DispArray
rgvarg[2] = <VARIANT: VT_EMPTY>               // RefGeom
rgvarg[3] = <VARIANT: VT_I4|VT_BYREF>        // ErrorCode（out int）
```

⚠ **已实测的坑**：用**假指针**测 `SafeArrayPutElement` 会直接
`AccessViolation (0xC0000005)` 崩进程——因为 `VT_DISPATCH`/`VT_UNKNOWN` 元素会被 `AddRef`。
⇒ **必须**在真实 COM 对象上测，不能脱离 COM 单测；填充前先
`GetIUnknownForObject` + `QueryInterface(IID_IDispatch)`。

⚠ 风险：纯原生内存操作，偏移写错即崩溃，且崩溃点可能与出错点无关。

### 8.1.1 建议的验证顺序（细化）

1. **先跑 VBA 宏交叉验证**（最省事、最能定性）：在 SolidWorks 内置 VBA 里跑一个只做
   `AddRestraint` 的最小宏。**若 VBA 通而 C# 不通 ⇒ 100% 坐实是互操作层问题**，
   §8.1 方向正确；若 VBA 也不通 ⇒ 问题在 cosworks 本身或本机许可，另作别论。
2. **再上 DISPPARAMS**（按上面的要点改 `rawdispatch.cs`）。
3. **DISPPARAMS 也失败时，用 C++/CLI `#import "cosworks.tlb"`** 生成原生包装再试一次。
   C++/CLI 完全不经过 `MarshalAs`，是**独立的交叉验证**——通了就 100% 证实是 CLR 封送层。
4. **兜底：读 TLB 原始类型信息** —— `LoadTypeLibEx` + `ITypeInfo::GetFuncDesc` 拿
   `AddRestraint` 的 `FUNCDESC`，查 `DispArray` 参数 `ELEMDESC.tdesc.vt` 与
   `lpadesc` 里数组元素的真实 `vt`，**用它来定死 SAFEARRAY 元素类型**（本轮最关键的未知量）。
   ⚠ 本机 .NET 8 的 `ITypeInfo.GetDocumentation` 没有 6 参重载，自写 C# 解析器会编译失败；
   建议用反射调用，或写一个十几行的 C++ 小工具读 TLB。

### 8.2 其它可能（我未做，价值低于 8.1）

1. **直接用 C++/CLI 或纯 C++ 写一个 .xla 或外部 exe** 调 `cosworks.tlb` ——
   官方生态里 C++ 才是主战场（VB 宏的宿主是 C++）。**如果 8.1 成功，这等于证实了假设。**
2. **读 `cosworks.tlb` 原始类型信息**（`LoadTypeLibEx` + `ITypeInfo`/`VARDESC`），
   看 `DispArray` 的真实 `vartype` 与数组元素类型到底是
   `VT_ARRAY|VT_VARIANT` / `VT_ARRAY|VT_DISPATCH` / `VT_ARRAY|VT_UNKNOWN` / 某个自定义结构。
   ⚠ 本机 .NET 8 的 `System.Runtime.InteropServices.ComTypes.ITypeInfo.GetDocumentation`
   **没有 6 参重载**，自写 TLB 解析器会编译失败——需要用反射或 tk 类工具。
3. **在 SolidWorks 界面里手工建一次 Fixed Geometry 夹具**，然后只用 API 跑网格+求解。
   ——⚠ 我已用判别性实验证明这条**不是必需的**（子系统对纯 API 调用有正常响应），
   但它能作为"API 路径是否真的可行"的最终交叉验证。
4. **换一个 SDK 版本/语言验证**（如用 VBA 宏在同一台机器上跑官方示例）——
   如果 VBA 能跑通而 C# 不行，就 100% 坐实是互操作层问题。

---

## 9. 关键文件位置

> ✅ 下面列的路径**已全部验证存在**（13/13，无死链）。
> ⚠ 脚本类文件已从 `%TEMP%` **复制到项目目录** `C:\Users\Zegel\solidpilot-mcp\tools\`（重启安全）。
> 原始工作副本仍在 `$env:TEMP\swprobe\`。

| 内容 | 路径 |
|---|---|
| 本问题所在的项目 | `C:\Users\Zegel\solidpilot-mcp\` |
| **工具脚本（持久）** | `C:\Users\Zegel\solidpilot-mcp\tools\`（build / call / reflect_cosmos / rawdispatch / dl_docs / grab1） |
| 实现（`TopologyOptimize`） | `execution\solidworks\SolidworksExecution\Services\SolidWorksService.Capability.cs` |
| 工具注册 | `execution\solidworks\SolidworksExecution\Controllers\ToolController.cs`（`case "topology_optimize"`） |
| 编译脚本（一键编译+替换+WMI 重启+健康检查） | `tools\build.ps1` |
| 直连 REST 调用助手 | `tools\call.ps1` |
| interop 反射助手 | `tools\reflect_cosmos.ps1` |
| **已备好的 DISPPARAMS 封装** | `tools\rawdispatch.cs`（编译通过，**未接进服务**） |
| CHM 批量解包脚本 | `tools\dl_docs.ps1` |
| 网页 API 抓取器（避开 Next.js SPA 的正文渲染） | `tools\grab1.ps1` |
| **官方 `Analyze Part` 示例（已抓取）** | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\Analyze_Part_Example_VBNET.txt` |
| 33 个载荷/夹具方法的官方签名表 | `官方文档\Simulation载荷夹具API签名全表.md` |
| 官方拓扑教程（11 篇，含官方流程） | `C:\swdoc\sim_otsimtopology\` |
| 离线 API 文档（16,254 个 md，含官方示例） | `C:\swapi\types\<接口>\<方法>.md` |
| 产品能力手册（本问题背景） | `SOLIDWORKS产品能力手册.md` §4 |

### 9.1 怎么快速复现这个 bug（供接手者确认环境一致）

```powershell
# ① 前置：add-in 注册 + 服务与 SW 都要是 WMI 派发起来的
#    且顺序必须是【先重启服务 → 再重启 SolidWorks】
# ② 打开零件
$dir = "D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt"
. C:\Users\Zegel\solidpilot-mcp\tools\call.ps1
Call 'open_document' @{ file_path = $dir }
# ③ 触发夹具（默认 opt-in，必须显式传 true）
Call 'topology_optimize' @{ action='solve'; material='AISI 1020'; add_fixture=$true }
# 预期：日志里出现
#   probe: Loads&Restraints subsystem = present, Count = 0
#   probe GetLoadsAndRestraints(0) -> err=1 ... SUBSYSTEM FUNCTIONAL
#   AddRestraint: threw ArgumentException: 未能将调用的参数 1 转换为 AddRestraint
# ④ 分析零件确认网格确实建出来了（证明只差约束）
Call 'analyze_model' @{ analysis_type='mass_properties' }   # 期望 volume=0.000220823
```

⚠ **`add_fixture=$true` 有挂死风险**（§7）——`RefGeom` 传 `null` 的那条路径会永久阻塞服务。
建议先在独立探针进程里复现。

---

## 10. 给接手者的三句话

1. **不要再试 C# 侧的参数形态** —— 12 种全试过了，包括官方示例逐字复刻。
2. **不要再猜根因** —— 我猜了 4 次，4 次都被自己的下一步实验推翻；
   唯一站得住的判别实验是"同接口不同参数形态对照"（§4.1 的 `GetLoadsAndRestraints`），
   它证明了"只有传几何数组这条路失败"。
3. **有依据的方向只有一个**：绕开 CLR/互操作层的封送 —— 手工 DISPPARAMS 或改用 C++。
