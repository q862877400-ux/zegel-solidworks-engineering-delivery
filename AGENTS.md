# AGENTS.md

本文件是 SolidWorks Automation Skill「集大成 + 建护城河」任务的常驻指令；工作区 `D:\AI\SW\`（已是 git 仓库），代码工作副本 `C:\swprojects\sw-skill-fork\`。跨项目的通用纪律在 `~/.dsh/AGENTS.md`（用户全局层，每轮自动注入）—— 缝合优先、签名以官方源为准、查不到就说查不到、许可红线、把验证责任转移到静态比对、验收判据写成可 grep 项；本文件只留 SolidWorks 专属的事实与规矩。

---

## 工作区（第一件事，先确认你在哪）

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `D:\AI\SW\` | 本文件所在 · DSH 工作区根 · 任务产物（草稿 / 日志 / 报告 / 证据） | 放产物 |
| `C:\swprojects\sw-skill-fork\` | 代码工作副本（独立 git 仓库） | 唯一改代码的地方 |
| `C:\swprojects\<owner>\` | 四家外部 MCP 项目的克隆 | 只读对照 |
| `C:\swprojects\sw-automation-skill\` | 上游的另一份克隆 | 只读对照 |
| `D:\AI\SW\AI Solidworks\` | SolidWorks 工作区（官方文档 / 手册 / 模型 / 截图） | 只读 |

`D:\AI\SW\` 现已是 git 仓库（提交 `1f86c5d` 起），收草稿脚本、运行日志、报告与证据；`.gitignore` 排除了 398 MB（官方文档 / 反射转储 / 探索截图 / CAD 保真数据）。

任务报告放 `D:\AI\SW\` 下，代码放 `C:\swprojects\sw-skill-fork\`。`D:\AI\SW\AI Solidworks\` 是模型 / 截图 / 手册，不是代码落点。

---

## 〇、一句话任务

> 把 `wzyn20051216/solidworks-automation-skill`（1010 星, MIT）补强成「官方 SolidWorks API 全覆盖 + 集四家 MIT/Apache MCP 项目之广度 + 业界空白域护城河」，最后推一个 fork。

三条主线：

- 集大成：把四家外部 MCP 项目的能力广度并入本仓库，使单一项目即可替代四家之和，每一步可指认出处（铁律 1）。
- 建护城河：攻业界空白域 —— 经核实真正全网空白的只有拓扑优化、动画导出（AVI）、Costing 三个。
- 正规军：不搞大杂烩，命名 / 单位 / 选择 / 验证等级 / 出处五统一，并挂机器门禁（`docs/union-conventions.md` + `scripts/check_union_conventions.py`）。

这仍是缝合项目，不是从零写：能力来自官方文档、外部开源项目与本仓库既有模式。

---

## 一、验收标准（做完这几条才算完成）

| # | 判据 | 怎么验 |
|---|---|---|
| A1 | 四家的能力广度已并入：域覆盖矩阵里本仓库每一格都有来源，或写明「不做 + 原因」 | `docs/union-coverage-matrix.md` 可重新生成且无空白格 |
| A2 | 每个并入条目带 `provenance`（`owner/repo` 全名 + 许可 + 文件 + 来源验证状态） | grep 抽查 10 条，100% 命中 |
| A3 | 五统一门禁通过：命名 / 单位 / 选择 / 验证等级 / 出处 | `scripts/check_union_conventions.py` 退出码 0，且已接进 `release_check.py` |
| A4 | 每个条目的 `level` 取自五级枚举；`verified` 必须有我们自己的运行证据 | 逐条核对 `capabilities.yaml` |
| A5 | 每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐 | `docs/signature-audit.md` |
| A6 | 许可无越界：AGPL / GPL / 无许可 / 全版权保留的代码没被抄进来；Apache-2.0 来源带 NOTICE 义务 | 逐文件对照「许可判定表」 |
| A7 | 全文没有一处把 `source_verified` 或 `stitched` 写成 `verified` | grep 全文，禁词 0 命中 |
| A8 | 报告写明并入了什么、仍空缺什么、为什么空缺 | `docs/harvest-report.md` |
| A9 | 空白域护城河有可跑的工程实现（拓扑优化优先），不是只有文档 | 对应 `scripts/` 模块 + `tests/` |

---

## 二、六条铁律

### 铁律 1 · 只做「缝合」，不做「发明」

每加一个能力，要能指认出处。四种合法来源：

| 来源 | 怎么用 | 例 |
|---|---|---|
| 官方 API 文档 | 决定接口选型与参数顺序 | Simulation 域（外部无人提供，只能照官方签名建） |
| 其它开源项目 | 直接移植 / 改写，保留来源头注释 | 建视图 ← codestack；VBScript ← pengxiaoan |
| 四家外部 MCP 项目 | 移植其能力广度，按 `provenance` 标注来源与许可 | `andrewbartels1` 的草图完全定义探针；`Slacker-LLC` 的声明式 selection |
| 本项目自身既有模式 | 沿用 `sw_part.py` / `sw_hole_features.py` 的写法与命名 | 新 `sw_xxx.py` 沿用 `_select_by_id` / `get_com_member` |

不可接受：凭印象写一个 `FeatureManager.XXX(...)` 然后「看着像对的」。

### 铁律 2 · 可以实测，但必须先关弹窗、必须有超时

验证顺序：静态签名比对（前置筛查）→ 本机实测（真跑，用 `mcp__solidworks__*` 或直接调 COM）→ 两关都过，才允许在文档里写「已验证 / 实测 / 跑通」。

实测的三条安全约束：

- **先置 `ISldWorks.CommandInProgress = True`** —— 未抑制的模态对话框会把会话永久挂起，这是无人值守挂起的头号原因。
- **每个 COM 调用设超时** —— COM 是 STA 且线程亲和，调用一旦开始无法强制中止；超时只救「等待」，救不了线程，超时后不要重试同一进程。
- **收尾必做** —— `CommandInProgress = False`、释放 COM 引用、关掉自己开的文档。

红线：破解相关（SolidWorks-CAD / Solidworks-Crack 类投递页、破解指南）零接触；不动注册表 / 全局环境变量 / 系统层；未经确认不 `git push` / 不建 fork / 不发 release；不删用户数据。

### 铁律 3 · 参照上游结构，不自创结构

新增文件 / 目录 / 命名 / 文档格式落在上游已有位置（见「上游仓库结构」）。不新增顶层目录；确需新功能域时，按上游 `subskills/` 的既有模式扩。

### 铁律 4 · 签名以官方文档为准，两套源都要用

本机有两套官方离线源，各有长短，都要查：`D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与 `C:\swapi\`（结构化 markdown，查精确签名与枚举值）。

出厂类型库是第三套源，也是冲突时的裁决者：`FeatureFillet3` 在本机类型库里有 14 个参数，官方文档写 7 个。口径是三源互证 —— 文档、反射、CHM；冲突时以出厂类型库的反射为准。不凭记忆、不凭反射猜参数、不照抄其它项目的注释。

### 铁律 5 · 查不到就说查不到

两套源都查不到 → 写「查不到」并停下换思路，不要用相似名字蒙混。名字缺席 = 官方 API 里没有这个成员，不是「没写文档」。

### 铁律 6 · 许可红线，一次都不能越

| 许可 | 能做什么 | 义务 |
|---|---|---|
| MIT | 读、抄、改、商用 | 保留版权声明 |
| Apache-2.0 | 读、抄、改、商用 | 保留 `NOTICE`（`Slacker-LLC/solidworks-mcp` 是 `Copyright 2026 JIALE LIU`）+ 声明改动了哪些文件 |
| AGPL / GPL | 只读思想 | 不抄代码、不抄文本 |
| 无许可 / 全版权保留 | 只读思想 | 同上 |

Apache-2.0 的 NOTICE 义务跟着分发走：一旦入库，推送 fork 时就要带 `THIRD-PARTY-NOTICES.md` —— 该文件尚未创建。

---

## 三、上游仓库结构（新增文件落在这里）

> 来源：工作副本 `C:\swprojects\sw-skill-fork\`（remote `wzyn20051216/solidworks-automation-skill`，390 个上游文件，MIT）；只读对照克隆在 `C:\swprojects\sw-automation-skill\`（395 文件）。

```
solidworks-automation-skill/
├─ SKILL.md                    ← 主技能入口
├─ capabilities.yaml           ← 能力真源：原子操作 → 后端映射，每条带 level / provenance
├─ golden-workflows.yaml       ← 黄金工作流
├─ agents/  ai_team/           ← 智能体定义
├─ apps/desktop/               ← 桌面工作台（cad_workbench/）
├─ docs/                       ← 说明与生成物：union-conventions.md / union-coverage-matrix.md
│                                / capability-matrix.md / gap-analysis.md / signature-audit.md
│                                / harvest-report.md
├─ mcp-server/server.py        ← MCP 服务
├─ references/                 ← 知识文档（language-backend-routing / troubleshooting / export …）
├─ scripts/                    ← 能力实现主战场，命名 sw_<域>.py
├─ subskills/                  ← autocad / 工程图 / 圆角倒角 CNC / 螺纹孔 / vibecad
├─ tests/                      ← 80+ 测试
├─ tools/                      ← 来源与地图构建：build_union_sources.py / build_union_map.py
│                                / union-sources.json
└─ requirements{,-mesh,-occt,-pdf}.txt
```

`scripts/` 已有能力模块（补全前先看是否已存在）：`sw_connect sw_preflight sw_session sw_part sw_assembly sw_drawing sw_motion sw_sheet_metal sw_weldment sw_export sw_gear sw_hole_features sw_appearance sw_delivery sw_review sw_document_data sw_entity_reference sw_import_mesh_reference sw_macro_guard sw_diagnostics sw_addin_host sw_capability_probe backend_router capabilities fea_analysis fea_convergence advanced_geometry advanced_geometry_ocp advanced_surface_ocp headless_cad_writer headless_occt_service dxf_preview_scene dfm_review dfm_profiles drawing_spec routing_review cad_studio cad_doctor cad_diagnostics cad_installation stability_regression release_check`。

新增模块的硬性要求：

- 命名 `sw_<功能域>.py`，与既有并列；顶部 docstring 写清能力域、对应官方接口族、移植来源、许可。
- 顶部 import 照抄 `sw_connect.py` 的依赖解析模式（`try: from .x import / except ImportError: from x import`）。
- 涉及选中的操作，一律复用 `sw_part._select_by_id` / `sw_connect.get_com_member`，不裸写 `SelectByID2`，不裸写 `getattr(obj, name)()`。
- 补 `tests/test_<模块名>.py`（静态可跑：mock adapter，不连 SolidWorks）。

---

## 四、素材库

### 4.1 两套官方离线源 + 反射（各管一头）

`D:\AI\SW\AI Solidworks\官方文档\` 是安装自带 3 册 CHM 用 `hh.exe -decompile` 解包而成（随安装自带，无许可风险）：

```
官方文档\SWhelp\sldworksapi\       11,579 文件  153.7 MB   C#/C++ API 主册
官方文档\SWhelp\sldworksapivb6\    16,718 文件   67.4 MB   VB6/VBA API 册
官方文档\SWhelp\swconst\            1,353 文件   22.4 MB   枚举
官方文档\SWhelp\cosworks\              47 文件   41.8 MB   Simulation（很薄，见下）
合计 29,697 文件 / 285.4 MB
```

检索工具 `手册\swdoc.ps1`：`-List` 三册概况 / `-Q '<关键词>'` 全文检索 / `-File '<页面名>'` 整页转纯文本。解包时输出目录要不存在且路径不带空格，否则 `hh.exe` 静默失败；7-Zip 25.01 起没有 CHM 解码器，只有 `hh.exe` 可用；不要去爬 help.solidworks.com（403 + JS 渲染，爬下来是空壳）。

`cosworks` 册只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页），正好命中本机 C# 执行层返工 24 轮的 Simulation 夹具 / 载荷坑；但它不等于 cosworks 全貌（DLL 里 168 接口 / 363 枚举）。深度查 CHM，广度查反射。

`C:\swapi\` 是结构化查询源：566 类型 / 963 枚举 / 11,557 成员 / 2,839 官方示例（16,254 文件）。入口 `python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" <子命令>`：

