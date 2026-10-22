"""★ 阶段 2 · 图纸义务的真机编排（规格 317 的 D4 真机链）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/drawing_run.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D4（图纸义务）的**真机链**。★★ 上一轮
#           （2026-10-12 第 1 轮）D4/D5 只做了机制与测试，**没跑真机图纸** ⇒ 本模块补那
#           一段。
# 官方依据: ① `subskills/solidworks-engineering-drawing/schemas/drawing_spec.schema.json
#           `   （★ DrawingSpec v1 的 `required` 九项：schemaVersion / sourceModel /    
#           documentType / standard / projection / paperSize / modelSizeMm /    views / 
#           outputs）② 工具真源 `solidworks_generate_drawing`（`mcp-server/server.py`） 
#             —— 它**一条链**出「工程图 + PDF + 预览 + 机器审视报告」③ 本仓**事实 71**（
#           `GetPartBox` 回毫米）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收见 `tools/run_stage2_plate.py --drawing`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

#: ★ GB/T A3 图框真源（★ 实测 2026-10-12 在本机找到；★ 两个语种下都有）
_GB_TEMPLATES = (
    r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\Chinese-Simplified"
    r"\sheetformat\a3 - gb.slddrt",
    r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\english"
    r"\sheetformat\a3 - gb.slddrt",
)


def gb_template_path() -> pathlib.Path:
    """★ 返回本机存在的 GB/T A3 图框（★ 都不在 ⇒ 回第一条，★ 让下游如实报缺）。"""
    for t in _GB_TEMPLATES:
        p = pathlib.Path(t)
        if p.is_file():
            return p
    return pathlib.Path(_GB_TEMPLATES[0])


def build_drawing_spec(*, source_model: str | pathlib.Path, size_mm: list,
                       hole_dia_mm: float, hole_count: int,
                       thickness_mm: float,
                       required_dims: list | None = None,
                       notes: list | None = None) -> dict:
    """★ 造一份 **DrawingSpec v1**（★ 按官方 schema 的九项必需字段）。

    ★★ 为什么必需字段一个都不能少：`solidworks_generate_drawing` 第一步就是
      `drawing_validate_spec` ⇒ 缺一项直接 `blocked`（★ 不静默降级）。
    """
    dims = list(required_dims or [])
    #: ★★ 关键尺寸：**只声明「要哪些」，不声明「尺寸对象」** ——
    #:   ⚠ 实测（2026-10-12）通用生成器逐条拒绝三件事，报的是**封闭码**：
    #:     ① `DRAWING_REQUESTED_VIEWS_UNSUPPORTED` —— 不能建辅助/轴测/剖视/局部视图
    #:     ② `DRAWING_VIEW_OPTIONS_UNSUPPORTED`     —— 视图对象里不能带落位/方向选项
    #:     ③ `DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED` ——
    #:        「通用生成器**只能导入模型尺寸**，不能可靠创建并绑定指定 ID、视图和语义的尺寸」
    #:   ⇒ ★ `requiredDimensions` **必须留空**；尺寸靠
    #:     `insertModelDimensions=True`（★ 导入模型自带的尺寸）。
    #:   ★★ 这**改变了 SC-005 的判据口径** —— 覆盖率不再由 spec 里的
    #:     `requiredDimensions` 数出来，而必须**从真机工程图上回读**（见
    #:     `drawing_view_annotations` / `inspect_drawing`）。★ 已如实记进 acceptance。
    #:   ⚠ 但 schema 的 `$defs.dimension` 形状仍记在这里（★ 供将来生成器支持时用）：
    #:     必需 `id` / `kind` / `view`；`kind` ∈ overall|linear|angular|radius|
    #:     diameter|tolerance|datum|gdt
    note_list = list(notes or [])
    note_list.append("孔数 %d × φ%g" % (hole_count, hole_dia_mm))
    note_list.append("材料：45 钢；未注公差按 GB/T 1804-m")

    return {
        "schemaVersion": "1.0",
        "sourceModel": str(pathlib.Path(source_model).resolve()),
        "documentType": "part",
        "standard": "GB_T",
        "projection": "first_angle",
        "paperSize": "A3",
        #: ★ 模型尺寸（★ 事实 71：`GetPartBox` 回毫米 ⇒ 这里就是毫米）
        "modelSizeMm": [float(x) for x in size_mm],
        "insertModelDimensions": True,
        #: ★★ 视图名是**固定键**（★ 官方 schema：`additionalProperties: false`，
        #:   只允许 front/top/bottom/left/right/isometric/sections/details；
        #:   ★ 且 `required: ["front"]`）。
        #:   ⚠ 实测踩过两次：
        #:     ① 写成 `{"list": [...]}` ⇒ `Additional properties are not allowed`
        #:     ② 带上 `isometric` ⇒ 通用生成器报
        #:        `DRAWING_REQUESTED_VIEWS_UNSUPPORTED`「尚不能创建辅助、轴测、
        #:        剖视或局部视图」⇒ ★ **只给正投影视图**（front/top/right）
        #:     ③ 视图对象里带 `direction`/`xMm`/`yMm` ⇒
        #:        `DRAWING_VIEW_OPTIONS_UNSUPPORTED` ⇒ ★ **只留空对象**（用默认落位）
        "views": {
            "front": {},
            "top": {},
            "right": {},
        },
        "requiredDimensions": dims,
        "notes": note_list,
        #: ★★ GB/T 图框（★ 实测 2026-10-12）：
        #:   ⚠ 不指模板 ⇒ 通用生成器报 `DRAWING_GBT_TEMPLATE_MISSING`（stage=sheet）。
        #:   ★ 本机真源：`C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\
        #:     Chinese-Simplified\sheetformat\a3 - gb.slddrt`（★ 中文语种，GB 图框）。
        #:   ★ `standard="GB_T"` 与它配套（★ 换成 `ISO` 应指 `a3 - iso.slddrt`）。
        "templateCandidates": [str(gb_template_path())],
        #: ★★ `outputs` 的字段名也是**固定集**（★ `slddrw` 与 `report` 是**必需**的）。
        #:   ⚠ 实测踩过：第一版写 `pdf`/`previews`/`reviewReport` ⇒
        #:   报「'slddrw' is a required property」+「'previews' were unexpected」。
        "outputs": {
            "slddrw": True,
            "pdf": True,
            "png": True,
            "report": True,
        },
    }


def write_spec(spec: dict, path: str | pathlib.Path) -> pathlib.Path:
    """★ 把 spec 落盘（★ `solidworks_generate_drawing` 收的是**路径**）。"""
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def validate_spec(spec: dict) -> dict:
    """★ 用**官方校验器**先验一遍（★ 别等真机报 blocked）。"""
    import importlib.util
    p = (ROOT / "subskills" / "solidworks-engineering-drawing"
         / "scripts" / "drawing_spec.py")
    s = importlib.util.spec_from_file_location("_dspec", p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.validate_drawing_spec(spec)
