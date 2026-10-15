# Acceptance — **把 `COMTYPES_CALL_SITES` 从「按行号」改成「按成员名」**

**Feature**: `specs/300-comtypes-table-name-keyed/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **同一形态的第三次失配被**从根上**消掉** ——
★ 表改成**按成员名**登记 ⇒ ★★ **加注释 / 挪代码都不会再让它失配** ✓

## 一、逐条验收

| # | 需求 | 判据 | ★ 读数 |
|---|---|---|---|
| FR-001 | ★★ 键是**成员名**不是行号 | `test_the_table_is_keyed_by_member_not_line` | ✅ pass |
| FR-002 | ★★★ **加行注释不再失配** | `test_adding_a_comment_does_not_break_it` | ✅ pass |
| FR-003 | ★★ 审计**真的**认出两条 | `test_audit_finds_both_sites` | ✅ pass |
| FR-004 | ★ 理由仍然齐全 | `test_reasons_survive_the_rekeying` | ✅ pass |
| FR-005 | ★ 四桶分流顺序未变 | `test_bucket_order_is_unchanged` | ✅ pass |
| — | **合计** | — | **5 passed** |

## 二、★★★★ 红消息与真因（★ 现场量出来的）

```
$ python -m pytest tests/test_arity_comtypes_classification.py -q
FAILED …::test_audit_separates_comtypes_from_doubt
E   AssertionError: 应当恰好 2 条 comtypes，实际 0
E   assert 0 == 2
```

| ★ 项 | ★ 值 |
|---|---|
| ★ 表里登记的键 | ★ `("sw_delivery.py", **671**)` · `("sw_delivery.py", **965**)` |
| ★★ 审计**实际**找到的站点 | ★ `(672, 'IGetDocumentNames', …)` · `(966, 'OpenDoc6', …)` |
| ★★ 差值 | ★★ **各 +1** |

★★ **那 +1 从哪来**：★ 工作树里给 `scripts/sw_delivery.py:248` 加了**一行**
`#: dispatch-guard: exempt internal-helper` ⇒ ★★ **它把后面所有行号推了 +1**。

## 三、★★★★★ 这是**同一形态的第三次**（★ 表自己的注释记着前两次）

★ `scripts/audit_call_arity.py:196-205` 逐字：

> ★★★★★★ 2026-10-04（轮 116）**⚠ 这张表按**行号**登记 ⇒ 它会**漂**** ——
> ★★ **真因**：★ 我在轮 87 与 115 改过 `sw_delivery.py`（★ 加注释 · ★ 换成员 · ★ 修 fake）⇒
> ★★★ **⇒ 那两条的行号从 `635` / `884` 漂到 `671` / `965`** ⇒ **登记失配** ✓
> ★★★★★ **⇒ 下次改这个文件时，★ 记得同步这两行**；★ **更稳的做法是改成**按成员名**登记**
> （★ 那要改 `audit` 的接口 —— ★ **本轮不动**、★ 如实留给后人）✓

★★★ **⇒ 前两次都是「改行号」（★ 把下一次漂移往后推）⇒ ★★ 本轮做那个「更稳的做法」** ✓

## 四、★★★ 红基线（★ 用「按行号」的旧形态复现）

```
# 把表换成「按当前实际行号」的旧形态
ac.COMTYPES_CALL_SITES = {('sw_delivery.py', 671): …, ('sw_delivery.py', 965): …}
ac.audit('scripts/sw_delivery.py', refs)
⇒ comtypes = 0（应是 2）· doubt members = {'IGetDocumentNames', 'OpenDoc6'}
```

★★ **⇒ 旧形态**确实**产出 0 条** ⇒ ★ 判据**真的在看这个形态**（★ 不是空判据）。

## 五、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `scripts/audit_call_arity.py` | ★ **键类型 `tuple[str,int]` → `tuple[str,str]`** + 两处查找点 + 注释 |
| 2 | `tests/test_arity_comtypes_classification.py` | ★ **断言改成成员名** + 加**负例**（键不许是 `int`） |
| 3 | `tests/test_comtypes_table_name_keyed_300.py` | ★ **新建判据**（5 例） |
| 4 | `specs/300-comtypes-table-name-keyed/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_delivery.py`（★ 那是**别人**的未提交改动 —— ★ 本轮**不动它**）。

## 六、★★★ 依据

| ★ 源 | ★ 逐字 |
|---|---|
| `MEMORY.md` 规则 32 | 「★★★ **证据表不许钉行号，也不许判「站点逐字相等」** —— ★ 站点只写**文件名**（或名字），★ 不写 `:行号`；★★ 因为「站点逐字相等」把「**代码变了**」与「**读取器坏了**」判成**同形** ⇒ ★ **每次改代码都假红**」 |
| `scripts/audit_call_arity.py:204` | 「★ 更稳的做法是改成**按成员名**登记」 |

## 七、★ 生成器链

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate300.log` |

## 九、未过门（如实登记）

| # | ★ 项 | ★ 说明 |
|---|---|---|
| ① | ★★ **同类形态还有一处**（★ `tests/test_arity_mismatch_triage.py` 的 `_TRIAGE`） | ★ 它**也按行号**登记（★ 16 条），★ 而它**当前是绿的** ⇒ ★ **说明它从不校验行号** ⇒ ★★ **潜在**缺陷（★ 一旦有人校验就红）。★ **本轮不改**（★ 不在本规格范围）；★ **如实登记**为同类风险。 |
| ② | ★ 广域回归里的 **15 条既有红** | ★★ **已用 `git stash` 隔离证明它们与本轮改动无关**（★ 去掉我的改动后**同样红**）⇒ ★ 属**他人未提交改动**造成的存量红；★ 另见 `specs/301-*`。 |
