# Tasks — 证据表去行号 + 收口 256/261 造成的 8 条红

**Feature**: `specs/292-evidence-table-line-free/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-292-01 先量**：跑 248/249/250/245 ⇒ ★ **8 failed, 41 passed**；★ 逐条取红消息。
- [x] **T-292-02 定性**：AST 探针 + 源码核 ⇒ ★★ **证明是代码真的变了**（★ 不是读取器坏了）：
  - ★ `av`/`view` ⇒ **256**（`sw_review.py:637` 现为 `av.GetName2`）
  - ★ `MaterialIdName` ⇒ **261**（`sw_simulation.py:793` 逐字「spec 261 换路由后的语义变化」）
  - ★ `KFactor` 宿主 `definition`→`cba` ⇒ **261**（`sw_sheet_metal.py:275` 逐字「spec 261 换路由」）
  - ★ 249 的 3 个「未表态」⇒ **纯行号漂移**（★ 宿主名没变：`257→352` · `1288→1383` · `442→451`）
- [x] **T-292-03 机械去行号**（★ 脚本 `output/_probe292_rewrite.py` / `_fix1.py` / `_fix2.py`）：
  ★ 245 **19 处** · 248 **52 处** · 249 **9 处** · 250 **15 处** = **95 处**。
- [x] **T-292-04 改比对**：248/250 的站点比对 → `Counter` **多重集**；249 的键 → `(文件, 宿主, 成员)`。
- [x] **T-292-05 删死条目 + 墓碑**：245/250 的 `MaterialIdName` · 248 的 `av`/`view`。
- [x] **T-292-06 改结论**：245/250 的 `Name` → `false-hit` · `KFactor` → `false-hit`。
- [x] **T-292-07 下调棘轮**（★ 逐条写「为什么是正当减少」）：
  | 文件 | ★ 棘轮 | ★ 值 |
  |---|---|---|
  | 248 | `BASELINE_HOSTS` / `_SITES` / `_REAL_SITES` | **16→14** · **51→47** · **4→0** |
  | 249 | `BASELINE_ENTRIES` | **15→14** |
  | 250 | `BASELINE_NAMES` / `_SITES` / `_REAL_SITES` / `_FALSE_SITES` | **13→12** · **14→13** · **7→5** · **7→8** |
  | 245 | 命中名 / 同名页 / 真 / 假 | **14→13** · **11→10** · **7→4** · **7→9** |
- [x] **T-292-08 补内容断言**（★ 铁律 22 · ★ 按**名字**定位）：
  `test_name_route_is_closed_by_256`（248）· `test_material_id_name_route_is_closed_by_261`（250）·
  `test_material_id_name_left_the_census_by_261`（249）· `test_name_and_material_lines_are_closed`（245）。
- [x] **T-292-09 修合成负例**：248 的变异体从 `view`/`av` 改成**合成**（`body` + 接口改 `IView`）；
  ★ **新增**「多塞一个文件」负例 ⇒ ★ 证明**新口径也能红**。
- [x] **T-292-10 修 256 的判据**：`test_four_view_name_sites_are_the_248_ones` 从「**换前**」改「**换后**」。
- [x] **T-292-11 跑绿**：★ 11 个相关文件 **70 passed** · **0 failed**。
- [x] **T-292-12 门禁**：`release_check.py` @**3.14.7** ⇒ `output/_gate292.log`。
- [x] **T-292-13 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` · `ROADMAP.md` §一 · `memory/2026-10-09.md` · `AUTO_RUN_*.md` · `.specify/feature.json`。

---

## 二、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| 245 | `test_obsolete_multi_successor_impact.py` | ❌ **3 failed** | ✅ pass |
| 248 | `test_obsolete_name_host_adjudication.py` | ❌ **2 failed** | ✅ pass |
| 249 | `test_multi_successor_both_needed_census.py` | ❌ **2 failed** | ✅ pass |
| 250 | `test_obsolete_host_review_family.py` | ❌ **1 failed** | ✅ pass |
| 256 | `test_iview_name_successor_machine.py` | ❌ **1 failed** | ✅ pass |
| — | **合计（11 个相关文件）** | **8 failed, 41 passed** | **70 passed · 0 failed** |

★ **行号残留**：四个证据表里 `(".py", <数字>)` 命中 **0** ✓

---

## 三、不做

- ★ **不动 `scripts/`** ⇒ ★ **不跑生成器链**；★ **不换路由**；★ **不动 `_hit_sites()`**。
