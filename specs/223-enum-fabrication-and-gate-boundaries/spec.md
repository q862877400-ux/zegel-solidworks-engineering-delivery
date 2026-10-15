---
description: "Feature specification: 伪造枚举表裁决与门禁边界透明化"
---

# Feature Specification: 伪造枚举表裁决与门禁边界透明化

**Feature Branch**: `223-enum-fabrication-and-gate-boundaries`
**Created**: 2026-10-08
**Status**: Draft
**Input**: 用户交接待办（2026-10-08 上一轮）+ `docs/ROADMAP.md` §一 游标的「下一 WIP」

**上游血缘**：`specs/222-relation-enum-and-public-contract/`（同族：**枚举名/值与官方源对不上**）。
本切片是 222 的**同型续集**，但对象不同：222 修的是**有官方标注却被写错**的表；本切片修的是
**根本没有官方对应、却被来源块自称官方**的表，以及**让这类表能被门禁看见**。

---

## 一、问题陈述（为什么开这个切片）

本仓的铁律 1 是「缝合优先，不发明」：每个值都要能指认官方出处。但**来源块本身可以撒谎** ——
一段注释写着「照录 `C:\swapi\enums\X.md`」，而表里的内容与那个文件**毫无关系**。
更糟的是：**两道门禁都看不见它**。

本切片处理三个互相咬合的事实：

| # | 事实 | 证据（本轮实测） |
|---|---|---|
| F1 | `scripts/sw_pattern.py:95/105` 两张表的来源块自称对应官方枚举页，**键与值全部对不上** | 官方 `swPatternElementSelection_e.md` 只有 **3** 项、`swFeaturesToPatternType_e.md` 只有 **2** 项；表里是 **7** 项 / **8** 项 |
| F2 | `scripts/check_undefined_names.py` 对**整文件静默跳过**且**从不报「跳过了谁」** | 本轮实测**静默跳过 7 个文件**，含 `scripts/sw_part.py`（★ 222 那个 `from typing import Any` 致命缺陷正藏在它里面） |
| F3 | `scripts/check_enum_values_vs_reflection.py` 只 glob `scripts/sw_*.py`，且要求小写键 + `# swXxx` 注释；**边界外的表静默不报** | 本轮实测**覆盖 122 行**；F1 那两张表**一行都不在**这 122 里（没有 `# swXxx` 注释） |
| F4 | 打包副本 `apps/workbench-ui/src-tauri/resources/skill/` 落后于源 | 实测 `find_bundled_skill_drift` 报 **4** 处内容不一致 + **1** 个文件缺失（`scripts/sw_sketch_relations.py`） |

---

## 二、需求（每条带「来源」与「验收场景」）

### US1（P1）—— 伪造枚举表的裁决与修正 🎯 MVP

**FR-001**：对 `scripts/sw_pattern.py` 的 `SWS_PATTERN_ELEMENT_SELECTION` 与
`SWS_FEATURES_TO_PATTERN` **给出裁决**：属于「**自造抽象冒官方名**」还是「照录写错」。
裁决必须写出**判据**（键是否在官方源出现过、值是否在官方源出现过），不得只给结论。

- **来源**：官方 `C:\swapi\enums\swPatternElementSelection_e.md`（MIT-free 官方文档快照）·
  `C:\swapi\enums\swFeaturesToPatternType_e.md` · 出厂反射 `D:\AI\SW\_raw\enum_values_sldworks.txt`
  · `C:\swapi\types\ILinearPatternFeatureData\PatternElement.md`（证明 `PatternElement` 属性的取值域**就是** `swPatternElementSelection_e`）。
- **license**：官方文档与反射转储为本仓工作区内的**只读参考**，不引入第三方代码；本仓 MIT。
- **验收场景**：`tests/test_pattern_enum_alignment.py` 断言两张表与官方枚举**逐项相等**（键、值、成员名）。
  改动前必须**红**。

**FR-002**：两张表按官方**重写**，键与值取自官方枚举，且每行带 `# sw<官方成员名>` 注释
（使 F3 的门禁**能覆盖**它们）。

- **来源**：同 FR-001；写法沿用本模块既有 `SWS_PATTERN_END_CONDITIONS` 的「小写语义键 + `# swXxx`」约定。
- **license**：本仓 MIT。
- **验收场景**：门禁 `scripts/check_enum_values_vs_reflection.py` 里 `sw_pattern.py` 的覆盖行数
  从 **2**（仅 `SWS_PATTERN_END_CONDITIONS`）升到 **≥7**（+3 +2 两张表）—— 即两张表**首次**贡献覆盖行。

**FR-003**：订正来源块 —— 原块声称「全量照录」官方页，须改为**如实描述**：写清官方页的真实项数、
以及本表是**官方枚举的忠实投影**（不是自造语义层）。

