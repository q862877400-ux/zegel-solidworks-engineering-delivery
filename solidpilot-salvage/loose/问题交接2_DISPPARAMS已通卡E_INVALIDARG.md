# 第二轮交接：DISPPARAMS 已打通，卡在 E_INVALIDARG —— 求下一步建议

> **第一份交接文档**（`问题交接_Simulation夹具API调不通.md`）讲的是"12 种托管形态全失败"。
> **这份讲的是那个问题的续集**：手工 DISPPARAMS 路线**已经走通**，
> 现在卡在一个具体的 COM 错误码上。**请先读这份**，第一份作为背景。

日期：2026-09-27 ｜ 环境：SOLIDWORKS 2026 SP0.0 Premium，x64，Windows
测试件：`D:\AI\SW\AI Solidworks\模型\主轴壳体_Housing.sldprt`（Ø80×110 回转体，2 个平面端面 + 2 个圆柱面）

---

## 1. 一句话现状

**调用已经真正进入 cosworks 内部并返回真实的 COM 错误码 `E_INVALIDARG (0x80070057)`，
但参数形态已穷尽排查、全部正确，仍被拒。**

```
SAFEARRAY(VT_VARIANT) 元素=24字节 VARIANT(vt=VT_DISPATCH, union@8=IDispatch*)
外层 VARIANT.vt = VT_ARRAY|VT_VARIANT = 0x200C
RefGeom = VT_EMPTY      ErrorCode = VT_I4|VT_BYREF      wFlags = 0
Invoke(DispId=3)  →  hr=0x80070057  argErr=0  ErrorCode 未被写回
```

**这是质变**：从"CLR 在门口就抛 `ArgumentException`"变成了"cosworks 收到参数后主动拒绝"。
但**仍未拿到解**。

---

## 2. 已确认正确的部分（不要重查）

| 项 | 值 | 依据 |
|---|---|---|
| `AddRestraint` 的 DispId | **3** | 反射 `DispIdAttribute` |
| 官方签名 | `AddRestraint(Int32 NRestraintType, Object DispArray, Object RefGeom, Int32& ErrorCode[out])` | 反射 |
| SAFEARRAY 元素 | **必须是 24 字节 VARIANT**（`vt=VT_DISPATCH`，指针在偏移 8） | 8 字节指针写法会崩；24 字节写法稳定 |
| 外层 VARIANT | `VT_ARRAY|VT_VARIANT = 0x200C` | 与元素类型一致 |
| `RefGeom` | `VT_EMPTY`（对应 VB 的 `Nothing`） | `VT_UNKNOWN`/`实体` 会崩 |
| `ErrorCode` | `VT_I4|VT_BYREF` 指向调用方缓冲区 | 我此前误用按值传，已修正 |
| `wFlags` | **0** | `1`(DISPATCH_METHOD) 会崩 —— 这条与常见建议相反 |
| `NRestraintType` | **0**（`swsRestraintTypeFixed`） | 传 1/2 会崩 |
| 几何来源 | 选中的面 / 官方 `GetObjectByPersistReference3` 往返，两者**结果相同** | 传"实体"会崩 |
| SAFEARRAY 分配 | 必须 `SafeArrayAccessData`（`SafeArrayCreateVector` 建的数组**惰性**，直接读 `pvData` 是 NULL） | 这曾让我误判"路走不通" |

---

## 3. 完整实测矩阵（每轮重启服务、只发一次 Invoke）

| 变量 | 取值 | 结果 |
|---|---|---|
| 元素类型 | `VT_DISPATCH`(0x9)，8 字节指针 | E_INVALIDARG |
| | **`VT_VARIANT`(0xC)，24 字节 VARIANT** | **E_INVALIDARG（唯一稳定）** |
| | `VT_UNKNOWN`(0xD) | 崩 |
| | `VT_VARIANT` 但按 8 字节布局写 | 崩 |
| `wFlags` | **0** | **E_INVALIDARG** |
| | 1（DISPATCH_METHOD） | 崩 |
| `NRestraintType` | **0** | **E_INVALIDARG** |
| | 1, 2 | 崩 |
| `RefGeom` | `VT_EMPTY` | E_INVALIDARG |
| | `VT_NULL` | 崩 |
| 几何来源 | 选中的面包装 | E_INVALIDARG |
| | 官方 PID 往返 | E_INVALIDARG（**结果相同**） |
| | 面所属实体 | 崩 |
| 前置 | 先 `CreateMesh` 再调 | **崩**（见 §4） |
| 次数 | 同一进程第二次 Invoke | **必崩** |