| 子命令 | 用途 |
|---|---|
| `member <Type> <Member>` | 精确签名 + 每个参数说明（写代码前查） |
| `type <Type> [--grep X]` | 某类型全部成员 |
| `enum <Enum>` | 枚举全部成员（枚举值也要查，不许猜） |
| `find <kw> [--kind type\|enum\|member\|example]` | 全库检索 |
| `examples "<多词>"` | 找官方示例（Example 页比方法页有用得多） |
| `domain --list` / `domain <域>` | 功能域导航（14 域） |
| `suggest <拼错的词>` | 近似名建议 |
| `verify` / `stats` | 校验功能域地图 / 规模总览 |

它只含 12 个程序集，缺 `cosworks`、`SWRoutingLib`、`sldcostingapi`、`fworks`、`sustainability`、`swdocumentmgr`、`sldtbt`；这些域改查 CHM 与反射。

反射是第三套源，补 CHM 与 `C:\swapi` 都缺的广度：`redist` 里的 interop DLL 没有 XMLDoc，但都是托管程序集，可直接 `Assembly.ReflectionOnlyLoadFrom(...).GetTypes()`。反射是「读官方程序集」，不是实测。已核实体量：`cosworks` 168 接口 / 363 枚举 / 9,281 成员；`SWRoutingLib` 28/26/527；`sldcostingapi` 28/24/1,006；`fworks` 2/10/65。

