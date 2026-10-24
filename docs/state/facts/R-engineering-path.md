# R 维度 · 工程交付路线的事实基础

> 记录员口径：只写观测、读数、证据、复现与未确认；不含判断、优先级、修复建议。
> 本文件记录外部评审方案 `output/PROJECT-CHARTER-TECHNICAL-PATH-AND-PLAN.md`
> 所依据的读数在本仓的核实结果，以及核实过程中发现的、方案未提及的读数。
>
> 核实基线：提交 `8b262d22`，解释器 Python 3.14.7。核实方式全部只读。

---

## R-01 工具声明：501 条声明 / 497 个唯一名 / 注册前检查 5 条问题

- **观测方式**：`python -B docs/state/probes/probe_all_specs.py`（只读，未传 `--json`）
- **读数**：声明总数 **501**；唯一名 **497**；`check_specs` 返回 **5** 条问题 —— 4 条工具名重复 + 1 条角度参数规则违反
- **证据**：
  - 重复：`solidworks_sketch_spline`（`mcp-server/tool_specs_batch76.py` 与 `batch116.py`）·
    `solidworks_sketch_offset`（`batch66.py` 与 `batch116.py`）·
    `solidworks_feature_cosmetic_thread`（`batch76.py` 与 `batch116.py`）·
    `solidworks_export_flat_pattern_dxf`（`batch100.py` 与 `batch116.py`）
  - 角度：`mcp-server/tool_specs_batch116.py` 的 `Param("angle_rad", float, ...)`；
    判定逻辑 `mcp-server/tool_registry.py` 的 `_ANGLE_WORDS` / `_ANGLE_SUFFIX` / `_ANGLE_SUFFIX_EXEMPT`
- **复现**：`python -B docs/state/probes/probe_all_specs.py`
- **未确认**：无

## R-02 注册门禁是「全有或全无」：5 条问题导致一个工具都不注册

- **观测方式**：读 `mcp-server/tool_registry.py` 的注册入口 + 假 mcp 实测
- **读数**：`check_specs` 非空即 `raise GateError("声明未过门禁，未注册任何工具：…")`；
  `mcp-server/server.py` 在**模块导入时**调用注册入口
- **证据**：`mcp-server/tool_registry.py` 的 `problems = check_specs(specs)` / `raise GateError(...)`；
  `mcp-server/server.py` 的 `_register_declarative_tools()`
- **复现**：见 R-01 的探测器；`check_specs` 的返回值即注册器的输入
- **未确认**：未实际启动 MCP 服务进程（只做导入级与函数级观测）

## R-03 聚焦测试：14 failed / 32 passed，失败全在 `test_ec03_compiler.py`

- **观测方式**：`python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py -q -p no:cacheprovider --tb=short`
- **读数**：**14 failed, 32 passed**。14 条失败**全部**来自 `tests/test_ec03_compiler.py`；
  `tests/test_stage2_rules.py` 单跑 **18 passed / 0 failed**
- **证据**：14 条失败的错误行同一处 —— `scripts/engineering/compiler.py` 的
  `over = [k for k in domains if not spec.allows(k)]` 抛
  `AttributeError: 'MethodSpec' object has no attribute 'allows'`。
  `MethodSpec` 的基类 `scripts/engineering/_applicability.py` 的 `ApplicabilityMixin` 只有 `applies_to()`；
  全仓 `.allows(` 仅此一处调用点、无定义
- **复现**：上述 pytest 命令
- **未确认**：`compiler.py` 该行自 `195e2000` 落地以来是否曾成功执行过（未逐 commit 追溯）

## R-04 草图自由度估算：`2×实体数 − 关系数 − 尺寸数`

- **观测方式**：读源码 + 纯内存合成输入实测（未落盘、未启 CAD）
- **读数**：`scripts/engineering/part_loop.py` 的 `DofPlan.total_dof` 即该公式。
  4 实体 / 2 关系 / 1 尺寸 → **5**。
  **同一条关系重复 8 次** → **0**（`is_acceptable: True`）；
  **同一条尺寸重复 4 次** → **0**；1 实体配 4 关系 + 4 尺寸 → **0**（clamp，无超约束告警）
- **证据**：`scripts/engineering/part_loop.py` 的 `def total_dof(self)`
- **复现**：构造 `DofPlan(entities=4, relations=[同一条]*8, dimensions=[])` 后读 `total_dof`
- **未确认**：未作真机草图求解状态比对

## R-05 装配自由度估算：按配合类型扣常数，重复配合可归零

