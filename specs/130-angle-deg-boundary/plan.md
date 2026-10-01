# Implementation Plan: 圆形阵列 + 旋转凸台（角度换算边界）

**Branch**: `130-angle-deg-boundary` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Summary
把 `circular_pattern` / `revolve_boss` 挂成 MCP 工具，表面用 `angle_deg`（规则 2），
★ 用 **`_consumed` + `derived_args`** 在**边界**换算一次（**不是改名**）。

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有 `derived_args` 机制）· 本批不连 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次查到 |
|---|---|---|
| `scripts/sw_part.py` 的函数签名 | 真实形参名（`angle_rad`）| `inspect.signature`（照实）|
| `scripts/sw_connect.py` | 换算助手的**家** | L929 `mm(value)` · L934 `deg(value)` ⇒ 实测 `deg(90)==π/2` |
| `mcp-server/tool_registry.py` | `derived_args` / `_consumed` 的语义 | 读到 docstring：「返回的字典**并进**调用目标函数的关键字实参里」+「派生实参**不得覆盖**已直传的参数名」 |
| `mcp-server/tool_specs_batch3.py` | **同一形状的先例** | `_consumed(...)` + `derived_args` + 声明 `angle_deg` |
| `AGENTS.md` §五 规则 2 / `docs/union-conventions.md` §规则 2 | 判据原文 | 「长度 `_mm`、角度 `_deg`，**换算只在边界做一次**（`sw_connect.mm()`）」|

**裁决顺序**：出厂类型库/反射 > `C:\swapi` > 本项目既有先例 > 目标函数 docstring。
★ 本批**不引入任何新 COM 成员** ⇒ 反射/`C:\swapi` 只用于"这个函数存不存在"的既有判定。

## ⚠ 一处**必须显式**的东西（§III）
```
★ 为什么不能用 `param_alias={"angle_deg": "angle_rad"}` —— 那条路**只改名、不换算**：
   用户填 `90`（度）⇒ 目标函数收到 `90`（**弧度**）⇒ 90 rad ≈ 5157° ⇒ **几何静默错**。
  核查命令（可重跑，证明"改名"与"换算"是两件事）：
     python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];from sw_connect import deg;print(deg(90), 90)"
     期望：1.5707963267948966 90      ← ★ 两个数不同，就是本批要防的那个差
★ 而"换算放哪一层"**已有先例**（batch3）⇒ 照抄形状，不另立：
     `_consumed(*names)` = 「这些入参由 derived_args 消费，**不传给目标函数**」
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"不引入新成员"的说明）|
| §III 查不到 | 附核查命令 | ✅ 一条可跑命令，且它**证明的是核心风险** |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch17.py        ← 新增 2 条 + `_consumed` + `_radians_of_deg`
mcp-server/register_capabilities.py     ← BATCH_MODULES +1
tests/test_tool_specs_batch17.py        ← **新增守卫测试（含负例）**
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 56→58 · 101→103
```