### 4.2 其它项目（`C:\swprojects\`）

`C:\swprojects\` 共 23 个目录 = 21 个外部项目克隆 + `sw-skill-fork` 自己 + 临时目录 `_tmp_mcp`；其中 22 个是 git 仓库。

> 目录名消歧：`sw-automation-skill\` 是 wzyn20051216 的 1010 星（本项目要完善的目标）；`solidworks-automation-skill\` 是 djlex83 的 24 星（只贡献一个 `VARIANT` 写法）。引用素材一律写 `owner/repo` 全名，不要只写目录名。

| 目录 | 项目（owner/repo） | 星 | 许可 | 能补什么 |
|---|---|---|---|---|
| `codestack` | xarial/codestack | 377 | MIT | 建视图 / 文档 / 装配 / 导入导出 / 22 篇 troubleshooting（433 篇 md） |
| `solidworks-api` | angelsix/solidworks-api | 370 | MIT | SolidDNA 模板（免弹模板设置）；`References/` 见下方例外 |
| `mcp-server-solidworks` | eyfel/mcp-server-solidworks | 355 | AGPL-3.0 | 只读架构思想（adapters / cad-planner / compiler / execution 四层） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 234 | MIT | `mock-solidworks-adapter` 测试分层；`macro-generator`；5 个 .vba |
| `CSharpAndSolidWorks` | painezeng/CSharpAndSolidWorks | 171 | MIT | 几何算法（自交 / 凸性 / 面积）；38 个 .SLDPRT 测试件 |
| `Solidworks-MCP` | alisamsam/Solidworks-MCP | 143 | MIT | 27 个 .vbs（最大 VBScript 语料）；Hub 死连接诊断 |
| `solidworks-skills` | delancy827/solidworks-skills | 115 | MIT | 交叉验证来源（「23 参数不是 17」独立佐证） |
| `sw-automation-skill` | wzyn20051216/solidworks-automation-skill | 1010 | MIT | 本项目目标本体 |
| `pySW` | kalyanpi4/pySW | 52 | GPL-2.0 | 只读思想，不抄代码 |
| `solidworks-automation-skill` | djlex83/solidworks-automation-skill | 24 | MIT | `VARIANT(VT_DISPATCH,None)` 简洁写法 |
| `offline-solidworks-api-docs` | pedropaulovc/offline-solidworks-api-docs | 13 | 无许可 | `C:\swapi` 的来源，产物同样不可再分发；只读流水线思路 |
| `solidworks-build-mechanical-models` | pengxiaoan/solidworks-build-mechanical-models | 13 | 无许可 | 只读思想（绕过 `SelectByID2`），不抄文本 |
| `solidworks-auto-modeling` | Sakikooooo/solidworks-auto-modeling | 8 | MIT | `Nothing`（标量 Dispatch）vs `Empty`（Variant 数组）规则 |
| `sw-ai-bridge` | Mochaxgcc/solidworks-ai-bridge | 7 | MIT | 裸传 23 个位置参数的佐证 |
| `sw-api-skill` | guoleizhen717/solidworks-api-skill | 5 | MIT | 「>12 参数会失败」是错的，别采信 |
| `ddeng-skills` | walterkken/doc-driven-engineering-software-skills | 5 | 全版权保留 | 只借鉴「文档驱动目录结构」这一条方法论 |
| `q3ds-solidworks-mcp` | Bennyco86/q3ds-solidworks-mcp | 5 | AGPL-3.0 | 只读产品设计（响应体裁剪省 token、视觉捕获） |
| `solidworks-com-automation-skill` | ZiChen-Ni/solidworks-com-automation-skill | 2 | MIT | 最小 COM 封装；Windows 安装脚本 |
| — | `SolidWorks-CAD` / `Solidworks-Crack` | 812/287 | — | 排除：投递页 / 破解指南。不下载、不读取、不运行 |

四家与本项目重叠的外部 MCP 项目（克隆在 `C:\swprojects\<owner>\`，已逐份读真实 LICENSE 文件，不采信 README 徽章）：

| 克隆目录 | 项目（owner/repo） | 工具 | 许可 | 测试文件 | 自己声明跑过的环境 |
|---|---|---|---|---|---|
| `Eduardof0nt` | Eduardof0nt/Solidworks-MCP-Server | 187 | MIT | 0 个 | 未声明 |
| `andrewbartels1` | andrewbartels1/SolidworksMCP-python | 128 | MIT | 147（7 live） | 未声明（README 自述 under active construction） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 103 | MIT | 7（0 live） | 未声明 |
| `Slacker-LLC` | Slacker-LLC/solidworks-mcp | 92 | Apache-2.0 | 2（1 live） | SW 2026 SP3.2 简体中文 |

三条警示：

- 工具最多的那家（187）测试文件数为 0：README 写着「Verified on SolidWorks 2024」，仓库里没有任何测试文件 —— README 说验过不等于验过。
- 四家里只有 `Slacker-LLC` 声明全工具真机跑过，而它的工具数最少（92）；它的 92 个里没有仿真 / 动画 / 拓扑 / 钣金 / 焊件 / 公差。
- `Slacker-LLC` 是 Apache-2.0：可抄，但要保留 `NOTICE`（`Copyright 2026 JIALE LIU`）并声明改动了哪些文件；推送 fork 时产生硬性义务，`THIRD-PARTY-NOTICES.md` 尚未创建。

许可判定表：

| 标记 | 含义 | 能做什么 |
|---|---|---|
| MIT | MIT | 可读、可抄、可改、可商用（保留版权声明） |
| Apache-2.0 | Apache-2.0 | 同上，另有 `NOTICE` 与改动声明义务 |
| AGPL-3.0 / GPL-2.0 | 传染性 | 只读思想，不抄代码、不抄文本 |
| 无 LICENSE / 全版权保留 | 保留所有权利 | 只读思想（全版权保留的只取方法论） |
| 排除 | 恶意 / 破解 | 零接触 |

MIT 唯一已知的例外（`angelsix/solidworks-api` 原文照抄）：

> All files inside the References folder are property of Dassault Systemes SolidWorks Corp and may only be used in unmodified form in conjunction with SolidDNA.

抄 `Templates/SolidDNA` 可以；`References/` 里的文件是达索的财产，原样用、只配 SolidDNA。

`C:\swapi` 的内容来自无许可的 `offline-solidworks-api-docs`（爬 help 站点），所以 `C:\swapi` 的产物同样不可再分发进闭源产品；fork 发布前要意识到这点。`D:\AI\SW\AI Solidworks\官方文档\` 是达索随安装自带的，没有这个问题，优先用它。

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

最后那行「未实测」标注不许删。并入 `capabilities.yaml` 的条目另带结构化出处：

```yaml
provenance:
  - {repo: Slacker-LLC/solidworks-mcp, license: Apache-2.0, files: ["sw_feature.py"], upstream_verified: "SW 2026 SP3.2"}
    # repo 要写 owner/repo 全名，不只写目录名；upstream_verified 填来源自己声明的验证环境，没有就留空
