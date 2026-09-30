# Tasks: P3 · 并入模板定型（焊件域）

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务必须带 `→ 验收:`

**⚠ 本特性的模板价值 > 焊件本身**：后面 15 个域都会照它做。所以宁可少搬几个函数，
也要把六条规则与来源头注释的**形状**定准。

---

## Phase 1: Setup

- [x] **T-001** 逐成员核反射，定出官方签名表（**已完成**，见 spec 的背景表）
  `→ 验收:` `Select-String iface_sldworks.txt -Pattern 'InsertStructuralWeldment\('` 有命中，
  而 `InsertStructuralMember3` **无**命中

---

## Phase 2: Foundational

- [x] **T-002** 确认四个目标域在来源里的实际实现清单（**已完成**）
  焊件 6 / 模具 1 / 参考几何 5 / 仿真 3（用 `async def sw_*` 全量抽取，不靠关键词猜）
  `→ 验收:` `Select-String server.py -Pattern '^\s*async def sw_\w+\(' | Measure-Object` 得 187

- [ ] **T-003** 记录来源缺陷（可复核）
  新增 `D:\AI\SW\_raw\source-defects\Eduardof0nt.md`：逐条「来源写的 / 官方真名 / 核对命令」
  `→ 验收:` 该文件含 ≥4 条记录，每条都能用给出的命令重跑复核

---

## Phase 3: User Story 1 —— 焊件域按官方签名实现（P1，MVP）

- [ ] **T-004** [US1] 写 `scripts\sw_weldment.py`
  - 走项目既有模式：双路 import / `get_com_member` / `_select_by_id`（若需选区）
  - 六个公开函数，**名字与签名一律照反射**：
    | 函数 | 官方成员 | 官方签名 |
    |---|---|---|
    | `insert_weldment_feature` | `InsertWeldmentFeature` | `Feature InsertWeldmentFeature()` |
    | `add_structural_member` | `InsertStructuralWeldment` | `Feature InsertStructuralWeldment(String, Int32, Double)` |
    | `add_gusset` | `InsertGussetFeature` | `Feature InsertGussetFeature(Double, Int16, Int16, Boolean, Double, Double, Double, Double, Double, Boolean, Double, Int32, Boolean, Boolean, Boolean)` |
    | `add_end_cap` | `InsertEndCapFeature` | `Feature InsertEndCapFeature(Double, Boolean, Boolean, Double, Double, Double)` |
    | `trim_weldment` | `InsertWeldmentTrimFeature2` | `Feature InsertWeldmentTrimFeature2(Int32, Int32, Double, Object, Object)` |
    | `set_weldment_profile_path` | `set_WeldmentProfilePath` | `Void set_WeldmentProfilePath(String)` |
  - 每个函数带**来源头注释**：来源 repo/文件/许可 + **更正说明**（原名字是什么、为何按反射改）
  `→ 验收:` `python scripts\check_member_names.py` exit 0；`compileall -W error::SyntaxWarning` exit 0

- [ ] **T-005** [US1] 建特征后查重建（并入规则 6：不静默成功）
  `EditRebuild3` + `GetWhatsWrong2`
  `→ 验收:` 源码里每个建特征函数都调到这两个

---

## Phase 4: User Story 2 —— 每处并入可追溯（P2）

- [ ] **T-006** [US2] 契约测试 `tests\test_sw_weldment_contract.py`
  断言每个函数的**官方 arity 与参数类型**（照 `test_sw_topology_contract.py` 的形状）
  `→ 验收:` `python -m pytest tests\test_sw_weldment_contract.py -q` 全绿，用例数 ≥ 5

- [ ] **T-007** [US2] `capabilities.yaml` 登记焊件域条目
  `provenance` 四字段齐全；`level` = `stitched`；`limitations` 写明「来源未声明验证 + 未实测」
  `→ 验收:` `check_union_conventions.py` exit 0（它的 R6/R9/R10 校验 provenance）

---

## Phase 5: User Story 3 —— 来源缺陷被记录（P3）

- [ ] **T-008** [US3] 来源头注释里逐处写明「原名字 → 官方名字」
  `→ 验收:` `grep -c "官方真名\|按反射更正" scripts\sw_weldment.py` ≥ 4

---

## Phase 6: Polish（**本特性会改变许可义务，别漏**）

- [ ] **T-009** 更新 `THIRD-PARTY-NOTICES.md`
  Eduardof0nt 从「已评估但尚未并入」**迁到「实际包含」**，写明改动文件
  `→ 验收:` 该文件里 Eduardof0nt 出现在 §一（实际包含）且含 `Copyright (c) 2026 Eduardo Font Cruz`

- [ ] **T-010** 更新 `docs\union-coverage-matrix.md` 的焊件节（标为已并入）+ 重新生成地图
  `→ 验收:` `python tools\build_union_map.py` 后焊件节的「本仓库」列 > 0

- [ ] **T-011** 五项门禁 + 全量回归
  `→ 验收:` `check_member_names` / `check_provenance` / `check_diff_markers` /
  `check_union_conventions` 全 exit 0；回归 6 failed / 749 passed / 15 skipped（与基线逐条相同）

- [ ] **T-012** 两仓库各自 commit；回写 `ROADMAP.md` 游标 + 调整记录
  `→ 验收:` 两个 `git status --porcelain` 都为空
