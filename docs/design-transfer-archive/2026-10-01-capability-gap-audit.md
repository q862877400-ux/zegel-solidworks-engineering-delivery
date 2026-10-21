# SolidWorks 自动化项目 · 能力空白审计报告

**版本**：v1 · 2026-10-01
**作者**：评审分支（另一个会话）
**落点**：`D:\AI\SW-transfer\`（**两个 git 仓库之外**，不会被 `git add -A` 扫到）
**⚠ 本报告只做只读审计**：未改动任何仓库文件、未连接 SolidWorks、未提交任何东西。

> **本报告是自包含的** —— 读者不需要本项目的任何前情。
> 需要先读的只有 §一（背景与术语表）；§二 讲方法与我踩过的错（**它决定你该怎么信后面的数字**）。

---

## 一、背景（读者须知）

### 1.1 这是什么项目

一个把 **SolidWorks 桌面自动化**做成可交付能力的项目。核心主张是：

- **不发明，只缝合** —— 每个能力要能指认出处（官方 API / 开源项目 / 本项目既有模式）
- **签名以官方三源互证为准**，冲突时以**出厂类型库反射**裁决
- **每个能力带验证等级**（五级枚举），`verified` 必须有**真机**证据

### 1.2 两个仓库的位置

| 路径 | 是什么 | 说明 |
|---|---|---|
| `C:\swprojects\sw-skill-fork\` | **代码仓库** | 实际实现；当前 **282 个提交**（相对上游 **281 个**）|
| `D:\AI\SW\` | **工作区仓库** | 报告、证据、规格、日志；不是代码 |

**代码仓库当前规模**：`scripts/` **130 个模块** · `subskills/` **5 个子技能** ·
`capabilities.yaml` **38 条能力**（`verified` 32 · `stitched` 5 · `not_implemented` 1）·
MCP 工具声明 **41 条** · Spec Kit 规格 **83 个**。

**本机环境**：SolidWorks **2026 SP4.1**（`RevisionNumber = 34.4.1`）· 中文界面 · Windows · Python 3.14.7。

### 1.3 ⚠ 术语表（**不先读这一节，后面的数字会读错**）

本项目的覆盖度台账用**三个不同的百分比**，含义**完全不同**，**合并就会误导**：

| 列名 | 含义 | 怎么算的 |
|---|---|---|
| **编目录**（`hit`）| 该族成员里，有多少**名字在代码里出现过** —— **含只写在 API 名登记表里的** | 静态文本匹配 |
| **护栏可调**（`gated`）| 登记在某模块的能力表里，**且有可达调用路径**（形如 `_checked(target, member, …)`）| 静态可达性 |
| **直接调**（`used`）| 静态上**看得见字面量**的调用（`get_com_member(x, "Name")` 或点调用）| 静态字面量匹配 |

**两个关键性质**：
- **护栏可调 ⊇ 直接调**；差值来自「调用处传的是变量」——
  模块写成 `_checked(target, member, …)` 时，静态归因看不到字面量。
  ⇒ ★ **「直接调」系统性低估，不是精确值。**
- ★★ **「编目录」高不代表能用。** 台账原文：
  > 「早先版本只报一个触及率，于是『族触及率 100%』是靠**把名字列进登记表**达成的 ——
  > 那证明的是『这份 API 清单做完了』，**不是『这些 API 都能用了』**。」

---

## 二、方法与可信度（**含我踩过的三次错**）

### 2.1 方法

**不靠印象，问项目自己的台账**：`C:\swprojects\sw-skill-fork\docs\family-coverage.json`
—— 881 个官方接口族的逐族覆盖，**由静态解析生成**（未执行仓库代码、未连 SolidWorks）。

再对可疑项**回代码核**（因为台账的「直接调」会低估）。

### 2.2 ⚠ 我在同一类错误上**连续犯了三次**（**这影响你怎么读这份报告**）

```
① 只搜 scripts/sw_*.py
   ⇒ 漏了 scripts/ 下 49 个**不带 sw_ 前缀**的模块（如 sketch_relations.py）
   ⇒ 据此断言「草图关系不能跨零件」—— 错，被业主纠正

② 正则里缺关键词（攻丝/螺纹孔/thread_hole）
   ⇒ 漏了 subskills/solidworks-threaded-holes/
   ⇒ 据此断言「螺纹孔是真缺口」—— 错，它 status: stable 且 SW2026 实测过

