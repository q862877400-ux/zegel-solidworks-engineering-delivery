# Amagine3D（amagine-ai）

<!-- survey: class=B; repr=code; orchestration=loop; verify=export-readback; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/amagine-ai/Amagine3D · 官网 https://amagine.ai · 中文说明 `docs/README.zh-CN.md` |
| 许可 | **Apache-2.0** —— 读仓库内 `LICENSE` 原文：第 2 行 `Apache License`、第 3 行 `Version 2.0, January 2004`；`package.json` 的 `"license": "Apache-2.0"`；`NOTICE` 首两行 `Amagine3D` / `Copyright 2026 amagine-ai` ⇒ **可借鉴**（须带 `NOTICE` 与「声明改动了哪些文件」义务） |
| 元数据 | stars **6280**、forks 536、open issues 4、主语言 Python、许可 Apache-2.0、最近推送 **2026-10-22T07:42:50Z**（来源：`gh api repos/amagine-ai/Amagine3D`，取数日 2026-10-23）；克隆 HEAD 提交时间 `git log -1` = 2026-10-22 15:42:50 +0800（`eca44f28`） |
| 克隆 | D:\ai3d-survey\repos\amagine-ai__Amagine3D |
| 证据等级 | **读码**（读 README / docs / SKILL.md / references / Python 与 TS 源码 + `gh api` 元数据；**未** `npm install`、未起服务、未跑 `a3d`） |

## 1. 一句话定位

「需求 → 可编辑硬件结构」的**证据门控**本地 Web 工作台：Agent（OpenAI Codex SDK）在隔离 session 工作区里改一个声明式 `.a3d.json` 设计或 build123d Python 源码，再由一个**只读的编译驱动**执行源码、审计导出并出证据，产物保留可编辑源码 + 真 STEP（`README.md:36-42`、`docs/cad-workflow.md:13-21`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：自然语言需求 + 参考图 + 关键尺寸（`README.md:9`）；参考图与尺寸进入不可变 intent 文件（`skills/a3d-public/references/evidence-contract.md:23-41`，`reference_files` 带 `sha256`、`dimensions_mm` 每个维度标 `source`/`confidence`）。外观类需求允许 Agent 主动检索：优先本地 `a3d search`（Tavily）后端，但**检索片段只是不可信线索**，用于视觉判断的图必须真的取回并看过（`README.md:44-49`）。

**② 中间表示（两层，刻意分开）**：
- **可编辑设计**：要么声明式 DSL `model.a3d.json`（`design_language.py:11` 的 `SCHEMA = "a3d-design/v1"`），要么 build123d Python 源码。技能明确要求「**优先 DSL，连外壳也用 DSL；不支持的几何/绑定要报出名字再退 Python**」（`skills/a3d-text/SKILL.md:18`）。DSL 是**有界**的：文档字节、节点数、变更数、表达式深度等都有硬上限（`skills/a3d-public/design_language.py:13-15`），且该模块**不 import CAD 内核**（同文件 `:1`）。
- **不可变需求**：intent 文件（`schema` 形如 `evidence-cad-intent/v5`），字节不可改；改需求必须新文件 + 指向父 SHA + 理由 + 用户请求或外部证据记录（`skills/a3d-text/SKILL.md:58`、`docs/cad-workflow.md:65-72`）。

**③ 生成**：源码在「真实几何环境」里执行并写语义场景（scene）：物理零件、特征归属、接口、材料、BRep 主件、产物绑定（`README.md:116`）。几何走 build123d + OCP + Manifold + trimesh + lib3mf（`README.md:273-278`、`requirements.txt`）。

**④ 编排**：`React/Vite UI → Express API → Codex SDK/runtime → 隔离工作区 → a3d/Python CAD`（`README.md:207`）。每会话一个 Codex thread + 独立工作区与状态目录；Codex 以 `workspace-write` + `approvalPolicy: never` 运行，越界写入被沙箱挡（`README.md:199-203`、`docs/threat-model.md:11-14`）。产品层只加「一份紧凑 `AGENTS.md` + `a3d-text` 技能」，**由 Codex 自己决定何时调用哪个 a3d 命令**，而不是服务端驱动的修复状态机（`README.md:240-243`）。