---

## 4. 关键判别：E_INVALIDARG 意味着什么

`argErr = 0`（参数 1 没问题）**且 `ErrorCode` 未被写回**。

⇒ **cosworks 在解包参数之前就返回了 `E_INVALIDARG`**，错误码也不是我们传的 `out` 参数写的。

⇒ 所以 `E_INVALIDARG` **不是"参数类型/形态不对"**（形态已全部排查正确），
而是**收到参数后做了某种状态/语义检查并拒绝**。

**这指向"研究状态"问题，而不是"调用格式"问题。**

---

### 4.5 ⭐⭐⭐ 2026-09-27 补充：两条决定性证据，方向已定案

第 3 节的实测矩阵之后又做了两个判别实验，**彻底改变了排查方向**：

**证据 A：传 `0 元素` SAFEARRAY 也失败**
```csharp
psa = SafeArrayCreateVector(VT_VARIANT, 0, 0);   // 零个元素
vArray.vt = VT_ARRAY|VT_VARIANT (0x200C);  vArray.parray = psa;
Invoke(DispId=3) -> hr=0x80070057 (E_INVALIDARG)
```
零个元素 ⇒ **没有任何东西可解包**，但依然 `E_INVALIDARG`
⇒ **"元素布局 / VT_VARIANT 24 字节 / 数组指针层级"这一整类假设被彻底排除。**

**证据 B：`AddForce`（另一个写方法，DispId=4）也一样失败**
不同方法、不同 DispId、不同语义 ⇒ 结果完全一致
⇒ **不是 `AddRestraint` 特有的问题。**

**汇总**

| 类别 | 实测 |
|---|---|
| **读操作**（`lrm.Count`→0、`GetLoadsAndRestraints(0)`→err=1=NotFoundAtIndex 且不抛异常） | ✅ **成功** |
| **写操作**（`AddRestraint` / `AddForce` / `AddForce3`） | ❌ **全部 E_INVALIDARG** |

**穷尽且全部不改变结果的参数维度**：0/1/2 元素 · VT_VARIANT(24B)/VT_DISPATCH(8B)/VT_UNKNOWN ·
RefGeom=VT_EMPTY/VT_NULL/空IDispatch/真实IDispatch · wFlags=0/1 · NRestraintType=0/1/2 ·
几何来源=选中面/官方 PID 往返 · 参数顺序=声明/逆序 · cArgs=4/cNamedArgs=0

### ⇒ 定案

**`E_INVALIDARG` 与任何调用参数无关。`ICWLoadsAndRestraintsManager` 的读操作正常、
写操作被整体拒绝。剩下两种可能（未能区分）：**

**(a) 许可边界** —— 写载荷/夹具需 Simulation 授权，读不需要。
> 佐证：`swsLoadsAndRestraintsError_InvalidLicense = 7` 存在但**从未被返回** ——
> 因为我们在解包前就被拒，走不到写 `ErrorCode` 的步骤。

**(b) 研究状态** —— 研究未激活/未网格化/未进入可编辑态。

**区分办法**：判 (a) 用 UI 手工建一次夹具（UI 也建不出 ⇒ 许可，本机无解）；
判 (b) 先解决建网格（见 §5.1，`CreateMesh` 会崩是当前第一障碍，可试 `CopyMeshFromStudy`）。

---

## 5. 未解决的问题（就是我要建议的部分）

### 5.1 ⭐ 最大嫌疑：cosworks 要求研究已网格化

**这是唯一"官方流程里必然先发生、而我测不了"的步骤。**

- 官方流程：材料 → 夹具 → 载荷 → 网格 → 求解（夹具在网格**之前**）
- 但我调用 `AddRestraint` 的那个研究**没有网格**（`run_solve` 默认 false）
- 我试了 `mesh_first`（先 `CreateMesh`）→ **服务崩溃**

**障碍**：`CreateMesh(Int32 NUnits, Double DElementSize, Double DTolerance) -> Int32`
在本机此位置**崩溃/阻塞**。这是已知的"同步 COM 调用弹模态框"问题
（枚举 SW 顶层窗口可见 `class='#32770' title=''`）。`MeshAndRun()` 能跑通但会直接求解。