③ ★ 用 Select-Object -First 22 **截断输出**
   ⇒ 探针其实**搜到了** subskills，是我没往下看

④ ★★ 根因：**用一个具体 API 名（HoleWizard5）的 0 命中，去推断"一整类能力"的缺失**
   ⇒ 而官方**可能有多条路**（该子技能走的是「底孔 + Metric Thread 特征」，完全绕开 HoleWizard5）
```

**⇒ 所以本报告的每一条「零命中」结论，都补了「回代码核」这一步**，
并且 §十一 专门写了**读表纪律**。**请照样怀疑本报告的任何单点结论。**

---

## 三、全局三列数字（2026-09-29 台账）

```
881 个官方接口族 / 15,466 个官方成员

  编目录    15,466   (100.0%)
  护栏可调  10,573   ( 68.4%)
  直接调     2,605   ( 16.8%)

★ 编进了目录、但从没被**直接调用**的成员 = 12,861 个（83.2%）
```

**可重跑**：
```powershell
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));print(len(d),sum(r['members'] for r in d),sum(r['hit'] for r in d),sum(r['gated'] for r in d),sum(r['used'] for r in d))"
```

### 3.1 ⚠ 顺手抓到一处**文档不一致**（已查清）

| 来源 | 数字 |
|---|---|
| `family-coverage.json`（实际数据） | 881 族 · **15,466** 成员 · 编目录 **15,466（100%）** · 直接调 **2,605（16.8%）** |
| `family-coverage.md` 的**表格**（881 行） | 与 json **一致**（如 `ISldWorks` 284/284 = 100%）|
| ★ `family-coverage.md` 的**正文段** | 「**16,615** 个成员里，编入目录 **12,870（77%）**、真调用 **2,636（16%）**」 |

**两个文件的 mtime 完全相同**（2026-09-29 20:19:00），但**数字对不上**。
**判定**：md 的**正文段是过时散文**（旧一代数据），**它与自己文件里的表格都矛盾**；
**以 json 与 md 表格为准**。
⚠ 那 12,870（77%）**具体是哪个口径，我没查出来** —— 按本项目纪律，记「**来源不明**」，不猜。

---

## 四、发现 A：**真·零覆盖 = 0 个族**

**`hit == 0` 且 `members > 0` 的族：0 个。**

⇒ **881 个官方接口族，名字层面全部编进了目录。**
⇒ **所以「还有哪个功能连名字都没编」这个问法，答案是「没有」。**

**可重跑**：
```powershell
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));z=[r for r in d if r['hit']==0 and r['members']>0];print(len(z))"
```

---

## 五、发现 B：**263 族 / 2,145 个成员「编进目录、从没直接调」**

**按域归口**（`hit>0` 且 `used==0`）：

| 域 | 族 | 成员 |
|---|---|---|
| 全量索引/sldworks | 102 | **841** |
| ★★ **仿真（需许可证）** | **36** | **642** |
| 路由/Composer/PDM | 52 | 233 |
| ★ **swdimxpert**（DimXpert 自动公差）| 42 | **153** |
| ★ **sldcostingapi**（成本细分）| 7 | **121** |
| swpublished | 11 | 75 |
| swmotionstudy | 7 | 51 |
| SWRoutingLib | 3 | 14 |
| dsgnchk（Design Checker）| 1 | 8 |
| sldtoolboxconfigureaddin | 2 | 7 |
| **合计** | **263** | **2,145** |

---

## 六、发现 C ★★★ 仿真域：**36 族 / 642 个成员，直接调全为 0**

```
ICWDynamicStudyOptions               119   ICWStaticStudyOptions                 57
ICWFrequencyStudyOptions              33   ICWDropTestSetup                      30
ICWFatigueStudyOptions                27   ICWBeamBody                           27
ICWLoadCaseManager                    27   ICWBucklingStudyOptions               26
ICWTopologyStudyManager               24   ICWThermalStudyOptions                22
ICWMultipleContactSetsEditManager     22   ICWContactManager                     20
ICWCable                              19   ICWEdgeWeldConnector                  19
ICWMultipleComponentContactsEditManager 18 ICWDynamicInitialCondition            15
ICWStudyResultOptions                 14   ICWJoints                             13
ICWSpotWeldConnector                  11   ICWDropTestStudyOptions               10
ICWSolidBody                          10   ICWDampingOptions                      8
ICWRigidConnector                      8   ICWTopologyMinimizeMaximumDisplacementGoal 8
ICWResultsProbeManager                 7   ICWSolidManager                        7
ICWTopologyStudyOptions                7   ICWDropTestResultOptions               6
ICWRunSpecStudiesRunMeshOptions        6   ICWBeamManager                         4
ICWDistributedMass                     4   ICWLinkConnector                       4
ICWShellManager                        4   ICWSolidComponent                      3
ICWRunStudiesResults                   2   ICWTrendTracker                        1
                                    ── 合计 36 族 / 642 成员
