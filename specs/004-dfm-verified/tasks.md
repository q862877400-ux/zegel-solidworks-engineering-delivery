# Tasks: DFM 复核升 `verified`

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 79）。本表同时是「这件事是怎么做成的」的可复核记录。

---

## Phase 0: 前提核查（**先查证，不写代码**）

- [x] **T-001** 核 `dfm_checks` 的依赖，判断本机能不能跑
  **✅** `dependencies: ["python"]` ⇒ **不需要** `OCP`/`trimesh`（本机两者都缺，但不影响本条）。
  ★ 这条推翻了它此前被笼统归入「需 B-Rep 证据」的搁置理由 ——
  「**B-Rep 证据绑定**」指的是**输入由外部给**，**不是**它自己去跑 OCP。
  `→ 验收:` `python -c "import json;d=json.load(open('capabilities.yaml'));print([c['dependencies'] for c in d['capabilities'] if c['id']=='dfm_checks'])"`

- [x] **T-002** 跑既有测试，确认实现本身是好的
  **✅** `tests/test_dfm_review.py` + `tests/test_dfm_queue_worker.py` ⇒ **19 passed**。
  ★★★ **2026-10-10 改验收命令（★ 如实）**：★ 业主架构指令 —— ★ **只继承工具 · 方法移出** ⇒
  ★ `dfm_review.py`（★ **DFM 规则库 = 方法**）已移出 ⇒ ★ 它的判据 `test_dfm_review.py` **跟着移出** ✓
  ★★ **⇒ 验收改为跑留下的那个**（★ 它测的是**队列工具**，★ 不是方法）✓
  `→ 验收:` `python -m pytest tests/test_dfm_queue_worker.py -q`

- [x] **T-003** 逐条读 `limitations` 三句，把每句变成可判的验收点
  **✅** L1（Profile 交集 / 单位归一 / B-Rep 绑定 / 缺失⇒blocked）· L2（人工确认项）·
  L3（风险复核非认证 / 缺关键输入⇒blocked）⇒ 落成 `spec.md` 的 SC-001..SC-008。
  `→ 验收:` `Select-String D:\AI\SW\specs\004-dfm-verified\spec.md -Pattern 'SC-00'`

---

## Phase 1: 摸清调用契约（**照测试抄，不臆造**）

- [x] **T-004** 从既有测试里抄出**文档 JSON 的真实形态**与**报告字段名**
  **✅** 见下（**全部来自测试，无一处臆造**）：
  ```
  工艺 : dfm_review.DFM_PROCESSES = {machining, sheet_metal, laser_cutting, 3d_printing}
  单位 : dfm_review.UNIT_TO_MM   = {mm:1.0, cm:10.0, m:1000.0, inch:25.4, in:25.4}
  入口 : dfm_review.check_dfm_document(...) / cad_studio 的 MCP 工具
  ```
  `→ 验收:` `Select-String archive\inherited-methods\scripts\dfm_review.py -Pattern 'DFM_PROCESSES|UNIT_TO_MM'`
  ★★★ **2026-10-10 改路径（★ 如实）**：★ 业主架构指令 —— ★ **只继承工具 · 方法移出** ⇒
  ★ `dfm_review.py`（★ **DFM 规则库 = 方法**）已移出 `scripts/` ⇒
  ★★ 落在 `archive/inherited-methods/scripts/dfm_review.py`（★ **只搬不删**）✓
  ★ 判据：★「**规则错了，回读能不能查出来**」⇒ ★ **不能** ⇒ 是方法 ✓

---

## Phase 2: 写验收命令

- [x] **T-005** 写 `tools/verify_dfm_e2e.py` —— **每条 SC 一个 `chk()`**，最后给 `verdict`
  **✅** 判据**故意造违规**：删关键输入 / 篡改证据哈希 / 用窄 profile 收窄交集 ⇒
  看它们是否**真的**导致 `blocked` 或收窄（不是"跑通就算"）。
  `→ 验收:` `python tools/verify_dfm_e2e.py`（退出码 0 且末行含 `verdict: pass`）

- [x] **T-006** [P] 证据落 `D:\AI\SW\output\dfm-evidence.json`
  **✅** 逐条 `chk` 的 `ok` 与 `detail` 都在里面（可复核是"哪一条"过的）。
  `→ 验收:` `Test-Path D:\AI\SW\output\dfm-evidence.json`

---

## Phase 3: 清单升级

- [x] **T-007** `dfm_checks`：`level` → `verified` + 补 `evidence` / `verified_versions`
  **✅** `evidence` 2 条（验收命令 + 19 个测试）· `verified_versions: ["python 3.14.7"]`
  （⚠ 本条**不依赖 SolidWorks / OCP** ⇒ **不填 CAD 版本**，按 `dxf_preview_scene` 先例填**依赖版本**）。
  ⚠ **`limitations` 一条不删**。
  `→ 验收:` `python scripts/check_union_conventions.py`（R4：`verified` 必须有 `evidence`）

---

## Phase 4: 门禁 + 回归 + 收工

- [x] **T-008** [P] 十二道硬门禁 + 生成物刷新
  **✅** `check_union_conventions` / `check_provenance` / … / `check_gate_wiring` 全 exit 0；
  `gen_level_audit.py` / `build_union_map.py` / `gen_harvest_digest.py` 已重生成。
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-009** 全量回归
  **✅** `970 passed / 17 skipped / 0 failed`（升级前基线同数；**无新增失败**）。
  `→ 验收:` `python -m pytest tests -q`

- [x] **T-010** 两仓库各自 commit
  **✅** 代码副本（验收命令 + 清单）与工作区（`specs/004-dfm-verified/`）分开提交。
  `→ 验收:` `git -C . log --oneline -1` +
  `git -C D:\AI\SW log --oneline -1`

---

## 依赖关系

```
T-001 ─┬─→ T-003 ─→ T-004 ─→ T-005 ─→ T-007 ─→ T-008 ─→ T-009 ─→ T-010
T-002 ─┘                └─→ T-006
```