```

---

## 五、工作方法（并入五步）

1. 建全景与对差：`sw_know.py domain --list` 拿 14 个域，`swdoc.ps1` + 反射补 `cosworks` / Routing / Costing / PDM，对照上游 `capabilities.yaml` + `scripts/` + `subskills/` 建 `docs/capability-matrix.md` 与 `docs/gap-analysis.md`（从零建表，不预设缺口结论）。
2. 找来源：按优先级取素材 —— 上游相邻模块 > MIT 项目现成实现 > MIT 项目文档 / 示例 > Apache-2.0 项目实现（带 NOTICE）> 只读思想（AGPL / GPL / 无许可，绝不抄文本）> 照官方签名自建。
3. 归一：按「并入六条规则」改造，命名 / 单位 / 选择 / 验证等级 / 出处五统一。
4. 标等级与出处：`capabilities.yaml` 每条给 `level`（五级）与 `provenance{repo, license, files, upstream_verified}`。
5. 门禁与实测：`check_union_conventions.py` → `python -m compileall -q scripts subskills` → 逐 COM 调用与官方签名对齐（`docs/signature-audit.md`）→ 本机实测；缺我们自己的运行证据的条目留在 `stitched`。

产出：`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/union-coverage-matrix.md`、`docs/harvest-report.md`。

并入六条规则（全文 `C:\swprojects\sw-skill-fork\docs\union-conventions.md`，机器校验 `scripts/check_union_conventions.py`，已在 `release_check.py` 里硬失败）：

| # | 规则 | 校验 |
|---|---|---|
| 1 | 命名统一 `solidworks_<域>_<动作>`；headless 路线用 `cadstudio_*`，两者不混用 | 工具名正则 |
| 2 | 长度参数 `_mm` 结尾、角度 `_deg` 结尾，换算只在边界做一次（`sw_connect.mm()`） | 参数名与描述 |
| 3 | 选择用声明式 `selection`，不写裸坐标，并按 mark 分配 | 参数 schema 无裸 `x` / `y` / `z` |
| 4 | 验证等级五级 `verified` / `source_verified` / `stitched` / `indexed` / `not_implemented`；`source_verified` 不得写成 `verified` | `level` 在枚举内，`verified` 要有 `evidence` |
| 5 | 每条并入条目带 `provenance{repo(owner/repo), license, files, upstream_verified}` | `repo` 匹配 `owner/repo`，`license` 在白名单 |
| 6 | 建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功 | 建特征类工具都要调 |

---

## 六、已知事实（已在本机核实，不要重新推导）

> 这些是上游文档 / 注释里没有或写错的。写代码直接用，别再踩。

| # | 事实 | 依据 |
|---|---|---|
| 1 | 切除的正确入口是 `IFeatureManager.FeatureCut4`（27 参数），不是 `FeatureExtrusion3(Flip=true)`：后者建出来是「凸台-拉伸」特征名，体积恒等于原板 | 本机实测 + 上游 `sw_part.extrude_cut` + `swdoc.ps1 -File FeatureCut4` |
| 2 | `IFeatureManager.FeatureExtrusion3` 是 23 个参数；`FeatureExtrusion2` 已废弃被 3 取代 | `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` + delancy827 README 独立佐证 |
| 3 | 「>12 参数 IDispatch 会失败」是错的（guoleizhen717 说法不可采信） | 23 / 27 参在 pywin32 迟到绑定下均正常 |
| 4 | pywin32 迟到绑定下同一成员可能是属性也可能是方法：`GetDocumentCount`、`GetMassProperties` 是属性，直接调用会 `TypeError: 'int' object is not callable`；移植代码沿上游 `get_com_member()` | 本机实测 + 上游 `sw_connect.py` |
| 5 | 质量属性用 `IModelDocExtension.GetMassProperties2(accuracy, out status, useSelected)`；下标 0-2 质心、3 体积、4 表面积、5 质量。`IModelDoc2.GetMassProperties` 是属性、返回 12 元 tuple | `C:\swapi\examples\Get_Mass_Properties_of_ActiveDoc_Example_VB.md` + CHM |
| 6 | `GetBodies2` 在 `IPartDoc` 上，不在 `IModelDoc2` 上 | 对 interop DLL 反射 |
| 7 | `ISketchManager.CreateCircle` 是 6 参（圆心 3 + 圆上点 3） | 对 interop DLL 反射 |
| 8 | `ISelectionMgr.AddSelectionListObject` 的 bool 返回值不可信，用 `GetSelectedObjectCount2(-1)` 回读 | 本机实测（12 次全 false 但计数 = 12） |
| 9 | 画草图前先 `SelectByID2` 选中基准面；基准面名随 UI 语言变（`"Front Plane"` / `"前视基准面"`）。不选面 → 特征返回 NULL 且几何零变化；沿上游 `_get_plane_name_candidates` | 本机实测 + 上游 `sw_part.py` |
| 10 | 贯穿切除用 `swEndCondThroughAll(1)` + 占位深度 0.01，不是把深度设 0 | 上游 `sw_part.extrude_cut` |
| 11 | `OpenDoc6` / `LoadFile4` 的 `[out] long` 在 SW2024/2026 的 makepy 强类型代理上会二次 `int()` → 捕获 `TypeError` 后退回 `dynamic.DumbDispatch` | 上游 `sw_connect.py` |
| 12 | 空 Dispatch 参数包 `VARIANT(VT_DISPATCH, None)` | 上游 `create_empty_dispatch_variant()` |
| 13 | 上游完全没有 SolidWorks Simulation：`cosworks` / `CWModelDoc` / `CwObjects` 在其仓库出现 0 次；它的 FEA 走 CalculiX(139 次) / Elmer(30 次) 开源求解器 | 全仓 grep |
| 14 | codestack 也没有 Simulation，且 `motion-study/` 只有 2 个文件（无实现） | 同上 |
| 15 | 标量 IDispatch → `Nothing`；Variant 数组 → `Empty`。`AddRestraint` 的 DispArray 属后者 | `swp-macro-reverse-engineering.md`（搜 `DispArray`） |
| 16 | CHM 的 `cosworks` 册只有 47 个文件、只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页），不等于 cosworks 全貌（DLL 里 168 接口 / 363 枚举） | `swdoc.ps1 -List` + 对 DLL 反射 |
| 17 | `C:\swapi` 不含 cosworks，只覆盖 12 个程序集；`D:\AI\SW\AI Solidworks\官方文档\` 才是全的 | `by_assembly.md` + `swdoc.ps1 -List` |
| 18 | 四家外部 MCP 项目的工具数与验证口径：Eduardof0nt/Solidworks-MCP-Server 187 / MIT / 测试文件 0 个 / 未声明环境；andrewbartels1/SolidworksMCP-python 128 / MIT / 147（7 live）/ 未声明；vespo92/SolidworksMCP-TS 103 / MIT / 7（0 live）/ 未声明；Slacker-LLC/solidworks-mcp 92 / Apache-2.0 / 2（1 live）/ SW 2026 SP3.2 简体中文。工具最多的那家测试文件为 0，README 却写「Verified on SolidWorks 2024」 | 逐份读真实 LICENSE 文件与仓库树 |
| 19 | 域覆盖矩阵（去重归一后 384 个操作，域定义见下方代码块）：本仓库只有 `高级/专项` 一域领先（3，四家 0–1），其余 15 个域都不领先 —— `草图` / `钣金` / `焊件` / `模具` / `参考` 为 0，`尺寸` / `零件` / `宏` 为 1，`工程图` 3 对四家的 15–18 | `tools/build_union_map.py` 生成 `docs/union-coverage-matrix.md` |
| 20 | `高级/专项`（拓扑优化 / DFM / Costing / PDM / 路由 / DimXpert / GD&T）是唯一「四家全空、只有本仓库有」的域 | 同上 |
| 21 | 真正全网空白的只有三个域：拓扑优化（`andrewbartels1` 明确列在 "Not Yet / Simulated"）、动画导出 AVI（Motion Study 创建有人做，出片没搜到）、Costing（PDM 被 `Eduardof0nt` 的 Contributing 列为 missing） | 上网核实 + 四家仓库源码 |
| 22 | 「草图完全定义」这条纪律 `andrewbartels1`（MIT）有实现且带测试：`_check_sketch_fully_defined_impl` 多探针（`ISketch.IsFullyConstrained` SW2018+ / `ISketch.GetStatus` / `ISketch.FullyDefined`）经 `_probe_to_flag` 归一 bool/int/float/string，返回 `{sketch_name, fully_defined, state, source_api}`，并接进 `checkpoint_service` 与 `parameter_repair_service`；本仓库 grep `完全定义\|fully defined\|欠定义` 0 命中 | 其源码 `src/solidworks_mcp/adapters/solidworks/sketch.py` + 三个测试用例 |
| 23 | 并入规范与门禁的落点：`docs/union-conventions.md`（六条规则全文）、`docs/union-coverage-matrix.md`（生成物）、`tools/build_union_sources.py`、`tools/build_union_map.py`、`tools/union-sources.json`（含每家的许可与验证口径）、`scripts/check_union_conventions.py`（已接进 `release_check.py`） | 工作副本 `C:\swprojects\sw-skill-fork\` |

```
              会话  参考  草图  尺寸  零件  曲面  钣金  焊件  模具  装配  工程图  检查  仿真  外观  宏  高级
