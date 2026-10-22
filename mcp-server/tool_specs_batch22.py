"""第二十二批 MCP 工具声明：**拉伸族** 3 个（砌墙 W4 续 / Spec Kit `136`）。

## ★★★ 本批是**第一批能建出实体**的工具 —— 前面几批补的前置现在才真正可用
```
★ W4（`specs/135`）补了「建草图 + 画几何」，本批补「**把草图变成实体**」。
⇒ 两批合起来，本仓库第一次具备**完整的建模最小闭环**：
    建草图 → 画几何 → **拉伸成实体** → 用只读工具回读验证。
★ 而此前 MCP 里已经有 `revolve_boss` / `create_hole_feature` / 钣金 `base_flange`，
  却**连拉伸都没有**（也正因为没有草图工具而全都用不了）⇒ 本批把这条链接通。
```

## ★ 为什么只做 3 个（都是"无选择依赖"的拉伸）
```
`sw_part` 里可注入且未挂的"建特征"函数有 10 个，本批**只取拉伸族 3 个**：
   `extrude_boss`（凸台）· `extrude_cut`（切除）· `extrude_midplane`（中面/两侧对称）
★ 理由：**它们同族、语义配套、且都不需要"选择"**（只要一个草图名）⇒ 证据脚本能干净地
  写成"建草图 → 拉伸 → 回读断言"。
★ `chamfer`（倒角）**本批不做** —— 它的调用形态我已按铁律 4 核过**是对的**
  （`swChamferType_e.swChamferAngleDistance = 1`，swapi 与出厂反射**两源一致**；
   Options=4 = `swFeatureChamferTangentPropagation`），
  但 ★ **它没有 `edges` 参数** ⇒ 倒哪些边必然来自**当前选择**
  ⇒ 它需要一层**规则 3 的声明式 `selection`** 包装 ⇒ ★ **单独一批做**。
  ★ 理由：**一个批次里混两种包装形状，会让证据脚本与工具说明都变复杂**；
    而"用 selection 驱动建特征工具"在本项目是**第一次**，值得单独验证。
★ `fillet`（圆角）同理（`edges=None` ⇒ 用当前选择）⇒ 与 `chamfer` 同批。
```

## 参数命名（规则 2）
```
能力层的形参是 `depth` / `total_depth`（**不带 `_mm`**）⇒ ★ 对外用 `param_alias` 改成
`depth_mm` / `total_depth_mm`（规则 2：长度参数 `_mm` 结尾）。
★ **能力层一行不改**（照 W4 `specs/135` 的定则：对外名与对内名不同时用 `param_alias`，
  别去改能力层的形参名 —— 那会动到既有调用点）。
★ `angle_deg` 已是合规名（W4 那批的 `chamfer` 用得上）。
```

## ★ 单位：**不换算**
```
`sw_part` 的模块单位是**毫米**（既有事实 73，本机实测）⇒ 三个函数的 docstring 都明写「毫米」
⇒ ★ 本批**不做任何换算**，只把参数名带上 `_mm` —— 换算本就无需发生，
  这比"先乘 1000 再除 1000"更安全。
```

## ★★ 验证方式：读写配对（**第一次建实体**）
```
建草图（batch21）→ 画矩形/圆 → `extrude_boss(depth_mm=10)`
  ⇒ ★ **用 `solidworks_part_bounding_box` 回读断言包围盒**
     （矩形 40×20 ⇒ 期望包围盒 **40 × 20 × 10 mm**）
⇒ ★ 断言是**数字**，可复跑、可进 CI；而且它把 **batch21（写草图）→ batch22（建实体）→
  只读工具（回读）** 三批串成一条**可验证的链**。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch22.py
# 定位:   「孤立能力暴露」第二十二批 / 砌墙 W4 续（Spec Kit `136`）。
# 官方签名依据: 不适用（只做参数搬运）；被搬运函数的官方依据见 `scripts/sw_part.py` 的来源块
#          （`IFeatureManager.FeatureExtrusion3` 共 23 参数 —— 见既有事实 2）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH22"]

_SKETCH = (
    'Name of an EXISTING sketch (e.g. "Sketch1" / "草图1"). ★ Create it first with '
    "solidworks_sketch_start + solidworks_sketch_add_* + solidworks_sketch_end."
)

_DIR = "True = extrude along the sketch normal; False = reverse."


def _consumed(*names: str) -> dict:
    """★ `param_alias`：这些入参由 `derived_args` 消费，**不传给目标函数**（先例：batch17/batch3）。"""
    return {n: None for n in names}


def _m_of_mm(p, declared: str) -> dict:
    """★★★ 把声明的 `*_mm` 换算成 `IFeatureManager.FeatureExtrusion3` 要的**米**（换算只做一次）。

    ★★★★ **这是本轮真机实测定案的一处真缺陷的修复**（用户两次点破，逐字：
      「你看到的是一根线，是因为你拉伸长度太长了，离远了看着就是一根线」·
       并附 SolidWorks 深度框截图 **`84300.00mm`**）✓

    ★ 证据链（**四条独立读数，全部一致**）：
      · ★ `create_basic_part`（`server.py:1551-1556`）**每一处都调 `mm()`** ⇒ 它建的 40×40×10 盒
        质量属性回 **16000 mm³**、包围盒回 `[0.04, 0.04, 0.01]` ⇒ ★ **该盒是真 40 mm** ✓
      · ★★ ⇒ 同一个 `extrude_boss` 被喂**米**（0.01）时正确、被喂**毫米**（10）时得 10 米 ✓
      · ★ 俯视草图我按毫米给（±62）⇒ 包围盒 X = **0.131 米 = 131 mm** ⇒ ★ **草图吃毫米** ✓
      · ★★ 而拉伸高度读回 **40.0 米** ⇒ ★ **D1 吃米、而我们传的是毫米值** ✓✗
      · ★ 分辨性序列（`SetSystemValue3` 写 0.0843 / 84.3 / 84300）⇒ 只有 **0.0843** m 让包围盒
        变成 0.0843 m（= 84.3 mm）⇒ ★ **再次确认 D1 的口径是米** ✓
    ⇒ ★★ 修法：与 `batch17` 的角度那条**同形**（`_consumed` + `derived_args`），
      用 `sw_connect.mm()`（规则 2 点名的既有助手，与 `deg()` 同族）—— **不手写 /1000** ✓
    """
    from scripts.sw_connect import mm

    return (
        {"depth": mm(float(getattr(p, declared)))}
        if declared == "depth_mm"
        else {"total_depth": mm(float(getattr(p, declared)))}
    )


SPECS_BATCH22 = [
    ToolSpec(
        name="solidworks_extrude_boss",
        title="Extrude a Boss (add material)",
        module="sw_part",
        function="extrude_boss",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        #: ★★★★ 2026-10-04（接手轮）**换算修正（真机定案）** —— 原为 `{"depth_mm": "dept
        #: h"}`，
        #: 那是**只改名、不换算**，而 `FeatureExtrusion3` 的 D1 吃**米** ⇒ 传 40（意图 4
        #: 0 mm）
        #:   会建出 **40 米**高的柱子（★ 真机：俯视图里就是"一根细柱"）✓✗
        #:   ★ 对照组：`create_basic_part` 每处都调 `mm()` ⇒ 它建的 40×40×10 盒是对的 ✓
        param_alias=dict(_consumed("depth_mm")),
        derived_args=lambda p: _m_of_mm(p, "depth_mm"),
        params=[
            Param("sketch_name", str, description=_SKETCH),
            Param(
                "depth_mm",
                float,
                description="Extrusion depth in MILLIMETRES (must be > 0). "
                "★ Converted to the metres that "
                "IFeatureManager.FeatureExtrusion3 expects — the "
                "conversion happens here, exactly once.",
            ),
            Param("direction", bool, default=True, description=_DIR),
            Param(
                "merge",
                bool,
                default=True,
                description="True = merge the result into the body; False = keep it as a new body.",
            ),
        ],
        doc="Extrude a sketch into a solid BOSS (adds material). ★ This is the first tool in the "
        "repo that turns a sketch into a solid body. ★ depth_mm is in MILLIMETRES and is "
        "converted to metres at this boundary.",
    ),
    ToolSpec(
        name="solidworks_extrude_cut",
        title="Extrude a Cut (remove material)",
        module="sw_part",
        function="extrude_cut",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** ✓
        #: ★★★★ 2026-10-04（接手轮）**同样补换算**（与 boss / midplane 同一处根因、同一
        #: 修法）✓
        param_alias=dict(_consumed("depth_mm")),
        derived_args=lambda p: _m_of_mm(p, "depth_mm"),
        params=[
            Param("sketch_name", str, description=_SKETCH),
            Param(
                "depth_mm",
                float,
                description="Cut depth in MILLIMETRES. ★ 0 means "
                "**through all** (完全贯穿). ★ Converted to metres "
                "at this boundary.",
            ),
            Param("direction", bool, default=True, description=_DIR),
            Param(
                "flip",
                bool,
                default=False,
                description="True = flip the cut direction.",
            ),
        ],
        doc="Extrude a sketch as a CUT (removes material). ★ depth_mm = 0 means through-all. "
        "⚠ The correct entry point for a cut is FeatureCut4, not FeatureExtrusion3 with "
        "flip=True — the capability layer already handles that.",
    ),
    ToolSpec(
        name="solidworks_extrude_midplane",
        title="Extrude Symmetrically About the Sketch Plane",
        module="sw_part",
        function="extrude_midplane",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** ✓
        #: ★★★★★ 2026-10-04（接手轮）**换算修正 + 记下我一度回退它的原因**：
        #:   ★ 原本是 `{"total_depth_mm": "total_depth"}`（**只改名、不换算**）⇒
        #:     真机：传 84.3 ⇒ **`84300.00mm`**（= 84.3 米）⇒ ★ 视图里"**就是一根线**" ✓✗
        #:   ★★ **我一度回退过这个修法** —— 依据是当时三条读数"一致指向按毫米"
        #:     （包围盒 X 回 84.3 / `GetSystemValue3` 回 84.3 / 改 50 后盒变 50）。
        #:   ★★★ **回退是错的，根因是我读错了单位**：`part_bounding_box` 返回的是**米** ——
        #:     由**标定实验**定死（建 40×40×10 的盒 ⇒ 该工具回 `[0.04, 0.04, 0.01]`）⇒
        #:     ★ 所以"盒 X = 84.3"意味着 **84.3 米**，不是 84.3 mm ✓
        #: ★★★★ **分辨性序列**（`SetSystemValue3` 依次写 0.0843 / 84.3 / 84300，每次读回
        #: 包围盒）：
        #:     只有 **0.0843** 让盒变成 0.0843 m（= 84.3 mm）⇒ ★★ **D1 的口径是米，定案** ✓
        #: ⇒ ★ 教训：**"两个读数一致"不等于"读对了单位"** —— 必须先做一个**已知尺寸的标
        #: 定实验**，
        #:     再拿别的数去比（★ 与事实 517 同族：口径不清时先量、别推理）✓
        param_alias=dict(_consumed("total_depth_mm")),
        derived_args=lambda p: _m_of_mm(p, "total_depth_mm"),
        params=[
            Param("sketch_name", str, description=_SKETCH),
            Param(
                "total_depth_mm",
                float,
                description="TOTAL depth in MILLIMETRES — each side gets half "
                "(total_depth_mm / 2). ★ Converted to metres at this boundary.",
            ),
        ],
        doc="Extrude a sketch symmetrically about its plane. ⚠ The parameter is the TOTAL depth, "
        "not the per-side depth. ★ The value is in MILLIMETRES and is converted to the metres "
        "that IFeatureManager.FeatureExtrusion3 expects — the conversion happens here, once.",
    ),
]
