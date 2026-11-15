# Implementation Plan: 造环节 —— 从需求到可交付模型

**Branch**: `354-make-side-generation` | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/354-make-side-generation/spec.md`

## Summary

把「造」这一环从「参数能推出来」推进到「真机建得出、量得准」。

现状：需求→参数（9 测试）、参数→计划（8 测试）、零件→分流（7 测试）三段的**离线部分已跑通**；
缺的是 `execute()` 接真机与 L3/L4 验证。本特性的核心交付是**让齿轮族从 `stitched` 变成 `verified`**，
并用轴族证明这套骨架可复制。

## Technical Context

**Language/Version**: Python 3.14.7（本机实测版本）

**Primary Dependencies**:
- `pywin32`（COM 桥，项目已有）
- `cq_gears` / `py_gearworks`（Apache-2.0，几何数学移植源）
- `pytest 9.1.1`（已装）
- 项目自有：`sw_part` / `sw_sketch_*` / `sw_connect` / `sw_measure`

**Storage**: 文件（`.json` 计划、`.json` 验证结果、`.png` 三视图）；无数据库

**Testing**: `pytest`（离线契约测试 24 条已有）+ 真机 L3/L4

**Target Platform**: Windows + SolidWorks 2026（本机）

**Project Type**: 方法层库（Python 模块）+ 真机执行器

**Performance Goals**:
- 参数推导 <100 ms（纯数学）
- 计划生成 <500 ms（齿轮 700 点）
- 单件真机建模 <60 s（含启动与回读）

**Constraints**:
- **COM 单进程**（项目已知事实 24），不并发建模
- **中文路径**会让 SolidWorks 丢路径 ⇒ 中间文件落纯 ASCII 临时目录
- **单位两套并存**：`sketch_line`/`sketch_circle` 收毫米、`extrude_boss` 收米
- **禁止折线模拟曲线**：不得把曲线采样成点列再逐段连直线（AGENTS.md 十四之五，业主 2026-11-07 令）；`outline_points_m` 这类离散点列字段不得出现在活跃功能里
- 方法层不得改动 `scripts/` 与 `capabilities.yaml`（搬入前）

**Scale/Scope**:
- 首件：齿轮族（1 个族，6 种几何原语中的 1/4/5）
- 验证族：轴（原语 2）
- 不做：装配级、强度校核、变位、买件

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪法条款 | 判据 | 本 plan 怎么满足 |
|---|---|---|
| **I. 缝合优先** | spec 每条需求有来源 | 几何来自 `cq_gears`(Apache-2.0) 数学与项目自有 `scripts/gear_geometry.py`（真曲线）；参数表来自 GB/T 1356/1357；不自推齿形公式。**禁止**用归档 `sw_gear.py` 的折线实现（业主 2026-11-07 令） |
| **II. 签名三源互证** | plan 列出官方源与裁决顺序 | 本特性只调用**项目已有**的 `sw_part` / `sw_sketch_*` / `sw_measure`，其签名已由项目审计过；新增 COM 调用 = **0 处** |
| **III. 查不到就写查不到** | 每个「应该有」附核查命令 | `execute()` 所需的 `extrude_boss` / `ForceRebuild3` 均已存在，见 §Phase 0 的核查命令 |
| **IV. 许可红线** | 每个来源行有 license | 见下表 |
| **V. 验收判据必须能跑** | tasks 每条带 `→ 验收:` | Phase 2 产出 |

### 来源与许可表（宪法 §IV 判据）

| 来源 | 许可 | 可做什么 | 义务 |
|---|---|---|---|
| `archive/inherited-methods/scripts/sw_gear.py` | 本项目自有 | **禁止复用**（折线模拟渐开线，业主 2026-11-07 令删除；见 AGENTS.md 十四之五），仅作历史追溯 | — |
| `scripts/gear_geometry.py` | 本项目自有 | 真曲线齿轮（方程式驱动渐开线 + 摆线齿根），**整圈闭合/单齿阵列均未通过真机验收** | 无 |
| `cq_gears`（meadiode） | **Apache-2.0** | 抄数学、改、商用 | 保留 NOTICE、声明改动文件 |
| `py_gearworks`（GarryBGoode） | **Apache-2.0** | 同上 | 同上 |
| `mechanism`（PiPy） | **MIT** | 抄、改、商用 | 保留版权声明 |
| `pylinkage` | **MIT** | 同上 | 同上 |
| `springcalc` | **MIT** | 同上 | 同上 |
| 嘉立创 FA 手册（GB 表） | **未明示** | 仅在线查阅 + 按标准号回查原文 | **不得把表打包进库**（协议第三条） |
| 本机 5,725 份国标 PDF | 国标版权 | 内部设计使用 | 不外发、不再分发 |

**Gate 结果：通过。** 无违宪项。

## Project Structure

### Documentation (this feature)

```text
specs/354-make-side-generation/
├── plan.md              # 本文件
├── research.md          # Phase 0 输出
├── data-model.md        # Phase 1 输出
├── quickstart.md        # Phase 1 输出
├── contracts/           # Phase 1 输出
└── tasks.md             # Phase 2 输出（/speckit.tasks）
```

### Source Code (repository root)

**落点决策：先留在 `research/text-to-cad-and-parametric-plugins/proto/`，验证通过后整体搬入 `scripts/`。**

理由：`scripts/` 一改动会触发 `release_check` + 五统一门禁 + `capabilities.yaml` 校验；
在一个模块还没真机验证前搬入，等于给门禁制造噪音。这也是 `06-第一步` 文档里已经写过的判断。

```text
research/text-to-cad-and-parametric-plugins/proto/     # 方法层（本特性主战场）
├── gear_method.py          # 需求 → 参数 + 溯源表（已有，9 测试）
├── build_plan.py           # 参数 → FeaturePlan（已有，8 测试）
├── dispatcher.py           # 零件 → 买/造/放（已有，7 测试）
├── execute.py              # ★ 新增：FeaturePlan → 真机建模（唯一碰 COM）
├── verify.py               # ★ 新增：L3 体积/包围盒 + L4 三视图
├── shaft_method.py         # ★ 新增：轴族（证明骨架可复制）
├── test_execute.py         # ★ 新增
├── test_verify.py          # ★ 新增
└── test_shaft_method.py    # ★ 新增
```

**搬入 `scripts/` 的时机**：齿轮族 `verified` 之后，一次搬完（含 `tests/` 与 `capabilities.yaml` 更新）。

**Structure Decision**: 单项目结构（方法层 Python 模块 + 测试），无前后端分离、无移动端。
理由：这是 SolidWorks 自动化项目的方法层扩展，不是独立应用。

## Phase 0: Outline & Research

### 需要解决的技术未知

| # | 未知 | 怎么解 |
|---|---|---|
| U1 | `extrude_boss` 到底收米还是毫米 | 读 `sw_part.py` 源码 + 归档 `sw_gear.py` 的 1000× 事故复盘注释 |
| U2 | 建模后怎么回读体积与包围盒 | 查 `sw_measure.py` / `sw_mass_property.py` 有无现成函数 |
| U3 | 三视图怎么导 PNG | 查 `sw_export.py` 或 `sw_drawing_view.py` |
| U4 | 失败时怎么留证 | 查 `sw_guard.py` / `tools/guard_run.py` 的既有做法 |
| U5 | 齿轮轮廓 700 点会不会太慢 | 本会话已实测：弦高 0.4 µm@700 点，5 µm 只需 200 点 |

### 核查命令（宪法 §III 要求）

```powershell
# U1: extrude_boss 的单位
Select-String -Path scripts\sw_part.py -Pattern "def extrude_boss" -Context 0,15

