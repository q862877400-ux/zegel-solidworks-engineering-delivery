# Implementation Plan: 拓扑族第二批

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
| `C:\swapi\types\ISldWorks\…` 等 markdown | 参数与返回 | 本次**不引入新 COM 成员**（只做参数搬运）⇒ 不适用 |
| 三方函数签名 `scripts/sw_topology.py` | 形参名与默认值 | `inspect.signature` 取到（照实，不发明）|

**裁决顺序**：出厂类型库/反射 **>** 官方 VBA 示例 **>** `C:\swapi` markdown。
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
