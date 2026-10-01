# Converge: B-Rep 证据绑定闭环

**Feature**: `005-brep-evidence-binding` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 80）· **环境**: Python 3.14.7（**纯离线**）

> **这一步做什么**：把 `spec.md` 的每条验收判据**与实测证据逐条对齐**，并**明确记下不符合项**。
> **不是复述 spec** —— 复述没有价值，找出「声称」与「实际」的差才有。

---

## 一、结论摘要

| 判据 | 结论 | 依据（可复跑的枚举命令） |
|---|---|---|
| SC-101 合法 OCCT 证据被接受 | ✅ 成立 | `python tools/verify_dfm_e2e.py`（`available=True` · `verifiedSource=True` · `backend='headless_occt'`）|
| SC-102 篡改 `sourceSha256` ⇒ 被拒 | ✅ 成立 | 同上（`error_code='dfm_invalid_brep_evidence'`，message 含「**SHA-256 不匹配，证据已失去绑定**」）|
| SC-103 篡改产物内容 ⇒ 被拒 | ✅ 成立 | 同上（改文件后真实哈希变 ⇒ 同样 `dfm_invalid_brep_evidence`）|
| SC-104 004 的其余判据不退化 | ✅ 成立 | 同上（**13/13 · `verdict: pass`**，004 时是 11/11）|
| SC-105 契约写进代码注释 | ✅ 成立 | `Select-String tools/verify_dfm_e2e.py -Pattern 'envelope_mm'` |

**总判定**：**13/13 项通过 · `verdict: pass`**（`D:\AI\SW\output\dfm-evidence.json`）。

---

## 二、**不符合项**（本节才是 converge 的价值所在）

### 2.1 ~~⚠ `bounds` 在「合法 B-Rep 证据」那条里仍然是 `None`~~ ⇒ ✅ **已查证：不是 bug，是我看错了字段**

> **✅ 2026-10-01 轮 81 查证结论**：
> ```
> ① 报告顶层**根本没有** `bounds` 字段
>    （24 个顶层字段逐个数过：artifacts / brepEvidence / checks / … / units）
> ② 它的产物在 **`checks.bounds_available`** 里，**且带着值**：
>    {"id":"bounds_available","status":"pass","severity":"medium",
>     "message":"已提取基础包络尺寸。",
>     "bounds":{"available":true,"min":[-60.0,-35.0,-4.0],"max":[...]}}
> ③ `_bounds()` 是模块内函数，被 `_common_checks` 调用 ⇒ **设计如此**
> ```
> ⇒ **`r.get("bounds")` 返回 `None` 是因为**这个键不存在**，不是"值算错了"。
> **我上一轮的「怀疑时序 bug」是误判。**
> ⇒ 本轮在验收命令里**加了一条判据**（SC-106）防止同类误判再发生：
> **断言 `bounds_available` 在 `checks` 里、且带非空 `bounds`**。
> ★ **教训：怀疑某个字段"值不对"之前，先确认**这个字段存不存在**** ——
>   `dict.get(k)` 对不存在的键**静默返回 `None`**，看起来就像"值是空的"。
>
> **原文保留在下面**（误判的记录也有价值：它说明"不查证就写怀疑"会留下什么）。

⚠ 上一轮记的原文：实测给了**被接受**的 B-Rep 证据（`verifiedSource=True`）后，
报告的 `bounds` 仍是 **`None`** ⇒ **当时怀疑** `_bounds(document, brep_evidence)` 的调用点
没把已解析的证据传进去（`build_dfm_report` 里的时序）。**—— 该怀疑已被上面推翻。**

⚠ 但 —— **本轮不做结论**：
* 本特性的判据是「**篡改必被拒**」（SC-101..103），那三条**已成立**；
* `bounds` 的取值属于**另一件事**（包络回读），**不在本特性的判据里**；
* 而**要判定"是不是 bug"**，需要先读 `build_dfm_report` 的调用时序 —— **本轮没读**。
⇒ **如实记为「未查证」**（铁律 5），**不写成 bug，也不放过**。

**下一步怎么做**：读 `build_dfm_report`（L858-1000）里 `_bounds` 与 `brep` 的先后，
必要时开 `006`。

### 2.2 ✓ 被门禁抓到一次：探针**不在仓库里**
`tasks.md` 里我先写了 `python D:\AI\SW\probe_brep_evidence.py` ⇒
`check_spec_acceptance_paths` **精确命中**：
```
· [outside-repo] D:\AI\SW\probe_brep_evidence.py —— 绝对路径且不在仓库根下
  ⇒ **只在写它的那台机器上有**
修法：把脚本按仓库规范收进 `tools/`，或改写成仓库内的等价命令。
```
⇒ 按修法**收进 `tools/probe_brep_evidence_contract.py`**（补来源块、保持只读），
`tasks.md` 的路径同步改为仓库内 ⇒ 门禁 `[PASS]`。
★ **那正是该门禁的设计意图**：把「只在我机器上能跑的路径」变成「仓库内可达」。

### 2.3 ✓ 一次**弱判据**被换成强判据
004 的 SC-004 原文是「给 B-Rep 证据时**报告仍成立（不崩）**」—— 那是个**弱判据**
（"不崩"几乎必然成立，且它当时连 `available` 都没看）。
⇒ 本特性**删掉它**，换成 SC-004a/b/c 三条**强判据**（接受 / 篡改哈希拒 / 篡改产物拒）。
★ **教训：验收里不留"必然成立"的弱判据充数** —— 它会让人以为那件事验过了。

---

## 三、与 `tasks.md` 的对账

**T-101..T-111 全部完成**（`[x]`）。关键事实：
* T-104/T-105 的探针**先证明了两件事**：**实现本来就是对的**（篡改本就被拒），
  以及**我的形态是错的**（缺 `backend`/`producedThisRun`/`sourceArtifact`/`envelope_mm`）；
  ⇒ 因此**只改判据，不动 `dfm_review.py`**（`spec.md §三` 的约定）；
* T-107 把契约**写进注释** —— 下一个人不必再读 80 行实现去猜五个必填项。

---

## 四、对 `004` 的闭环

`specs/004-dfm-verified/converge.md §2.1` 记的那条**不符合项**（SC-004 未达成）
**已由本特性还清** ⇒ 已在 004 的 converge 里加**指向本特性的注记**（不删原文）。

---

## 五、复跑全部命令

```powershell
cd C:\swprojects\sw-skill-fork
python tools/verify_dfm_e2e.py                                  # 13/13 · verdict: pass
python tools/probe_brep_evidence_contract.py                    # 契约对照实验（四组）
python -m pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py -q   # 19 passed
python scripts/check_spec_acceptance_paths.py                   # exit 0（77 处 → 验收 行全可达）
python scripts/check_union_conventions.py                       # exit 0
python -m pytest tests -q                                       # 970 passed / 17 skipped / 0 failed
python scripts/release_check.py                                 # exit 0
```
