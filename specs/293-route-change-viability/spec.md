# Spec — **换路由可行性逐站点拍板**：★ 5 处真命中里 **2 处可换、3 处不可换**

**Feature**: `specs/293-route-change-viability/`
**日期**: 2026-10-10
**上游**: `specs/292-evidence-table-line-free/`（★ 292 用 AST 量出 `scripts/` 里**只剩 5 处**真命中）
**本轮只做一件事**：★★ 收 ② 段**唯一**一条「250 的换路由 + 真机验」的**先量那一半** —— ★ **逐站点判「能不能换」**。

---

## 一、★★★★ 先量：官方后继**全部要求预选**

| 源 | ★ 逐字 |
|---|---|
| `FeatureLinearPattern5.md:12` | 「Obsolete. See `IFeatureManager::CreateFeature` and the Remarks in `ILinearPatternFeatureData` and `ILocalLinearPatternFeatureData`.」 |
| `FeatureLocalCurveDrivenPattern.md:12` | 「Obsolete. See `IFeatureManager::CreateFeature` and the Remarks in `ILocalCurvePatternFeatureData`.」 |
| `InsertFormToolFeature.md:12` | 「Obsolete. Superseded by `IFeatureManager::CreateDefinition` and `IFeatureManager::CreateFeature`.」 |
| **`Pattern Features and their Feature Data Objects.md:20`** | ★★★ 「**Before calling `IFeatureManager::CreateDefinition`, you must pre-select the entities needed to create the linear pattern feature.**」 |
| `ILinearPatternFeatureData/_overview.md:20` | ★★★ **同句** + mark 表：**1** = Direction 1 · **2** = Direction 2 · **4** = faces/features · **256** = solid bodies |
| `Create_Bidir_Linear_Pattern_Example_CSharp.md:50-67` | ★★ **官方迁移示例**：`SelectByID2(mark 4)` ⇒ `(mark 1)` ⇒ `(mark 2)` ⇒ `CreateDefinition(swFmLPattern)` ⇒ `CreateFeature` |
| `Create_and_Access_Curve-driven_Pattern_Feature_Example_VB.md:65-74` | ★★ 同形：`mark 4` ⇒ `mark 1` ⇒ `CreateDefinition(swFmCurvePattern)` ⇒ `CreateFeature` |

⇒ ★★★ **两条独立官方示例**都证明：★ **后继必须先有选择集**（★ mark 1/2/4）。
★★ **顺带订正一个易犯的误判**：★ `AccessSelections` **只用于**编辑**（★ `GetDefinition` → `AccessSelections` · ★ 示例 `:79`）
⇒ ★★ **280/281 的 `AccessSelections` 族不可调用**（`0x80010105`）**不适用**于**创建** —— ★ 别误引。

---

## 二、★★★★ 逐站点拍板：★ **2 处可换 · 3 处不可换**

★ 判据 = ★★ **该站点是否**已经预选****（★ 因为后继**必须**预选）：

| ★ 站点 | ★ 包围函数 | ★ 现行入口 | ★ **已经预选？** | ★ 可换？ | ★ 依据 |
|---|---|---|---|---|---|
| `sw_part.py:1536` | ★ **`linear_pattern`**（生产封装） | `FeatureLinearPattern5` | ❌ **否**（★ 靠 `DName1`/`DName2` **尺寸名**） | ★★ **否** | ★ **换 = 改契约** |
| `sw_part.py:2544` | `linear_pattern_report` | 同上 | ❌ 否 | ★★ **否** | ★ 同上 |
| `sw_pattern.py:548` | `insert_local_curve_driven_pattern_report` | `FeatureLocalCurveDrivenPattern` | ✅ **是**（`mark=1` + `mark=2`） | ★★ **是** | ★ 与后继要求**一致** |
| `sw_sheet_metal.py:1535` | `insert_form_tool_report` | `InsertFormToolFeature` | ✅ **是**（`select_entity_by_index(model,"FACE",…)`） | ★★ **是** | ★ 同上 |
| `sw_render_material.py:345` | `delete_render_material` | `DeleteRenderMaterial` | — | ★★ **否** | ★ **后继在本机不可调**（★ `output/render-material-family-evidence.json`：`新入口能调数 **3/4**` · `DeleteDisplayStateSpecificRenderMaterial.ok = false`） |

