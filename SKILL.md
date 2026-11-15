---
name: solidworks-automation
description: "SolidWorks CAD 自动化技能，优先覆盖经验证的零件、孔槽、装配、工程图、导出和交付复核；所有能力等级以 capabilities.yaml 为准，未验证能力必须走人工复核。"
metadata: { "openclaw": { "homepage": "https://github.com/wzyn20051216/solidworks-automation-skill", "os": ["win32"], "requires": { "anyBins": ["python", "py"] } } }
---

# SolidWorks 自动化技能

## 快速开始

### 环境要求

- Windows 系统；原生 SolidWorks 格式需要 SolidWorks，开放格式无头写入不要求安装 CAD 软件
- Python 3.10+；原生 Windows CAD 自动化另需 `pywin32` / `comtypes`
- MCP/工具化调用需要 `mcp` / `pydantic`
- 工程图最终交付审查需要 `PyMuPDF`；它从 SolidWorks 导出 PDF 回读实际尺寸文字边界，已包含在 `requirements.txt`
- 处理 GLB/GLTF/OBJ/STL 网格参考模型时，可能还需要 `trimesh` / `pygltflib` / `numpy` / `Pillow`
- 如果通过 OpenClaw 使用，确保技能目录位于 `~/.openclaw/skills/solidworks-automation/` 或 `~/.agents/skills/solidworks-automation/`

### 入口自检

所有代理在执行 SolidWorks 自动化前，先运行技能自检：

```bash
python SKILL_DIR/scripts/sw_preflight.py
```

桌面端或 CLI 执行前建议先运行环境诊断：

```powershell
python SKILL_DIR/scripts/cad_studio.py doctor
```

`capabilities.yaml` 是 Skill、MCP、队列和 UI 共用的能力唯一真源。能力等级为 `verified`、`pilot`、`reference_only` 或 `not_implemented`；后两者不得作为无人值守交付。该清单还维护 Python、C# PIA/Add-in、原生 C++、SWBasic、OCCT 和外部求解器的原子操作路由；执行前可用 `python scripts/backend_router.py --list` 查询，规则见 `references/language-backend-routing.md`。

### 多入口与多后端

- CAD Studio 与 Skill/CLI/MCP 是平级入口，共用 Automation Job、NeutralCadDocument、Preview Manifest、Evidence Graph 和能力清单。
- 检测不到 SolidWorks/AutoCAD 时，只阻断 `SLDPRT/SLDASM/SLDDRW/DWG` 等原生格式；开放格式任务优先路由到 `headless_open_format_writing`。
- 无头写入使用 `scripts/headless_cad_writer.py`；OCCT/OCP 隔离进程真实写入 STEP、IGES、BREP、STL、OBJ、GLB，二维后端写入 DXF、SVG、PDF、PNG，并生成几何与 SHA-256 证据。
- DXF 交付会额外生成 `preview_scene`；已有 DXF 可通过 `python scripts/cad_studio.py preview-dxf --input drawing.dxf --output drawing.scene.json` 或 MCP `cadstudio_build_dxf_preview_scene` 转成受限 PreviewScene。该命令只读白名单实体并拒绝覆盖旧文件。
- OCCT 当前覆盖盒体、圆柱、布尔合并、圆柱孔切除、直纹/受限平滑 Loft、直线/单圆弧 Sweep、闭壳 Knit 和开放面 Thicken；复杂路径、自交偏置或缺少 OCP 运行时时保持 `blocked`。禁止通过改扩展名或空文件伪造支持。
- `delivery-preview` 只允许显示当前任务真实产物；固定样例必须标记 `demo-showcase` 与 `isDemo: true`，不得进入交付判断。

规则：

1. 检测到缺少 `comtypes` / `win32com` / `pythoncom` 时，向用户弹出友好确认：
   `检测到当前 Python 环境缺少 comtypes / win32com 库，是否授权 AI 自动为您配置本地环境？[Y/N]`
2. 用户输入 `Y` / `yes` 后，代理可在本地 shell 中自动执行 `python -m pip install "pywin32>=305" "comtypes>=1.2.0"` 补齐依赖；用户拒绝时停止并给出手动安装命令。
3. 检测不到 SolidWorks 安装或 COM 注册时，停止原生 SolidWorks 操作；若原生格式并非必需且 `fallbackPolicy=allow_open_formats`，继续执行无头开放格式后端，不要把整个任务误标为失败。

### Python 依赖提醒

按任务最小化安装依赖，不要在普通零件建模时强制安装网格转换库；工程图交付需要标准 `requirements.txt` 中的 PyMuPDF：

```powershell
# 核心 SolidWorks COM 自动化依赖
python -m pip install -r SKILL_DIR\requirements.txt

# 仅在需要 GLB/GLTF/OBJ/STL 网格检查、缩放或转换时安装
python -m pip install -r SKILL_DIR\requirements-mesh.txt
```

执行涉及 GLB/GLTF/FBX/BLEND 转 OBJ/STL 的任务前，先用 `importlib.util.find_spec()` 检查
`trimesh`、`pygltflib`、`PIL` 是否可用；缺失时先提示用户需要安装哪些库和用途，再安装或给出手动命令。

### 连接 SolidWorks

