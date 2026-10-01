# Implementation Plan: 视图读取 + 体上实体枚举

**Branch**: `126-view-selection-batch` | **Date**: 2026-10-01 | **Spec**: 同目录

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 本批不连 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `scripts/sw_view.py` / `sw_selection_spec.py` 的函数签名与 docstring | 形参、返回值、注意事项 | `inspect.signature` + `inspect.getsource`（照实）|
| `sw_selection_spec.ENTITY_KINDS`（本项目常量）| `kind` 合法值 | `['EDGE','FACE']` |
| `IModelDoc.ActiveView`（官方属性）| `get_active_view` 的官方依据 | 该函数自己的来源块已写（**本批不引入新 COM 成员**）|
| `C:\swapi\types\IModelDoc2\ActiveView.md` 等 | 交叉核 | **本批未查**（不引入新成员 ⇒ 不必）；★ 如实记 |

**裁决顺序**：出厂类型库/反射 > `C:\swapi` markdown > 本项目常量与来源块。

## ⚠ 查不到 / 做不到（§III）
```
① `activate_view` / `add_perspective` 要 `IView`，而**既有注入器没有 `view`**
   核查命令（可重跑）：
       python -c "import re;from pathlib import Path;t=Path(r'C:/swprojects/sw-skill-fork/mcp-server/tool_registry.py').read_text(encoding='utf-8');print(re.findall(r'\"(model|sw_app|study|view)\"\s*:', t))"
   期望：只出现 model/sw_app/study（**没有 view**）
② 既有工具里**没有**"靠 model 取 view"的先例
   核查命令：见 tasks.md T-12602（期望**空**）
⇒ 处置：本批**不挂**这两个，记进队列 A10。
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"未查"的如实标注）|
| §III 查不到 | 附核查命令 | ✅ 两条命令 |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch14.py    ← 新增 2 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 51→53 · 96→98
```
