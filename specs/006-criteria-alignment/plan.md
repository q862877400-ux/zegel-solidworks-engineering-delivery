# Implementation Plan: 交付报告的判据编号与 `AGENTS.md §一` 对齐

**Feature**: `006-criteria-alignment` · **Spec**: [spec.md](spec.md)

**Created**: 2026-10-01 · **Status**: Implemented

---

## 一、与既有实现的关系（**不重造**）

**零新增能力实现**。本特性只动三处：
1. `docs/harvest-report.md §四` —— **重写那一节的表**（10 行，逐条对齐）；
2. `scripts/check_report_criteria_alignment.py` —— **新增元门禁**（编号一致性）；
3. `scripts/check_report_freshness.py` —— **加固**（把一处假绿 SKIP 改成 FAIL）。

⚠ 第 3 项**不是本特性最初的范围** —— 它是**修 §四 时撞见的**（见 `spec.md §二`），
按本项目纪律「撞见的真缺陷就该当场记下并按需修」，**并入本特性**而不是另开一个。

---

## 二、步骤

### 阶段 0 · 对照两套编号（**先查证**）
`Select-String AGENTS.md -Pattern '^\| A\d+ \|'` 拿权威表；
再解析报告 §四 的表 ⇒ **逐行对照** ⇒ 得出 `spec.md` 那张错位表。
⚠ 关键：**不能假定是"整体偏移一位"** —— 实测发现**不是**
（报告 A4「目录结构与上游一致」在 `AGENTS.md` 里**根本没有**对应判据，那是铁律 3）。

### 阶段 1 · 写门禁（**先证明它有牙齿**）
`scripts/check_report_criteria_alignment.py`：
* 从 `AGENTS.md §一` 抽 `A\d+` 集合（**限定在 §一 那节**，避免把别的节的 A 编号算进来）；
* 从报告的自评表抽编号集合 + **列出非 `A\d+` 的编号行**；
* **两者必须相同**，且非 A 编号行为空。
⚠ **跑现状应先红**（缺 A1/A9/A10 + 混入「官方 API 覆盖」）
—— **那才是"有牙齿"的证明**（本项目已知事实 62：负例是唯一的证明）。

### 阶段 2 · 重写 §四
10 行，每行的**自评必须带可复跑的依据**（跑门禁 / 查清单 / 读报告别的节），
**不编**。⚠ 每行原先的编号**不沿用**（那正是错源）。

### 阶段 3 · 接线（**两层，缺一不可**）
* `release_check.py` 里**调用**它（否则就是「存在但没人跑」——已知事实 40）；
* `docs/gate-classification.json` 里**登记** `hard`（元门禁要求登记表覆盖每个调用点）；
* 结果**进 `_gate_results`**（否则「它跳过了」在外面看不见 —— 第 4 种面孔）。

### 阶段 4 · 加固 `check_report_freshness`
把「报告在、但那行读不出来」从 **SKIP** 改成 **FAIL**，保留「报告不存在 ⇒ SKIP」（便携性）。

### 阶段 5 · 收工
十三道硬门禁 · 全量回归 · 两仓库 commit。

---

## 三、风险与对策

| 风险 | 对策 |
|---|---|
| **判据臆造**（本项目已多次：判据的关键词/正则不贴合实际）| 门禁第一版**漏了粗体** `\| **A1** \|` ⇒ 当场被现状输出暴露；改成容忍 `\*{0,2}` |
| 写报告数字时**把行写坏** | 加固脚本对「修法行为空」**直接退出**（不写空值）—— 那正是本轮踩到的坑 |
| 改门禁后**旧 SKIP 白名单过期** | 改完立刻跑 `check_gate_wiring.py`（它管 skipped 分支白名单）|
| 又一次"门禁写了没接线" | 阶段 3 的两层 + 元门禁自己会报 |

---

## 四、产物

| 文件 | 变化 |
|---|---|
| `docs/harvest-report.md` | §四 重写（15 行 → 24 行，10 条逐条对齐）|
| `scripts/check_report_criteria_alignment.py` | **新增**（元门禁）|
| `scripts/check_report_freshness.py` | 加固（SKIP → FAIL 那一处）|
| `scripts/release_check.py` | 接线 + 结果进汇总 |
| `docs/gate-classification.json` | 登记第 14 条（`hard`）|
