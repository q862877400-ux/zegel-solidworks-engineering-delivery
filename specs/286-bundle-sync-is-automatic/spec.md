# Spec — **「同步打包副本」不是待办**（★ 生成器链头尾各一次 + 门禁两道守）

**Feature**: `specs/286-bundle-sync-is-automatic/`
**日期**: 2026-10-10
**上游**: ★ ② 段原第 3 条（★ 原话：「**发版前**才需要：同步打包副本（`scripts/sync_bundled_skill.py`）」）
**本轮只做一件事**：★ **量它到底是不是待办**（★ 按 §二：★ 不是待办的要**删号**，★ 别占编号）。

---

## 一、★★★ 现场量：★ 副本与源**逐字节一致**

| 项 | 读数 |
|---|---|
| ★ 源 `scripts/*.py` | **199** 个 |
| ★ **一致** | ★★ **199** |
| ★ **不一致** | ★★ **0** |
| ★ **副本缺** | ★★ **0** |

⇒ ★★★ **副本**始终同步**** —— ★ 不是因为「碰巧」，★ 而是因为**链每轮都跑**（★ 见 §二）。

---

## 二、★★★ 为什么它**永远不会被漏掉**（★ 两道保险）

| # | 保险 | ★ 内容 |
|---|---|---|
| ① | ★★ **生成器链头尾各一次** | ★ 顺序逐字：★ **`scripts/sync_bundled_skill.py`** → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → ★ **`scripts/sync_bundled_skill.py`**（★ 本会话**每轮改 `scripts/` 都跑**，★ 实测 **7/7 `exit 0`**） |
| ② | ★★ **门禁两道守** | ★ `release_check.py` 的 **`bundled_skill_files`**（★ 打包文件数 · 实测 **471**）· ★ **`digest_freshness`**（★ 摘要新鲜度） |

⇒ ★★★ **就算链漏跑**，★ **门禁也会红** ⇒ ★★ **它**不是待办****，★ 而是**工作流的一个自动环节**。

---

## 三、需求

### FR-001 ★★★ 副本与源**逐字节一致**（★ 现场比对）
- **验收场景**：`test_bundle_is_byte_identical` 通过（★ **live**：★ 每次跑都现场比）。

### FR-002 ★★ 门禁**两道守**都在
- **验收场景**：`test_two_gate_guards_exist` 通过。

### FR-003 ★★★ 链**头尾各一次**同步器
- **验收场景**：`test_the_chain_syncs_at_both_ends` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 四、非目标

- ★ **不改** `scripts/` ⇒ ★ **不跑生成器链**。
- ★ **不改** 链的顺序（★ 那是既有纪律）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 零比到 / 有不一致 / 有缺 / 守少一道 / 结论不对 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_bundle_sync_is_automatic.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 六、未过门（本轮不做，如实登记）

- ★★★ **12 条 `arity` 接线**（★ ② 段第 1 条的衍生项）—— ★ 前置是**6 个 `Double&` 要先在 cosworks 上找到正例**（★ 274）。
- ★★ **250 的 7 处换路由**（★ ② 段第 2 条）—— ★ 要真机验。
- ★ `create_draft` 的 `pre_call` 未接 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
