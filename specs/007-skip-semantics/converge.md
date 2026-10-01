# Converge: 门禁 SKIP 的语义

**Feature**: `007-skip-semantics` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 83）· **环境**: Python 3.14.7

> **这一步做什么**：把 `spec.md` 的每条验收判据**与实测证据逐条对齐**，并**明确记下不符合项**。
> **不是复述 spec** —— 复述没有价值，找出「声称」与「实际」的差才有。

---

## 一、结论摘要

| 判据 | 结论 | 依据（可复跑的枚举命令） |
|---|---|---|
| SC-301 两处正例仍 exit 0 | ✅ 成立 | `python scripts/check_signature_audit_freshness.py` / `check_workspace_shadowing.py` |
| SC-302 文档在但表读不出 ⇒ exit 1 | ✅ 成立 | 见 §2.1 负例 A |
| SC-303 文档不存在 ⇒ 仍 SKIP exit 0 | ✅ 成立 | 见 §2.1 负例 B |
| SC-304 `mcp-server/` 在但 `server.py` 不在 ⇒ exit 1 | ✅ 成立 | 见 §2.2 负例 A |
| SC-305 `mcp-server/` 整个不在 ⇒ 仍 SKIP exit 0 | ✅ 成立 | 见 §2.2 负例 B |
| SC-306 元门禁仍 PASS | ✅ 成立 | `[PASS] 14 个门禁全部已接线`，exit 0 |
| SC-307 排查方法可复跑（探针入库）| ✅ 成立 | `python tools/probe_skip_semantics.py` |

---

## 二、**实测记录**（本节才是价值所在）

### 2.1 `check_signature_audit_freshness` —— 与轮 82 修掉的**完全同型**
```
修前: 文档在、但逐模块表读不出  ⇒  print("**SKIP** —— 文档里找不到逐模块表")  ⇒  return 0
修后: 文档不存在   ⇒ SKIP（便携性）exit 0
      文档在但读不出 ⇒ FAIL           exit 1
```
**负例 A 实测**（造一份「故意没有逐模块表」的文档当 `--doc`）：
```
exit=1
[FAIL] 文档**存在**，但读不出「逐模块表」⇒ 产物已损坏或被写坏
```
**负例 B 实测**（`--doc` 指向不存在的路径）：`exit=0` + `**SKIP** —— 文档不存在（…）`。
**正例**：`exit=0`。

### 2.2 `check_workspace_shadowing` —— 「本仓库文件」被当成「外部数据源」
```
SERVER = ROOT / "mcp-server" / "server.py"     ← ROOT 由 __file__ 推出 ⇒ 永远是本仓库
修前: if not SERVER.is_file(): SKIP(return 0)
修后: mcp-server/ 目录不在   ⇒ SKIP（这里不是本仓库）exit 0
      mcp-server/ 在但文件不在 ⇒ FAIL（仓库不完整）  exit 1
```
**负例实测**（在 `tempfile` 造**假仓库**，因为 `ROOT` 不能靠参数改）：
```
mcp-server/ 目录在、server.py 不在   ⇒ exit=1
[FAIL] `mcp-server/` 目录在，但读不到 `server.py` ⇒ **仓库不完整**

mcp-server/ 目录整个不在             ⇒ exit=0
[SKIP] 找不到 `mcp-server/` 目录（…）—— **这里不是本仓库**
```
**正例**：`exit=0`，输出 `[PASS] 工作区根没有会遮蔽它们的 .py/目录`。

### 2.3 ✓ 分类时的一处**差点误判**
`check_member_names.py` 的 SKIP 原文是
「反射清单不在本机，无法校验（**这是静默通过，不算通过**）」——
⚠ 名字里带「本机」，看起来像**产物**；**读源码确认它读的是 `official` = 反射转储（仓库外）**
⇒ **外部数据源 ⇒ SKIP 正确**。
★ 又一次印证：**分类要读常量的来源，不靠名字猜**。

### 2.4 ★ 修 §四 时**又撞见一处**：验收命令门禁把 **glob 当字面路径**
我的 `007/tasks.md` 写了一条**合法**的验收命令：
`→ 验收:` `Select-String scripts\check_*.py -Pattern 'SKIP' -List`
⇒ `check_spec_acceptance_paths` **误报** `[missing-in-repo] …仓库里没有这个文件`。

**根因**：它的 ② 分支用 `p.is_file()` 判「带仓库目录前缀的 token」，
而**本仓库的验收判据惯用 grep 形态**（`Select-String <glob> -Pattern …`）
⇒ **带 `*` 的必然误报**。
★ 与它**自己 docstring 里记的那次假阳性**（轮 53：绝对路径**在仓库里**却被报「仓库外」）
**是同一族**：**判据要贴合实际的书写形态**。

**修法**：含 glob 元字符（`*` `?` `[`）的 token 用 `repo.glob()` 展开 ——
**匹配到 ≥1 个**才算通过；**一个都没匹配到** ⇒ 报 `glob-no-match`（**仍然红**，只是换了原因名）。

**负例证明**（`tools/probe_spec_glob_gate.py`，三种情形）：
```
正例 glob 能匹配            ⇒ exit=0  ✓（不再误报）
负例 glob 一个都匹配不到     ⇒ exit=1  ✓（换原因名但没放过）
负例 字面文件不存在          ⇒ exit=1  ✓（原有行为未退化）
```

### 2.5 ⚠ 本轮**未查证**：`check_signature_audit_freshness` 的**第三处** SKIP
```
L278  if checked == 0:  →  print("**SKIP** —— 一个模块都没能实跑（便携性守卫）")  →  return 0
```
它的注释写着「便携性守卫」，**但轮 55 首跑时就撞上过**：路径解析写法不对 ⇒ 6/6 全报「跑不了」
⇒ **误 SKIP**（当时靠人发现并修了路径）。
⚠ **本轮没有查证**：在**本机**（`--raw` 那个目录**在**）却 `checked == 0` 时，
它是否也该 **FAIL**（那说明路径解析又坏了，而不是"别的机器上没有反射转储"）。
⇒ 按铁律 5 **如实记为未查证**，作下轮候选。**不猜着改**。

---

## 三、与 `tasks.md` 的对账

**T-301..T-311 全部完成**。关键：T-302 的蒐集**不靠印象**（扫出 15 处，而不是我以为的 2~3 处）；
T-307 的负例用**假仓库**（`ROOT` 不可参数化，只能造目录）。

---

## 四、本轮**没有**做的事

* **没有**新增第 15 道门禁（判据已存在，只是两处用错）—— 避免「为了修房子创建公司」；
* **没有**动那 5 处「外部数据源」的 SKIP 语义；
* **没有**查证 `checked == 0` 那一处（§2.4）。

---

## 五、复跑全部命令

```powershell
cd C:\swprojects\sw-skill-fork
python tools/probe_skip_semantics.py                          # 蒐集 + 分类 + 实测
python scripts/check_signature_audit_freshness.py             # 正例 exit 0
python scripts/check_workspace_shadowing.py                   # 正例 exit 0
python scripts/check_gate_wiring.py                           # [PASS] 14 个门禁全接线
python -m pytest tests -q                                     # 970 passed / 17 skipped / 0 failed
python scripts/release_check.py                               # exit 0
```
