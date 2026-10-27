"""★ B4 草图编辑·移动族的声明式工具（5 条）。

来源
====
仓库:   本项目自身（ToolSpec 声明层）
文件:   mcp-server/tool_specs_batch67.py
定位:   ★ 2026-10-03（轮 472）★ `specs/201-toolbar-gaps` 的 **B4**（用户工具栏：移动 / 旋转 /
  缩放实体比例 / 伸展实体，★ 另加同族的镜像）。
  ★ 实现层在 `scripts/sw_sketch_modify_ops.py`；★ **真机证据**在
  `output/b4-sketch-modify-evidence.json`（★ **5/5，判据见下**）。

★ **判据（★ 按操作分，不是一条判据套全部）** —— 这是 B4 最要紧的一条经验：
  · **改坐标系**的（移动 / 旋转 / 镜像）⇒ 判据 = `Sketch.ModelToSketchTransform.ArrayData` 变没变
    （★ 官方 Remarks：**前 9 个**是 3×3 旋转、**第 10-12 个**是平移）
  · **改几何**的（缩放 / 伸展）      ⇒ 判据 = 草图线段端点的 bbox 变没变
  ★★ 起因：我第一版**只**用 bbox ⇒ 移动 / 旋转 / 镜像三条**全记成"不能"**——
    而真因是**它们改的是坐标系、不改草图内点的坐标值** ⇒ ★ **判据选错，不是能力不行** ⚠

★ **规则 2**（`_mm` / `_deg` 后缀，只在边界换算一次）·
  **规则 3**（★ 本批的参数都是**在草图平面内的长度/角度**，★ 不是"裸坐标"——
  它们带 `_mm`/`_deg`，按门禁的判据「`_mm` 携带单位信息 ⇒ 不是裸坐标」放过）·
  **规则 6**（★ 实现层回来的是**带回读判据**的 dict，不是裸 `True`）。

官方依据（三源互证，详见 `scripts/sw_sketch_modify_ops.py` 的模块头）:
  · `C:\\swapi\\types\\IModelDoc2\\SketchModifyTranslate.md`
  · `C:\\swapi\\types\\IModelDoc2\\SketchModifyRotate.md`
  · `C:\\swapi\\types\\IModelDoc2\\SketchModifyScale.md`
  · `C:\\swapi\\types\\IModelDoc2\\SketchModifyFlip.md`
  · `C:\\swapi\\types\\IModelDocExtension\\Stretch.md`
  · `C:\\swapi\\types\\IMathTransform\\ArrayData.md`（★ 判据的依据）
许可:   本仓库 MIT。无第三方代码引入。
覆盖:   全文件
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   mcp-server/tool_specs_batch67.py
# 定位:   B4 草图编辑·移动族的声明式工具（5 条）。
# 官方依据: = 各条 ToolSpec 所包装函数的来源（见同文件内 `module=` / `function=`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

#: ★ 复用 batch66 的"选择器"说明尾巴（★ 那一条已过门禁）
_SEL = " ★ 声明式选择器（规则 3）：'__current_selection__' 或 'index:<n>'。"

_BATCH67: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_sketch_move_entities",
        title="Move Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_move",
        inject="model",
        param_alias={
            "start_x_mm": "start_x_mm",
            "start_y_mm": "start_y_mm",
            "end_x_mm": "end_x_mm",
            "end_y_mm": "end_y_mm",
        },
        params=[
            Param("start_x_mm", float, description="Start point X in millimetres."),
            Param("start_y_mm", float, description="Start point Y in millimetres."),
            Param("end_x_mm", float, description="End point X in millimetres."),
            Param("end_y_mm", float, description="End point Y in millimetres."),
        ],
        evidence=(
            "★ 移动实体：`IModelDoc2.SketchModifyTranslate`（★ 改的是**草图坐标系**）。★ 判据 = `ModelToSketchTransform"
            ".ArrayData` 的平移分量变化（★ 真机 5mm 严格对应）。"
        ),
        doc=(
            "Move the active sketch by the vector from a start point to an end point. Writes the sketch transform and d"
            "oes not save the document; the result carries a geometry read-back, so do not read it as a bare success fl"
            "ag."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_rotate_entities",
        title="Rotate Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_rotate",
        inject="model",
        param_alias={
            "center_x_mm": "center_x_mm",
            "center_y_mm": "center_y_mm",
            "angle_deg": "angle_deg",
        },
        params=[
            Param("center_x_mm", float, description="Centre X in millimetres."),
            Param("center_y_mm", float, description="Centre Y in millimetres."),
            Param(
                "angle_deg",
                float,
                description="Rotation angle in degrees, converted to radians once at this boundary.",
            ),
        ],
        evidence=(
            "★ 旋转实体：`IModelDoc2.SketchModifyRotate`（★ 改的是**草图坐标系**）。★ 真机验证：30° ⇒ 3×3 旋转矩阵首行"
            "变成 `[0.866025, -0.500001, 0]`（cos30°/sin30°）。"
        ),
        doc=(
            "Rotate the active sketch about a centre point by an angle. Writes the sketch transform and does not save t"
            "he document; the angle is given in degrees and converted to radians once at this boundary."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_scale_entities",
        title="Scale Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_scale",
        inject="model",
        param_alias={"factor": "factor"},
        params=[
            Param(
                "factor",
                float,
                description=(
                    "Scale factor, which must be greater than 0; it is a ratio, not a length, so it carries no unit suf"
                    "fix."
                ),
            ),
        ],
        evidence=(
            "★ 缩放实体比例：`IModelDoc2.SketchModifyScale` —— ★ **本批唯一有 bool 返回值**的成员。★ 真机验证：1.5 ⇒ 草"
            "图 bbox 从 ±20/±10 变成 ±30/±15（**正好 ×1.5**）。"
        ),
        doc=(
            "Apply a scale factor to the active sketch. Writes the sketch geometry and does not save the document; ok i"
            "s true only when the call returns non-false and the geometry read-back changes as well."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_stretch_entities",
        title="Stretch Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_stretch",
        inject="model",
        param_alias={
            "base_x_mm": "base_x_mm",
            "base_y_mm": "base_y_mm",
            "dest_x_mm": "dest_x_mm",
            "dest_y_mm": "dest_y_mm",
            "keep_relations": "keep_relations",
        },
        params=[
            Param("base_x_mm", float, description="Base point X in millimetres."),
            Param("base_y_mm", float, description="Base point Y in millimetres."),
            Param("dest_x_mm", float, description="Destination point X in millimetres."),
            Param("dest_y_mm", float, description="Destination point Y in millimetres."),
            Param(
                "keep_relations",
                bool,
                description="Whether to keep the sketch relations while stretching.",
            ),
        ],
        evidence=(
            "★ 伸展实体：**`IModelDocExtension.Stretch`**（★ 入口在 **Extension** 上，不是 `IModelDoc2`）。⚠ 官方说明「"
            "Stretch the **selected** entities」⇒ ★ **要求先选中实体**。"
        ),
        doc=(
            "Apply a stretch from a base point to a destination point on the sketch. Writes the sketch geometry and doe"
            "s not save the document; it selects the active sketch segments for you, because the official call only act"
            "s on a selection."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_flip_entities",
        title="Flip Sketch Entities",
        module="sw_sketch_modify_ops",
        function="sketch_flip",
        inject="model",
        param_alias={"axis_flag": "axis_flag"},
        params=[
            Param(
                "axis_flag",
                int,
                description=(
                    "Axis flag passed through as an integer; the official sources document no value table for it."
                ),
            ),
        ],
        evidence=(
            "★ 镜像/翻转：`IModelDoc2.SketchModifyFlip(AxisFlag)`。★ 真机验证：`axis_flag=1` ⇒ 3×3 旋转矩阵首行从 `[1,0"
            ",0]` 变成 **`[-1,0,0]`**（X 符号翻转）。⚠ `AxisFlag` 的取值表**官方未给** ⇒ 按铁律 5 原样透传、不猜语义。"
        ),
        doc=(
            "Mirror the active sketch about an axis selected by axis_flag. Writes the sketch geometry and does not save"
            " the document; the axis_flag value table is documented in neither official source, so it is passed through"
            " as an integer without interpretation."
        ),
    ),
]

#: ★★ 名字必须是 `SPECS_BATCH67` —— ★ 注册器按 `SPECS_*` 找（★ 我第一版写成 `SPECS`，
#:   报 "模块 tool_specs_batch67 里找不到任何 SPECS_* 列表"）。★ 本仓既有批次亦然
#:   （`tool_specs_batch66.py` 是 `SPECS_BATCH66`）。
SPECS_BATCH67 = _BATCH67
