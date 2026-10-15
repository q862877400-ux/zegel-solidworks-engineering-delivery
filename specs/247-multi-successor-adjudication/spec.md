# Spec — 多后继的机械化表态（官方措辞 ⇒ 真后继个数）

**Feature**: `specs/247-multi-successor-adjudication/`
**日期**: 2026-10-09
**上游**: `specs/243-admission-gate-tightening/`（关 5）· `specs/246-admissible-candidates/`（4 条 `reject-multi-successor`）
**本轮只做一件事**：把 243 关 5 的「多后继**必须人工表态**」**机械化** —— 用**官方那句的措辞**判「真后继有几个」，并据此**收 2 条 / 拒 2 条**。

---

## 一、背景（243 的关 5 把「数据接口」也算成了后继）

243 的关 5 只数**全部** `[[…]]` 链接 ⇒ 官方常写「`See [[X]] and the Remarks in [[Y]]`」时
★ 把 **`Y`（数据接口）** 也算成「第二个后继」⇒ **假红**。

**本轮先量**（`output/_probe247_multi.py`）—— 254 条多链接条目的**措辞分布**：

| 措辞 | 条数 | 真后继 | 例 |
|---|---|---|---|
| `Superseded by A and B` | **235** | ★ **A 与 B 都是** | `IModelDoc2::SketchTrim`（`SketchExtend` + `SketchTrim`） |
| `See X and the Remarks in/of Y` | **14** | ★ **只有 X**（Y 是数据接口） | `IFeatureManager::FeatureLinearPattern5` |
| 其它 `See …` | **5** | ★ **判不出**（★ 顺序不可靠：`See [[IProjectionCurveFeatureData]] and [[IFeatureManager::CreateDefinition]]` ⇒ **数据接口在前**） | `IDimension::GetSystemValue3` |

★ **真树在调的多链接条目 = 18**：`SUPERSEDED-BY 16` · `SEE+REMARKS 2` · `SEE(other) 0`。

---

## 二、需求（每条带来源与验收场景）

### FR-001 ★★ 真后继个数必须由**纯函数**判出（三态）

- **来源**：官方文档 —— `C:/swapi/types/IModelDoc2/SketchTrim.md`（`Superseded by A and B`）·
  `IFeatureManager/FeatureLinearPattern5.md`（`See X and the Remarks in Y`）·
  `IDimension/GetSystemValue3.md`（`See A and B`，顺序不可靠）。
- **规则**：`_official_successor_links(line) -> list[str] | None`：
  - `Superseded by <clause>` ⇒ clause 里的链接**全部**是后继
  - `See <clause> and the Remarks in/of …` ⇒ ★ **只取 `Remarks` 之前**的链接
  - 其它 ⇒ **`None`**（机械判不出 ⇒ 必须人工表态）
- **验收场景**：`test_superseded_by_counts_all_links` · `test_see_remarks_counts_only_the_links_before_remarks` ·
  `test_see_without_remarks_is_undecidable` · `test_single_link_is_counted_as_one`（★ 四条**纯函数**用例，含 `Remarks of` 形态）。

### FR-002 ★★ 关 5 改为**三态**（1 过 / >1 拒 / None 须表态）

- **来源**：243 的关 5（★ 本轮**细化**，不是推翻）。
- **规则**：`_admission_failures(..., adjudicated=…)` 新增**表态表**参数：
  - `n > 1` ⇒ `multiple-official-successors`（★ **表态也不放行**）
  - `n is None` 且不在表态表 ⇒ `successor-count-undecidable`
  - `n == 1` ⇒ 该链接必须**在通往本表后继的链上**（★ 允许跳代）
- **验收场景**：`test_undecidable_requires_adjudication_and_superseded_pair_is_refused`（★ **合成表态表**驱动 ⇒ 真表为空也**有检查量**）。

### FR-003 ★★★ 「`Superseded by A and B`」**不许**被表态放行

- **来源**：246 的结论（★ 表的值是**裸成员名**，表达不了「两个都要」）。
- **验收场景**：`test_adjudication_never_whitelists_a_two_successor_entry`；★ 能红（把 `SketchTrim` 塞进表态表即红）。

### FR-004 表态表每条必须有**依据**（引用官方页路径）

- **来源**：本项目既有模式（「不许空口登记」）。
- **验收场景**：`test_adjudication_entries_have_evidence` —— ★ 真表为空 ⇒ ★ 该判据**把「依据不合格」抽成纯函数**，
  由**合成负例**证明它**能红**（★ 纪律 15：真树上不会自然触发的自证 ⇒ 抽纯函数喂输入）。

### FR-005 ★★ 收 **2** 条（`SEE+REMARKS` 形态）

- **来源**：官方页两边签名（见 `scripts/sw_com_traps.py` 的 spec 247 段）。
- **规则**：`IFeatureManager::FeatureLinearPattern5 → CreateFeature` ·
  `IFeatureManager::FeatureLocalCurveDrivenPattern → CreateFeature`（★ 真后继只有 `CreateFeature`）。
- **验收场景**：`test_collected_multi_successor_entries_pass_admission`（★ 真跑六关）·
  `test_collected_multi_successor_entries_are_in_the_target_table`（★ 逐字一致）。

### FR-006 ★ 拒 **2** 条

- `IFeatureManager::InsertFormToolFeature`：`Superseded by [[CreateDefinition]] and [[CreateFeature]]`
  ⇒ ★ **两个都是后继**（一个造 definition、一个建 feature）⇒ 表表达不了。
- `IModelDoc2::SketchTrim`：★ 关 4 拒（真后继是同名的 `ISketchManager::SketchTrim`）。
- **验收场景**：★ 两条**都不在** `DEPRECATED_ENTRIES` 里（`test_collected_..._in_the_target_table` 的反向）。

### FR-007 ★★ 收表的必须同步补 `_REGISTERED`

- **来源**：242 的教训 40。
- **验收场景**：`test_collected_multi_successor_entries_are_registered_where_called`（★ 含**死条目**反向检查）。

### FR-008 ★ **不许**改索引生成器

- **验收场景**：`git status --short tools/build_obsolete_index.py` 无输出。

---

## 三、非目标

- **不**改 `tools/build_obsolete_index.py`。
- **不**收 `Superseded by A and B` 的 16 条（★ 表表达不了）。
- **不**改任何**调用点**（★ 换路由必须真机验）。
- **不**动需 COM 的六项。

## 四、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 变异检验 **7 组**（24 处 `✓` · 0 处 `✗`） |
| SC-2 | 判据**是绿的** | `tests/test_deprecated_multi_successor_adjudication.py` **11/11 通过** |
| SC-3 | 扩容**不破互锁族** | 相关族 **65 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 生成器链已跑 | 7 步全跑（★ 改了 `scripts/`） |
| SC-6 | 生成器未改 | `git status --short tools/build_obsolete_index.py` 无输出 |

## 五、未过门（本轮不做，如实登记）

- **16 条 `Superseded by A and B`** 只登记理由、**不收**（★ 表表达不了「两个都要」）。
- **5 条 `See(other)`** 机械判不出 ⇒ ★ 但**真树在调的是 0 条** ⇒ **没有靶子**，表态表**现在为空**（★ 空满足，
  由 FR-002 的**合成表态表**用例保证机制可跑）。
- **新收 2 条的调用点一律不换路由**（★ 两条都不是 drop-in：都要先造 `I*PatternFeatureData`）。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
