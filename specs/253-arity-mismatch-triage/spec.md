# Spec — 16 条「arity 不符」的**分桶定罪**（★ 推翻「全部是『实参 = 反射 − 1』」）

**Feature**: `specs/253-arity-mismatch-triage/`
**日期**: 2026-10-09
**上游**: `docs/ROADMAP.md:199` 的旧结论 + `scripts/check_dispatch_byref_guard.py`（★ 只计数、不列明细）
**本轮只做一件事**：把门禁那句「**arity 不符 16**」**逐条导出并定罪**。

---

## 一、背景（旧结论）

`docs/ROADMAP.md:199` 逐字写着：

> **arity 不符 16 处**全部是「实参 = 反射计数 − 1」，且其内联签名表**自己写着**「不含末尾 by-ref `ErrorCode`」
> ⇒ ★ **这是约定问题、不是缺陷** ⇒ 只登记不判罪。

★★★ **本轮实测：那句话是错的。** 16 条里**只有 10 条**是 −1。

---

## 二、★★★ 实测（`output/_probe253_arity_sites.py`，★ 口径 **import** 自门禁）

| # | 站点 | 成员 | 实参 | 反射 | 差 | ★ 桶 |
|---|---|---|---|---|---|---|
| 1 | `sw_feature_readback.py:133` | `GetWhatsWrong` | 3 | 3 | **0** | ★ **全 by-ref 假阳性** |
| 2 | `sw_pdm.py:275` | `GetBOMStartNumber` | 0 | 1 | −1 | 末尾 by-ref 约定 |
| 3 | `sw_routing.py:200` | `CreateFlattenRoute` | 1 | 11 | **−10** | ★ **`*args` 假阳性** |
| 4 | `sw_routing.py:208` | `CreatePipeDrawingforPipeRoute` | 1 | 12 | **−11** | ★ **`*args` 假阳性** |
| 5 | `sw_simulation_results.py:179` | `CreatePlot` | 4 | 5 | −1 | 末尾 by-ref 约定 |
| 6 | `sw_simulation_results.py:185` | `CreateDeformedBody` | 2 | 3 | −1 | 末尾 by-ref 约定 |
| 7 | `sw_simulation_results.py:216` | `GetDisplacementAtPoints` | 5 | 6 | −1 | 末尾 by-ref 约定 |
| 8 | `sw_simulation_results.py:222` | `GetBucklingLoadFactors` | 0 | 1 | −1 | 末尾 by-ref 约定 |
| 9 | `sw_simulation_results.py:246` | `GetNodeLocation` | 1 | 4 | **−3** | ★★ **真缺口** |
| 10 | `sw_simulation_results.py:251` | `GetElementLocation` | 1 | 4 | **−3** | ★★ **真缺口** |
| 11 | `sw_simulation_study.py:231` | `CreateNewStudy` | 3 | 4 | −1 | 末尾 by-ref 约定 |
| 12 | `sw_simulation_study.py:237` | `CreateNewStudy2` | 2 | 3 | −1 | 末尾 by-ref 约定 |
| 13 | `sw_simulation_study.py:243` | `CreateNewStudy3` | 3 | 4 | −1 | 末尾 by-ref 约定 |
| 14 | `sw_simulation_study.py:261` | `DuplicateStudy` | 4 | 5 | −1 | 末尾 by-ref 约定 |
| 15 | `sw_simulation_study.py:274` | `ConvertStudy` | 6 | 7 | −1 | 末尾 by-ref 约定 |
| 16 | `sw_simulation_study.py:395` | `ExportSimulationStudy` | 1 | 7 | **−6** | ★ **`*args` 假阳性** |

⇒ ★ **桶的分布：`byref-tail` 10 · `starargs` 3 · `real-gap` 2 · `all-byref` 1**。

### 四个桶的定性（★ 每条都有源码/真机依据）

| 桶 | 条数 | 依据 |
|---|---|---|
| **`starargs-false-positive`** | **3** | ★ 三个封装是 `def f(obj, *args)`，**自己**校验 `if len(args) != N: raise ValueError`（★ 逐字见 `sw_routing.py:196-198` / `sw_simulation_study.py:393-394`）⇒ ★ 门禁只数到 1 个非 Starred 实参 ⇒ **假阳性** |
| **`byref-tail-convention`** | **10** | ★ 反射签名末位是 `Int32&`（`ErrorCode`），★ 内联表声明 `byref=excluded` ⇒ ★ **约定问题**（★ 旧结论只对这一桶成立） |
| **`real-arity-gap`** | **2** | ★★ `GetNodeLocation(Int32, Double&, Double&, Double&)` 三个 by-ref 出参**一个都没传**；★ docstring **自认**「官方是 by-ref 出参，本封装**取不到坐标**，只透传」⇒ ★ **已知功能缺口** |
| **`all-byref-false-positive`** | **1** | ★★ `GetWhatsWrong(Object&, Object&, Object&)` **三个形参全是 by-ref** ⇒ 门禁的 `counted_positions` 把它们**全剥掉** ⇒ 计数 0 ≠ 3 ⇒ 判 `arity`；★ **真机证明能调通** |

