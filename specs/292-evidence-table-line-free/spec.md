# Spec — **证据表去行号 + 收口 256/261 造成的 8 条红**

**Feature**: `specs/292-evidence-table-line-free/`
**日期**: 2026-10-10
**上游**: `specs/248-*`（`Name` 逐宿主表态）· `specs/249-*`（两个后继的宿主级先量）· `specs/250-*`（其余 13 条命中名）
**触发**: ★ 收 `GOAL.md` §五 第 2 步「**先收口上一轮的半成品**」—— ★★ 实测 **8 条既有红**（★ 判据红 **>** 一切）。

---

## 一、★★★★ 先量：8 条红，**一个根因**

★ 跑 248/249/250 与 245 的判据 ⇒ **8 failed, 41 passed**：

| # | 文件 | 判据 | ★ 红消息 |
|---|---|---|---|
| ① | 248 | `test_every_host_expression_is_adjudicated` | 宿主表达式从 **16 降到 14** |
| ② | 248 | `test_criterion_catches_unadjudicated_host` | 拿 `view` 当变异体 ⇒ **它不存在了** |
| ③ | 249 | `test_census_sizes_are_frozen` | 条目从 **15 降到 14** |
| ④ | 249 | `test_every_write_site_is_adjudicated` | **3 个写站点「未表态」** |
| ⑤ | 250 | `test_every_remaining_name_is_adjudicated` | 命中名从 **13 降到 12** |
| ⑥ | 245 | `test_every_hit_name_is_reviewed` | 命中名从 **14 降到 13** |
| ⑦ | 245 | `test_live_same_name_pages_are_adjudicated` | 有非废弃同名页的名从 **11 降到 10** |
| ⑧ | 245 | `test_evidence_sites_match_recomputed_sites` | 证据 `sw_sheet_metal.py:1440` 等**不在重算站点里** |

★★★ **根因 = 一个**：★ 四张**证据表**把站点写成 **`(文件, 行号)`** ⇒ ★★ **行号会漂**。

★ 逐条对因（★ **全部是后续切片**真的**改了代码**，★ 不是读取器坏了）：

| ★ 消失的名 / 宿主 | ★ 谁改的 | ★ 证据 |
|---|---|---|
| `av`（`IView` · 1 处）· `view`（`IView` · 3 处） | ★★ **spec 256** 换成 `IView::GetName2` | ★ `sw_review.py:637` 现为 `av.GetName2` · `sw_drawing_query.py` / `sw_drawing_view.py` 同 |
| `MaterialIdName`（`IModelDoc2` · 1 处） | ★★ **spec 261** 换成 `IPartDoc::GetMaterialPropertyName2` | ★ `sw_simulation.py:793` 逐字「**spec 261 换路由后的语义变化**」 |
| `KFactor` 的宿主 `definition` → **`cba`** | ★★ **spec 261** 换成 `ICustomBendAllowance` | ★ `sw_sheet_metal.py:275` 逐字「**spec 261 换路由**：官方后继 `GetCustomBendAllowance().KFactor`」 |
| 3 个写站点行号 `257→352` · `1288→1383` · `442→451` | ★ 无关改动（★ 含 291 的 docstring 增行） | ★ 宿主名**没变** ⇒ ★ **纯行号漂移** |

★★★ **⇒ 这是「假红发生器」**：★ 实测 **~40 个切片里破了 4 次**（★ 256 · 261 · 新增站点 · 文档增行）
⇒ ★★ 本仓铁律 7 **逐字**写着「**判据按「名字」定位，不按行号**」（★ 试点文件那条 `(916, "SaveAs")` 就是这么烂掉的）。

---

## 二、★★★★ 改动：**证据表去行号**（★ 结构性，不是把行号改一遍）

