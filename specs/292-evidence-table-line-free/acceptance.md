# Acceptance — 证据表去行号 + 收口 256/261 造成的 8 条红

**Feature**: `specs/292-evidence-table-line-free/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 8 条既有红全清（`8 failed, 41 passed` → `70 passed, 0 failed`）· 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **8 条红是**一个根因**：★ 四张**证据表**把站点写成 `(文件, 行号)` ⇒ ★★ 行号会漂**
⇒ ★ 实测 **~40 个切片里破了 4 次**（★ 256 · 261 · 新增站点 · 文档增行）⇒ ★ 那是**假红发生器**
⇒ ★★ **改成按名字/按文件**（★ 铁律 7），★ 并**顺带复核出 4 条结论**。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★★ 四张表**去行号** | `grep -c '\.py", [0-9]'` = **0** | ❌ 95 处 | ✅ **0** |
| FR-002 | ★★★ 248 站点比对改**文件多重集** | `test_every_host_expression_is_adjudicated` | ❌ FAILED | ✅ pass |
| FR-003 | ★★★ 249 写站点键**去行号** | `test_every_write_site_is_adjudicated` | ❌ FAILED | ✅ pass |
| FR-004 | ★★★ 棘轮下调**逐条带内容断言** | 4 条新判据 | ❌ 无 | ✅ pass |
| FR-005 | ★★★ 判据**仍能红** | 248 的 4 组合成负例 | — | ✅ 全红 |

## 二、★★★★ 先量：8 条红 → **一个根因**

| # | 文件 | 判据 | ★ 红消息 |
|---|---|---|---|
| ① | 248 | `test_every_host_expression_is_adjudicated` | 宿主表达式 **16 → 14** |
| ② | 248 | `test_criterion_catches_unadjudicated_host` | 变异体 `view` **不存在了** |
| ③ | 249 | `test_census_sizes_are_frozen` | 条目 **15 → 14** |
| ④ | 249 | `test_every_write_site_is_adjudicated` | **3 个写站点「未表态」** |
| ⑤ | 250 | `test_every_remaining_name_is_adjudicated` | 命中名 **13 → 12** |
| ⑥ | 245 | `test_every_hit_name_is_reviewed` | 命中名 **14 → 13** |
| ⑦ | 245 | `test_live_same_name_pages_are_adjudicated` | 同名页 **11 → 10** |
| ⑧ | 245 | `test_evidence_sites_match_recomputed_sites` | 证据 `sw_sheet_metal.py:1440` **不在重算站点里** |
| ⑨ | 256 | `test_four_view_name_sites_are_the_248_ones` | ★ **`ValueError`**（解包 3 元组）★ **本轮新发现** |

★★★ **逐条对因（★ 全部是后续切片**真的**改了代码，★ 不是读取器坏了）**：

| ★ 消失的名 / 宿主 | ★ 谁改的 | ★ 证据（★ 逐字） |
|---|---|---|
| `av`（`IView`·1 处）· `view`（`IView`·3 处） | ★★ **spec 256** → `IView::GetName2` | ★ `sw_review.py:637` 现为 `av.GetName2`（注释逐字「spec 256 换路由」） |
| `MaterialIdName`（`IModelDoc2`·1 处） | ★★ **spec 261** → `IPartDoc::GetMaterialPropertyName2` | ★ `sw_simulation.py:793` 逐字「**spec 261 换路由后的语义变化**」 |
| `KFactor` 宿主 `definition` → **`cba`** | ★★ **spec 261** → `ICustomBendAllowance` | ★ `sw_sheet_metal.py:275` 逐字「**spec 261 换路由**：官方后继 `GetCustomBendAllowance().KFactor`」 |
| 3 个写站点行号 `257→352`·`1288→1383`·`442→451` | ★ 无关改动（★ 含 291 的 docstring 增行） | ★ 宿主名**没变** ⇒ ★ **纯行号漂移** |

## 三、★★★★ 改动（★ **只动 `tests/`** · 5 个文件 · 95 处元组）

| # | 表 | ★ 键 → ★ 改法 |
|---|---|---|
| ① | 245 `_HOST_REVIEW` | 证据 `(文件, 行号, 宿主)` → **`(文件, 宿主)`** |
| ② | 248 `_NAME_HOST_REVIEW` | 站点 `(文件, 行号)` → **`(文件,)`** · ★ 比对改 `Counter` **多重集** |
| ③ | 249 `_WRITE_SITE_REVIEW` | 键 → **`(文件, 宿主, 成员)`** |
| ④ | 250 `_HOST_EXPR_REVIEW` | 站点 `(文件, 行号)` → **`(文件,)`** · ★ 比对改 `Counter` **多重集** |

★★ **保留多重集** ⇒ ★ 同名文件的**处数**仍被约束 ⇒ ★ **去行号没有放宽判据**（★ 由 248 新增的
「多塞一个文件」合成负例**证明**）✓

## 四、★★★★ 复核出的 4 条结论（★ 比修红更有价值）

| # | ★ 结论 | ★ 依据 |
|---|---|---|
| ① | ★★★ **`Name` 这条线已收口** | ★ 248 的真命中 **4 → 0** ⇒ ★ 245 的 `Name` 从 **`mixed` → `false-hit`** |
| ② | ★★ **`KFactor` 的真命中也没了** | ★ 261 换成 `ICustomBendAllowance`（★ 官方页 `grep -c -i obsolete` = **0**）⇒ ★ 真 → 假 |
| ③ | ★★ **`MaterialIdName` 已完全离开** | ★ 261 换掉 ⇒ ★ 既离开命中集（245/249）也离开「有非废弃同名页」集 |
| ④ | ★★★ **「站点逐字相等」本身是错的口径** | ★ 它把「**代码变了**」与「**读取器坏了**」判成**同形** ⇒ ★ 每次改代码都假红 |

## 五、★★★ 棘轮下调（★ 每处都写「为什么是正当减少」+ 补**内容断言** · 铁律 22）

| 文件 | ★ 棘轮 | ★ 值 | ★ 真因 |
|---|---|---|---|
| 248 | `HOSTS` / `SITES` / `REAL_SITES` | **16→14** · **51→47** · **4→0** | ★ 256（4 处真命中消失） |
| 249 | `ENTRIES` | **15→14** | ★ 261（`MaterialIdName` 不再「真树在调」） |
| 250 | `NAMES` / `SITES` / `REAL_SITES` / `FALSE_SITES` | **13→12** · **14→13** · **7→5** · **7→8** | ★ 261（`MaterialIdName` + `KFactor`） |
| 245 | 命中名 / 同名页 / 真 / 假 | **14→13** · **11→10** · **7→4** · **7→9** | ★ 256 + 261（同上） |

★ **内容断言 4 条**（★ 全部**按名字**定位 · 铁律 7）：
`test_name_route_is_closed_by_256` · `test_material_id_name_route_is_closed_by_261` ·
`test_material_id_name_left_the_census_by_261` · `test_name_and_material_lines_are_closed` ✓

## 六、★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_obsolete_host_review_family.py \
    tests/test_obsolete_name_host_adjudication.py \
    tests/test_multi_successor_both_needed_census.py -q
5 failed, 13 passed            # ★ 248 ×2 · 249 ×2 · 250 ×1
$ python -m pytest tests/test_obsolete_multi_successor_impact.py -q
3 failed                       # ★ 245 ×3
$ python -m pytest tests/test_iview_name_successor_machine.py -q
1 failed                       # ★ 256 ×1（★ 本轮新发现）
```