```python
import sys; sys.path.insert(0, r"SKILL_DIR/scripts")
from sw_connect import mm
from sw_part import sketch, sketch_circle, extrude_boss
from sw_session import SolidWorksSession

session = SolidWorksSession()
model = session.new_part()

with sketch(model, "Front Plane") as sketch_name:
    sketch_circle(model, 0, 0, mm(25))

extrude_boss(model, sketch_name, mm(50))
session.save(model, r"C:\temp\cylinder.sldprt")
session.export(model, r"C:\temp\cylinder.step")
```

> 将 `SKILL_DIR` 替换为此技能的实际安装路径。

## 核心工作流

根据用户需求选择对应模块：

| 需求 | 脚本 | 参考文档 |
|---|---|---|
| 入口自检与依赖补齐 | `scripts/sw_preflight.py` | `references/troubleshooting.md` |
| 无 CAD 开放格式写入 | `scripts/headless_cad_writer.py`、`scripts/cad_studio.py write-open-format` | `capabilities.yaml`、公共 CAD Core Schema |
| 高级能力/类型库探测 | `scripts/sw_capability_probe.py` | `references/complex-mechanical-routing.md` |
| Python/C#/C++/SWBasic/OCCT 后端选择 | `scripts/backend_router.py` | `references/language-backend-routing.md`、`capabilities.yaml` |
| C# 进程内 Add-in 宿主、事件与 UI | `scripts/sw_addin_host.ps1`、`scripts/sw_addin_host.py` | `references/solidworks-addin-host.md` |
| 多模型宏生成防护 | `scripts/sw_macro_guard.py` | `references/openclaw.md` |
| 友好会话 API | `scripts/sw_session.py` | - |
| 连接与文档管理 | `scripts/sw_connect.py` | - |
| 外观与材质 | `scripts/sw_appearance.py` | `references/appearance.md` |
| 零件建模（草图+特征） | `scripts/sw_part.py` | `references/part-modeling.md` |
| 标准外啮合直齿轮实体 | **当前无可用生成器**（折线 `sw_gear.py` 已禁用；真曲线 `scripts/gear_geometry.py` 待验证） | `references/gears.md` |
| 盲孔/沉孔/沉头孔/半圆端槽与孔位验收 | `scripts/sw_hole_features.py`、`scripts/sw_review.py` | `references/complex-hole-features.md`、`references/review.md` |
| 自然语言到参数化设计计划 / VibeCAD | `subskills/solidworks-vibecad/scripts/plan_from_brief.py` | `subskills/solidworks-vibecad/SKILL.md`、`subskills/solidworks-vibecad/README.md` |
| 多圆角/倒角 CNC 机加工件 | `subskills/solidworks-fillet-chamfer-cnc/scripts/create_cnc_mount_template.py`；高级圆角用 `verify_advanced_fillets.py` | `subskills/solidworks-fillet-chamfer-cnc/SKILL.md`、`subskills/solidworks-fillet-chamfer-cnc/references/cnc-fillet-chamfer-lessons.md` |
| 螺丝孔/螺纹孔、攻丝底孔 | `subskills/solidworks-threaded-holes/scripts/create_threaded_hole_template.py` | `subskills/solidworks-threaded-holes/SKILL.md`、`subskills/solidworks-threaded-holes/references/threaded-hole-lessons.md` |
| AutoCAD DWG/DXF 二维绘图、线稿转 CAD、批量改图 | `subskills/autocad-automation/scripts/acad_draw.py`、`subskills/autocad-automation/scripts/acad_review.py` | `subskills/autocad-automation/SKILL.md`、`subskills/autocad-automation/references/troubleshooting.md` |
| 装配体操作、齿轮联动/铰链/可拖动运动配合 | `scripts/sw_assembly.py` | `references/assembly.md` |
| Motion Study 运动算例、旋转马达与结果审计 | `scripts/sw_motion.py` | `references/motion-study.md`、`references/complex-mechanical-routing.md` |
| 工程图出图 | `scripts/sw_drawing.py` | `references/drawing.md` |
| 文件导出 | `scripts/sw_export.py` | `references/export.md` |
| 配置族创建/激活、参数修改与自定义属性 | `scripts/sw_document_data.py` | `references/advanced.md` |
| 装配 BOM CSV 与 Pack and Go | `scripts/sw_delivery.py` | `references/export.md` |
| OBJ/STL 高还原网格参考导入 | `scripts/sw_import_mesh_reference.py` | `references/mesh-reference-import.md` |
| 结果自审查 | `scripts/sw_review.py` | `references/review.md` |
| 语义实体引用 | `scripts/sw_entity_reference.py` | 逐步替代 Face1/Edge1 和屏幕坐标 |
| DFM 制造风险复核 | `scripts/dfm_review.py`、`scripts/dfm_profiles.py`、`scripts/cad_studio.py check-dfm` | 供应商 profile、B-Rep 证据、机加工、钣金、激光切割和 3D 打印的结构化规则检查 |
| Routing 中性复核与前置 | `scripts/routing_review.py`、`scripts/cad_studio.py check-routing`、`scripts/cad_studio.py routing-preflight` | 端点、分段、长度、弯曲半径、碰撞/间隙、支撑、Routing BOM；原生写入必须等加载项/许可证证据 |
| FEA 前置、输入与受限求解 | `scripts/fea_analysis.py`、`scripts/fea_convergence.py`、`scripts/cad_studio.py fea-preflight/prepare-fea/run-fea/run-fea-convergence` | CalculiX 2.23 已验证线性/非线性静力、塑性、面接触、最终步 COPEN/CPRESS/CSLIP 与线性/非线性网格收敛；全部仍需工程复核 |
| 复杂曲面与模具 | `scripts/advanced_geometry.py`、`scripts/advanced_geometry_ocp.py`、`scripts/advanced_surface_ocp.py`、`scripts/cad_studio.py review-advanced-geometry/create-ocp-loft/create-ocp-surface` | 直纹/平滑 Loft、受限 Sweep/Knit/Thicken 可写并重开 B-Rep；G1/G2 和曲率半径只返回离散采样证据 |
| 本地 MCP Server | `mcp-server/server.py` | `mcp-server/README.md`、`references/mcp-server.md` |
| MCP 协议验证 | `scripts/validate_mcp.py` | `mcp-server/README.md` |
| 未封装 API 查证 | - | `references/api-lookup.md` |
| OpenClaw 控制 SolidWorks | - | `references/openclaw.md` |
| 钣金/焊件/仿真/属性 | - | `references/advanced.md` |
| 企业 Agent / 本地优先与云 RAG | `apps/desktop/cad_workbench/knowledge_retrieval.py` | `references/enterprise-agent-rag.md` |
| Codex/Claude/Gemini/OpenCode Provider Adapter | `apps/desktop/cad_workbench/agent_providers.py` | `references/agent-provider-architecture.md` |
| 综合机械工程 DAG 自动编排 | `apps/desktop/cad_workbench/engineering_orchestrator.py` | `references/complex-mechanical-routing.md` |
| 常见错误排查 | - | `references/troubleshooting.md` |