# U2: 体积与包围盒回读
Select-String -Path scripts\sw_measure.py,scripts\sw_mass_property.py -Pattern "^def "

# U3: 三视图导出
Select-String -Path scripts\sw_export.py,scripts\sw_drawing_view.py -Pattern "^def "

# U4: 失败留证
Get-ChildItem tools -Filter "*guard*"
```

**Phase 0 输出**：`research.md`（含上述五项的实测结果与决策）

## Phase 1: Design & Contracts

### 实体（→ `data-model.md`）

| 实体 | 字段 | 验证规则 |
|---|---|---|
| `GearRequest` | ratio, center_mm, bm_ratio, pin_z1, pin_module, z_min_policy | ratio>0, center_mm>0 |
| `Row` | key, meaning, value, source, evidence, how_to_change | source ∈ 六类 |
| `FeaturePlan` | name, units, sketch_entities[], features[], expected{volume,bbox}, provenance | units=="mm"；坐标 1~1000 |
| `Verification` | measured_volume, measured_bbox, deviation_pct, screenshots[] | deviation_pct <1.0 |

### 契约（→ `contracts/`）

| 契约 | 内容 |
|---|---|
| `execute.contract.md` | `execute(plan) -> (model, evidence)`；失败抛异常不返回 None；单位转换单点 |
| `verify.contract.md` | `verify(model, plan) -> Verification`；偏差 >1% 判 fail |

### 快速验证（→ `quickstart.md`）

```powershell
# 离线（无 SolidWorks）
cd research\text-to-cad-and-parametric-plugins\proto
python -m pytest -q          # 期望 24 passed

# 真机（需 SolidWorks）
python execute.py --gear i=3 a=40    # 期望输出体积与包围盒
```

**Phase 1 输出**：`data-model.md`、`contracts/`、`quickstart.md`

## Constitution Check（Phase 1 后复查）

| 条款 | 复查结果 |
|---|---|
| I. 缝合优先 | ✅ 新增的 `execute.py` / `verify.py` 只调项目已有函数，无新数学 |
| II. 签名三源互证 | ✅ 新增 COM 调用 0 处 |
| III. 查不到就写查不到 | ✅ Phase 0 五项全部有核查命令 |
| IV. 许可红线 | ✅ 来源表已列 license |
| V. 验收判据能跑 | ⏳ Phase 2 落实 |

**Gate 结果：通过。**

## Complexity Tracking

> 无违宪项，本节不填。

## 交付判据（本特性「做完」的定义）

| # | 判据 | 现在 |
|---|---|---|
| 1 | 离线测试 ≥30 条全绿（现 24） | ⏳ |
| 2 | 齿轮族真机建成，体积偏差 <1% | ❌ |
| 3 | 三视图无悬空草图 | ❌ |
| 4 | 轴族复用同一骨架 | ❌ |
| 5 | `capabilities.yaml` 里齿轮族 `stitched` → `verified` | ❌ |

**前三条全绿 = 造环节成立。第五条是它的账。**
