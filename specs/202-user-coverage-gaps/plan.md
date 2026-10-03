# Implementation Plan: 用户视角能力覆盖 · 缺口攻关

**Branch**: `202-user-coverage-gaps` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/202-user-coverage-gaps/spec.md`

## Summary

把 `docs/user-feature-coverage.md` §八 的 **35 项缺口**逐项分诊为「**建成 / 带依据的到不了 / 查不到**」，
并顺手把 §五 标注的 `stitched` 转 `verified`。技术路径沿用本仓既有形态：
**官方三源核签名 → `scripts/sw_*.py` 加包装 → `mcp-server/tool_specs_*.py` 挂 ToolSpec → 真机探针（`tools/sw_guard.py`）→ `capabilities.yaml` 标级**。

## Technical Context

**Language/Version**: Python 3.11（`from __future__ import annotations`；顶层脚本与包内相对导入双兼容）
**Primary Dependencies**: `pywin32`（COM 迟到绑定）· 本仓 `scripts/sw_connect.py`（`get_com_member`）· `pytest`
**Storage**: `capabilities.yaml` / `docs/toolbar-ledger.json` / `output/*.json`（证据）
**Testing**: `pytest`（聚焦）+ `scripts/release_check.py`（**25 道门禁**）+ `tools/round_chain.ps1`（收尾链）
**Target Platform**: Windows · SolidWorks 2026 SP4.1 · 中文 UI · **单源运行时**（事实 24）
**Project Type**: 单体库（`scripts/` 能力层 + `mcp-server/` 工具层 + `tools/` 探针 + `tests/`）
**Constraints**: ★ **COM 是 STA 且线程亲和**；★ 真机命令**一律**走 `tools/sw_guard.py`（弹窗护栏）；
★ **不联网**；★ **不手改**任何生成物（`docs/user-feature-coverage.md` · `docs/toolbar-ledger*.json` · `docs/dead-ends.md`）
**Scale/Scope**: 35 个缺口项 + 13 条 `stitched`；预期**能建成的占一部分**，其余**单列并带依据**

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪法条款 | 本计划的落点 | 判据（可 grep） |
|---|---|---|
| **I · 缝合优先** | ★ spec.md 的 **FR-001…FR-012 每条都写了「来源=」** | `grep -c "来源=" spec.md` ≥ 12 |
| **II · 签名三源互证** | 下方「官方源与裁决顺序」段；每个新 COM 调用**先查源再写** | plan 里每个源都有路径；`docs/signature-audit.md` 收录新调用 |
| **III · 查不到就写查不到** | 侦察产物**必须**把查不到的写成「官方没写」，**不许凑** | `grep -c "官方没写" specs/202-user-coverage-gaps/recon/*.md` |
| **IV · 许可红线** | ★ 下方「来源与许可」表**每行都带 `license`** | `grep -c "license" plan.md` ≥ 5 |
| **V · 验收判据必须能跑** | ★ tasks.md **每条**都带 `→ 验收:` + 命令 | `grep -c "→ 验收:" tasks.md` = 任务数 |

★ **与既有载体的接口**（宪法 §SDD 接口表）：`tasks.md` ↔ `docs/ROADMAP.md` 的一个阶段；
实现完成后落 **`capabilities.yaml`**（`level` + `evidence` + `limitations`）。

## 官方源与裁决顺序（宪法 §II）

| 源 | 路径 | 管什么 |
|---|---|---|
| ① 结构化官方 markdown | `C:\swapi\types\<接口>\<成员>.md` | **精确签名 + `## Remarks` + `## Examples` 索引** |
| ② CHM 解包 | `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` | **语义与官方例子正文**（★ 例子给"调用序"，签名与 Remarks 都给不出） |
| ③ 出厂类型库反射 | `D:\AI\SW\_raw\` · `.api-signatures` | **arity 与枚举值；冲突时的裁决者** |

★ **裁决顺序**：③ 反射 **>** ① md **>** ② CHM 正文。★ **三源都查不到 ⇒ 按铁律 5 写「查不到」并停下换思路。**
★ **优先级再一条**：**`## Examples` > `## Remarks` > 签名**（2026-10-03 的实测教训：分割线卡两轮，
真因是**只读了签名与 Remarks、没读例子里的"调用序"**，见 `docs/known-facts.md` 事实 484）。

## 来源与许可（宪法 §IV · ★ 每行都带 license）

| 来源 | license | 能做什么 | 义务 |
|---|---|---|---|
| **官方 API 文档**（`C:\swapi` + CHM 解包） | 官方文档（非开源许可） | ★ **只作签名与语义依据** | ★ **不抄其代码文本**；引用时标页名 |
| `Eduardof0nt/Solidworks-MCP-Server` | **MIT** | 读、抄、改、商用 | 保留版权声明 |
| `andrewbartels1/SolidworksMCP-python` | **MIT** | 读、抄、改、商用 | 保留版权声明 |
| `vespo92/SolidworksMCP-TS` | **MIT** | 读、抄、改、商用 | 保留版权声明 |
| `Slacker-LLC/solidworks-mcp` | **Apache-2.0** | 读、抄、改、商用 | ★ 保留 `NOTICE`（`Copyright 2026 JIALE LIU`）+ **声明改动了哪些文件** |
| **本项目自身既有模式** | 本仓 MIT | 沿用 `sw_part.py` / `sw_surface.py` 的写法与命名 | — |

⛔ **AGPL / GPL / 无许可 / 全版权保留**：★ **只读思想，不抄代码不抄文本**（本规格不引这类来源）。

## Project Structure

### Documentation (this feature)

```text
specs/202-user-coverage-gaps/
├── spec.md                      # 需求（本文件同目录）
├── plan.md                      # 本文件
├── tasks.md                     # 任务 + 逐条 → 验收:
└── recon/                       # ★ 侦察产物（按域一份，六列缺口表）
    ├── drawing.md               #   ★ 由便宜模型助手**并行**产出
    ├── feature.md
    ├── surface.md
    ├── sheetmetal.md
    ├── weldment.md
    └── misc.md
```

### Source Code (repository root)

```text
scripts/            # ★ 能力层：新增/扩展 sw_drawing_*.py · sw_sketch*.py · sw_assembly*.py …
mcp-server/         # ★ 工具层：tool_specs_batch*.py 追加 ToolSpec
tools/              # 探针（prove_*.py）+ sw_guard.py（弹窗护栏）+ round_chain.ps1
tests/              # 聚焦测试（契约 + 负例）
docs/               # capabilities.yaml 在上层；docs/ 放知识文档与生成物
output/             # ★ 证据 .json（gitignore）
```

**Structure Decision**: 沿用铁律 3 的 14 个顶层白名单目录，**不新增顶层目录**。
能力实现进 `scripts/`、工具声明进 `mcp-server/`、探针进 `tools/`、测试进 `tests/`。

## 执行策略（★ 含"哪部分并行、哪部分必须 Lead 亲自做"）

| 阶段 | 谁做 | 为什么 |
|---|---|---|
| 侦察（读官方页 → 结构化清单） | ★ **便宜模型助手并行**（`ninfer-sm89` / `qwen3.8-27b`，**后台非阻塞**） | ★ 高省、低风险（`docs/SUBAGENT-USAGE.md` §1.1）；★ 产物**写文件**、只回三行 |
| 判据设计 / 分诊结论 | **Lead** | ★ 判据是 Lead 职责，外派会"看着合理而漏掉要害" |
| 真机探针 | **Lead**（★ **绝不外派**） | ★ COM 单源，多进程抢同一连接**会死锁**（事实 24） |
| `capabilities.yaml` / `known-facts.md` / 台账 | **Lead** | ★ 要逐条对齐本仓格式与事实编号 |
| 门禁 + 负例测试 | **Lead** | ★ 事实 62：门禁"写了"不等于"有效" |

## Complexity Tracking

> 无宪法违规。★ 唯一需说明的是**本规格不新增顶层目录**（铁律 3 白名单）。

| 项 | 判断 |
|---|---|
| 新增 `specs/202-*` 目录 | ★ `specs/` 是**既有**白名单内目录（201 已在），非新增顶层 |
| 新增 `specs/202-*/recon/` | ★ 属于特性目录内部结构，宪法 §Flow-forward 允许 |