Pack and Go 在 SW2026 SP01.1 的基础两零件装配上已连续三次通过原生回归：`SavePackAndGo()` 实际输出装配体和两个零件，状态码均为 0，未使用暂存回退。部分版本的 `GetDocumentNames()` 仍可能在保存前只枚举顶层文件；不要用 `AddExternalDocuments` 补装配体原生零件，应先执行原生保存，再审计实际落盘依赖。若落盘仍缺依赖，`scripts/sw_delivery.py::pack_and_go()` 默认按 `GetDependencies2` 生成带 manifest 和 SHA-256 的 `pilot` 暂存包；需要严格原生语义时使用 `fallback_policy="blocked"`。外部引用、Toolbox、配置和工程图仍必须人工复核，因此总能力保持 `pilot`。

## OpenClaw 协作方式

1. 先确认 SolidWorks 版本、界面语言、输入文件路径、输出路径，以及目标操作（建模 / 装配 / 出图 / 导出）。
2. 优先复用 `{baseDir}/scripts` 下已有模块，不要重复手写 COM 连接逻辑。
3. 在 OpenClaw 的 `exec` / `shell` 能力中执行短小、一次性的 Python 脚本，最小导入集如下：

```python
import sys
sys.path.insert(0, r"{baseDir}/scripts")
from sw_connect import connect_solidworks, mm, deg, new_document
```

4. 执行后检查返回对象是否为 `None`、保存/导出是否成功、输出文件是否落盘。
5. 生成或修改模型后必须做结果自审查：导出至少一个等轴测预览图，必要时导出前/俯/右视图，并通过截图或 BMP 目视检查几何是否符合用户意图。
6. 如果需要更完整的 OpenClaw 工作流、提示词示例和排障建议，再读取 `references/openclaw.md`。

## 使用流程

1. 先根据原子操作运行 `backend_router.py`，再结合 `preferredBackend`、`requiredOutputs`、`nativeFormatRequired` 和 `fallbackPolicy` 判定后端；不要先假定 Python、C# 或 SolidWorks 必然可用。普通任务优先 Automation 等价接口，明确要求仅非托管 C++ 支持的原始 `I*` 指针语义时才升级到原生 C++。
   事件订阅、PropertyManagerPage、TaskPane 或长期驻留 UI 走 `solidworks_addin_ui_events` 路由，优先 C# Add-in；必须检查 HKLM 注册、64 位 TLB 注册和 `host-status.json`，不能只凭 `LoadAddIn=0` 宣称成功。SW2026 的 PMP Handler 必须公开、COM 可见并提供 `IDispatch` class interface。
2. 需要原生 SolidWorks 格式时运行 `sw_preflight.py`；缺依赖则请求用户授权自动安装，缺 SolidWorks 则只阻断原生阶段。
3. 不需要原生格式或允许开放格式回退时，运行 `python scripts/cad_studio.py write-open-format --input model.cadstudio.json --out-dir output`。
4. 需要制造性快速复核时，运行 `python scripts/cad_studio.py check-dfm --input model.cadstudio.json --output output/dfm_report.json --process machining`；支持 `--profile supplier.json` 和 `--brep-evidence brep.json`。报告缺少材料、壁厚、K 因子、割缝、成型空间或要求的 B-Rep 证据时返回 `blocked`，规则通过也必须人工复核。
5. 原生 SolidWorks 路线优先用 `SolidWorksSession()` 管理连接、打开、新建、保存、导出；需要底层控制时再组合 `sw_connect.py`、`sw_part.py` 等函数。
6. 当用户需求偏自然语言、参数不完整或需要“行业知识库 + 提示词模板 + 参数化设计计划”时，先读取 `subskills/solidworks-vibecad/SKILL.md`，生成 `design_plan.json` 和执行摘要。
7. 圆角/倒角很多的 CNC 件、安装座、连接块、支架，先读取 `subskills/solidworks-fillet-chamfer-cnc/SKILL.md`，按“基础体 -> 外轮廓圆角/倒角 -> 孔槽切除 -> 孔口倒角 -> 审查”的稳定顺序执行。
8. 螺丝孔、螺纹孔、攻牙孔、M3/M4/M5/M6/M8 盲孔或贯穿孔任务，先读取 `subskills/solidworks-threaded-holes/SKILL.md`；默认按“参数/孔位校验 -> 攻丝底孔 -> Metric Tap 真实 Thread -> CosmeticThread/证据螺旋线降级 -> 孔口倒角 -> 重建后特征证据 -> 属性和审查”的稳定路线执行。Hole Wizard、外螺纹、英制/管螺纹和现有零件改孔仍按 pilot 处理。

