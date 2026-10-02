"""第十八批 MCP 工具声明：**草图只读查询** 4 个（砌墙 W1）。

## 来源与筛选（2026-10-01 轮 222，Spec Kit `131`）

候选源：`D:/AI/SW/output/orphan-capabilities.json` + `scripts/sw_sketch.py`。
`sw_sketch` 有 **25 个公开函数没挂**，而它们**首参全是 `sketch`**（COM 对象），
不在既有注入点（`model` / `sw_app` / `study`）里 ⇒ 需要一层「**从 model 取到 sketch 对象**」。

## ★★★ 包装层的形状是**真机探针定的**，不是猜的
```
`tools/probe_sketch_object_routes.py`（轮 220，SW 2026 SP4.1）：
                     草图打开中      草图已关闭
  model.GetActiveSketch2   草图1      **None**
  SketchManager.ActiveSketch 草图1    **None**
  按名取（FeatureByName→GetSpecificFeature2）  草图1   **草图1** ✓
⇒ ★ **草图一关，"活动草图"两条路都取不到；只有按名取还活着。**
  而调用方的实际用法恰恰是「草图建完了，看看里面有什么」⇒ **那时草图已关闭**。
⇒ 所以包装层**只能走按名取**（`sw_sketch.sketch_by_name`，本轮新增）。
⚠ 另注：`sw_part._find_cached_sketch_ref` 走**进程内缓存** ⇒ **MCP 是独立进程、缓存为空**
  ⇒ **不能用于工具层**；`sketch_by_name` 是无状态的。
```

## ★★ 为什么要"只回读数的薄函数"（而不是直接挂 `get_lines`）
```
★ 实测（`output/sketch-getter-shapes.json`，轮 141）：`get_lines` 返回的是**数值数组**，
  **每条线 12 个 float**（1↔12、2↔24、3↔36）；`get_arcs` 每条 16 个。
⇒ AI 问「草图里有几条线」，拿回 **36 个浮点数**没法用。
⇒ 所以本轮在 `scripts/sw_sketch.py` 里加了 **`count_lines` / `count_arcs` / `count_segments`**
  三个薄函数，把"数值数组"翻译成**条数**；条数的除数有真机证据。
⚠ 若官方返回长度**不是除数的整数倍** ⇒ 薄函数 **抛错**，**不静默圆整**（形状变了要被看见）。

## ★ 为什么不用 `extra_op`
`batch1` 立的规矩是「**全部声明式**」。查过它当初不用 `extra_op` 的原因：
**是加了 `inject` 之后就不需要了**，不是它有问题。
⇒ 本批沿用同一方向：**能力落在 `scripts/`（薄函数，别的代码也能用），不落在工具声明里。**

## 参数
| 参数 | 说明 |
|---|---|
| `sketch_name` | 草图特征名；★ **留空 = 用当前活动草图的**名字（`sw_part.current_sketch_name`）。★ **已关闭的草图也能按名取** |

★ `inject` **不设**（默认 `''` ⇒ 不注入）—— ★ 因为目标函数要的是 **`sketch`** 而不是 `model`；
  `model` 由 `derived_args` 自己连一次（照 `tool_specs_batch4.py::_model` 的既有模式）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch18.py
# 定位:   「孤立能力暴露」第十八批 / 砌墙 W1（Spec Kit `131`）—— 草图只读查询。
# 官方签名依据: 不适用（只做参数搬运）；取草图对象的依据是真机探针 `tools/probe_sketch_object_routes.py`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH18"]


def _consumed(*names: str) -> dict:
    """构造 `param_alias`：**这些入参由 `derived_args` 消费，不传给目标函数**。

    ★ 与 `tool_specs_batch3/4/17.py` 里的同名函数**同一约定**（先例，不另立一套）。
    """
    return {n: None for n in names}


def _model():
    """取活动文档（照 `tool_specs_batch4.py::_model` 的既有模式）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _sketch_args(p) -> dict:
    """把声明的 `sketch_name` 解析成目标函数要的 **`sketch`（ISketch 对象）**。

    ★ 留空 ⇒ 用**当前活动草图**的名字；★ **已关闭的草图也能按名取**（真机探针证明，见批头）。
    ⚠ 找不到 / 不是草图 ⇒ `sketch_by_name` 抛错（**选不中要报错，不静默**）。
    """
    from scripts.sw_sketch import resolve_sketch

    #: ★ 用 resolve_sketch 而**不是** sketch_by_name + current_sketch_name：
    #:   真机验证抓到 —— 草图关闭时 current_sketch_name 回**英文 fallback**「Sketch1」，
    #:   而中文 UI 下真名是「草图1」⇒ 直接按那个名字找**必然找不到**（第一次真机调用即失败）。
    #:   resolve_sketch 试中英文候选名，并在都失败时从**特征树**兜底（语言无关）。
    model = _model()
    return {"sketch": resolve_sketch(model, str(getattr(p, "sketch_name", "") or ""))}


#: 本批 4 个工具共用的参数表（只有 `sketch_name`）
_PARAMS = lambda: [                                            # noqa: E731
    Param("sketch_name", str, default="",
          description="Sketch feature name (e.g. \"Sketch1\" / \"草图1\"). ★ Leave empty to use "
                      "the CURRENT sketch. ⚠ A CLOSED sketch is still reachable by name — that is "
                      "the only reliable route (the probe showed GetActiveSketch2 / ActiveSketch "
                      "both return None once the sketch is closed)."),
]

_ALIAS = lambda: dict(_consumed("sketch_name"))                # noqa: E731

SPECS_BATCH18 = [
    ToolSpec(
        name="solidworks_sketch_count_lines",
        title="Count Sketch Lines",
        module="sw_sketch", function="count_lines",
        param_alias=_ALIAS(),
        derived_args=_sketch_args,
        params=_PARAMS(),
        doc="Count the straight LINES in a sketch. ⚠ Use this rather than the raw getter: "
            "the underlying ISketch call returns a NUMBER array (12 floats per line), which "
            "cannot answer \"how many lines\".",
    ),
    ToolSpec(
        name="solidworks_sketch_count_arcs",
        title="Count Sketch Arcs",
        module="sw_sketch", function="count_arcs",
        param_alias=_ALIAS(),
        derived_args=_sketch_args,
        params=_PARAMS(),
        doc="Count the ARCS in a sketch (the underlying call returns 16 floats per arc). "
            "⚠ A full CIRCLE counts as ONE arc — verified on a real machine (2026-10-01): a sketch "
            "with 1 line + 1 circle reports count_lines=1, count_arcs=1, count_segments=2.",
    ),
    ToolSpec(
        name="solidworks_sketch_count_segments",
        title="Count Sketch Segments",
        module="sw_sketch", function="count_segments",
        param_alias=_ALIAS(),
        derived_args=_sketch_args,
        params=_PARAMS(),
        doc="Count ALL segments in a sketch. ⚠ Not the same as the line count: segments are the "
            "total geometry units; lines are one kind among them.",
    ),
    ToolSpec(
        name="solidworks_sketch_is_3d",
        title="Is 3D Sketch",
        module="sw_sketch", function="is_3d_sketch",
        param_alias=_ALIAS(),
        derived_args=_sketch_args,
        params=_PARAMS(),
        doc="Whether the sketch is a 3D sketch (ISketch.Is3D).",
    ),
]
