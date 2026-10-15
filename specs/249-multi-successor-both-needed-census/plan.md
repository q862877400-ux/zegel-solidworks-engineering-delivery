# Plan — 「两个后继都要」的宿主级先量

**Feature**: `specs/249-multi-successor-both-needed-census/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 本轮用途 | 权威度 |
|---|---|---|---|---|
| 1 | **官方类型页** | `C:/swapi/types/<接口>/<成员>.md` | 判宿主接口（★ 主要靠 `## Returns`） | ★★★ **最高** |
| 2 | **官方废弃索引** | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 取「`Superseded by A and B`」的 15 条 | ★★ 派生自 1 |
| 3 | **真树源码** | `scripts/sw_*.py`（AST） | 取**写**站点与其**宿主表达式**、赋值来源 | ★ 事实来源 |

**冲突裁决顺序**：1 > 2 > 3。★ 与 248 同。

---

## 二、口径（逐字对齐，不许凭印象）

| 口径 | 真源 | 本文件怎么用 |
|---|---|---|
| 真树扫描 | `tests/test_deprecated_entry_interlock._scan_all_modules` | ★ **import** |
| 真树被调成员名 | `tests/test_deprecated_table_admission._called_names` | ★ **import**（★ 不重写） |
| 「写」的判据 | `ast.Attribute` 的 **`Store`** 上下文 | ★ 本文件自定（★ 见下） |
| 多后继形态 | 索引 `obsolete_line` 以 `Obsolete. Superseded by` 开头 **且** `[[…]]` ≥ 2 | ★ 逐字 |

★★ **为什么「写」必须单独定**：`get_com_member(obj, "M")` 与 `obj.M(...)` 都是**读**；
★ 只有 `obj.M = v` 是**写**。★ 而「两个后继」里**只有 Set 侧**才需要写 ⇒ ★ 读站点**不能**算作「需要两个后继」。

★★ **教训（本轮踩的，见 spec §二）**：★ **第一版探针按裸成员名归集** ⇒ 报出 **4 条假靶子**
（`KFactor` 的写站点宿主其实是 `ICustomBendAllowance`；`Name` 的写站点宿主是 `IMate2`/`IFeature`/`CWStudy`）。
⇒ ★ **定则：归集站点必须带宿主接口**（245 → 248 → 249 同一条线）。

---

## 三、实现步骤

1. **先量**（一次性探针，放 `output/`）：`output/_probe249_both_successors.py` → `.txt`
   ⇒ 列出 15 条条目 + 每个成员的**全部**站点（含 `read` / `write` 语义）。
2. **★ 发现第一版有假靶子** ⇒ 把口径下沉到**宿主级**：7 个写站点逐个读**赋值来源**判接口。
3. **先写能红的判据**：`tests/test_multi_successor_both_needed_census.py`
   ⇒ 纯函数 `_both_needed_failures` + 合成负例（正例 `IView` 写 `Name` ⇒ 红；反例 `IFeature` 写 `Name` ⇒ 不红）。
4. **证明它红**：变异（把 `sw_sheet_metal.py:257` 的宿主接口改成 `IBendsFeatureData`）⇒ 判出 **1 条**靶子。
5. **把踩的坑冻成判据**：`test_bare_name_aggregation_would_give_false_targets`（下界 **4**）。
6. **回写四处**：ROADMAP §一 · `memory/2026-10-09.md`（append）· `output/AUTO_HANDOFF.md`（覆盖）· `output/AUTO_RUN_*.md`。

---

## 四、改动面（预期）

| 文件 | 动作 |
|---|---|
| `tests/test_multi_successor_both_needed_census.py` | ★ **新增**（6 例） |
| `specs/249-multi-successor-both-needed-census/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` | §一 游标追加 |
| `.workbuddy-ai/memory/2026-10-09.md` | append |
| `output/AUTO_HANDOFF.md` | 覆盖写四段 |
| `.specify/feature.json` | `248` → `249` |

★ **不改**：`tools/build_obsolete_index.py` · `scripts/sw_com_traps.py` · `scripts/sw_*.py` · `scripts/release_check.py` ·
`docs/gate-classification.json` · `mcp-server/**`。
★ **不跑生成器链**（★ 没改 `scripts/`）。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 按裸名归集 ⇒ 假靶子 | ★★ 判据必须带**宿主接口**（本文件的核心） |
| 「写」漏读（点式赋值 / 包装器写） | ★ 用 `ast.Attribute` 的 `Store` 上下文收；★ 包装器形态（`get_com_member`）**只读**，★ 不可能是写 |
| 写站点被改名/移动 ⇒ 判据红 | ★ 这正是设计意图；★ 红时按新站点补表态 |
| `C:/swapi/types` 不在本机 | ★ 判据 `pytest.skip`；★ 但表态是**离线判读结果**，仍在 |
| `release_check` 约 2m40s | ★ **后台跑 + 落盘日志** |
