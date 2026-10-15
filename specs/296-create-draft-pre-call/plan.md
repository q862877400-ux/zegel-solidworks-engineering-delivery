# Plan — **`create_draft` 的 `pre_call` 补上「方向项」（mark 1）**

**Feature**: `specs/296-create-draft-pre-call/`
**日期**: 2026-10-10

---

## 一、施工顺序

| # | 步 | ★ 内容 | ★ 为什么 |
|---|---|---|---|
| 1 | **先量** | 读 283 的两条真机读数（18 臂全失败 · 配方成功）+ 工具层现状 | ★ 不先量就改 = 赌 |
| 2 | **定性** | 工具层 `_pre_draft` **只选面** ⇒ 与 283 的「需要两个」**不符** | ★ 证明缺的是**接线** |
| 3 | **写判据（先红）** | `tests/test_create_draft_pre_call_296.py`（6 条） | ★ 含「能红」的负例（事实 62） |
| 4 | **跑红基线** | ⇒ **`3 failed, 3 passed`** | ★ 三条对照**本来就该绿** |
| 5 | **改工具层** | 加 `direction_plane` 参数 + `_select_plane()` + 重写 `_pre_draft()` | ★ 接 283 的配方 |
| 6 | **跑绿（离线）** | ⇒ **6 passed** | ★ 离线绿 ≠ 真机绿 |
| 7 | ★★ **真机验** | 走 `sw_guard` 跑 `output/_probe296_draft_precall.py`（★ **按 §十七 的契约调**） | ★★ **离线绿不算数**（铁律 2） |
| 8 | ★★★ **真机发现真 bug** | ★ 第一版 `mark1=0`（★ 面选择**清空了**方向项）⇒ **改顺序 + `append=True` + 显式 mark** | ★★ 这正是「真机验」的价值 |
| 9 | **真机复验** | ⇒ ★ **`mark1=1` · 合计=2 · 建成 `拔模1`** ✓ | ★ |
| 10 | **无残留** | `sw_guard --scan` = 0 弹窗 · 打开文档 = **0** | ★ `MEMORY.md` 事实 76 |
| 11 | **顺带修陈旧判据** | `test_draft_official_entry.py` 那条**恒红**的（★ `git stash` 证明非本轮引入） | ★ `MEMORY.md` 规则 28 |
| 12 | **生成器链 + 门禁 + 回写** | 7/7 · `release_check` · 四处状态 | ★ `GOAL.md` §五 |

---

## 二、★★★ 真机发现的那个 bug（★ 本轮最重要的读数）

| ★ 版本 | ★ `_pre_draft` 的写法 | ★ 真机读数 | ★ 结果 |
|---|---|---|---|
| ★ 第一版 | `_select_plane(mark=1)` → `_select(params, "FACE")` | ★ **`mark1=0` · 合计=1** | ★ **失败**（`InsertMultiFaceDraft 创建失败`） |
| ★★ 修后 | `ClearSelection2` → `_select_plane(mark=1)` → `_select_com_object(face, append=True, mark=2)` | ★★ **`mark1=1` · 合计=2** | ★★ **建成 `拔模1`** ✓ |

★★ **根因**：`_select` 内部走 `resolve_selection` → `select_object(append=False)`
⇒ ★★ **它按 `append=False` 选面，把刚选好的方向项清掉了**。

★★★ **可复用的定则**（★ 本轮新增）：
> **「两个前置」的选择必须**同一个 append 语义**地建立** ——
> ★ 先选的那个用 `append=False`、后选的必须 `append=True`；
> ★ **每个 mark 都要单独回读**（`GetSelectedObjectCount2(mark)`），
> ★ 不能只看**合计**（合计 = 2 也可能是「一个选择被算了两次」）。

---

## 三、★ 判据设计

| ★ 判据 | ★ 它防的是什么 |
|---|---|
| `test_pre_call_selects_both_a_plane_and_a_face` | ★★ 只给一个前置（★ 283 证明必失败） |
| `test_direction_is_a_declarative_param` | ★ 方向项**无法表达**（★ 规则 3：不给裸坐标） |
| `test_pre_call_raises_when_the_plane_is_missing` | ★★ 静默继续（★ 把「前置没上」记成「能力不成」） |
| `test_criterion_is_red_able` | ★ 空判据（★ 事实 62） |
| `test_implementation_signature_untouched` | ★ 边界漂移（★ 本轮**只接 `pre_call`**） |
| `test_machine_recipe_is_recorded` | ★ 靶子丢失（★ 判据的期望值来自 283 的真机读数） |

★★ `test_pre_call_raises_when_the_plane_is_missing` 用**传递闭包**（★ 规则 21）——
★ 因为「抛」**可以**落在 `_pre_draft` 上、★ 也**可以**落在它调用的帮手身上。

---

## 四、★ 官方/仓内依据

| 源 | ★ 逐字 | ★ 用途 |
|---|---|---|
| `C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md` | 「direction **mark 1**, faces to draft **mark 2**, draft edges **mark 4**」 | ★★ **两个选择 + 各自 mark** |
| `output/_probe283_draft_dir.txt` | 「`Front Plane` + 面#0 ⇒ 选中 2 · **成功**（`拔模1`）」 | ★★ **真机配方**（★ 验收靶子） |
| `output/_probe283_draft.txt` | 「18 臂 · 报文恒定『此拔模方向尚未定义。』」 | ★ 排除「选错面/mark」 |
| `AGENTS.md` §十七 | 「按 `ToolSpec` 的契约调，别手调内部实现」 | ★ 探针的**调用方式** |
| `MEMORY.md` 规则 21 | 「**「只看点式调用」= 空判据** … 修法：… 做**传递闭包**」 | ★ 判据形态 |
| `MEMORY.md` 规则 28 | 「改实现前先搜『有没有测试钉住旧行为』」 | ★ 陈旧判据的**处置依据** |
| `MEMORY.md` 规则 37 | 「按对象选 + 带 mark」= `CreateSelectData().Mark` + `IEntity::Select4` | ★ 修法的**实现路径** |
