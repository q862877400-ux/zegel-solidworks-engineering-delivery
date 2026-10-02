# Tasks: 门禁 SKIP 的语义

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 83）。

---

## Phase 0: 蒐集（**不靠印象**）

- [x] **T-301** 扫出 `scripts/check_*.py` 的**全部** SKIP 点
  **✅** 11 个脚本 / 15 处（其中「打印 SKIP 并返回」的出口 9 个）。
  `→ 验收:` `Select-String scripts\check_*.py -Pattern 'SKIP' -List`

- [x] **T-302** 对每一处抽出**守卫条件**（往上找最近的 `if`/`except`）
  **✅** 结果见 `spec.md §二` 的表。
  `→ 验收:` `python tools/probe_skip_semantics.py`

---

## Phase 1: 分类（**读常量的来源，不靠名字猜**）

- [x] **T-303** 按「本仓库产物 vs 本机/外部数据源」逐条分类
  **✅** 5 处「外部数据源」保持 SKIP；**2 处「本仓库产物」是缺陷**。
  ⚠ 关键证据（**读源码得到**）：
  ```
  check_signature_audit_freshness:  ap.add_argument("--doc", default=str(DOC))   ← DOC 在仓库内
  check_workspace_shadowing:        SERVER = ROOT / "mcp-server" / "server.py"   ← ROOT 由 __file__ 推出
  ```
  `→ 验收:` 同上探针的「argparse 参数」段

---

## Phase 2: 修（**照轮 82 的形状：不存在 ⇒ SKIP；在但读不出 ⇒ FAIL**）

- [x] **T-304** 修 `check_signature_audit_freshness.py`
  **✅** `Path(a.doc).is_file()` ⇒ FAIL；否则 SKIP。
  **实测**：坏文档（表整段缺失）⇒ **exit 1**（修前 exit 0）。
  `→ 验收:` 见 [converge.md](converge.md) §2.1

- [x] **T-305** 修 `check_workspace_shadowing.py`
  **✅** `SERVER.parent.is_dir()`（`mcp-server/` 在 = 这是本仓库）⇒ FAIL；否则 SKIP。
  **实测**：假仓库（目录在、`server.py` 不在）⇒ **exit 1**；目录整个不在 ⇒ **exit 0 SKIP**。
  `→ 验收:` 见 [converge.md](converge.md) §2.2

---

## Phase 3: 负例证明（**两边都测**）

- [x] **T-306** 签名审计：**正例** + **负例 A（产物坏）** + **负例 B（不存在）**
  **✅** exit 0 / **exit 1** / exit 0 SKIP（便携性未受损）。
  `→ 验收:` 同上

- [x] **T-307** 遮蔽门禁：**正例** + **负例 A（目录在、文件不在）** + **负例 B（目录不在）**
  **✅** exit 0 / **exit 1** / exit 0 SKIP。
  ⚠ 负例用 `tempfile` 造**假仓库** —— 它的 `ROOT` 由 `__file__` 推出，**不能靠参数改**。
  `→ 验收:` 同上

---

## Phase 4: 收工

- [x] **T-308** 元门禁（SKIP 白名单是否被改坏）
  **✅** `[PASS] 14 个门禁全部已接线`，exit 0。
  `→ 验收:` `python scripts/check_gate_wiring.py`

- [x] **T-309** [P] 13 道门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-310** 全量回归
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-311** 两仓库各自 commit
  `→ 验收:` `git -C . log --oneline -1` + `git -C D:\AI\SW log --oneline -1`