**⑤ 执行**：单一编译入口 `a3d compile`（`bin/a3d.mjs:27` 把 `compile` 映射到 `cad_compile.py`）。该驱动**只做编排**：先校验 intent、再以无 shell 的子进程执行 Agent 写的源码、校验场景、选 BRep/Hybrid 编译路径、跑全部适用审计与一次新鲜渲染；**它从不编辑源码/intent/几何**（`skills/a3d-public/cad_compile.py:1-12`、`skills/a3d-public/references/cad-compile.md:1-5`）。子进程有一条 5400 秒（90 分钟）的聚合编译期限，超时 fail-closed 为 `COMPILE.DEADLINE_EXCEEDED` 并停止再起后续检查（`references/cad-compile.md:45-50`）。

**⑥ 验证（本仓最强的一层，四道闸）**：
1. **复用需要的不只是源码哈希没变**：已成功的草稿或自动通过的编译，只有在绑定的输入、输出、阶段、能力版本都仍匹配时才能复用；输入含源码/设计修订、适用 intent、scene 与 printer profile、本地 Python imports、显式声明的数据依赖（`docs/cad-workflow.md:55-63`）。
2. **需求与修复互相独立**：intent 拥有验收目标，源码/设计拥有控制量，scene 把物理零件与特征绑到 intent；冻结 intent 文件字节不可改，合法修订走新文件 + 父 SHA（`docs/cad-workflow.md:65-72`）。
3. **证据必须描述「这一次」尝试**：编译驱动在执行前按 SHA-256/大小/时间戳快照源码、intent、printer profile，运行中若变更即拒；失败的上游依赖使下游检查**保持 blocked 而不是被当成通过**（`docs/cad-workflow.md:74-81`、`cad-compile.md:32-39`）。
4. **自动通过仍须人/模型看图**：`pass=true` 只把结果置成 `awaiting-visual-review`（`visualReviewRequired=true`），Agent 必须对**当前** preview 用 `view_image`，与请求比对，并如实报告未解决的 warning（`docs/cad-workflow.md:83-88`）。`artifactStages` 分七段：`geometry`/`cadExport`/`tessellation`/`display`/`preview`/`manufacturing`/`visualReview`；通过的 `cadExport` 带有针对原 BRep 的 STEP 读回证据（`references/cad-agent-api.md:36-40`）。
   修复进度用**问题身份差分**表达，而不是「过了没有」：`new`/`newlyUnblocked`/`remaining`/`resolved`/`regressed`/`scope_changed`（`docs/cad-workflow.md:99-110`）。

**⑦ 交付**：可编辑源码 + 真 STEP 主件 + 派生 STL/STEP(显示)/3MF（`README.md:40`）；check report（`README.md:69`）；工位预览用生成好的五视图（等轴/前/侧/顶/底）渲染，**要求配置的模型/网关具备图像感知能力**，可用 `npm run doctor -- --vision` 做一次带两张小随机图的探针（`README.md:51-59`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明 | 证据 |
|---|---|---|
| **三层分离：需求 / 控制 / 绑定** | intent（验收目标，字节冻结）· source 或 `.a3d.json`（控制量）· scene（把物理零件与特征绑到 intent） | `skills/a3d-text/SKILL.md:11`、`docs/cad-workflow.md:65-72` |
| **DSL 优先、有界、与内核解耦** | 声明式 `.a3d.json` 有硬性大小/节点/深度上限，模块不 import 内核 ⇒ 校验便宜、可在无内核环境跑 | `skills/a3d-public/design_language.py:1-15` |
| **编译器是只读编排器** | 编执行、审计、渲染，但**永不**编辑源码/intent/几何；不跑自动修复循环、不设重试次数 | `cad_compile.py:1-12`、`docs/cad-workflow.md:20-21` |
| **尝试标记（UUID-bound attempt marker）** | 在本次产物前立刻落一个尝试标记，使「证据属于哪一次」可判，旧的成功渲染指针无法冒充本次 | `references/cad-compile.md:32-39` |
| **修复差分分类** | 用问题身份算 delta（新增/新解除阻塞/残留/已解决/回归/目标变更）；目标一变就不算修复 | `docs/cad-workflow.md:103-118` |
| **复用门禁 = 绑定输入集合** | 复用要求 phase、能力版本、intent 血缘、全部输入输出都仍校验通过 | `docs/cad-workflow.md:55-62` |
| **自动通过 ≠ 验收** | `pass=true` 只到 `awaiting-visual-review`；无「评审后接受」的独立 API，看图的动作不改变编译字段 | `docs/cad-workflow.md:83-88` |
| **「未测量=未知」而非「未测=通过」** | 未测量的配合关系记为未知；薄壁采样最小值不能反证告警为假 | `skills/a3d-text/SKILL.md:74`、`bin/a3d.mjs:59` |
| **能力契约按需批量拉取** | `a3d agent capabilities '{"designOps":[...]}'` 一次只取当前决策需要的契约；结果分页，用 `page.nextRequest` 翻 | `skills/a3d-text/SKILL.md:19-20` |
| **检索片段不可信** | 搜索片段只是线索，用作视觉判断的图必须真取回；尺寸仍来自图纸或显式假设 | `README.md:46-49` |
| **密钥只在运行时进程** | Tavily 账号 key 留在 runtime 进程，每个 turn 只拿到 loopback 临时能力，turn 结束即撤销 | `docs/threat-model.md:18-22` |

