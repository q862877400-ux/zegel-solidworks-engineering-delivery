"""声明式 MCP 工具注册 —— 把「加一个工具」从 54 行手写降到 1 条声明。

## 为什么需要它
`mcp-server/server.py` 现在 **2455 行 / 45 个 `@mcp.tool` / 46 个 `BaseInput` 类**
⇒ **平均 54 行一个工具**。而 `AGENTS.md` 已知事实 25 记着：
`server.py` 只引用 **25** 个 `scripts` 模块，**本仓库后补的 61 个模块一个都没进**（交集 = 0）。

按老办法补齐 ⇒ **~120 个函数 × 54 行 ≈ 4800 行**手写样板
（评估见 `docs/history/T-011-expose-capabilities-assessment.md` —— 真实工作量是 ~120 个函数，不是 814）。

**⇒ 本模块把「简单工具」变成一条声明**：
```python
ToolSpec(
    name="solidworks_topology_create_study",
    title="Create SolidWorks Topology Study",
    module="sw_topology", function="create_topology_study",
    params=[Param("study_name", str, default="Topology Study 1"), ...],
    needs_model=False,
)
```

## 设计边界（**明确不做**什么）
| 做 | 不做 |
|---|---|
| 覆盖「**调一个既有函数、参数直传**」这类工具（评估里 120 个的绝大多数）
| **不**覆盖有自定义后处理的工具（如 `cadstudio_build_dxf_preview_scene`） —— 它们**继续手写**，
本模块给 `extra_op` 逃生口 |
| 生成 `@mcp.tool` 装饰器 + 函数 + `op()` 闭包 | **不**自动猜参数语义（`_mm` / `_deg` / `selection` 要**显式声明**） |
| 把三条硬约束做成**注册时即报错**的门禁 | **不**改 `server.py`（本模块只提供 `register()`，接入与否由人决定） |

## 为什么「不自动猜参数语义」很重要
六条规则里的 1/2/3 是**人工判断**的：
- 规则 1：工具名 `solidworks_<域>_<动作>` —— 要判「域是什么」
- 规则 2：长度 `_mm`、角度 `_deg`，换算**只在边界做一次**（`sw_connect.mm()`）
- 规则 3：**声明式 `selection`**，禁裸坐标

**⇒ 自动生成名字会造出语义不清的名字；自动猜单位会造出静默的 1000× 错误
（本项目刚在 `CreateMesh` 上踩过：把毫米当米 ⇒ 1950 万个单元 / 20–25 GB）。**
**故本模块只做「把已判好的东西写成代码」，不做判断。**

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_registry.py
# 定位:   AGENTS.md 已知事实 25「我们补的能力没被 MCP 暴露」的**工程解法**；
#         `docs/history/T-011-expose-capabilities-assessment.md` 的实现层。
#         写法照 `server.py` 既有 45 个工具的形状抽取（见该文件 1031/1045/1090 行附近）。
# 官方签名依据: 不适用（本模块只做 Python 层注册，不直接调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **本模块尚未接入 `mcp-server/server.py`** —— 那正是本会话 `mcp__solidworks__*` 工具的来源，
#   改它会动**正在运行的** MCP 表面（「单源运行」原则，已知事实 24）。
#   接入 = 在 `server.py` 里 `from tool_registry import register, SPECS` + `register(mcp, SPECS)`。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "Param",
    "ToolSpec",
    "GateError",
    "check_spec",
    "check_specs",
    "build_input_model",
    "make_tool_function",
    "register",
    "effective_inject",
    "SOLIDWORKS_NAME_RE",
    "CADSTUDIO_NAME_RE",
]

#: 六条规则 1：工具名统一 `solidworks_<域>_<动作>`；headless 用 `cadstudio_*`
SOLIDWORKS_NAME_RE = re.compile(r"^solidworks_[a-z0-9_]+$")
CADSTUDIO_NAME_RE = re.compile(r"^cadstudio_[a-z0-9_]+$")

#: 六条规则 2：长度以 `_mm` 结尾、角度以 `_deg` 结尾
_LEN_SUFFIX = "_mm"
_ANGLE_SUFFIX = "_deg"

#: 六条规则 3：选择必须用声明式 `selection`，禁裸坐标
#: ★★★ 2026-10-03（轮 433）**去掉了 `x_mm` / `y_mm` / `z_mm`** —— 而理由是
#:   **规则 2 与规则 3 在这三个名字上自相矛盾**：
#:     · 规则 2 要求**长度参数以 `_mm` 结尾**（`x_mm` 正是它要的写法）；
#:     · 规则 3 却把 `x_mm` 当"裸坐标"拦掉。
#:   ★★ 而**"裸"的定义本该是「没有单位信息、也没有具名实体」** ⇒
#: `x_mm` **带着单位**（★ 不裸）；★ 而 `x` / `boundary_z` / `d1_x` **都不带**（★ 才裸）
#: 。
#:   ★ 依据：`AGENTS.md` 明写规则 3 **有一条文档化的例外** ——
#:     「*Sketch geometry MUST be given as in-plane coordinates — this is the documented
#:      exception in rule 3*」⇒ 草图几何**本来就该给坐标** ✓
#:   ⚠ 而**没被放过的那条**（`solidworks_surface_fill.boundary_z`）是**真欠账** ——
#:     ★ 它是"**用坐标去选那一圈边**"，★ 那**正是**规则 3 要禁的形态 ⇒ 它照旧被拦 ✓
_BARE_COORD_NAMES = {"x", "y", "z", "point", "coordinate"}


def _looks_like_coord_component(name: str) -> bool:
    """★ **结构性判据**：这个参数名看着像"**坐标的一个分量**"吗？

    ★★ 为什么加它（2026-10-01 轮 261 · **修地基 D5**）：
      原判据只有一张 **8 个名字**的表 ⇒ ★ 而本仓库实际存在的裸坐标参数**远不止**：
        `x1` / `y1` / `x2` / `y2`（草图弧/中心线/槽的端点）· `cx` / `cy`（圆心）·
        `major_x` / `minor_y`（椭圆长短轴分量）· `d1_x` / `d1_y` / `d1_z`（阵列方向分量）
      ⇒ ★ 它们**全都漏过**了规则 3 的门禁（★ 事实 153：规则有**三句**，机器只验过第一句）。
    ★★★ **而判据要"结构"不要"枚举"**（★ 同轮 249 用 `GetTypeName2` 判特征、不枚举容器名的同一思路）：
      · **`^[a-z]\\d?_[xyz]$`** ⇒ `d1_x` / `major_y` / `x1`… ⚠ 不，那会命中 `x1`
      · 形式① **`^[xyz]\\d*$`** ⇒ `x` / `x1` / `y2` / `z`（★ 轴名 + 可选编号）
      · 形式② **`^c[xyz]$`** ⇒ `cx` / `cy` / `cz`（★ 圆心）
      · 形式③ **`(^|_)[xyz]\\d*$`** ⇒ `major_x` / `d1_x` / `minor_y`（★ 以轴名结尾）
      · 形式④ **`^[\\w]*[dD]\\d_[xyz]$`** ⇒ `d1_x` / `d2_y`（★ 已由形式③覆盖，留作说明）
    ⚠⚠ **刻意不收的**（★ 事实 74：按名字判语义在本项目失败过 8 次）：
      · `w` / `h` ⇒ ★ 在非几何语境里同样常用（`lot_size` 是批量、`h` 可能是句柄）
      · `center` ⇒ ★ 它是**元组名**、语义上算坐标，**但名字本身不表态**（★ 收进来会误伤
        「用户自定义的中心名」这类参数）⇒ ★ **只登记不判**（★ 见 `_COORD_COMPONENT_NOTE`）。
    """
    import re

    low = str(name).strip().lower()
    if not low:
        return False
    #: ★★★ 2026-10-03（轮 433）**"裸"的定义就是「没有单位信息」** ——
    #:   ★ 而 `_mm` 后缀**恰恰携带着单位信息**（★ 规则 2 **要求**长度参数以 `_mm` 结尾）。
    #:   ★★ 所以**以 `_mm` 结尾的坐标不是裸坐标** ⇒ 放过。
    #:   ⚠ 而这条**不是新例外** —— ★ 门禁**本来就在**放过它：`sketch_add_line` 的
    #:     `start_x_mm` / `end_x_mm` **从没被拦过**（★ 因为它们不以 `_x$` 结尾）。
    #:   ★★★ 矛盾在**精确黑名单**那三个条目（`x_mm`/`y_mm`/`z_mm`）：
    #: ★ 它们**同时**被规则 2 要求、★ 被规则 3 拦 —— ★ **两条规则自相矛盾** ⚠（本轮查明
    #: ）
    #:   ⇒ ★ 而**无单位**的（`x` · `boundary_z` · `d1_x` · `major_y`）**照旧拦** ✓
    if low.endswith("_mm"):
        return False
    if re.fullmatch(r"[xyz]\d*", low):  #: x / x1 / y2 / z
        return True
    if re.fullmatch(r"c[xyz]", low):  #: cx / cy / cz
        return True
    if re.search(r"(^|_)[xyz]\d*$", low):  #: major_x / d1_x / minor_y / point_x
        return True
    return False


#: ★ 语义上是坐标、**但名字不表态**的那些（★ 只登记，**不判** —— 免得制造假阳性）
_COORD_COMPONENT_NOTE = ("center", "w", "h")

#: 规则 2 的**长度词汇**：参数名里出现这些词 ⇒ 认为是长度参数，必须以 `_mm` 结尾。
#: ⚠ 这是**有界词表**，刻意保守（只收"几乎必然是长度"的词）。
#: ⚠⚠ **不包含** `size` / `w` / `h` —— 它们在非几何语境里同样常用
#: （`lot_size` 是批量、`h` 可能是句柄）⇒ 收进来只会制造假阳性
#: （见已知事实 74：按名字判语义的检查在本项目的失败记录）。
_LEN_WORDS = (
    "radius",
    "diameter",
    "depth",
    "thickness",
    "distance",
    "width",
    "height",
    "length",
    "offset",
    "spacing",
    "pitch",
)

#: ⚑⚑ **规则 2 的显式豁免**：这些参数的**单位不是毫米**，`_mm` 后缀会**说错话**。
#: 判据：该参数的值是**直接交给 SolidWorks 的"文档默认量"**，而不是我们换算出的毫米。
#: ⚠ 照 `check_interface_member_ownership.MANUAL_MAP` 的先例：
#: **每条都要写清"为什么它不属于这一条"**，没依据的不许进来。
#: 规则 2 的**角度词汇**。⚠ 刻意**不含** `rad` —— 它会**子串命中 `radius`**
#: （本轮实测：`bend_radius_mm` / `use_default_radius` 一共 **7 处**假阳性就是这么来的）
#: 。
_ANGLE_WORDS = ("angle", "degrees", "draft")

#: ⚑⚑ **规则 2 的角度那一半的显式豁免**（判据同长度表：值是**交给 SolidWorks 的
#: 文档默认量**，不是我们换算出的度）。
_ANGLE_SUFFIX_EXEMPT: dict = {
    (
        "solidworks_mold_parting_surface",
        "angle",
    ): "官方参数 `Angle`；本工具的文档写明「**0.0 = 用文档默认**」⇒ "
    "是**交给 SolidWorks 的文档默认量** ⇒ 加 `_deg` 反而**说错话**。",
    #: ★ 2026-10-03（轮 480）：官方**同一个形参承载两种量纲** ⇒ 加 `_deg` 会**说错一半**
    #: 。
    (
        "solidworks_insert_ref_plane",
        "first_angle_or_dist",
    ): "官方参数 `FirstConstraintAngleOrDistance` —— ★ **同一个形参**在 `FirstConstraint` 取 "
    "`Angle(16)` 时是**角度**、取 `Distance(8)` 时是**长度**（官方 Parameters："
    '"Angle **or** distance of the first constraint"）⇒ ★★ **一个名字带不了两种单位后缀**，'
    "加 `_deg` 会在 Distance 那一档说错话、加 `_mm` 会在 Angle 那一档说错话 ⇒ "
    "**两边都不加，并在返回值里显式声明「官方未给单位、本工具不换算」**。",
    (
        "solidworks_insert_ref_plane",
        "second_angle_or_dist",
    ): "同上（`SecondConstraintAngleOrDistance`）—— ★ 官方同一个形参承载角度或长度两种量纲。",
    (
        "solidworks_insert_ref_plane",
        "third_angle_or_dist",
    ): "同上（`ThirdConstraintAngleOrDistance`）—— ★ 官方同一个形参承载角度或长度两种量纲。",
}

#: ⚑⚑⚑ **规则 2b 的三件套**（★ 2026-10-07 规格 212 · C-4；★ 判据**全确定性**、★ 不猜语义
#: ）─────
#:   ★★ ① `_UNIT_DESC_WORDS`：**每档单位后缀 ↔ 该单位的写法**（★ 极窄：★ 只收该单位本身）✓
#:     ★ 为什么要窄：★ C 批第一版"从描述推断形参是不是长度"**假阳性压不住** ✗
#:     （★ 实录：`deg` 命中 `degenerate` · 「度」命中「**深**度」「**厚**度」）⇒
#:     ★★ **换了立足点**：★ **名字已带后缀** ⇒ ★ 只需查"描述里有没有本档单位词" ✓
_UNIT_DESC_WORDS: dict = {
    "_mm": re.compile(r"(\bmm\b|\bmm2\b|\bmm3\b|毫米|millimet\w*)", re.I),
    "_mm2": re.compile(r"(mm\s*[²2]\b|平方毫米|square\s+milli)", re.I),
    "_mm3": re.compile(r"(mm\s*[³3]|立方毫米|cubic\s+milli)", re.I),
    "_deg": re.compile(r"(\bdeg\w*|\bdegree\w*|度\b|°|弧度)", re.I),
    "_px": re.compile(r"(\bpixel\w*|\bpx\b|像素)", re.I),
    "_s": re.compile(r"(\bsecond\w*|\bsec\b|秒)", re.I),
    "_kg": re.compile(r"(\bkilogram\w*|\bkg\b|千克|公斤)", re.I),
}

#: ★★ ② `_DIMENSIONLESS_CLAIM`：**描述自称无量纲的固定词**（★ 用于"后缀说假话"那半）✓
_DIMENSIONLESS_CLAIM = re.compile(r"(无量纲|枚举值|布尔|百分比|比值|计数|序号)")

#: ★★ ③ `_UNIT_DESC_EXEMPT`：**唯一的逃生口** —— ★ 每条**必须写清"为什么它不需要描述里写
#: 单位"** ✓
#:   ★ 照 `_LEN_SUFFIX_EXEMPT` 的先例（`check_interface_member_ownership.MANUAL_MAP`）：
#:   **绝不覆盖自动结果**、**输出分开报**、**没有依据的不许进来** ✓
_UNIT_DESC_EXEMPT: dict = {
    ("solidworks_sheet_metal_insert_miter_flange", "relief_width_mm"):
    #: ★★ **这一条是"挂起"而不是"豁免"** —— ★ 它的单位**本身就没确证** ✗
    #: ★ 官方对 `ReliefWidth` 与 `ReliefDepth` **写的是同一句**「…specify relief **d
    #: epth**」⇒
    #:   ★ **官方这两句自相矛盾** ⇒ ★ 本工具**原样透传、不替官方调和**（铁律 5）✓
    #:   ★★ 而代码实测（`scripts/sw_sheet_metal.py`）：★ `float(args["ReliefWidth"])`
    #:   **直接送进 `InsertSheetMetalHem2`**、★ **中途没有 `mm()` 换算** ✗
    #:   ⇒ ★★★ **所以"名字该不该留 `_mm`"取决于官方吃什么 —— 而官方没说** ✗
    #:   ★ 已登记为 **`docs/history/unit-conflicts.md` 第 2 条**（★ 含真机验证判据：
    #:   ★ 传 `1.0` ⇒ **回读几何**：≈1mm ⇒ 名字对；★ ≈1000mm ⇒ 名字说假话）✓
    #: ⚠ ★ **结论出来后要回到这里改**（★ 要么补描述、要么去掉后缀）—— ★ **不是永久豁
    #: 免** ✓
    "★ **挂起**（不是豁免）：★ 官方对该形参**未给单位**、★ 且官方 `ReliefWidth`/`ReliefDepth` "
    "两句自相矛盾 ⇒ ★ 『名字该不该留 `_mm`』**取决于官方吃什么，而官方没说** ✗ "
    "★ 已登记 `docs/history/unit-conflicts.md` 第 2 条，★ **真机验完就回来改**（★ 非永久豁免）✓",
}


#: ⚑⚑ **规则 2 的显式豁免**（★ 原表 —— ★ 2026-10-07 我插 2b 三件套时**误删了这一行** ✗，
#: 现补回）✓
_LEN_SUFFIX_EXEMPT: dict = {  #: ★ 2026-10-03（轮 480）：官方**同一个形参承载两种量纲** ⇒ 加 `_mm` 会**说错一半**。
    (
        "solidworks_insert_reference_point",
        "distance_or_percent",
    ): "官方参数 `DDistance_or_Percent` —— ★ **同一个形参**在 "
    "`NRefPointAlongCurveType` 取 `Distance(0)` 时是**距离**、取 `Percentage(1)` 时是**百分比**"
    '（官方 Parameters："Distance at which … **or** percentage of…"）⇒ '
    "★★ **一个名字带不了两种单位后缀**：加 `_mm` 会在 Percentage 那一档说错话 ⇒ "
    "**不加，并在返回值里显式声明「官方未给单位、本工具不换算」**。",
    (
        "solidworks_mold_core_cavity_split",
        "thickness",
    ): "官方参数 `Thickness`；本工具的文档写明「0.0 = 用文档默认」⇒ "
    "它是**交给 SolidWorks 的文档默认量**，不是我们换算出的毫米 ⇒ "
    "加 `_mm` 反而**说错话**。",
    (
        "solidworks_mold_core_cavity_split",
        "offset",
    ): "同 `thickness`：官方 `Offset`，文档写明「0.0 = 用文档默认」。",
    (
        "solidworks_mold_parting_surface",
        "distance",
    ): "同 `thickness`：官方 `Distance`，文档写明「0.0 = 用文档默认」。",
    (
        "solidworks_export_bmp",
        "pixel_width",
    ): "★ 它**不是长度**，是**像素** —— 官方 `ExportToBMP(FileName, Width, Height)` 的两个尺寸"
    "单位是像素。⚠ 而门禁按**子串**匹配（`width` ∈ `pixel_width`）⇒ ★ **改名解决不了**，"
    "只能在这里登记。★ 登记的理由要写清：加 `_mm` 会把「像素」说成「毫米」——**那是说错话**。",
    (
        "solidworks_export_bmp",
        "pixel_height",
    ): "同 `pixel_width`：官方 `ExportToBMP` 的 `Height`，单位是**像素**不是长度。",
    ("solidworks_assembly_add_mate_checked", "width_mate_option"):
    #: ★★★ 2026-10-07（规格 212 · C-3）：★ 这条豁免是**改名撞出来的** ——
    #: ★ 原名 `width_mate_option_mm`，★ 而它其实是官方 `swMateWidthOptions_e` 的**枚
    #: 举值**、
    #:   ★★ **不是长度** ⇒ ★ 规格 212 的"后缀说假话"判据把它揪出来了 ✓
    #:   ★ 改名成能力层的真名 `width_mate_option` 之后 ⇒ ★★ **门禁又命中它** ——
    #:   ★ 因为门禁按**子串**匹配、`width` ∈ `_LEN_WORDS`）✗
    #:   ★★ 正解就是**走豁免通道并写清"为什么它不是毫米"**（★ 门禁提示的第二条路）✓
    #:   ⚠ ★ 门禁按子串匹配 ⇒ ★ **光改名解决不了**（★ 与 `pixel_width` 那条同一形态）✓
    "★ **不是长度**，是**枚举值** —— 官方 `swMateWidthOptions_e`（宽度配合选项）。"
    "官方逐字：valid only if MateTypeFromEnum is swMateWIDTH。★ 门禁命中它只因为"
    "`width` 是 `_LEN_WORDS` 里的子串 ⇒ 加 `_mm` 会把「枚举」说成「毫米」——**那是说错话**。",
    #: ★★ 2026-10-03（轮 470）：它**是角度**（名字里就写着 `_deg`）。门禁命中它只因为
    #:   `_LEN_WORDS` 里有 `spacing`；★ 而**一个参数不可能同时是长度与角度**
    #:   ⇒ 走门禁文档写明的这条通道，**不改它的名字**（改成 `_mm` 反而是说错话）。
    (
        "solidworks_sketch_circular_pattern",
        "pattern_spacing_deg",
    ): "★ 参数**不是长度**（★ 它是**角度**：名字已含 `_deg`，官方 `PatternSpacing` 收弧度、"
    "本工具在边界收度并换算一次）。★ 门禁命中它只因为 `_LEN_WORDS` 里有 `spacing` —— "
    "**一个参数不可能同时是长度与角度**。"
    "★★ 也**不是**「交给 SolidWorks 的**文档默认**量」（那是另一类豁免的形态）—— "
    "它**是我们自己换算出的度**，只是后缀该是 `_deg` 而非 `_mm`。",
    #: ★★★★ 2026-10-04（接手轮 · 规格 205 的批 86）：`sw_view.set_view_frame` 的四个**像
    #: 素**参数。
    #: ★ 该函数的官方读数逐字是「Left position of document window in client area **in pi
    #: xels**」
    #: ⇒ ★★ **单位是像素、不是长度** ⇒ 加 `_mm` 会把「像素」说成「毫米」（**那是说错话**
    #: ）✓
    #:   ★ 与既有的 `solidworks_export_bmp` 的 `pixel_width`/`pixel_height` **同一形态**
    #:     （★ 门禁按**子串**匹配，`width`/`height`/`left`/`top` 都在 `_LEN_WORDS` 里）✓
    #:   ⚠ ★ 我先前让**生成器自动改名**成 `width_px_mm` 想绕过本门禁 —— ★★ **方向错了**
    #: （那会造出一个**不存在的形参**，被 `check_param_binding` 与注册器**双双拒绝、整批
    #:  30 个
    #:     全注册不上**）；★ 正解就是这里：**走豁免通道并写明理由** ✓
    (
        "solidworks_view_set_frame",
        "left_px",
    ): "★ **不是长度**，是**像素** —— 官方 `IView.GetViewFrame` 的读数逐字 "
    "`Left position of document window in client area in pixels` ⇒ 加 `_mm` 是说错话。",
    ("solidworks_view_set_frame", "top_px"):
    #: ⚑⚑ ★ 2026-10-07（规格 212 · A-1）**修自洽性**：★ 原文只写「**同 `left_px`**」
    #: ⇒
    #: ★★ 而门禁要求**每条豁免自己点明三类依据之一**（「文档默认」/「不是长度（如像
    #: 素）」/
    #: 「同一个形参两种量纲」）✗ —— ★ **理由挂靠别条时，读者（与门禁）都得去翻另一条
    #: ** ✓
    #:   ★ 故改成与 `width_px` **同构**的写法（★ 自己点明"不是长度、是像素"）✓
    #: ⚠ ★ **没有为过门禁说假话** —— ★ 该理由**本来就成立**（官方读数逐字就是像素）
    #: ，
    #: ★ 只是**没写全** ✓（★ 这条纪律见 `test_rule2_exemptions_are_explicit_and_reas
    #: oned` 的 docstring）
    "★ **不是长度**，是**像素** —— 官方 `IView.GetViewFrame` 的读数逐字 "
    "`Top position of document window in client area in pixels` ⇒ 加 `_mm` 是说错话。",
    (
        "solidworks_view_set_frame",
        "width_px",
    ): "同 `left_px`：官方读数逐字 `Width of the window in pixels` ⇒ 单位是**像素**。",
    (
        "solidworks_view_set_frame",
        "height_px",
    ): "同 `left_px`：官方读数逐字 `Height of the window in pixels` ⇒ 单位是**像素**。",
}


class GateError(ValueError):
    """注册时违反「并入六条规则」⇒ 直接抛，不让它进到运行期。"""


@dataclass(frozen=True)
class Param:
    """一个入参的**显式**声明。

    :param name: 参数名。长度参数**必须以 `_mm` 结尾**、角度以 `_deg` 结尾（规则 2）。
    :param kind: Python 类型注解（`str` / `float` / `int` / `bool`）。
    :param default: 默认值；给 `...` 表示必填。
    :param description: 给人看的说明（会进 Pydantic 的 `Field(description=...)`）。
    :param required: 覆盖「没有默认值即必填」的推断。
    """

    name: str
    kind: type
    default: Any = ...
    description: str = ""
    required: bool | None = None

    @property
    def is_required(self) -> bool:
        return self.required if self.required is not None else self.default is ...


def effective_inject(spec: ToolSpec) -> str:
    """把 ``inject`` 与兼容别名 ``needs_model`` 归一成一个字符串。

    ⚠ 两者都给且冲突 ⇒ 抛 :class:`GateError`（**不静默取其一**）。
    """
    if spec.inject and spec.needs_model:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 needs_model=True —— 二者等价，只留一个"
            % (spec.name, spec.inject)
        )
    if spec.inject:
        return spec.inject
    return "model" if spec.needs_model else ""


@dataclass
class ToolSpec:
    """一个工具的**声明**。

    :param name: MCP 工具名（规则 1 的正则会被检查）。
    :param title: 给人看的标题。
    :param module: `scripts` 下的模块名，如 `"sw_topology"`。
    :param function: 该模块里的函数名。
    :param params: 入参声明列表（**不含** `response_format`，注册器自动加）。
    :param inject: **注入哪种宿主对象**（注册器负责造并把它作为实参传进去；空串 = 不注入）。
        取值由**调用方注册的解析器**决定 —— 本模块**不硬编码任何宿主 API**，
        因此可独立测试（见 `tests/test_tool_registry.py` 的假宿主）。
        约定俗成的四个：``""`` / ``"model"``（活动文档）/ ``"sw_app"``（ISldWorks）/
        ``"study"``（按 ``study_name`` 入参解析）。
        ⚠ 注入用的**关键字名**必须与目标函数的**真实形参名**一致
        （``model`` / ``sw_app`` / ``study``）。
    :param needs_model: **兼容别名**（等价于 ``inject="model"``）；新声明请直接用 ``inject``。
    :param param_alias: **对外参数名 → 目标函数形参名** 的显式映射。
        值为 ``None`` 表示「该参数由解析器消费，**不传给目标函数**」。
        未列出的参数**同名直传**。
        ⚠ 为什么要显式：MCP 表面用 ``study_name`` 比 ``name`` 清楚、
        ``element_size_mm`` 比 ``element_size`` 合规（规则 2），
        而实现里的名字不该为了对外好看去改。
        **但别名必须写出来** —— 否则与「拼错了参数名」无法区分。
    :param derived_args: **从已声明的标量入参派生额外实参**，形如
        ``lambda params: {"spec": BaseFlangeSpec(...)}``。返回的字典会**并进**
        调用目标函数的关键字实参里。
        ⚠ 与 `extra_op` 的分工：`extra_op` **替换整个调用**（用了就放弃声明式）；
        `derived_args` **只补一个实参**，`module`/`function`/同名直传都还在。
        **能不退就退。**
        ⚠ 单位换算也放这里，且**只做一次**（并入规范规则 2）：spec 说「米」、
        MCP 表面按规则 2 用 ``_mm`` ⇒ 在派生函数里 ``/1000.0``。
    :param pre_call: **调用前的副作用钩子**，形如 ``lambda params: None``。
        用途：那些**实现里明写「调用前必须先选好」**的函数（如钣金 C2 类：
        `create_edge_flange` / `create_gusset` / `create_draft`）。
        ⚠ 与 `derived_args` 的分工：`derived_args` **产出实参**，
        `pre_call` **只做副作用、不产出实参**。给字段安它没有的含义是本项目反对的。
    :param omitted_params: **故意不暴露**的形参名（如 ``Object`` 型的 ``colors``）。
    :param read_only: 只读工具 ⇒ `readOnlyHint=True`。
    :param idempotent: 幂等 ⇒ `idempotentHint=True`。
    :param load_automation: 是否需要加载 SolidWorks 自动化（headless 工具传 False）。
    :param extra_op: 逃生口 —— 有自定义后处理的工具给一个 `op(params) -> Any`，
        此时 `module`/`function` 可省。
    :param doc: 函数 docstring（会变成 MCP 工具描述）。
    :param omitted_params: **故意不暴露**的形参名（如 `Object` 型的 `colors`）。
        ⚠ 必填理由：**省略必须是显式的**，否则它和「手抄漏了」无法区分 ——
        `tests/test_tool_specs_batch1.py` 就靠这个字段区分二者。
    """

    name: str
    title: str
    module: str = ""
    function: str = ""
    params: list[Param] = field(default_factory=list)
    inject: str = ""
    needs_model: bool = False
    read_only: bool | None = None
    #: ★★ **效应声明**（规格 210 · B1）：**可能改**哪几类状态 ——
    #: 类别固定七类：文档内容 / 文件系统 / 选区 / 激活文档 / 编辑态 / 视图 / 重建或解析
    #: 。
    #:   ★★ **三态**：`None` = **未知**（★ 机械初判判不出的那批，**不许当成"无写"**）·
    #:   `()` = **确认不改任何状态**（这才是"纯读"）· 非空 = 改这几类 ✓
    #:   ★ 由 `scripts/` 侧的效应表（生成物）填充，见 `effective_writes()`。
    writes: tuple | None = None
    #: ★ `writes` 的**来源**：`static`（机械初判）/ `observed`（真机指纹实证）/ `human`
    #: （人判）
    writes_source: str = "unknown"
    #: ★ **依赖**哪几类状态（前置）。★ 与 `writes` 同一套类别名 ✓
    requires: tuple = ()
    idempotent: bool | None = None
    #: ★ `idempotent` 的**来源**（`static` / `observed` / `human`；`unknown` = 尚未判过
    #: ）✓
    idempotent_source: str = "unknown"
    #: ★★ **是否会做破坏性更新**（删除、覆盖保存、清空）—— ★ 与"写"**分开**：
    #:   ★ "写"可以是可补偿的（新增特征就删掉增量），★ "破坏性"是**不可逆**的那类 ✓
    #:   ★ 三态：`None` = **未声明** ⇒ ★ 注解里**不发**这一条 ⇒ ★ 按 MCP 缺省语义
    #:   **客户端会当作"可能破坏"**（★ 这正是我们要的保守方向）✓
    destructive: bool | None = None
    load_automation: bool = True
    extra_op: Callable[[Any], Any] | None = None
    doc: str = ""
    #: ★★ **工程证据**（规格 352 · D3/D4）：**非模型可见**。
    #:   装旧的 `doc` 原文：`★ 官方签名（逐字…）` / `查不到` / `事实 47` / 真机读数 / 废弃链。
    #:   ★ 为什么不放在 `doc` 里：DSH `agent-experience` 逐字要求
    #:     「**Describe behavior, not implementation.** …omit internal mechanisms and
    #:     enforcement details」—— 那些是**实现与执法细节**，不该占模型的第一眼 ✗
    #:   ★ 为什么不删掉：**五统一 / A2 两层 provenance** 要求证据可追溯 ⇒ 搬家、不丢 ✓
    #:   ★ 注册路径**只读 `doc`**（`make_tool_function` 里 `_impl.__doc__ = spec.doc`）
    #:     ⇒ 本字段**不会**进 `tools/list` ✓
    evidence: str = ""
    omitted_params: tuple[str, ...] = ()
    param_alias: dict[str, str | None] = field(default_factory=dict)
    derived_args: Callable[[Any], dict] | None = None
    pre_call: Callable[[Any], None] | None = None


def check_spec(spec: ToolSpec) -> None:
    """把三条可由机器判定的规则**在注册时**验掉；违者抛 :class:`GateError`。

    ⚠ 这里只验**机器能判**的（名字正则、后缀、裸坐标）；
    「域判得对不对」「单位换算对不对」属人工判断，本模块**不假装能验**。
    """
    if not (SOLIDWORKS_NAME_RE.match(spec.name) or CADSTUDIO_NAME_RE.match(spec.name)):
        raise GateError(
            "规则 1 违反：工具名 %r 必须匹配 %s 或 %s（域在前、动在后、蛇形）"
            % (spec.name, SOLIDWORKS_NAME_RE.pattern, CADSTUDIO_NAME_RE.pattern)
        )
    if not spec.title.strip():
        raise GateError("工具 %r 缺 title" % spec.name)
    if spec.pre_call is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 pre_call 与 extra_op —— extra_op 自己就是完整执行体，"
            "pre_call 无处安放" % spec.name
        )
    if spec.derived_args is not None and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 derived_args 与 extra_op —— 前者是「补一个实参」，"
            "后者是「替换整个调用」，语义冲突，只留一个" % spec.name
        )
    inj = effective_inject(spec)
    if inj and not inj.isidentifier():
        raise GateError("工具 %r 的 inject=%r 不是合法标识符" % (spec.name, inj))
    if inj and spec.extra_op is not None:
        raise GateError(
            "工具 %r 同时给了 inject=%r 与 extra_op —— extra_op 自己负责注入，二者互斥"
            % (spec.name, inj)
        )
    if not (spec.extra_op or (spec.module and spec.function)):
        raise GateError(
            "工具 %r 既没给 (module, function) 也没给 extra_op ⇒ 没有可执行体"
            % spec.name
        )
    if spec.name.startswith("solidworks_") and not spec.load_automation:
        raise GateError(
            "工具 %r 以 solidworks_ 开头却 load_automation=False —— "
            "headless 路线应当用 cadstudio_*（规则 1：两者不混用）" % spec.name
        )
    for src, dst in spec.param_alias.items():
        if src not in {p.name for p in spec.params}:
            raise GateError(
                "工具 %r 的 param_alias 指向未声明的参数 %r" % (spec.name, src)
            )
        if dst is not None and not dst.isidentifier():
            raise GateError(
                "工具 %r 的 param_alias[%r]=%r 不是合法形参名" % (spec.name, src, dst)
            )
        if dst is not None and dst in spec.omitted_params:
            raise GateError(
                "工具 %r 的 param_alias[%r] 指向被省略的形参 %r" % (spec.name, src, dst)
            )
    seen: set[str] = set()
    for p in spec.params:
        if p.name in seen:
            raise GateError("工具 %r 的参数 %r 重复" % (spec.name, p.name))
        seen.add(p.name)
        if p.name in _BARE_COORD_NAMES or _looks_like_coord_component(p.name):
            raise GateError(
                "规则 3 违反：工具 %r 的入参 %r 是裸坐标 —— "
                "必须改用具名实体 + 声明式 selection" % (spec.name, p.name)
            )
        #: ★★ 规则 3 的**第二句**（2026-10-01 轮 218 接上，地基③）。
        #: ⚠ 规则 3 在文档里有**三句**，机器**只验过第一句**（参数名）⇒ 后两句无人看守（
        #: 事实 153）。
        #:    ★ 而**能被机器判的其实只有两句**：
        #:      句1「不许裸坐标」    ⇒ 上面那段（参数名黑名单）
        #:      句2「必须是声明式选择」⇒ **本段**：声明式选择在参数上就是 `selection: str`
        #:      句3「按 mark 分配」   ⇒ ★ **静态判不了** —— 那是**运行行为**
        #:                              （多引用特征读 mark 0/1/2，不读选择顺序）⇒ 只能靠真机证据
        #:    ⚠⚠ 我一度还加了「说明里必须写合法取值」「mark 必须说明」两条 ——
        #:       ★ **那是我自己的好习惯，不是规则的内容** ⇒ 已撤掉：
        #:       门禁**只验规则真正要求的**，不把偏好伪装成规则。
        #:       撤掉的理由有证据：既有的 `test_rule3_named_entity_selection_is_ok`
        #:       断言「`Param("selection", str)` 无说明也应通过」—— 那条测试编码的是**本意**。
        if p.name == "selection" and p.kind is not str:
            raise GateError(
                "规则 3 违反：工具 %r 的 selection 必须是 str（声明式选择器），"
                "现为 %r —— 传数字/坐标不是声明式选择" % (spec.name, p.kind.__name__)
            )
        if p.name in ("response_format",):
            raise GateError(
                "工具 %r 不要自己声明 response_format —— 注册器会自动加" % spec.name
            )
        # ⚑⚑ 规则 2 的**长度那一半**（2026-10-01 轮 134 接上）。
        #    ⚠⚠ **接上之前，这一半从未生效** —— `_LEN_SUFFIX` 是个**死常量**
        #    （只在定义处出现一次）。⇒ 规则 2 一直被算进「五统一门禁通过」，
        #    但它的长度那一半**从来没拦过任何东西**（已知事实 40：存在但没人用的守卫）。
        #    证据：`tests/test_rule2_length_suffix_is_enforced.py` 的负例。
        low = p.name.lower()
        #: ⚠ `bool` **不是长度**（`use_default_radius` / `reverse_thickness` 是**标志**
        #: ）
        if (
            p.kind is not bool
            and any(w in low for w in _LEN_WORDS)
            and not low.endswith(_LEN_SUFFIX)
        ):
            if (spec.name, p.name) not in _LEN_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**长度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_LEN_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是毫米**"
                    % (spec.name, p.name, _LEN_SUFFIX, p.name, _LEN_SUFFIX)
                )
        # ⚑⚑ 规则 2 的**角度那一半**（2026-10-01 轮 135 接上；同 `_LEN_SUFFIX` 一样，
        #    它此前也是**死常量** —— `probe_dead_guards.py` 扫出来的）。
        if (
            p.kind is not bool
            and any(w in low for w in _ANGLE_WORDS)
            and not low.endswith(_ANGLE_SUFFIX)
        ):
            if (spec.name, p.name) not in _ANGLE_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**角度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_ANGLE_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是度**"
                    % (spec.name, p.name, _ANGLE_SUFFIX, p.name, _ANGLE_SUFFIX)
                )
        # ⚑⚑⚑ 规则 2b 的**前半**（★ 2026-10-07 规格 212 · C-4）—— ★★ **只报不拦，不在这
        # 里 `raise`** ✓
        #    ★★ 判据：**名字带单位后缀 ⇒ 描述里应有本档单位词** ✓
        # ★★★ **为什么它不做硬拦**（★ 这是本批最重要的分寸判断，★ 被一次测试失败逼出来的
        # ）：
        # ★ 实录：★ 接上硬拦后，**既有测试** `test_radius_param_is_not_flagged_as_an_ang
        # le`
        #        当场失败 —— ★ 它的夹具 `bend_radius_mm` **描述里没写 "mm"** ✗
        #      ★★ 而那条夹具的**意图与单位无关**（★ 它测的是"半径不该被当角度" ✓）
        #      ⇒ ★★★ **判断**：★「描述没写全」**不构成危险**（★ 名字已经说清了 ✓）⇒
        #        ★ **它适合当"审计发现"，不适合当"硬拦"** ✗ ✓
        # ★★ 而**后半（说假话）才是真危险** —— ★ 它主动误导，★ **读代码的人与 AI 都会信*
        # * ✗
        # ★★ **故分工**：★ **前半**留 `tools/check_unit_suffix_consistency.py`（★ 只报 ✓
        # ）·
        #      ★ **后半**在这里硬拦 ✓
        #    ★ 判据**全确定性**（★ 描述里的单位词是**固定词表**，★ 不猜语义）✓
        # ⚑⚑⚑ 规则 2b 的**后半：不许说假话**（★ 硬拦 ✓；★ C 批清后**已 0 条**）→
        #    ★★ **描述自称无量纲/枚举/布尔 ⇒ 名字不许带单位后缀** ✗
        # ★ 依据：★ 实录 —— `lock_rotation_deg` 是 `bool`、`width_mate_option_mm` 是 `in
        # t` 枚举，
        #      ★★ 两个后缀**都在说假话**，★ 而**读代码的人与 AI 都会信它** ✗
        # ★★ 这正是**规则 2 的盲区**：★ 原门禁只查「名字含长度词却无 `_mm`」（**单向** ✗
        # ）⇒
        #      ★ 反过来那种（★ **不含长度词、却带了 `_mm`/`_deg`**）**门禁抓不到** ✓
        #    ⚠⚠ ★ **修过一次**：★ 我第一版在这半里也写了 `p.kind is not bool` ⇒
        #      ★★ **于是 `lock_rotation_deg`（★ 它正是 `bool`）逃掉了** ✗ ——
        #      ★ 是**负例测试当场报 `DID NOT RAISE`** 抓出来的 ✓
        #      ⇒ ★★ 定则：★ **前半可以排除 `bool`（`use_default_radius` 那类标志）**，
        #        ★ **后半绝不能** —— ★ **布尔带单位后缀恰恰是最典型的"说假话"** ✗ ✓
        if isinstance(p.description, str) and p.description:
            _fake = next((s for s in _UNIT_DESC_WORDS if low.endswith(s)), None)
            if _fake is not None:
                _m = _DIMENSIONLESS_CLAIM.search(p.description)
                if _m:
                    raise GateError(
                        "规则 2b 违反（后缀说假话）：工具 %r 的入参 %r 带着 %r 后缀，"
                        "★ 而描述里自称「%s」⇒ ★ 两者矛盾：要么去掉后缀，"
                        "要么把描述改准（★ 不许让后缀说假话）"
                        % (spec.name, p.name, _fake, _m.group(0))
                    )


def check_specs(specs: list[ToolSpec]) -> list[str]:
    """批量校验，返回**所有**问题（不短路）；空列表 = 全过。"""
    problems: list[str] = []
    names: set[str] = set()
    for s in specs:
        try:
            check_spec(s)
        except GateError as exc:
            problems.append(str(exc))
        if s.name in names:
            problems.append("工具名重复：%r" % s.name)
        names.add(s.name)
    return problems


def build_input_model(spec: ToolSpec, base: type, response_enum: Any) -> type:
    """由声明生成 Pydantic 输入模型（`class <Name>Input(base)`）。

    `response_format` 由**入参顺序的最后一位**固定加上 —— 与 `server.py` 既有 45 个工具一致。
    """
    from pydantic import Field

    model_name = "".join(part.capitalize() for part in spec.name.split("_")) + "Input"
    fields: dict[str, Any] = {}
    for p in spec.params:
        kwargs: dict[str, Any] = {}
        if p.description:
            kwargs["description"] = p.description
        if p.is_required:
            fields[p.name] = (p.kind, Field(..., **kwargs))
        else:
            fields[p.name] = (p.kind, Field(default=p.default, **kwargs))
    fields["response_format"] = (
        response_enum,
        Field(default=response_enum.JSON, description="Return format."),
    )
    return type(
        model_name,
        (base,),
        {
            "__annotations__": {k: v[0] for k, v in fields.items()},
            **{k: v[1] for k, v in fields.items()},
        },
    )


#: ★★ B4 的预检开关（★ 规格 210）—— ★ **默认开**；★ `SW_PRECHECK=off` 可关（★ 于是**可回
#: 退**）✓
PRECHECK_ENABLED = str(os.environ.get("SW_PRECHECK", "on")).strip().lower() not in (
    "off",
    "0",
    "false",
)


def precheck_payload(spec: ToolSpec, inject_name: str, host) -> str | None:
    """★★ **按声明自动生成的预检** —— ★ 返回 `None` 表示**放行**；★ 否则返回**要直接回的 JSON 串** ✓

    ★★ 这是 B4 的落点（★ 评审的四条之一）：★「工具层返回**结构化**的『不适用』，
      ★ **不要抛字符串异常**」⇒ ★★ 于是**不适用时工具回的是 JSON 载荷**，★ 不是异常 ✓
    ★★ 三条保守判据：
      ① ★ **预检自己出错 ⇒ 放行** —— ★ 预检是**保护**，★ 不该变成新的**路障** ✓
         （★ 这条与本会话两次"过度纠正"的教训**同族**：★ 保守 ≠ 一律拒绝）✓
      ② ★ **没建的检查（`unchecked`）⇒ 放行**（★ 它如实说"没查"，★ 不许因此挡住工具）✓
      ③ ★ 开关关掉 ⇒ 一律放行 ✓
    """
    if not PRECHECK_ENABLED or not inject_name:
        return None
    try:
        try:
            import scripts.sw_applicability as ap
        except ImportError:
            import sw_applicability as ap  # noqa: PLC0415
        ap.precheck(inject_name, host, tool_name=spec.name)
        return None
    except Exception as exc:  # noqa: BLE001
        #: ★ 认得出是"不适用" ⇒ 回**结构化载荷**（★ 这是唯一的"拒绝"路径）✓
        name = type(exc).__name__
        if name == "NotApplicable" and hasattr(exc, "to_dict"):
            import json as _json

            return _json.dumps(exc.to_dict(), ensure_ascii=False)
        #: ★ 其余异常（含"没建的检查"）⇒ **放行** —— ★ 保护不许变成路障 ✓
        return None


def make_tool_function(
    spec: ToolSpec,
    input_model: type,
    run_locked: Callable[..., str],
    resolve_model: Callable[[], Any] | None = None,
    resolvers: dict[str, Callable[[Any], Any]] | None = None,
    inject_as: str | None = None,
) -> Callable[..., str]:
    """生成与 `server.py` 既有工具**同形状**的函数体。

    形状（照 `server.py:1077` 的 `cadstudio_write_open_format` 抽取）::

        def <name>(params: <X>Input) -> str:
            \"\"\"<spec.doc>\"\"\"
            def op():
                from scripts.<module> import <function>
                return <function>(<kwargs>)
            return run_locked(op, params.response_format, load_automation=...)
    """

    def _impl(params: Any) -> str:  # noqa: ANN401
        def op():
            kwargs = {}
            for p in spec.params:
                # `param_alias` 里 None = 由解析器消费，不进目标函数
                if p.name in spec.param_alias and spec.param_alias[p.name] is None:
                    continue
                target = spec.param_alias.get(p.name, p.name)
                kwargs[target] = getattr(params, p.name)
            inj = effective_inject(spec)
            if inj:
                resolver = (resolvers or {}).get(inj)
                if resolver is None:
                    raise RuntimeError(
                        "工具 %r 声明了 inject=%r，但注册时没给对应的解析器"
                        "（已给的：%r）"
                        % (spec.name, inj, sorted((resolvers or {}).keys()))
                    )
                kwargs[inject_as or inj] = resolver(params)
                #: ★★ **B4：按声明自动生成的预检** ⇒ ★ 不适用就回**结构化载荷**，★ 不调
                #: 目标函数 ✓
                #:   ★（★ 只在 `inject` 非空时做 —— ★ 没有宿主对象就没有"不适用"可言）✓
                _blocked = precheck_payload(spec, inj, kwargs.get(inject_as or inj))
                if _blocked is not None:
                    return _blocked
            if spec.extra_op is not None:
                return spec.extra_op(params)
            if spec.pre_call is not None:
                # ⚠ 在**调用目标函数之前**执行（选择类副作用）——
                #   实现里明写「调用前必须先选好」的函数靠它。
                spec.pre_call(params)
            if spec.derived_args is not None:
                # ⚠ 派生实参**不得覆盖**已直传的参数名 —— 覆盖会静默改变语义。
                extra = spec.derived_args(params) or {}
                clash = set(extra) & set(kwargs)
                if clash:
                    raise GateError(
                        "工具 %r 的 derived_args 想覆盖已直传的参数 %r —— 不允许"
                        % (spec.name, sorted(clash))
                    )
                kwargs.update(extra)
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            return getattr(mod, spec.function)(**kwargs)

        return run_locked(
            op, params.response_format, load_automation=spec.load_automation
        )

    _impl.__name__ = spec.name
    _impl.__doc__ = spec.doc or spec.title
    _impl.__annotations__ = {"params": input_model, "return": str}
    return _impl


#: ★★ 效应表（**生成物**，规格 210 · B1）：`工具名 -> {"writes": [...], "destructive": b
#: ool, "source": ...}`
#:   ★ 由 `tools/gen_effect_declarations.py` 从**底层成员动词**机械初判生成；
#:   ★★ **表缺失或查不到 ⇒ 一律按"未知"处理**（★ 保守方向：绝不因为查不到就当成"无写"）✓
_EFFECTS_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "effect-declarations.json"
)
_EFFECTS_CACHE: dict | None = None


def _effects_table() -> dict:
    """★ 惰性加载效应表；★ **读不到就回空表**（⇒ 全部按未知处理，保守）✓"""
    global _EFFECTS_CACHE
    if _EFFECTS_CACHE is None:
        try:
            _EFFECTS_CACHE = json.loads(_EFFECTS_PATH.read_text(encoding="utf-8")).get(
                "tools", {}
            )
        except Exception:  # noqa: BLE001
            _EFFECTS_CACHE = {}
        if not isinstance(_EFFECTS_CACHE, dict):
            _EFFECTS_CACHE = {}
    return _EFFECTS_CACHE


#: ★★★ **实证覆盖层**（规格 210 · B3/B4）：★ **真机观察到变化的工具** —— ★ 实证**优先于*
#: *静态 ✓
#:   ★★ 外部评审的设计原话：★「**静态当提案与否决票，运行时实证当实证，两者都通过才开**」✓
#:   ⇒ ★ 于是覆盖层的语义是：★ **静态说「无写」而实证观察到改动 ⇒ 以实证为准** ✓
#:     ★（★ 保守方向：★ **一旦观察到变化，就绝不许再当只读**）✓
#: ★ 现场（真机）：★ `assembly_check_interference` 静态 `[]` 而观察 **改了 `selection`**
#:  ·
#:     ★ `motion_create_study` 静态 `[]` 而观察 **改了 `selection`+`dirty`+`features`** ✓
_OBSERVED_PATH = Path(__file__).resolve().parents[1] / "docs" / "effect-observed.json"
_OBSERVED_CACHE: dict | None = None


def _observed_table() -> dict:
    """★ 惰性加载实证覆盖层；★ **读不到就回空表**（⇒ 退化成"只有静态"，★ 保守）✓"""
    global _OBSERVED_CACHE
    if _OBSERVED_CACHE is None:
        try:
            _OBSERVED_CACHE = json.loads(
                _OBSERVED_PATH.read_text(encoding="utf-8")
            ).get("tools", {})
        except Exception:  # noqa: BLE001
            _OBSERVED_CACHE = {}
        if not isinstance(_OBSERVED_CACHE, dict):
            _OBSERVED_CACHE = {}
    return _OBSERVED_CACHE


def observed_writes(spec: ToolSpec) -> tuple | None:
    """★ **真机观察到**的效应（★ 没有记录 ⇒ `None`）✓"""
    row = _observed_table().get(spec.name)
    if isinstance(row, dict) and row.get("writes"):
        return tuple(row["writes"])
    return None


def effective_writes(spec: ToolSpec) -> tuple | None:
    """★ 这个工具**可能改**哪几类状态 —— ★★ `None` 表示**未知**（★ 不等于"无写"）✓

    ★★ 判序（★ **实证优先** —— 这是评审定的）：
      ① ★ 声明里**显式写的**（`writes is not None`）⇒ 用它 ✓
      ② ★★ **真机实证**（覆盖层）⇒ 用它 —— ★ **与静态冲突时以它为准** ✓
      ③ ★ 静态生成物效应表 ✓
      ④ ★ 都查不到 ⇒ `None`（未知）—— ★ 下游**保守处理**（不发"只读"、不开自动重试）✓
    """
    if getattr(spec, "writes", None) is not None:
        return tuple(spec.writes)
    obs = observed_writes(spec)
    if obs:
        return obs
    row = _effects_table().get(spec.name)
    if isinstance(row, dict) and row.get("writes") is not None:
        return tuple(row["writes"])
    return None


def effective_read_only(spec: ToolSpec) -> bool:
    """★ 是否**只读** —— ★★ 由 `writes` **派生**（这是 B1-4 要修的根因：它曾是独立手填的布尔）✓

    判序：★ 显式声明优先（人判 / 真机实证）· 其次"**确认无写**" ⇒ 真 · 再次"确有写" ⇒ 假 ·
    ★★ **未知 ⇒ 假**（★ **绝不因为"判不出"就宣称只读**）✓
    """
    explicit = getattr(spec, "read_only", None)
    if explicit is not None:
        return bool(explicit)
    writes = effective_writes(spec)
    return writes == ()


def _tool_annotations(spec: ToolSpec) -> dict:
    """★ 造 MCP 工具注解 —— ★★ **只发我们真的知道的那些**（未知就**不发**，别替客户端猜）。

    ★★★ 2026-10-06：**这里原本有两个对外"误报"，都是安全相关的**：
      ① `idempotentHint` 原为 `bool(spec.idempotent)`，而 `idempotent` 的**默认值是 True**
         ⇒ ★★ **448 个工具全部对外宣称"幂等 / 可安全重试"** —— ★ 而其中绝大多数是创建、插入、阵列类
         （重复调用会**多出一份特征**）⇒ ★★ **客户端超时后重试就会重复改模型** ✓
      ② `destructiveHint` **硬编码 False** ⇒ ★ 删除、覆盖保存这类工具也在宣称"**非破坏性**" ✓
    ⇒ ★ 现在按"**三态 + 未知不发**"处理，依据是 MCP 的缺省语义：
      ★ `destructiveHint` **缺省即视为"可能破坏"**（⇒ **省略就是保守**）；
      ★ `idempotentHint` 缺省即"未声明"（⇒ 客户端**不得**假定可重试）✓
    ★ 唯一**可以明确**推出的：★ `read_only=True` 的工具**确定**不做破坏性更新 ⇒ 发 `False` ✓
    """
    ann: dict = {
        "readOnlyHint": bool(effective_read_only(spec)),
        "openWorldHint": False,
    }
    if getattr(spec, "idempotent", None) is not None:
        ann["idempotentHint"] = bool(spec.idempotent)
    #: ★ 未声明破坏性时：只读 ⇒ 可明确 False；★ 其余**一律不发**（缺省 = 可能破坏 = 保守
    #: ）✓
    destructive = getattr(spec, "destructive", None)
    if destructive is not None:
        ann["destructiveHint"] = bool(destructive)
    elif effective_read_only(spec):
        ann["destructiveHint"] = False
    return ann


def uniform_safety_fields(specs: list) -> dict:
    """★ **单值安全字段**盘点（★ 门禁的判据来源）：安全相关字段里**所有工具取同一非"未知"值**的。

    ★★ 为什么要有它：★ `idempotent` 曾经**448 个全是 True**、`destructiveHint` 曾经**硬编码 False** ——
      ★ 两者都是"**没人真想过、被默认值填满**"的形态，★ 而它们在 MCP 里是**客户端据以决定
      要不要确认、能不能重试**的依据 ⇒ ★ 单值 = **等于没声明，却看起来像声明过**（比空缺更糟）。
    ★ 判据刻意**只报"非未知的单值"**：★ 全体都是未声明是**诚实的合法状态**，不报 ✓
    """
    out: dict = {}
    for field_name in ("read_only", "idempotent", "destructive"):
        values = [getattr(s, field_name, None) for s in specs]
        if not values:
            continue
        distinct = set(values)
        only = next(iter(distinct))
        if len(distinct) == 1 and only is not None:
            out[field_name] = {"value": only, "count": len(values)}
    return out


def register(
    mcp: Any,
    specs: list[ToolSpec],
    base: type,
    response_enum: Any,
    run_locked: Callable[..., str],
    resolve_model: Callable[[], Any] | None = None,
    resolvers: dict[str, Callable[[Any], Any]] | None = None,
) -> list[str]:
    """把声明注册成 MCP 工具。返回**已注册的工具名**（供日志与门禁核对）。

    先 `check_specs` 全量校验 —— **有任何问题就整体不注册**（不让半套工具进到运行期）。

    :param resolvers: 注入解析器表：``{注入名: (params) -> 宿主对象}``。
        **由调用方提供** ⇒ 本模块保持宿主无关（其自测用假宿主）。
        典型：``{"model": lambda p: active_doc(), "sw_app": lambda p: sw(),
                 "study": lambda p: study_by_name(sw(), p.study_name)}``。
        兼容：只给 ``resolve_model`` 时等价于 ``{"model": lambda p: resolve_model()}``。
    """
    if resolvers is None and resolve_model is not None:
        resolvers = {"model": lambda _p: resolve_model()}

    problems = check_specs(specs)
    if problems:
        raise GateError(
            "声明未过门禁，未注册任何工具：\n  - " + "\n  - ".join(problems)
        )
    registered: list[str] = []
    for spec in specs:
        model = build_input_model(spec, base, response_enum)
        fn = make_tool_function(spec, model, run_locked, resolve_model, resolvers)
        decorated = mcp.tool(
            name=spec.name,
            title=spec.title,
            annotations=_tool_annotations(spec),
        )(fn)
        registered.append(spec.name)
        # 保持模块级可见（MCP 库会按名字解析）
        globals()[spec.name] = decorated
    return registered