- **来源**：AGENTS.md 铁律 1 / 铁律 5（查不到就写查不到）。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_pattern_enum_alignment.py` 断言来源块里出现官方页路径**且**不再出现
  「7 项/8 项」这类与官方不符的自述（用「官方页项数」与「表项数」相等来机器判定）。

**FR-004**：`__all__` 的公开面**保持**（表名不删），但内容替换为官方枚举 —— 因为
`read_pattern_element()` 读的 `PatternElement` 属性官方取值域就是 `swPatternElementSelection_e`，
旧表会让调用方**按错值解读**。

- **来源**：`C:\swapi\types\ILinearPatternFeatureData\PatternElement.md` 的 `## Returns` 逐字。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_sw_pattern_contract.py`（既有）保持绿；新增判据断言 `__all__` 含两表名。

### US2（P1）—— 两道门禁的边界透明化

**FR-010**：`scripts/check_undefined_names.py` 在跳过任何文件时，**必须打印被跳过的文件与原因**
（`from x import *` 还是运行期 `globals()` 注入），并给出计数；**不得静默**。

- **来源**：本项目自身门禁（`scripts/check_undefined_names.py` 的 `_has_star_import` 注释自陈
  「本文件跳过」，但主流程从不报告）。判据依据：AGENTS.md「一个事实一个家」的反面 —— **看不见的豁免**。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_gate_boundary_transparency.py` 跑该门禁为子进程，断言 stdout 里出现
  被跳过文件的**相对路径**与**原因词**；改动前必须**红**（当前输出只有「扫 962 个文件 · 命中 0 处」）。

**FR-011**：`scripts/check_enum_values_vs_reflection.py` 必须打印**覆盖清单**：
扫了哪些文件、找到多少张「整数枚举表」、其中多少张**被值+成员名判据覆盖**、多少张**未覆盖**，
并把未覆盖的**表名逐个列出**（不是只给个数）。

- **来源**：本项目自身门禁。判据依据：同 FR-010 —— **静默漏过 = 看不见的豁免**。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_gate_boundary_transparency.py` 断言 stdout 出现覆盖清单段
  （含「已覆盖 / 未覆盖」计数）且**计数与所列表名条数一致**；改动前必须**红**。

**FR-012**：扫描边界从 `scripts/sw_*.py` 扩到 `scripts/**/*.py`（保持「值 + `# swXxx`」为**覆盖**判据，
新增的是**可见性**而非放宽判定）。`mcp-server/**/*.py` 只做**只读清点**，不引入新的 FAIL。

- **来源**：本项目自身门禁。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_gate_boundary_transparency.py` 断言覆盖清单的「扫描文件数」> 原 `scripts/sw_*.py` 的条数。

### US4（P2）—— 同类候选：门禁看不见的错值表

> ★ 来源：本切片的**全仓同类候选扫描**（委派只读核对成员完成，报告
> `output/223-verify/fabrication-candidates.md`）。它找出 2 处**「门禁双盲」**表 ——
> 既**没有** `# swXxx` 注释（门禁看不见），值**又**与出厂反射不符。

**FR-030**：`scripts/sw_ref_geometry.py` 的 `REF_PLANE_CONSTRAINTS` 两个值按**出厂反射**订正：
`OptionProjectToNearestLocation` 1028 → **1024**、`OptionProjectAlongSketchNormal` 2056 → **2048**；
并补 `# sw<成员名>` 注释（使其进入门禁覆盖面）。

- **来源**：官方 `C:\swapi\enums\swRefPlaneReferenceConstraints_e.md` —— 该页**自身矛盾**
  （写 `1028 or 0x400`、`2056 or 0x800`，而 `0x400=1024`、`0x800=2048`）· 出厂反射
  `_raw/enum_values_sldworks.txt`（`…NearestLocation = 1024` / `…AlongSketchNormal = 2048`）。
  ⇒ 铁律 4：取反射（反射恰等于 md 的**十六进制列**）。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_pattern_enum_alignment.py::test_ref_plane_constraints_values_match_reflection`
  断言 10 项与反射一致；改动前必须**红**。

**FR-031**：`scripts/sw_sheet_metal.py` 的 `HEM_POSITIONS` 是**真两源冲突**
（md `Inside=1/Outside=2` · 反射 `0/1`）⇒ 按**铁律 4 取反射（0/1）**，补 `# sw<成员名>` 注释，
并把冲突**写进注释**；同步更新耦合的 `tests/test_tool_specs_batch93.py` 与工具描述。

- **来源**：官方 `C:\swapi\enums\swHemPositionTypes_e.md`（1/2）· 出厂反射（0/1）·
  事实 34/53（`create_hem` 真机五种形态全 `None` ⇒ 改它**不回退任何已验证路径**）。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_tool_specs_batch93.py::test_hem_position_and_relief_tables` 与
  `tests/test_pattern_enum_alignment.py::test_hem_positions_matches_reflection` 同时绿；
  后者改动前必须**红**。

**FR-032**：`references/part-modeling.md` 的「常用约束类型」清单行**只许列官方名** ——
它此前仍写 `sgEQUAL` / `sgMIDPOINT`（★ 222 只改了 `.py`，**漏了这份文档**）。

- **来源**：官方 `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` 的 `## Remarks` · `specs/222` 的裁决。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_bundled_skill_enum_freshness.py::test_bundled_doc_lists_only_official_sg_names`
  断言清单行无旧名、含官方名；改动前必须**红**。

