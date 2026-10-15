# Acceptance — **`create_draft` 的 `pre_call` 补上「方向项」（mark 1）**

**Feature**: `specs/296-create-draft-pre-call/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立（`3 failed, 3 passed`）· 生成器链 7/7 · 真机建成 · 无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★★ **「283 真机建成」这个结论，本轮**终于经工具层复现了** ——
★ 真机读数：★ **`mark1=1` · 合计=2** ⇒ ★★ **建成 `拔模1`** ✓
★ 而 296 之前，工具层只给一个前置 ⇒ ★ 真机**必报**「此拔模方向尚未定义。」

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★ `pre_call` 建**两个**选择 | `test_pre_call_selects_both_a_plane_and_a_face` | ❌ **FAILED** | ✅ pass |
| FR-002 | ★★ 方向项**可声明**（规则 3） | `test_direction_is_a_declarative_param` | ❌ **FAILED** | ✅ pass |
| FR-003 | ★★ 前置没备齐**必须抛** | `test_pre_call_raises_when_the_plane_is_missing` | ❌ **FAILED** | ✅ pass |
| FR-004 | ★ 判据能红 | `test_criterion_is_red_able` | ✅ pass | ✅ pass |
| FR-005 | ★ 边界冻结（不改实现签名） | `test_implementation_signature_untouched` | ✅ pass | ✅ pass |
| — | 配方留档可查 | `test_machine_recipe_is_recorded` | ✅ pass | ✅ pass |
| — | **合计** | — | **3 failed, 3 passed** | **6 passed** |

## 二、★★★★ 真机读数（★ 决定性 · 走 `sw_guard` · SW rev **34.4.1**）

### 2.1 第一次真机（★ **发现真 bug**）

```
=== ① 跑 `pre_call` ===
  ★ 回读选区：mark1=0 · 合计=1          ← ★★ 方向项**没选上**
=== ② 调目标函数 ===
  ★★ 异常：RuntimeError: InsertMultiFaceDraft 创建失败
```

★★★ **真因**：★ 第一版写成 `_select_plane(mark=1)` 然后 `_select(params, "FACE")`，
而 `_select` 内部走 `resolve_selection` → `select_object(append=False)`
⇒ ★★ **把刚选好的方向项清掉了**（`mark1` 由 1 → **0**）。

### 2.2 修后真机（★ 建成）

```
=== ① 跑 `pre_call` ===
  ★ 回读选区：mark1=1 · 合计=2          ← ★★ 两个前置都在
=== ② 调目标函数 ===
  ★ 结果：**建成** ✓（'拔模1'）
```

★ 证据：`output/_probe296_draft_precall.txt` · 探针 `output/_probe296_draft_precall.py`。
★★ **探针按 `AGENTS.md` §十七 的契约调**（★ 从 `ToolSpec` 读 `inject`/`params`，★ 不手调内部实现）。

### 2.3 ★ 无残留

| 项 | 读数 |
|---|---|
| `sw_guard --scan` | ★ 弹窗 **0** 个 |
| 打开的文档 | ★ **0** 个（临时零件**关闭且未保存**） |

## 三、★★★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `mcp-server/tool_specs_batch4.py` | ★ **加 `_face_object()` / `_select_plane()`** · **改 `_pre_draft()`** · 加 `direction_plane` 参数 · `param_alias` 登记 |
| 2 | `tests/test_create_draft_pre_call_296.py` | ★ **新建判据**（6 例） |
| 3 | `tests/test_draft_official_entry.py` | ★★ **订正一条恒红的陈旧判据**（★ 见 §五） |
| 4 | `specs/296-create-draft-pre-call/*` | ★ 本规格四件套 |

★ **未改**：`scripts/sw_sheet_metal.py`（★ 边界冻结 —— `create_draft` 的签名与 `InsertMultiFaceDraft` 调用**一字未动**）。

## 四、★★★ 判据形态（★ 为什么用「传递闭包」）

★★ `test_pre_call_raises_when_the_plane_is_missing` **不是**只看 `_pre_draft` 一个函数 ——
★ 它取 `_pre_draft` 及其**传递闭包**（★ `_called_chain`）。

★★★ **依据**（`MEMORY.md` 规则 21 逐字）：
> 「**「只看点式调用」= 空判据** —— 调用**藏在共用骨架**里时读成 **0 个调用** ⇒ 改前也是绿的」
> ★ 修法：把骨架名也列为禁止项 + 同时收**裸名调用**，并做**传递闭包**。

★ 本处的形态：★「前置没备齐就抛」这个性质**可以**落在 `_pre_draft` 自己身上、
★ 也**可以**落在它调用的帮手（`_select_plane` / `_face_object`）身上 ⇒ ★★ 只看一个函数会**误报**
（★ 实测：第一版判据就是这么红的）。

## 五、★★★ 顺带修掉一条**恒红的陈旧判据**（★ 非本轮引入）

★ `tests/test_draft_official_entry.py::test_runtime_status_says_untested_not_verified`
★★ **在我改动之前就是红的**（★ 用 `git stash` 隔离证明）：

| ★ 事实 | ★ 值 |
|---|---|
| `HEAD` 的 `SHEET_METAL_RUNTIME_STATUS["create_draft"]` | `(False, …)` |
| 工作树的（★ **283 改的**） | **`(True, …)`** |
| 那条判据断言的 | ★ **`"None"`** |

⇒ ★★★ **283 把状态升成了 `True`，却没同步改这条判据** ⇒ ★ 它变成**恒红**
（★ `MEMORY.md` 规则 28 逐字：「改实现前先搜『有没有测试钉住旧行为』 ——
★ 不同步改就等于**在断言错的东西**」）。

★ **订正后的判据保留原意图**（「不许无证据地自称可用」）：
★★ **状态与真机证据必须一致** —— ★ 若为 `True`，★ 283 的**真机读数必须存在且含 `拔模1`**。

## 六、★★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_create_draft_pre_call_296.py -q
FAILED tests/test_create_draft_pre_call_296.py::test_pre_call_selects_both_a_plane_and_a_face
FAILED tests/test_create_draft_pre_call_296.py::test_direction_is_a_declarative_param
FAILED tests/test_create_draft_pre_call_296.py::test_pre_call_raises_when_the_plane_is_missing
3 failed, 3 passed
```

## 七、★ 生成器链（★ 改了 `mcp-server/` 与 `tests/`）

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate296.log` |

## 九、未过门（如实登记）

| # | ★ 项 | ★ 说明 |
|---|---|---|
| ① | ★ `direction_plane` **只支持基准面名** | ★ 283 的真机配方用的是 `Front Plane`；★ 若用户想给**非基准面**的方向项（如某个平面型面），★ **本工具表达不了** ⇒ ★ 如实登记，★ **不假装支持**。 |
| ② | ★ 面的选择只支持 `index:<n>` / `__current_selection__` | ★ 沿用本仓 `sw_selection_spec` 的既有口径（★ 事实 32：面**不能按名字选**）。 |
| ③ | ★ 4 处 `needs-feature-data` · `DeleteRenderMaterial` · 223 的 B1–B5 | ★ 属**其它**已登记项，★ 不在本规格范围内。 |