**齿轮路由门禁：** 当用户说“画/建模/生成齿轮”时，先读取 `references/gears.md`。**全项目禁止折线模拟曲线**（把渐开线采样成点列再逐段连直线）：旧 `archive/inherited-methods/scripts/sw_gear.py` 的 `involute_segments` 弦线离散已明令禁用，不得再作为实现来源。真曲线实现 `scripts/gear_geometry.py`（方程式驱动渐开线 + 摆线齿根）尚未通过真机验证，**当前不提供可用的齿轮实体生成器**；遇到建齿轮需求应如实说明“尚无可验收生成器”，不得回退到折线、也不得用 Gear Mate 冒充实体。制造任务不得臆造参数。斜齿、锥齿、内齿、齿条、蜗轮蜗杆、变位或生产级修形/侧隙必须转专用路线或人工复核。“齿轮联动/传动/配合”才路由到 `sw_assembly.add_gear_mate_by_cylinders()`。

9. 普通盲孔、通孔、圆柱沉孔、锥形沉头孔、半圆端槽或孔阵列任务，读取 `references/complex-hole-features.md` 并优先调用 `scripts/sw_hole_features.py`；创建参数证据必须再与 `collect_geometry_measurements()`、`validate_hole_positions()` 和剖视图交叉复核。
10. SolidWorks 零件图、装配图、GB/T 工程图、尺寸链、孔表、BOM、标题栏或工程图审视任务，先读取 `subskills/solidworks-engineering-drawing/SKILL.md`；该子技能消费根技能的模型、孔槽和属性证据。AutoCAD 的 DWG/DXF、二维图纸、线稿转 CAD、批量改图或 AutoCAD 原生预览任务，读取 `subskills/autocad-automation/SKILL.md`。机械/3D 打印开孔交付必须按可制造图纸处理：所有孔、槽、接口、水口、螺丝孔和螺丝柱同时给出规格、数量和定位尺寸；图面拥挤时用孔表/槽表，不得用长引线替代关键尺寸。
11. 当用户要求真实产品“原版外观”“1:1 复刻”“不像概念版”，先读取 `references/mesh-reference-import.md`：公开网格/蓝图参考优先，不要在低保真手搓底稿上反复精修；需要导入 OBJ/STL 时优先用 `scripts/sw_import_mesh_reference.py`。
12. 如果必须由大模型生成 VBA 宏，先使用 `sw_macro_guard.py` 做模型分流、代码校验、重试和本地模板兜底。
13. 使用 `session.export()` 或 `sw_export.py` 保存/导出文件。
14. 使用 `sw_review.py` 导出预览图并自审查；如果有 GUI/桌面截图能力，打开 SolidWorks 视图截图复核。
15. 遇到钣金、焊件、复杂曲面、模具、Routing、Simulation/FEA、复杂 Motion 或配置族任务，先运行 `sw_capability_probe.py` 并读取 `references/complex-mechanical-routing.md`；Routing 使用 `routing-preflight/check-routing`，FEA 使用 `fea-preflight/prepare-fea/run-fea/run-fea-convergence`，复杂曲面使用 `review-advanced-geometry/create-ocp-loft/create-ocp-surface`。FEA 和高级曲面求解通过仍为 `review_required`。
16. 需要企业/项目机械知识时读取 `references/enterprise-agent-rag.md`；默认只用本地知识，云 RAG 必须显式启用、声明 `external_network` 并完成人工审批。
17. 当一个需求同时跨越零件、孔槽/圆角、装配 Mate、Motion、工程图/BOM 和多格式交付中的两个以上工程域时，调用 `apps/desktop/cad_workbench/engineering_orchestrator.py` 生成阶段 DAG。必须按依赖串行执行关键 CAD 写操作，每阶段独立保存产物和验收证据；局部修改只重规划受影响阶段及其后继，禁止把整项工程塞进一条超长 Prompt 后一次性宣称完成。

### 机械图纸默认底线

以后凡是本技能参与 CAD/机械结构/3D 打印项目，都默认执行这些底线：

1. 不把“看得懂的示意图”当成“能制造的工程图”。只要涉及开孔、开槽、接口、装配孔或打印外壳，必须补齐外形尺寸、壁厚/底厚、孔槽规格和定位尺寸。
2. 用户要求“中国常用格式”“国标风格”“严格规范”时，必须采用国内机械制图习惯：规范图幅/图框/标题栏、仿宋中文、分层线型、中心线/虚线、真实标注实体和技术要求。
3. 长引线只能做局部说明，不能替代尺寸链；不得跨视图、压孔、压中心线、压尺寸文字或侵入标题栏。
4. 密集孔槽必须优先用孔表、槽表或孔槽明细表，表内写清部位、规格、数量和定位；表格不能成为逃避定位尺寸的借口。
5. 交付前必须目视复核预览图，发现漏标、重叠、压线或标题栏侵入时先返工再汇报。