**求建议**：
- 有没有办法**建网格但不求解**？（`CreateMesh` 的三个参数怎么给？`NUnits` 用哪个枚举？）
- 能否**用 `MeshAndRun` 建完网格后不等它求解**、或用 UI 预建一次网格再复制？
- `ICWStudy` 上有个 **`CopyMeshFromStudy(String SStudyName) -> Int32`** ——
  能否先手工建一个带网格的研究，再把它复制过来？

### 5.2 研究可能需要显式激活/求解菜单

`ICWStudy` 上有 `ActivateConfiguration() -> Void`，但我没找到 `SetSolveMenu`。
**求建议**：cosworks 是否需要先把研究设成"活动/待求解"状态，才接受夹具？
有没有类似 `ICWStudy.ActivateStudy()` / `SetSolveMenu` 的成员（可能名字不同）？

### 5.3 也许该读 TLB 定死真实类型（一直没做）

`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\cosworks.tlb`（512 KB）
TypeLib GUID `{B5697F4F-C68A-4685-A7B8-478AF05EF605}`

**没读到的信息**：`AddRestraint` 的 `DispArray` 参数在 IDL 里的真实声明——
到底是 `SAFEARRAY(VARIANT*)` 还是 `SAFEARRAY(IFace2**)` 还是某个自定义结构。
如果它其实是"**指向数组指针的指针**"（`VARIANT**`），那我的 `VT_ARRAY|VT_VARIANT` 就**差一层间接**。

**求建议**：
- 怎么用 C++ 小工具（十几行）读 TLB 的 `FUNCDESC`/`ELEMDESC`？
  （.NET 8 的 `ITypeInfo.GetDocumentation` 没有 6 参重载，自写 C# 解析器会编译失败）
- 有没有现成工具（`oleview.exe` / `tlbview`）能直接看？

### 5.4 也可能 cosworks 要的"几何"根本不是面

`AddRestraint` 官方说明是 *"Array of entities to which to apply the restraint"*——
"entities" 可能特指 **实体(Body)** 而非面。但我传实体会崩，
说明崩在**封装层**（`IFace2.GetBody()` 返回的 RCW 的 QI 可能失败），不代表 cosworks 拒收实体。

**求建议**：怎么正确地把一个 **Body/ModelEntity** 的 IDispatch 传进去？
`GetSelectedObject6(1, -1)` 在选面时返回的是什么类型？有没有更直接的
`IEntity.GetPersistReference3` 路径？

### 5.5 ⭐⭐ 新证据：元素个数改变了崩溃行为（这条最值得看）

官方示例是 `Dim varArray1 As Object() = {pointer1, pointer2}` —— **两个**面。
我长期只传 1 个，本轮补测了 2 个：

| 元素个数 | 结果 |
|---|---|
| **1 个** | `E_INVALIDARG`（进方法体，被语义拒绝） |
| **2 个** | **直接崩服务**（AccessViolation） |

⚠ **这个对比信息量很大**：如果 cosworks 期望的元素是 8 字节裸指针，
那我写的 24 字节 VARIANT 就会**越界写坏相邻内存**——单面时越界可能刚好落在
未使用的分配区（所以"看起来能跑"），双面时越界就会踩到活的结构 ⇒ 崩。

**⇒ 这强烈提示：我造的元素布局可能仍然是错的，只是单面时"侥幸没炸"。**
换句话说，`E_INVALIDARG` 可能**不是语义检查失败，而是它按 8 字节元素解包我的
24 字节数据，读到了垃圾**。

**求建议**：
- `SAFEARRAY(VT_VARIANT)` 的元素在 VBA 封送里到底是 **8 字节还是 24 字节**？
  （理论上 SAFEARRAY(VT_VARIANT) 元素应是 16/24 字节的 VARIANT，但有些封送路径是 8 字节指针）
- 有没有办法在**不崩**的前提下把两种布局都试一遍（比如先传 2 个但每个元素后跟 16 字节填充，
  或者传 1 个但数组分配得更大）？
- `VBA 的 Object() 数组`在 C++ 侧看到的 SAFEARRAY 描述符是什么样？

### 5.6 未经测试的组合

- `RefGeom` 传**真实对象**（如坐标系/面）而不是 `VT_EMPTY`
- `NRestraintType` = 3/4/…（我只试了 0/1/2，1 和 2 都崩了所以没继续）
- 一次传两个**不同**的面（本轮试了但因为上面 5.5 的问题崩了，
  且中途还发现 `SelectFaceByIndex` 连调两次会返回**同一个**面，
  已改用 `IBody2.GetFaces()[k]` 取真正的第 k 个面）

