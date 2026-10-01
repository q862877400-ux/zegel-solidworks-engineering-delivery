import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\124-topology-batch2")
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# Feature Specification: 拓扑族第二批（脱模 / 应力约束 / 对称）

**Feature Branch**: `124-topology-batch2` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A1（`docs/backlog-8h.md`）—— 继续把孤立能力挂成 MCP 工具。

## 来源（宪法 §I：每条需求带来源；§IV：带 license）

| 需求 | 来源 | license |
|---|---|---|
| 暴露 `create_demold_control` / `create_stress_constraint` / `create_symmetry_control` | **本项目自身既有模式**（包装 `scripts/sw_topology.py`，**不是第三方移植**）| 本仓库 **MIT** |
| 三个枚举的**取值** | **出厂反射转储** `D:/AI/SW/_raw/reflect/enum_cosworks.txt`（官方类型库）| 不适用（官方元数据）|
| 对称类型的取值语义 | **官方 VBA 示例** `Create_Topology_Study_Example_VBA.txt` | 不适用（官方示例）|
| 工具声明形状 | 既有 `mcp-server/tool_specs_batch1.py`（`solidworks_topology_*` 三工具）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能一句话加"制造约束"（Priority: P1）

用户要对一个拓扑研究加**脱模方向**约束（铸造件必须能拔模），
现在只能写脚本调 `sw_topology.create_demold_control`；希望能在 MCP 里直接点。

**Why this priority**: 拓扑那族里"约束/控制"是**唯一没挂出去**的一环，缺了它拓扑工具链是断的。

**Independent Test**: 单独注册后，`all_specs()` 里出现这三个名字，且规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 45 变 **48**（本批 3 个）
2. **Given** 一个已存在的拓扑研究，**When** 用 `solidworks_topology_create_demold_control`，
   **Then** 工具把 `direction` 透传给 `create_demold_control(study, *, direction)`，**参数名与真名一致**
3. **Given** 本批的 3 个工具，**When** 跑规则 1/2/3 门禁，**Then** 全过（无裸坐标、名带 `solidworks_` 前缀）

### User Story 2 - 枚举取值有据可查（Priority: P2）

用户看到 `direction` / `comparator` 时要知道**能填什么**，而不是去翻转储。

**Independent Test**: 每个带枚举的参数，其 `description` 里**列出取值与含义**。

**Acceptance Scenarios**:
1. **Given** `direction` 参数，**When** 读它的描述，**Then** 看到 `0=TwoDirectionMidPlane / 1=PullDirectionOnly / 2=Stamping`
2. **Given** `comparator` 参数，**When** 读它的描述，**Then** 看到 `0=IsLessThan / 1=IsGreaterThan / 2=IsInBetween`
3. **Given** `symmetry_type` 参数，**When** 读它的描述，**Then** 看到"取值来自**官方 VBA 示例**（0/1/2）"——
   ★ **并注明枚举名在本地转储里未找到**（宪法 §III：查不到就写查不到）

### User Story 3 - 顺带把上批的一个参数说明补全（Priority: P3）

`create_preserved_region` 上批已挂，但 `option` 只写"官方枚举值"—— 现在知道取值了。

**Independent Test**: 读它的 `description`，能看到 `0=LoadsOnly / 1=FixturesOnly / 2=LoadsAndFixtures / 3=None`。

## 明确不做（附理由）
| 不做 | 理由 |
|---|---|
| 给 `symmetry_type` 编一个枚举名 | ★ 本地转储里**查不到**那个枚举名 ⇒ 按铁律 5 **写"查不到"**，不发明 |
| 真机验证这三个工具 | ★ **暴露 ≠ 验证**（宪法接口表）；真机验证排 B 组（`135`）|
""", encoding="utf-8")

(S / "plan.md").write_text("""# Implementation Plan: 拓扑族第二批

**Branch**: `124-topology-batch2` | **Date**: 2026-10-01 | **Spec**: `specs/124-topology-batch2/spec.md`

## Summary
把 `sw_topology` 里 3 个「目标/约束/控制」构造器挂成 MCP 工具（`inject="study"`，照既有模板），
并把**已核到的官方枚举取值**写进参数描述；顺带补全上批 `create_preserved_region` 的说明。

## Technical Context
**Language/Version**: Python 3.14.7 · **Primary Dependencies**: `tool_registry.Param/ToolSpec`（既有）
**Testing**: `pytest`（含两处"钉死数量"的计数测试）· **Project Type**: 库 + MCP server
**Constraints**: 规则 1（`solidworks_` 前缀）· 规则 2（长度 `_mm`）· 规则 3（禁裸坐标）

## ★ 要查的官方源（宪法 §II）与冲突裁决顺序
| 源 | 用途 | 本次查到什么 |
|---|---|---|
| 出厂反射 `D:/AI/SW/_raw/reflect/enum_cosworks.txt` | **枚举取值** | `swsTopologyDemoldDirectionOption_e`（0/1/2）· `swsTopologyStudyConstraintComparator_e`（0/1/2）· `swsTopologyPreservedRegionOption_e`（0/1/2/3）|
| 官方 VBA 示例 `Create_Topology_Study_Example_VBA.txt` | **对称类型的取值语义** | `SelectSymmetryType 0/1/2`，注释 `'Define topology one-half symmetry control'` |
| `C:\\swapi\\types\\ISldWorks\\…` 等 markdown | 参数与返回 | 本次**不引入新 COM 成员**（只做参数搬运）⇒ 不适用 |
| 三方函数签名 `scripts/sw_topology.py` | 形参名与默认值 | `inspect.signature` 取到（照实，不发明）|

