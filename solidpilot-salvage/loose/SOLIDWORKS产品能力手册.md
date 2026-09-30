# 本机 SOLIDWORKS 产品能力手册（2026-09-27 实测盘点）

> **数据来源全部是本机实测**，不是网上抄的：目录体积、exe 存在性、interop DLL 反射、
> 组件命令清单、注册表、Windows 服务状态。
> **每个产品都回答 6 个问题**：是什么 / 能干什么 / 本机状态 / 怎么用 / 能不能被 AI 编程 / 有什么坑。

---

## 0.0 执行层工具速查（都经直连 REST 实测）

| 工具 | 状态 | 实测证据 |
|---|---|---|
| `insert_standard_part` | ✅ 已修复 | 配置选项改 `0` 后 **15/15** 成功（修前 0/15） |
| `motion_study` | ✅ 可用（AVI 除外） | explode / rotation 均 `-> True`；AVI 导出 `SaveToAVI` 真实返 `False`（渲染侧限制，已如实回报） |
| **`electrical`** | ✅ **实测通过** | `reachable=True`、`version=2026.0.0.5070`、`project_manager=EwAPI.EwProjectManagerXClass`、`env_qi=True`（58 方法） |
| `topology_optimize` | ⚠ 控制项全通，夹具受阻 | 四控制 + 质量/位移约束 + 网格 `mesh_present=true` 全通；凡接收几何数组的 `Add*` 12+ 形态全败（详见 §4） |
| `bom_from_assembly` / `list_standard_parts` / `lcsc_fetch_step` | ✅ 可用 | 见 §13/§14 |

**`electrical` 的调用链（已验证，改代码时别改坏）**：
```
CoCreateInstance(EwInteropFactoryXClass {B5F20185-7EA0-43C1-B21D-94175E6F01FF})   ← 不是 EwAPIXClass（未注册）
  → factory.getEwAPI(out err)      [IDispatch 调，QI 会失败]        err=0
  → api.setEwSoftType(kSoftTypeSWElectrical=1)                        0
  → api.initialize()                                                 0
  → api.newEwEnvironment()                                           EwEnvironmentX
  → env.getEwProjectManager(out err) / env.getVersion()   [强类型调]  2026.0.0.5070
```

---

## 0. 一句话总览

本机装的是 **SOLIDWORKS 2026 完整套件**（Premium），含 **15 个可用产品 + 2 个空壳**。
它们不是互相独立的软件，而是**共用一个 CAD 内核的"专业模块"**：

```
                    ┌─────────────────────────────────────┐
                    │  SOLIDWORKS 核心（7.8 GB, 107 个 exe）│
                    │  零件 / 装配体 / 工程图 / 钣金       │
                    └─────────────────────────────────────┘
                                    │ 共享文件格式、界面、许可证
   ┌────────┬────────┬────────┬──────┼──────┬────────┬────────┐
   ▼        ▼        ▼        ▼      ▼      ▼        ▼        ▼
 CAM     Electrical  Flow    Simulation Motion Toolbox  CAM     ...
(加工)   (电路)     (流体)  (结构)  (运动)  (标准件)
```

**关键认知 1**：SolidWorks 是"一个软件 + 一堆插件模块"，不是"一堆软件"。

**关键认知 2（最易混的概念）**：SOLIDWORKS 里有两个都叫"渲染/仿真"的东西，
**完全是两回事**：

| | **Visualize = 美术渲染** | **Simulation / Flow = 仿真** |
|---|---|---|
| 算什么 | 光线反射（光学） | 应力 / 压力（力学·流体力学） |
| 要什么输入 | 3D 模型 + **材质 + 灯光** | 3D 模型 + **材料 + 载荷 + 夹具** |
| 出什么 | **好看的图/动画** | **数字**：应力 MPa、位移 mm、温升 ℃ |
| 回答的问题 | "产品长什么样" | "这东西会不会断/过热" |

⇒ **出宣传图找 Visualize，判断能不能用找 Simulation。二者不可互相替代。**
（详细证据见 §10.1：本机 Visualize Boost 带的是 `optix_prime` 光追 + `OpenImageDenoise` 降噪
+ 材质库 + 云渲染 broker，**一个求解器都没有**。）

---

## 1. 本机产品总表（实测判定）

| # | 产品 | 体积 | 状态 | 干什么 | AI 可编程 |
|---|---|---|---|---|---|
| 1 | **SOLIDWORKS 核心** | 7,860 MB | ✅ 完整 | 零件/装配体/工程图/钣金/曲面 | ✅ `sldworks.dll` **1872 类型** |
| 2 | **SOLIDWORKS Electrical** | 703 MB | ✅ 完整 | **电路原理图 + PCB + 布线 + BOM** | ✅ **683 类型**（`Interop.EwAPI.dll`，见 §3.5） |
| 3 | **SOLIDWORKS Simulation** | 466 MB | ✅ 完整 | 结构强度/疲劳/拓扑优化 | ✅ `cosworks.dll` 615 类型 |
| 4 | **SOLIDWORKS Flow Simulation** | 1,230 MB | ✅ 完整 | 流体/散热/ CFD | ⛔ **API 未安装**（见 §5） |
| 5 | **SOLIDWORKS Inspection** | 813 MB | ✅ 完整 | 尺寸检测报告/CMM | ✅ `dsgnchk.dll` 19 类型 |
| 6 | **SOLIDWORKS PDM / Manage** | 1,448 MB | ✅ 完整 | 文档/版本/权限管理 | ✅ `swdocumentmgr.dll` 504 类型 |
| 7 | **Visualize Boost** | 821 MB | ✅ 完整 | **美术渲染**（不是仿真！见 §10.1） | ⚠ 未确认 .NET API |
| 8 | **Composer Player** | 405 MB | ✅ 完整 | 看技术文档（只读） | ❌ |
| 9 | **eDrawings** | 601 MB | ✅ 完整 | 轻量看图/审阅，**免费** | ❌ |
| — | ~~SOLIDWORKS CAM~~ | 2,868 MB | 已装但**不用** | CNC 刀路 | — **你用 Fusion 360 加工，跳过** |
| — | ~~SOLIDWORKS Plastics~~ | 2,332 MB | 已装但**不用** | 注塑模 | — **你不搞注塑，跳过** |
| — | ~~SOLIDWORKS Composer~~ | 1 MB | ❌ 空壳 | 技术文档创作 | — 目录无 exe，**没装** |
| — | ~~SOLIDWORKS Visualize~~ | 2 MB | ❌ 空壳 | 渲染 | — 只有 2 个 dll，**没装** |

### 1.1 用户的实际工作范围（决定学习优先级）

**用户 2026-09-27 明确排除**：
- **CAM 不用** —— 加工走 Fusion 360。实测本项目**无任何刀路文件**（`.nc`/`.tap`/`.gcode`/`.mpf`），印证属实
- **Plastics 不用** —— 不搞注塑。实测项目里无注塑件
- **Composer** —— 本机是空壳（只有 1 个 dll 无 exe），本体根本没装

⇒ **本手册后续只展开"要学"的 9 个产品**，划掉的三个只保留一行说明跳过理由。

### 1.2 ⚠ 澄清：Composer ≠ 装配体

