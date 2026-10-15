# tasks 234 —— `local` 桶调用点的候选集门禁

> 每条带**可复制执行**的验收命令。状态：`[x]` 已完成并跑绿。

## T1 量测（先量后改）

- [x] T1-1 量 `local` 桶调用点与候选集：`output/_probe234_values.py`
  ```bash
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe234_values.py
  ```
  ⇒ `local 46 · 可枚举 42 · 仍不可枚举 4 · 候选值 distinct 131`
- [x] T1-2 量两源覆盖边界（**决定存在性检查可行**）：反射转储**仅方法** ⇒ 属性须剥 `get_`/`set_`；
  swapi 无 cosworks ⇒ 须并集。
  ⇒ 单用转储 100 个假阳性 / 单用 swapi 41 个 / **并集后仅 21 个**（其中 9 个是读取器自己的口径错）。

## T2 先写判据并确认能红

- [x] T2-1 新增 `tests/test_dispatch_arg_guard.py`（17 例）
  ```bash
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_arg_guard
  ```
  ⇒ `Ran 17 tests · OK`
- [x] T2-2 **红基线**（改实现前必须失败一次）：门禁首跑
  ```bash
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_arg_guard.py
  ```
  ⇒ `[FAIL] 违规 8 处：[undeclared] ×7 + [baseline-shrunk] ×1` · `exit 1`

## T3 实现

- [x] T3-1 新增 `scripts/check_dispatch_arg_guard.py`（封闭形态读取器 + 两源存在性 + 两个逃生门 + 下界 + 零检查 + 口径一致性断言）
- [x] T3-2 修读取器两处口径错（`.items()` 按位置、`.get()` 取值）⇒ 候选值 distinct `140 → 131`
- [x] T3-3 补 7 处声明（**纯插入零删除**）：`output/_insert234_decls.py`
  ```bash
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_insert234_decls.py
  git diff --numstat -- scripts/sw_feature_readback.py scripts/sw_part.py scripts/sw_sheet_metal_weld_entry.py scripts/sw_simulation_loadprops.py scripts/sw_units.py
  ```
  ⇒ 每个文件 `+N -0`
- [x] T3-4 门禁转绿
  ```bash
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_arg_guard.py
  ```
  ⇒ `local 46 · 可枚举 42 · 候选值 131 · 违规 0 · [PASS] · exit 0`

## T4 接线

- [x] T4-1 `scripts/release_check.py`：`_run_dispatch_arg_guard_gate` + fail 判据 + `_gate_results` 登记
      （★ 元门禁 `check_gate_wiring.py` 当场抓到「`dispatch_arg` 的结果没有进返回体」⇒ 已补）
- [x] T4-2 `docs/gate-classification.json` 登记（`classification` 43 → 44）：`output/_reg234_gate.py`
- [x] T4-3 复核插入点的 `# ── 来源 ──` 相邻头（★ 已踩：`Edit` 吞掉了 `_run_interface_ownership_probe` 的来源块头 ⇒ 已恢复）

## T5 收尾

- [x] T5-1 收尾链
  ```bash
  pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_arg_guard.py
  ```
  ⇒ `release_check: 第 1 轮 OK` · `17 passed`
- [x] T5-2 门禁全套（★ 3.14.7）
  ```bash
  C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
  ```
  ⇒ `status pass` · `missing []` · `gates 42 → 43` · `dispatch_arg_guard: pass`
- [x] T5-3 229–234 合并回归（见 `acceptance.md` §二）
- [x] T5-4 更新 `docs/ROADMAP.md` §一 · `.specify/feature.json` · `memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_2026-10-09-*.md`

## T6 明确不做（登记，不在本切片）

- [ ] T6-1 候选值的**接口归属**判定（属 `check_interface_member_ownership.py`）
- [ ] T6-2 扩 `_entry_sites()` 认别名（触发条件 = spec 232 门禁变红）
- [ ] T6-3 `partial` / `unresolved` / `no-callers` 入口的**非字面量**调用点判据（需先量）
- [ ] T6-4 16 条 arity 不符定罪 / `HEM_POSITIONS` 真机复核（**需业主另行授权 COM**）
