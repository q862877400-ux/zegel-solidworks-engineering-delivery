# Tasks — **`create_draft` 的 `pre_call` 补上「方向项」（mark 1）**

**Feature**: `specs/296-create-draft-pre-call/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-296-01 先量**：读 283 两条真机读数 + `_pre_draft` 现状
  ⇒ ★ 工具层**只选面**，与 283 的「需要**两个**」**不符**。
- [x] **T-296-02 查钉住**（★ 规则 28）：`test_tool_specs_batch4.py`（参数必须映射或显式消费）·
  `test_create_draft_machine_verified.py`（283 的读数）· `test_draft_official_entry.py`（★ **发现一条恒红**）。
- [x] **T-296-03 写判据（先红）**：`tests/test_create_draft_pre_call_296.py`（**6 条**）。
- [x] **T-296-04 跑红基线**：⇒ **`3 failed, 3 passed`** ✓
- [x] **T-296-05 改工具层**：`mcp-server/tool_specs_batch4.py`
  - 加 `Param("direction_plane", str, default="Front Plane", …)`；
  - `param_alias` 登记 `{"direction_plane": None}`（★ 由 `pre_call` 消费）；
  - 加 `_face_object()` / `_select_plane()`；重写 `_pre_draft()`。
- [x] **T-296-06 跑绿（离线）**：⇒ **6 passed**（★ 连同既有 **14 passed, 2 skipped**）。
- [x] **T-296-07 ★★★ 真机验（第一次）**：走 `sw_guard --timeout 600` 跑 `output/_probe296_draft_precall.py`
  ⇒ ★★ **`mark1=0` · 合计=1** ⇒ ★ **`InsertMultiFaceDraft 创建失败`**（★ **发现真 bug**）。
- [x] **T-296-08 ★★★ 修真 bug**：★ 顺序 + `append` 语义 ——
  `ClearSelection2` → `_select_plane(mark=1)` → `_select_com_object(face, append=True, mark=2, model)`；
  ★ 并**分别回读** `GetSelectedObjectCount2(1)` 与 `(2)`。
- [x] **T-296-09 ★★★ 真机复验**：⇒ ★★ **`mark1=1` · 合计=2** · ★ **建成 `拔模1`** ✓
  ★ 证据 `output/_probe296_draft_precall.txt`。
- [x] **T-296-10 无残留**：`sw_guard --scan` ⇒ 弹窗 **0** · 打开文档 **0**（★ 临时零件关闭且未保存）。
- [x] **T-296-11 顺带修陈旧判据**：`tests/test_draft_official_entry.py` 那条**恒红**的
  （★ `git stash` 隔离证明**非本轮引入**）⇒ 改成「状态与真机证据必须一致」。
- [x] **T-296-12 生成器链**（★ 改了 `mcp-server/`）：7 步 `rc=0`。
- [x] **T-296-13 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate296.log`。
- [x] **T-296-14 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `mcp-server/tool_specs_batch4.py` | ★ **加 2 个帮手 + 改 1 个 `pre_call` + 加 1 个参数 + 1 处 `param_alias`** |
| 2 | `tests/test_create_draft_pre_call_296.py` | ★ **新建判据**（6 例） |
| 3 | `tests/test_draft_official_entry.py` | ★ **订正 1 条恒红的陈旧判据** |
| 4 | `specs/296-create-draft-pre-call/*` | ★ 本规格四件套 |
| 5 | `output/_probe296_draft_precall.py` / `.txt` | ★ 真机探针与读数（★ 一次性，★ 留 `output/`） |

★ **未改**：`scripts/sw_sheet_metal.py`（★ 边界冻结）。

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_pre_call_selects_both_a_plane_and_a_face` | ❌ **FAILED** | ✅ pass |
| ② | `test_direction_is_a_declarative_param` | ❌ **FAILED** | ✅ pass |
| ③ | `test_pre_call_raises_when_the_plane_is_missing` | ❌ **FAILED** | ✅ pass |
| ④ | `test_criterion_is_red_able` | ✅ pass | ✅ pass |
| ⑤ | `test_implementation_signature_untouched` | ✅ pass | ✅ pass |
| ⑥ | `test_machine_recipe_is_recorded` | ✅ pass | ✅ pass |
| — | **合计** | **3 failed, 3 passed** | **6 passed** |

---

## 四、★★★ 真机读数（★ 本规格的**决定性**证据）

| ★ 阶段 | ★ 命令 | ★ 读数 |
|---|---|---|
| 第一次 | `sw_guard --timeout 600 -- python output/_probe296_draft_precall.py` | ★ **`mark1=0` · 合计=1** ⇒ 失败 |
| ★★ 修后 | 同上 | ★★ **`mark1=1` · 合计=2** ⇒ ★ **建成 `拔模1`** |
