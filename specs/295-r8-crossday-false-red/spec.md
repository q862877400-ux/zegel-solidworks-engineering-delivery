# Spec — **R8 跨天假红：比对生成物时必须先剥掉「非数据字段」（日期）**

**Feature**: `specs/295-r8-crossday-false-red/`
**日期**: 2026-10-10
**上游**: `docs/AUTO_HANDOFF.md` ③ 第 **74** 条（★ 本会话**上一轮**记下的坑，★ 但**没修**）
**触发**: ★ 收 `GOAL.md` §五 优先级 **② 门禁本体**（★ 排在「能力项」之前）。

---

## 一、★★★★ 先量：R8 是一条**每天必红一次**的门禁

★ **复现**（★ 只改**日期**那一个字段，★ 数据零变化）：

```
$ sed -i 's/生成日期：2026-10-10/生成日期：2026-10-09/' docs/union-level-audit.md
$ python scripts/check_union_conventions.py
[FAIL] 规范与地图存在性
   - docs/union-level-audit.md 与最新数据**不一致** —— 跑 `python scripts/gen_level_audit.py` 重生成（R8）
```

★★★ **而两次的内容逐字相同**（★ 实测：`git diff` **只有 2 行**，★ 只差那个日期）：
```
> 生成日期：2026-10-09 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
> 生成日期：2026-10-10 ｜ 数据源：`capabilities.yaml`（`schema_version` = `2.0`）
```

⇒ ★★ **根因**：`check_union_conventions.check_docs()` 做的是**逐字节比对**：

```python
want = _mod.build(json.loads(...), sys.modules[__name__])
if want != audit.read_text(encoding="utf-8"):      # ★ 逐字节
    bad.append("… 与最新数据**不一致** …")
```

★★ 而 `gen_level_audit.build()` 第 **81** 行**把 `date.today()` 写进正文**：

```python
L.append("> 生成日期：%s ｜ 数据源：…" % (date.today().isoformat(), …))
```

⇒ ★★★ **跨过午夜 ⇒ 即便数据零变化，「重生成出来的」与「盘上那份」也必然不同**
⇒ ★ **每天一次假红** —— ★ 而假红会**淹没真红**（★ 这正是 `AUTO_HANDOFF.md` ③ 第 74 条记的）。

---

## 二、★★★ 同类风险扫描（★ 只修一处不算修）

| # | ★ 站点 | ★ 有没有同一个病 | ★ 依据 |
|---|---|---|---|
| ① | `check_union_conventions.check_docs`（R8） | ★★ **有** | ★ 逐字节比对 + 生成物带 `date.today()` |
| ② | `check_digest_freshness.py` | ★ **没有** | ★ 它比的是**结构化字段**（★ 生成器 `gen_harvest_digest` 不写日期进正文） |
| ③ | `check_signature_audit_freshness.py` | ★ **没有** | ★ 同上（★ 它给「要改成的那一行」，★ 是**行级**比对） |
| ④ | `check_report_freshness.py` | ★ **没有** | ★ 它比**4 个数字字段**（★ 且无 `origin/main` 时 SKIP） |
| ⑤ | `check_map_fresh`（union-coverage-matrix） | ★ **没有** | ★ `build_union_map.py` **不写日期**（★ 实测 `grep` 无 `date.today`） |

⇒ ★★★ **只有 R8 一处** —— ★ 而它**每 24 小时必红一次**。

---

## 三、需求

### FR-001 ★★★ **比对前必须归一化「非数据字段」**（日期/时间戳）
- **验收场景**：`test_date_only_difference_is_not_a_freshness_failure` 通过
  （★ 造一份**只改日期**的盘上文件 ⇒ 门禁**不得**报不一致）。

### FR-002 ★★★ **真数据变化必须仍然报红**（★ 不能把门禁改瞎）
- **验收场景**：`test_real_data_difference_is_still_red` 通过
  （★ 改一条能力的 `level` ⇒ 门禁**必须**报不一致）。

### FR-003 ★★ 归一化必须**可指认**（★ 不是静默吞掉）
- **验收场景**：`test_normalizer_is_declared_and_named` 通过
  （★ 归一化函数**存在且带来源块**，★ 且门禁输出里**说明**了「已忽略非数据字段」）。

### FR-004 ★★ **边界冻结**：本轮**只改比对口径**，★ 不改生成器、不改 `capabilities.yaml`
- **验收场景**：`test_generator_and_manifest_untouched` 通过。

### FR-005 ★★ 修法要有**负例**（★ 事实 62：写了 ≠ 有效）
- **验收场景**：`test_normalizer_keeps_data_lines_and_drops_dates` 通过（★ 纯函数三组正负例）。