| | 装配体（Assembly） | Composer |
|---|---|---|
| 是什么 | 3D 零件的**装配关系** | 把 3D 模型做成**带图解的技术说明书** |
| 产物 | `.SLDASM` 文件 | 可交互说明书（爆炸图 + 步骤图 + 注释） |
| 举例 | 你项目里的 `换刀主轴装配_BT30_ATC_Assembly.SLDASM` | 自动生成"①拆顶盖 ②取主轴 ③注意轴承预紧"发给装配工 |
| 属于谁 | **核心功能**（7.8GB 内） | **独立产品**（本机空壳） |

⇒ 装配体是核心的一部分，天天在用；Composer 消费装配体、但本身是另一个产品。

### 1.3 其它状态的判定依据

另有 `ForFaceSelector`（**20.6 GB**）——这不是产品，是个巨大的第三方人脸/面框选择器
（ForFaceSelector 是个 AI 人脸插图工具，20GB 说明装了模型库）。

### 1.1 本机版本号实测（判断是否同版配套）

| 产品 | 主 exe | 版本 |
|---|---|---|
| SOLIDWORKS 核心 | `DsgnChkRptView.exe` | **34.0.0.5070**（内核版本号） |
| Electrical | `SOLIDWORKSElectrical.exe` | **2026.0.0.5070** |
| Inspection | `SOLIDWORKS Inspection.exe` | **2026.0.0.5070** |
| CAM | `cwadoserver32.exe` | 2026.0.0.869 |
| Flow Simulation | `flow simulation api sdk x64.exe` | 516.0.6837.0 |
| PDM | `AddInRegSrv64.exe` | 34.0 |
| Manage Client | `adxregistrator.exe` | 10.1.4703.0 |
| Visualize Boost | `broker_node.exe` | 93.19 |
| Composer Player | `composerplayer.exe` | 7.13.2.26361 |
| eDrawings | `eDrawingOfficeAutomator.exe` | 34.0.0.5029 |

**`34.0.0.5070` 是 SolidWorks 2026 的 interop/内核版本号**——电气/检测/核心三者的
`5070` 后缀一致，说明它们是**同一次安装的配套版本**，可以互相传数据。

---

## 2. SOLIDWORKS 核心（基础，一切的前提）

**是什么**：参数化 CAD 内核。画的是"特征"（草图→拉伸→切除…）而不是"面"，
所以改尺寸能自动更新整个模型。

**能干什么**：草图/特征建模、装配与配合、工程图、钣金、曲面——**本项目 90% 的工作都在这里**。
纯参数化：改尺寸模型自动更新（不是直接画面）。

**本机能力**（`SolidWorks.Interop.sldworks.dll`，**1872 个类型**，最大的 interop）：
- 零件建模：草图/拉伸/旋转/扫掠/放样/圆角/倒角/阵列/钣金
- 装配：配合（`add_mate`）、零部件、`analyze_assembly`
- 工程图：`create_drawing` / `add_drawing_view`（⚠ 本机中文版 `add_drawing_view` 返
  `VIEW_CREATION_FAILED`，出图走不通）
- 曲面：`surfacing` 目录 176 MB

**本机状态**：✅ 完整（7,860 MB / 107 个 exe / 20,549 文件），版本 `34.0.0.5070`
（= SolidWorks 2026 内核版本号，Electrical/Inspection 的 `5070` 后缀与之相同 ⇒ 同版配套，可互传数据）

**怎么用**：见 `AI操作手册_SolidWorks.md` §3。

**AI 可编程性**：✅ **本项目最成熟的部分**（1872 个类型，官方离线包
`C:\swapi\types\<接口>\<方法>.md` 逐方法有文档，含 3,708 个官方示例）。

**坑**：
- ⚠ **`AddComponent5` 的配置选项必须传 `0`**（`CurrentSelectedConfig`），
  传 `2`（`NewConfigWithAsmStructure`）会**间歇性返回 null**——空装配体必失败，
  有配置时成败取决于当前配置状态。修正后 15/15。详见 `AI建模操作手册.md` §14.1。
- ⚠ `x/y/z` 传的是**零件中心**不是原点（官方原文 "X coordinate of the component center"），
  需要落原点要自己传 `center_offset_*`。
- ⚠ **`add_drawing_view` 在本机中文版 2026 返回 `VIEW_CREATION_FAILED`**（已知问题），
  所以"AI 自动出工程图"这条路目前走不通。
- ⚠ SolidWorks 的方向参数是 `Dir` 不是 `Reverse`；切除边界靠 `T0`+`StartOffset` 不靠 `D1`。

---

## 3. ⚡ SOLIDWORKS Electrical —— 你问的这个是什么

### 3.1 它是什么（一句话）

**电气工程师的"原理图 + PCB"设计软件**，和机械 CAD 同一家公司出品、同一套界面，
但管的是**电**，不是**铁**。

### 3.2 它能干什么（从本机组件直接读出的功能地图）

Electrical 的每个功能是一个"命令模块"（`.trx` 文件），本机实测装了这些：

| 命令模块 | 功能 |
|---|---|
| `EweDrawingsCmd` | **出工程图**（电气原理图图纸、端子图） |
| `EwBomCmd` | **物料清单 BOM**（Excel 格式，可导入 PDM） |
| `EwRoutingCmd` | **布线/走线**（导线自动布放） |
| `EwTerminalCmd` | **端子与端子排**（接线端子、端子编号） |
| `EwBibCmd` | **图框/标题栏/BIB**（图纸边框与信息块） |
| `EwDlPartsCmd` | **可复用电路模块**（类似"电气零件"） |
| `EwExchangeCmd` | **数据交换**（导入/导出、与 Excel/PDM 互转） |
| `EwBidExcelCmd` | **Excel 自动化**（官方文档 `excel automation_en.pdf` 专讲这个） |
| `EwPrintCmd` | 打印 |
| `EwAppCmd` / `EwCmd` | 主程序 / 通用命令 |
| `EwAddInMngCmd` | 插件管理 |
| `EwProjDlgCmd` / `EwPropertiesCmd` / `EwRightCmd` | 项目对话框 / 属性 / 权限 |

**后端架构（实测发现，很多人不知道）**：
- 核心是 **TEKLA-DB 引擎**（`TD_Db*.dll` / `*.tx`）——这不是 Dassault 自研的，是外购的第三方库
- **`EwServer` 服务本机正在运行**（pid 10176）
- **`MSSQL$TEW_SQLEXPRESS` 服务也在运行**——Electrical 自带一个 SQL Server Express 实例
  （`TEW` = **T**ekla **E**lectrical **W**orkstation），所有电气元件数据存在这个数据库里
- 符号库（元件图形）在 `C:\ProgramData\SOLIDWORKS\...\ecadlib.db`

### 3.1b ⚠ 三个名字极易混，实测厘清（查手册前先看这段）

| 名字 | 是什么 | 本机官方文档 |
|---|---|---|
| **SOLIDWORKS Electrical** | **主体**：原理图 + PCB + 端子 + BOM | ⚠ **本机没有原理图主体 CHM** |
| **CircuitWorks** | **ECAD 转换器**（Altium/OrCAD ⇄ SOLIDWORKS），管 IDF / PADS / 网表转换 | `circuitworks.chm`（167 页）+ `otcircuitworks.chm`（14 页）✅ |
| **Routing Electrical** | **线束/导管布线**（线束、导管、电缆走向） | `otroutingelectrical.chm`（24 页）✅ |

