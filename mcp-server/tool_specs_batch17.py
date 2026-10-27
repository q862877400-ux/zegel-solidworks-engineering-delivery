"""第十七批 MCP 工具声明：**圆形阵列 / 旋转凸台** 2 个 —— ★ 并**解决规则 2 的角度边界**。

## 来源与筛选（2026-10-01 轮 211，Spec Kit `130`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`。
队列 A6 要解决的是：`sw_part` 里两个函数的形参是 **`angle_rad`**，而并入规则 2 要求
「**角度参数必须 `_deg` 结尾**，换算只在边界做一次」⇒ 它们**上批被留批**（见 `batch16` 头部那张表）。

## ★★★ 本批先把「换算边界在哪」定死（**不是改名**）
```
⚠⚠ **改名不够，而且会静默出错**：
   `param_alias={"angle_deg": "angle_rad"}` **只改名、不换算** ⇒
   用户填 `90`（度）会被当成 `90 **弧度**` 传给目标函数 ⇒ **几何静默错**（90 rad ≈ 5157°）。
⇒ ★ 规则 2 的措辞是「换算**只在边界做一次**」—— 所以要用**能换算**的那个机制：
   注册器的 `derived_args`：「从已声明的标量入参派生额外实参，返回的字典**并进**调用目标函数的关键字实参里」。
★ **既有先例**（同一形状，`tool_specs_batch3.py`）：
       param_alias=dict({"sketch_name": "sketch_ref"},
                        **_consumed("bend_radius_mm", "angle_deg", ...)),
       derived_args=lambda p: {"spec": _one_bend_spec(p)},
   其中 `_consumed(*names)` = 「这些入参由 `derived_args` 消费，**不传给目标函数**」
   （不标记就会被当 kwarg 传进去 ⇒ `TypeError`）。
★ **而换算函数的家已经存在**，不需要新建：
       `scripts/sw_connect.py`  L929 `def mm(value)`（米→毫米族）
       `scripts/sw_connect.py`  L934 `def deg(value)` → 本机实测 `deg(90) == 1.5707963267948966`（= π/2）
   ⇒ ★ 规则 2 点名的 `sw_connect.mm()` 是**同一族的长度换算**；角度用**同一个模块的 `deg()`**。
```

| 取 | 函数（真实签名，`inspect.signature` 取）| MCP 表面 |
|---|---|---|
| ✅ | `sw_part.circular_pattern(model, feature_name, axis_name, angle_rad, count, equal_spacing=True)` | `angle_deg` + 换算 |
| ✅ | `sw_part.revolve_boss(model, sketch_name, angle_rad, axis_sketch_name=None)` | `angle_deg` + 换算 |

## ⚠ 一处**归一化**（不是为了好看，是为了不改变语义）
```
`revolve_boss` 的 `axis_sketch_name` 默认是 **`None`**（不是空串）。
★ 而 MCP 表面的字符串参数默认值习惯写 `""` ⇒ 若把 `""` 直接传进去，
  目标函数拿到的是 `""` 而不是 `None` —— **那可能改变分支**。
⇒ 处置：把 `axis_sketch_name` **也交给 derived_args**，在里面做 `p.axis_sketch_name or None`，
  即 **`""` → `None`**（与目标函数的默认对齐）。★ 这就是它被 `_consumed` 的原因。
```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch17.py
# 定位:   「孤立能力暴露」第十七批（Spec Kit `130`）—— 圆形阵列 + 旋转凸台，
#         并落定规则 2 的**角度换算边界**（`_consumed` + `derived_args` + `sw_connect.deg`）。
# 官方签名依据: 不适用（只做参数搬运）；换算助手依据 `scripts/sw_connect.py` 的既有 `deg()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH17"]


def _consumed(*names: str) -> dict:
    """构造 `param_alias`：**这些入参由 `derived_args` 消费，不传给目标函数**。

    ★ 与 `tool_specs_batch3.py` / `batch4.py` 里的同名函数**同一约定**（先例，不另立一套）。
    注册器会把每个声明参数当 kwarg 传给目标函数，而 `angle_deg` 目标函数**并不接受**
    ⇒ 不标记就 `TypeError`。**⇒ 显式，不靠猜。**
    """
    return {n: None for n in names}


def _radians_of_deg(p) -> dict:
    """把声明的 `angle_deg` 换算成目标函数要的 `angle_rad`（★ **换算只做一次**）。

    ⚠ 用 `sw_connect.deg()`（既有助手，与规则 2 点名的 `mm()` 同族），**不在这里手写 π/180** ——
    换算只有一个家，免得两处口径分叉。
    """
    from scripts.sw_connect import deg

    return {"angle_rad": deg(float(p.angle_deg))}


SPECS_BATCH17 = [
    # 签名: def circular_pattern(model, feature_name, axis_name, angle_rad, count, equal
    # _spacing=True)
    ToolSpec(
        name="solidworks_circular_pattern",
        title="Create Circular Pattern",
        module="sw_part",
        function="circular_pattern",
        inject="model",
        #: ★ 显式声明为写：实现调 `FeatureManager.FeatureCircularPattern4` **创建特征**。
        #: ⚠ 效应解析器按**成员名前缀**判（`effects.WRITE_VERBS`），而
        #:   `FeatureCircularPattern4` 以 `Feature` 开头 ⇒ 前缀匹配不到 `Pattern`
        #:   ⇒ 会判 `unknown` ⇒ 按 I5 不予准入。这是**判据盲区**，不是该工具真的效应未知
        #:   ⇒ 在此显式声明，不靠解析器猜。
        read_only=False,
        param_alias=dict(_consumed("angle_deg")),
        derived_args=_radians_of_deg,
        params=[
            Param("feature_name", str, description="Name of the feature to pattern."),
            Param("axis_name", str, description="Name of the axis to revolve around."),
            Param(
                "angle_deg",
                float,
                description="Total pattern angle in DEGREES (rule 2). Converted to radians "
                "exactly once at this boundary via sw_connect.deg().",
            ),
            Param("count", int, description="Number of pattern instances."),
            Param(
                "equal_spacing",
                bool,
                default=True,
                description="Space the instances equally.",
            ),
        ],
        evidence=(
            "Create a circular pattern about an axis."
        ),
        doc="Create a circular pattern about an axis.",
    ),
    # 签名: def revolve_boss(model, sketch_name, angle_rad, axis_sketch_name=None)
    ToolSpec(
        name="solidworks_revolve_boss",
        title="Create Revolve Boss",
        module="sw_part",
        function="revolve_boss",
        inject="model",
        param_alias=dict(_consumed("angle_deg", "axis_sketch_name")),
        derived_args=lambda p: dict(
            _radians_of_deg(p),
            #: ⚠ 归一化：`""` → `None`（与目标函数默认值对齐，见批头说明）
            axis_sketch_name=(str(p.axis_sketch_name) or None),
        ),
        params=[
            Param("sketch_name", str, description="Profile sketch NAME."),
            Param(
                "angle_deg",
                float,
                description="Revolve angle in DEGREES (rule 2). Converted to radians exactly "
                "once at this boundary via sw_connect.deg().",
            ),
            Param(
                "axis_sketch_name",
                str,
                default="",
                description='Axis sketch name; omit ("") to use the function default (None).',
            ),
        ],
        evidence=(
            "Revolve a profile sketch into a boss feature. ⚠ This call is routed through a closed-source COM backend — "
            "see docs/known-facts.md."
        ),
        doc="Revolve a profile sketch into a boss feature. ⚠ This call is routed through a "
        "closed-source COM backend — see docs/known-facts.md.",
    ),
]
