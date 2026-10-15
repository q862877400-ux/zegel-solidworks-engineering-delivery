# Baseline — **EC01 工程设计契约与对象模型** · G0 基线与权属

**Feature**: `specs/303-ec01-engineering-contract/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC01**（★ 逐字：目标「把"做一个支架"变成能计算、规划、验收的工程需求」）
**前置**: ★ **EC00（规格 302）已收口** —— ★ 四项残留全部清完（★ 见 `specs/302-*/acceptance/T032-closeout.md` §六）
**对应任务**: **EC01-T01**（★ 定义用户故事和非目标；★ 划分已知、假设、待确认、必需缺失四类信息）

---

## 一、★★★★★ 编号与游标（★ 承 EC00 的 G0 口径）

| ★ 项 | ★ 实测读数 | ★ 处置 |
|---|---|---|
| ★ **最高正式编号** | ★ **302**（`specs/302-ec00-trustworthy-tool-base/`） | ★★ **本特性取 `303`** —— ★ 无冲突 ✓ |
| ★★ **重号检查** | ★ **`207` × 2**（★ 历史遗留） | ★ **保留不合并**（★ 承 `DSH_DECISIONS.md` **D5**） |
| ★ 分支 | `master` | ★ **不切分支** |
| ★ `HEAD` | `d072d0c79985f87e9d1f6278241b18fc1f26d713` | ★ **未提交**（★ 红线） |

---

## 二、★★★★★ 权属（★ 承 `DSH_DECISIONS.md` **D6** · ★ EC00 的 `baseline.md` §二）

| ★ 组 | ★ 内容 | ★ 处置 |
|---|---|---|
| ★★ **A 组** | ★ `scripts/sw_part.py`（★ **本会话改过 docstring** —— ★ 见 §三）· ★ `?? scripts/sw_sketch_relations.py` | ★★ **可认领**；★ 合并/提交**仍由 merge owner 单点** |
| ★★ **B 组** | ★ 其余（★ `AGENTS.md` · `docs/*` · ★ 本会话新增的 `archive/` 与 `specs/294–303`） | ★★★ **禁止覆盖** |

---

## 三、★★★ 本会话对 `scripts/sw_part.py` 的改动（★ 如实登记）

★★★ **改了一处**：★ `extrude_boss` 的 **docstring**（★ 清 **EC00 残留 ⑥**）：
- ★ **原**：★ `depth: 拉伸深度（**毫米**）`
- ★★ **问题**：★ 官方 `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` **逐字**说
  ★ `D1`: **「Depth of extrusion for first end **in meters**」** ⇒ ★★ **文档与官方矛盾**
- ★★★ **改后**：★ 写明「**米**」+ 附官方依据 + 真机脚本的 `mm(...)` 写法 + 官方 Example 的调用序
- ★ **判据**：★ `tests/test_ec00_extrude_precondition.py`（★ **4 例**）
- ★★ **⚠ 这是**文档订正**，★ **不是签名变更** ⇒ ★ 不动任何调用契约 ✓

---

## 四、★★★ 本轮允许写入的文件

| ★ 类 | ★ 路径 |
|---|---|
| ★ **本特性目录** | `specs/303-ec01-engineering-contract/**` |
| ★ **判据** | `tests/test_ec01_*.py` |
| ★ **实现** | ★ **优先扩展**现有模块（★ 见 §五）；★ 确需新增时**只进 `schemas/engineering/`**（★ 计划 §5 EC01 逐字建议落点） |
| ★★ **禁止写** | ★ B 组任何路径 · ★ `AGENTS.md` 纪律正文 · ★ `.gitignore` · ★ `.codebuddy/` · ★ `.workbuddy-ai/` |

---

## 五、★★★★ 起点状态（★ 计划 §5 EC01 的「建议落点」逐条核）

| ★ 计划说 | ★ 实测 | ★ 处置 |
|---|---|---|
| ★ 扩展**现有 design_plan schema** | ★ `subskills/solidworks-vibecad/schemas/design_plan.schema.json` **存在**（★ **10 个字段**：`plan_version` / `source_brief` / `part_family` / `parameters` / `features` / `operation_sequence` / `assumptions` / `risk_register` / `review_plan` / `solidworks_mapping`） | ★★ **扩展它**（★ **不另建**） |
| ★ 扩展**编排入口** | ★ `apps/desktop/cad_workbench/engineering_orchestrator.py` **存在** | ★ **扩展它** |
| ★ **必要时**在 `schemas/engineering/` 建 schema | ★ `schemas/` **不存在** | ★★ **只在「design_plan 装不下」时才建**（★ 见 §六） |
| ★ 增加**单一权威** `EngineeringContract` 定义 | ★ **不存在** | ★★★ **本特性的核心产物** |
| ★ 旧设计计划 → 新契约**适配** | ★ **不存在** | ★ 本特性（EC01-T05） |

★★★ **⇒ 铁律 1（只做缝合）**：★ **优先扩展** `design_plan.schema.json`；
★★ **只有它装不下**（★ 如「量纲/工况/义务/批准」这些**新概念**）才在 `schemas/engineering/` 新建 ✓

---

## 六、★★★★ 与 EC00 的接口（★ 承 `specs/302-*/quickstart.md` §5.1）

| ★ EC00 交付 | ★ EC01 怎么用 |
|---|---|
| ★ `Quantity` / `NormalizedQuantity` | ★★ **直接复用**（★ **不另建一套量纲**）—— ★ `contracts/quantity.md` |
| ★ `ToolExecutionRequest` | ★ EC01 的 `EngineeringContract` 冻结后**编译**成它 |
| ★ `ObjectReference` 解析结果 | ★ EC01 的 `Datum` / `Fit` **引用**它 |
| ★★ **边界** | ★★★ **EC00 只做「工具执行可信」，★ EC01 做「工程语义正确」** —— ★ 「这个支架设计得对不对」是 EC01/EC05 的事 |

---

## 七、★★ G0 判据（★ 计划 §1.4）

| ★ 门 | ★ 放行条件 | ★ 本文件 |
|---|---|---|
| **G0 基线** | ★ 权属和起点明确；★ **没有覆盖别人的改动** | ★★ **满足** ✓ —— ★ 编号 **303** · ★ 权属按 D6 · ★ 写入面已列 · ★ **未触碰 B 组** |

★★★ **⇒ G0 通过** ⇒ ★ 可进入 **EC01-T01**（需求冻结）。
