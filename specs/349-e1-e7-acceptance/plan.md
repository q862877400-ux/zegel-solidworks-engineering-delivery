# Implementation Plan: S1 — E1–E7 的验收规范与坏样件

**Feature**: `349-e1-e7-acceptance`

**对应 PLAN 阶段**: S1（`docs/ENGINEERING-PATH.md` 第六节）

## Summary

为 E1–E7 各建一对「采集器 / 判定器」，并写出好/坏/缺证据三组样件。
把四个已被实测证明可零成本伪造的估算器降级为预检用途。

## Technical Context

- 语言：Python 3.14.7
- 新增模块落点：`scripts/engineering/acceptance/`（新建子包）
- 复用既有：`part_loop`、`assembly`、`drawing_obligations`、`rule_service`（只读它们的取数逻辑，不改它们的语义）
- 全部离线；不连 SolidWorks
- 不需要新依赖

## Constitution Check

| 原则 | 满足方式 |
|---|---|
| I 缝合优先 | 采集器的取数逻辑复用既有模块；判定器是新增（本仓无先例，属 ④「本项目自身既有模式」的延伸） |
| II 签名三源互证 | 本特性不新增 COM 调用 |
| III 查不到就写查不到 | 见下方 |
| IV 许可红线 | 不引入外部代码 |
| V 验收判据能跑 | tasks.md 每条带 `→ 验收:` |

### 官方源核查

本特性**不新增任何 COM 调用**，故无官方签名需核。
但采集器在 S3/S4 接真机时会需要读草图求解状态与配合状态 ——
**那些成员名本特性不杜撰**，留到 S3 按铁律 4 三源互证后再写。

`docs/ENGINEERING-PATH.md` 第四节已写明：「具体 API 是否支持数值 DOF、
仅支持状态枚举或需要组合诊断，在首个真机技术验证中确认；本文件不杜撰成员名。」

## Project Structure

### Documentation (this feature)

```
specs/349-e1-e7-acceptance/
├── spec.md
├── plan.md
├── tasks.md
└── acceptance.md
```

### Source Code

| 文件 | 性质 |
|---|---|
| `scripts/engineering/acceptance/__init__.py` | 子包入口，导出统一接口 |
| `scripts/engineering/acceptance/result.py` | `CheckResult` 与四值状态 |
| `scripts/engineering/acceptance/e1_sketch.py` … `e7_provenance.py` | 七对采集器/判定器 |
| `scripts/engineering/acceptance/samples.py` | 好/坏/缺证据样件 |
| `tests/test_acceptance_e1_e7.py` | 三态测试 |
| `tests/test_acceptance_forgery.py` | R-04/R-05/R-06/R-09 四条负例 |

## 关键设计决定

### 决定 1：采集器与判定器是**两个函数**，不是一个

`ENGINEERING-PATH.md` 第四节的硬要求。规划器不能提交「我已经检查过」代替观测。

接口：

```
collect_*(artifact) -> Observation   # 只取数，含「观测是否完整」
judge_*(observation, requirement) -> CheckResult   # 只判断，不取数
```

### 决定 2：`unknown` 是一等公民，不是 fail 的别名

采集失败、上游失败、对象未覆盖 —— 全部记 `unknown`。
`unknown` 使报告不绿，但**不等于产物不合格**。两者必须可区分。

### 决定 3：四个既有估算器不改语义，只加「预检」标注

`part_loop.DofPlan.total_dof` 等四处的算法本身在 S1 **不动** ——
动它们等于在判据还没建好时先改实现，无法证明改对了。

S1 只做两件事：
1. 在代码注释与 docstring 里写明「预检用途，不得直接授权交付」
2. 用新判定器证明它们的输出可被伪造（负例）

### 决定 4：坏样件必须「真实触发拒绝」

不是「构造一个明显错误的输入让判定器说 fail」，而是
**用 R-04/R-05/R-06/R-09 记录的伪造手法**，证明判定器能抓住。

## Complexity Tracking

| 项 | 为什么需要 | 更简单的替代为何不够 |
|---|---|---|
| 新建 `acceptance/` 子包 | 七对采集器/判定器 + 统一结果结构，塞进既有模块会破坏其职责 | 塞进 `engineering/` 顶层会与 48 个既有模块混在一起 |
| 四条独立负例文件 | 这四条是历史病症的具体形态，需要单独可见 | 混在三态测试里会被淹没 |
