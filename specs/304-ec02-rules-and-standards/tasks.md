# Tasks — **EC02 领域规则、计算与国家标准适用性基础**

**Feature**: `specs/304-ec02-rules-and-standards/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC02**（★ T01–T08 逐字）
**对应**: `spec.md`（★ 8 FR · 8 V）· `baseline.md`（★ G0）· `acceptance.md`

---

## 一、★★★★★ 当前状态总表（★ 2026-10-10 逐条实测）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC02-T01** rule/calculation 标准接口 | ✅ **完成** | ★ `Rule`（★ `unit`/`applicable_devices`/`source`/`threshold`/`counterexample`/`priority`/`statistical_basis`）· ★ `RuleDecision`（★ **必带 `basis`**） |
| **EC02-T02** 标准登记模型 | ✅ **完成** | ★ `StandardRef`（★ 标准号/条款/效力/**查证日期**/许可/适用设备/证据类型/`evidence_url`/`doc_id`）· ★ **效力四色与 KS 对齐** |
| **EC02-T03** 五类义务分开 | ✅ **完成** | ★ `ObligationKind`（★ 强制/合同/推荐/企业/经验）· ★ `HARD` **只有前两类** ⇒ ★ **GB/T 不当硬义务** |
| **EC02-T04** 首批五个算法 | ✅ **完成** | ★ `tolerance_stack_worst_case` · `tolerance_stack_rss` · `hole_edge_margin` · `shaft_strength` · `power_efficiency_margin` |
| **EC02-T05** 算例/独立复算/边界/量纲/单调/区间 | ✅ **完成** | ★ **5 个算法各自独立复算**（★ 手写公式）· ★ 单调性 · ★ 边界（★ 直径 0）· ★ 区间（★ **RSS ≤ 极限法**） |
| **EC02-T06** 依据/反例/优先级仲裁 | ✅ **完成** | ★ `RuleDecision.basis` · ★ `Rule.counterexample` · ★ `arbitrate()`（★ **按优先级** · ★ **平局 `unknown`，不投票**） |
| **EC02-T07** 版本变化影响清单 + 证据过期 | ✅ **完成** | ★ `version_impact()`（★ **受影响 ⇒ 自动标 `expired` + 降为 `unknown`** · ★ **要求重判**）· ★ 判据 5 例 |
| **EC02-T08** 适用性矩阵 + 未知类别待澄清 | ✅ **完成** | ★ `applicability_lookup()`（★ **未知类别 ⇒ `needs_clarification`** · ★ **「无标准适用」须带依据**） |

---

## 二、阶段A —— 接口与登记

- [x] **EC02-T01** 定义 rule/calculation 标准接口：输入单位、适用域、来源、版本、阈值、输出和 `unknown`。依赖：无。
  **→ 验收**：★ `test_v3_rule_interface_has_all_required_fields` + ★ `test_v1_rule_without_source_cannot_pass`。

- [x] **EC02-T02** 建立标准登记模型：标准号、版本、实施/废止状态**查证日期**、许可、适用设备、条款索引、证据类型。依赖：T01。
  **→ 验收**：★ `StandardRef` 字段齐 · ★ `test_v1_rule_without_verification_date_cannot_pass`。

- [x] **EC02-T03** 分开强制义务、合同要求、推荐标准、企业规范和经验规则，**不用 GB/T 标签替代法律适用判断**。依赖：T01。
  **→ 验收**：★ `test_obligation_kinds_are_separated` + `test_recommended_standard_is_not_hard`。

## 三、阶段B —— 算法与仲裁

- [x] **EC02-T04** 第一批算法做尺寸链极限法、明确统计假设的 RSS、孔边距/工具可达性、基本轴强度、传动功率/效率边界。依赖：T01。
  **→ 验收**：★ `test_v5_*` 三例 + ★ `test_v6_*` 五例。

- [x] **EC02-T05** 建立计算手册算例/独立复算/边界值/量纲/单调性/区间检查。依赖：T04。
  **→ 验收**：★ `test_v6_*`（★ **5 个算法各自手写复算** + ★ 单调 + ★ 边界 + ★ 区间）。

- [x] **EC02-T06** 规则决策保留依据与反例；矛盾规则按**优先级和适用性**处理，**不能多数投票**。依赖：T01。
  **→ 验收**：★ `test_v7_higher_priority_wins` + ★★ `test_v7_tie_is_unknown_not_a_vote`（★ **红基线已验**）。

- [x] **EC02-T07** 标准版本变化形成**影响清单**；证据**自动标过期**；**不能只改数据库版本号**。依赖：T02/T06。
  **→ 验收**：★ `tests/test_ec02_version_impact.py`（★ **5 例**：★ 换版 ⇒ 标 `expired` + 降 `unknown` · ★ 要求重判 · ★ 无变化不瞎报 · ★ 带版本对与依据 · ★ **过期不得放行**）。

- [x] **EC02-T08** 建立首个限定设备类别的适用性矩阵；**未知类别返回待澄清**，**不能「无标准适用」**。依赖：T01。
  **→ 验收**：★ `test_v8_*` 三例（★ **红基线已验**）。

---

## 四、★★ 依赖

```text
T01 → T02 → T03
T01 → T04 → T05
T01 → T06
T02/T06 → T07
T01 → T08
```

---

## 五、★★★ 与 EC01 / EC03 / EC11 的边界

| ★ 谁 | ★ 做什么 | ★ **不做什么** |
|---|---|---|
| ★ **EC01**（★ 已收口） | ★ 冻结**工程意图** | ★ 不判「行不行」 |
| ★ **EC02**（★ 本特性） | ★★ **确定性规则与计算** ⇒ 回答「行不行」 | ★ **不碰 COM** · ★ **不调 LLM** · ★ **不新建检索**（★ 复用 KS） |
| ★ **EC03** | ★ 方法库与规划编译 | ★ 不改规则（★ 只**消费**判定） |
| ★ **EC11** | ★ 合规发布 | ★ ★ **标准登记表的自动填充**属它（★ 本特性手工填） |
