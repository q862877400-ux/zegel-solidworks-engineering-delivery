# Plan — R8 跨天假红：比对生成物时必须先剥掉「非数据字段」（日期）

**Feature**: `specs/295-r8-crossday-false-red/`
**日期**: 2026-10-10

---

## 一、施工顺序

| # | 步 | ★ 内容 | ★ 为什么 |
|---|---|---|---|
| 1 | **先量** | 复现：只改日期 ⇒ `[FAIL] 与最新数据不一致` | ★ 先证明它**真的**会红 |
| 2 | **定性** | 证明「只差日期、数据零变化」（`git diff` 只 2 行） | ★ 与「数据真变了」区分开 |
| 3 | **同类扫描** | 枚举 5 条新鲜度门禁 × 各自的生成器 | ★ **只修一处不算修** —— 要证明别处没同一个病 |
| 4 | **写判据（先红）** | `tests/test_r8_crossday_false_red_295.py`（5 条） | ★ 含**正例**（只差日期 ⇒ 不报）与**负例**（数据变了 ⇒ 必报） |
| 5 | **跑红基线** | `pytest …` ⇒ **`3 failed, 2 passed`** | ★ 两条对照（生成器未动 / 真数据仍红）**本来就该绿** |
| 6 | **改比对** | 加 `normalize_generated_text()`；R8 两侧都过它 | ★ 修在**读者**侧（★ 生成器**应当**记录生成时间） |
| 7 | **跑绿** | `pytest …` ⇒ **5 passed** | ★ |
| 8 | **端到端复验** | 再跑一次「只改日期」的真门禁 ⇒ `rc=0` | ★ 判据绿 ≠ 真场景绿 |
| 9 | **门禁 + 回写** | `release_check` @3.14.7 · 四处状态 | ★ `GOAL.md` §五 |

---

## 二、★ 判据设计（为什么是这两条对照）

| ★ 判据 | ★ 它防的是什么 |
|---|---|
| `test_date_only_difference_is_not_a_freshness_failure` | ★★ **假红**（每天一次） |
| `test_real_data_difference_is_still_red` | ★★★ **假绿**（把门禁改瞎 —— ★ 比假红更糟） |
| `test_normalizer_keeps_data_lines_and_drops_dates` | ★ 归一化的**作用范围**（★ 只吞日期、不吞数据） |
| `test_normalizer_is_declared_and_named` | ★★ **可指认**（★ 不是静默吞掉差异） |
| `test_generator_and_manifest_untouched` | ★ **边界冻结**（★ 不改生成器） |

★★ **两条对照缺一不可**：只写「不报红」的判据 ⇒ ★ 把比对**整段删掉**也能过。

---

## 三、★ 同类风险扫描读数（★ 只修一处不算修）

| # | ★ 门禁 | ★ 比对方式 | ★ 生成器写日期？ | ★ 同一个病？ |
|---|---|---|---|---|
| ① | `check_union_conventions.check_docs`（R8） | ★ **逐字节** | ★★ **写**（`date.today()`） | ★★ **有** |
| ② | `check_digest_freshness` | ★ 结构化字段 | ★ 否 | ★ 没有 |
| ③ | `check_signature_audit_freshness` | ★ 行级（给「要改成的那一行」） | ★ 否 | ★ 没有 |
| ④ | `check_report_freshness` | ★ 4 个数字字段 | ★ 否 | ★ 没有 |
| ⑤ | `check_map_fresh`（`union-coverage-matrix`） | ★ 逐字节 | ★ 否（`grep` 无 `date.today`） | ★ 没有 |

⇒ ★★★ **只有 R8 一处** —— ★ 而它**每 24 小时必红一次**。

---

## 四、★ 仓内依据

| 源 | ★ 逐字 | ★ 用途 |
|---|---|---|
| `docs/AUTO_HANDOFF.md` ③ 第 74 条 | 「比生成物时先剥掉时间戳/日期，★ 否则「日期变了」被误判成「数据变了」」 | ★ 定则的**出处**（上一轮记的坑） |
| `scripts/gen_level_audit.py:81` | `% (date.today().isoformat(), manifest.get("schema_version"))` | ★ 病灶 |
| `scripts/check_union_conventions.py` `check_docs()` | `if want != audit.read_text(encoding="utf-8")` | ★ 逐字节比对 |
| `MEMORY.md` 判据纪律 1 | 「『修宽判据/正则』本身必须有能红的判据」 | ★ 本轮**先跑红基线** |
| `known-facts.md` 事实 62 | 「一个门禁『写了』不等于它『有效』—— 负例测试是唯一的证明」 | ★ 归一化函数配**正负例** |