- **观测方式**：读源码 + 纯内存合成输入实测
- **读数**：`scripts/engineering/assembly.py` 的 `ConstraintGraph.total_dof` 从基座减
  `MateKind.REMOVES` 的常数（coincident 3 / concentric 4 / distance 1 / parallel 2 / perpendicular 2）。
  同一对组件**重复贴 6 次 coincident** → dof **0**、verdict `fully_constrained`、`releasing: True`
- **证据**：`scripts/engineering/assembly.py` 的 `def total_dof(self)` 与 `MateKind.REMOVES`；
  冗余只有调用方预置 `Mate.redundant=True` 才被识别，该字段默认 `False`，代码内无自动判定
- **复现**：构造 `ConstraintGraph` 并重复 append 同一条 `Mate`
- **未确认**：未作真机配合状态回读比对

## R-06 图纸义务覆盖率只看 `covered` 布尔，不看 `evidence`

- **观测方式**：读源码 + 纯内存合成输入实测
- **读数**：两条义务以**空字符串** evidence 标记 covered 后，`coverage()` 返回
  `{'total': 2, 'covered': 2, 'ratio': 1.0, 'ok': True}`
- **证据**：`scripts/engineering/drawing_obligations.py` 的 `def coverage(obls)` 只统计 `o.covered`；
  `def mark_covered(obls, name, evidence="")` 的 evidence 默认为空串
- **复现**：`mark_covered(obls, "a")` / `mark_covered(obls, "b")` 后读 `coverage(obls)`
- **未确认**：无

## R-07 板件规划可省略请求中的孔；`PlanSet.ok` 不检查几何覆盖

- **观测方式**：读源码 + 以四孔请求实测候选生成
- **读数**：请求「100×60×20 安装板 + 四角四个 φ6 孔」时，抽到 5 个候选，
  其中 **3 个**（`plate_only` / `plate_chamfer` / `minimal`）**不含任何孔**。
  `PlanSet.ok` 的判据只有两条：候选数在 3–5 之间、全部可编译
- **证据**：`scripts/engineering/planner.py` 的 `_steps_for`（`if route in ("plate_only", "minimal"): return base`）
  与 `PlanSet.ok`（`MIN_VARIANTS <= len(candidates) <= MAX_VARIANTS and len(compilable) == len(candidates)`）
- **复现**：以该需求串调用规划入口并打印各候选的步骤集合
- **未确认**：未验证下游执行器是否会因缺孔而失败

## R-08 `frozen` 的 `ExecutablePlan` 内部参数字典仍可修改

- **观测方式**：读源码 + 纯内存实测
- **读数**：`PlanStep` 与 `ExecutablePlan` 的 `@dataclass(frozen=True)` 只挡住属性重绑定；
  内部 `params` dict 可 mutate（10 → 999 成功），且穿透到 `ExecutablePlan.steps` 里的同一对象；
  `PlanStep` 因此不可哈希
- **证据**：`scripts/engineering/registry.py` 的 `class PlanStep` / `class ExecutablePlan` 的
  `params: dict = field(default_factory=dict)`
- **复现**：构造 `ExecutablePlan` 后 `plan.steps[0].params["depth_mm"] = 999`
- **未确认**：未检查生产执行入口是否另有内容校验

## R-09 规则服务可凭两个布尔 + 来源标签返回 PASS，输出与引用为空

- **观测方式**：读源码 + 合法 `RuleRequest` 实测
- **读数**：`formula_ok=True` / `applicability_ok=True` 时返回 `PASS`，
  `outputs={}`、`citations=[]`、`checked_preconditions=[]`。
  来源标签 `official_status_record` / `contract_specified` / `offline_cache` 三种都直接 PASS；
  `retrieval_summary` / 空串 / 未知值 → `INDETERMINATE`
- **证据**：`scripts/engineering/rule_service.py` 的 `evaluate_rule` 的 PASS 分支；
  新鲜度检查仅在 `checked_on` 与当日**都非空**时才执行
- **复现**：构造 `RuleRequest` 并以不同 `source` 调用 `evaluate_rule`
- **未确认**：无

## R-10 变更传播是「新建文档重跑」，不是「改已交付件的驱动尺寸」

- **观测方式**：读 `tools/run_stage2_plate.py` 的 `run_change`
- **读数**：`run_change` 走 `sw_connect.new_document(sw, "part")` 新建文档，
  用修改后的参数重新执行建模；全文件对已交付件的打开只有 `reopen_drawing()`（重开工程图，非零件）
- **证据**：`tools/run_stage2_plate.py` 的 `def run_change`；`scripts/sw_connect.py` 的 `def new_document`
- **补充读数**：改驱动尺寸的能力已存在 —— `scripts/sw_document_data.py` 的 `update_dimension_mm`
  走 `SetSystemValue3`，并已挂为工具 `solidworks_config_update_dimension`
  （`mcp-server/tool_specs_batch33.py` / `mcp-server/server.py`）