### 高还原外观/公开网格参考模型

当用户要求汽车、消费电子、雕塑等真实对象外观高还原时，先区分“视觉参考模型”和“工程可制造参数模型”：

1. 若用户要“像原版”，优先索取或查找公开 3D 模型/多视图蓝图，并记录来源、作者、许可证和下载日期；不要声称生成的是官方 Class-A 或扫描级模型。
2. `.glb/.gltf/.fbx/.blend` 先转换为 `.obj/.stl`；OBJ 优先保留材质，STL 作为无材质兜底。
3. 导入前用包围盒确认坐标轴和尺度，再按真实公称尺寸缩放。
4. 如果需要 Python 转换/缩放，先确认 `requirements-mesh.txt` 中的可选依赖可用；缺失时说明用途并提示安装。
5. OBJ/STL 导入 SolidWorks 时用 `sw_import_mesh_reference.py`；关键写法是 `LoadFile4(path, "r", create_empty_dispatch_variant(), errors)`，不要用 `OpenDoc6()` 或把 `None` 传给 `LoadFile4()`。
6. 结果审查必须看四视图和关键识别特征；“预览非空白”不能替代“像用户指定对象”。
7. 若用户后续要工程可编辑结构，应基于网格参考分件逆向重建，并明确说明网格导入件不是参数化实体。

### 多色外观要求

当模型包含车身、玻璃、灯组、轮胎、轮毂或其他多种颜色时：

1. 读取 `references/appearance.md`，统一使用 `sw_appearance.py`，禁止把普通 Python `list` 直接传给 COM 材质属性。
2. 源零件先设置文档级颜色；装配体中需要覆盖时再用组件级颜色。
3. 每次设置后调用 `verify_appearance()` 或 `apply_component_palette()` 回读 RGB；只检查 setter 返回值不算通过。
4. 保存与截图前调用 `model.ClearSelection2(True)`；`sw_review.save_preview()` 已内置该清理。
5. 目视确认至少三种预期颜色真实可见；“预览非空白”不能替代颜色检查。
6. 外观异常时先运行 `tests/solidworks_appearance_regression.py`，再重建用户模型。

### MCP Server 使用

当用户要求“让 SolidWorks 支持 MCP”“接入 Codex/Claude Desktop 工具调用”“不要每次生成一大段 Python 脚本”时：

1. 读取 `mcp-server/README.md`。
2. 若用户要求自动配置 MCP，优先运行多客户端注册器：`powershell -ExecutionPolicy Bypass -File mcp-server/register_all_ai_mcp.ps1 -InstallDependencies`；它会尝试注册 Codex、Claude Code、Claude Desktop、Cursor、Windsurf。
3. 使用本地 `stdio` MCP server：`python mcp-server/server.py`。
4. 无 CAD 开放格式写入优先调用 `cadstudio_write_open_format`；DFM、Routing、FEA 和复杂几何分别调用 `cadstudio_check_dfm`、`cadstudio_check_routing`、`cadstudio_routing_preflight`、`cadstudio_fea_preflight`、`cadstudio_prepare_fea`、`cadstudio_run_fea`、`cadstudio_run_fea_convergence`、`cadstudio_review_advanced_geometry`、`cadstudio_create_ocp_loft`、`cadstudio_create_ocp_surface`；SolidWorks 原生操作再调用白名单 `solidworks_*` 工具。
5. 不要暴露任意 Python/VBA 执行工具；新增 MCP 工具时应复用 `scripts/sw_*.py` 中已验证封装。
6. SolidWorks COM 操作必须串行执行；MCP server 内部已使用全局锁降低桌面会话冲突。
7. 基准 demo 使用 `examples/08_mini_fan_motion_assembly.py`；它验证自动建模、装配、Mate 和 Motion Study，不承诺圆角/倒角外观完美。

### 运动装配体要求

当用户要求“能动起来”“在 SolidWorks 里拖动”“铰链”“齿轮联动”“真实机械配合”时：

1. 先读取 `references/assembly.md` 的运动型装配工作流；如果用户明确要求 Motion Study / 运动算例 / 马达，再读取 `references/motion-study.md`。
2. 优先复用 `sw_assembly.py` 中的 `resolve_component()`、`get_assembly_entity()`、`find_largest_cylinder_face()`、`add_mate5_checked()`、`add_concentric_mate_by_cylinders()`、`add_gear_mate_by_cylinders()`。
3. 旋转件用同心 Mate 且 `lock_rotation=False`，不要用三基准面把轴、齿轮、上盖完全锁死。
4. 齿轮传动用真实 Gear Mate，不用脚本假动画冒充机械配合。
5. 创建后用 `collect_mate_feature_summary()` 或特征树遍历验证 MateGroup 下存在 `MateConcentric`、`MateGearDim` 等真实 Mate 特征。
6. 需要真实运动算例时，优先复用 `sw_motion.create_motion_study()`、`add_constant_speed_rotary_motor_by_cylinders()`、`calculate_and_play()` 创建 Motion Study 和马达。
7. 计算后调用 `sw_motion.validate_motion_studies()` 或 MCP `solidworks_validate_motion_study`，检查类型、时长、马达数量、结果存在性和 `results_out_of_date=False`；只看到时间轴、动画或 `Calculate=True` 不算验收通过。
8. 需要演示动画时可以额外脚本驱动组件位姿或 Mate Controller，但必须说明动画演示不等同于交互自由度；最终以 SolidWorks 中可拖动为准。

