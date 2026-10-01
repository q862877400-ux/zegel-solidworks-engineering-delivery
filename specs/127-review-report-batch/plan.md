# Implementation Plan: 结构化审查报告

**Branch**: `127-review-report-batch` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Summary
把 `sw_review.build_review_report` 挂成 MCP 工具（`inject="model"`），
★ **只暴露 3 个简单参数**（`model` 由注入给、`output_dir`、`basename`），
另两个 **`list` 型**可选参数**刻意不暴露**（无先例 ⇒ 不顺手引入）。

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 本批不连 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `scripts/sw_review.py` 的函数签名与 docstring | 形参名、默认值、返回 | `inspect.signature` + `inspect.getdoc`（照实）|
| `mcp-server/tool_registry.py` 的 `Param`/`check_spec` | 参数类型支持范围 | 读到 `kind` 的说明只列 `str/float/int/bool` |
| 既有 `tool_specs_batch*.py` 全量 | `list` 型参数的**先例** | ★ **空**（T-12702）|
| `C:\swapi` / 反射 | 官方成员签名 | **不引入新 COM 成员** ⇒ 不适用；★ 如实记 |

**裁决顺序**：出厂类型库/反射 > `C:\swapi` markdown > 本项目既有先例 > 该函数自述。

## ⚠ 两处"不硬挂"的核查命令（§III）
```
① `activate_plot` 首参不是注入点：
   python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import inspect,sw_simulation_results as m;print(inspect.signature(m.activate_plot))"
   期望：(results, plot_name: 'str') -> 'bool'
② 没有 list 型 Param 先例：
   Select-String -Path C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch*.py -Pattern 'Param\([^)]*,\s*list'
     | Where-Object { $_.Filename -ne 'tool_specs_batch15.py' }      ← ★ 排除本批产物（事实 147）
   期望：空
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"不适用"的说明）|
| §III 查不到 | 附核查命令 | ✅ 两条（且**都排除了本批产物**）|
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch15.py    ← 新增 1 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 53→54 · 98→99
```
