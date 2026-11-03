# Acceptance — 修回归夹具的草图几何单位

**Feature**: `specs/278-base-flange-regression-units/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **维护回归跑绿了** —— ★ 只改夹具的 **3 行**草图几何（`mm(30)` ⇒ **裸毫米** `30`）；
★★ **顺带证伪事实 209**（★ 长度是**米**，★ 不是「文档单位（毫米）」）⇒ ★ 已订正 `BaseFlangeSpec` 的 docstring。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 维护回归跑绿 | `test_the_maintained_regression_now_passes` | ✅ `status: pass` |
| FR-002 | ★★★ 事实 209 被证伪 | `test_fact_209_unit_claim_is_falsified` | ✅ `thickness=2.0` 全失败 |
| FR-003 | ★★★ 四处回源码核 | `test_source_checks_prove_the_fixture_and_docstring` | ✅ 4/4 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★ 修法与真机结果

★ **只改 3 行**（`tests/solidworks_sheet_metal_regression.py` 的草图几何）：

```python
sketch_line(model, -mm(30), mm(25), -mm(30), 0.0)   ⇒   sketch_line(model, -30, 25, -30, 0.0)
sketch_line(model, -mm(30), 0.0, mm(30), 0.0)       ⇒   sketch_line(model, -30, 0.0, 30, 0.0)
sketch_line(model, mm(30), 0.0, mm(30), mm(25))     ⇒   sketch_line(model, 30, 0.0, 30, 25)
```

★★★ **真机跑维护回归**（★ 走 `sw_guard`）⇒ **`"status": "pass"`**：

| 产物 / 读数 | 值 |
|---|---|
| `u_channel_sheet_metal.SLDPRT` | **95 871 B** |
| `u_channel_flat_pattern.dxf` | **20 660 B** |
| `thickness_m` | **0.002**（= **2 mm** 的真板） |
| `has_base_flange` / `all_solid_bodies_are_sheet_metal` | **true** / **true** |

★ 读数原文 `output/_probe278_regression.txt`。

## 三、★★★ 中途的**自我纠错**（★ 值得留档）

★ 第一次**连 spec 的长度也改成了「文档单位」** ⇒ 回归**反而更失败** ⇒ ★ 于是**逐臂量**（★ 几何一律 30/25 **毫米**）：

| 臂 | 厚度 | 半径 | 深度 | 结果 |
|---|---|---|---|---|
| ★ 对照 | **0.002** | **0.0025** | **0.1** | ★ **建成**（★ 读回 = **2 mm**） |
| A | 2.0 | 1.0 | 100.0 | ✗ |
| B | 2.0 | 1.0 | 0.1 | ✗ |
| D | 2.0 | 0.5 | 0.1 | ✗ |
| E | 2.0 | 1.0 | 0.1（★ 不用默认弯补） | ✗ |

★ 四条失败的报文**完全相同**：★ **「无法添加此圆角，因为指定的半径值将会删除其中一个实体」**。

⇒ ★★★ **长度就是**米**** —— ★ 若按毫米，**2.0 mm 的板配 1.0 mm 半径**应当可行，★ 而它**全失败**；
★ 反之 `0.002`（**2 mm**）**建成**，★ 且读回键名**本来就写着 `thickness_m`** ⇒ ★ `0.002 m = 2 mm` 自洽 ✓。
★ 读数原文 `output/_probe278_values.txt`。

## 四、★★★ 证伪**事实 209**

| 项 | 内容 |
|---|---|
| **被推翻的旧结论** | ★「`IBaseFlangeFeatureData` 的长度按**文档长度单位**解释（本机 = 毫米）」 |
| ★ **它错在哪** | ★ 它用的草图是 **40 / 60 量级**（★ 按米就是 40 m × 60 m 的巨件）⇒ ★ 那个尺度下 `0.002` 与 `2.0` **都能建**（★ 只是棱长读数跟着变）⇒ ★ 它把「棱长跟着变」**误读**成「单位是毫米」 |
| ★ **订正** | ★ **长度按**米**传**；★ 本仓既有调用点传 `0.002` **本来就是对的** |
| ★ **落地** | ★ 已写回 `scripts/sw_sheet_metal.py` 的 `BaseFlangeSpec` docstring（★ 旧结论**留档** + 标明**被推翻**） |
| ★ **另一条真机约束** | ★ **`bend_radius` 必须 < `thickness`** |

## 五、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 回归没绿 | 报错 | ✅ `["回归不是 pass：'failed'"]` |
| 产物缺 | 报错 | ✅ `['产物不齐或过小：{}']` |
| 两臂都成功 | 报错 | ✅ `["应**恰好**「厚 0.002」那一臂成功，实测 […, '厚 2.0 · 半径 1.0 · 深 0.1']"]` |
| 旧结论为空 | 报错 | ✅ `['旧结论 / 订正结论 之一为空 ⇒ 检查量为 0']` |
| 回源码核失败 | 报错 | ✅ `['★ 回源码核失败：几何是裸毫米']` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` / `gates_passed` | **47** / **44** |
| 日志 | `output/_gate278.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 八、未过门（如实登记）

1. ★★ **同族另 4 个**（`create_one_bend` / `create_draft` / `create_edge_flange` / `create_gusset`）
   **未用毫米几何复测** ⇒ ★ 下一轮做（★ 工具链已备齐：★ 报错入口 **276** · ★ 单变量法 **277** · ★ 毫米几何 **278**）。
2. ★ 事实 209 的**姊妹条**（★「`InsertMoveCopyBody2` 的长度也是文档单位」）**未复核** ⇒ ★ 只登记。
3. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