---

## 三、★★★ 真机只读复核（`output/_probe253_whatswrong.py`）

★ 走护栏（预检「读到文档 0 个」）· SW **rev 34.4.1** · ★ 开一个临时零件，**用完关闭且不保存**。

| 写法 | 结果 |
|---|---|
| **3 个 by-ref VARIANT**（★ 真树就是这种） | ★★ **OK**（`ret=True`） |
| 2 个 by-ref VARIANT | **FAIL** `com_error(-2147352561, '非选择性的参数。')` |
| 0 实参 | **FAIL** 同上 |

⇒ ★★★ **真树那种写法能调通** ⇒ ★ `all-byref` 桶确系**假阳性**（★ 这是该桶判定的**唯一证据**）。

---

## 四、需求

### FR-001 16 条必须逐条导出（★ 门禁只计数、不列明细）

- **来源**：`scripts/check_dispatch_byref_guard.py`（★ `arity` 桶「只计数、不判罪」）。
- **规则**：探针必须把 16 条逐条列出（文件 · 行号 · 成员 · 实参 · 反射 · 转发入口）。
- **验收场景**：`output/_probe253_arity_sites.txt` 含 **16** 条。

### FR-002 ★★ 每条必须归入**封闭词表**里的一个桶，且**桶与差值自洽**

- **来源**：本仓铁律（「分类不是判据 —— 必须接进一条判据」）。
- **规则**：桶 ∈ {`starargs` · `byref-tail` · `real-gap` · `all-byref`}；
  ★ 且 `byref-tail` ⇒ 差 **−1** · `real-gap` ⇒ 差 **≤ −3** · `all-byref` ⇒ 差 **0**。
- **验收场景**：`test_every_arity_site_is_triaged` 通过。

### FR-003 ★★★ 推翻旧结论：**−1 的只有 10 条**

- **来源**：`docs/ROADMAP.md:199` 的「16 处**全部**是 −1」。
- **规则**：`byref-tail` 桶的条数 **≥10 且 ≠ 16**（★ 等于 16 就说明旧结论居然对了，必须复核）。
- **验收场景**：`test_old_claim_all_minus_one_is_falsified` 通过；
  ★★ **能红的判据**：把任意一条非 −1 的改判成 `byref-tail` ⇒ 当场红。

### FR-004 桶的条数下界

- **来源**：本项目纪律（「可见性边界必须被量出来并冻结下界」）。
- **规则**：`starargs ≥3` · `byref-tail ≥10` · `real-gap ≥2` · `all-byref ≥1` · 总数 **16**。
- **验收场景**：`test_bucket_sizes` 通过。

### FR-005 ★★ 真机证据必须留在判据里

- **来源**：本仓纪律（「声明要能被证据判定」）。
- **规则**：`MACHINE_WHATSWRONG` 必须写明「3 参 OK / 2 参 FAIL / 0 参 FAIL」。
- **验收场景**：`test_machine_evidence_whatswrong_three_byref_works` 通过。

### FR-006 ★★ 判据必须能红

- **来源**：本仓铁律。
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 三组负例）。

### FR-007 ★ 不改 `scripts/`、不改门禁

- **来源**：本项目纪律（★ 本轮只**定罪**，★ **不修**门禁的口径）。
- **验收场景**：`scripts/check_dispatch_byref_guard.py` mtime 未变。

---

## 五、非目标

- **不**改 `check_dispatch_byref_guard.py` 的口径 —— ★ 那要动门禁本体 + 重跑生成器链（★ **独立一件工作**）。
- **不**修 `real-gap` 两处 —— ★ 它们要**先有 by-ref 取坐标的写法**（★ 独立一件工作）。
- **不**动 cosworks/PDM 的真机调用（★ 需活的研究对象/PDM 库）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 翻 `real-gap` ⇒ 报错；全判 −1 ⇒ 条数 16 = 旧断言 ⇒ 红 |
| SC-2 | 判据**是绿的** | `tests/test_arity_mismatch_triage.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机只读 | 护栏预检「读到文档 0 个」；★ 临时零件**已关闭且未保存** |
| SC-5 | 未改 `scripts/` | mtime 核 |

## 七、未过门（本轮不做，如实登记）

- **门禁的口径缺陷未修**（★ `counted_positions` 会剥掉全 by-ref 形参 ⇒ 假阳性 4 条）——
  ★ 改它要动门禁本体，**独立一件工作**。
- **`real-gap` 两处未修**（`GetNodeLocation` / `GetElementLocation`）—— ★ 需先有 by-ref 取坐标的写法。
- **10 条 `byref-tail` 的真机验证** —— ★ 需活的研究对象（cosworks）/ PDM 表；★ 本轮**只证了 1 条**（`GetWhatsWrong`）。
- 真机未验的其他项；223 的 8 条既有红未修；未提交未部署。