Eduardof0nt    14    3    26    6    23   11   10    5     3    13    18    11    3    10    4    0
andrewbartels1 22    3    15    2    11    0    0    0     0     7    18     3    0     1   22    0
vespo92        10    0    16    6     3    1    1    0     0     4    15     7    1     3   21    1
Slacker-LLC     7    3    20    2    13    0    0    0     0     3    17     6    0     2    0    0
本仓库           7    0     0    1     1    2    0    0     0     6     3     2    2     4    1    3
                                                                                              ↑ 唯一独有
```

---

## 七、Git / Fork 规则

```
代码工作副本：C:\swprojects\sw-skill-fork\     唯一改代码的地方，已是 shallow clone
  origin : https://github.com/wzyn20051216/solidworks-automation-skill   ← 刻意保留的只读锚点
  MIT · fork 目标：<你的 GitHub 账号>/solidworks-automation-skill
工作区仓库：  D:\AI\SW\                        git 仓库（提交 1f86c5d 起），只放产物
```

建 fork 前不要动 origin：`origin` 指向上游是刻意保留的只读锚点，用 `git diff origin/main` 看自己偏离上游多少；要推的远端等 fork 建好后再 `git remote add fork <url>`。origin 还是上游就 `git push` 会误推上游仓库。

| 动作 | 是否需要用户批准 |
|---|---|
| 本地 clone / 分支 / commit / `git add` / `git remote add\|remove` | 不需要 |
| 改文件、跑 `compileall`、跑 `sw_know.py` / `swdoc.ps1` | 不需要 |
| `gh repo fork`（建 fork） | 要先批准 |
| `git push`（任何远端） | 要先批准 |
| 提 PR / 发布 release | 要先批准 |

三条红线（任何模式都不豁免）：删数据 / 删仓库 / 强推；对外发布；只有用户能提供的东西（凭据、业务口径）。

推送前置义务：并入了 Apache-2.0 来源（`Slacker-LLC/solidworks-mcp`）⇒ fork 要带 `THIRD-PARTY-NOTICES.md`（含 `Copyright 2026 JIALE LIU` 与改动文件清单），该文件尚未创建；MIT 来源保留版权声明。

分支策略：`main` 与上游保持一致便于 rebase；每个功能域一个分支（`feat/simulation`、`feat/drawing-views` …）；每个 PR 一句话写清「补了哪个官方接口族，来源是哪个项目 / 哪套文档」。

---

## 八、智能体团队分工

> 角色定义在 `~/.dsh/team-roles.yaml`（全局）；用法见 `~/.dsh/智能体团队-使用说明.md`。三个角色的工具限制是机制锁死的。

| 角色 | 工具限制 | 在本项目干什么 | 绝不能干 |
|---|---|---|---|
| researcher | 禁 write/edit/pwsh | 跑 `sw_know.py` / `swdoc.ps1` / 反射建能力全景；扫 `C:\swprojects\` 下 21 个项目定位可移植实现 | 不改任何文件；只报事实，不提改动建议 |
| coder | 可写 | 按 `gap-analysis.md` 移植或新写 `scripts/sw_*.py` + `tests/test_*.py` + `provenance` 标注 | 不启动 SolidWorks、不跑 COM、不编译 C#/C++；不写「已验证」 |
| reviewer | 禁 write/edit/pwsh | 复核签名比对表、许可合规、结构一致性、五统一门禁、禁词 | 只报问题，不动手修 |

派活按「来源 + 域」两个维度切，互不重叠：来源组一人一家（四家外部 MCP 各扫工具清单、许可与测试口径），域组按 `高级/专项`、`曲面`、`钣金` … 分批。每个任务登记 `write_scopes`（绝对路径，代码副本不在 DSH 工作区内），例如 `C:\swprojects\sw-skill-fork\scripts\sw_simulation*.py` 与其对应的 `tests\`。

lead 维护 `docs/union-coverage-matrix.md` 与 `docs/gap-analysis.md` 的打勾状态，并汇总 `docs/harvest-report.md`。

---

## 九、停止条件（遇到就停，不要自行拍板）

1. 两套官方源都查不到某接口，且 `sw_know suggest` 也给不出合理近似 → 先确认该接口是否存在，再写。
2. 某个缺口在 21 个项目里都找不到可移植实现，且官方文档也没有示例 → 标为「无法缝合」，写进报告的「仍然空缺」段，不要硬编。
3. 需要碰 AGPL / GPL / 无许可 / 全版权保留 的代码才能补齐 → 停下，报告「需用户提供授权或接受缺口」。
4. 需要 `git push` / 建 fork / 提 PR → 停下，等批准。
5. 发现上游结构与本文「上游仓库结构」描述不符 → 停下报告，以实际仓库为准并更新本文件。
6. 来源没有测试、我们又无法本机实测 → 标 `stitched`，不得标 `verified`。

---

## 十、本地资源速查

```
D:\AI\SW\AGENTS.md                          本文件（唯一真源，勿复制到别处）
D:\AI\SW\                                   工作区仓库（git，提交 1f86c5d 起）
C:\swprojects\sw-skill-fork\                代码工作副本（git，唯一改代码的地方）

