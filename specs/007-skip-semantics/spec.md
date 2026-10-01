# Feature Specification: 门禁 SKIP 的语义 —— 「数据源不可用」vs「输入坏了」

**Feature Branch**: `007-skip-semantics`

**Created**: 2026-10-01 · **Status**: Implemented

**Input**: 轮 82 修掉一个**假绿**（`check_report_freshness`：产物那行读不出 ⇒ 曾 `SKIP` ⇒ 全绿），
并在 `converge.md §2.1` 如实记下「**仓库里别的门禁是否也这样，本轮没逐条查**」。
本特性就是**去查**，并把结论**变成规则 + 修掉同型缺陷**。

---

## 背景：这为什么是**高危**缺口

一个门禁 `SKIP` 时**退出码是 0** ⇒ 它`跳过`和它`通过`**在调用方看来一模一样**。
若 `SKIP` 的触发条件是「**我读不出输入**」而不是「**本机没有那份数据**」，
那么**产物被写坏**（本轮真实发生过：一个变量为空的脚本把报告数字整段抹掉）
就会让门禁**报全绿**。

★ 那正是本项目记录过的**第 4 种面孔**：**失败伪装成 `skipped`**。
轮 82 修了**一处**；本特性**系统排查全部 14 道门禁的每一个 SKIP 点**。

---

## 一、排查方法（**先蒐集，再分类，不靠印象**）

1. 扫 `scripts/check_*.py` 的**全部** `SKIP` 点（11 个脚本里共 15 处）；
2. 对每一处，抽出它的**守卫条件**（往上找最近的 `if` / `except`）；
3. 按一条判据分类：
   > **被读的那个东西，是本仓库自己的产物，还是本机/外部才有的数据源？**
   * **本机/外部数据源**（官方文档树、反射转储、`origin/main`、specs 目录）
     ⇒ **`SKIP` 正确**（别的机器上不该无条件红 —— 便携性）；
   * **本仓库自己的产物**（`docs/*.md`、`mcp-server/server.py`、`capabilities.yaml`）
     ⇒ 「读不出」= **产物坏了** ⇒ **必须 `FAIL`**。

---

## 二、排查结果

| 门禁 | SKIP 条件 | 分类 | 处置 |
|---|---|---|---|
| `check_interface_member_ownership` | 官方文档树不在 | 外部数据源 | ✅ 保持 SKIP |
| `check_member_names` | 反射清单不在 | 外部数据源 | ✅ 保持 SKIP |
| `check_spec_acceptance_paths` | specs 目录不在 | 外部数据源 | ✅ 保持 SKIP |
| `check_report_criteria_alignment` | `AGENTS.md` 不在 | 外部数据源 | ✅ 保持 SKIP（轮 82 新写，已正确）|
| `check_report_freshness` | 报告不存在 / 无 `origin/main` | 前者=产物·后者=外部 | ✅ 轮 82 已修 |
| `check_signature_audit_freshness` | 拿不到 `iface_*.txt` | 外部数据源 | ✅ 保持 SKIP |
| **`check_signature_audit_freshness`** | **文档里找不到逐模块表** | 🔴 **本仓库产物** | **本轮修**：文档在 ⇒ FAIL |
| **`check_workspace_shadowing`** | **`server.py` 不在** | 🔴 **本仓库产物** | **本轮修**：目录在 ⇒ FAIL |
| **`check_spec_acceptance_paths`** | **把 glob（`check_*.py`）当字面路径** | 🔴 **判据不贴合书写形态** | **本轮修**：glob 展开后匹配 ≥1 个即通过；**0 匹配仍红**（`glob-no-match`）|

---

## 三、验收判据

| ID | 判据 | 怎么验 |
|---|---|---|
| **SC-301** | 两处修好后，**正例**（真输入）仍 exit 0 | `python scripts/check_signature_audit_freshness.py` / `check_workspace_shadowing.py` |
| **SC-302** | 签名审计：**文档在但表读不出 ⇒ exit 1** | 负例见 converge §2.1 |
| **SC-303** | 签名审计：**文档不存在 ⇒ 仍 SKIP exit 0**（便携性未受损）| 同上 |
| **SC-304** | 遮蔽门禁：**`mcp-server/` 在但 `server.py` 不在 ⇒ exit 1** | 负例见 converge §2.2 |
| **SC-305** | 遮蔽门禁：**`mcp-server/` 整个不在 ⇒ 仍 SKIP exit 0** | 同上 |
| **SC-306** | 元门禁仍 PASS（SKIP 白名单没被改坏）| `python scripts/check_gate_wiring.py` |
| **SC-307** | 排查方法**可复跑**（探针入库）| `python tools/probe_skip_semantics.py` |

---

## 四、明确**不做**的

* **不删**任何 `SKIP`（便携性守卫是对的，只是**触发条件要分清**）；
* **不改**那 5 处「外部数据源」的 SKIP 语义；
* **不引入**新依赖。

---

## 五、结果

见 [converge.md](converge.md)。
