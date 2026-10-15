# Acceptance — 16 条 arity 不符的分桶定罪

**Feature**: `specs/253-arity-mismatch-triage/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **推翻 `docs/ROADMAP.md:199` 的「16 处全部是『实参 = 反射 − 1』」** —— 实测**只有 10 条**是 −1。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 16 条逐条导出 | `output/_probe253_arity_sites.txt` | ✅ **16** 条 |
| FR-002 | 归入封闭词表且与差值自洽 | `test_every_arity_site_is_triaged` | ✅ 问题数 **0** |
| FR-003 | ★★★ 推翻旧结论（−1 只有 10 条） | `test_old_claim_all_minus_one_is_falsified` | ✅ `byref-tail` = **10** ≠ 16 |
| FR-004 | 桶条数下界 | `test_bucket_sizes` | ✅ 3 / 10 / 2 / 1 · 合计 **16** |
| FR-005 | ★★ 真机证据留在判据里 | `test_machine_evidence_whatswrong_three_byref_works` | ✅ 3 参 OK · 2 参 FAIL · 0 参 FAIL |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |
| FR-007 | 不改 `scripts/` / 门禁 | mtime 核（§四） | ✅ 全部早于开工时刻 |

---

## 二、★★★ 分桶结果（★ 与旧结论的对照）

| 桶 | 条数 | 定性 | 依据 |
|---|---|---|---|
| **`starargs-false-positive`** | **3** | ★ **假阳性** | 封装是 `def f(obj, *args)` + **自校验** `if len(args) != N: raise`（`sw_routing.py:196-198` · `sw_simulation_study.py:393-394`） |
| **`byref-tail-convention`** | **10** | ★ 约定问题 | 反射末位 `Int32&`（`ErrorCode`）+ 表声明 `byref=excluded` |
| **`real-arity-gap`** | **2** | ★★ **真缺口** | `GetNodeLocation(Int32, Double&, Double&, Double&)` —— 三个 by-ref 出参**一个都没传**；docstring **自认**「取不到坐标，只透传」 |
| **`all-byref-false-positive`** | **1** | ★★ **假阳性** | `GetWhatsWrong(Object&, Object&, Object&)` —— 形参**全是** by-ref ⇒ `counted_positions` 剥光 ⇒ 计数 0 ≠ 3 |

⇒ ★★ **旧结论只对 `byref-tail` 那一桶（10 条）成立**；★ 另外 **6 条**：**4 条假阳性 + 2 条真缺口**。

---

## 三、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常表 | 0 条 | ✅ **`0`** |
| 把 `real-gap`（差 −3）改判成 `byref-tail` | 报错 | ✅ 判出（★ 桶与差值不自洽） |
| **全部 16 条都判成 `byref-tail`** | 条数 = 16 = 旧断言 ⇒ **红** | ✅ **`n = 16` ⇒ `assert n != 16` 失败** |
| 桶码不在封闭词表（如「待定」） | 报错 | ✅ 判出 |

---

## 四、★ 未改动证明（★ 用 mtime）

| 文件 | mtime | 早于 23:56？ |
|---|---|---|
| `scripts/check_dispatch_byref_guard.py` | `10-09 10:40` | ✅ |
| `scripts/sw_routing.py` | `10-09 09:28` | ✅ |
| `scripts/sw_simulation_study.py` | `10-09 09:28` | ✅ |

★ **本切片改过**：`tests/test_arity_mismatch_triage.py`（新）· `output/_probe253_arity_sites.py` / `.txt` ·
`output/_probe253_whatswrong.py` / `.txt` · `output/_probe253_cleanup.py` · `specs/253-*/`（新）·
`docs/ROADMAP.md` · `.workbuddy-ai/memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` · `.specify/feature.json`。
★ **新建**：`tools/goal_gate.py`（★ Stop hook 判定器）· `.codebuddy/settings.json`（★ Stop hook 配置）· `output/GOAL.md`。

---

## 五、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

---

## 六、★★★ 真机只读复核（★ 唯一的行为证据）

★ 走护栏（预检「读到文档 **0** 个」）· SW **rev 34.4.1** · ★ 临时零件**用完关闭且未保存**（★ 事后护栏再扫：**0 个弹窗**）。

| 写法 | 结果 |
|---|---|
| **3 个 by-ref VARIANT**（★ 真树就是这种） | ★★ **OK**（`ret=True`） |
| 2 个 by-ref VARIANT | **FAIL** `com_error(-2147352561, '非选择性的参数。')` |
| 0 实参 | **FAIL** 同上 |

⇒ ★★★ **真树那种写法能调通** ⇒ ★ `all-byref` 桶确系**假阳性**。

★ **踩的坑**：★ 第一版探针的关闭调用写成 `sw.CloseDoc(doc.GetTitle())` —— ★ `GetTitle` 是**属性**不是方法
⇒ `TypeError: 'str' object is not callable` ⇒ **临时零件没关掉**。★ 事后护栏预检确认**已无打开文档**（0 个）。

---

## 七、★★★ 本轮**额外发现**：门禁的**每日跨天假红**

★ 本切片首跑门禁时 **`EXIT=1`**：`[FAIL] 规范与地图存在性 · docs/union-level-audit.md 与最新数据不一致`。

★ **根因**（已实测）：`scripts/check_union_conventions.py` 的 **R8** 做的是
**逐字节比对**「重新生成的内容」与「磁盘上的文件」（`want != audit.read_text()`）；
★ 而 `gen_level_audit.build()` 会写进 `生成日期：<today>` ⇒ ★★ **跨过午夜后，即使数据零变化，
文件也必然"不一致"** ⇒ **每天一次假红**。

★ **实测证据**：重生成后的 diff **只有 2 行**（`<`/`>` 各 1），且只差日期：
```
< > 生成日期：2026-10-09 ｜ 数据源：`capabilities.yaml`
> > 生成日期：2026-10-10 ｜ 数据源：`capabilities.yaml`
```
★ 内容（140 条能力 · level 分布 · source 分布）**完全一致**。

★★ **定则**：★ **「逐字节比对生成物」的判据，必须先把「非数据字段」（时间戳/日期）归一化**，
★ 否则它把「日期变了」误判成「数据变了」。
★ 与 248/249/250 的「口径错了结论就反」**同族**，但这是**门禁本体**的问题。

★ **处置**：★ **本轮只重生成、不改门禁**（★ 改门禁本体 = 独立一件工作，★ 要重跑生成器链 + 复核 8 段检查）。

---

## 八、未过门（如实登记）

1. **门禁的口径缺陷未修** —— ★ `counted_positions` 会剥掉**全 by-ref** 形参 ⇒ 4 条假阳性；
   ★ 改它要动**门禁本体** + 重跑生成器链 ⇒ **独立一件工作**。
2. **`real-gap` 两处未修**（`GetNodeLocation` / `GetElementLocation`）—— ★ 需先有 **by-ref 取坐标的写法**。
3. **10 条 `byref-tail` 的真机验证** —— ★ 需活的研究对象（cosworks）/ PDM 表；★ 本轮**只证了 1 条**（`GetWhatsWrong`）。
4. **223 的 8 条 `HEAD` 即红既有失败未修**；**未提交 / 未部署**。
5. **未删任何文件**；★ 未 create 或 update 除「SW 施工 · 跨会话持续（每小时）」以外的任何自动任务。
6. ★★ **门禁 R8 的「每日跨天假红」未修** —— ★ 见 §七；★ 改 `check_union_conventions.py` = **独立一件工作**。