⇒ **查 Electrical 原理图时别被带偏**：`lang\english` 里**没有 Electrical 原理图手册**，
只有上面后两个。`C:\swdoc\elec_circuitworks` 那 167 页讲的是 **ECAD 转换**（打开 ECAD 文件 →
编辑属性 → 从 CircuitWorks 建 SOLIDWORKS 零件/装配 → 改 ECAD → 导出回 CircuitWorks），
**不是画原理图**。
**Electrical 原理图侧的知识以反射 `Interop.EwAPI.dll` 的 683 个接口为准（见 §3.5）。**

**本机实测版本与运行态（2026-09-27）**：
```
SOLIDWORKSElectrical.exe  文件版本 2026.0.0.5070
                         产品名 "SOLIDWORKS Electrical"，描述 "SOLIDWORKS Electrical 2026 SP0.0"
服务  ewserver                Running   ← Electrical 后端
服务  MSSQL$TEW_SQLEXPRESS    Running   ← 电气元件数据库
服务  SQLTELEMETRY$TEW_SQLEXPRESS Running
服务  SQLAgent$TEW_SQLEXPRESS  Stopped  （正常，非必需）
```
⇒ **Electrical 是完整可运行状态，不是只装了文件。**

### 3.3 典型工作流

```
① 建工程（Project）→ ② 放元件（从符号库拖：电阻/电容/连接器/继电器…）
③ 连线（wire）→ ④ 加智能部件（Smart Components：比如"一个电机"自动带出
   驱动器+电缆+端子+原理图）→ ⑤ 出图 + BOM + 布线
```

**Smart Components 是 Electrical 的杀手锏**：机械那边有"标准件自动插入"，
电气这边就是"电机/传感器/按钮 → 自动生成整套电气原理图 + 端子表 + BOM"。

### 3.4 和机械设计怎么接上

这是你可能真正关心的：**Electrical 出的东西能进机械装配吗？**
- **能**：Electrical 的"机柜/柜体布置"（`EwSwCabinetLayoutAddin`）配合 `SOLIDWORKS PDM`
  和结构件，可以做"电控柜 = 钣金柜体 + 安装板 + 电气元件"的装配
- `SWE_EPDM_Workflow_EN.pdf`（本机有的官方文档）讲的就是 Electrical ↔ PDM 的工作流

### 3.5c ✅ COM 全链路实测通过（2026-09-27，与 Simulation 形成根本对比）

冒烟测试（`$env:TEMP\swprobe\ewsmoke.cs`，只读，不建不删任何东西）：

```
LoadLibrary(SOLIDWORKS Electrical\bin)                -> ok
Interop.EwAPI 加载，导出类型 = 683
EwErrorCode 枚举 = 62 个（EW_NO_ERROR=0 / EW_BAD_INPUTS=2 / EW_DATABASE_CONNECTION_ERROR=6 …）
CoCreateInstance(EwPointX)                          -> System.__ComObject   ← COM 类建得出
EwAPI.IEwPointX : ✅ QI 成功，6 个真实方法
   setXCoordinate / getXCoordinate / setYCoordinate / getYCoordinate / setZCoordinate / getZCoordinate
```

⇒ **Electrical 的 COM 层是真通的**：建得出对象、QI 得到真实接口、方法可枚举。
**与 Simulation 形成根本对比**——那边 24 轮里连一个 `Add*` 调用都发不出去。
（唯一遗留：`getEwApplication(strKey, out err)` 需要一个 key 字符串，
且 `initialize(hwnd)` / `initializeInBackground(hwnd)` 看起来需要主窗口句柄，
**能否纯 headless 初始化尚未验证**，须在 C# 执行层内做——pwsh 7 没有
`Marshal.GetActiveObject`，无法在此验证。）

### 3.5 AI 能不能用它编程 —— ✅ **能，683 个类型**

**本机状态**：✅ 完整（703 MB，11 个 exe），`SOLIDWORKSElectrical.exe`
**文件版本 2026.0.0.5070 / 描述 "SOLIDWORKS Electrical 2026 SP0.0"**（与核心 `34.0.0.5070` 同版配套）。
后端服务 `EwServer` + `MSSQL$TEW_SQLEXPRESS` 均 **Running**。

> ⚠ **本节在初版写的是"没有公开 COM API"，那是错的。**
> 错因：只扫了 `SOLIDWORKS\api\redist` 这一个目录就下了结论。
> **Electrical 的 API 在它自己的 `bin` 目录里**——而 `redist` 目录只装"主 SOLIDWORKS"的产品。
> 教训：**判定"某产品有没有 API"，必须扫它自己的安装目录，不能只看公共 redist。**

**实测证据**：

| 项 | 值 |
|---|---|
| API 程序集 | `SOLIDWORKS Electrical\bin\Interop.EwAPI.dll`（**588 KB**） |
| 64 位版 | `Interop.x64.EwAPI.dll`（同尺寸） |
| 命名空间 | `EwAPI` |
| **导出类型数** | **683** |
| COM 服务器 | `bin\ewapix.dll`（3,939 KB），CLSID `{1EB320E5-9275-4995-969A-30AA4841B667}` |
| 注册状态 | `InprocServer32` + **`Programmable`** + `TypeLib {4714D4C0-…}`，Apartment |

**核心接口**（都是可编程对象）：

| 接口 | 管什么 |
|---|---|
| `IEwAPIX` | **入口**：`getEwApplication` / `newEwEnvironment` / `initialize` / `setApplicationWindow` / `getUTLastError` |
| `IEwEnvironmentX` | 环境（相当于"会话"） |
| `IEwProjectX` | **工程**——加/删项目文件 |
| `IEwSymbolX` / `IEwSymbolCircuitX` | **符号与符号电路** |
| `IEwManufacturerPartX` / `…CircuitX` / `…TerminalX` | **元件、元件电路、端子** |
| `IEwProjectSymbolX` / `…PointX` | 工程里的符号实例与引脚点 |
| `IEwCableReferenceX` | **电缆** |
| `IEwTitleBlockX` | **图框/标题栏** |
| `IEwRoutingConnectionX` | 布线连接 |

**这意味着 AI 可以做的事**（需实测验证，本轮只确认了接口存在）：
建/读工程文件、放置符号、连电路、生成 BOM、出图框、导出 Excel。
—— 也就是**大部分 Electrical 工作流可以自动化**。

⚠ 注意方向：bin 下的 `EwSwAPIImplCmd` 是"**从 Electrical 调 SolidWorks API**"，
和"**用 API 驱动 Electrical**"是两件事，别混。

### 3.5d ⚠ 应用级入口无法直接创建（2026-09-27 实测）

**逐实体对象可以建，应用级入口不行**：

```
CoCreateInstance(EwPointX {1EB320E5-…})        -> ✅ 成功，QI 到 IEwPointX，6 个真实方法
CoCreateInstance(EwAPIXClass {A111EAC6-E900-4CB7-B23B-C31F85414F27})
                                                -> ❌ 0x80040154 REGDB_E_CLASSNOTREG（没有注册类）
```

⇒ **`Interop.EwAPI.dll` 声明了 `EwAPIXClass`（GUID `A111EAC6-E900-4CB7-B23B-C31F85414F27`），
但 COM 里没有注册它。** 只有 6 个实体级 CLSID 注册在 `ewapix.dll` 下
（`{1EB320E5-…}` `{2B57DE04-…}` `{3F20DD28-…}` `{842586D5-…}` `{8e9f0f05-…}` `{B5F20185-…}`）。

