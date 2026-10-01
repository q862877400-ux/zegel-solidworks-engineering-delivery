# Tasks: P3 · 并入模板定型（**改判据版**）

**Input**: [spec.md](spec.md)（已修订）· [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**⚠ 本特性的第一版前提是错的**（见 spec 的修订说明）：原以为焊件是缺口，
实际本仓库早有 `sw_weldment.py` 且 `weldments` 是 `verified`。
**⇒ 任务表随之重排：先修判据，再并入真缺口。**

---

## Phase 1: Setup —— 修判据（**阻塞全部后续**）

- [x] **T-001** 核实「焊件是缺口」这个前提
  **✅ 已证伪** —— `scripts/sw_weldment.py`（666 行 / 20 函数）；
  `capabilities.yaml` 的 `weldments` = **verified**（`verified_versions: ["2026"]`，
  真机验过 `InsertStructuralWeldment5` 等）
  `→ 验收:` `Select-String capabilities.yaml -Pattern '"id": "weldments"' -Context 0,3` 显示 verified

- [x] **T-002** 定位根因：地图的「本仓库」列怎么算的
  **✅** `tools/build_union_map.py` 的 `_our_tools()` 只数 `mcp-server/server.py` 的工具名
  `→ 验收:` `Select-String tools\build_union_map.py -Pattern 'def _our_tools' -Context 0,3`

- [x] **T-003** 建立**能力口径**的对照（两个口径并存、各自标注）
  **✅** 新增 `tools/capability_gap.py`
  ⚠ **2026-10-01（轮 53）从工作区根搬进 `tools/`** —— 原先只在 `D:\AI\SW\`，
  **换机器/CI 跑不了**（本轮新加的**验收命令可跑性门禁**
  `scripts/check_spec_acceptance_paths.py` 查出来的第 1 例）。
  搬移时把 `REPO` 改成 `Path(__file__).resolve().parents[1]`（**可移植**）；
  **并顺带修掉它自己两个 bug**（见下）。
  `→ 验收:` `python tools\capability_gap.py` 输出逐域表，
  且焊件行显示「我们函数 **14**」而地图缺口 **5**
  ```powershell
  python tools\capability_gap.py      # 75 模块 / 842 函数；地图缺口合计 **339**；焊件 14 / 模具 8
  ```
  ⚠⚠ **搬移时查出它自己有两个 bug（都是既有的、与我无关）**：
  | # | bug | 表现 | 修法 |
  |---|---|---|---|
  | 1 | `map_gap_counts()` 的正则写的是**八列**，而地图 §五 是**两列**、§二 是**九列** ⇒ **两张表都不匹配** | 「地图缺口」列**全是 `?`** | 改成两列 `\|\s*([①-⑰][^|]*?)\s*\|\s*(\d+)\s*\|` |
  | 2 | 域名的**空格形态**不同（§五 有空格、模块常量无空格）⇒ 查询扑空 | 同上（叠加） | 加 `_norm_domain()` 去空白，查询两侧都规范化 |
  ⇒ **修完合计 = `339`**（正是那个数）⇒ **这才叫「可复核的数字」**。
  ★ 这两个 bug 是**因为要搬它、不得不跑它**才暴露的 —— **搬到仓库里 = 逼它进入被跑的状态**。

- [x] **T-004** 更新记忆与文档（判据更正要留痕）
  **✅** 长期记忆已提交 Correction；`ROADMAP.md` §一 新增「重大调整」段、§五 新增 3 条反模式
  `→ 验收:` `Select-String docs\ROADMAP.md -Pattern '口径不清的数字'` 有命中

**Checkpoint**：判据已改 ✅ —— 可以开始并入真缺口

---

## Phase 2: User Story 1 —— 找出**真的**缺的域（P1）

- [x] **T-005** [US1] 按能力口径排序各域，选出模板域
  **✅** 模具：地图缺口 3、本仓库仅 1 个函数（且那 1 个是 `core_only` 误分类）
  ⇒ 满足 US2 的三条件：① 本仓库≈0 ② 有来源 ③ 最小
  `→ 验收:` `python tools\capability_gap.py` 的模具行「我们函数 8」
  ⚠ 原文写的是「我们函数 **1**」—— 那是**选择当时**的值；并入 `sw_mold.py` 后已是 **8**
  （**同轮 49 抓到的 `002` SC-004「时点判据」问题**：任何「本仓库 = N」型判据**在并入后都会变**）。
  ⚠ 命令本身也从裸文件名 `capability_gap.py` 改成**仓库内** `python tools\capability_gap.py`（轮 53）。

- [x] **T-006** [US1] 核实来源在该域的实现，并**逐成员核反射**
  **✅ 来源 2/2 个方法名都是错的**：`InsertPartingLines` → 官方 `InsertMoldPartingLine(Boolean)`；
  `InsertShutOffSurfaces` → 官方 `InsertMoldShutOffSurface()`
  `→ 验收:` 见 T-007 的记录文件

- [x] **T-007** [US1] 记录来源缺陷（可复核）
  **✅** `D:\AI\SW\_raw\source-defects\Eduardof0nt.md` —— 7 条记录 + 逐条可重跑命令
  `→ 验收:` 该文件含「焊件 4/5 错 · 模具 2/2 错」与三组复核命令

---

## Phase 3: User Story 2 —— 并入模板域（P2）

- [x] **T-008** [US2] 写 `scripts/sw_mold.py`（**签名全照反射**）
  七个入口：`insert_parting_line` / `insert_parting_surface` / `insert_shut_off_surface` /
  `insert_core_cavity_solids` / `mold_draft_analysis` / `mold_undercut_detect` / `mold_evidence`
  `→ 验收:` `python scripts\check_member_names.py` **[PASS]**（614 个调用点全部命中官方反射）

- [x] **T-009** [US2] 契约测试 `tests/test_sw_mold_contract.py`
  **✅ 9 passed**，含一条**反自证锚点**：断言来源的错名不得作为成员名出现在本模块
  `→ 验收:` `python -m pytest tests\test_sw_mold_contract.py -q` → 9 passed

- [x] **T-010** [US2] `capabilities.yaml` 更新 `mold_tools` 条目
  补上「生成侧」；`provenance` 为**数组**（门禁要求）；`level` **维持 `stitched`**（未实测）
  `→ 验收:` `python scripts\check_union_conventions.py` exit 0

---

## Phase 4: User Story 3 —— 厘清「已有能力 → MCP 工具」（P3）

- [x] **T-011** [US3] 评估把既有函数暴露成 MCP 工具的路径与代价
  **✅ 已完成** —— 产出两份：评估文档 + 最小可跑示例的草稿。
  **结论**：
  - `server.py` 45 个工具 / 2455 行 = **54.6 行/工具** ⇒ 手工注册 814 个函数 ≈ **44,408 行，不现实**
  - **三条硬约束挡住自动注册**：规则 1（名字要人工判域）、规则 2（`_mm`/`_deg` 后缀逐参判）、
    规则 3（必须声明式 `selection`，而很多函数以「调用方先选好实体」为前置）
  - **真实工作量是 ~120 个函数**（不是 814）—— 按新立的**暴露判据**筛：
    「该函数是不是『用户会用一句自然语言要求的**动作**』？」是 ⇒ 候选；内部索引
    （12 个 `sw_api_*`）、GUI 步骤（13 个 `sw_jlcfa_*`）、门禁工具 ⇒ 不暴露
  - **不做**「泛型调用」工具（违规则 3 + 把整个 `scripts/` 变成远程执行面）
  `→ 验收:`
  ```powershell
  # 评估文档（含成本量化与三批判选）
  Select-String D:\AI\SW\docs\T-011-expose-capabilities-assessment.md -Pattern '44,408'
  # 最小示例草稿（3 个护城河工具，未接入在跑的服务）
  Select-String D:\AI\SW\mcp-tool-draft\topology_tools.py -Pattern 'solidworks_topology_'
  # 草稿引用的函数均已核实存在
  Select-String C:\swprojects\sw-skill-fork\scripts\sw_simulation.py -Pattern 'def (iter_studies|get_study_by_name)\('
  ```
  **⚠ 未接入** `mcp-server/server.py` —— 那正是本会话 `mcp__solidworks__*` 工具的来源，
  改它会动**正在运行的** MCP 表面；「单源运行」原则下（已知事实 24）重启需确保无任务在跑
  ⇒ **接入时机由人决定**（草稿里已写明三步接法）。

---

## Phase 5: Polish

- [x] **T-012** 更新 `THIRD-PARTY-NOTICES.md`
  Eduardof0nt 从「已评估但尚未并入」**迁到「部分并入」**，写明「**代码未移植、只引用思路**」
  与改动文件名录（MIT 版权声明已留）
  `→ 验收:` 该文件 §一 有 Eduardof0nt 一节；§二 表格该行改为「部分并入」

- [x] **T-013** 五项门禁 + 全量回归
  **✅** 四项门禁全 exit 0；`compileall -W error::SyntaxWarning` exit 0；
  回归 **6 failed / 758 passed / 15 skipped**（749→758 即新增的 9 条；失败列表与基线逐条相同）
  `→ 验收:` 上述命令的实际输出

- [x] **T-014** 两仓库 commit + 回写 ROADMAP 游标与调整记录
  **✅** 代码副本 `4b2e71d`；工作区 `d89f558`
  `→ 验收:` 两个 `git status --porcelain` 都为空

---

## 未完成 / 已改写（如实记）

- **T-011** 未做（US3 属评估类，本轮优先把 US1+US2 做实）
- **原第一版的「焊件并入」任务全部作废** —— 前提错，见 spec 修订说明
- **模具域未做实测** ⇒ `level` 维持 `stitched`（不升 `verified`）
