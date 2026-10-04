# T003 抽查（第二份）—— `recon/bunny-L2-official-member-calls.md`

> 依据：SPEC `202-user-coverage-gaps` 的 **T003**（P0）逐字：「逐条**拿官方原文抽查**侦察结论 ——
> 宪法 §III「**专挑最容易编造处**」」✓
> 脚本 `tools/spotcheck_t003_l2.py`（纯静态）· 机器可读 `output/t003-spotcheck-l2.json` ✓

## 一 · 抽到了什么

L2 自称「函数总数 **83** / 调用了至少一个官方成员的 **67** / 全文去重后的官方成员名共 **143** 个」。

我的脚本从那张对照表的第 4 列解出：**数据行 83 行 · 去重成员名 143 个** —— **与它的自称一字不差**。

## 二 · 判据① 逐个成员名核官方源

```
143 个名字逐个去 C:/swapi/types/** 查有没有一页
⇒ 找到 141 / 143，没找到 2 个
```

| 没找到的 | 出现在的函数 | 官方真名 | 性质 |
|---|---|---|---|
| `CreateFirstAngleViews2` | `create_adaptive_standard_views` · `create_standard_views_with_projection` | **`Create1stAngleViews2`**（`IDrawingDoc`，`bool Create1stAngleViews2(string ModelName)`） | **拼写差异**（`1st` 非 `First`） |
| `GetModelViewManager` | `get_model_view_manager` | **`ModelViewManager`**（`IModelDoc2`，**属性**，`{get;}`） | **拼写差异**（官方无 `Get` 前缀） |

⇒ 143 个名字**没有一个是凭空编造的** —— 2 个是**写法不准**。

## 三 · 判据② 它 §五 那条代码断言

它说：「`dict[str, Any]` 用了，但顶部没有 `from typing import Any`，也没有 `from __future__ import annotations`」。

我读源码核：**成立** —— 用到 `dict[str, Any]` 为真，两个 import 都不在，顶部 import 只有
`math` / `re` / `fractions.Fraction` / `pathlib.Path` / `scripts.sw_preflight` / `scripts.sw_connect` /
`scripts.sw_drawing_view_types`。

## 四 · 那 2 个名字的**去向**（这才是重点）

### `CreateFirstAngleViews2`

代码里 **4 处**用它、**`Create1stAngleViews2` 0 处**：
```
L838  ("CreateFirstAngleViews2", "Create3rdAngleViews2")     ← 候选元组
L889  if method_name == "CreateFirstAngleViews2"
L974  method_name = "CreateFirstAngleViews2" if projection == "first_angle" else …
```
★ 它经 `_safe_member` 守卫（`docs/signature-audit.md` 已记：「⚠ **官方拼写是 `1st` 非 `First`**｜✅ 守卫写法正确」）。

**而本仓把这处失败记成的是**：
```
create_standard_views_with_projection(drw, part_path, "first_angle") 回 blocked
  error_code: DRAWING_PROJECTION_API_UNAVAILABLE · method: CreateFirstAngleViews2
⇒ 结论写成「所以那条路走不通（该 API 不可用）」
```
（见 `capabilities.yaml` · `docs/dead-ends.md` · `ROADMAP.md`）

⇒ **两处记录各自都对、而没有被连起来**：`signature-audit.md` 知道拼写错、
`dead-ends.md` 说 API 不可用 —— **而"第一角投影视图"这个官方成员（`Create1stAngleViews2`）是存在的、带 ModelName 一个参数**。
⇒ 所以那个 `blocked` 的**归因是错的**：真正的直接原因是候选名拼错，不是 API 不存在。

⚠ **不进结论的部分**：我没有在真机上用正确拼写试过 ⇒ **不能说"改成 `1st` 就能用"**。
本条能说的是：**"该 API 不可用"这个结论缺少一个必要对照**（用正确拼写试一次）。

### `GetModelViewManager`

`get_model_view_manager()`（L2888-2893）逐字：
```python
def get_model_view_manager(model):
    """取 IModelViewManager（属性，不是方法）。"""
    manager = get_com_member(model, "GetModelViewManager")
    if manager is None:
        raise RuntimeError("IModelDoc2.GetModelViewManager() 返回 None")
    return manager
```
★ docstring 自己写着「**属性，不是方法**」，而代码要的是 `Get` 前缀名。

而 `sw_connect.get_com_member` 的实现开头是 `member = getattr(obj, attr_name)` ——
**没有 try 包裹** ⇒ 对不存在的成员**抛 `AttributeError`**、**不会走到 `if manager is None`**。

⚠ **这仍是"候选 bug"、不是"已证 bug"**：我没有在真机上跑过这条路径。
判据缺口是：**它实际报的是 `AttributeError` 还是别的** —— 那要真机一跑才知道。
（★ 本轮真机被另一会话占着：`SW_MUTEX_TIMEOUT`。）

## 五 · 汇总

```
成员名       141 / 143 在官方源找到（2 个是拼写差异，非编造）
自称 143     ✅ 与实际解出的 143 一致
§五 代码断言  ✅ 成立
行号口径     L2 自己在第 5-6 行声明「以 ast 为准，read 工具有 +2~+5 偏移」⇒ 口径写明，好
新增线索     2 处拼写差异都写进了代码（不只在稿子里）⇒ 值得各自真机核一次
```

## 六 · 可复用判据

**「侦察稿里的拼写错」与「代码里的拼写错」是两件事，而只有后者会变成 bug。**
本轮 143 个名字里 2 个不准 —— 若只停在稿子上，它们无害；而它们**都进了代码**，
所以抽查的价值不在"稿子准不准"，在于**把稿子的名字回溯到代码里去看它有没有被用**。
