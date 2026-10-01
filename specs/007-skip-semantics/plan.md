# Implementation Plan: 门禁 SKIP 的语义

**Feature**: `007-skip-semantics` · **Spec**: [spec.md](spec.md)

**Created**: 2026-10-01 · **Status**: Implemented

---

## 一、与既有实现的关系（**不重造**）

**零新增门禁**。本特性只：
1. **蒐集 + 分类**（写成一个可复跑的探针 `tools/probe_skip_semantics.py`）；
2. **修两处**同型缺陷（`check_signature_audit_freshness.py` / `check_workspace_shadowing.py`）。

⚠ **不新增第 15 道门禁** —— 那是「**为了修房子创建公司**」。
判据已经存在（`SKIP` 语义），只是**两处用错了**。

---

## 二、步骤

### 阶段 0 · 蒐集（**不靠印象**）
扫 `scripts/check_*.py` 全部 `SKIP` 点 ⇒ 11 个脚本 / 15 处。
⚠ 只蒐集**打印 SKIP 的地方**，因为那是**唯一的跳过出口**。

### 阶段 1 · 分类（**一条判据**）
> **被读的那个东西，是本仓库自己的产物，还是本机/外部才有的数据源？**
* 外部 ⇒ SKIP 正确；本仓库产物 ⇒ 「读不出」= 坏了 ⇒ FAIL。

⚠ 分类时**必须读源码看 `--doc` / `SERVER` 这类常量的**来源**（`ROOT / …` = 仓库内，
`RAW` / `TYPES` = 仓库外）—— **不靠名字猜**。

### 阶段 2 · 修（**照轮 82 的形状**）
两处都用**同一形状**：
```
if 东西不存在:            ⇒ SKIP（便携性）
elif 东西在但读不出:       ⇒ FAIL（产物坏了）
```
* `check_signature_audit_freshness`：`Path(a.doc).is_file()`
* `check_workspace_shadowing`：`SERVER.parent.is_dir()`（`mcp-server/` 在 = 这是本仓库）

### 阶段 2b · 修第三处（**实测撞见**）
写 `007/tasks.md` 时用了合法但**带 glob** 的验收命令 ⇒ `check_spec_acceptance_paths` **误报**
⇒ 修它的 ② 分支（含 glob 元字符则 `repo.glob()` 展开，≥1 匹配即通过；0 匹配报 `glob-no-match`）。
★ 与它自己记过的轮 53 假阳性**同族**。

### 阶段 3 · 负例证明（**两边都测**）
每处修完**测两个方向**：
* **正例**（真输入）⇒ exit 0；
* **负例 A**（产物在、内容坏）⇒ **exit 1**；
* **负例 B**（产物不存在）⇒ **仍 exit 0 SKIP**（便携性未受损）。
⚠ 遮蔽门禁的负例要用**假仓库**（`tempfile` 里造 `mcp-server/` 有无两种），
因为它的 `ROOT` 由 `__file__` 推出、**不能靠参数改**。

### 阶段 4 · 收工
元门禁（SKIP 白名单是否被改坏）· 13 道门禁 · 全量回归 · 两仓库 commit。

---

## 三、风险与对策

| 风险 | 对策 |
|---|---|
| 把「外部数据源」误判成「产物」⇒ 别的机器上无条件红 | 分类时**读常量的来源**；修完**都测便携性那一边** |
| 修完**元门禁的红**（SKIP 白名单过期）| 立刻跑 `check_gate_wiring.py`（轮 82 已见它尽职）|
| 探针入库后**没带来源块**（`check_provenance` 会红）| 写的时候就带（轮 76 的教训）|
| 探针写成**本机绝对路径**（轮 80 被门禁抓过）| 入库版用仓库内相对路径 |

---

## 四、产物

| 文件 | 变化 |
|---|---|
| `tools/probe_skip_semantics.py` | **新增**（蒐集 + 分类 + 实测，可复跑）|
| `scripts/check_signature_audit_freshness.py` | 修（1 处 SKIP → 分两种情况）|
| `scripts/check_workspace_shadowing.py` | 修（1 处 SKIP → 分两种情况）|
