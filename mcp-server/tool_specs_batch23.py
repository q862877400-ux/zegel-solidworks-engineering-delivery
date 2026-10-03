"""第二十三批 MCP 工具声明：**倒角 / 圆角** 2 个（砌墙 W4 续 / Spec Kit `137`）。

## ★★★ 本批第一次用「规则 3 的声明式 `selection`」驱动**建特征**工具
```
★ 前面几批的包装形状：
   W1（只读）      ：`derived_args` 取对象
   W4（写草图）    ：`param_alias` 改名
   W4 续（拉伸）   ：`param_alias` 改名
★ 本批的包装形状：**`pre_call` —— 调用目标函数之前先把"要倒哪条边"选好**。
   `sw_part.chamfer(model, distance, angle_deg=45)` 与 `sw_part.fillet(model, radius, edges=None)`
   ★ **都没有 `edges` 参数用于传对象** ⇒ 它们作用在**当前选择**上
   ⇒ 所以对外的 `selection`（规则 3 的声明式形态）由 `pre_call` 解析成真实选区。
★ 机制复用 `tool_specs_batch4.py` 的既有一行：
     `resolve_selection(_model(), params.selection, "EDGE")`
   ★ 不另立一套（`batch1` 立的规矩：能声明式就声明式，别自造机制）。
```

## ★ 参数命名（规则 2）
```
能力层形参：`distance`（倒角距离）· `radius`（圆角半径）—— **都不带 `_mm`**
⇒ 对外用 `param_alias` 改成 `distance_mm` / `radius_mm`。
★ `angle_deg` 已是合规名 ⇒ 直接用（W4 那份核对已确认它在 AngleDistance 下才有效）。
★ **能力层一行不改**（照 W4 的定则）。
```

## ★★ 调用形态**已按铁律 4 核过是对的**（W4 续那批做的核对，见事实 164）
```
`InsertFeatureChamfer(Options, ChamferType, Width, Angle, OtherDist, VertexChamDist1/2/3)`
   · 实现传 `(Options=4, ChamferType=1, Width=distance, Angle=angle_rad, 0,0,0,0)`
   · `swChamferType_e.swChamferAngleDistance = **1**`（swapi 与出厂反射**两源一致**）
   · 官方说明：Width/Angle **只在 `swChamferAngleDistance` 下有意义** ⇒ ★ **一致** ✓
   · `Options = 4` = `swFeatureChamferTangentPropagation`
⇒ ★ 所以本批**不改能力层**，只在它前面加一层"把边选好"。
```

## ⚠⚠ 本批要真机回答的**一个未知**（★ 不能假设）
```
`chamfer` / `fillet` **没有 `edges` 参数** ⇒ ★ 它们**真的作用在当前选择上吗**？
   · 若是 ⇒ 本批的设计成立；
   · ★ 若它们**忽略选择、作用在"所有边"或默认边**上 ⇒ **本批的 `selection` 就是假设计**，
     必须**如实记录并改设计**（不能把假设计当成功）。
⇒ 证据脚本里**必须**包含这个对照：**"选了一条边"与"不选"的结果是否不同**。
```

## ★ 断言方式（本批可用什么读数）
```
★ 项目里**没有"体积 / 质量属性"的工具**（已核：能力层与 MCP 都没有）
⇒ 用**特征树 + 特征名**断言：倒角后应出现「倒角1」、圆角后应出现「圆角1」
   （读数走 `solidworks_collect_model_summary` 的那条能力层路径）
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch23.py
# 定位:   「孤立能力暴露」第二十三批 / 砌墙 W4 续（Spec Kit `137`）。
# 官方签名依据: 不适用（只做参数搬运）；形态依据见上「已按铁律 4 核过」
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH23"]


def _consumed(*names: str) -> dict:
    """这些入参由 `pre_call` 消费（选中边），**不传给目标函数**。

    ★ 与 `tool_specs_batch3/4/17/18.py` 里的同名函数**同一约定**（先例，不另立一套）。
    """
    return {n: None for n in names}


def _model():
    """取活动文档（照 `tool_specs_batch4.py::_model` 的既有模式）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _select_edge(params):
    """★ **调用目标函数之前**：把 `selection`（声明式）解析成真实选区。

    ★ 复用 `sw_selection_spec.resolve_selection` —— 与 `batch4` 的 `_select` 同一行逻辑。
    ★ 返回选区计数；`0` 表示没选中 ⇒ `resolve_selection` 自己会抛错（不静默）。
    """
    from scripts.sw_selection_spec import resolve_selection

    return resolve_selection(_model(), params.selection, "EDGE")


_SEL = ("Declarative EDGE selection: '__current_selection__' (use whatever is already selected) "
        "or 'index:<n>' (the n-th edge on the body, 0-based). ⚠ Chamfer/fillet act on the "
        "CURRENT SELECTION — there is no edge-object parameter — so this argument is what "
        "decides which edge is modified.")
_ALIAS_SEL = lambda: dict(_consumed("selection"))                 # noqa: E731


SPECS_BATCH23 = [
    ToolSpec(
        name="solidworks_chamfer",
        title="Chamfer the Selected Edge(s)",
        module="sw_part", function="chamfer",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0 个实参 ⇒
        #:   `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidworks_part_bounding_box` 写着 `inject='model'` ✓
        param_alias={**_ALIAS_SEL(), "distance_mm": "distance"},
        pre_call=_select_edge,
        params=[
            Param("selection", str, description=_SEL),
            Param("distance_mm", float, description="Chamfer distance in MILLIMETRES."),
            Param("angle_deg", float, default=45.0,
                  description="Chamfer angle in DEGREES (used because the capability layer "
                              "requests swChamferAngleDistance)."),
        ],
        doc="Chamfer the selected edge(s). ★ The edge comes from `selection` (declarative), "
            "because the API takes no edge object — it acts on the current selection.",
    ),
    ToolSpec(
        name="solidworks_fillet",
        title="Round (Fillet) the Selected Edge(s)",
        module="sw_part", function="fillet",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0 个实参 ⇒
        #:   `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidworks_part_bounding_box` 写着 `inject='model'` ✓
        param_alias={**_ALIAS_SEL(), "radius_mm": "radius"},
        pre_call=_select_edge,
        params=[
            Param("selection", str, description=_SEL),
            Param("radius_mm", float, description="Fillet radius in MILLIMETRES."),
        ],
        doc="Round the selected edge(s) with the given radius. ★ The edge comes from `selection` "
            "(declarative) — the capability layer passes edges=None, i.e. it acts on the "
            "current selection.",
    ),
]
