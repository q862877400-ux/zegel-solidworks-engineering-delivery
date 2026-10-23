# text-to-cad（earthtojake）

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/earthtojake/text-to-cad · 官网 https://www.texttocad.dev · PyPI 包名 `cadgen` |
| 许可 | **MIT** —— 读仓库内 `LICENSE` 原文：第 1 行 `MIT License`，第 3 行 `Copyright (c) 2026 Thompson Labs LLC`（同一文件也在每个技能目录下，如 `skills/cad/LICENSE`）⇒ **可借鉴**（保留版权声明）；`packages/cadgen/pyproject.toml:10` 亦写 `license = "MIT"` |
| 元数据 | stars **22691**、forks 2214、open issues 33、主语言 Python、许可 MIT、最近推送 **2026-10-23T05:02:51Z**（来源：`gh api repos/earthtojake/text-to-cad`，取数日 2026-10-23） |
| 克隆 | D:\ai3d-survey\repos\earthtojake__text-to-cad |
| 证据等级 | **读码**（读 README / SKILL.md / references / Python 源码 + `gh api` 元数据；**未**安装 `cadgen`、未运行任何 cadgen 命令） |

## 1. 一句话定位

它不是「LLM 调工具画 CAD」，而是**让 agent 写一个普通 Python 模型脚本、由本地运行时执行它**：装饰器只声明输出，运行脚本即构建几何，产物是 STEP（主）与 STL/3MF/GLB（`skills/cad/SKILL.md:3`、`packages/cadgen/src/cadgen/authoring.py:1-16`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**① 输入**：自然语言或图片；技能按任务路由到不同 reference（`skills/cad/SKILL.md:16-27`）。请求里可带「提示词引用」——查看器把用户选中的实体复制成一行 ref 字符串（如 `/work/robot/STEP/assembly.step#o1.2.f7`），模型侧用 `scene.resolve(ref)` 取回几何（`skills/cad/SKILL.md:125-142`）。模糊尺寸要求「记录假设并验证」，而不是静默编数（`skills/cad/references/cad-brief.md`）。

**② 中间表示 = 一个普通 Python 脚本 + 装饰器声明**，没有自造 DSL、没有 IR 文件。模型是「无参装饰函数，返回 build123d 的 `Shape`」：`skills/cad/SKILL.md:55-58`；装饰器语义写在 `packages/cadgen/src/cadgen/authoring.py:9-14`（`@step()` 的 `out=` 默认是同目录同名 `.step`）。**参数化几何放普通工厂函数**，另一个配置＝另一个模型文件（`skills/cad/references/step-generation.md:70-98`）。

**③ 生成**：装饰器**只声明、不在 import/装饰期执行任何东西**（`authoring.py:18-21`）；顶层调用才跑整条流水线——新鲜度门禁 → 进度 → 增量包构建 → 写 `.step`/`.dxf`（`authoring.py:22-30`）。几何内核是 build123d + cadquery-ocp（`packages/cadgen/pyproject.toml:50-54`）。子件组合就是普通 Python：`from link_pin import link_pin` 后直接调用，返回几何而不是导出字节（`step-generation.md:179-195`）。

**④ 编排**：常驻「热 worker 池」——一个模型绑一个 worker，worker 忙就给一个临时 extra，spare 默认 2 个且已 import 完 build123d；准入按常驻 worker 树的内存估算，先回收空闲 worker（`packages/cadgen/src/cadgen/daemon/pool.py:1-26`）。路由铁律是「**没有任何构建等待另一个构建**」（`pool.py:3`）。

**⑤ 执行**：入口在 `packages/cadgen/src/cadgen/_internal/generation.py:1415`（`generate_step_targets`）与同文件 `:338`（`_generate_part_outputs`）；写盘走确定性 STEP 写出器与 store（`packages/cadgen/src/cadgen/step_export.py`）。