## 4. 运行条件与依赖

- **Node.js 22.19.0 或更新**（`README.md:134`；`.nvmrc` = `22.19.0`）；**Python 3.10 至 3.13**（`README.md:135`）；npm；现代桌面浏览器；**OpenAI Responses 兼容的 API key 或模型网关**（`README.md:138`）。
- Python 侧由 `scripts/setup-python.mjs` 建仓内 `.venv`，装 pin 死的 build123d 0.11.1、lib3mf 2.5.0、manifold3d 3.5.2、numpy 2.2.6、pillow 12.3.0、rtree 1.4.1、trimesh 5.0.0、networkx 3.4.2（`requirements.txt`）。**不需要装桌面 CAD 应用**（`README.md:140-142`）。
- 默认端口：Web `6160`、API `6161`（`README.md:154-155`、`:171-172`）。
- **本机（Windows / 16GB 显存 / Python 3.14.7）能不能跑**：不需要 GPU（几何是 CPU 内核，trimesh/Manifold 也是 CPU），显存无关；Windows 在 CI 覆盖范围内（`docs/CONTRIBUTING.md:73`）。**但本机 Python 3.14.7 落在声明支持区间 3.10–3.13 之外**（`README.md:135`，来源：本机 `python --version` 实测），且需要外接 LLM 网关与 key。⇒ 判断「需换 Python 版本 + 配 key 才可能跑」，**本卡未实测**。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | 自动通过不等于可制造：`pass=true` 仍停在 `awaiting-visual-review`；没有「看过图就算接受」的 API | `docs/cad-workflow.md:83-88` |
| 2 | 制造过、PNG 证据不全 ⇒ 结果 `awaiting-preview` 且 `pass=false`；只能复用**已通过**的制造证据重建显示层，且输入变了就不能复用 | `docs/cad-workflow.md:90-95`、`references/cad-agent-api.md:52-58` |
| 3 | 失败的上游让下游检查 **blocked 而非通过**；诊断性 preview 能定位故障但**不能**作为制造验收 | `docs/cad-workflow.md:74-81` |
| 4 | 子进程边界**不是 OS 沙箱**：Agent 写的 Python 拥有 Amagine3D 进程的权限 | `cad_compile.py:10-12` |
| 5 | 编译有一条 **5400 秒**聚合期限，超时 fail-closed 并停止再起检查（与任务运行期超时是两回事） | `references/cad-compile.md:45-50` |
| 6 | 本地应用、无应用级认证，只绑 `127.0.0.1`；对外暴露须另行设计鉴权/TLS/CSRF | `docs/threat-model.md:25-31` |
| 7 | 每 turn 硬超时 `AGENT_RUN_HARD_TIMEOUT_MS=7200000`（2 小时，绝对上限）、空闲超时默认 1800000（30 分钟） | `README.md:173-174` |
| 8 | 曲面连续性可能偏粗（官方自陈），只保证有效实体 + 可编辑源码 + 真 STEP + 制造检查 | `README.md:253` |
| 9 | 视觉审查依赖配置的模型/网关具备图像感知；若探针失败，视觉审查即为未完成，不得据视觉接受 CAD | `README.md:51-59` |
| 10 | 依法/合规地使用须读 `docs/THIRD_PARTY_NOTICES.md` 的源码分发边界与第三方归属 | `README.md:281-285` |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。