```

**⚠ 这意味着什么**：项目对外把 `simulation_and_fea` 标为 **`verified`（`verified_versions = ['2026']`）**，
但那条 `verified` **只覆盖 `ICWStudy` 的一小部分**；
**动态 / 静力选项 / 频率 / 跌落 / 疲劳 / 梁 / 载荷工况 / 屈曲 / 拓扑管理器 / 热 / 接触 / 点焊 / 线缆 / 阻尼 / 分布式质量 —— 全部没有直接调用。**

**⇒ 建议**：`simulation_and_fea` 的 `limitations` 应当**写明覆盖到哪一族为止**，
否则「仿真 verified」这个结论**比实际证据宽**。

**可重跑**：
```powershell
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));c=[r for r in d if r['family'].startswith('ICW') and r['used']==0];print(len(c),sum(r['members'] for r in c))"
```

---

## 七、发现 D ★★★ `ISafeArrayUtility` —— **官方给了工具集，我们在手搓**

```
ISafeArrayUtility    21 个成员    编目录=21    护栏=21    **直接调 = 0**
```

**为什么这条特别重要**：这个项目的**已知事实**里，有一长串 BYREF / 数组 / VARIANT 的坑：

```
事实 12  空 Dispatch 参数包 VARIANT(VT_DISPATCH, None)
事实 33  SelectByID2 / Select4 的 Callout 必须传 VARIANT(VT_DISPATCH, None)
         —— 传 None 得到「类型不匹配 0x80028CA0」，而该错误**看不出是 Callout 的问题**