**裁决顺序**：出厂类型库/反射 **>** 官方 VBA 示例 **>** `C:\\swapi` markdown。
★ 本次**无冲突**（反射与 VBA 示例一致）。

## ⚠ 一处**查不到**（宪法 §III）
```
对称类型的**枚举名**（如 `swsTopologySymmetryType_e`）在本地转储里**没有** ——
`enum_cosworks.txt` 里搜不到该名。★ 只查到官方 VBA 示例的**取值用法**（0/1/2）。
⇒ 处置：工具描述里**如实标注**"取值来自官方 VBA 示例；枚举名未在本地转储中找到"。
   核查命令（可重跑）：见 tasks.md T-12402。
```

## Constitution Check（§I–§V，GATE）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | spec 每条需求有来源 | ✅ 四条来源表 |
| §II 官方源 | plan 列源 + 裁决序 | ✅ 上表 |
| §III 查不到 | 「应该有」附核查命令 | ✅ 对称枚举名**明写查不到** + 命令 |
| §IV license | 每个来源行带 license | ✅ |
| §V 可跑验收 | tasks 每条带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch12.py   ← 新增（3 条 ToolSpec）
mcp-server/register_capabilities.py ← BATCH_MODULES 加一行
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 两处计数 +3（45→48 · 90→93）
```
""", encoding="utf-8")

(S / "tasks.md").write_text("""# Tasks: 拓扑族第二批

- [x] T-12401 写 `mcp-server/tool_specs_batch12.py`（3 条 `ToolSpec`，照 `batch1` 的 `study` 模板）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\mcp-server',r'C:\\swprojects\\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**48**）
- [x] T-12402 ★ 三个枚举的**取值**逐个核到（可重跑的命令）
  `→ 验收:` `python -c "import re,sys;from pathlib import Path;t=Path(r'D:/AI/SW/_raw/reflect/enum_cosworks.txt').read_text(encoding='utf-8',errors='replace');[print(n, n in t) for n in ('swsTopologyDemoldDirectionOption_e','swsTopologyStudyConstraintComparator_e','swsTopologyPreservedRegionOption_e','swsTopologySymmetryType_e')]"`
  （期望 **True/True/True/False** —— ★ 最后一个 False **就是"查不到"的证据**）
- [x] T-12403 注册（`BATCH_MODULES` 加一行）并过规则 1/2/3 门禁
  `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`（0 failed）
- [x] T-12404 两处计数测试同步更新（45→48 · 90→93）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12405 五处口径一致地动 3
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12406 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
""", encoding="utf-8")

(S / "checklist.md").write_text("""# Checklist: 拓扑族第二批

- [x] **规则 1**：三个工具名都是 `solidworks_topology_create_*`（`solidworks_` 前缀，不与 `cadstudio_*` 混用）
- [x] **规则 2**：长度参数带 `_mm`（本批无长度参数）· 角度无
- [x] **规则 3**：无裸坐标（本批全是 `study` + 枚举/数值入参）
- [x] **参数名与目标函数真名一致**（`reduce_percent` / `specified_factor` / `option` / `direction` / `value` / `comparator` / `symmetry_type`）
- [x] ★ **每个枚举参数在描述里列出取值与含义**
- [x] ★ **查不到的**（对称枚举名）**如实标注**，不发明
- [x] 计数类测试**同步更新**（两处）
- [x] **不声称真机验证**（暴露 ≠ 验证；真机排 `135`）
- [x] 特性目录写完**不再改**（Flow-forward）
""", encoding="utf-8")

(S / "converge.md").write_text("""# Converge: 拓扑族第二批

## 结果
| 判据 | 结论 |
|---|---|
| 注册数 45 → **48** | （见 tasks.md 的验收命令）|
| 三个枚举取值核到 | ✅ 反射转储里三个都在 |
| ★ 对称枚举名**查不到** | ✅ 如实标注（T-12402 那条命令期望 `False`）|
| 规则 1/2/3 门禁 | ✅ |
| 两处计数同步 | ✅ |
| 五处口径一致动 3 | ✅ |
| 全链 + 回归 | ✅ |

## ★ 未查证（逐条）
* ⚠ **没跑真机** —— 本批只做"暴露"，真机验证排 `135`（B2）；
* ⚠ `symmetry_type` 的取值**语义**只有"官方示例用了 0/1/2 + 注释写 one-half" ⇒
  **0 未必就等于 one-half**（★ 不猜；要确定得真机试，排 `135`）；
* ⚠ `direction` 的 `2=Stamping` 在示例里**没出现** ⇒ 语义来自枚举名，**未真机核**。
""", encoding="utf-8")
print("  ok Spec Kit 124 五件套已写")