1. **「不可变需求 vs 可变控制 vs 绑定层」是本仓最值得抄的一件**：普通模型最容易在失败后偷改需求（把 target 调松来「通过」）。用字节冻结的 intent + 只按新文件+父 SHA 走修订 + 修复差分里的 `scope_changed` 显式标记，就能把「这不算修复」变成机器可判的事实。
2. **「编译器只编排、不修复」**：把「谁可以改」写死在架构里（编译驱动永不编辑源码/几何），普通模型乱改也改不到审计层。
3. **「有界 DSL 优先、Python 兜底」这条路线与我们的处境同构**：SolidWorks 的特征/草图/配合天然可以表达成有界声明式 JSON（参数 + 操作 + 引用），把不支持的几何显式报名字而不是静默退化——这正是「普通模型也能建出规范模型」的脚手架。
4. **`artifactStages` 分段 + 分段复用**：把「几何/导出/网格化/显示/预览/制造/视觉评审」拆成独立阶段，某段失败仍保留已通过的绑定产物（如 STEP），并允许只重跑派生段。我方可照此分级，避免一次失败全部重来。
5. **「未测量=未知，不是通过」**：与 globale 纪律「失败的计算不是通过」同族，可直接写成我方检查器的判据。
6. **不适合照搬的**：它面向**可打印 FDM 壳体**（Tavily 检索 + Bambu 打印剖面 + 五视图渲染），不涉参数化特征历史与装配配合；其 intent/QA 词汇（壁厚、打印朝向、板面排布）对我方 SolidWorks 场景只部分适用。

## 7. 许可与红线

**Apache-2.0**（`LICENSE:2-3`；`package.json` `"license": "Apache-2.0"`；`NOTICE` = `Amagine3D` / `Copyright 2026 amagine-ai`）。⇒ 可读、可抄、可改、可商用，但**必须**：① 保留 `NOTICE`（`README.md:291` 明确「See NOTICE for details」）；② 声明改动了哪些文件。同一 `NOTICE` 还逐条列出依赖的第三方版权（如 build123d `Copyright (c) 2022–2025 The build123d Contributors`，原始派生自 Apache-2.0 的 CadQuery）——`README.md:283-285` 另说明源码分发边界由 `docs/THIRD_PARTY_NOTICES.md` 界定。仓库内未见 AGPL/GPL 代码。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 许可与版权 | `LICENSE:2-3`、`NOTICE:1-2`、`package.json`（`license` 字段） |
| 定位、能力、示例 | `README.md:36-49`、`README.md:63-71` |
| 3D-native Agent 与内/外循环 | `README.md:86-116` |
| 证据门控工作流四道闸 | `docs/cad-workflow.md:53-95` |
| 修复差分语义 | `docs/cad-workflow.md:99-118` |
| 技能操作手册（草稿/契约/证据三段） | `skills/a3d-text/SKILL.md:1-78` |
| 编译边界（只编排、期限、快照） | `skills/a3d-public/references/cad-compile.md:1-50` |
| 任务 CLI 契约与阶段 | `skills/a3d-public/references/cad-agent-api.md:1-58` |
| intent 结构（含维度来源与置信度） | `skills/a3d-public/references/evidence-contract.md:17-70` |
| DSL 上界与零内核依赖 | `skills/a3d-public/design_language.py:1-15` |
| 编译驱动头（只编排、非沙箱） | `skills/a3d-public/cad_compile.py:1-12` |
| Agent 任务 API 与锁 | `skills/a3d-public/agent_api.py:1-55` |
| CLI 命令表 | `bin/a3d.mjs:23-36` |
| 运行时（Codex SDK 适配） | `packages/a3d-runtime/README.md`、`packages/a3d-runtime/src/runtime.ts:1-45` |
| 威胁模型（沙箱、密钥、无认证） | `docs/threat-model.md:1-40` |
| 依赖与版本 | `requirements.txt`、`.nvmrc` |
| 仓库元数据 | `gh api repos/amagine-ai/Amagine3D`（2026-10-23 取数） |

## 9. 未确认事项

1. **未实测运行**：没 `npm install`、没起服务、没跑 `a3d` ⇒ 全卡为**读码结论**；`requirements.txt` 里 build123d 0.11.1 能否在本机 Python 3.14.7 装上未验证（`README.md:135` 只声明到 3.13）；
2. **生成质量未验证**：`README.md:253` 自陈「曲面连续性可能偏粗」，但仓库内没有第三方的成功率/质量评测；测试文件数 **74 个**（`来源：Get-ChildItem tests -Recurse`），测的是服务端/运行时/产物逻辑，不是 LLM 建出的模型好不好；
3. **是不是真开源可商用**：`README.md:283-285` 提到「源码分发边界」由 `docs/THIRD_PARTY_NOTICES.md` 界定，我未逐行读完该文件以确认有无非商业条款；
4. **本项目是否复用了第三方闭源组件**未确认（`src/` 与 `server/` 未逐个读完）；
5. 元数据（stars 6280、推送 2026-10-22）是取数日快照，会变；
6. 未确认其 Tavily 检索默认是否开启（`README.md:169` 的 `CODEX_WEB_SEARCH_ENABLED` 默认值我没读到）。