| # | 表 | ★ 键 | ★ 改法 |
|---|---|---|---|
| ① | 245 `_HOST_REVIEW` | 名 | 证据 `(文件, 行号, 宿主)` → **`(文件, 宿主)`** |
| ② | 248 `_NAME_HOST_REVIEW` | 宿主表达式 | 站点 `(文件, 行号)` → **`(文件,)`**，★ 比对改**多重集** |
| ③ | 249 `_WRITE_SITE_REVIEW` | — | 键 `(文件, 行号, 宿主, 成员)` → **`(文件, 宿主, 成员)`** |
| ④ | 250 `_HOST_EXPR_REVIEW` | 名 | 站点 `(文件, 行号)` → **`(文件,)`**，★ 比对改**多重集** |

★★ **保留多重集（不是集合）** ⇒ ★ 同名文件的**处数**仍被约束 ⇒ ★ **去行号没有放宽判据**。
★★ **248/250 只消费** 245 的 `_hit_sites()`（★ 它仍回 `(文件, 行号, 宿主)`）⇒ ★ **`_hit_sites()` 不动**。

---

## 三、★★★★ 复核出的**结论**（★ 比修红更有价值）

| # | ★ 结论 | ★ 依据 |
|---|---|---|
| ① | ★★★ **`Name` 这条线已收口** | ★ 248 的真命中 **4 → 0**（★ 256 把 4 处全换成 `GetName2`）⇒ ★ 245 的 `Name` 从 **`mixed` → `false-hit`** |
| ② | ★★ **`KFactor` 的真命中也没了** | ★ 261 把读点换成 `ICustomBendAllowance`（★ **非废弃**，★ 官方页 `grep -c -i obsolete` = **0**）⇒ ★ `KFactor` **真命中 → 假命中** |
| ③ | ★★ **`MaterialIdName` 已完全离开** | ★ 261 换掉 ⇒ ★ 既离开命中集（245/249）也离开「有非废弃同名页」集 |
| ④ | ★★★ **「站点逐字相等」本身是错的口径** | ★ 它把「**代码变了**」与「**读取器坏了**」**判成同形** ⇒ ★ 每次改代码都假红 |

---

## 四、需求

### FR-001 ★★★ 四张证据表**去行号**
- **验收场景**：`grep -c '\.py", [0-9]'` 在四个文件里全为 **0**。

### FR-002 ★★★ 248 的站点比对改**文件多重集**
- **验收场景**：`test_every_host_expression_is_adjudicated` 通过；★ **且**合成负例「多塞一个文件」被判出。

### FR-003 ★★★ 249 的写站点键**去行号**
- **验收场景**：`test_every_write_site_is_adjudicated` 通过（★ 3 个「未表态」是纯行号漂移）。

### FR-004 ★★★ 棘轮下调**逐条带内容断言**
- **验收场景**：`test_name_route_is_closed_by_256` · `test_material_id_name_route_is_closed_by_261` ·
  `test_material_id_name_left_the_census_by_261` · `test_name_and_material_lines_are_closed` 通过。

### FR-005 ★★★ 判据**仍能红**
- **验收场景**：248 的 4 组合成负例全红；★ 245/249/250 的既有合成负例仍绿。

---

## 五、非目标

- ★ **不改** `scripts/`（★ 本轮**只动判据与证据表**）⇒ ★ **不跑生成器链**。
- ★ **不改** `_hit_sites()`（★ 它是**原始扫描**，★ 回三元组是对的）。
- ★ **不换任何路由** —— ★ 256/261 已换完；★ 本轮只**同步证据**。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**先红后绿** | 改前 **8 failed, 41 passed**；改后 **0 failed** |
| SC-2 | 相关族**全绿** | 11 个相关文件 **70 passed** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★★ 行号**不再出现** | 四个文件里 `(".py", <数字>)` 命中 **0** |

## 七、未过门（本轮不做，如实登记）

- ★★ **250 的 7 处换路由 + 真机验**（★ ② 段**唯一**一条）· ★ `create_draft` 的 `pre_call` ·
  ★ `DeleteRenderMaterial` · ★ 4 处 `needs-feature-data` · ★ 223 的 B1–B5（需业主定权属）· 未提交未部署。
