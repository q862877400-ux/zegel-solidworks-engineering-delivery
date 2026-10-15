# Acceptance — 换路由可行性逐站点拍板

**Feature**: `specs/293-route-change-viability/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线 3 条（★ 跑在 `git HEAD` 的旧实现上）· 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **5 处真命中里**2 处可换、3 处不可换**** ——
★ 「250 的换路由」**不是一件事，是五件事**，★ 且**只有两件成立**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★ 官方三页 + 指南逐字被锚住 | `test_official_pages_give_successor_and_preselect` | ✅ pass |
| FR-002 | ★★★ `scripts/` 里只有 5 处真命中 | `test_exactly_five_real_sites_in_scripts` | ✅ 5 处 |
| FR-003 | ★★★ 可换的 2 处**必须已经预选** | `test_switchable_sites_already_preselect` | ✅ `mark=1`/`mark=2` · `select_entity_by_index` |
| FR-004 | ★★★ 不可换的记档写清真因（★ 「后继空」绝迹） | `test_unspportable_site_records_the_real_reason` | ✅ `grep -c 后继空` = **0** |
| FR-005 | ★★ 第三处不可换有真机证据 | `test_render_material_successor_is_unreachable_per_evidence` | ✅ `新入口能调数 3/4` |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★★ 逐站点拍板（★ 本轮的核心产出）

★ 判据 = ★★ **该站点是否**已经预选****（★ 因为后继**必须**预选）：

| ★ 站点 | ★ 包围函数 | ★ 已预选？ | ★ 可换？ | ★ 依据 |
|---|---|---|---|---|
| `sw_part.py:1536` | ★ **`linear_pattern`**（生产封装） | ❌ **否**（★ 靠 `DName1`/`DName2` **尺寸名**） | ★★ **否** | ★ **换 = 改契约** |
| `sw_part.py:2544` | `linear_pattern_report` | ❌ 否 | ★★ **否** | ★ 同上 |
| `sw_pattern.py:548` | `insert_local_curve_driven_pattern_report` | ✅ **是**（`mark=1` + `mark=2`） | ★★ **是** | ★ 与后继要求**一致** |
| `sw_sheet_metal.py:1535` | `insert_form_tool_report` | ✅ **是**（选一个 `FACE`） | ★★ **是** | ★ 同上 |
| `sw_render_material.py:345` | `delete_render_material` | — | ★★ **否** | ★ **后继在本机不可调**（`DeleteDisplayStateSpecificRenderMaterial.ok = false`） |

## 三、★★★★ 官方依据（★ 逐条逐行）

| 源 | ★ 逐字 |
|---|---|
| `FeatureLinearPattern5.md:12` | 「Obsolete. See `IFeatureManager::CreateFeature` and the Remarks in `ILinearPatternFeatureData` and `ILocalLinearPatternFeatureData`.」 |
| `FeatureLocalCurveDrivenPattern.md:12` | 「Obsolete. See `CreateFeature` and the Remarks in `ILocalCurvePatternFeatureData`.」 |
| `InsertFormToolFeature.md:12` | 「Obsolete. Superseded by `CreateDefinition` and `CreateFeature`.」 |
| **`Pattern Features and their Feature Data Objects.md:20`** | ★★★ 「**Before calling `IFeatureManager::CreateDefinition`, you must pre-select the entities needed to create the linear pattern feature.**」 |
| `ILinearPatternFeatureData/_overview.md:20` | ★★★ **同句** + mark 表：**1** Direction 1 · **2** Direction 2 · **4** faces/features · **256** solid bodies |
| `Create_Bidir_Linear_Pattern_Example_CSharp.md:50-67` | ★★ **官方迁移示例**：`SelectByID2(mark 4)` ⇒ `(mark 1)` ⇒ `(mark 2)` ⇒ `CreateDefinition(swFmLPattern)` ⇒ `CreateFeature` |
| `Create_and_Access_Curve-driven_Pattern_Feature_Example_VB.md:65-74` | ★★ 同形：`mark 4` ⇒ `mark 1` ⇒ `CreateDefinition(swFmCurvePattern)` ⇒ `CreateFeature` |

★★★ **顺带订正一个易犯的误判**：★ `AccessSelections` **只用于**编辑**（★ 示例 `:79`：`GetDefinition` → `AccessSelections`）
⇒ ★★ **280/281 的 `AccessSelections` 族不可调用**（`0x80010105`）**不适用**于**创建** —— ★ **别误引**。

## 四、★★★★ 顺带订正一条**错的记档**（★ 3 处）

★★ `scripts/sw_part.py` 原写「★ `5` 也废弃、★ **后继空**」+「∴ 是官方**没清状态标记**」⇒ ★★★ **两处都错**：

| ★ 错话 | ★ 为什么错 |
|---|---|
| 「**后继空**」 | ★ 官方逐字**给了后继**（`CreateFeature`） |
| 「官方**没清状态标记**」 | ★ 官方**不是**漏标，★ 是**换了族**（★ 后继不是 `FeatureLinearPattern6`） |

★★ 真因 = ★ **「最高代」说的是**本族**（`1`–`5`）**，★ **官方给的替换是**跨族**的 `CreateFeature`**。
★ **已订正 3 处**：★ 1456（官方链）· 1533（换代记档）· 2547（报告函数）。
★★ **判据按**整文件**守**（★ 因为实测**先漏了一处** —— 只查一个函数会漏）。

## 五、★★★ 红基线（★ 跑在 `git HEAD` 的旧实现上 · 铁律 1/12）

```
$ git show HEAD:scripts/sw_part.py > output/_probe293_head.py
$ python -B output/_probe293_red.py
HEAD 源码段里有「后继空」吗: True
HEAD 源码段里有 `CreateFeature` 吗: False
★ 红基线读数：问题 3 条
    ★★★ `sw_part.py` 的原记档仍写「后继空」⇒ 与官方逐字矛盾
    ★★ `sw_part.py` 没写出官方后继 `CreateFeature`
    ★★ `sw_part.py` 没写出「后继**要求预选**」这条**不能换的真因**