**⑥ 验证**（四层，彼此独立）：
- **新鲜度门禁**：`stale(model)` 五条判据——无记录；源码闭包 hash 变了（或按值 import 的常量变了）；任一记录的子件 stale 或其树 hash 与钉住值不同；树对象/被引用对象缺失；任一声明输出不匹配（`packages/cadgen/src/cadgen/store/gate.py:3-16`）。
- **输入追踪**：**不靠声明**——一个平台原生 tracer 把进程内所有库的 C 库 `open`/`CreateFile` 重写到自己的 wrapper，构建期记录每个被打开文件的 size 与 mtime（`packages/cadgen/native/filetrace.c:1-28`、`packages/cadgen/src/cadgen/_internal/filetrace.py:1-21`）。目录 glob 走 `os.listdir`/`os.scandir` 审计事件（`filetrace.py:12-15`）。
- **几何核对**：对**已保存的 STEP** 写小 Python 脚本 `read_scene`/`read_step` 读回，选定实体再测量；报告须写「测了什么、单位、阈值、选中几何」，且「失败的计算不是通过」（`skills/cad/references/inspection-and-validation.md:3-19`）。
- **视觉复核**：每次产生或可见改动几何后，自己渲染并读快照 `cadgen step snapshot STEP/bracket.step tmp/review.png`（`skills/cad/SKILL.md:182-191`）；快照只吃已保存文档、不吃模型脚本（`skills/cad/references/repair-loop.md:43-46`）。

**⑦ 交付**：STEP 为主输出，网格输出是叠在模型上的 `@stl`/`@threemf`/`@glb` 装饰器（`skills/cad/SKILL.md:107-121`）；另有工程图 PDF（`packages/cadgen/src/cadgen/eng_drawing.py`，PDF 经 ezdxf drawing add-on + matplotlib 渲染，见 `pyproject.toml:56-61`）与 DFM/DfAM 报告（`skills/dfm/SKILL.md:19-29`、`skills/dfam-check/SKILL.md:20-34`）。人看的界面走查看器：`cadgen viewer --host 127.0.0.1 --json --detach`，URL 从它唯一一行 JSON 里读、不要猜端口（`skills/cad/SKILL.md:213-223`）。

## 3. 技术方案要点（可迁移的机制）

| 机制 | 说明 | 证据 |
|---|---|---|
| **模型=普通脚本 + 装饰器声明** | 不自造 DSL：agent 只写 Python，契约由装饰器强制（无参数、返回裸 `Shape`、dict 返回被拒） | `skills/cad/SKILL.md:55-58`、`step-generation.md:99-103` |
| **装饰器只声明，不在 import 期执行** | 使模型文件可被安全 import/静态检查/组合，也让「检查声明」这一步很便宜 | `authoring.py:18-21`、`step-generation.md:42-44` |
| **依赖追踪三粒度** | 取模型函数＝按**结果**（钉子件树 hash）；取模块级字面量常量＝按**值**；取其它（helper/表达式）＝按**文件**整文件入闭包 | `step-generation.md:226-248` |
| **不声明输入的输入追踪** | 原生 tracer 挂在 C 库 open 上，`json.load`/`np.load`/OCCT C++ reader/字体加载全都记到 | `filetrace.py:1-10`、`native/filetrace.c:1-20` |
| **新鲜度门禁是显式判据表** | 五条 stale 子句 + `cadgen store why <model>.py` 把「为什么不重建」讲成人话，退出码 0/1 可脚本化 | `store/gate.py:3-16`、`step-generation.md:440-451` |
| **热 worker 池 + 内存准入** | 「没有任何构建等另一个构建」；extra worker 让父件 fan-out 子件时并行；spare 预热使新模型首次构建免 import 开销 | `daemon/pool.py:1-26` |
| **MCP 只承载查看器，不承载建模** | 服务端工具是 `cad_show`/`cad_view`/`cad_screenshot`/`cad_open`（读用户所见与所选），建模走「写文件 + 本地执行」 | `packages/cadgen/src/cadgen/mcp/server.py:366-390`、`skills/cad/SKILL.md:206-213` |
| **用户选择以字符串 ref 回传** | 选中实体被复制成 `文件#o1.2.f7` 形式，模型侧 `resolve()` 解析；引用绑定到该次保存的修订，重建后须重选 | `skills/cad/SKILL.md:125-142`、`step-generation.md:167` |
| **证据优先的规则引用** | DFM 要求逐条规则带 URL/版本/访问日/单位；查不到就「报缺失而不是造默认值」 | `skills/dfm/SKILL.md:51-59` |
| **检查脚本进仓库** | 探索脚本放 gitignore 的 `tmp/`，可复用的检查放 `checks/` 并提交，好让模型改了以后能重跑 | `inspection-and-validation.md:8-12` |