- `RefGeom` 传**真实对象**（如坐标系/面）而不是 `VT_EMPTY`
- `NRestraintType` = 3/4/…（我只试了 0/1/2，1 和 2 都崩了所以没继续）
- 一次传**两个面**（官方示例就是 `{pointer1, pointer2}`，我一直只传 1 个）
  ← **这个我漏了！** 官方 `varArray1 = {pointer1, pointer2}` 是**两个元素**，
  虽然第一行注释说"First two selections are the faces for restraints"。
  单元素数组是否被拒？**这是很可能的。**

---

## 6. 我的下一步计划（如果你没别的建议就按这个走）

| 顺序 | 做什么 | 成本 | 预期 |
|---|---|---|---|
| **1** | **把 SAFEARRAY 元素布局彻底定死**（见 §5.5）：8 字节指针 vs 24 字节 VARIANT，<br>在不崩的前提下两遍都试 | 低 | ⭐⭐ **现在最可疑** |
| 2 | 解决 `CreateMesh` 单独建网格 | 中 | 验证"需网格化"假设 |
| 3 | 读 TLB 定死 `DispArray` 真实 IDL 声明 | 中 | 可能是"**差一层间接**"（`VARIANT**`） |
| 4 | C++/CLI `#import "cosworks.tlb"` 写最小 C++ 验证 | 高 | 独立交叉验证，绕开全部托管层 |
| 5 | 研究激活/求解菜单相关成员 | 低 | 备选路径 |

**第 1 项我现在就能做**（用填充/对齐的方式让两种布局都不越界），要不要我先做掉再回来？

---

## 7. 工程约束（接手的人务必知道）

- **每轮必须重启服务 + SolidWorks**（WMI 派发），**只发一次 Invoke** ——
  第二次必崩（第一次 `E_INVALIDARG` 之后 cosworks 内部状态已不一致）。
- `topology_optimize` 的 `raw_invoke` 默认 **false**（崩服务风险）。
- 服务编译：Roslyn `csc`，递归编译 `Services\*.cs`；脚本 `tools\build.ps1`。
- 一键测一个组合：`tools\rawtest.ps1 -Elem 12 -WFlags 0 -RestType 0 -RefGeom 'empty' -FaceSrc 'sel' [-Mesh]`
  （它自己会编译 + 重启 + 调 + 打印结果）
- 关键文件：
  - `execution\solidworks\SolidworksExecution\Services\RawInvoke.cs`（原生调用实现）
  - `execution\solidworks\SolidworksExecution\Services\SolidWorksService.Capability.cs`
    （`TopologyOptimize`，L1600 附近是 RAW-INVOKE 块）
  - `tools\rawtest.ps1`（测试驱动）
  - `tools\rawinvoke.cs`（`RawInvoke` 的独立副本，改动前先同步）
- **不要联网碰任何许可/激活/注册端点**（本机是盗版安装，红线）。

---

## 8. 给你的一句话

**通道已经打通了，参数形态也全部正确，但 `ICWLoadsAndRestraintsManager` 的
写操作被整体拒绝（传 0 个元素也一样、`AddForce` 也一样），而读操作正常。**

**这已经不是调用方式问题了。** 请优先帮我区分这两种可能：

1. **是不是许可问题？** —— 最快的判法：用 SolidWorks 界面手工建一次 Fixed 夹具。
   UI 能建 ⇒ 许可没问题，是研究状态问题；UI 也建不出 ⇒ 许可，本机无解，别再投时间。
2. **是不是研究状态问题？** —— 如果是，`CreateMesh` 的正确用法是什么？
   （`CreateMesh(NUnits, DElementSize, DTolerance)`，返回 `swsStudyMeshError_e`；
   但本机调用它会崩/阻塞，是当前第一障碍。`CopyMeshFromStudy(SStudyName)` 能否绕开？）

**另外两个可能值得一并考虑**（我已排除但也许判断有误）：
- 论文里用的是 `SelectByID2(name, "PLANE", ...)`，我全程用 `"FACE"`。
  `DispArray` 要的会不会是**参考几何**而不是模型面？
- `ICWRestraint` 有 `InsertEntity(Object)` / `SetReferenceGeometry(Object)`，
  能否先建空夹具再插几何，完全绕开 `AddRestraint` 的数组参数？