── 官方离线源（见 §四.1）──
D:\AI\SW\AI Solidworks\官方文档\SWhelp\     29,697 文件 / 285.4 MB（CHM 解包，权威）
    sldworksapi 11579 | sldworksapivb6 16718 | swconst 1353 | cosworks 47
D:\AI\SW\AI Solidworks\手册\swdoc.ps1       官方文档全文检索（-Q / -File / -List）
C:\swapi\                                    566 类型 / 963 枚举 / 11,557 成员 / 2,839 示例
%USERPROFILE%\.agents\skills\mech-design\tools\sw_know.py    结构化检索工具
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist\      interop DLL（反射原料，无 XMLDoc）

── 素材仓库 ──
C:\swprojects\                               23 个目录：21 个项目 + sw-skill-fork + _tmp_mcp
C:\swprojects\sw-automation-skill\           上游只读克隆（与 24 星的 djlex83 消歧）
C:\swprojects\{Eduardof0nt,andrewbartels1,SolidworksMCP-TS,Slacker-LLC}\   四家外部 MCP
C:\swtest\                                   此前的 B1/B2 实测脚本（只读参考，本项目不执行）
```

产出落点（写在工作副本里，随 fork 一起走）：`docs/union-conventions.md`、`docs/union-coverage-matrix.md`、`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/harvest-report.md`、`tools/build_union_sources.py`、`tools/build_union_map.py`、`tools/union-sources.json`、`scripts/check_union_conventions.py`。

---

## 十一、开工第一句话模板

先把 DSH 工作区切到 `D:\AI\SW\`，然后起手（本文件会自动注入）：

> 工作区 `D:\AI\SW\`，代码副本 `C:\swprojects\sw-skill-fork\`。
> 读 `D:\AI\SW\AGENTS.md`，按「工作方法」五步推进：
> 先跑 `sw_know.py domain --list` 与 `swdoc.ps1` + 反射建能力全景，
> 再扫 `C:\swprojects\` 下 21 个项目定位可移植实现，
> 按「并入六条规则」归一、标验证等级与 `provenance`，
> 门禁 `check_union_conventions.py` 通过后再谈实测，
> 缺我们的运行证据的条目留在 `stitched`。
> 产出落 `docs/`；不要动 origin，实测阶段之前不启动 SolidWorks。
