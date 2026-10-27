"""★ 批次 107：规格 219 · 边界凸台 + 边界曲面（官方 IFeatureManager::InsertNetBlend）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现与来源块在 scripts/sw_net_blend.py）
# 文件:   specs/219-user-coverage-100/ 的 T-219-04
# 定位:   ★ 补两个真缺口：★ 特征/边界凸台 · 曲面/边界曲面
# 官方依据: 签名 C:\swapi\types\IFeatureManager\InsertNetBlend.md（20 参，逐参含义官方有
#           ）
#   · Type 枚举 0=Base · 1=Boss · 2=Surface · 3=Cut
#   · 调用序出自官方示例 Insert_Boundary_Feature_Example_VB.htm 第 67-74 行
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **2 个工具** ⇒ 工具数 472 → 474
# ★★★ 等级如实：★★ 两个都**尚未真机验证** ⇒ ★ stitched（红线⑥）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

_COMMON = [
    Param(
        "face_index_1",
        int,
        default=0,
        description="Zero-based index of the first face on the body. Defaults to 0.",
    ),
    Param("face_index_2", int, default=1, description="Zero-based index of the second face on the body. Defaults to 1."),
    Param(
        "influence_type",
        int,
        default=0,
        required=False,
        description=(
            "Influence type: 0 = global, 1 = to next curve, 2 = to next sharp, 3 = to next edge. Defaults to 0."
        ),
    ),
    Param(
        "trim_curves",
        bool,
        default=False,
        required=False,
        description="Whether to trim the curves. Defaults to false.",
    ),
    Param(
        "blend_closed",
        bool,
        default=False,
        required=False,
        description="Whether to close the boundary blend. Defaults to false.",
    ),
    Param(
        "tangency_deg",
        float,
        default=15.0,
        required=False,
        description="Tangency angle in degrees. Defaults to 15.",
    ),
    Param(
        "merge_body",
        bool,
        default=True,
        required=False,
        description="Whether to merge the result into a single body in a multibody part. Defaults to true.",
    ),
]

SPECS_BATCH107 = [
    ToolSpec(
        name="solidworks_boundary_boss_report",
        title="Boundary Boss (official InsertNetBlend, Type=1)",
        module="sw_net_blend",
        function="insert_boundary_boss_report",
        inject="model",
        params=_COMMON,
        evidence=(
            "★ **边界凸台**：★ 用两个面建一个边界特征（官方 IFeatureManager::InsertNetBlend，Type=1 Boss）⇒ ★ 回一份回"
            "读报告 ✓ ★ 面由 face_index_1 / face_index_2（**面序号**）指定 —— ★ 声明式，★ 不收坐标（规则 3）✓ ★ 调用序"
            "照官方示例：清选区 ⇒ 选两个面（第 2 个 Append）⇒ 设曲线数据 x2 ⇒ 设方向数据 x2 ⇒ InsertNetBlend ✓ ★ 判据是"
            "**回读**：特征树计数前后 + 选区计数（事实 8：布尔返回值不可信）✓ ★★ 等级 stitched —— ★ 尚未真机验证（红线⑥"
            "）✓"
        ),
        doc=(
            "Create a boundary boss feature from two faces and return a read-back report. Writes a solid feature into t"
            "he active part and does not save the document; the faces are chosen by face index and both are selected fo"
            "r you after the selection is cleared."
        ),
    ),
    ToolSpec(
        name="solidworks_boundary_surface_report",
        title="Boundary Surface (official InsertNetBlend, Type=2)",
        module="sw_net_blend",
        function="insert_boundary_surface_report",
        inject="model",
        params=_COMMON,
        evidence=(
            "★ **边界曲面**：★ 与凸台同一个官方入口，★ 区别只在 Type=2 Surface ⇒ ★ 建出的是曲面体 ✓ ★ 面由 face_index_1"
            " / face_index_2（**面序号**）指定 —— ★ 声明式，★ 不收坐标（规则 3）✓ ★ 调用序照官方示例：清选区 ⇒ 选两个面"
            "（第 2 个 Append）⇒ 设曲线数据 x2 ⇒ 设方向数据 x2 ⇒ InsertNetBlend ✓ ★ 判据是**回读**：特征树计数前后 + 选"
            "区计数（事实 8：布尔返回值不可信）✓ ★★ 等级 stitched —— ★ 尚未真机验证（红线⑥）✓"
        ),
        doc=(
            "Create a boundary surface from two faces and return a read-back report. Writes a surface body into the act"
            "ive part and does not save the document; it is the same entry point as the boundary boss with the surface "
            "type, so no solid is added. The faces are chosen by face index and both are selected for you after the sel"
            "ection is cleared."
        ),
    ),
]