★ 改后（★ 11 个相关文件）：**`70 passed` · `0 failed`** ✓
★ **行号残留**：四张表里 `(".py", <数字>)` 命中 **0** ✓
★ ★★ **合成负例**（★ 证明新口径**能红**）：248 的 4 组 —— ① 未表态宿主 · ② 接口矛盾 ·
③ 漏表态 · ④ **多塞一个文件**（★ 新增，★ 专门守**新口径**）⇒ ★ **全红** ✓

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` | **47**（★ 未新增门禁文件 ⇒ 不变） |
| `skipped` | `["provenance"]`（★ 缺数据源 ⇒ `[SKIP]`，非失败 · 铁律 14） |
| `bundled_skill_files` | **471** |
| 日志 | `output/_gate292.log`（★ 实测 **2m19s**） |
| ★★ 日志 ②（★ **回写全部完成后重跑**） | `output/_gate292b.log` —— **`status pass` · `EXIT 0` · `missing []` · `gates 47` · `non-pass []`**（★ **2m18s**） |

★ **未改 `scripts/`** ⇒ ★ **不跑生成器链**。

## 八、未过门（如实登记）

1. ★★★ **250 的 7 处换路由 + 真机验**（★ **② 段唯一**一条）—— `FeatureLinearPattern5`（`sw_part.py` ×2）·
   `FeatureLocalCurveDrivenPattern`（`sw_pattern.py`）· `InsertFormToolFeature`（`sw_sheet_metal.py`）
   ⇒ ★ **三条官方后继都是 `IFeatureManager::CreateFeature`**（★ 都要**先造 `I*FeatureData`**，★ **不是 drop-in**）。
2. ★ `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data`。
3. ★ 223 的 B1–B5（★ **需业主定** `mcp-server/tool_specs_batch*.py` 权属）。
4. **未提交 / 未部署**；★ **未删任何文件**；★ **未动任何 hook**；★ **未派任何成员**。