## GPT / Kimi / Claude 多模型策略

当代理需要让大模型生成 VBA 宏时，必须通过 `scripts/sw_macro_guard.py`：

1. **模型分流**：GPT 系列使用原有简洁提示词；Kimi / Claude / 未知模型自动加载强格式约束 Prompt，强制只输出 VBA 源码。
2. **本地模板兜底**：模型输出失败或解析失败时，不直接报错；按用户关键词（如“立方体”“圆柱”“拉伸”“草图”）选择内置 VBA 模板继续执行。
3. **输出校验**：执行前检查 `SldWorks`、`ModelDoc2`、`Sub`、`End Sub`，通过后才允许交给 SolidWorks；不通过则重试。
4. **超时/重试**：单次模型请求建议 `30s` 超时；解析失败自动重试 `1~2` 次，重试 Prompt 追加更强格式指令。

示例：

```python
from sw_macro_guard import build_prompt, fallback_macro_for_request, validate_vba_macro

prompt = build_prompt("画一个 50mm 圆柱", model_name="claude")
macro = fallback_macro_for_request("画一个 50mm 圆柱")
result = validate_vba_macro(macro)
assert result.ok, result.issues
```

## 未封装 API 规则

当任务需要调用 `scripts/` 中尚未封装的 SolidWorks API 时：

1. 先读取 `references/api-lookup.md`，再查询 SolidWorks 官方 API 文档，或本地 SolidWorks SDK / 参考资料，确认方法签名、参数含义、枚举值、返回值和版本差异。
2. 禁止凭记忆猜接口；尤其是长参数 COM 方法、`VARIANT` / by-ref 参数、枚举值、选择标记和 `SaveAs` 类接口。
3. 写代码时保留最小可运行脚本，并对每一步返回值做 `None` / `False` 检查。
4. 实现后必须真实运行，保存或导出目标文件，并使用 `sw_review.py` 生成预览图与审查报告。
5. 新发现的坑、错误码、兼容写法或稳定封装，要补充到 `references/troubleshooting.md` 或对应模块参考文档；常用逻辑再沉淀进 `scripts/`。

## 能力索引与使用指南

按「我要做什么」查，不是按「有哪些 API」查。

### 查表

| 我想知道 | 去哪 |
|---|---|
| 这个功能**官方怎么用**（2,839 个官方示例按 14 域归类） | [`docs/usage-guide.md`](docs/usage-guide.md) |
| 官方某个成员**本仓库哪个函数能调到** | [`docs/api-map.md`](docs/api-map.md) |
| 某个功能域的接口族**覆盖到什么程度**（定量） | [`docs/family-coverage.md`](docs/family-coverage.md) |
| 官方有**哪些接口族**、这个域覆盖到什么程度 | [`docs/capability-matrix.md`](docs/capability-matrix.md) |
| 还**缺什么**、为什么没做 | [`docs/gap-analysis.md`](docs/gap-analysis.md) |
| 某个 COM 调用的**参数个数**与官方是否一致 | [`docs/signature-audit.md`](docs/signature-audit.md) |
| 改完代码的**全量体检结果** | [`docs/harvest-report.md`](docs/harvest-report.md) |

官方 API 清单速查（**「收录」= 名字与参数个数已抄进官方 API 索引，可直接调用**）：

| 判据 | 实测 |
|---|---|
| 收录程序集 | **12** 个 |
| 接口族 | **792** |
| 成员 | **15,466** |
| 编入官方 API 索引 | **15,466 / 15,466 = 100%** |
| 未编入的族 | **0** |

本机实装 **18** 个 interop 程序集（合计 1,804 个接口），收录 12 个；
未收录的 3 个是明确排除的（`sustainability` 绿色设计 / `sw3dprinter` 3D 打印 /
`swbrowser` PDM 浏览器），另 `swconst` 只有枚举（已单独收录字面值）、
`swcommands` 实测 0 个接口。

12 份索引一览：

| 索引 | 族 | 能力 | 是什么 |
|---|---|---|---|
| `sw_api_sldworks.py` | 523 | 8,210 | 主体：零件 / 装配 / 工程图 / 草图 / 钣金 / 焊件 |
| `sw_api_swdocumentmgr.py` | 138 | 2,524 | Enterprise PDM（需许可） |
| `sw_api_cosworks.py` | 84 | 1,235 | Simulation 仿真（需许可） |
| `sw_api_swdimxpert.py` | 51 | 136 | 尺寸标注自动化 / GD&T 公差 |
| `sw_api_swpublished.py` | 31 | 354 | 加载项框架（属性管理页回调、消息栏） |
| `sw_api_SWRoutingLib.py` | 14 | 87 | Routers 线缆路由（需许可） |
| `sw_api_sldcostingapi.py` | 14 | 81 | Composer / Costing（需许可） |
| `sw_api_swmotionstudy.py` | 11 | 81 | 机构运动仿真（需许可） |
| `sw_api_gtswutilities.py` | 11 | 120 | 几何分析 / 壁厚分析 / 图档比较 |
| `sw_api_sldtoolboxconfigureaddin.py` | 2 | 5 | Toolbox 配置 |
| `sw_api_fworks.py` | 1 | 7 | Factory / 辅助 |
| `sw_api_dsgnchk.py` | 1 | 19 | Design Checker 设计检查器 |