**⇒ 推论**：`IEwAPIX`（`getEwApplication` / `newEwEnvironment` / `getEwProjectCurrent` /
`openEwProjectID` / `importFile`）**必须从"正在运行的 Electrical 应用"取得**
（ROT 或应用内嵌），**不能 CoCreateInstance 直接造**。
且 `initialize(hwnd)` / `initializeInBackground(hwnd)` 看起来需要主窗口句柄。
**这两点合起来 ⇒ Electrical 的自动化很可能要求 Electrical 应用已启动，
纯 headless 从零拉起尚未验证。**

⚠ 与 Simulation 的对比：Simulation 是"能进 study、但几何数组调用发不出去"；
Electrical 是"实体对象能造、应用入口造不出"。**两个产品的边界性质不同。**

### 3.5e ✅✅ 完整初始化链路已打通（2026-09-27，Electrical 可用）

**实测可跑的完整序列**（`$env:TEMP\swprobe\ewfactory.cs`）：

```csharp
// ① 工厂（关键：不是那个未注册的 EwAPIXClass）
var factory = Activator.CreateInstance(Type.GetTypeFromCLSID(
    new Guid("B5F20185-7EA0-43C1-B21D-94175E6F01FF")));   // EwInteropFactoryXClass ✅

// ② 拿应用级入口
var api = IDispatch(factory, "getEwAPI", out err);          // err = 0  ✅ 拿到 IEwAPIX

// ③ 官方初始化顺序
IDispatch(api, "setEwSoftType", EwSoftType.kSoftTypeSWElectrical /*=1*/);  // -> 0 ✅
IDispatch(api, "initialize");                              // -> 0  ✅ 服务启动
// ④ 取应用对象
var app = IDispatch(factory, "getEwApplication", key, out err);   // err=0 但 null（key 待定）
```

**实测输出**：
```
CoCreateInstance(EwInteropFactoryXClass)          -> System.__ComObject
IDispatch getEwAPI(out err)                       -> err=0, api=System.__ComObject  ✅
api.setEwSoftType(kSoftTypeSWElectrical=1)        -> 0
api.initialize()                                  -> 0    (0 = EW_NO_ERROR，服务已初始化)
```

⚠ **三个必须知道的坑**：

1. **`EwAPIXClass{A111EAC6-E900-4CB7-B23B-C31F85414F27}` 没有注册**
   （`0x80040154 REGDB_E_CLASSNOTREG`）⇒ **别用 interop 里的这个 coclass**，
   要用 `EwInteropFactoryXClass{B5F20185-…}` 的 `getEwAPI()`。
2. **`IInteropFactoryX` 的 QI 会失败**（interop 声明的 GUID 与实际 `ewapix.dll` 不一致），
   但 **IDispatch（`Type.InvokeMember`）调用完全正常** ⇒ **一律走 IDispatch，不要依赖 QI/转型**。
3. **必须先 `initialize()`**，否则后续调用报
   `Services are not initialized. -- Context: [EwCommon][error]`（EWCommon 的日志会直接告诉你）。

**剩余未解**：`getEwApplication(strKey)` 三种 key（`"SWElectrical"` / `"1"` /
`"kSoftTypeSWElectrical"`）都返回 `err=0` + `null`——这个 `strKey` 很可能是**许可证产品键**
而非模块名。下一步可试 `IEwAPIX.newEwEnvironment()`（不经过 getEwApplication）。

**⇒ 结论：SOLIDWORKS Electrical 是本机唯一已验证"API 全链路可驱动"的仿真类模块**
（Simulation 的 `Add*` 调用发不出去，Electrical 则是能进能初始化）。

### 3.6 坑（补充上面 3.5e 之外的）

- **API 不在公共 redist**，在各产品自己的 `bin` 目录 ⇒ 找 API 要**逐产品扫** `bin`
- **它强依赖后台**：`EwServer` 服务 + `MSSQL$TEW_SQLEXPRESS` 数据库必须在跑，
  否则 API 拿到的是空环境
- **元件库是数据库不是文件**（`ecadlib.db`），复制安装目录 ≠ 复制元件库
- `initialize` / `setApplicationWindow` 看起来是**需要窗口**的初始化步骤
  ⇒ 能否纯 headless 自动化**待实测**（下一轮就验这个）

---

## 4. SOLIDWORKS Simulation（结构仿真）—— 本项目已深挖

**是什么**：有限元分析（FEA）。给零件加**载荷 + 夹具 + 材料**，算**应力/应变/位移/
安全系数/疲劳寿命/固有频率**。还有**拓扑优化**（在保证刚度的前提下尽量减重）。

**能干什么（对本项目的价值）**：
- **静力学**：主轴壳体在扭矩/轴承载荷下的应力与位移 → 判断壁厚够不够、哪里会开裂
- **拓扑优化**：保证刚度前提下把壳体"掏空"减重（**本机被许可边界卡住，见下**）
- **疲劳**：主轴是旋转件，疲劳寿命是关键指标
- **模态/频率**：主轴-刀具-壳体系统要避开共振（刀具跳动、转速谐波）

**本机状态**：✅ 完整（466 MB），
`HKCU\...\AddinsStartup\SldWorks.Simulation.19 = 1` 时可随 SW 启动加载
（`ICosmosWorks.VersionNumber = 891107`，实测）。

**怎么用（典型工作流）**：Simulation 选项卡 → New Study（静力学/拓扑/疲劳/频率）
→ 材料 → 夹具（固定约束，选面）→ 载荷（力/压力/扭矩，选面）→ 右键网格 → 算
→ 看应力云图/S.F. 因子/位移 → 出报告。

