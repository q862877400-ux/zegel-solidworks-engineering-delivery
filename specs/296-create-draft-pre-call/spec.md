# Spec — **`create_draft` 的 `pre_call` 补上「方向项」（mark 1）**：把 283 的真机配方接进工具层

**Feature**: `specs/296-create-draft-pre-call/`
**日期**: 2026-10-10
**上游**: `specs/283-create-draft-machine-verified/`（★ 真机建成 `拔模1`）· `specs/239-draft-official-entry/`（★ 路径改对）
**触发**: ★ 收 `AUTO_HANDOFF.md` ④ 段登记项 **②**：★ 「`create_draft` 的 `pre_call` 接线（★ 283 真机**已建成** ⇒ 只差接线）」。

---

## 一、★★★★ 先量：283 已证明**需要两个选择**，而 `pre_call` 只给了**一个**

★★ 283 的真机读数逐字（`output/_probe283_draft_dir.txt`）：

```
★ 单变量：**mark 1 上挂什么**
  ★ Front Plane  + 面#0 ⇒ 选中 2 · **成功** ✓（'拔模1'）
★★ 结论：★ **`create_draft` 真机建出来了** ✓（方向项 = Front Plane · 面#0）
```

★★ 而 283 的**读数 1** 把另一半钉死了：★ **只给面**（6 面 × 3 标记 = **18 臂**）⇒ **全失败**，
★ 报文**恒定**「**此拔模方向尚未定义。**」⇒ ★★ **不是选错面、也不是选错 mark**。

★★★ **⇒ 结论**：`create_draft` 的前置是**两个**选择 ——
★ **方向项（mark 1 · 一个平面）** + ★ **待拔模面（mark 2）**。

★ 而**工具层现在只做了一件**（`mcp-server/tool_specs_batch4.py`）：

```python
def _pre_draft(params):
    _select(params, "FACE")        # ★ 只选了面（★ mark 由 resolve_selection 内部定）
```

⇒ ★★★ **于是「283 真机建成」这个结论，经工具层**根本复现不了**：
★ 工具层少给一个前置 ⇒ ★ 真机会报「**此拔模方向尚未定义。**」
⇒ ★★ 这正是**事实 503** 那一族：「**代码里写了**」≠「**真机上前置真的上了**」。

---

## 二、★★★★ 官方依据（★ 逐字）

| 源 | ★ 逐字 | ★ 用途 |
|---|---|---|
| `C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md` | 「selections must be made with `IModelDocExtension::SelectByID2` (**direction mark 1**, faces to draft **mark 2**, draft edges **mark 4**)」 | ★★ **两个选择 + 各自 mark** |
| `scripts/sw_sheet_metal.py::create_draft` 的 docstring | 「调用前必须先用 `IModelDocExtension::SelectByID2` 选好（官方 `## Remarks`）：方向项 **mark 1**、待拔模面 **mark 2**、拔模边 **mark 4**」 | ★ 实现层的**自述**（★ 283 证明它是**对的**） |
| `output/_probe283_draft_dir.txt` | 「`Front Plane` + 面#0 ⇒ 选中 2 · **成功**（`拔模1`）」 | ★★ **真机配方**（★ 本轮的**验收靶子**） |

---

## 三、需求

### FR-001 ★★★ `pre_call` 必须**同时**建立两个选择（方向项 mark 1 + 面 mark 2）
- **验收场景**：`test_pre_call_selects_both_a_plane_and_a_face` 通过。

### FR-002 ★★★ 方向项必须**可声明**（★ 规则 3：不给裸坐标）
- **验收场景**：`test_direction_is_a_declarative_param` 通过
  （★ 工具参数里有 `direction_plane`，★ 取值为**平面名**，★ 不是坐标）。

### FR-003 ★★★ **前置没备齐必须抛**（★ 不许静默继续）
- **验收场景**：`test_pre_call_raises_when_the_plane_is_missing` 通过
  （★ 平面名非法 ⇒ 抛，★ 不是"选了 0 个继续调"）。

### FR-004 ★★★ 判据必须**能红**（★ 事实 62）
- **验收场景**：`test_criterion_is_red_able` 通过（★ 纯函数喂**旧形态** ⇒ 报错）。

### FR-005 ★★ **边界冻结**：★ 不改 `scripts/sw_sheet_metal.py::create_draft` 的签名与调用
- **验收场景**：`test_implementation_signature_untouched` 通过。