怎么用（**只有一种走法，全用官方名**）：

```python
call_index(对象, "族名", "成员名", *参数)
```

例：

```python
call_index(特征管理器, "IFeatureManager", "FeatureCut4", x1, x2, ..., x27)
```

三处口径（各索引的 docstring 里都写明）：

- **成员名用 COM 名** —— 反射里 `get_CustomPropertyManager` 的 COM 名是
  `CustomPropertyManager`；⚠ 传 `GetXxx`（大写 G）**谁都不认**
- **arity = 调用方要传的实参，排除 by-ref 出参** ——
  ⚠ `GetErrorMessages(Object&, Object&, Object&)` 是 **0 参**，三个全是 [out]
- **不收 COM 内部分发口** —— `IGetXxx` / `IUpdateYyy` 是同一能力的内部变体

> ⚠ 域 13/14 需要**独立许可产品**（Simulation / Routers / Composer / Enterprise PDM），
> 本机**均未安装**，加载项 ProgID 与取用链**查不到**——
> 相关入口一律**接收调用方传入的对象**，不代为连接。
> 逐族明细见 `docs/family-coverage.md`；口径讨论见 `docs/gap-analysis.md`。
> 相关模块一律**接收调用方传入的对象**，不代为连接。

### 端到端示例

`examples/` 下 13 份，其中 09–11 覆盖本仓库新增的三个能力域：

| 示例 | 覆盖 | 来源 |
|---|---|---|
| [`09_sheet_metal.py`](examples/09_sheet_metal.py) | 基体法兰 → 扫掠法兰 → 证据回读 | 官方 `Create_Swept_Flange_Example_VBNET` 的 Python 翻译 |
| [`10_surface_geometry.py`](examples/10_surface_geometry.py) | 原生曲面路线 A（`IModeler.Create*Surface`） | 官方示例 + 反射 |
| [`11_simulation_study.py`](examples/11_simulation_study.py) | 建研究 → 夹具 → 载荷 → 网格 → 求解 → 回读 | **该域官方示例数为 0**，序列来自反射 |

### 新增能力模块（19 个）

**高层封装**（按能力挑选，可读性好）：

| 模块 | 能力域 | 关键入口 |
|---|---|---|
| `sw_simulation.py` | 仿真（**需许可证**） | `get_cosmosworks` / `create_static_study` / `apply_normal_force` / `create_mesh` / `run_analysis` |
| `sw_simulation_loads.py` | 仿真·载荷 | 24 个 `add_*`（固定/力/压力/辐射/温度/连接件…） |
| `sw_simulation_study.py` | 仿真·研究 | `create_study_v3` / `run_analysis` / `mesh_and_run` / `create_mesh` |
| `sw_simulation_results.py` | 仿真·结果 | `create_plot` / `get_worst_jacobian_ratio` / `collect_mesh_evidence` |
| `sw_simulation_loadprops.py` | 仿真·载荷属性 | `configure_force` / `edit_transaction`（编辑事务） |
| `sw_simulation_study_options.py` | 仿真·求解器 | 242 个设置项的登记表 + `set_option` |
| `sw_simulation_registry.py` | 仿真·成员级 | 19 族登记表 + `call_sim` |
| `sw_surface.py` | 曲面 | `get_modeler` + 14 个 `create_*_surface` |
| `sw_render_material.py` | 配置/材料 | `create_render_material` / `apply_visual_properties` |
| `sketch_relations.py` | 草图·约束 | `add_relation` / `suppress_relation` / `create_spline` |
| `sw_sketch.py` | 草图·图元 | 按类型取法（`get_lines` / `get_arcs` / `get_splines` …） |
| `sw_selection.py` | 选中（地基） | `get_selected_object` / `add_to_selection_list`（回读计数，不信布尔） |
| `sw_view.py` | 三维视图 | `zoom_view` / `rotate_about_center` / `set_view_camera_by_name` |
| `sw_pattern.py` | 阵列特征 | `configure_linear_pattern` / `configure_curve_driven_pattern` |
| `sw_geometry.py` | 几何图元 | 5 族登记表（曲线/面/边/配合/公差） |
| `sw_part_features.py` | 零件特征 | 8 族 + 共用选区事务 `edit_feature_selection` |
| `sw_sketch_sheetmetal.py` | 草图 + 钣金 | 27 族（两域分两张表） |
| `sw_hubs.py` | 两个总入口 | `IFeatureManager`(96%) / `IDrawingDoc`(84%) 登记表 |
| `sw_drawing_annotations.py` | 工程图标注 | 6 族（尺寸/注释/表格/图纸） |
| `sw_assembly_doc.py` | 装配 | `IAssemblyDoc` 133 能力 + `FEATURE_MANAGER_TRAPS` 式的陷阱表 |
| `sw_routing.py` / `sw_costing.py` / `sw_pdm.py` | 路由/Composer/PDM | 高层封装 |

**全量登记表**（有多少、叫什么、几个参数）：

| 模块 | 族 | 能力 | 属性 |
|---|---|---|---|
| `sw_simulation_full.py` | 84（cosworks 全库） | 1235 | 704 |
| `sw_pdm_full.py` | 138（swdocumentmgr 全库） | 2524 | 912 |
| `sw_sldworks_remaining.py` | 138 | 4148 | 1504 |
| `sw_routing_costing_full.py` | 31 | 189 | 145 |

