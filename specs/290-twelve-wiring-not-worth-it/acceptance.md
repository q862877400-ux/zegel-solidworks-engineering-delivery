# Acceptance — 核销「12 条接线」：不值

**Feature**: `specs/290-twelve-wiring-not-worth-it/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **12 个封装的生产调用点 = 0** ⇒ ★★ **接线对**运行期**毫无影响**；
★ 而**生产路径已经是对的** ⇒ ★★ **不是**修一个真 bug ⇒ ★★★ **与 266 同一判断：★ 不值** ⇒ ★ **核销**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 12 条封装零生产调用点 | `test_all_twelve_wrappers_have_no_production_callers` | ✅ 全 0 |
| FR-002 | ★★★ 生产路径已经是对的 | `test_the_production_path_is_already_correct` | ✅ 3 处带 `out_i4()` |
| FR-003 | ★★ 乙方案有先例 | `test_the_b_route_has_a_precedent` | ✅ `sw_simulation_loads.py:251` |
| FR-004 | ★★★ 核销理由（与 266 同一判断） | `test_the_verdict_matches_266` | ✅ |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★★ 现场量：★ **12 个封装的生产调用点 = 0**

★ 扫 `scripts/` + `mcp-server/` + `tools/`（★ 排除**定义**与**注释**）：

| 模块 | ★ 封装 | ★ 生产调用点 |
|---|---|---|
| `sw_simulation_results.py` | `create_plot` · `create_deformed_body` · `get_displacement_at_points` · `get_buckling_load_factors` · `get_mesh_node_location` · `get_mesh_element_location` | ★ **全 0** |
| `sw_simulation_study.py` | `create_study` · `create_study_v2` · `create_study_v3` · `duplicate_study` · `convert_study` | ★ **全 0** |
| `sw_pdm.py` | `get_bom_start_number` | ★ **0** |

⇒ ★★★ **接线对**运行期**毫无影响**（★ 没有任何东西会调它们）。

## 三、★★★ 而**生产路径已经是对的**

```
scripts/sw_simulation.py:348  manager, "CreateNewStudy3", str(name), int(study_type), int(mesh_type), out_i4()
scripts/sw_simulation.py:355  manager, "CreateNewStudy2", str(name), int(study_type), out_i4()
scripts/sw_simulation.py:364  manager, "CreateNewStudy",  str(name), int(study_type), int(mesh_type), out_i4()
```

⇒ ★★ **生产路径是对的** ✓ ⇒ ★ 那 12 条的「接线」**只是**让**未被调用**的封装也对
—— ★★ **不是**修一个真 bug（★ **272/273/274 都没量到这一点** —— ★ 它们都在「怎么改」上打转）。

## 四、★★ 乙方案**有先例**

★ `scripts/sw_simulation_loads.py:251` 逐字：
**「★★ 修法：★ 由本函数统一补 `out_i4()`（★ 一处修改 ⇒ 整批 `Add*` 全受益）」**
⇒ ★★ 那正是乙方案的**思想**，★ 且**已经在别处落地过** ✓

## 五、★★★ 核销（★ 与 266 同一判断）

★ 理由两条：
1. ★★ **12 条封装零生产调用点** ⇒ ★ **接线对运行期无影响**；
2. ★★ 对**静态门禁**只影响 **`arity` 桶** ⇒ ★ 而它**只计数、不判罪**
   ⇒ ★★ 与 **266**（★「改口径**不值**」）**同一判断** ✓

⇒ ★★★ **按 `GOAL.md` §二「做不了的标注…并删号」的精神** —— ★ 这条**不是做不了**，
★ 而是**量清之后确认「不值」** ⇒ ★ **删号**（★ 证据留档）。

## 六、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 封装数不对 | 报错 | ✅ `['★ 应数 12 个封装，实测 5']` |
| 某个有生产调用点 | 报错 | ✅ `["★ 这些封装**有**生产调用点：['create_study']"]` |
| 生产路径不是 3 处 | 报错 | ✅ `['★ 生产路径应有 3 处，实测 1']` |
| 结论不是「核销」 | 报错 | ✅ `['★ 结论应是「核销」', '★ 理由里要写明…']` |
| 理由缺「只计数」 | 报错 | ✅ `['★ 理由里要写明「`arity` 桶只计数、不判罪」']` |

## 七、★★★ 判据**将来会红**（★ 那是**有意**的）

★ 判据钉的是「**零生产调用点**」⇒ ★★ **将来有人给这 12 条加了生产调用点 ⇒ 判据当场红**
⇒ ★★ 那正是「**该重新评估**」的信号 ✓（★ 不是误红）

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate290.log` |

★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

## 九、未过门（如实登记）

1. ★★★ **`AddMate5` 的分流语义复核**（★ ② 段第 1 条**剩下的那一条子项** · ★ 只读）⇒ ★ 下一轮。
2. ★★ **250 的 7 处换路由 + 真机验**（★ ② 段第 2 条）。
3. ★ `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