- **复现**：读上述两个函数体
- **未确认**：未作真机「打开已交付件 → 改驱动尺寸 → 重建」试验

## R-11 阶段 317 记录：通用生成器不能创建并绑定指定语义的尺寸

- **观测方式**：读阶段 317 验收文件
- **读数**：通用生成器报 `DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED`，
  「只能导入模型尺寸，不能可靠创建并绑定指定 ID、视图和语义的尺寸」；
  `requiredDimensions` 必须留空，覆盖率只能从真机图纸回读
- **证据**：`specs/317-stage2-real-holes/acceptance.md` 的验收记录段
- **同文件内的另一处读数**：`scripts/engineering/drawing_run.py` 固定追加
  `"材料：45 钢；未注公差按 GB/T 1804-m"` 与孔数说明，与请求实际材料无关；
  调用方 `tools/run_stage2_plate.py` 无 material 参数可传
- **复现**：读上述两处
- **未确认**：未核实标准数值本身（本文件不作标准符合性判断）

## R-12 阶段 322 与 319 的验收末尾各自声明了未覆盖项

- **观测方式**：读两份验收文件的结论段
- **读数**：
  - `specs/322-stage7-housing-final-dod/acceptance.md` 记录「9 案例不是 9 次真机运行」——
    其中箱体类走真机，平口钳与连杆共 6 条走的是判定层
  - `specs/319-stage4-constrained-planning/acceptance.md` 记录未真调云端 LLM（主动不做），
    且「可解盲题 93.8%」是对 AI 起草的标签算的，不是对业主冻结的标签算的
- **证据**：上述两份文件的结论段
- **复现**：读文件末尾
- **未确认**：无

## R-13 阶段 317 验收文件内部不一致：正文与结论段对同一试验给出相反状态

- **观测方式**：同文件内两处比对
- **读数**：同一份 `specs/317-stage2-real-holes/acceptance.md` 中，
  全量验收表记「真机变更传播 pass=True（板宽 100→120、三类产物全变）」，
  而结论段记「真机变更传播与工程图重开仍未跑（机制与测试已就绪）」
- **证据**：该文件的验收表段与结论段
- **复现**：在同一文件内检索「变更传播」
- **未确认**：哪一处为准（记录员不裁决）

## R-14 规划出口当前被注册重名阻断

- **观测方式**：`python -B -m pytest tests/test_stage4_planner.py -q -p no:cacheprovider --tb=no`
- **读数**：**4 failed / 26 passed**，4 条失败同一原因
  `RegistryError: duplicate-canonical-name: solidworks_sketch_spline`
- **证据**：`scripts/engineering/registry.py` 的 `build_registry` 在重名时抛错；
  `scripts/engineering/planner.py` 的 `plan_from_requirement` 内部调用 `build_registry`
- **复现**：上述 pytest 命令
- **未确认**：无

## R-15 `FinalDod` 的 `evaluate` 方法在重构中消失

- **观测方式**：读源码 + `python -B -m pytest tests/test_stage7_housing.py -q -p no:cacheprovider --tb=no`
- **读数**：**9 failed**，错误全为 `'FinalDod' object has no attribute 'evaluate'`；
  `scripts/engineering/housing.py` 的 `FinalDod` 当前只有字段；
  抽出的 `CaseCollectorMixin`（`scripts/engineering/_case_collector.py`）只补回了 `add_case`
- **证据**：`scripts/engineering/housing.py` 的 `class FinalDod`；
  `tools/run_stage7_final_dod.py` 仍在调用 `d.evaluate()`
- **复现**：上述 pytest 命令
- **未确认**：该删除是有意还是意外（未查提交意图）

## R-16 工程层聚焦测试的合计红面

- **观测方式**：`python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py tests/test_stage4_planner.py tests/test_stage7_housing.py -q -p no:cacheprovider --tb=no`
- **读数**：**27 failed / 75 passed**（本次实跑）
- **证据**：上述命令输出
- **复现**：上述命令
- **未确认**：全量测试的合计红面（本次未跑全量；历史读数见 `Q3-tests-full.md`）

## R-17 文档层：137 个 `docs/` 根文件按「是否被代码读 / 是否被门禁守 / 是否承载当前定义」的分类结果

- **观测方式**：逐个文件搜代码引用（跳过 `apps/workbench-ui/src-tauri/resources/skill/` 内嵌快照），
  并核对门禁源码里的常量路径
