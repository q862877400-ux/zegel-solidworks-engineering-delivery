# Implementation Plan: 静力学真机复验

**Branch**: `134-static-simulation-reverified` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Technical Context
**Language/Version**: Python 3.14.7 · **Testing**: 该脚本**不在 pytest 里跑**（需许可，单次约秒级）
**Target Platform**: 本机 SW 2026 SP4.1（34.4.1）· 单实例 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `C:\swapi\types\ICWStudy\*` 等 | 成员语义 | **不引入新 COM 成员**（只复跑既有脚本）⇒ 不适用 |
| 出厂反射 `reflect/enum_cosworks.txt` | 若要看枚举 | 本次未涉及 |

**裁决顺序**：出厂类型库/反射 > `C:\swapi` markdown。★ 本次无冲突（无新调用）。

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（说明"不适用"的理由）|
| §III 查不到 | 附核查命令 | ✅ 见下（本特性**没有**"应该有"式断言）|
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
无代码改动 —— 本特性只跑既有脚本 + 落证据（output/simulation-evidence.json，gitignore 的产物目录）
```
