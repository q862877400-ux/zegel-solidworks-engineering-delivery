# Baseline — **EC03 方法库、工程IR与受约束规划编译**

**Feature**: `specs/305-ec03-method-library-and-ir/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC03**（★ T01–T08 逐字）
**前置**: ★ **EC01（303）· EC02（304）已收口**
**对应任务**: **EC03-T01**（★ 定义 `MethodSpec`）

---

## 一、★★★★★ 编号与权属

| ★ 项 | ★ 读数 | ★ 处置 |
|---|---|---|
| ★ **最高正式编号** | ★ **304** | ★★ **本特性取 `305`** ✓ |
| ★ 分支 / `HEAD` | `master` / `d072d0c7…` | ★ **不切分支 · 不提交** |
| ★★ **权属** | ★ 承 **D6**（★ A 组可认领 · ★ **B 组禁止覆盖**） | ★ 只写 §三 的路径 |

---

## 二、★★★★★ 起点状态（★ 计划 §5 EC03 的「复用」逐条核）

| ★ 计划说复用 | ★ 实测 | ★ 处置 |
|---|---|---|
| ★ **golden-workflows** | ★ `golden-workflows.yaml` **存在** —— ★ **10 个 workflow**（★ `mounting_bracket` · `enclosure` · `holes_slots_threads` · `modify_existing_part` · `assembly_mates` · `batch_export` · `configuration_family` · `properties_bom` · `engineering_drawing` · `autocad_cleanup_delivery`）★ 每个带 `capabilities` / `required_inputs` / `required_artifacts` | ★★ **复用**（★ **不另建方法库**） |
| ★ **vibecad 计划** | ★ `subskills/solidworks-vibecad/schemas/design_plan.schema.json`（★ 10 字段） | ★ **复用**（★ EC01 已建适配器） |
| ★ **工程 DAG** | ★ `apps/desktop/cad_workbench/engineering_orchestrator.py` **存在** —— ★ 逐字「★ 将复杂机械需求拆解为**可审计的** SolidWorks 工程 DAG」· ★ **八阶段** | ★★ **复用**（★ **不另建编排**） |
| ★ **既有效应声明** | ★ `docs/effect-declarations.json`（★ EC00 已核） | ★ **复用** |
| ★ 计划建议「**必要时**」新增 | ★ — | ★★ **只在「`MethodSpec` 装不下」时才建**（★ 铁律 1） |

---

## 三、★★★ 本轮允许写入的文件

| ★ 类 | ★ 路径 |
|---|---|
| ★ **本特性目录** | `specs/305-ec03-method-library-and-ir/**` |
| ★ **判据** | `tests/test_ec03_*.py` |
| ★★ **实现** | ★ `scripts/engineering/`（★ **EC02 已建** ⇒ ★ **扩展它**） |
| ★★ **禁止写** | ★ B 组 · ★ `AGENTS.md` 纪律正文 · ★ `.gitignore` · ★ `.codebuddy/` · ★ `.workbuddy-ai/` · ★ **`golden-workflows.yaml` 与 `engineering_orchestrator.py`（★ 只读复用，★ 不改）** |

---

## 四、★★★★★ 本特性的核心设计（★ 由计划 §5 EC03 的「验收」推出）

★★★ **计划 §5 EC03 验收逐字**：
> ★ 两模型生成的合法意图都通过**同一编译器**；★ 编译器能拒绝**越权/欠约束/循环依赖**；
> ★ **不需要 COM 即可检验计划正确性**；★ **冻结计划不能被执行器静默改写**。

★★★ **⇒ 四条判据各自对应一个设计决定**：

| ★ 验收 | ★ 设计决定 |
|---|---|
| ★ **同一编译器** | ★★ 编译**只吃** EC01 的 `EngineeringContract`（★ **不吃**模型输出的自由文本）⇒ ★ **模型无关** |
| ★ **拒绝越权/欠约束/循环依赖** | ★★ 编译**期**检查（★ 不是执行期才发现） |
| ★★ **不需要 COM 即可检验** | ★★★ **编译器纯离线** —— ★ **不 import 任何 COM 模块** |
| ★★★ **冻结计划不能被静默改写** | ★★ 冻结后带**内容哈希**；★ 执行前**校验哈希** ⇒ ★ 变了就**拒绝** |

---

## 五、★★★ 与 EC01 / EC02 / EC04 的边界

| ★ 谁 | ★ 做什么 | ★ **不做什么** |
|---|---|---|
| ★ **EC01**（★ 已收口） | ★ 冻结**工程意图** | ★ 不选方法 |
| ★ **EC02**（★ 已收口） | ★ **确定性规则与计算** | ★ 不编译计划 |
| ★ **EC03**（★ 本特性） | ★★ **选方法 + 编译成工具 DAG** | ★ **不碰 COM** · ★ **不执行**（★ 执行是 EC04/EC05） |
| ★ **EC04** | ★ 租约/围栏/证据链 | ★ 不改计划（★ **只校验哈希**） |

---

## 六、★★ G0 判据

| ★ 门 | ★ 放行条件 | ★ 本文件 |
|---|---|---|
| **G0 基线** | ★ 权属和起点明确；★ **没有覆盖别人的改动** | ★★ **满足** ✓ —— ★ 编号 **305** · ★ 权属按 D6 · ★ 写入面已列 · ★ **复用目标已实测** · ★ **未触碰 B 组** |

★★★ **⇒ G0 通过** ⇒ ★ 可进入 **EC03-T01**。