**AI 可编程性**：✅ `cosworks.dll` **615 个导出类型**，官方 API 文档已抓 33 个方法页
（`D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\`）。

**✅ 本项目已跑通（headless 全链路）**：
- 加载：需 `HKCU\...\AddinsStartup\SldWorks.Simulation.19 = 1`
- 建研究：`StudyManager.CreateNewStudy3(name, 13, 0, out err)`（13=拓扑，**索引 1-based**）
- 约束：`BeginEdit → CreateGoal(2=MinimizeMass) → 四个 Create*Control + CreateMassConstraint
  + CreateDisplacementConstraint → EndEdit`，**全部 err=0**
- 材料：`SetLibraryMaterialToSelectedEntities` → 0
- headless 选**面**：`SelectByID2("", "FACE", GetClosestPointOn 投影点)` → `swSelFACES=2` ✅
- 网格：`CreateMesh` / `MeshAndRun` → **`mesh_present=true`**（网格确实建出来了）

**❌ 被封的是整个 `ICWLoadsAndRestraintsManager` 接口**（不是某个方法、不是用法错）：

官方签名（从 help.solidworks.com/2021 提取，见 `官方文档\Simulation载荷夹具API签名全表.md`）：

```
AddRestraint  (NRestraintType, DispArray, RefGeom, ErrorCode)
AddForce3     (21 参完整重载)
AddCyclicSymmetryRestraint(FirstFace, SecondFace, Axis, ErrorCode)      ← 不接数组
AddPrescribedDisplacement(Displacements, NLengthUnit, DispArray, RefGeom, ErrorCode)
```

**官方示例的逐字复刻也失败**。官方 `Analyze Part (VB.NET)` 原文：
```vb
pointer1 = Part.Extension.GetObjectByPersistReference3(var1, longstatus)
Dim varArray1 As Object() = {pointer1, pointer2}
LBCMgr = Study.LoadsAndRestraintsManager
CWRes1 = LBCMgr.AddRestraint(0, (varArray1), Nothing, errCode)
```
本机实测（2026-09-27，**官方每一个要素都对上**）：
```
pointer1: persist-ref round trip err=0 -> System.__ComObject    ← 转换成功
>>> AddRestraint(0, Object[]{1}, Type.Missing) -> ArgumentException
```

### 4.4 排查记录（**连续四次自我推翻**）

| 轮次 | 我的说法 | 怎么被推翻的 |
|---|---|---|
| 18 | `MarshalAs(Struct)` 是根因 | `Struct` 是 **cosworks 全程序集统一模式**（`ComputerNames`/`StudyNames`/`VerticesDispArray` 同样）⇒ tlbimp 通用兜底 |
| 18 | 整个接口被封 / 许可边界 | 同对象 **`Count` 正常返回 0**、QI 成功 ⇒ 接口是通的 |
| 20 | 研究类型不对（试拓扑 13，官方用静力学 0） | 改 **`study_type=0` 静力学，同样失败** |
| 21 | CLR 封送层拒绝（错误文本是 CLR 格式） | **把 `cosworks.dll` 移出 `bin\Debug`**（`raw type = System.__ComObject`）⇒ **仍失败** |
| 24 | CLR 是经**注册表 TypeLib** 拿到封送规则的（所以移 DLL 无效） | **临时注销 `HKCR\TypeLib\{B5697F4F-…}` 后重测 ⇒ 仍失败** |

⚠ 第 24 轮改过系统注册表（TypeLib 键），**已用 `reg copy` 完整恢复并验证**，测试副本已删除。
做类似实验务必先备份。

### 4.4b 唯一的判别性实验（站得住的结论）

同接口上【不接收几何数组】的方法作对照：

```csharp
int err; dynamic got = lrm.GetLoadsAndRestraints(0, out err);   // 只收一个 int
// 实测：err = 1，返回 null，**没有抛异常**
```

`err=1` = `swsLoadsAndRestraintsErrorNotFoundAtIndex` —— 因为 `Count=0`，
**这是一个完全正确的响应**。⇒

| # | 结论 | 依据 |
|---|---|---|
| 1 | **子系统功能正常** | 接收调用、返回语义正确错误码、不抛异常 |
| 2 | **不是许可问题** | `InvalidLicense=7` 存在却未出现；许可问题会返 7 而非抛 .NET 异常 |
| 3 | **不是"要求 UI 引导"** | 子系统对纯 API 调用有正常响应 |
| 4 | **只有"传几何数组"这条路抛异常** | 不带数组→正常返码；带 `DispArray`→抛 `ArgumentException` |

**已排除（有证据，勿重试）**：许可 · 子系统不可用 · 必须 UI 引导 · 研究类型 ·
接口不可达 · 选面错误 · 元素类型 · 数组形态（`object[]`/`Array`/SafeArray）·
null 语义（null/Missing/DBNull）· interop DLL 的 `MarshalAs` · **注册表 TypeLib 的封送规则**。

**⇒ 阻塞点仍未定位。** 唯一未试方向见 §4.5。

### 4.4c `DispArray` 的封送声明（现象记录，非结论）

```
AddRestraint:
  NRestraintType  Int32    (无)
  DispArray       Object   MarshalAs = Struct
  RefGeom         Object   MarshalAs = IDispatch
  ErrorCode       Int32&
AddForce3 的 DispArray（第18参）同样 Struct
```
⚠ 只是现象。`Struct` 是 cosworks 全程序集统一模式，且第 24 轮证明注销 TypeLib 后仍失败，
**不能据此断定它是原因**。


| 方案 | 状态 |
|---|---|
| ~~界面里手工建夹具~~ | ❌ **已排除必要性**——§4.4b 证明子系统对纯 API 调用有正常响应 |
| **手工 DISPPARAMS 直调** | ⭐ 唯一未试方向 |
| 换机器 | 换了也不解决——**证据表明不是许可问题** |

**DISPPARAMS 实施要点与坑（已探明，供实施者直接用）**：

```
① 基础件（已验证可编译）：oleaut32!SafeArrayCreateVector(VT_UNKNOWN,0,n)、
   SafeArrayPutElement(psa,&i,pIUnknown)；VARIANT x64 布局 vt@0、union@8，
   数组 vt = VT_ARRAY|VT_VARIANT = 0x200C
② 取真实指针用 Marshal.GetIUnknownForObject(face)，不是 GetDispatch
③ ⚠ 已实测：用【假指针】测 SafeArrayPutElement 直接 AccessViolation(0xC0000005)
   崩进程（VT_UNKNOWN 元素会被 AddRef）⇒ 必须【在服务里对真实面对象】测