- **读数**：LIVE **62** · GENERATED **8** · DATA **2** · HISTORY **65**（合计 137）
- **证据**：分类明细见本文件所在提交的归档动作；归档落点 `docs/history/`
- **复现**：对每个文件名在 `scripts/ tests/ tools/ mcp-server/` 内检索 `docs/<name>`，
  并区分「注释提及」与「实际 `read_text` / `open` 读取」
- **未确认**：`user-feature-coverage.md` 的生成器在仓库之外，未能验证其当前可运行性

## R-18 两个「存在即通过」的判据对象

- **观测方式**：读 `scripts/release_check.py` 的 `REQUIRED_ABILITY_FILES` 与对应生成器
- **读数**：
  - `docs/provenance-index.json` 的唯一消费者是存在性断言；`scripts/check_provenance.py --index`
    只把结果输出到 stdout，仓内无脚本回写该文件
  - `docs/T-040-unmapped-constants-evidence.md` 的唯一引用是注释；
    真正判据是 `scripts/check_interface_member_ownership.py` 内的 `MANUAL_MAP` 硬编码表
- **证据**：上述两处
- **复现**：检索这两个文件名在全仓的出现位置并区分读/写/注释
- **未确认**：无

## R-19 T008 真机：交付板件零驱动尺寸；`AutoDimension2` 可行、`update_dimension_mm` 单位放大 1000 倍

- **观测方式**：两个真机探针（走 `tools/sw_guard.py` 护栏，`CommandInProgress` 抑制弹窗）
  - `tools/probe_s3_dimensions_exist.py`（量现状）
  - `tools/probe_s3_t008_dimension_driven.py`（量可行路径）
- **读数一：现状是零驱动尺寸、草图欠约束**
  - `ISketch.GetConstrainedStatus()` = **2**（`swUnderConstrained`）
  - 驱动尺寸数 = **0**；特征树只有 `草图1` + `凸台-拉伸1`
  - 根因：`tools/run_stage2_plate.py` 的 `build_plan()` 用 `x1_mm`/`x2_mm`/
    `center_x_mm`/`radius_mm` 这类**坐标参数**建板，每轮重画一遍，模型里不留尺寸
- **读数二：加驱动尺寸**有**两条**入口，一条死一条通
  - ❌ `IModelDoc2.AddHorizontalDimension2` —— 本机实测**直接把 SolidWorks 崩掉**
    （`com_error: RPC 服务器不可用`）。这与 `docs/dead-ends.md` 轮 400/153/154/155
    记的 `AddDimension2` 死路**同族**，且症状更重
  - ✅ `ISketch.AutoDimension2(1, 1, -1, 1, -1)` —— 回 `0`（success），
    **建成 1 个尺寸** `D1@草图1`（值 = 100 mm = 板宽），草图 `2 → 3`（完全定义）
  - ❌ `ISketchManager.FullyDefineSketch`（官方指它取代 `AutoDimension2`）——
    按官方 **10 个参数**调用，第 6 参（`HorizontalDatumDisp`，`object`）报
    `类型不匹配`。未查明正确的传法
- **读数三：`update_dimension_mm` 写入的值放大约 1000 倍**
  - 请求把 `D1@草图1` 从 100 mm 改成 120 mm（×1.2）
  - `IDimension.SystemValue`：`0.1` → **`120.0`**（比例 **1200**，期望 **0.12**）
  - 该函数**自报** `success: True`，且其 `after_mm` 回 `120.0`（与请求一致）
    ⇒ **它的自我报告不能当证据**
  - 依据：`scripts/sw_document_data.py` 的 `update_dimension_mm` 用
    `_document_length_unit_scale(model)` 求 scale 后 `SetSystemValue3(value_mm / _scale, ...)`
- **证据**：`tools/probe_s3_dimensions_exist.py` / `tools/probe_s3_t008_dimension_driven.py`；
  产物 `output/s3-dimensions-exist.json` 与 `output/s3-t008-dimension-driven.json`
  （`output/` 在 `.gitignore` 里，关键读数已抄进本节）
- **复现**：
  ```powershell
  python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_dimensions_exist.py
  python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_t008_dimension_driven.py
  ```
- **未确认**：
  - `GetSystemValue3` 的正确调用形状 —— 传 `(0, None)` 回 `null`，未查明缺哪个参数
  - 包围盒读法 —— `IPartDoc.GetBodies2(True)` 报「非选择性的参数」、
    `IModelDocExtension.GetBox` 不存在 ⇒ **没有独立读数能证实几何真的变宽了**
  - `update_dimension_mm` 的单位缺陷是「`_scale` 求错」还是「`SetSystemValue3` 吃米制」
    未见分晓；两种解释都未被证据排除
