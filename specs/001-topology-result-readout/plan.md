# Implementation Plan: 拓扑优化结果读取

**Feature**: `001-topology-result-readout` · **Spec**: [spec.md](spec.md) · **Created**: 2026-10-01

## Summary

判定「Material Mass 图 / 收敛数据 / 导出平滑网格」三件事**有没有公开 API**，
并在此过程中把 `ICWResults` 里**确实可用**的读数入口包成函数。

**本特性的交付物是一个判定 + 证据，不是一堆新代码。** 若判定为「无 API」，
那么代码增量很小，价值在**证据的可复查性**。

## Technical Context

| 项 | 值 |
|---|---|
| 语言 / 运行时 | Python 3.14 + pywin32（迟到绑定 `dynamic.DumbDispatch`） |
| 目标宿主 | SolidWorks 2026 SP4.1（`RevisionNumber` = 34.4.1）+ Simulation 加载项 |
| 代码落点 | `C:\swprojects\sw-skill-fork\scripts\sw_topology.py`（扩既有模块） |
| 测试落点 | `C:\swprojects\sw-skill-fork\tests\test_sw_topology_contract.py`（扩既有契约测试） |
| 证据落点 | `D:\AI\SW\_raw\`（探针脚本与输出）+ `capabilities.yaml` 的 `limitations` |
| 性能约束 | **本特性的关键前提**：跑一次拓扑优化（网格 + 求解）必须在本机可行 |

**⚠ 本特性最大的不确定性**：`study.Results` 在**没跑过优化的研究**上返回 False
（本轮实测）⇒ `ICWResults` 的运行期试探**没做成**。
**必须先在真机上跑通一次优化**，否则 FR-001 无法满足。

## Constitution Check

| 宪法条款 | 本特性如何满足 |
|---|---|
| §I 缝合优先 | 不新增「发明」的能力；本特性若判定无 API，则**不写代码**去硬凑 |
| §II 签名三源互证 | §背景 的四源表即此条落实（比三源多一关：运行期） |
| §III 查不到就写查不到 | **本特性就是这条的范例**：四源皆无才写「查不到」，且必须附命令 |
| §IV 许可红线 | 未引入任何第三方代码；官方文档只用于接口判定 |
| §V 验收可跑 | SC-001–SC-004 各给可重跑命令 |
| SDD 接口表 | tasks.md 的每个任务带 `→ 验收:`；完成后条目的 `level` 仍须取自五级枚举 |

**无违反项。**

## Project Structure

### Documentation (this feature)

```
D:\AI\SW\specs\001-topology-result-readout\
├── spec.md          本特性规格（四源取证表在此）
├── plan.md          本文件
└── tasks.md         任务分解
```

### Source Code (repository root)

```
C:\swprojects\sw-skill-fork\
├── scripts\sw_topology.py            ← 扩：加 collect_topology_numbers()
├── tests\test_sw_topology_contract.py ← 扩：加读数函数的契约测试
└── capabilities.yaml                 ← 改：topology_optimization 的 limitations
```

### Evidence (workspace)

```
D:\AI\SW\
├── probe_results_api_surface.py      ← 已有：运行期成员试探
├── probe_run_and_read_results.py     ← 新增：跑一次优化再试探（闭合 FR-001）
└── _raw\topo-reflect\                ← 反射转储（四源中的两源）
```

## 实施顺序（**先证据，后代码**）

```
1. 跑一次真机拓扑优化 → 拿到有结果的研究     ← 阻塞全部后续
2. 在 ICWResults 上试探六个候选名            ← US1 的交付
3. 若存在 ⇒ 实现导出；若不存在 ⇒ 写「查不到」+ 评估替代路径
4. 实现 collect_topology_numbers()（US2）    ← 不依赖第 3 步结论
5. 回写 capabilities.yaml 与 ROADMAP 游标
```

**第 1 步是唯一的阻塞点。** 若跑不通，本特性降级为「静态三源已查、运行期未验」，
并在 limitations 里**明说未验**（不得含糊成「已验证不存在」）。

## Complexity Tracking

| 决策 | 为什么不更简单 |
|---|---|
| 四源而不是三源 | 铁律 4 说三源互证，但「某方法不存在」这类**否定命题**静态证据弱（延迟绑定下 IDispatch 可能暴露更多）⇒ 必须加运行期一关 |
| 不直接写「做不到」 | A2/A7 要求可追溯；「试过了不行」不可复查，等于没证据 |
| 读数函数与导出**分开**做 | 「读不到图」≠「读不到数」；混在一起会让整个域被误判为不可用 |