> 高层封装回答「怎么用」，全量登记表回答「还有什么」——两者互补，不冲突。

⚠ 上游 `capabilities.yaml` 的 `level` 字段含 `"verified"` 一值，那是上游对**其自身**
能力等级的声明。本任务新增内容一律不使用 A6 禁词表里的任何词。

⚠ **两个域都有「刻意不提供」的部分，别硬调**：
- 仿真域 84 个接口只有 7 个拿得到签名（另 27 个 `Add*` 的两套官方源同时失效），
  且 `ICWResults` **没有** `GetStressComponent` / `GetDisplacementComponent`。
- 曲面域的 Radiate/Planar/Extend/Knit/Fill **没有脚本创建入口**
  （唯一例外 `IFeatureManager.PostTrimSurface(Boolean)`），本仓库只做路线 A。

### 代码体检工具

```powershell
# 一次性：反射本机 SolidWorks 的 interop DLL，生成 arity 审计所需的签名清单
python scripts\refresh_api_signatures.py        # 产物在 .api-signatures/（已 gitignore）

# 日常：三个门禁
python scripts\check_provenance.py              # 来源可追溯性（已接入 release_check）
python scripts\audit_call_arity.py <文件> .api-signatures/iface_sldworks.txt
python -m compileall -q scripts subskills tests
python scripts\release_check.py                 # 发布前门禁
```

> ⚠ **签名清单不提交进仓库**。它是从达索 interop 程序集派生的内容（事实性签名，
> 非创作性表达），但把大体积派生件塞进 MIT 仓库是不必要的分发风险。
> **工具进仓库、产物留本地**——装了 SolidWorks 的人一条命令即可复现。
>
> ⚠ `check_provenance.py` 需要一个 git 锚点判断「哪些行是新增的」，
> 默认 `origin/main`，可用 `PROVENANCE_ANCHOR` 覆盖。
> 无 git 或锚点不可解析时它**显式返回 skipped**，不静默放行。
>
> ⚠ A6 禁词**不能**做成全仓严格检查：上游基线自身在
> `scripts/subskills/tests/examples/docs/references` 下就有 **23 处**命中
> （`capabilities.yaml` 另有 37 处），全仓严格会因**上游既有内容**失败。
> 禁词只对「相对锚点的新增/修改行」生效 —— 这正是它依赖 git 的原因。

> ⚠ 反射清单（`iface_sldworks.txt` / `iface_cosworks.txt`）由
> `tools\reflect-interop.ps1` 对官方 interop DLL 做纯元数据反射生成，
> **不在本仓库内**，需本地重跑。

## 结果自审查

每次生成、修改、导入或导出 CAD 后都要做自审查，除非用户明确说不需要：

1. 检查 COM 返回值、特征对象、保存/导出返回值和输出文件大小。
2. 调用 `model.ForceRebuild3(False)`、`model.ViewZoomtofit2()` 刷新模型。
3. 用 `scripts/sw_review.py` 的 `run_review()` 导出 `isometric/front/top/right` 预览图并写入 `*_review_report.json`。
4. 读取报告里的 `evaluation.status`、`evaluation.issues`、`checks` 和预览图；通过截图或导出的 BMP 检查：主体是否存在、比例/方位是否合理、关键部件是否缺失、是否明显重叠或悬空、文件名和输出路径是否正确。
5. 若发现问题，先修脚本并重新生成，再汇报；不要只报告“保存成功”。

示例：

```python
from sw_review import run_review

model.ForceRebuild3(False)
report, report_path = run_review(
    model,
    r"C:\temp\review",
    basename="car",
    expected_outputs=[r"C:\temp\car.sldprt", r"C:\temp\car.step"],
)
print(report_path)
print(report["evaluation"])
```

## 关键注意事项

- **单位**：API 统一使用**米**。用 `mm(50)` 转换 50mm 为 0.05m，用 `deg(90)` 转换角度
- **版本**：使用 `SldWorks.Application` 自动连接，兼容所有版本
- **选择**：能拿到 COM 对象时优先用对象级 `Select2()`；基准面可用 `SelectByID2("PLANE")`，草图不要只依赖 `SelectByID2("SKETCH")`
- **草图**：推荐用 `with sketch(model, "Front Plane") as sketch_name:` 自动进入/退出草图；`sw_part.py` 会缓存草图对象引用，避免 SW2024 中文版按名称选择草图失败
- **添加组件**：装配体优先用 `sw_assembly.add_component()`；SW2024 中文版下 `AddComponent4` 可能返回 `None`，封装会用 `AddComponent5`、静默打开零件、重新激活装配体后重试
- **外观**：对颜色要求高的模型优先拆成多零件装配体；材质数组必须用 `SAFEARRAY(double)` 编组，并回读 RGB 验证
- **VARIANT**：by-ref 参数必须用 `VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)` 包装
- **基准面名称**：`start_sketch()` 会自动兼容英文版 "Front/Top/Right Plane" 与中文版 "前视/上视/右视基准面"
- **草图坐标**：基于草图平面的局部坐标系，单位为米
- **运动装配**：先解析组件再选 Mate 实体；`GetCorresponding()` 用于把零件内面/特征映射到装配体上下文；同心 Mate 默认不锁旋转
- **Motion Study**：`swmotionstudy.tlb` 需加载；pywin32 下 `CreateMotionStudy` / `Activate` / `Calculate` 可能表现为属性，优先用 `sw_motion.motion_member()` 兼容
