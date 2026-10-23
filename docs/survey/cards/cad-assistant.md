# CAD-Assistant

<!-- survey: class=B; repr=code; orchestration=loop; verify=visual; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/dimitrismallis/CAD-Assistant · 项目页 https://cadassistant.github.io/ · 论文 https://arxiv.org/abs/2412.13810 |
| 许可 | **CC BY-NC 4.0**（读克隆内 `LICENSE.md:1`「Attribution-NonCommercial 4.0 International」；`gh api` 因 GitHub 不认它为标准 SPDX 而返回 `NOASSERTION`）→ **只读思想**：非商用，代码与文本都不许搬进本仓 |
| 元数据 | stars 85 · 最近推送 2025-10-30T16:26:03Z · 语言 Python（来源：https://api.github.com/repos/dimitrismallis/CAD-Assistant ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant （HEAD `5fea473`，末次提交 2025-10-30T16:25:11Z；`git status --porcelain` 为空） |
| 证据等级 | 读码 |

## 1. 一句话定位

ICCV 2025 的「**训练-free 的工具增强 VLLM 建模代理**」：不训练任何模型，让一个云端多模态大模型在一个持久 Jupyter 内核里**写 FreeCAD Python 代码**，靠两个自建感知工具（草图识别器 / 实体识别器）把几何**序列化成 JSON + 渲染成图**再回喂，循环到它自己说 `TERMINATE`（`README.md:19-26`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

★ **输入形态**：多模态任意组合——**文字问题 + 草图/手绘命令图 + 3D 扫描**；评测时每个样本是一份预载好的 FreeCAD 工程（`.FCStd`）加一道四选一题（`README.md:19`、`README.md:56`）。★ 注意它**不是"图生模型"**，它主要是**改/读已有草图与实体**并在问答里出结论。

★ **中间表示**：**Python 代码**（FreeCAD API 调用串）是唯一的可执行中间表示；跨步状态全部留在同一个内核的变量里（`doc` / `sketch` / 自建变量，`cad_assistant/core.py:22-27`、`cad_assistant/init_freecad.py:45-75`）。几何的"可读形态"是两套临时产物：草图→JSON（几何 + 约束逐条，`cad_assistant/cad_tools/sketch_recognizer_code.py:127-161`、`:235-256`）、实体→STEP 文件 + 多视图 PNG（`cad_assistant/cad_tools/solid_recognizer_code.py:61-82`）。

