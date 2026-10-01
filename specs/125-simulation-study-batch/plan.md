# Implementation Plan: 仿真研究族

**Branch**: `125-simulation-study-batch` | **Date**: 2026-10-01 | **Spec**: 同目录

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 单实例 COM（本批不连）

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次查到 |
|---|---|---|
| `scripts/sw_simulation_study.py` / `sw_simulation.py` 的函数签名 | 形参名与默认值 | `inspect.signature` 取到（照实）|
| `C:\swapi\enums\swsUnit_e.md` | `units` 取值 | ★ **文件不在** ⇒ 只能引既有工具的先例描述 |
| 既有工具 `solidworks_topology_run` 的 `units` 描述 | `units` 取值先例 | "0=SI, 1=English, 2=Metric; **-1 is rejected**" |
| 该函数自己的 docstring | `units=-1` 的真机结论 | "**本机实测：units=-1 时返回毫米级数值**" |
| `C:\swapi\types\ICWStudy\GenerateReport.md` | `template` 取值 | ★ 本次**未查到**合法取值 |

**裁决顺序**：出厂类型库/反射 > 官方 markdown > **既有工具先例** > 该函数自述。
★ 本次**刻意不裁决** `units=-1` 的冲突：两处来源**同级**，且**其中之一是"本机实测"** ⇒
  按"真实运行证据优先"取 **-1**，但**把两句话都留在描述里**。

## ⚠ 查不到（§III）
```
`generate_report` 的 `template` 合法取值：`C:\swapi` 与反射里**都没查到**。
核查命令（可重跑）：
    python -c "from pathlib import Path;print([p.name for p in Path(r'C:/swapi/enums').glob('*eport*')])"
    python -c "from pathlib import Path;t=Path(r'D:/AI/SW/_raw/reflect/enum_cosworks.txt').read_text(encoding='utf-8',errors='replace');print('Report' in t)"
```
⇒ 处置：`template` 按普通 `str` 暴露 + 描述里明写"未查到"。

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"刻意不裁决"的说明）|
| §III 查不到 | 附核查命令 | ✅ `template` + `swsUnit_e.md` 不在 |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch13.py    ← 新增 3 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 48→51 · 93→96
```