★★★ **⇒ 5 处里 3 处按 `GOAL.md` §二「做不了的标注理由并删号」**：
- **2 处**（`sw_part.py` ×2）= ★★ **换它 = 改 `linear_pattern` 的契约**（★ 调用方要开始负责预选）
  ⇒ ★ **不是"换路由"**，★ 是**独立的能力升级**（★ 需真机验 + 业主拍板）；
- **1 处**（`sw_render_material.py`）= ★★ **后继在本机到不了**（★ 已有真机证据）。

★★ **剩下 2 处**（`sw_pattern.py` / `sw_sheet_metal.py`）⇒ ★ **可以换**，★ **但换它必须真机验**（铁律 2）
⇒ ★★ **本轮 SolidWorks 未运行**（★ `Get-Process SLDWORKS` 空）⇒ ★ **不在本轮改**。

---

## 三、★★★★ 顺带订正一条**错的记档**

★★ `scripts/sw_part.py` 里 **3 处**写「★ `5` 也废弃、★ **后继空**」+「∴ 是官方**没清状态标记**」
⇒ ★★★ **两处都错**：
- ★ 「后继空」**错** —— ★ 官方逐字**给了后继**（`CreateFeature`）；
- ★ 「官方没清状态标记」**错** —— ★ 官方**不是**漏标，★ 是**换了族**（★ 后继不是 `FeatureLinearPattern6`）。

★★ 真因 = ★ **「最高代」说的是**本族**（`1`–`5`）**，★ **而官方给的替换是**跨族**的 `CreateFeature`**。
⇒ ★ **已订正 3 处**（★ 1456 官方链 · 1533 换代记档 · 2547 报告函数）· ★ 判据按**整文件**守「`后继空` 绝迹」。

---

## 四、需求

### FR-001 ★★ 官方三页 + 指南的逐字被锚住
- **验收场景**：`test_official_pages_give_successor_and_preselect` 通过。

### FR-002 ★★★ `scripts/` 里**只有 5 处**真命中
- **验收场景**：`test_exactly_five_real_sites_in_scripts` 通过。

### FR-003 ★★★ **可换的 2 处必须已经预选**
- **验收场景**：`test_switchable_sites_already_preselect` 通过。

### FR-004 ★★★ **不可换的记档必须写清真因**（★ 且「后继空」绝迹）
- **验收场景**：`test_unspportable_site_records_the_real_reason` 通过。

### FR-005 ★★ **第三处不可换**有真机证据
- **验收场景**：`test_render_material_successor_is_unreachable_per_evidence` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 五、非目标

- ★★★ **不改任何路由** —— ★ **SolidWorks 未运行** ⇒ ★ **不能真机验** ⇒ ★ **铁律 2 不许换**。
- ★ **不改** `sw_pattern.py` / `sw_sheet_metal.py`（★ 它们**可以**换，★ 但那要**真机验** ⇒ 下一轮）。
- ★ **不删任何文件** · ★ **不动任何 hook**。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**先红后绿** | ★ 把纯函数跑在 **`git HEAD` 的旧 `sw_part.py`** 上 ⇒ **3 条问题**（★ 含「后继空」）；改后 **`6 passed`** |
| SC-2 | 「后继空」**整文件绝迹** | `grep -c 后继空 scripts/sw_part.py` = **0** |
| SC-3 | 相关判据不破 | 6 个文件 **41 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 七、未过门（本轮不做，如实登记）

- ★★★ **2 处可换的换路由 + 真机验**（★ `sw_pattern.py::insert_local_curve_driven_pattern_report` ·
  `sw_sheet_metal.py::insert_form_tool_report`）—— ★ **前置 = SolidWorks 必须在运行**。
- ★ `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` ·
  ★ 223 的 B1–B5（需业主定权属）· ★ `docs/phase2-obsolete-status.md:36` 的同一句旧措辞 · 未提交未部署。