- **生成**：OpenAI Responses API，模型 `gpt-4o-2024-08-06`、`temperature=0.0`、多轮用 `previous_response_id` 续接（`config.json:3`、`cad_assistant/openai_planner.py:137-142`）。回复按 `ACTION` 关键字切出「计划」、再用正则抓 ```` ```python ```` 代码块当动作（`cad_assistant/openai_planner.py:197-224`）。
- **编排**：单循环、双终止条件——`while iteration_count < max_iterations`（默认 10，`config.json:4`）+ 计划里出现 `TERMINATE`（`cad_assistant/core.py:152-224`）；每轮把上一步执行输出拼成 `Previous action result: ...` 作为下一轮输入（`cad_assistant/core.py:216`）。
- **执行**：`langchain_experimental.utilities.PythonREPL`，globals/locals 打成同一个 dict，所以跨 cell 变量可见（`cad_assistant/core.py:22-27`）；异常被吞成字符串 `ERROR: ...` 回灌给模型（`cad_assistant/core.py:255-286`）。
- **验证**：**视觉自检**——每步工具产出的 PNG 命名为 `step_image_<n>.png`，下一轮被读回来当图像输入发回模型（`cad_assistant/openai_planner.py:35-67`、`:118-128`）。评测层的判定是**选项字母比对**（正则 `Answer:\s*([ABCD])`，`sgp_cad_evaluator.py:274-288`），可跑多轮多数投票（`run_cad_evaluation.py:34-35`、`sgp_cad_evaluator.py:290-323`）。**没有几何合法性闸门**（不查闭合、不查流形、不查可制造）。
- **交付**：会话结束时把文档另存为 `final.FCStd`（`cad_assistant/core.py:243-252`）；实体识别器还会把最后一个对象导出成 `.stp`（`cad_assistant/cad_tools/solid_recognizer_code.py:64-70`），并把全过程记成 Jupyter notebook（`cad_assistant/logger.py:9`、`cad_assistant/core.py:322-338`）。

## 3. 技术方案要点（可迁移的机制）

- **给模型"感知外挂"而不是让它猜像素**：两个工具都返回「**结构化 JSON + 一张渲染图**」双重表示；提示词明确交代"你的视觉能力不完美，应该用工具帮你推理图像"（`cad_assistant/prompts/developer.j2:17-18`）。这是本卡最值得抄的一条（对我方＝把 SolidWorks 的特征树/草图状态序列化后回喂）。
- **文档切片注入**：FreeCAD API 文档是 Jinja 模板，**按类分段**用开关控制注入（`Sketch`/`LineSegment`/`Circle`/`Point`/`ArcOfCircle`/`Arc`/`Constraint`/`Extrusion`/`Solid` 九段，`cad_assistant/prompts/freecad_doc.j2:1-566` 的 `{% if include_* %}` 分段，配置见 `config.json:7-21`）。上下文可裁剪、幻觉可压低——我方 SolidWorks API 文档体量更大，这个机制直接可用。
- **工具必须有文档才能注册**：每个工具是 `<name>_code.py` + `<name>_doc.txt` 一对，缺任一个直接抛异常；文档被自动拼进系统提示词（`cad_assistant/core.py:103-150`、`cad_assistant/prompts.py:71-114`）。
- **初始化代码也当提示词用**：`init_freecad.py` 里的 `print(...)` 是**故意**的——它把"已经可用的 import 与变量"以执行输出的形式告诉模型（`cad_assistant/init_freecad.py:10`、`:19-31`、`:56-73`）。
- **失败即回灌，不即中断**：执行异常转成 `ERROR: ...` 文本喂回下一轮，让模型自己改（`cad_assistant/core.py:269-277`）。
- **双终止 + 迭代上限**：`TERMINATE` 是"模型认为做完了"，`max_iterations` 是"防它绕圈"；两者都走到同一个后处理（`cad_assistant/core.py:206-224`）。
- **状态外置成文件**：FreeCAD 的 `.FCStd` 里没有"构造几何"标志位，于是作者把它存成同名的 `_isconstruction.json` 旁挂文件，进内核时读回（`cad_assistant/core.py:50-65`、`README.md:88-90`）。⇒ 宿主软件没有的语义，用旁挂文件补，不改宿主。
- **过程即产物**：每步代码、输出、计划都落 notebook 与日志（`cad_assistant/logger.py:149-170`），事后可逐 cell 复跑审计。

## 4. 运行条件与依赖

- 形态：**Linux 容器**为主。Dockerfile 基于 `ubuntu:22.04`（`Dockerfile:1`），装 `freecad`（`Dockerfile:57-62`）、Miniconda 并 `conda env create -f occenv.yml`（`Dockerfile:64-79`）。
- 硬编码的 Linux 假设（两条，任一条都足以让 Windows 跑不动）：`sys.path.insert(0, '/usr/lib/freecad/lib')`（`cad_assistant/init_freecad.py:22`）；渲染走 `xvfb-run --auto-servernum conda run -n occenv python ...`（`cad_assistant/cad_tools/solid_recognizer_code.py:72-77`）。
- Python 3.10（`Dockerfile:14-19`）；主依赖 `langchain>=0.3.26`、`langchain-experimental>=0.3.0`、`openai>=1.0.0`、`jinja2`、`nbformat`（`requirements.txt:2-9`）；渲染环境另建 conda env `occenv`＝`python=3.10` + `pythonocc-core` + `pyqt5` + `Pillow`（`occenv.yml:1-9`）。
- 必须联网：`config.json:2` 要填 `openai_api_key`，模型在云端（`config.json:3`）⇒ **不是离线可跑**，也不是本地权重。
- 内置数据：`sgp_bench_samples/` 有 **1700 个** `FCStd` 样本目录（实测：`2D_*` **700 个** + `3D_*` **1000 个**，实测于本次读码，与 `README.md:56` 自述一致）。
- 本机判断（Windows / 默认 Python 3.14.7 / RTX 4080S 16GB）：**不能按仓库给的方式跑**（两条 Linux 硬编码 + 需要 OpenAI API key）。理论路径是 WSL2/Docker Desktop（`README.md:37-51` 的 docker 建法）；本次**未安装、未运行**，WSL 下能否装出 FreeCAD+pythonocc 未验证。显存：无本地模型，**不需要**（推理在云端）。

## 5. 失败模式与已知坑

- **写代码 = 全权限**：`PythonREPL` 的 globals 是 `{"__builtins__": __builtins__}`（`cad_assistant/core.py:22-23`），模型生成的代码在本机无限执行；这是"能力"也是"危险面"，我方若照做必须先收窄宿主权限。
- **循环预算硬上限 10 次**（`config.json:4`、`cad_assistant/core.py:152`）；到顶就 `MAX_ITERATIONS_REACHED` 收工（`cad_assistant/core.py:218-224`）⇒ 复杂件会被截断在半成品。
- **`previous_response_id` 续接把整段对话绑在单个供应商**（`cad_assistant/openai_planner.py:137-142`），换模型/换供应商要重写这一层；`except: pass` 还吞掉了请求异常（`cad_assistant/openai_planner.py:143-144`、`:191-192`）⇒ 静默失败风险。
- **视觉判断不可靠**：它靠"看图"决定对不对，渲染视角固定、线宽/字号是硬编码常量（`cad_assistant/cad_tools/sketch_recognizer_code.py:15-30` 的 `PlottingDefaults`/`GeometryDefaults`/`IMAGE_SIZE = 512`）⇒ 细小特征在小图上看不见。
- **适用域窄**：任务域是"读/改已有草图与实体 + 回答四选一"，不是"从零建可制造零件"；2D 分区只涉及单草图对象（`cad_assistant/init_freecad.py:61-66` 只在文档只有一个对象且名为 `sketch` 时才绑定 `sketch` 变量）。
- **宿主软件版本漂移无保护**：FreeCAD 由 PPA 装（`Dockerfile:58-62`），没有版本钉；API 行为随上游变。`README.md:6` 自述"这个仓库将包含官方代码库"，说明仍在陆续发布，接口不稳。
- **`_isconstruction` 旁挂文件是外部约定**（`cad_assistant/core.py:50-52`），文件不在就退化为全 False ⇒ 静默降级。

## 6. 对我方目标的可用处（机制层面）

目标：让**普通模型**也能建出**能用、规范**的 SolidWorks 模型。

1. **「序列化 + 渲染」双通道的感知工具**：普通模型的瓶颈是"看不见自己建的东西有多糟"。把 SolidWorks 的状态导成 JSON（特征树、草图几何与约束、尺寸）+ 标准三视图 PNG 回喂，是成本最低的能力补偿（形态见 `cad_assistant/cad_tools/solid_recognizer_code.py:39-58`）。
2. **文档按能力切片注入**：把 SolidWorks API 文档切成"每个接口族一段 + 开关"，按当前任务只注入需要的段——既省上下文也压幻觉（`cad_assistant/prompts/freecad_doc.j2:1-566` 的分段法 + `config.json:7-21` 的开关）。
3. **工具注册表双文件强制**：工具没文档就不许注册，"模型不知道有这工具"被结构上排除（`cad_assistant/core.py:121-129`）。
4. **双终止护栏**：`TERMINATE` + 硬上限 + 顶层 `run_until_terminate`（`cad_assistant/core.py:293-312`）——廉价但能拦住 90% 的失控。
5. **宿主缺的语义用旁挂文件补**：SolidWorks 里也有"草图构造线"这类导出后丢失的状态，可照此用 sidecar JSON 保真（`cad_assistant/core.py:50-65`）。
6. **执行即审计**：每步代码/输出/计划落 notebook（`cad_assistant/logger.py:149-170`）——我方每轮也应有同等的可复核轨迹。
7. **反面警示**：它的"验证"只是看图 + 读题选字母，**没有几何闸门**；我方必须补 export-readback / 几何有效性这一层，否则"看起来对"会被当成"对"。

## 7. 许可与红线

- 顶层 `LICENSE.md` 是 **CC BY-NC 4.0**（`LICENSE.md:1`）⇒ **只读思想**：非商用；**不抄代码、不抄文本、不抄提示词模板**。`README.md:112-114` 也自述"Attribution-NonCommercial License"。
- 内含第三方副本另有许可：vendored `SketchGraphs` 自述 `license='MIT'`（`SketchGraphs/setup.py:7`），其中 `onshape/` 目录是 **MIT / Copyright (c) 2020 PTC Inc.**（`SketchGraphs/sketchgraphs/onshape/LICENSE:1-3`）⇒ 这部分是**上游 MIT 代码**，与 CAD-Assistant 自身的 NC 条款不是一回事；要用只能去上游原仓取，不要从这个 NC 仓库里拿。
- 工具实现自述改编自 Vitruvion / SketchGraphs（`README.md:88`）⇒ 又一层上游溯源义务。
- 红线：本仓**不得**把它的 `prompts/*.j2`、`cad_tools/*` 复制进来（NC + 上游改编链）。可写的只有"机制描述"。

## 8. 证据清单

- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\LICENSE.md:1`（CC BY-NC 4.0 首行）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\README.md:19-26`（多模态输入 + FreeCAD 内执行）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\README.md:56`（1700 个 FCStd：700 个 2D + 1000 个 3D，自述）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\README.md:84-94`（两个工具与来源）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\core.py:22-27`（PythonREPL 共享 globals）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\core.py:103-150`（工具注册：code+doc 成对）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\core.py:152-224`（迭代循环、TERMINATE、MAX_ITERATIONS）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\core.py:243-252`（另存 final.FCStd）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\core.py:50-65`（`_isconstruction.json` 旁挂）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\openai_planner.py:137-142`（Responses API + previous_response_id）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\openai_planner.py:35-67`、`:118-128`（上一轮渲染图回喂）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\openai_planner.py:197-224`（ACTION/代码块解析）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\prompts\freecad_doc.j2:1-566`（按类分段 + include_* 开关）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\prompts\developer.j2:17-18`（"你的视觉能力不完美"）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\prompts.py:56-66`、`:71-114`（文档切片与工具文档注入）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\cad_tools\solid_recognizer_code.py:39-58`（实体→JSON）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\cad_tools\solid_recognizer_code.py:61-82`（STEP 导出 + xvfb-run OCC 渲染 + 改名 step_image_）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\cad_assistant\init_freecad.py:10`、`:22`（print 当提示词；Linux 路径）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\config.json:2-4`、`:7-25`（key/model/max_steps/文档开关/工具表）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\sgp_cad_evaluator.py:274-288`、`:290-323`（答案正则 + 多数投票）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\Dockerfile:1`、`:14-19`、`:57-62`、`:64-79`（ubuntu 22.04 / py3.10 / freecad / occenv）
- `D:\ai3d-survey\repos\dimitrismallis__CAD-Assistant\SketchGraphs\setup.py:7`、`SketchGraphs\sketchgraphs\onshape\LICENSE:1-3`（内含 MIT 副本）
- 实测：`Get-ChildItem sgp_bench_samples -Directory` ⇒ 1700 个目录，`2D_*` 700 个、`3D_*` 1000 个（2026-10-24）
- https://api.github.com/repos/dimitrismallis/CAD-Assistant （stars/推送/语言/`license=NOASSERTION`，取数日 2026-10-24）

## 9. 未确认事项

- **未安装、未运行**：结论全部读码得来；WSL2/Docker Desktop 下能否建出 FreeCAD + pythonocc 环境**未验证**。
- 论文里的分数（SGP-Bench 2D/3D 上的准确率）本卡未核对，仓库也未附结果文件 ⇒ 不引用具体数值。
- 云端模型的计费与限流对"可跑性"的影响**查不到**（仓库无相关说明）。
- 换掉 OpenAI 换成别的供应商（或本地 VLM）后这套 planner 还能不能工作**未验证**——`previous_response_id` 是 OpenAI 专有字段。
- `class=B`（代码回环）是按本仓 A–J 枚举的判读：它确实是"写代码→执行→看结果→再写"的回环，但它**不是生成式建模器**（主要在改/读已有模型 + 答题），与 earthtojake/agentcad 那种"从零建"的 B 类不完全同质；R7 汇总时若要区分"建模型 B"与"问答型 B"，这张卡属于后者。