## 4. 运行条件与依赖

- Python `>=3.11`（`packages/cadgen/pyproject.toml:12`）；官方统一启动命令把解释器 pin 成 3.13，由 uv 托管：`uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.26 cadgen`（`skills/cad/SKILL.md:37`、`AGENTS.md:69-73`）。本机 `python --version` 报 3.14.7，与 pin 的 3.13 不同，但 uv 的 managed Python 会另装 3.13（`来源：本机 pwsh 实测 python 版本`）。
- 依赖：`build123d>=0.11.1,<0.12`、`cadquery-ocp-novtk>=7.9,<8`、`ezdxf`、`matplotlib`、`pillow`、`playwright==1.64.0`、`shapely`（`pyproject.toml:41-72`）。Playwright 浏览器首次快照时才下载（`pyproject.toml:63-69`）。
- 需要 `uv`；首次启动下载运行时，故需联网（`README.md:51-57`）。
- **本机（Windows / 16GB 显存 / Python 3.14）能不能跑**：显存无关（几何是 CPU 内核）；但有两条本机约束——① Windows 11 的 Smart App Control 会拦 OCP 未签名原生模块，表现为每次 `cadgen` 与 `import build123d` 都 `ImportError: DLL load failed while importing OCP`，且**该功能没有 per-app 例外**（只能整个关掉，或改在 WSL 里跑），`cadgen doctor` 会点名这个病因（`README.md:310-326`）；② 需装 uv 与联网。⇒ 判断「可跑但需前置条件」，**本卡未实测**。

## 5. 失败模式与已知坑

| # | 坑 | 来源 |
|---|---|---|
| 1 | **Windows 11 Smart App Control 拦 OCP**，无 per-app 例外；关掉后只能重装 Windows 才能再开 | `README.md:310-326` |
| 2 | **永远不要读自己的输出**：模型读它即将写的 `.step` ⇒ 输入每次都变，门禁永不能判 current，且几何依赖上次运行的遗留 | `step-generation.md:411-418` |
| 3 | 可选模块装配的暗礁：闭包按**构建时实际 import 到**的模块算，之后才出现的模块永不让模型过期，**无报错无警告**，须 `--force` | `step-generation.md:516-526` |
| 4 | 门禁追不到环境变量/工作目录/时间/随机性 ⇒ 配置必须写进源码或工厂参数 | `step-generation.md:453-456` |
| 5 | glob 兄弟模型输出目录的模型会「陈旧一次」（兄弟首次构建后） | `step-generation.md:426-430` |
| 6 | 一个文件里多个 `@step` 函数时，文件任一行改动使它们全 stale | `step-generation.md:282-283` |
| 7 | 快照命令只吃已保存文档，不吃模型脚本；缺输出要先跑模型 | `repair-loop.md:43-46` |
| 8 | 外来 STEP 往返丢失厂商元数据（PMI、GD&T） | `step-generation.md:504` |
| 9 | 遥测与崩溃报告**默认开启**（随机安装 ID、OS/agent 名、工具调用计数与失败原因词；不含文件名/路径/内容/提示词），`uvx cadgen telemetry off` 关闭 | `README.md:288-308` |
| 10 | `Playwright` 被**精确 pin** 在 1.64.0：放宽成范围会导致每次它移动都重新下载浏览器 | `pyproject.toml:63-69` |
| 11 | 未声明几何源（行内 `bd.Box` 等）不可被静态分析看到，故鼓励把几何放 `lib/` 工厂（否则整个文件一起 stale） | `step-generation.md:272-283` |

## 6. 对我方目标的可用处（机制层面）

我方目标：让**普通模型**也能建出**能用、规范**的模型（SolidWorks 自动化）。

