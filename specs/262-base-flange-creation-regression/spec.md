# Spec — **造钣金件失败**：`create_base_flange` 本机建不出来（★ 与 261 无关，已静态排除）

**Feature**: `specs/262-base-flange-creation-regression/`
**日期**: 2026-10-10
**上游**: `specs/261-routing-batch1-adapt-args/` 的未过门 1（★「`_read_k_factor` 未被真机走到」）
**本轮只做一件事**：查**为什么造不出 `BaseFlange`**。

---

## 一、★★★ 真机读数（★ 用**仓里维护好的**配方）

★ 走护栏 · SW rev **34.4.1** · 跑 `tests/solidworks_sheet_metal_regression.py --output-dir output/fixtures/_probe262`：

```json
{ "status": "failed",
  "error": "CreateFeature(IBaseFlangeFeatureData) 创建失败" }
```

★★★ **关键**：★ 这个脚本是**仓里维护的**配方（mtime `10-03 07:17`，★ 不是我临时写的）⇒ ★ **它也失败**
⇒ ★★ **不是探针写错，是 `create_base_flange` 本身建不出来**。

★★ **而且这是**回归**：★ `docs/known-facts.md` **事实 34**（**2026-10-01**）逐字记它**成功**：

> ✓ `create_base_flange`（真建出特征：特征树出现「**钣金6 / 基体-法兰1 / 平展型式6**」）

⇒ ★ **2026-10-01 成功 · 2026-10-10 失败** ⇒ ★★ **回归**。

---

## 二、★★★ 静态排除：**不是 261 引起的**

★ 我第一反应是「是不是我上一轮改坏的」⇒ ★ **静态排除**：

| 261 改了什么 | 在 `create_base_flange` 里吗 |
|---|---|
| 新增 `_read_k_factor`（★ **读**路径，在 `sheet_metal_evidence` 里调用） | ★ **不在** |
| 替换 `float(get_com_member(definition, "KFactor") or 0.0)`（★ **读**） | ★ **不在** |
| — | ★ `create_base_flange` 用的是 **`bend_allowance.KFactor = float(spec.k_factor)`**（★ **写**路径） |

⇒ ★★ **261 只碰了「读」，而 `create_base_flange` 走「写」** ⇒ ★ **嫌疑排除**。
★ 判据 `test_261_did_not_touch_create_base_flange` **钉住这条排除**（★ 免得下一个人先去怀疑 261）。

---

## 三、★★ 一条方法论教训：**`git diff HEAD` 不能用来核「我这轮改了什么」**

★ 我一开始想用 `git diff HEAD -- scripts/sw_sheet_metal.py` 看 261 改了什么 ⇒ ★ 它回了 **120 增 / 26 删**，
★ 里面**混着大量我没做的改动**（`import math`、规格 239 的 `create_draft` 条目…）。
★★ 因为**本仓工作树是「已 staged 的整树基线」** ⇒ ★ `git diff HEAD` 给的是**整树差异**，★ 不是本轮差异。
⇒ ★★ **定则：核「本轮改了什么」要看「我自己的编辑动作」，或用 `find -newermt`**。

---

## 四、需求

### FR-001 ★★★ 真机失败必须如实记录（★ 且标为**回归**）
- **规则**：`status = failed` · `error` 含 `CreateFeature` · ★ `regression = True`。
- **验收场景**：`test_machine_failure_is_recorded` 通过。

### FR-002 ★★★ 静态排除 261
- **规则**：`create_base_flange` 的函数体里**不许**出现 `_read_k_factor` 或旧读法；
  ★ 且**必须**有写路径 `bend_allowance.KFactor = float(spec.k_factor)`。
- **验收场景**：`test_261_did_not_touch_create_base_flange` 通过。

### FR-003 ★★ 阻塞链必须写清
- **规则**：★ `_read_k_factor` 验不了的**真因**是「**造不出 `BaseFlange`**」，
  ★ **不是**「没有夹具零件」—— ★ 两者在**只看结论**时同形。
- **验收场景**：`test_blocking_chain_is_explicit` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 五、非目标

- **不**修 `create_base_flange`（★ 需真机逐层探：属性层 / 预选 / `CreateFeature` 各查一遍 ⇒ **另开切片**）。
- **不**改 `scripts/` ⇒ ★ **不跑生成器链**。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 状态改 ok / 失败点改掉 / 混入 261 的函数 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_base_flange_creation_regression.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机 | 护栏预检「读到文档 0 个」· ★ 文档已关闭 |

## 七、未过门（本轮不做，如实登记）

- **`create_base_flange` 未修** —— ★ 要真机逐层探（★ 属性层 8/8 已过、预选、`CreateFeature` 回 None 的**错误码**）。
- **`_read_k_factor` 仍未被真机走到** —— ★ **但阻塞原因已查明**（★ 造不出件）。
- 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
