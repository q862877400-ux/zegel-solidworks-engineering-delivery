# AGENTS.md — SolidWorks Automation Skill 完善与 Fork

> **本文件是本任务的唯一开工入口。** 任何执行者（人或 AI、含子代理）动手前必须先读完。
> 建立于 2026-09-28，基于对 18 个 SolidWorks 开源项目 + 本机两套官方 API 离线源的实地普查与核实。
>
> **本文件里的通用方法论已上移到 `~/.dsh/纪律/查证与验证.md`**（每轮自动注入）：六条铁律里的
> 「只做缝合不做发明」「签名以官方文档为准」「查不到就说查不到」「许可红线」「不实测时把验证责任转移到静态比对」
> 「验收标准写成可 grep 判据」都是跨项目通用的。
> **本文件只留 SolidWorks 专属**：工作区、官方离线源、素材库、上游结构、验收判据、停止条件。

---

## ★ 工作区（第一件事，先确认你在哪）

> **本任务在 `D:\AI\SW\`，不在 DSH 默认工作区 `D:\AI`。开工前先把工作区切过去。**

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `D:\AI\SW\` | 本文件所在 · DSH 工作区根 |  放任务产物（报告、分析） |
| `D:\AI\SW\AGENTS.md` | 本文件（唯一真源，勿复制到别处） | — |
| `C:\swprojects\sw-skill-fork\` | ★ 代码工作副本（git 仓库，唯一改代码的地方） |  |
| `C:\swprojects\sw-automation-skill\` | 上游的另一份克隆（395 文件） | ⛔ 只读对照 |
| `D:\AI\SW\AI Solidworks\` | 既有的 SolidWorks 工作区（官方文档/手册/模型） | ⛔ 只读，见其 README 约定 |

**代码工作副本现状**（2026-09-28 核实）：
```
C:\swprojects\sw-skill-fork\
  origin : https://github.com/wzyn20051216/solidworks-automation-skill   ← 刻意保留的只读锚点
  HEAD   : 8be39ac（2026-09-28）· 390 个上游文件 · MIT