1. **「模型＝普通脚本」这一层可移植，是普通模型最需要的脚手架**：普通模型写 Python 比写 COM 调用序列稳，而它把契约（无参数、返回裸 Shape、输出全在装饰器里）用装饰器强制出来——我方可以把同样的契约架在「脚本 → COM 调用序列」之上，让脚本而不是 MCP 工具承载建模。
2. **「不声明输入的输入追踪」值得照抄思路**：它的 native open-hook 解决的是「LLM 写的脚本里读什么文件没人声明」这个问题；我方对应物是「脚本读了哪些参考模型/配置文件」⇒ 装上同类追踪就能判「模型是否需要重建」。
3. **「门禁 + 人话解释」双件套**：判据表 + `store why` 把「为什么重建」讲成人话，退出码可脚本化——这是把验证责任转移给静态比对的可复用形态。
4. **「MCP 只做查看器」的架构取向**：它证明了 agent 建模不需要 MCP 承载建模工具；我方「运行时只能有一个 SolidWorks MCP」的死锁约束因此有另一种解法——把建模留在脚本/本地执行，MCP 只负责「给人看」。
5. **证据优先与缺失即报**：DFM 的「每个限额带 URL/版本/访问日/单位，查不到就报缺失」与我方「查不到就说查不到」同构，可直接沿用其条款措辞作为我方可制造性检查的模板。
6. **不适合照搬的**：内核是 OCP/build123d，产物是 STEP/网格且**无参数化历史树**；SolidWorks 的价值恰恰在特征历史与装配约束上，故它的「确定性 STEP 写出」等机制不构成我方等价物。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`：`MIT License` / `Copyright (c) 2026 Thompson Labs LLC`；`packages/cadgen/pyproject.toml:10` 亦声明 MIT）：可读、可抄、可改、可商用，**保留版权声明**。仓库内未见 AGPL/GPL 部分；12 个技能目录各带同一份 MIT（`来源：skills/*/LICENSE 均为 1095 bytes 的同一文本`）。红线：品牌资源（`apps/docs/public/brand/logo-*.svg`）是商标性资产，只可读不可挪用；遥测默认开启，引用其行为时须如实标注。

## 8. 证据清单

| 证据 | 出处 |
|---|---|
| 许可原文 | `LICENSE:1-3` |
| 定位与技能表 | `README.md:25-28`、`README.md:333-346` |
| 模型契约（脚本即工具） | `skills/cad/SKILL.md:55-58`、`skills/cad/references/step-generation.md:7-39` |
| 装饰器语义 | `packages/cadgen/src/cadgen/authoring.py:1-51` |
| 依赖与内核 | `packages/cadgen/pyproject.toml:41-72` |
| 依赖追踪三粒度 | `skills/cad/references/step-generation.md:226-248` |
| 新鲜度门禁五判据 | `packages/cadgen/src/cadgen/store/gate.py:3-16` |
| native 输入追踪 | `packages/cadgen/native/filetrace.c:1-28`、`packages/cadgen/src/cadgen/_internal/filetrace.py:1-21` |
| 热 worker 池 | `packages/cadgen/src/cadgen/daemon/pool.py:1-26` |
| 生成入口 | `packages/cadgen/src/cadgen/_internal/generation.py:338`、`:1415` |
| MCP 工具集（查看器） | `packages/cadgen/src/cadgen/mcp/server.py:366-390` |
| 提示词引用与 resolve | `skills/cad/SKILL.md:125-142` |
| 几何核对与检查脚本 | `skills/cad/references/inspection-and-validation.md:3-38` |
| 修复回路 | `skills/cad/references/repair-loop.md:1-58` |
| DFM 规则出处纪律 | `skills/dfm/SKILL.md:19-59` |
| DfAM 事实/结论分离 | `skills/dfam-check/SKILL.md:13-41` |
| Windows 坑 | `README.md:310-326` |
| 遥测 | `README.md:288-308` |
| 仓库元数据 | `gh api repos/earthtojake/text-to-cad`（2026-10-23 取数） |

## 9. 未确认事项

1. **未实测运行**：没装 uv/cadgen、没跑过任何 `cadgen` 命令 ⇒ 生成质量、STEP 保真度、快照链路均为**读码结论**，未经验证；
2. **「普通模型能否写出合格模型脚本」未确认**：仓库内 Python 测试文件共 **276 个**（`来源：Get-ChildItem tests -Recurse -Filter *.py`），测的是 cadgen 自身契约，不是 LLM 成功率——它的 stars 高不等于普通模型能用；
3. **本机 Smart App Control 当前状态未查**，故「本机能否跑」只是条件判断；
4. **遥测默认开启在本机是否可接受**未确认（是否需先 `cadgen telemetry off`）；
5. 元数据（stars 22691、推送 2026-10-23）是取数日的快照，会随时间变；
6. 我没有核验 `skills/*/LICENSE` 与根 `LICENSE` 是否**逐字节**相同，只核了首行/版权行与文件尺寸。