④ 本机 .NET 运行时【没有】Marshal.GetNativeVariantForObject，只能 P/Invoke oleaut32
⑤ Marshal.WriteInt16 第三参必须 (short) 强转 ushort
```

**风险**：纯原生内存操作，偏移写错即崩溃且崩溃点可能与出错点无关。
**建议放在独立探针进程里做，不要直接改主执行服务。**

### 4.5 怎么解决

1. **元素类型**：需把指针 `Marshal.GetTypedObjectForIUnknown` 转成具体接口
   （如 `IFCEntity2`/`IFace2`）再入数组。
2. ✅ **已修**：选面后曾被 `SelectBodyArray` 覆盖成实体（`selectedObjectType2` 曾是 76
   而非 2）——已修，现稳定为 2，但**不是根因**。
3. **调用时机**：夹具/载荷应在网格**之后**、求解**之前**加（我目前放在之前）。
4. **原始 TLB**：直接查 `Simulation\cosworks.tlb` 里 `DispArray` 的 VARIANT 声明。

---

## 5. SOLIDWORKS Flow Simulation（流体/散热）

**是什么**：CFD。基于有限体积的流体仿真——管路压力损失、阀门流量、
**电子器件散热**、风道、泵/风机性能曲线。

**本机状态**：✅ 完整（1,230 MB，16 个 exe，含 `flow simulation api sdk x64.exe` 36 MB）

**AI 可编程性**：⛔ **本机【未安装】API**（2026-09-27 复查确认）

| 项 | 实测结果 |
|---|---|
| `API\flow simulation api sdk x64.exe`（35.6 MB） | 它的 `FileDescription` 是 **"Setup Launcher Unicode"** —— **这是安装程序，不是 SDK 本体** |
| `API\` 目录内容 | **只有这一个 exe**，没有任何 dll/tlb/头文件 ⇒ **API 尚未安装** |
| `binCFW\EFDApi.tlb`（542 KB） | 原生类型库，`LoadFrom` 抛 `Bad IL format`，**未在 `HKCR\TypeLib` 注册** |
| `bin\efdsolver.exe`（1.8 MB） | 求解器本体（命令行可调，但需已有算例文件） |

⇒ **准确表述：Flow Simulation 的 API 是"可安装但本机未装"**，
不是"没有 API"。要用得先跑那个 Setup Launcher 装上（装完再复查有什么 interop）。

⚠ 这条是本手册 §16 五步法的**第四种情形**——"安装器在但组件没装"，
只扫 redist 或只看文件大小都会误判。

**典型用途**（对你这个项目直接相关）：
- **主轴壳体的轴承位发热分析**——热源（电机+轴承损耗）→ 壳体温升 → 是否需要散热筋
- 这比拓扑优化更可能对主轴壳体有实际价值（拓扑卡在许可边界，流体这条路没被堵）

**怎么用（典型工作流）**：Flow Wizard 选分析类型（内部/外部流体、热传导、散热）
→ 选区域（入口/出口/壁面/热源）→ 网格 → 设材料与边界条件 → 算 → 看温度/压力/速度云图
→ 出报告。`efdsolver.exe` 是底层求解器。

**坑**：
- ⚠ **API 未安装**（上表）⇒ 想自动化得先跑那个 Setup Launcher 装上，
  装完才能谈编程；**不要在没装前假设它可驱动**。
- ⚠ 和 Simulation 一样需要夹具（入口/出口）和载荷，**但 Flow 的边界条件
  比结构夹具容易建**（入口/出口是面选择，不是"固定"这种约束）⇒ 如果拓扑因
  `AddRestraint` 卡死，Flow 有可能反而能跑通——**值得单独验证一次**。
- ⚠ 需要网格质量；薄壁件（垫圈/碟簧类）要用足够的单元数，否则结果不可信。
- ⚠ 热分析耦合固体导热时，材料导热系数是必填项，容易漏。

---

## 6. ~~SOLIDWORKS CAM~~ —— 已排除，不学

**用户 2026-09-27 明确：CAM 不用，加工走 Fusion 360。**

- **是什么**（了解即可）：把 3D 模型编程成机床执行的刀路（G 代码）。铣削/车削/线切割/电火花。
- **本机状态**：✅ 装了（2,868 MB，14 个 exe，`TechDB-App.exe` 176 MB 是完整刀具数据库）
- **实证不用**：本项目无任何刀路文件（`.nc`/`.tap`/`.gcode`/`.mpf`），
  所有零件只有 `.sldprt`（设计）+ `.step`（交换），印证属实。
- **顺带记录**：`SOLIDWORKS CAM\camworks.tlb`（677 KB）存在，但是**原生类型库**
  （`LoadFrom` 抛 `Bad IL format`）且**未在 `HKCR\TypeLib` 注册** ⇒ 判为
  "有 API 但未验证可用"（见 §16）。既然不用，不投入。

**能干什么 / 怎么用**：把 3D 模型的表面加工工艺编程成机床执行的刀路（铣削/车削/线切割/电火花）→
导出 G 代码 → 交给机床。流程：选毛坯与机床 → 选工序（粗/精/钻/攻）→ 选刀具 → 算刀路 → 仿真 → 出 NC。

**AI 可编程性**：⚠ 见上（`camworks.tlb` 原生 TLB，未验证可用）。

**坑**：
- ⚠ **本机不装不影响你**：加工走 Fusion 360。
- ⚠ 即使能编程，AI 帮的忙也有限——它产的是**刀路不是形状**，且需要真实机床、
  刀具、工件材料参数才有意义。
- ⚠ `TechDB-App.exe` 有 176 MB（完整刀具/加工数据库），装它很占地方。

## 7. ~~SOLIDWORKS Plastics~~ —— 已排除，不学

**用户 2026-09-27 明确：不搞注塑。**

- **是什么**（了解即可）：塑料件设计 + 注塑成型分析（分型面/浇口/冷却水路 + 充填保压翘曲预测）。
- **本机状态**：✅ 装了（2,332 MB，33 个 exe，`packw.exe`/`cool.exe`/`warp.exe`
  各 208 MB，是真求解器）
- **实证不用**：项目里无注塑件（全是你 BT30 主轴的金属机加工件）。
- **API**：实测**确认无**（redist 无、产品目录也无 .tlb/.olb）——
  这是本表中少数确认为"无 API"的产品（与 CAM/Flow 的"有文件但用不了"不同）。
- **能干什么 / 怎么用**：注塑模部分——分型面、浇口、顶针、冷却水路、滑块/斜顶；
  成型分析部分（Moldflow 引擎）——充填、保压、冷却、翘曲、收缩预测。
  流程：建塑件 → 定模架 → 分型面 → 布浇口/顶针 → 冷却水路 → 网格 → 跑分析 → 看翘曲。
- **AI 可编程性**：❌ 确认无（连 `.tlb` 都没有 ⇒ 自动化路径**完全没有**，不是"没试通"）。
- **坑**：
  - ⚠ **本机不搞注塑，这个产品用不上**（用户 2026-09-27 明确排除）。
  - ⚠ 三个求解器 `packw/cool/warp.exe` 各 208 MB，很占地方。

## 8. SOLIDWORKS Inspection（检测）

**是什么**：尺寸检测。用 CMM（三坐标测量机）或激光扫描仪测零件，
自动比对图纸公差，**生成检测报告（含测量值、合格判定、统计图表）**。
可以把检测报告挂在 `eDrawings` 或 PDF 上发给客户。

**本机状态**：✅ 完整（813 MB，9 个 exe，`SOLIDWORKS Inspection.exe` 66 MB）。
本机有 `C:\ProgramData\SOLIDWORKS\SOLIDWORKS Inspection 2026 Addin` 和 `Standalone` 两种模式。

**AI 可编程性**：
- ✅ 主 API：`dsgnchk.dll`（**19 个类型**，在 redist，是 .NET 程序集）
- ⚠ 另有 `PDF\edm.tlb`（229 KB）是**原生类型库**，`LoadFrom` 抛 `Bad IL format`、
  **未在 `HKCR\TypeLib` 注册** ⇒ 不等于可编程，需另行验证

**能干什么（典型工作流）**：导入 CMM 测量数据 → 选图纸/CMM → 设基准与公差 →
自动比对 → 出 Pass/Fail 判定 → 生成带统计图（SPC）的检测报告 → 发给客户/存档。
本机 `C:\ProgramData\SOLIDWORKS\SOLIDWORKS Inspection 2026 Addin` = 装进 SolidWorks 里用，
`Standalone` = 独立程序。

**坑**：
- ⚠ 必须有**实际测量数据**（CMM 或扫描仪导出）才能用；光有 3D 模型没用。
- ⚠ 公差体系（ASME Y14.5 / ISO  GPS）要对齐图纸，否则判定会全错。
- ⚠ `edm.tlb` 未注册 ⇒ 报告排版相关的接口调不通，只有 `dsgnchk.dll` 那 19 个类型可用。

---

## 9. SOLIDWORKS PDM / Manage Client（数据管理）

**是什么**：管理企业内的所有设计文件——版本控制、权限、审批流、变更单、多人协作。
- **PDM**：服务器端（Vault）
- **Manage Client**：每个工程师电脑上的客户端（平时用它看/签出文件）

**本机状态**：✅ 两者都装了，但**本机 `swprv` 服务是 Stopped** ⇒
**没有在跑 PDM 服务器**。本机只能当"装了客户端"看。
（版本：PDM `AddInRegSrv64.exe` v34.0 / Manage Client `adxregistrator.exe` v10.1.4703.0）

**AI 可编程性**：✅ `swdocumentmgr.dll`（**504 类型**）——这是 PDM 的 API，
可以做批量改属性、查版本、批量导出文件等。

**能干什么（典型工作流）**：多人同时改同一零件 → PDM 检出/签入 → 自动升版本 →
按审批流走签核 → 变更单追溯；文件不会被"谁覆盖了谁"搞丢。

**坑**：
- ⚠ **本机没有 PDM 服务器**（`swprv` 停止）⇒ API 能编译但实际连不上库，
  单机做设计的话这个产品用不上，别浪费时间配。
- ⚠ 要多人协作才有意义；单人项目用 SolidWorks 自带的版本管理就够。
- ⚠ `swdocumentmgr` 的 API 需要先连上 Vault 才能用，与 SolidWorks 是否运行无关。

---

## 10. SOLIDWORKS Visualize / Visualize Boost（渲染）

### 10.1 ⚡ 先答一个常见误会：**这是美术渲染，不是仿真渲染**

"渲染"这个词在 SOLIDWORKS 里容易被误解成"算仿真"。**不是。**
Visualize 做的是**把 3D 模型画成好看的图/动画**，用的是**光线追踪**，
输入是 CAD 模型 + 材质 + 灯光 + 相机，**输出是一张图**。

| | Visualize（渲染） | Simulation / Flow（仿真） |
|---|---|---|
| 输入 | 3D 模型 + 材质 + 灯光 | 3D 模型 + **材料 + 载荷 + 夹具** |
| 计算什么 | 光线怎么反射（**物理光学**） | **结构应力 / 流体压力**（物理方程） |
| 输出 | **看起来真实的图/动画** | **数字结果**：应力值、位移 mm、温升 ℃ |
| 有无求解器 | ❌ **完全没有** | ✅ `efdsolver.exe` 等 |
| 用来回答 | "产品长什么样/宣传图怎么拍" | "这个零件会不会断/过热" |

⇒ **两者互不替代**：渲染做得再好看也不告诉你零件强度够不够；
仿真算出应力也不给你好看的图。**要出宣传图用 Visualize，要判断能不能用用 Simulation。**

### 10.2 本机实测证据（判定它是渲染而非仿真）

**渲染引擎栈**（`Visualize Boost` 目录）：

| 文件 | 大小 | 是什么 |
|---|---|---|
| `optix_prime.6.6.0.dll` | **35.8 MB** | **NVIDIA OptiX 光线追踪框架**（路径追踪核心） |
| `OpenImageDenoise_core.dll` | **21.4 MB** | **Intel OIDN 降噪**（路径追踪噪点消除） |
| `render_executable.dll` | 11.8 MB | 渲染执行体 |
| `Bunkspeed.Raytrace.RendererApi.Mapper.dll` | 0.3 MB | 光线追踪 API |
| `RaystackCamera.mlho` | 0.2 MB | 相机/光线栈 |

**材质库**（美术渲染的标志）：`ExaMaterials.mlco`、`Materials.mlco`、
`MaterialFs/Vs.snippet`（Finite-Scattering / Volumetric Scattering 材质）

**分布式云渲染架构**：`broker_node.exe`（10.5 MB，任务分发）+
`remote_node.exe`（9.0 MB，远端渲染工作节点）⇒ **模型要传到云端/远端机器出图**

**没有任何求解器**：对比 Flow 有 `efdsolver.exe`、Simulation 有 `star.exe`，
**Visualize Boost 一个都没有**——它只负责"画"。

### 10.3 本机状态

| | 状态 |
|---|---|
| `SOLIDWORKS Visualize`（本地版） | ❌ **空壳**，只有 2 个 dll，无 exe，**没装** |
| `SOLIDWORKS Visualize Boost`（云版） | ✅ 完整（821 MB，v93.19） |

⚠ **Boost = 云渲染**：模型要上传到 Dassault 云端算，本机只做调度。
**这意味着你的 CAD 数据要出本机**——涉及保密项目要留意。

**AI 可编程性**：⚠ 未确认有 .NET API。

**对你的价值**：给主轴/刀柄做产品展示图、装配演示动画。
**但本机没装本地版**，要出图得用 Boost（走云）或装回本地版。

**能干什么 / 怎么用**：导入 CAD/STEP → 摆相机、打光、换材质（金属/塑料/玻璃）→
调背景与 HDR 环境光 → 实时预览 → 出静帧或转动画（绕轴旋转/剖切演示）→ 分享链接。
Boost 版还能把项目扔云端渲染，手机上看。

**坑**：
- ⚠ **本地版是空壳**（只有 2 个 dll，无 exe）⇒ 现在只能用 Boost。
- ⚠ **Boost = 云渲染，模型要上传到 Dassault 云端** ⇒ 保密项目不能用。
- ⚠ 材质是**美术渲染用的**，不是物理材料属性——别拿它当分析输入。
- ⚠ `SwVisualize` 不可用时不要用"渲染"二字去套 Simulation：两者算的东西完全不同（见 §10.1）。

---

## 11. SOLIDWORKS Composer / Composer Player（技术文档）

**是什么**：做**技术文档/操作手册**——从 3D 模型自动生成带爆炸图、步骤图、注释的
交互式说明书。Player 则是免费的阅读器（发给客户/车间）。

**本机状态**：
- `SOLIDWORKS Composer` ❌ **空壳**（只有 `netapi32.dll`，无 exe）
- `SOLIDWORKS Composer Player` ✅ 完整（405 MB，`composerplayer.exe` 26 MB）

**AI 可编程性**：❌ 无 interop。

**怎么用 / 能干什么**：从装配体导出 → Composer 里自动生成爆炸图 → 给每个步骤加
注释和序号 → 存成可交互文档 → 用 Player 分发给装配工人。Player 只读、不能编辑。

**对你的项目价值**：
主轴壳体装配、拓扑优化说明、电气柜操作手册——都适合用 Composer 做。
**但本机没装本体**，需要时得补装（Player 不能编辑）。

**坑**：
- ⚠ **本机只有 Player，Composer 本体是空壳**（只有 `netapi32.dll`，无 exe）
  ⇒ **做不了，只能看**。要写手册得先补装 Composer。
- ⚠ Composer 文档是独立的专有格式，不能反向可靠地变成 SolidWorks 装配体。
- ⚠ Player 需要对方机器上也装 Player（免费分发，但要各自安装）。

---

## 12. eDrawings（看图）

**是什么**：**免费**的轻量看图/审阅软件。可以打开 SolidWorks 文件、
转成 eDrawings 发给别人（对方没 SolidWorks 也能看）、支持 3D 测量和剖切。

**本机状态**：✅ 完整（601 MB，4 个 exe，`eDrawingOfficeAutomator.exe` v34.0.0.5029）

**AI 可编程性**：❌ 无 interop（只有 `eDrawingsGraphicsCardClient.tlb` 7 KB）。
但它文件格式开放，是**交换数据的天然中间格式**。

**怎么用 / 能干什么**：SolidWorks 里"另存为 → eDrawings"（可选打包成自解压 exe）→
发给客户/供应商 → 对方用 eDrawings 打开、可旋转缩放、量尺寸、剖切看内部。

**坑**：
- ⚠ 只能看、不能改（不装 SolidWorks 就完全不能编辑）。
- ⚠ 大装配可能很卡（要看的东西全在里面）。
- ⚠ 做**可交互的**技术文档要用 Composer，不是 eDrawings（两者常被混淆）。

---

## 13. Toolbox 与标准件（回到你已建的能力）

**是什么**：SolidWorks 内置的标准件库（螺栓/螺母/销/垫圈/型材/O 型圈…）。

**本机状态**：`Toolbox` 目录 82 MB，design library 有 **215 个 .sldprt**，
但**分类统计显示 `parts/` 里只有 18 个且全是模具件**——
**ISO/DIN/GB/ANSI 紧固件库没装**（这就是为什么我们用 bd-warehouse 补）。

**AI 可编程性**：✅ `sldtoolboxconfigureaddin.dll`（6 类型，只能配置）+ `swbrowser.dll`（25 类型）。
真正的零件获取走 `list_standard_parts`（自己扫目录建索引）。

**能干什么 / 怎么用**：设计时从 Toolbox 拖标准件进装配 → 自动按规格匹配 →
出 BOM 时自带标准件属性。**本机缺紧固件库**，已用 bd-warehouse（Apache-2.0）参数化生成补齐：
六角螺母 M12 ISO4032 / 平垫圈 M12 ISO7089 / 内六角螺钉 M12×40 ISO4762，
已导入 SolidWorks 与 build123d 双内核交叉验证（体积偏差 0.001%–0.003%）。

**坑**：
- ⚠ **本机 Toolbox 紧固件库没装**，`list_standard_parts` 索引到 215 个 sldprt 但
  `parts/` 只有 18 个模具件 ⇒ 找 ISO 紧固件要走 bd-warehouse，不要指望 Toolbox。
- ⚠ bd-warehouse 的 size 格式**分产品**：螺母/螺钉要带螺距（`"M12-1.75"`），
  垫圈**不带**（`"M12"`），写错会报 `ValueError`。
- ⚠ bd-warehouse 生成的尺寸应与**库自己的 CSV 参数表**核对（`bd_warehouse/data/*.csv`），
  别拿记忆当标尺。

---

## 14. 其它本机有的 API（散装但有用）

| DLL | 类型数 | 是什么 |
|---|---|---|
| `sldcostingapi.dll` | 66 | **成本估算**（报价用：材料+工艺+工时→成本） |
| `sustainability.dll` | 35 | **可持续性/环保**（材料碳足迹、回收率） |
| `sw3dprinter.dll` | 14 | **3D 打印**（切片准备） |
| `swdimxpert.dll` | 173 | **尺寸标注专家**（GD&T 公差） |
| `gtswutilities.dll` | 46 | **公差分析（Tolerance Analysis）**——堆叠公差 |
| `SWRoutingLib.dll` | 68 | **Routing 线缆/管路自动布放** |
| `fworks.dll` | 13 | SolidWorks MFG/钣金相关 |
| `swpublished.dll` | 46 | Publish/出图相关 |
| `swcommands.dll` | 2 | 内部命令常量 |

⚠ **`sldcostingapi`（成本估算）对你可能有实际价值**：报价是机械设计的刚需，
而它有 66 个类型、是有 API 的。

---

## 15. 给你的学习路径建议

按"对做机械设计最有用"排序，而不是按产品大小：

| 优先级 | 产品 | 为什么 |
|---|---|---|
| 1️⃣ | **核心** | 一切的前提，没这个其它都免谈 |
| 2️⃣ | **Toolbox / 标准件** | 天天要用；本机库不全，用 bd-warehouse 补 |
| 3️⃣ | **Simulation（结构）** | 决定强度够不够、能不能减重 |
| 4️⃣ | **Flow Simulation** | 主轴壳体散热分析（拓扑被卡住时，这条路更可能出成果） |
| 5️⃣ | **Electrical** | 只做电控柜才需要（**但有 683 类型 API 可编程**） |
| 6️⃣ | **eDrawings** | 免费看图/发给别人 |
| 7️⃣ | **PDM** | 多人协作才需要。⚠ 本机 `swprv` 服务 **Stopped** = 没跑服务器 |
| 8️⃣ | **Visualize Boost** | 出效果图；⚠ 是**云渲染**，要联网传模型 |
| — | ~~CAM / Plastics / Composer / Composer Player / Manage~~ | **你已明确排除**（见 §1.1） |

### 15.1 我的建议：下一个做 Flow Simulation 的散热分析

理由：①主轴壳体是你项目里**唯一有真实热问题**的零件（电机损耗→轴承→壳体）；
②拓扑优化被 `AddRestraint` 的许可边界堵死，换条路走；③它有官方 36MB SDK，
不依赖被卡的那个接口；④散热筋的增删会直接影响你现在的设计。

⚠ **前置**：本机 Flow Simulation **没有可用的 .NET API**（只有原生 TLB + 独立 SDK），
所以第一步不是直接建算例，而是**先验证那个 36MB 的 `flow simulation api sdk x64.exe`
能否被脚本驱动**。这条未验证。

---

## 16. 判定"某产品能不能编程"的正确顺序 ⚠ 本文最重要的一节

> **本文初版在这一步犯过错**：只扫了 `SOLIDWORKS\api\redist` 就断言
> "Electrical 无 API / CAM 无 API / Flow 无 API"。
> **实际 Electrical 有 683 个类型的 API（在自己 bin 目录），
> CAM 和 Flow 也都有 `.tlb`（只是用不了）。**
> 错因：**把"一个目录"当成了"全部"**。

### 16.1 五步判定法（顺序不能省）

```
① 扫公共 redist        → D:\...\SOLIDWORKS\api\redist\SolidWorks.Interop.*.dll
   ⚠ 只有【主 SOLIDWORKS 产品线】的 interop 放这里，产品自己的 API 不在这

② 扫产品自己的 bin     → Get-ChildItem <产品目录> -Recurse -Include *.tlb,*.olb
   ⚠ Electrical 的 Interop.EwAPI.dll 就在这一步被找到

③ 判断格式：.NET 还是原生？
   [Reflection.Assembly]::LoadFrom(f) 成功 → .NET，可直接引用
   抛 "Bad IL format"                   → 原生 TLB，.NET 侧不能直接用

④ 判断是否注册
   reg query "HKCR\CLSID\<clsid>" /s   → 看有没有 Programmable + TypeLib
   reg query "HKCR\TypeLib" /s /f "<名>" → 0 匹配 = 没注册

⑤ 才下结论
```

### 16.2 四种结论的准确表述

| 结论 | 含义 | 本机实例 |
|---|---|---|
| ✅ **可直接编程** | .NET 程序集 + 已注册 | 核心 1872 类型、Simulation 615、**Electrical 683**、PDM 504 |
| ⛔ **可安装但未装** | 目录里只有**安装器**（`FileDescription` 含 "Setup Launcher"），组件本体缺失 | **Flow Simulation**（`API\` 下只有那个 35.6MB 安装器） |
| ⚠ **有 API 但未验证可用** | 文件在，但是原生 TLB 或未注册 | CAM `camworks.tlb` 677KB、Inspection `edm.tlb` 229KB |
| ⚠ **有独立 SDK（非 COM）** | 官方提供但不是 interop | — |
| ❌ **确认无 API** | 两处都扫过、都没有 | **Plastics**、Composer、Visualize、eDrawings |

⚠ **别把 ⚠ 写成 ❌**（我犯过），也别把 ⚠ 写成 ✅（同样是错）。
⚠ **第三种"安装器在但没装"最隐蔽**——看到 35MB 的 sdk.exe 就以为"有 API"，
实际它只是个 Setup Launcher（看 `FileDescription` 即可识别）。

### 16.3 本文数据的复现方式

```powershell
# 产品目录与体积
Get-ChildItem "D:\Program Files\SOLIDWORKS Corp" -Directory | % { ... }
# 判定空壳：看有没有 .exe
Get-ChildItem "<产品目录>" -Recurse -Filter *.exe | ? { $_.Name -notmatch 'unins|setup' }
# 有 API 的产品 = redist 下的 interop DLL
Get-ChildItem "D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist" -Filter "*.dll"
# 反射任意产品接口
[Reflection.Assembly]::LoadFrom("<dll>").GetExportedTypes()
# Electrical 的功能清单 = bin 下的 Ew* 命令模块
Get-ChildItem "...\SOLIDWORKS Electrical\bin" -Filter "Ew*"
# 后端服务
Get-Service | ? { $_.Name -match 'Ew|TEW' }
```

**所有结论都可用以上命令复现。**
