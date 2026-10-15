# Acceptance — R8 跨天假红：比对生成物时必须先剥掉「非数据字段」（日期）

**Feature**: `specs/295-r8-crossday-false-red/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立（`3 failed, 2 passed`）· 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **R8 从「每天必红一次」变成「只在数据真变时红」** ——
★ 修在**读者**侧（`normalize_generated_text`），★ **不动生成器**（★ 生成物**应当**记录生成时间）。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★ 只差日期 ⇒ **不得**报红 | `test_date_only_difference_is_not_a_freshness_failure` | ❌ **FAILED** | ✅ pass |
| FR-002 | ★★★ 真数据变化 ⇒ **必须**报红 | `test_real_data_difference_is_still_red` | ✅ pass | ✅ pass |
| FR-003 | ★★ 归一化**可指认** | `test_normalizer_is_declared_and_named` | ❌ **FAILED** | ✅ pass |
| FR-004 | ★★ 边界冻结（不改生成器） | `test_generator_and_manifest_untouched` | ✅ pass | ✅ pass |
| FR-005 | ★★ 归一化的**正负例** | `test_normalizer_keeps_data_lines_and_drops_dates` | ❌ **FAILED** | ✅ pass |
| — | **合计** | — | **3 failed, 2 passed** | **5 passed** |

★★★ **两条对照缺一不可**：只写「不报红」⇒ ★ 把比对**整段删掉**也能过；
只写「报红」⇒ ★ 假红照样在。★ 本规格**两条都钉住**。

## 二、★★★★ 复现（★ 修前）

```
$ # 只把生成日期改成昨天（★ 数据一字不改）
$ python scripts/check_union_conventions.py
[FAIL] 规范与地图存在性
   - docs/union-level-audit.md 与最新数据**不一致** —— 跑 `python scripts/gen_level_audit.py` 重生成（R8）
```

★ 而 `git diff` **只有 2 行**：`生成日期：2026-10-09` ↔ `生成日期：2026-10-10`。

## 三、★★★ 根因链

| ★ 环 | ★ 逐字 | ★ 位置 |
|---|---|---|
| ① | `L.append("> 生成日期：%s ｜ 数据源：…" % (date.today().isoformat(), …))` | `gen_level_audit.py:81` |
| ② | `if want != audit.read_text(encoding="utf-8"):` | `check_union_conventions.check_docs()`（R8） |
| ③ | ★★ 跨午夜 ⇒ ① 变、② 逐字节比 ⇒ **必然不同** | — |

⇒ ★★★ **定则**（`AUTO_HANDOFF.md` ③ 第 74 条逐字）：
「**比生成物时先剥掉时间戳/日期**，★ 否则「日期变了」被误判成「数据变了」」。

## 四、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `scripts/check_union_conventions.py` | ★ **加 `normalize_generated_text()`** + R8 两侧过归一化 + 报错文案补「已忽略**非数据字段**」 |
| 2 | `tests/test_r8_crossday_false_red_295.py` | ★ **新建判据**（5 例） |
| 3 | `specs/295-r8-crossday-false-red/*` | ★ 本规格四件套 |

★ **未改**：`gen_level_audit.py`（★ 边界冻结）· `capabilities.yaml` · `docs/union-level-audit.md`。

## 五、★★★ 同类风险扫描（★ 只修一处不算修）

| # | ★ 门禁 | ★ 比对方式 | ★ 生成器写日期？ | ★ 同一个病？ |
|---|---|---|---|---|
| ① | `check_union_conventions.check_docs`（R8） | ★ **逐字节** | ★★ **写** | ★★ **有 ⇒ 本轮修** |
| ② | `check_digest_freshness` | ★ 结构化字段 | ★ 否 | ★ 没有 |
| ③ | `check_signature_audit_freshness` | ★ 行级 | ★ 否 | ★ 没有 |
| ④ | `check_report_freshness` | ★ 4 个数字字段 | ★ 否 | ★ 没有 |
| ⑤ | `check_map_fresh` | ★ 逐字节 | ★ 否（`grep` 无 `date.today`） | ★ 没有 |

## 六、★★★ 端到端复验（★ 判据绿 ≠ 真场景绿）

```
$ # 修后，再把日期改成昨天
$ python scripts/check_union_conventions.py
并入规范门禁通过
rc=0
```

## 七、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** · ★ 打包副本 **471 files · pruned []** |

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` | **47** |
| 日志 | `output/_gate295.log` |

## 九、未过门（如实登记）

★ 无新增未过门。★ 本规格**只修比对口径**，★ 不改任何能力状态。