事实 68  Object& 出参必须填（VT_BYREF | VT_VARIANT）
轮 081   fix: AddRelation 必须包 VARIANT(VT_ARRAY, …)
```

**⇒ `ISafeArrayUtility` 是官方为这类问题提供的 21 个成员的工具集，而项目一个没用，全靠手搓 `VARIANT(...)`。**

**⇒ 建议**：这是一条**高杠杆**的补充 —— 它可能一次性替掉一批手搓代码与对应的坑。

---

## 八、发现 E：25 个**零调用、且与本项目能力面相关**的族

| 族 | 成员 | 为什么值得看 |
|---|---|---|
| `IPropertyManagerPage2Handler9` | 37 | add-in 的 PropertyManager 回调 |
| **`IRayTraceRendererOptions`** | **36** | ★★ **渲染选项** —— 渲染链的另一半 |
| **`ISwScene`** | **35** | ★★ **场景（背景 / 环境 / 地板 / 光源）** |
| **`ITessellation`** | **28** | 三角剖分 / 网格化 ⇒ 几何核验与导出 |
| **`IDragOperator`** | **25** | ★★ **拖拽 + 碰撞检测** —— 装配体干涉的官方做法 |
| `IFrame` | 25 | SW 主窗口框架（add-in 用）|
| **`ICostAnalysisMachining`** | **24** | ★ **机加工成本** |
| `IRouteManager` | 21 | 管线（需加载项）|
| `ICommandManager` | 21 | add-in 命令管理 |
| **★ `ISafeArrayUtility`** | **21** | 见 §七 |
| `ITabAndSlotGroupData` | 21 | 钣金 tab/slot |
| **`ICostAnalysisSheetMetal`** | **20** | ★ 钣金成本 |
| **`IMBD3DPdfData`** | **20** | ★★ **MBD / 3D PDF** |
| **`IPrintSpecification`** | **20** | ★ **打印 / 出图规格** |
| `ISimulationMotorFeatureData` | 20 | 仿真马达 |
| `ICostAnalysisPlastic` / `Structural` / `3dPrinting` / `Casting` | 15/15/14/12 | ★ **成本分析只做了通用那块** |
| `IMBDSTEP242Data` · `IPMIFrameData` | 6 · 6 | ★ **MBD / PMI（三维标注）** |
| `IAutoRoute` · `IElectricalRouteProperty` | 7 · 5 | 电气布线 |
| **`IRayTraceRenderer`** | **7** | ★ **光线追踪渲染器**（见 §九）|

---

## 九、发现 F：「**连计划都没有**」的（不在任何文档、任何规划里）

| 项 | 规模 | 现状 |
|---|---|---|
| **MBD / 3D PDF / PMI** | `IMBD3DPdfData` 20 + `IPMIFrameData` 6 + `IMBDSTEP242Data` 6 = **32** | ❌ 零调用，**任何文档里都没提过** |
| **`ISafeArrayUtility`** | 21 | ❌ 零调用，**而它该干的事我们一直在手搓** |
| **成本分析 6 个细分族** | 24+20+15+15+14+12 = **100** | ❌ 只做了通用那块 |
| **渲染两半** | `IRayTraceRendererOptions` 36 + `ISwScene` 35 + `IRayTraceRenderer` 7 = **78** | ❌ 零实现 |
| **`IDragOperator`** | 25 | ❌ 零调用 |
| **`ITessellation`** | 28 | ❌ 零调用 |
| **`IPrintSpecification`** | 20 | ❌ 零调用 |
| **仿真 13 类研究选项** | **642** | ❌ 零调用（对外却标 `verified`）|
| **DimXpert** | 42 族 / **153** | ❌ 零调用 |
| **Design Checker**（dsgnchk）| 8 | ❌ 零调用 |
| **`SOLIDWORKS Visualize`** | 本机已装 | ❌ **仓库 0 命中** |

### 9.1 ★ `SOLIDWORKS Visualize` 的细节（本机实测）

```
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS Visualize\
  SLDWORKSVisualize.exe                 主程序
  ★★ OfflineRendererConsole.exe        **命令行离线渲染器**（30,808 B · 2026-08-14）
  ★  OfflineRenderer.exe               离线渲染器
  SWVisualize.Queue.exe                队列
  Bunkspeed.Exchange.dll               交换（**Bunkspeed** = 达索收购的专业渲染内核）
  SWVisualize.Exchange.PluginHost.exe  SolidWorks ↔ Visualize 交换插件
  AMD.ProRender.dll · amd_fidelityfx_vk.dll        GPU 渲染后端
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS Visualize Boost\
  broker_node.exe · remote_node.exe                ★ **分布式渲染节点**
```
**实测（有超时、不碰 COM）**：
```
OfflineRendererConsole.exe --help ⇒ 15 秒内自己退出（退出码 -1），输出：
    CreateContext - type=Bunkspeed.Applications.OfflineRendererConsole.IOfflineRendererConsoleBootstrapContext
    CreateContext - type=Bunkspeed.Rendering.OfflineRendererApplication.Manage.IOfflineRendererShellContext
    CreateContext - type=Bunkspeed.Applications.OfflineRendererConsole.IOfflineRenderingConsoleDocumentContext
    ★★ Cannot find input folder for rendering: ''
⇒ 它**要一个「输入文件夹」**，但**参数形态未定**：
  试了 4 种（位置参数 / `/input:` / `-i` / `/folder:`）都还是 `''`
  ⇒ 按**已知事实 53**（同一启发式连续修补 ≥3 次就停手）**停手，记「查不到」**
⚠ 本机**没有 PhotoView 360 目录** ⇒ 装机的是 **Visualize**
```
**⇒ 「渲染效果图」这条路存在且可自动化，但从没被发现。**

---

## 十、发现 G：一处**台账口径的活标本**（教学价值）

```
docs/family-coverage.md 里写着：
  | 全量索引/sldworks | `IRayTraceRenderer` | 7 | **7** | **100%** |