```
用 `git diff origin/main` 随时看自己偏离上游多少。

>  `D:\AI\SW\AI Solidworks\README.md` 写着「所有用 AI 操作 SolidWorks 产生的东西都在这里」。
> **本任务的代码不放那儿** —— 那里是模型/截图/手册，不是 git 仓库。
> 任务报告放 `D:\AI\SW\` 下，代码放 `C:\swprojects\sw-skill-fork\`。

---

## 〇、一句话任务

> **把 `wzyn20051216/solidworks-automation-skill`（1010★）补成「官方 API 全覆盖」，
> 素材来自官方 API 文档 + 其它 18 个开源项目，最后推一个 fork。**
>
> **不是**自己写代码、不是自己跑 SolidWorks 试出来、不是模拟验证 ——
> 是用别的项目去缝合，让能力面覆盖官方 API 声明的全部功能域。

---

## 一、验收标准（做完这几条才算完成）

| # | 判据 | 怎么验 |
|---|---|---|
| A1 | 官方 API 的每个功能域在 skill 里都有对应 `scripts/*.py`，或明确标注「不覆盖 + 原因」 | 逐域打勾表，无空白格 |
| A2 | 每个新增/移植的函数都带来源头注释（owner/repo + 文件 + 行号 + 许可） | grep 抽查 10 个，100% 命中 |
| A3 | 每个新增文件里每个 COM 调用的参数顺序与类型，与官方签名逐个对齐 | 签名比对表，见 §五.4 |
| A4 | 目录结构与上游一致，新增文件落在对应位置 | 与上游目录树逐层比对 |
| A5 | 许可证无越界：AGPL/GPL/无许可/全版权保留的没有被抄进代码 | 逐文件对照 §四 许可表 |
| A6 | 全文没有任何一处写着「已验证 / 实测通过 / 跑通了」 | grep 全文，这些词必须 0 命中 |
| A7 | 报告写明：补齐了什么、仍然空缺什么、为什么空缺 | `docs/harvest-report.md` |
| A8 | fork 已创建且记录清晰 |  见 §七 批准门 |

---

## 二、六条铁律

### 铁律 1 · ★★ 只做「缝合」，不做「发明」

每加一个能力，必须能指认出处。三种合法来源，缺一不可：

| 来源 | 怎么用 | 例 |
|---|---|---|
| 官方 API 文档 | 决定接口选型与参数顺序 | Simulation 域（无人提供，只能照官方签名建） |
| 其它开源项目 | 直接移植/改写，保留来源头注释 | 建视图 ← codestack；VBScript ← pengxiaoan |
| 本项目自身既有模式 | 沿用 `sw_part.py` / `sw_hole_features.py` 的写法与命名 | 新 `sw_xxx.py` 沿用 `_select_by_id` / `get_com_member` 惯例 |

⛔ 不可接受：凭印象写一个 `FeatureManager.XXX(...)` 然后「看着像对的」。

### 铁律 2 ·  可以实测，但必须先关弹窗、必须有超时

> **2026-09-29 用户撤销**：原「不实测、不模拟」条款已删除。
> 现行要求是「测，但测得安全」——理由见下。

**为什么当初要禁**：已实测证明「看起来对」和「真能跑」之间差着 4 轮返工（见 §六 事实 4），所以当时把验证责任整体转移到了静态签名比对上。

**为什么现在撤销**：本项目已产出 12 份官方 API 全量索引（792 族 / 15,466 成员）和 8 万行代码，全部只经过静态比对，从未真正跑过。静态比对查不出「参数顺序对但语义错」「返回值类型不符」「实际会抛异常」这类问题。能跑之后，验证责任回到实测，静态比对降级为前置筛查。

 现在的验证顺序：
1. **静态签名比对**（前置筛查，先过这一关）—— §五.4
2. **本机实测**（真跑）—— 用 `mcp__solidworks__*` 工具或直接调 COM
3. 两关都过，才允许在文档里写「已验证 / 实测 / 跑通 / 验证通过」

 实测的三条安全约束（不是禁止，是要求）：
- **先置 `ISldWorks.CommandInProgress = True`** —— 否则未抑制的模态对话框会
  **把会话永久挂起**（外部实证：未抑制模态框是无人值守挂起的头号原因）
- **每个 COM 调用设超时** —— COM 是 STA 且线程亲和，调用一旦开始无法强制中止，
  超时只能救「等待」，救不了线程；超时后不要重试同一进程
- **收尾必做**：`CommandInProgress = False`、释放 COM 引用、关掉自己开的文档

 仍然禁止：
| 禁止 | 说明 |
|---|---|
| 破解相关的一切 | SolidWorks-CAD / Solidworks-Crack 类（投递页、破解指南）—— 零接触 |
| 改注册表 / 全局环境变量 / 系统层 | 数据与代码分离 |
| 未经确认就 `git push` / 建 fork / 发 release | 对外发布必须先经用户批准 |
| 删用户数据 | 不可逆破坏 |

🔒 AGPL / GPL / 无许可 / 全版权保留项目仍只读思想，不抄代码不抄文本（铁律 6 不变）。

### 铁律 3 · ★ 参照上游结构，不自创结构

新增文件/目录/命名/文档格式必须落在上游已有位置（见 §三）。不新增顶层目录；确需新功能域时，按上游 `subskills/` 的既有模式扩。

### 铁律 4 · ★★ 签名以「官方文档」为准，两套都要用

**本机有两套官方离线源，各有长短，必须都查**（详见 §四.1）：
- `D:\AI\SW\AI Solidworks\官方文档\` —— CHM 解包，权威、带说明与示例、覆盖 cosworks → 查语义与用法
- `C:\swapi\` —— 结构化 markdown，适合精确查签名/枚举 → 查参数与枚举值

⛔ 不凭记忆、不凭反射猜参数、不照抄其它项目的注释。写下来之前必须先查过。

### 铁律 5 · ★ 查不到就说查不到

两套源都查不到 → 写「查不到」并停下换思路。不要用相似名字蒙混。 名字缺席 = 官方 API 里没有这个成员，不是「没写文档」。

### 铁律 6 · ★★ 许可红线，一次都不能越

见 §四.2。AGPL / GPL / 无许可 / 全版权保留的项目，只能读思想，不能抄文本、不能抄代码。

---

## 三、上游仓库结构（新增文件必须落在这里）

> 来源：工作副本本身 `C:\swprojects\sw-skill-fork\`（上游 HEAD `8be39ac`，390 文件，
> remote `wzyn20051216/solidworks-automation-skill`，2026-09-28）。
> 只读对照克隆在 `C:\swprojects\sw-automation-skill\`（395 文件）。

```
solidworks-automation-skill/
├─ SKILL.md                    ← 主技能入口（28KB）
├─ SUBSKILLS.md                ← 子技能索引
├─ capabilities.yaml           ← ★ 能力真源：原子操作 → 后端映射（8 种后端）
├─ golden-workflows.yaml       ← ★ 黄金工作流
├─ manifest.json / package.json / project.yaml / pyproject.toml
├─ install.js                  ← 安装器
├─ agents/  ai_team/           ← 智能体定义
├─ apps/desktop/               ← 桌面工作台（cad_workbench/）
├─ assets/  docs/  examples/   ← 资源 / 文档 / 8 个示例
├─ dotnet/                     ← .NET 侧
├─ mcp-server/server.py        ← MCP 服务
├─ references/                 ← ★ 知识文档（language-backend-routing / troubleshooting / export / motion-study …）
├─ scripts/                    ← ★★ 能力实现主战场，命名 sw_<域>.py
├─ subskills/                  ← ★ autocad-automation / solidworks-engineering-drawing
│                                /   solidworks-fillet-chamfer-cnc / solidworks-threaded-holes
│                                /   solidworks-vibecad
├─ tests/                      ← ★ 80+ 测试（test_*.py + solidworks_*_regression.py 两种命名）
└─ requirements{,-mesh,-occt,-pdf}.txt
```

**`scripts/` 已有能力模块**（补全时先看是否已存在，避免重复造）：

```
sw_connect  sw_preflight  sw_session  sw_part  sw_assembly  sw_drawing  sw_motion
sw_sheet_metal  sw_weldment  sw_export  sw_gear  sw_hole_features  sw_appearance
sw_delivery  sw_review  sw_document_data  sw_entity_reference  sw_import_mesh_reference
sw_macro_guard  sw_diagnostics  sw_addin_host  sw_capability_probe
backend_router  capabilities  fea_analysis  fea_convergence  advanced_geometry
advanced_geometry_ocp  advanced_surface_ocp  headless_cad_writer  headless_occt_service
dxf_preview_scene  dfm_review  dfm_profiles  drawing_spec  routing_review  cad_studio
cad_doctor  cad_diagnostics  cad_installation  stability_regression  release_check
```

**新增模块的硬性要求**
- 命名 `sw_<功能域>.py`，与既有并列。
- 顶部 docstring 写清：能力域、对应官方接口族、移植来源、许可。
- 顶部 import 照抄 `sw_connect.py` 的依赖解析模式（`try: from .x import / except ImportError: from x import`）。
- 涉及选中的操作，一律复用 `sw_part._select_by_id` / `sw_connect.get_com_member`，
  **不要**裸写 `SelectByID2`、不要裸写 `getattr(obj, name)()`。
- 补 `tests/test_<模块名>.py`（静态可跑：mock adapter，不连 SolidWorks）。

---

## 四、素材库

### 4.1  两套官方离线源（都要用，各管一头）

#### ① `D:\AI\SW\AI Solidworks\官方文档\` —— 权威原文

SolidWorks 安装自带 3 册 CHM，用 `hh.exe -decompile` 解包而成。 随安装自带，无许可风险；本机已有人做好解包与检索工具。

```
D:\AI\SW\AI Solidworks\官方文档\SWhelp\
    sldworksapi/       11,579 文件  153.7 MB   接口页(带 ~) 8,726   ← C#/C++ API 主册
    sldworksapivb6/    16,718 文件   67.4 MB   接口页        15,993  ← ★ VB6/VBA API 册
    swconst/           1,353 文件   22.4 MB   接口页           968  ← 枚举
    cosworks/             47 文件   41.8 MB   接口页            34  ← ★ Simulation（很薄，见下）
合计 29,697 文件 / 285.4 MB
```

>  重新解包的坑（`AI Solidworks\README.md` 记录）：输出目录必须不存在且路径不能带空格，
> 否则 `hh.exe` 静默失败（返回 0 个文件）。7-Zip 25.01 已移除 CHM 解码器，只有 `hh.exe` 可用。
> **不要去爬 help.solidworks.com**（403 + JS 渲染，爬下来是空壳）。

**检索工具**（已就绪，直接用）：
```powershell
.\手册\swdoc.ps1 -List                          # 三册概况
.\手册\swdoc.ps1 -Q 'FeatureCut4'               # 关键词全文检索
.\手册\swdoc.ps1 -Q 'swEndCondUpToSelection' -Max 5
.\手册\swdoc.ps1 -File 'AddComponent5'          # 按页面名定位，整页转纯文本
```
（`-File` 走 `SWhelp\<册>\<类型>~<成员>.html` 命名；`-Q` 全文 grep 后转纯文本）

> ★★ `cosworks` 册只有 47 个文件，且只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族
> （夹具/载荷/轴承载荷/位移约束等，34 个接口页 + 13 个枚举页）。
> 它薄得「刚刚好」—— 正中本机 C# 执行层烧了 24 轮的「Simulation 夹具/载荷」那个坑。
> **但它不等于 cosworks 全貌**（DLL 里是 168 接口 / 363 枚举）。
> ⇒ 深度查 CHM，广度查反射，两个都要。

#### ② `C:\swapi\` —— 结构化查询

566 类型 / 963 枚举 / 11,557 成员 / 2,839 官方示例 / 30.3MB（16,254 文件）

```powershell
python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" <子命令>
```

| 子命令 | 用途 |
|---|---|
| `member <Type> <Member>` | ★ 精确签名 + 每个参数说明（写代码前必查） |
| `type <Type> [--grep X]` | 某类型全部成员 |
| `enum <Enum>` | 枚举全部成员（★ 枚举值必须查，不许猜） |
| `find <kw> [--kind type\|enum\|member\|example]` | 全库检索 |
| `examples "<多词>"` | 找官方示例（★ Example 页比方法页有用 10 倍） |
| `domain --list` / `domain <域>` | 功能域导航（14 域，清单见 §五 步骤 1） |
| `suggest <拼错的词>` | 近似名建议 |
| `verify` | 校验功能域地图，改过就要重跑 |
| `stats` | 规模总览 |

>  `C:\swapi` 的覆盖缺口（`sw_know.py verify` 可查）—— 它只含 12 个程序集，
> **没有 `cosworks`（Simulation）**、`SWRoutingLib`、`sldcostingapi`、`fworks`、
> `sustainability`、`swdocumentmgr`、`sldtbt`。
> ⇒ 这些域必须改查 CHM 的 `cosworks` 册 + 反射。

#### ③ 反射（补 CHM 和 C:\swapi 都缺的广度）

`redist` 里的 interop DLL 没有 XMLDoc，但都是托管程序集，可直接枚举：
```csharp
Assembly.ReflectionOnlyLoadFrom(@"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\SolidWorks.Interop.cosworks.dll")
    .GetTypes()   // → 接口 / 类 / 枚举 / 成员
```
**反射是「读官方程序集」，不是「实测」，符合铁律 2。** 已核实体量：`cosworks` 168 接口 / 363 枚举 / 9,281 成员；`SWRoutingLib` 28/26/527； `sldcostingapi` 28/24/1,006；`fworks` 2/10/65。

### 4.2 其它项目（`C:\swprojects\`，共 19 个目录 = 18 个项目 + `sw-skill-fork` 自己）

> #### 🚨 目录名消歧 —— 读表前必看
>
> 本地有两个目录名只差一个词，是本项目最容易搞错的地方：
>
> | 目录 | 是谁 | 星 | 地位 |
> |---|---|---|---|
> | `C:\swprojects\sw-automation-skill\` | wzyn20051216 | 1010★ | ★★★ 本项目要完善的目标 |
> | `C:\swprojects\solidworks-automation-skill\` | djlex83 | 24★ | ★ 无关的小项目，只贡献一个 `VARIANT` 写法 |
>
> **`solidworks-automation-skill`（多一个 `solid`）是 djlex83 的 24★，不是 1010★ 那个。**
> **引用素材一律写 `owner/repo` 全名，不要只写目录名。**

| 目录 | 项目（owner/repo） | 星 | 许可 |  能补什么 |
|---|---|---|---|---|
| `codestack` | xarial/codestack | 377 |  MIT | ★★★ 建视图 / 文档 / 装配 / 导入导出 / 22 篇 troubleshooting（433 篇 md） |
| `solidworks-api` | angelsix/solidworks-api | 370 |  MIT  | ★★ SolidDNA 模板（免弹模板设置）；`References/` 见例外 |
| `mcp-server-solidworks` | eyfel/mcp-server-solidworks (SolidPilot) | 355 | 👁 AGPL-3.0 | ⛔ 只读架构思想（adapters/cad-planner/compiler/execution 四层） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 234 |  MIT | ★★ `mock-solidworks-adapter` 测试分层；`macro-generator`；5 个 .vba |
| `CSharpAndSolidWorks` | painezeng/CSharpAndSolidWorks | 171 |  MIT | ★ 几何算法（自交/凸性/面积）；38 个 .SLDPRT 测试件 |
| `Solidworks-MCP` | alisamsam/Solidworks-MCP | 143 |  MIT | ★★ 27 个 .vbs（最大 VBScript 语料）；Hub 死连接诊断 |
| `solidworks-skills` | delancy827/solidworks-skills | 115 |  MIT | ★ 交叉验证来源（「23 参数不是 17」独立佐证） |
| `sw-automation-skill` | wzyn20051216/solidworks-automation-skill | 1010 |  MIT | ★★★ 本项目目标本体（另见 §三） |
| `pySW` | kalyanpi4/pySW | 52 | 👁 GPL-2.0 | ⛔ 只读思想，不抄代码（🚫 停更 2023-04） |
| `solidworks-automation-skill` | djlex83/solidworks-automation-skill | 24 |  MIT | ★ `VARIANT(VT_DISPATCH,None)` 简洁写法（ 见上方消歧） |
| `offline-solidworks-api-docs` | pedropaulovc/offline-solidworks-api-docs | 13 | ⛔ 无许可 | ⛔ `C:\swapi` 的来源，产物同样不可再分发；只读流水线思路 |
| `solidworks-build-mechanical-models` | pengxiaoan/solidworks-build-mechanical-models | 13 | ⛔ 无许可 | ⛔ 只读思想（绕过 `SelectByID2`），不抄文本 |
| `solidworks-auto-modeling` | Sakikooooo/solidworks-auto-modeling | 8 |  MIT | ★★ `Nothing`(标量 Dispatch) vs `Empty`(Variant 数组) 规则；已验证/未验证清单 |
| `sw-ai-bridge` | Mochaxgcc/solidworks-ai-bridge | 7 |  MIT | ★ 裸传 23 个位置参数的佐证 |
| `sw-api-skill` | guoleizhen717/solidworks-api-skill | 5 |  MIT |  「>12 参数会失败」是错的，别采信 |
| `ddeng-skills` | walterkken/doc-driven-engineering-software-skills | 5 | ⛔ 全版权保留 | ⛔ 只借鉴「文档驱动目录结构」这一条方法论 |
| `q3ds-solidworks-mcp` | Bennyco86/q3ds-solidworks-mcp | 5 | 👁 AGPL-3.0 | ⛔ 只读产品设计（响应体裁剪省 token、视觉捕获） |
| `solidworks-com-automation-skill` | ZiChen-Ni/solidworks-com-automation-skill | 2 |  MIT | 最小 COM 封装；Windows 安装脚本 |
| — | `SolidWorks-CAD` / `Solidworks-Crack` | 812/287 | — | 🚫 排除：投递页 / 破解指南。不下载、不读取、不运行 |

**许可判定表**

| 标记 | 含义 | 能做什么 |
|---|---|---|
|  MIT | MIT | 可读、可抄、可改、可商用（保留版权声明） |
| 👁 AGPL-3.0 / GPL-2.0 | 传染性 | 只读思想，不抄代码、不抄文本 |
| ⛔ 无 LICENSE | 保留所有权利 | 只读思想 |
| ⛔ All rights reserved | 版权方全权 | 只读方法论，不碰文本 |
| 🚫 排除 | 恶意 / 破解 | 零接触 |

**MIT 唯一已知的例外**（`angelsix/solidworks-api` 原文照抄）：

> All files inside the References folder are property of Dassault Systemes SolidWorks Corp
> and may only be used in unmodified form in conjunction with SolidDNA.

⇒ 抄 `Templates/SolidDNA` 可以；`References/` 里的文件是达索的财产，原样用、只配 SolidDNA。

> 📌 另注：`C:\swapi` 的内容来自无许可的 `offline-solidworks-api-docs`（爬 help 站点），
> 所以 `C:\swapi` 的产物同样不可再分发进闭源产品。本机自用无碍，但 fork 发布前要意识到这点。
> `D:\AI\SW\AI Solidworks\官方文档\` 则是达索随安装自带，没有这个问题，优先用它。

### 4.3 来源标注制（每个移植函数都要有）

```python
# ── 来源 ─────────────────────────────────────────────────────────
# 仓库: xarial/codestack  (MIT License)
# 文件: solidworks-api/document/drawing/create-third-angle-views.md
# 定位: Create3rdAngleViews2 正确入口
# 官方签名依据: C:\swapi\types\IDrawingDoc\Create3rdAngleViews2.md
#              + D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\
# 本函数为静态移植，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────
```

⛔ 最后那行「未实测」标注不许删。

---

## 五、工作方法（四步法）

### 步骤 1 · 建立官方能力全景

**分两路做**（因为覆盖不同）：

**(a) 域 1–12 走 `sw_know.py`**（CHM 也有，但 markdown 更好批量枚举）
```powershell
python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" domain --list
```
**14 个域的实际清单**（`sw_know.py verify` 全部通过，2026-09-28 核实）：

| # | 域 | 查哪套源 | # | 域 | 查哪套源 |
|---|---|---|---|---|---|
| 1 | 应用与会话 | sw_know | 8 | 装配 | sw_know |
| 2 | 草图 | sw_know | 9 | 工程图 | sw_know |
| 3 | 零件特征 | sw_know | 10 | 几何与拓扑 | sw_know |
| 4 | 孔与螺纹 | sw_know | 11 | 质量属性与导出 | sw_know |
| 5 | 钣金 | sw_know | 12 | 配置·材料·自定义属性 | sw_know |
| 6 | 焊件 | sw_know | 13 | 仿真(需许可证)  | CHM + 反射 |
| 7 | 曲面 | sw_know | 14 | 路由·Composer·PDM(需许可证)  | CHM + 反射 |

 域 13 / 14 对应的程序集 `C:\swapi` 完全没有，`sw_know.py` 查不到它们的类型 → 走 (b)。

**(b) 域 13/14 + 任何 `sw_know` 报 `[SWK_NOT_FOUND]` 的接口 → 走 CHM + 反射**
```powershell
.\手册\swdoc.ps1 -Q 'ICWLoadsAndRestraintsManager'     # CHM 查语义
.\手册\swdoc.ps1 -File 'ICWLoadsAndRestraintsManager~AddBearingLoad'
# 反射 cosworks / SWRoutingLib / sldcostingapi / fworks 拿全量签名
```

**产出**：`docs/capability-matrix.md` —— 官方功能域 × 接口族 × 覆盖来源（CHM / swapi / 反射 / 无）。

### 步骤 2 · 对差：官方有 / skill 缺

把步骤 1 的清单逐项对照上游 `capabilities.yaml` + `scripts/` + `subskills/`。 不得预设任何缺口结论 —— 从零建表。

**产出**：`docs/gap-analysis.md` —— 三列表：
```
官方接口族 | 上游现状(有/无/薄) | 拟采取的来源(见步骤3优先级)
```

### 步骤 3 · 缝合（按「上游优先」）

对每个缺口逐项按这个优先级找素材，找不到才自己照官方签名建：

```
1. 上游自己已有的相邻模块        ← 最优先：保持风格一致
2. MIT 项目里现成的实现          ← 次优先：直接移植 + 来源标注
3. MIT 项目里的文档/示例         ← 照着写
4. 👁/⛔ 项目的【思想】           ← 只借思路，绝不抄文本
5. 照官方 API 签名自己写          ← 最后手段
```

**每补一项必须同时产出**：① 代码文件 ② `tests/test_*.py` ③ 来源标注 ④ `gap-analysis.md` 打勾。

### 步骤 4 · 静态自检 + 报告

```powershell
# a) 语法/导入（不执行业务逻辑）
python -m compileall -q scripts subskills

# b) ★ 签名比对表（铁律 2 认可的验证）
#    docs/signature-audit.md：逐个 COM 调用与官方签名对齐

# c) ★ 许可自检：逐文件确认来源标注的许可与 §4.2 表一致

# d) ★ 禁词自检（必须全 0）
Select-String -Path <所有新增文件> -Pattern '已验证|实测通过|跑通了|验证通过|已跑通'
```

**产出**：`docs/harvest-report.md` —— 补齐了什么、还缺什么、为什么缺。

---

## 六、已知事实（已在本机核实，不要重新推导）

> 这些是上游文档/注释里没有或写错的。写代码直接用，别再踩。

| # | 事实 | 依据 |
|---|---|---|
| 1 | 切除的正确入口是 `IFeatureManager.FeatureCut4`（27 参数），不是 `FeatureExtrusion3(Flip=true)`。用后者建出来的是「凸台-拉伸」特征名，体积恒等于原板（零体积效应） | 本机实测 + 上游 `sw_part.extrude_cut` 用 `FeatureCut4` + `swdoc.ps1 -File FeatureCut4` |
| 2 | `IFeatureManager.FeatureExtrusion3` 是 23 个参数；`FeatureExtrusion2` 已废弃被 3 取代 | `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` + delancy827 README 独立佐证 |
| 3 | ⛔ 「>12 参数 IDispatch 会失败」是错的（guoleizhen717 说法不可采信） | 23/27 参在 pywin32 迟到绑定下均正常 |
| 4 | pywin32 迟到绑定下同一成员可能是属性也可能是方法：`GetDocumentCount`、`GetMassProperties` 是属性，直接调用会 `TypeError: 'int' object is not callable`。上游已有 `get_com_member()` —— 移植代码必须沿用 | 本机实测 + 上游 `sw_connect.py:109-130` |
| 5 | 质量属性用 `IModelDocExtension.GetMassProperties2(accuracy, out status, useSelected)`；下标 0-2=质心，3=体积，4=表面积，5=质量。`IModelDoc2.GetMassProperties` 是属性、返回 12 元 tuple | `C:\swapi\examples\Get_Mass_Properties_of_ActiveDoc_Example_VB.md` + CHM |
| 6 | `GetBodies2` 在 `IPartDoc` 上，不在 `IModelDoc2` 上 | 对 interop DLL 反射 |
| 7 | `ISketchManager.CreateCircle` 是 6 参（圆心 3 + 圆上点 3） | 对 interop DLL 反射 |
| 8 | `ISelectionMgr.AddSelectionListObject` 的 bool 返回值不可信，必须用 `GetSelectedObjectCount2(-1)` 回读 | 本机实测（12 次全 false 但计数=12） |
| 9 | 画草图前必须先 `SelectByID2` 选中基准面；基准面名随 UI 语言变（`"Front Plane"` / `"前视基准面"`）。不选面 → 特征返回 NULL 且几何零变化。上游已有候选名机制 `_get_plane_name_candidates` —— 沿用它 | 本机实测 + 上游 `sw_part.py` |
| 10 | 贯穿切除用 `swEndCondThroughAll(1)` + 占位深度 0.01，不是把深度设 0 | 上游 `sw_part.extrude_cut` |
| 11 | `OpenDoc6` / `LoadFile4` 的 `[out] long` 在 SW2024/2026 的 makepy 强类型代理上会二次 `int()` → 捕获 `TypeError` 后退回 `dynamic.DumbDispatch` | 上游 `sw_connect.py:456-478` |
| 12 | 空 Dispatch 参数必须包 `VARIANT(VT_DISPATCH, None)` | 上游 `create_empty_dispatch_variant()` |
| 13 | 上游完全没有 SolidWorks Simulation：`cosworks` / `CWModelDoc` / `CwObjects` 在其仓库出现 0 次。它的 FEA 走 CalculiX(139 次)/Elmer(30 次) 开源求解器 | 2026-09-28 全仓 grep |
| 14 | codestack 也没有 Simulation，且 `motion-study/` 只有 2 个文件（无实现） | 同上 |
| 15 | 标量 IDispatch → `Nothing`；Variant 数组 → `Empty`。`AddRestraint` 的 DispArray 属后者 | `swp-macro-reverse-engineering.md`（搜 `DispArray`） |
| 16 | CHM 的 `cosworks` 册只有 47 个文件、只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页）。它薄得「刚刚好」—— 正中 Simulation 夹具/载荷那个坑 —— 但不等于 cosworks 全貌（DLL 里 168 接口 / 363 枚举） | `swdoc.ps1 -List` + 对 DLL 反射，2026-09-28 |
| 17 | `C:\swapi` 不含 cosworks；只覆盖 12 个程序集。`D:\AI\SW\AI Solidworks\官方文档\` 才是全的 | `by_assembly.md` + `swdoc.ps1 -List` |

---

## 七、Git / Fork 规则

```
代码工作副本：C:\swprojects\sw-skill-fork\      ★ 唯一改代码的地方，已是 shallow clone
  origin : https://github.com/wzyn20051216/solidworks-automation-skill
  HEAD   : 8be39ac（2026-09-28）· 390 个上游文件 · MIT
上游：    wzyn20051216/solidworks-automation-skill   (MIT, 1010★)
fork 目标：<你的 GitHub 账号>/solidworks-automation-skill
```

>  建 fork 前不要动 origin。 当前 `origin` 指向上游，是刻意保留的「只读锚点」——
> 用来随时 `git diff origin/main` 看自己偏离上游多少。
> 真正要推的远端得等 fork 建好后再 `git remote add fork <url>`。
> 若已 `git push` 而 origin 还是上游，会误推上游仓库（无权限也会被拒，但别试）。

| 动作 | 是否需要用户批准 |
|---|---|
| 本地 clone / 分支 / commit / `git add` |  不需要 |
| 改文件、跑 `compileall`、跑 `sw_know.py` / `swdoc.ps1` |  不需要 |
| `git remote add/remove`（本地配置，不推） |  不需要 |
| `gh repo fork`（创建 fork） |  必须先批准 |
| `git push`（任何远端） |  必须先批准 |
| 提 PR / 发布 release |  必须先批准 |

⛔ 三条红线（任何模式都不豁免）：删数据 / 删仓库 / 强推；对外发布；只有用户能提供的东西（凭据、业务口径）。

**建议的分支策略**（等批准后再执行）：
- `main` 保持与上游一致，便于 rebase
- 每个功能域一个分支：`feat/simulation`、`feat/drawing-views`、`feat/vbscript-macros` …
- 每个 PR 一句话写清「补了哪个官方接口族，来源是哪个项目/哪套文档」

---

## 八、智能体团队分工

> 角色定义在 `~/.dsh/team-roles.yaml`（全局，已配好）；用法见 `~/.dsh/智能体团队-使用说明.md`。
> **三个角色的工具限制是机制锁死的**，不是靠自觉。

| 角色 | 工具限制 | 在本项目干什么 | 绝不能干 |
|---|---|---|---|
| researcher | 🚫 禁 write/edit/bash | 步骤 1-2：跑 `sw_know.py` + `swdoc.ps1` + 反射建能力全景；grep 18 仓库定位可移植实现 | 不得改任何文件；不得提改动建议，只报事实 |
| coder | 可写 | 步骤 3：按 gap-analysis 移植/新写 `scripts/sw_*.py` + `tests/test_*.py` + 来源标注 | 不得启动 SolidWorks、不得跑 COM、不得编译 C#/C++；不得写「已验证」 |
| reviewer | 🚫 禁 write/edit/bash | 步骤 4：复核签名比对表、许可合规、结构一致性、禁词 | 只报问题，不动手修 |

**派活顺序**（串行为主，避免重复劳动）：
```
researcher(A) ──能力全景（12域走 sw_know）──┐
researcher(B) ──cosworks/Routing 域（CHM+反射）──┤
researcher(C) ──18 仓库可移植实现扫描────────┤
                                            ├──> coder(按域分批) ──> reviewer(逐批复核) ──> 下一批
lead ───────────────────────────────────────┘
```

**按缺口切，互不重叠**：
- researcher A：`sldworksapi` / `swconst` 覆盖的 12 个域 → `sw_know.py`
- researcher B：`cosworks`（Simulation）+ Routing / Costing / PDM → `swdoc.ps1` + 反射
- researcher C：18 仓库里已实现的接口族定位（重点：建视图、VBA/VBS 宏、钣金、焊件、Simulation 载荷）
- coder：按功能域一批一批做，每批交付后 reviewer 复核再进下一批
- lead：维护 `gap-analysis.md` 打勾状态 + 汇总 `harvest-report.md`

**共享任务板约定**：每个任务登记 `write_scopes`，例如 `C:\swprojects\sw-skill-fork\scripts\sw_simulation*.py` + `C:\swprojects\sw-skill-fork\tests\test_sw_simulation*.py`，避免两个 coder 撞同一文件。 `write_scopes` 用绝对路径，因为代码副本不在 DSH 工作区内。

---

## 九、停止条件（遇到就停，不要自行拍板）

1. 两套官方源都查不到某接口，且 `sw_know suggest` 也给不出合理近似 → 先确认该接口是否存在，再写。
2. 某个缺口在 18 个项目里都找不到可移植实现，且官方文档也没有示例 → 标为「无法缝合」，
   写进报告的「仍然空缺」段，不要硬编。
3. 需要碰 AGPL / GPL / 无许可 / 全版权保留 的代码才能补齐 → 停下，报告「需用户提供授权或接受缺口」。
4. 需要 `git push` / 建 fork / 提 PR → 停下，等批准。
5. 发现上游结构与本文 §三 描述不符 → 停下报告，以实际仓库为准并更新本文件。

---

## 十、本地资源速查

```
★ D:\AI\SW\AGENTS.md                       ← 本文件（唯一真源）

★ C:\swprojects\sw-skill-fork\             ← 代码工作副本（git repo，唯一改这里）
    origin = 上游 wzyn20051216 · HEAD 8be39ac · 390 文件

── 官方离线源（两套，见 §4.1）──────────────────────────────
D:\AI\SW\AI Solidworks\官方文档\SWhelp\     29,697 文件 / 285.4 MB（CHM 解包，权威）
    sldworksapi 11579 | sldworksapivb6 16718 | swconst 1353 | cosworks 47
D:\AI\SW\AI Solidworks\手册\swdoc.ps1       ★ 官方文档全文检索工具（-Q / -File / -List）
C:\swapi\                                   结构化 markdown
                                            566 类型 / 963 枚举 / 11,557 成员 / 2,839 示例
$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py
                                            ★ 结构化检索工具（见 §4.1②）

── 素材仓库 ────────────────────────────────────────────────
C:\swprojects\                              19 个目录 = 18 个项目 + sw-skill-fork
C:\swprojects\sw-automation-skill\          ★★ 上游只读克隆（注意与 24★ 那个消歧）
C:\swtest\                                  上一轮 B1/B2 实测脚本（⛔ 只读参考，本项目不执行）

── 报告与知识 ──────────────────────────────────────────────
$env:USERPROFILE\.agents\skills\mech-design\知识库\95-调研源\
                                            18 仓库总览 + GitHub项目清单与链接.md
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\
                                            interop DLL（反射原料，无 XMLDoc）
```

**本任务的产出落点**（写在工作副本里，随 fork 一起走）：
```
C:\swprojects\sw-skill-fork\docs\capability-matrix.md
C:\swprojects\sw-skill-fork\docs\gap-analysis.md
C:\swprojects\sw-skill-fork\docs\signature-audit.md
C:\swprojects\sw-skill-fork\docs\harvest-report.md
```

---

## 十一、开工第一句话模板

**先把 DSH 工作区切到 `D:\AI\SW\`**，然后起手（会自动注入本文件）：

> 工作区是 `D:\AI\SW\`，代码副本在 `C:\swprojects\sw-skill-fork\`。
> 读 `D:\AI\SW\AGENTS.md`，按 §五 步骤 1 开始：
> 派 researcher A 跑 `sw_know.py domain --list` 建 12 个域的官方能力全景，
> 派 researcher B 用 `swdoc.ps1` + 反射建 cosworks/Routing 域的清单，
> 派 researcher C 扫描 18 个仓库定位已实现的接口族。
> 产出 `docs/capability-matrix.md` 和 `docs/gap-analysis.md`（从零建表，不要预设结论），
> **不要动任何代码，也不要启动 SolidWorks**。
