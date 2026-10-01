# Implementation Plan: B-Rep 证据绑定闭环

**Feature**: `005-brep-evidence-binding` · **Spec**: [spec.md](spec.md)

**Created**: 2026-10-01 · **Status**: Implemented

---

## 一、与既有实现的关系（**不重造**）

**零新增实现**：契约**早已存在**于 `scripts/dfm_review.py`
（`_load_brep_evidence` L284-365 / `_brep_size` L260-281 / `_sha256_file`）。
本特性**只改验收命令** `tools/verify_dfm_e2e.py` 的 SC-004 段。

---

## 二、步骤（**先读契约，再改判据**）

### 阶段 0 · 读契约（**不猜**）
* `Select-String scripts/dfm_review.py -Pattern 'brep_evidence|_brep_size'` 定位；
* 逐行读 `_load_brep_evidence` 的**每一条 `raise`** —— 那些 `raise` **就是契约**；
* 读 `_brep_size` 拿到包络字段名。

### 阶段 1 · 探针验证（**先探再改**）
`D:\AI\SW\probe_brep_evidence.py`：① 不给证据 ② 给"我认为对"的证据 ③ 篡改哈希 ④ 篡改产物。
⇒ 实测暴露了两层：**③④ 本来就成立**（实现是对的），**② 失败**（我的形态错）——
再顺 `ValueError: 缺少有效的三轴包络` 追到 `_brep_size` 的字段名。

### 阶段 2 · 改验收命令（SC-004 → 三条）
把原来那条「给证据时不崩」（**弱判据**）换成 **SC-004a/b/c** 三条**强判据**，
并把契约写进注释（SC-105：让下一个人不必再猜）。

### 阶段 3 · 复跑 + 证据
`python tools/verify_dfm_e2e.py` ⇒ **13/13 · verdict: pass**；
证据落 `D:\AI\SW\output\dfm-evidence.json`。

### 阶段 4 · 收工
十二道硬门禁 · 全量回归 · 两仓库 commit。

---

## 三、风险与对策

| 风险 | 对策 |
|---|---|
| 又一次"按自己的理解造形态"（004 的错因）| **先读每一条 `raise`**，再用探针**实测**，最后才写判据 |
| 把「弱判据」留在验收里充数 | SC-004 原判据（"不崩"）**删除**，换成三条强判据；**不留弱判据凑数** |
| 误以为"实现有 bug"而去改 `dfm_review.py` | 探针 ③④ 先证明**实现是对的**（篡改本就被拒）⇒ **只改判据** |

---

## 四、产物

| 文件 | 变化 |
|---|---|
| `tools/verify_dfm_e2e.py` | SC-004 段重写（8 → 13 项判据）|
| `D:\AI\SW\output\dfm-evidence.json` | 证据刷新 |
| `D:\AI\SW\probe_brep_evidence.py` | 探针（保留，供下一个人复核契约）|