### US3（P2）—— 打包副本同步

**FR-020**：`apps/workbench-ui/src-tauri/resources/skill/` 与源树同步，
`find_bundled_skill_drift()` 返回空。**同步只做复制，不删除任何文件**（先验证待裁剪集为空）。

- **来源**：`scripts/sync_bundled_skill.py`（既有生成器）· `scripts/release_check.py::find_bundled_skill_drift`（既有门禁）。
- **license**：本仓 MIT。
- **验收场景**：`find_bundled_skill_drift(ROOT, BUNDLED)` == `[]`；且 `sync_bundled_skill()` 的 `pruned` 为空列表。

**FR-021**：打包副本内**不得**再出现 `sgEQUAL` / `sgMIDPOINT`（222 已判定的非官方名）。

- **来源**：`specs/222` 的裁决；官方 `C:\swapi\types\IModelDoc2\SketchAddConstraints.md` 的 `## Remarks`。
- **license**：本仓 MIT。
- **验收场景**：`tests/test_bundled_skill_enum_freshness.py` 断言打包副本的
  `scripts/sw_part.py` / `mcp-server/tool_specs_batch16.py` / `references/part-modeling.md`
  不含那两个串；改动前必须**红**。

---

## 三、关键实体

| 实体 | 是什么 | 状态真源 |
|---|---|---|
| `SWS_PATTERN_ELEMENT_SELECTION` | `swPatternElementSelection_e` 的投影（官方 3 项） | `C:\swapi\enums\swPatternElementSelection_e.md` |
| `SWS_FEATURES_TO_PATTERN` | `swFeaturesToPatternType_e` 的投影（官方 2 项） | `C:\swapi\enums\swFeaturesToPatternType_e.md` |
| 出厂反射转储 | `_raw/enum_values_sldworks.txt`（10588 成员，铁律 4 的裁决基准） | 反射转储本身 |
| 打包 Skill 快照 | `apps/workbench-ui/src-tauri/resources/skill/` | `sync_bundled_skill.py` 的产物 |

---

## 四、验收判据（Summary）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 两张表与官方枚举逐项相等 | `tests/test_pattern_enum_alignment.py` 全绿 |
| SC-2 | 两道门禁的边界**可见** | `tests/test_gate_boundary_transparency.py` 全绿 |
| SC-3 | 打包副本与源一致、无非官方 sg 名 | `tests/test_bundled_skill_enum_freshness.py` 全绿 |
| SC-4 | 既有回归不破 | `tests/test_sw_pattern_contract.py` 全绿 |
| SC-5 | 判据**先红后绿** | 三份新测试在改动前各至少一次红（读数记入 `acceptance.md`） |

---

## 五、Assumptions

- **不删表、只改内容**：两张表在 `__all__` 里，属模块公开面；且 `PatternElement` 的官方取值域就是
  `swPatternElementSelection_e` ⇒ 修正内容即**修复**，删表反而丢失投影能力。
- **无生产消费者**：全仓 grep 确认 `SWS_PATTERN_ELEMENT_SELECTION` / `SWS_FEATURES_TO_PATTERN`
  除 `sw_pattern.py` 自身与 `__all__` 外**无引用**（`tests/test_sw_pattern_contract.py` 只引用
  `SWS_PATTERN_END_CONDITIONS`）⇒ 本次是**公开面内容修正**，不是行为回归。
- **离线边界**：不调用 SolidWorks / COM；所有结论来自三源静态比对。
- **`_SG_RELATIONS` 的 45/77 口径**：官方 `SketchAddConstraints` 的 Remarks 共 **77 行 / 45 个不重复名**
  （分两子块：旧式 `sgHORIZONTAL` 与新式 `sgHORIZONTAL2D`）。`_SG_RELATIONS` 是**常用子集（12 项）**，
  是官方 45 的**真子集**（本轮逐项核过）⇒ **本切片不动它**，只在 `plan.md` 与
  `tests/test_pattern_enum_alignment.py` 里把它登记为「已核：子集合法、非伪造」。

## 六、Out of Scope

- 真机验证任一枚举值（需业主另行授权 COM）。
- 把 `_SG_RELATIONS` 扩到官方 45 项（需先知道哪些在本机 2D 草图可用 —— 属真机范围）。
- 全量 pytest 与 `tools/round_chain.ps1`（只在发布前/改门禁本体时跑；本切片**改了门禁本体**
  ⇒ 收尾时按 AGENTS.md §十六 另跑一次全量）。
