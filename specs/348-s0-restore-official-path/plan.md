# Implementation Plan: S0 — 恢复首件所需的正式通路

**Feature**: `348-s0-restore-official-path`

**对应 PLAN 阶段**: S0（`docs/ENGINEERING-PATH.md` 第六节）

## Summary

修掉首件链路上的三处执行层阻断，使编译入口、最终 DoD 入口、规划出口都能跑通；
并审计收尾链的副作用。本特性**只修实现，不改判据**。

## Technical Context

- 语言：Python 3.14.7（本仓基线解释器）
- 相关模块：`scripts/engineering/{compiler,registry,housing,planner,_applicability}.py`
- 测试：`tests/test_ec03_compiler.py` · `tests/test_stage7_housing.py` · `tests/test_stage4_planner.py` · `tests/test_stage2_rules.py`
- 不涉及 SolidWorks 真机；全部为离线修复
- 不需要新依赖

## Constitution Check

| 原则 | 本特性如何满足 |
|---|---|
| I 缝合优先 | 三处修复都基于本仓既有模式（`applies_to` / 历史 `evaluate` 实现 / 既有重名处置先例） |
| II 签名三源互证 | 不新增 COM 调用，不涉及 |
| III 查不到就写查不到 | 见下方「官方源核查」 |
| IV 许可红线 | 不引入外部代码 |
| V 验收判据能跑 | tasks.md 每条带 `→ 验收:` 与可跑命令 |

### 官方源核查

本特性**不新增任何 COM 调用**，故无官方签名需核。三处修复全部在纯 Python 层。

`git show a695ac62` 可找回 `FinalDod.evaluate` 的历史实现 —— 这是本仓自身的提交，不是外部来源。

## Project Structure

### Documentation (this feature)

```
specs/348-s0-restore-official-path/
├── spec.md      本特性的需求与验收场景
├── plan.md      本文件
├── tasks.md     施工任务
└── acceptance.md 收口记录（施工后写）
```

### Source Code

| 文件 | 改动性质 |
|---|---|
| `scripts/engineering/compiler.py` | 把 `spec.allows(k)` 改为本仓既有语义的判定 |
| `scripts/engineering/housing.py` | 补回 `FinalDod.evaluate()` |
| `scripts/engineering/_case_collector.py` | 若 `evaluate` 需 `add_case` 之外的协作，在此补 |
| `scripts/engineering/registry.py` | 重名冲突时报出**具体冲突对**，不阻断构建 |
| `tools/round_chain.ps1` | 副作用显式化 |
| `tests/test_*.py` | 只允许**补**断言，不允许放宽既有断言 |

## 关键设计决定

### 决定 1：`allows` 用 `applies_to` 实现，不新造语义

`MethodSpec` 的基类 `ApplicabilityMixin` 已有 `applies_to(device_class)`。
`compiler.py:594` 调用不存在的 `allows(k)` 是**误写**，不是缺功能。

⇒ 改调用点，不扩基类。若将来需要「允许多个域」的语义，另开特性。

### 决定 2：`FinalDod.evaluate` 从 git 历史恢复，不重写

`git show a695ac62` 的删除行里含完整的 `def evaluate(self) -> dict:` 与六条判据。
「仓库统一化」重构把它抽进 `CaseCollectorMixin` 时只补回了 `add_case`，漏了 `evaluate`。

⇒ 恢复原实现到 `housing.py`，保持与历史验收记录的字段一致。

### 决定 3：重名处置按「保留更完整的那份」

`mcp-server/tool_specs_batch116.py` 与本批修复已确立先例：
重复声明时保留参数更全、带 `param_alias`、带官方依据的那份。

`registry.py` 的 `build_registry` 面对的是**实现层**重名，判据不同：
必须报出冲突对（哪两个规范名、各自来自哪个模块），由人决定保留哪份 ——
**不得自动挑一个**。

### 决定 4：收尾链副作用显式化，不改行为

`tools/round_chain.ps1` 里有 `git add -A`、生成器、关闭 SolidWorks。
本特性只做**显式化**（打印将要做什么、给出 `-DryRun`），不改它的既有行为 ——
改行为需要单独的验收判据。

## Complexity Tracking

| 项 | 为什么需要 | 更简单的替代为何不够 |
|---|---|---|
| 从 git 历史恢复 `evaluate` | 保证与历史验收记录字段一致 | 重写会引入字段漂移，使 322 的历史结论无法对账 |
| `round_chain` 只显式化不改行为 | 收尾链是每轮都跑的路径，改行为风险高 | 直接改会同时影响所有后续轮次的证据链 |