⇒ 但**回代码核**：这个族 7 个成员**一个都没实现**（含 RenderToFile / InvokeFinalRender）
⇒ 那个「100%」是**编目录口径** —— 名字在 sw_api_sldworks.py 的接口名字符串列表里
```

**这正是台账自己警告的那件事**（§1.3 引文）。
★ **`IRayTraceRenderer` 就是那个「100%」的活标本** —— 建议拿去当教学例子。

---

## 十一、⚠ **读这张表的三条纪律**（否则必误判）

**① 三列不可合并。**
「编目录 100%」只证明「这份 API 清单做完了」，**不等于「这些 API 都能用了」**。

**② 「直接调 = 0」≠「没实现」** —— 反例就在表里：
```
IGtolFrame    9 个成员    编目录=9    护栏=9    **直接调 = 0**
⇒ 但项目对它**确实有实现**：scripts/sw_gtol.py 的 add_gtol_indicator 走 IGtolFrame.AddIndicator
⇒ 之所以静态看不到，是因为**成员名通过变量传入**
```
**⇒ 判「有没有」必须回代码核，不能只读这张表。**

**③ 台账是静态解析的** —— 它**不执行代码、不连 SolidWorks**。
所以它证明的是「**静态可见性**」，**不是运行期可用性**。

---

## 十二、每条结论的可重跑命令

```powershell
# ① 全局三列
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));print(len(d),sum(r['members'] for r in d),sum(r['hit'] for r in d),sum(r['gated'] for r in d),sum(r['used'] for r in d))"

# ② 真·零覆盖（应为 0）
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));print(len([r for r in d if r['hit']==0 and r['members']>0]))"

# ③ 编进目录但没直接调的族与成员数
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));z=[r for r in d if r['hit']>0 and r['used']==0];print(len(z),sum(r['members'] for r in z))"

# ④ 仿真域 ICW* 的零调用规模
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));c=[r for r in d if r['family'].startswith('ICW') and r['used']==0];print(len(c),sum(r['members'] for r in c))"

# ⑤ 逐族三列（自己筛）
python -c "import json;d=json.load(open(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json',encoding='utf-8'));[print('%-46s %4d hit=%-5d gated=%-5d used=%d'%(r['family'],r['members'],r['hit'],r['gated'],r['used'])) for r in sorted(d,key=lambda r:-r['members'])[:40]]"

# ⑥ ★ 回代码核任意一个族「到底有没有实现」（纪律 ②）
python -c "import sys,re;from pathlib import Path;R=Path(r'C:\swprojects\sw-skill-fork');n='ISafeArrayUtility';[print(p.relative_to(R),i,l.strip()[:70]) for p in R.rglob('*.py') if 'sw_api_' not in str(p) and 'workbench-ui' not in str(p) and 'sw_api_'.join([])=='' and 'sw_api_' not in p.name for i,l in enumerate(p.read_text(encoding='utf-8',errors='replace').splitlines(),1) if n in l and not l.strip().startswith('#')]"
```

---

## 十三、限度（**这份报告没证明什么**）

1. **未执行任何代码、未连 SolidWorks。** 全部结论来自静态解析 + 文件系统。
2. **「零调用」是静态口径** —— 走变量传成员名的调用**看不到**（`IGtolFrame` 是反例）。
3. **未判定"该不该做"** —— 本报告只说「没做」，**不判断优先级**。
   有些零调用族是**故意不做**的（如需许可证、需加载项、非托管 C++ 独占）。
4. **未核实许可** —— `仿真 / Routing / PDM / Costing` 等域在台账里标「需许可证」，
   **本报告没有验证这些许可证在本机是否可用**。
5. **§3.1 那处不一致的「12,870（77%）」来源不明** —— 我没查出来，**记「查不到」，不猜**。
6. **`OfflineRendererConsole` 的参数形态未定**（试了 4 种，按纪律停手）。
7. **§2.2 记录了我连续三次同类错误** —— 所以**请对本报告的每个单点结论保持怀疑**，
   用 §十二 的命令自己跑一遍。

---

## 附：一页速览

```
真·零覆盖（连名字都没编）      = 0 个族        ← §四
编进目录但没直接调            = 263 族 / 2,145 成员   ← §五
★ 仿真域（对外标 verified）    = 36 族 / 642 成员，直接调全 0  ← §六
★ ISafeArrayUtility（21）      = 官方工具集，我们在手搓  ← §七
★ 「连计划都没有」的 11 项      = 含 MBD/3D PDF 32 · 成本细分 100 ·
                                渲染 78 · Visualize（仓库 0 命中）  ← §九
⚠ 台账三列不可合并；「直接调=0」≠「没实现」  ← §十一
```
