# Tasks — 枚举表盲区收口

**Feature**: `specs/224-enum-table-disposition/`
**解释器**: 判据 `PY=C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe`（无 pytest，标准库 unittest）；
★ **门禁全套 `release_check` 必须用 3.14.7**（3.13.12 缺 comtypes ⇒ 触发交互式 COM 提示 ⇒ 假红，见 `acceptance.md` §五）。

★ **顺序纪律**：T-001～T-006 是**判据**，必须先跑出**红**再动实现（T-007 起）。
★ 每条任务的验收命令**可复制执行**；`[x]` 只在**命令真跑过且读数符合**时打。

**收口轮（2026-10-09 01:08–01:20，任务 `3c1e4507`）**：T-001～T-018 全部完成；读数逐条见 `acceptance.md`。

---

## A. 判据（先写、先红）

- [x] **T-001** 新建 `tests/test_enum_table_disposition.py`（实为 **8 用例**，含 3 条负例）。
  - 验收：`$PY -B tests/test_enum_table_disposition.py`
  - 实测（改动前）：**FAILED**（负例文案不含「未表态」⇒ 1 例红；机制未生效时 44 张全无声明）
- [x] **T-002** 红基线读数：收口首跑 **`FAILED (failures=1)`**（见 `acceptance.md` §四·注 2）。
- [x] **T-003** 改动前门禁读数：`扫描 189 · 模块级整数表 101 · 已覆盖 33 · 未覆盖 68` / `门禁盲区 44` / `[PASS] 175` / exit 0 ✓

---

## B. 实现（串行，主代理自己做）

- [x] **T-004** FR-001：`DUMP_ROW` 成员名 `sw\w+` → `[A-Za-z_]\w*` ⇒ 成员 **10664**（改前 10588）✓
- [x] **T-005** FR-002：`DISPOSITION`/`DISPOSITION_CODES`/`NOT_ENUM_SUBS`/`parse_dispositions()`/`enum_value_sets()`/`check_dispositions()` ✓
- [x] **T-006** FR-003：覆盖清单改三段读数 + 未表态 `return 1` ✓（负例证 exit 1）
- [x] **T-007** FR-004：按 AST 定位给 **44 张**表逐张插入 `#: enum-gate: …`（enum 23 · member 11 · not-enum 10）✓
- [x] **T-008** 插入后复核表集合未漂移：`find_int_tables()` = **101** ✓

---

## C. 验收（每条都要跑出读数）

- [x] **T-009** 主判据全绿：`Ran 8 tests · OK` ✓
- [x] **T-010** 门禁本体绿：`已表态 44 · 未表态 0 · [PASS] 175 条 · exit 0` ✓
- [x] **T-011** 223 判据仍绿：`7/7 passed` ✓
- [x] **T-012** 222 判据仍绿：`18/18` + `12/12` ✓
- [x] **T-013** 既有代码行零改动：含 `#: enum-gate:` 的 hunk 中**同含删除行 = 0** ✓
- [x] **T-014** 打包副本新鲜度：首跑 2/3 → `sync_bundled_skill`（461 文件，`pruned=[]`）后 **3/3** ✓

---

## D. 收尾

- [x] **T-015** 更新 `docs/ROADMAP.md` §一 游标（追加 224 段 + 新「下一 WIP」）✓
- [x] **T-016** 更新 `.specify/feature.json` → `specs/224-enum-table-disposition` ✓
- [x] **T-017** `.workbuddy-ai/memory/2026-10-08.md` 把「本轮进行中」改写成结论（append）✓
- [x] **T-018** 写 `output/AUTO_RUN_2026-10-09-0118.md` ✓

**不做**：不 commit / 不 push / 不部署 / 不打 tag / 不调 COM / 不删文件。
