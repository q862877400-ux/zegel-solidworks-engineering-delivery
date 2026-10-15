# Spec — **核销「12 条接线」**：★ 12 条封装**零生产调用点** ⇒ ★ 按 266 的同一判断：**不值**

**Feature**: `specs/290-twelve-wiring-not-worth-it/`
**日期**: 2026-10-10
**上游**: `specs/289-arity-change-route-decision/`（★ 拍板乙 · ★ 改动面 2 处 × 3 模块）
**本轮只做一件事**：★ 287/288/289 把「**怎么改**」量清了 ⇒ ★ 本轮**量「值不值得改」**：★ **数生产调用点**。

---

## 一、★★★★ 现场量：★ **12 条封装的生产调用点 = 0**

★ 扫 `scripts/` + `mcp-server/` + `tools/`（★ 排除**定义**与**注释**）：

| 模块 | ★ 封装 | ★ 生产调用点 |
|---|---|---|
| `sw_simulation_results.py` | `create_plot` · `create_deformed_body` · `get_displacement_at_points` · `get_buckling_load_factors` · `get_mesh_node_location` · `get_mesh_element_location` | ★ **全 0** |
| `sw_simulation_study.py` | `create_study` · `create_study_v2` · `create_study_v3` · `duplicate_study` · `convert_study` | ★ **全 0** |
| `sw_pdm.py` | `get_bom_start_number` | ★ **0** |

★★★ **⇒ 「接 by-ref 出参」对**运行期**毫无影响**（★ **没有任何东西会调它们**）。

---

## 二、★★★ 而**生产路径已经是对的**

★ `scripts/sw_simulation.py` **直接**调 `ICWStudyManager` 时**已经**传 `out_i4()`：

```
:348  manager, "CreateNewStudy3", str(name), int(study_type), int(mesh_type), out_i4()
:355  manager, "CreateNewStudy2", str(name), int(study_type), out_i4()
:364  manager, "CreateNewStudy",  str(name), int(study_type), int(mesh_type), out_i4()
```

★★★ **⇒ 生产路径是对的** ✓ ⇒ ★ 那 12 条的「接线」**只是**让**未被调用**的封装也对
—— ★★ **不是**在修一个真 bug**（★ 这一点 272/273/274 都没量到）。

---

## 三、★★ 顺带：★ 乙方案**有先例**

★ `scripts/sw_simulation_loads.py:251` 逐字：
**「★★ 修法：★ 由本函数统一补 `out_i4()`（★ 一处修改 ⇒ 整批 `Add*` 全受益）」**
⇒ ★★ **那正是乙方案的**思想**，★ 且**已经在别处落地过** ✓

---

## 四、★★★ **核销**（★ 与 **266** 同一判断）

★ 理由两条：
1. ★★ **12 条封装零生产调用点** ⇒ ★ **接线对运行期无影响**；
2. ★★ 对**静态门禁**只影响 **`arity` 桶** ⇒ ★ 而它**只计数、不判罪**
   ⇒ ★★ 与 **266**（★「改口径**不值**」）**同一判断** ✓

⇒ ★★★ **按 `GOAL.md` §二「做不了的标注…并删号」的精神** —— ★ 这条**不是做不了**，
★ 而是**量清之后确认「不值」** ⇒ ★ **删号**（★ 并把证据留档）。

---

## 五、需求

### FR-001 ★★★ 12 条封装**零生产调用点**
- **验收场景**：`test_all_twelve_wrappers_have_no_production_callers` 通过。

### FR-002 ★★★ 生产路径**已经是对的**
- **验收场景**：`test_the_production_path_is_already_correct` 通过。

### FR-003 ★★ 乙方案**有先例**
- **验收场景**：`test_the_b_route_has_a_precedent` 通过。

### FR-004 ★★★ **核销理由**（★ 与 266 同一判断）
- **验收场景**：`test_the_verdict_matches_266` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 六、非目标

- ★★★ **不改任何实现** —— ★ 本轮的结论是「**不值**」⇒ ★ 改它**没有收益**。
- ★ **不改** `scripts/` ⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 封装数不对 / 某个有生产调用点 / 生产路径不是 3 处 / 结论不是「核销」/ 理由缺「只计数」 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_twelve_wiring_is_not_worth_it.py` **5/5 通过** |
| SC-3 | ★★ 判据**不钉现状** | ★ 若**将来**有人给这 12 条加了生产调用点 ⇒ ★ **判据当场红**（★ 那正是**该重新评估**的信号）✓ |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 八、未过门（本轮不做，如实登记）

- ★★★ **`AddMate5` 的分流语义复核**（★ ② 段第 1 条**剩下的那一条子项** · ★ 只读）⇒ ★ 下一轮。
- ★★ **250 的 7 处换路由 + 真机验**（★ ② 段第 2 条）· ★ `create_draft` 的 `pre_call` · ★ `DeleteRenderMaterial` · ★ 4 处 `needs-feature-data` · 未提交未部署。