```
★ 改后：**`6 passed`** · ★ `grep -c 后继空 scripts/sw_part.py` = **0** ✓
★ 相关判据（6 个文件）：**`41 passed`** ✓

## 六、生成器链（★ 改了 `scripts/` ⇒ 必须）

★ 7 步全 `rc=0`：`sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest`
→ `build_union_map` → `gen_dead_ends` → **`sync_bundled_skill`**（★ 头尾各一次）· ★ 打包副本 **471 files · pruned []**。

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` | **47**（★ 未新增门禁文件） |
| `skipped` | `["provenance"]`（★ 缺数据源 ⇒ `[SKIP]`，非失败） |
| `bundled_skill_files` | **471** |
| 日志 | `output/_gate293.log`（★ 实测 **2m19s**） |
| ★★ 日志 ②（★ **回写全部完成后重跑**） | `output/_gate293b.log` —— **`status pass` · `EXIT 0` · `missing []` · `gates 47` · `non-pass []`**（★ **2m20s**） |

## 八、★★★ 未过门：2 处可换 —— ★ **已被 294 真机推翻**（★ 2026-10-10 追记）

★★★ **真机读数**（★ 走 `tools/sw_guard.py --timeout 600` 跑 `tools/probe_spec211_curvedriven.py` ·
★ SW rev **34.4.1** · ★ 7.26 s · ★ 证据 `output/spec211-b5-curvedriven.json`）：
★ `mark1(要阵列的特征)=True` · ★★ **`mark2(方向曲线)=False`** · ★ `selection_count=1`
⇒ ★★★ **`new_features=[]` · `returned_is_none=true` ⇒ **不建**** ⇒ ★★ **真因是**前置没上****。

★★★ **⇒ 本切片的两条「可换」结论被改**：
| ★ 站点 | ★ 293 原判 | ★ **294 真机订正** |
|---|---|---|
| `sw_pattern.py:548` | ★ 可换 | ★★ **换路由**无效**** —— ★ 后继 `CreateDefinition` + `CreateFeature` **同样要 mark2** ⇒ ★ **换了照样不建** |
| `sw_sheet_metal.py:1535` | ★ 可换 | ★★ **降级为「从未真机验」** —— ★ 293 的判据只查**代码里有选择调用** ⇒ ★ **弱判据**（★ 已删 · ★ 立墓碑） |

★★★ **★ 本切片的判据由此升级**：★ `SITES` 的第一项从「**代码里已预选**」改成「**真机前置已满足**」，
★ 并**新增** `test_machine_says_the_direction_curve_never_selects`（★ 查**真机读数**，★ 不查代码）。
★★★ **★ 真正剩下的**是「**修 `FeatureLocalCurveDrivenPattern` 的 mark2 前置**」—— ★ **不是换路由**。

★ **其余未过门**：★ `create_draft` 的 `pre_call` · ★ `DeleteRenderMaterial` · ★ 4 处 `needs-feature-data` ·
★ 223 的 B1–B5（需业主定权属）· ★ `docs/phase2-obsolete-status.md:36` 的**同一句旧措辞**（★ 本轮只改了**第一现场** `sw_part.py`）·
★ **未提交 / 未部署** · ★ **未删任何文件** · ★ **未动任何 hook** · ★ **未派任何成员**。
