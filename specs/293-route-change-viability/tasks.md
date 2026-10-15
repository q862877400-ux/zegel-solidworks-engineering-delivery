# Tasks — 换路由可行性逐站点拍板

**Feature**: `specs/293-route-change-viability/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-293-01 先量①：环境** —— ★ `Get-Process SLDWORKS` ⇒ ★★ **未运行** ⇒ ★ **真机验做不了**。
- [x] **T-293-02 先量②：官方页** —— ★ 三页 `Obsolete` 逐字 + 官方指南四步流程 + mark 表（1/2/4/256）。
- [x] **T-293-03 先量③：官方示例** —— ★ `Create_Bidir_Linear_Pattern_Example_CSharp:50-67` 与
  `Create_and_Access_Curve-driven_Pattern_Feature_Example_VB:65-74` ⇒ ★★ **两条都先选 mark 4/1/2**。
- [x] **T-293-04 先量④：真树** —— ★ AST 找 5 处站点 + ★ **逐处查「是否已预选」**。
- [x] **T-293-05 拍板**（★ 授权 E）—— ★★ **2 处可换 · 3 处不可换**：
  | ★ 站点 | ★ 已预选 | ★ 可换 | ★ 依据 |
  |---|---|---|---|
  | `sw_part.py:1536` `linear_pattern` | ❌ | ★ **否** | ★ 换 = 改契约 |
  | `sw_part.py:2544` `linear_pattern_report` | ❌ | ★ **否** | ★ 同上 |
  | `sw_pattern.py:548` `insert_local_curve_driven_pattern_report` | ✅ | ★★ **是** | ★ `mark=1` + `mark=2` |
  | `sw_sheet_metal.py:1535` `insert_form_tool_report` | ✅ | ★★ **是** | ★ 选一个面 |
  | `sw_render_material.py:345` `delete_render_material` | — | ★ **否** | ★ 后继不可调（★ 证据 `3/4`） |
- [x] **T-293-06 订正记档** —— ★ `scripts/sw_part.py` **3 处**（★ 1456 · 1533 · 2547）：
  ★ 「后继空」+「官方没清状态标记」⇒ 官方依据（`CreateFeature` + **要求预选**）。
- [x] **T-293-07 写判据（先红）** —— `tests/test_route_change_viability.py`（**6 例**）。
- [x] **T-293-08 跑红基线** —— ★ 纯函数跑在 **`git HEAD` 的旧 `sw_part.py`** 上 ⇒ ★ **3 条问题**：
  ★ 「后继空」仍在 · ★ 没写 `CreateFeature` · ★ 没写「要求预选」。
- [x] **T-293-09 跑绿** —— ★ `6 passed` · ★ 「后继空」`grep -c` = **0**。
- [x] **T-293-10 相关判据** —— ★ 6 个文件 **41 passed**。
- [x] **T-293-11 生成器链** —— ★ 7 步全 `rc=0`（★ 改了 `scripts/`）。
- [x] **T-293-12 门禁** —— `release_check.py` @**3.14.7** ⇒ `output/_gate293.log`。
- [x] **T-293-13 回写四处** —— `GOAL.md` §七 · `AUTO_HANDOFF.md` · `ROADMAP.md` §一 ·
  `memory/2026-10-09.md` · `AUTO_RUN_*.md` · `.specify/feature.json`。

---

## 二、判据读数

| # | 判据 | ★ 改前（★ HEAD 旧实现） | ★ 改后 |
|---|---|---|---|
| ① | `test_official_pages_give_successor_and_preselect` | — | ✅ pass |
| ② | `test_exactly_five_real_sites_in_scripts` | — | ✅ pass |
| ③ | `test_switchable_sites_already_preselect` | — | ✅ pass |
| ④ | `test_unspportable_site_records_the_real_reason` | ❌ **3 条问题** | ✅ pass |
| ⑤ | `test_render_material_successor_is_unreachable_per_evidence` | — | ✅ pass |
| ⑥ | `test_pure_function_is_red_able` | — | ✅ pass（★ 五组负例全红） |
| — | **合计** | **3 条问题** | **`6 passed`** |

---

## 三、改动面

| # | 文件 | ★ 性质 |
|---|---|---|
| 1 | `scripts/sw_part.py` | ★ **仅 `#:` 注释块**（★ 3 处订正）· ★ 调用**一字未动** |
| 2 | `tests/test_route_change_viability.py` | ★ **新建判据**（6 例） |

---

## 四、不做

- ★ **不改任何路由**（★ SW 未运行 ⇒ 不能真机验 ⇒ 铁律 2）· ★ **不动** `sw_pattern.py` / `sw_sheet_metal.py`。
