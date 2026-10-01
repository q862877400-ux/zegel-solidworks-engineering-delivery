# Implementation Plan: 草图几何关系 + 镜像特征

**Branch**: `128-sketch-relation-mirror-batch` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Summary
把 `sw_part` 里**按规则 2/3 分诊后真正干净**的 2 个挂成工具；
★ 并给那 14 个**逐条写明归属**（本批 / A6 / A8 / 本来就坏）。

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 本批不连 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `scripts/sw_part.py` 的函数签名与 docstring | 形参名、`relation_type` 合法值 | `inspect.signature` + `inspect.getdoc`（照实）|
| 规则 2 / 规则 3（`AGENTS.md §五`）| 分诊的判据 | 逐条套用（见 spec 的来源表）|
| `D:/AI/SW/output/orphan-capabilities.json` | 14 个的签名与可注入性 | 读出（生成物）|
| `C:\swapi` / 反射 | 官方成员签名 | **不引入新 COM 成员** ⇒ 不适用；★ 如实记 |

**裁决顺序**：出厂类型库/反射 > `C:\swapi` markdown > 目标函数 docstring > 本项目规则表。

## ⚠ 两处核查命令（§III，**都排除本批产物**，事实 147）
```
① `relation_type` 的合法值确实来自 docstring（不是猜）：
   python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import sw_part as m;print(m.add_sketch_relation.__doc__)"
   期望：含 sgFIXED … sgCOINCIDENT 共 12 个
② `insert_composite_curve` 是坏的（事实 121/124）：
   python -c "import re,sys;from pathlib import Path;t=Path(r'D:\AI\SW\docs\known-facts.md').read_text(encoding='utf-8');print([l[:80] for l in t.splitlines() if 'InsertCompositeCurve' in l][:3])"
   期望：至少一条记着"返回 False / 真失败"
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅ |
| §III 查不到 | 附核查命令 | ✅ 两条，且**都排除本批产物** |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch16.py    ← 新增 2 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 54→56 · 99→101
```
