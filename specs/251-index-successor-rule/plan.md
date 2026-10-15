# Plan — 索引后继规则：同名链接优先

**Feature**: `specs/251-index-successor-rule/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | **官方类型页** | `C:/swapi/types/<接口>/<成员>.md` | 官方那句原文 + 后继页语义（判哪个才是真后继） | ★★★ **最高** |
| 2 | **244 的裁决** | `specs/244-multi-successor-rule/` | 「同名链接优先」规则的**来源** | ★★ 派生自 1 |
| 3 | **现行索引** | `specs/202-.../recon/official-obsolete-index.json` | 旧值的**事实来源**（用于 diff） | ★ 产物 |

**冲突裁决顺序**：1 > 2 > 3。

---

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 取行 / `OBS` / `SWAPI` | `tools/build_obsolete_index.py`（★ 现行唯一真源） | ★ 探针 **import** 常量，逐字复刻循环 |
| 「同名链接」判据 | 244 的 `_split` 口径（`Iface::Member`） | ★ 逐字 |
| 靶子表值 = **裸成员名** | 247 已定（★ 本轮踩到：夹具里误写全限定名 ⇒ 关 2 报红） | ★ 逐字 |

★★ **教训（本轮踩的）**：★ 改 `SketchTrim` 夹具时**误写成全限定名** `"ISketchManager::SketchTrim"`
⇒ ★ 关 2（链终点）报 `successor-is-not-chain-terminal:ISketchManager::SketchTrim!=SketchTrim`
—— ★ **靶子表的值是裸成员名**，链终点 `term[1]` 也是裸名。

---

## 三、实现步骤

1. **先量**：`output/_probe251_rule_impact.py` → `.txt` ⇒ 全 1671 条里会变的 = **6**。
2. **备份**：`cp` 索引到 `output/_index_backup_251.json`（★ 可回滚）。
3. **改生成器**：`tools/build_obsolete_index.py` 的取链接三行（★ 只改这一处）。
4. **重生成**：`python -B tools/build_obsolete_index.py` ⇒ diff = **6**。
5. **同步连带判据**（★ 4 处，见 `spec.md` FR-004）+ 修 244 的**潜伏空判据**（FR-005）。
6. **回写四处**：ROADMAP §一 · memory · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_*.md`。

---

## 四、改动面

| 文件 | 动作 |
|---|---|
| `tools/build_obsolete_index.py` | ★ **改取链接逻辑**（3 行 → 7 行） |
| `specs/202-.../recon/official-obsolete-index.json` | ★ **重生成**（6 条后继 + `at` 时间戳） |
| `tests/test_obsolete_multi_successor.py` | `_KNOWN_WRONG` 清空 + `_FIXED_BY_251` + 修空判据 + 检查量下界 |
| `tests/test_deprecated_table_admission.py` | `SketchTrim` 夹具值 → `"SketchTrim"` |
| `tests/test_deprecated_multi_successor_adjudication.py` | 同上 |
| `tests/test_deprecated_admissible_disposition.py` | 删 `SketchTrim` 行 + 下界 15 → 14 |
| `specs/251-index-successor-rule/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **未改**：`scripts/sw_*.py` · `scripts/sw_com_traps.py` · `scripts/release_check.py` · `docs/gate-classification.json` · `mcp-server/**`。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 改生成器影响面失控 | ★★ **先量**（6 条）+ **备份索引**（可回滚） |
| 清空 `_KNOWN_WRONG` ⇒ 判据变空 | ★★ 补**正向** `_FIXED_BY_251` + 检查量下界 |
| 连带判据（243/246/247）红 | ★ 已逐处定位并同步（★ 4 处） |
| 靶子表值写成全限定名 | ★ 已踩到并修（★ 裸成员名） |
| 改了 `tools/` ⇒ 生成器链 | ★ 索引本身**就是**生成器产物 ⇒ ★ 已重跑；★ 其余生成器产物不受影响（它们不读索引） |
