"""
SolidWorks 工程图操作工具
"""
import math
import re
from fractions import Fraction
from pathlib import Path

try:
    from scripts.sw_preflight import import_com_dependencies
    from scripts.sw_connect import create_empty_dispatch_variant, get_com_member
    from scripts.sw_drawing_view_types import LABELLED_VIEW_TYPES
except ImportError:
    from sw_preflight import import_com_dependencies
    from sw_connect import create_empty_dispatch_variant, get_com_member
    from sw_drawing_view_types import LABELLED_VIEW_TYPES

pythoncom, _win32com, VARIANT = import_com_dependencies()


PAPER_SIZES = {
    "A4": {"code": 5, "width_m": 0.297, "height_m": 0.210},
    "A3": {"code": 6, "width_m": 0.420, "height_m": 0.297},
    "A2": {"code": 7, "width_m": 0.594, "height_m": 0.420},
    "A1": {"code": 8, "width_m": 0.841, "height_m": 0.594},
    "A0": {"code": 9, "width_m": 1.189, "height_m": 0.841},
}

STANDARD_DRAWING_SCALES = (10.0, 5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01)

# SolidWorks.Interop.swconst.swAlignDimensionType_e（SW2026 Interop 反射确认）。
ALIGN_DIMENSION_TYPES = {
    "auto_arrange": 0,
    "space_evenly": 1,
    "colinear": 2,
    "stagger": 3,
    "top_align_text": 4,
    "bottom_align_text": 5,
    "left_align_text": 6,
    "right_align_text": 7,
}

# SolidWorks.Interop.swconst.swAutoInsertCenterMarkTypes_e
# （SW2026 Interop 反射与官方 API 帮助交叉确认）。
AUTO_CENTER_MARK_TARGETS = {
    "holes": 1,
    "fillets": 2,
    "slots": 4,
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（非开源项目，无第三方许可）
# 文件:   C:\swapi\enums\swDetViewStyle_e.md
#         （对应托管程序集 SolidWorks.Interop.swconst.dll 的 swDetViewStyle_e）
# 定位:   CreateDetailViewAt4 第 4 个参数 Style 的取值域
# 取值:   官方 5 项全量照录，逐行对应，未增删、未改写
# 查证:   python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" enum swDetViewStyle_e
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 许可提示: C:\swapi 镜像自无许可的 offline-solidworks-api-docs，产物不可再分发进闭源产品
# ────────────────────────────────────────────────────────────────────
DET_VIEW_STYLES = {
    "standard": 0,      # swDetViewSTANDARD  = 0
    "broken": 1,        # swDetViewBROKEN    = 1
    "leader": 2,        # swDetViewLEADER    = 2
    "noleader": 3,      # swDetViewNOLEADER  = 3
    "connected": 4,     # swDetViewCONNECTED = 4
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（非开源项目，无第三方许可）
# 文件:   C:\swapi\enums\swDetCircleShowType_e.md
#         （对应托管程序集 SolidWorks.Interop.swconst.dll）
# 定位:   CreateDetailViewAt4 第 8 个参数 Showtype 的取值域
# 取值:   官方 3 项全量照录，逐行对应，未增删、未改写
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 许可提示: 同上，C:\swapi 产物不可再分发进闭源产品
# ────────────────────────────────────────────────────────────────────
DET_CIRCLE_SHOW_TYPES = {
    "profile": 0,       # swDetCirclePROFILE  = 0
    "circle": 1,        # swDetCircleCIRCLE   = 1
    "dont_show": 2,     # swDetCircleDONTSHOW = 2
}

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（非开源项目，无第三方许可）
# 文件:   C:\swapi\enums\swBomType_e.md
#         （对应托管程序集 SolidWorks.Interop.swconst.dll）
# 定位:   IModelDocExtension.InsertBomTable4 第 4 个参数 BomType 的取值域
# 取值:   官方 4 项全量照录，逐行对应，未增删、未改写
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 本表修正了原 insert_bom_table docstring 的错误：「1=顶层, 2=仅零件」
#   与官方相反，官方 1=仅零件(PartsOnly)、2=仅顶层(TopLevelOnly)。
# ────────────────────────────────────────────────────────────────────
BOM_TYPES = {
    "parts_only": 1,       # swBomType_PartsOnly
    "top_level_only": 2,   # swBomType_TopLevelOnly
    "indented": 3,         # swBomType_Indented
    "flattened": 4,        # swBomType_Flattened
}


def _safe_member(obj, name, *args, default=None):
    """@brief 读取工程图 COM 成员，失败时返回默认值。"""
    if obj is None:
        return default
    try:
        value = get_com_member(obj, name, *args)
        return default if value is None else value
    except Exception:
        return default


def _as_sequence(value):
    """@brief 统一 COM 数组、元组和单对象返回值。"""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _normalise_box(value):
    """@brief 将 COM Outline/GetBox 数组统一为二维边界框。"""
    if isinstance(value, dict) and {"left", "bottom", "right", "top"} <= set(value):
        try:
            x1, y1, x2, y2 = (float(value[key]) for key in ("left", "bottom", "right", "top"))
        except (TypeError, ValueError):
            return None
        return {"left": min(x1, x2), "bottom": min(y1, y2), "right": max(x1, x2), "top": max(y1, y2)}
    values = _as_sequence(value)
    try:
        if len(values) >= 6:
            x1, y1, x2, y2 = float(values[0]), float(values[1]), float(values[3]), float(values[4])
        elif len(values) >= 4:
            x1, y1, x2, y2 = map(float, values[:4])
        else:
            return None
    except (TypeError, ValueError):
        return None
    return {
        "left": min(x1, x2),
        "bottom": min(y1, y2),
        "right": max(x1, x2),
        "top": max(y1, y2),
    }


def _annotation_box(owner):
    """@brief 读取尺寸、注释或表格注解的二维包围盒。"""
    annotation = _safe_member(owner, "GetAnnotation") or owner
    return _normalise_box(_safe_member(annotation, "GetBox"))


def _view_display_dimensions(view):
    """@brief 兼容数组接口与链式接口，返回视图中的真实 DisplayDimension。"""
    dimensions = _as_sequence(_safe_member(view, "GetDisplayDimensions", default=[]))
    if dimensions:
        return dimensions
    current = _safe_member(view, "GetFirstDisplayDimension5") or _safe_member(view, "GetFirstDisplayDimension")
    while current is not None:
        dimensions.append(current)
        current = _safe_member(view, "GetNextDisplayDimension", current)
    return dimensions


def auto_arrange_drawing_dimensions(drawing_model, *, spacing_m=0.01, mode="auto_arrange") -> dict:
    """@brief 使用 SolidWorks 官方 AlignDimensions 对每个视图的尺寸自动排列。

    该接口只负责 SolidWorks 自身的尺寸布局，不提供尺寸文字包围盒，也不能证明最终
    图面无重叠。调用后仍必须导出 PDF/BMP 做视觉复核。
    """
    spacing, spacing_valid = _finite_positive(spacing_m, 0.01)
    if not spacing_valid or spacing > 0.1:
        raise ValueError("spacing_m 必须是 (0, 0.1] 米范围内的有限数值。")
    if mode not in ALIGN_DIMENSION_TYPES:
        raise ValueError(f"未知尺寸排列模式: {mode}")
    extension = _safe_member(drawing_model, "Extension")
    if extension is None or not hasattr(extension, "AlignDimensions"):
        return {
            "status": "blocked",
            "stage": "arrange",
            "method": "IModelDocExtension.AlignDimensions",
            "mode": mode,
            "spacing_m": spacing,
            "views": [],
            "selected_dimension_count": 0,
            "manual_review_required": True,
            "retryable": False,
            "error_code": "DRAWING_ALIGN_DIMENSIONS_API_UNAVAILABLE",
        }

    results = []
    total_selected = 0
    sheets = _as_sequence(_safe_member(drawing_model, "GetSheetNames", default=[]))
    for sheet_name in sheets or [""]:
        # ── 来源 ────────────────────────────────────────────────────────
        # 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 反射）
        # 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
        # 定位:   IDrawingDoc 上**按图纸名取页**的成员，官方签名为
        #             Sheet get_Sheet( String Name )
        #         即 COM 属性名是 ``Sheet``（参数化属性），不是 ``GetSheet``。
        # 本次改动: 原写作 ``_safe_member(drawing_model, "GetSheet", sheet_name)``。
        #         扫描该程序集的全部 1032 个接口，``GetSheet`` 只有两个**零参**
        #         版本，分别挂在 IFamilyTableAnnotation 与 IRevisionTableAnnotation
        #         上；IDrawingDoc 与 IModelDoc2 上均无 GetSheet。
        #         故原写法永远返回 None，再经 ``or`` 静默回落到 GetCurrentSheet()，
        #         使**指定图纸名的证据被记到当前页**——多页图纸下张冠李戴。
        #         这类「静默无效果」正是 AGENTS.md 铁律 2 要防的情况。
        # 查证:   python scripts/audit_call_arity.py（随本仓库提供）
        # ⚠ 本行为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
        # ────────────────────────────────────────────────────────────────
        sheet = _safe_member(drawing_model, "Sheet", sheet_name) or _safe_member(drawing_model, "GetCurrentSheet")
        for view in _as_sequence(_safe_member(sheet, "GetViews", default=[])):
            dimensions = _view_display_dimensions(view)
            _safe_member(drawing_model, "ClearSelection2", True)
            selected = 0
            for dimension in dimensions:
                annotation = _safe_member(dimension, "GetAnnotation")
                if annotation is None:
                    continue
                selected_ok = _safe_member(annotation, "Select2", selected > 0, 0, default=False)
                if not selected_ok:
                    selected_ok = _safe_member(annotation, "Select", selected > 0, default=False)
                if selected_ok:
                    selected += 1
            attempted = selected >= 2
            aligned = False
            error = None
            if attempted:
                try:
                    aligned = bool(get_com_member(extension, "AlignDimensions", ALIGN_DIMENSION_TYPES[mode], spacing))
                except Exception as exc:
                    error = str(exc)
            results.append({
                "sheet": str(sheet_name),
                "view": str(_safe_member(view, "Name", default="") or ""),
                "dimension_count": len(dimensions),
                "selected_count": selected,
                "attempted": attempted,
                "aligned": aligned,
                "error": error,
            })
            total_selected += selected
    _safe_member(drawing_model, "ClearSelection2", True)
    _safe_member(drawing_model, "ForceRebuild3", False)
    _safe_member(drawing_model, "GraphicsRedraw2")
    attempted_results = [item for item in results if item["attempted"]]
    failed_results = [item for item in attempted_results if not item["aligned"]]
    if not attempted_results:
        status = "review_required"
        error_code = "DRAWING_ALIGN_DIMENSIONS_NOT_ENOUGH_PER_VIEW"
    elif failed_results:
        status = "review_required"
        error_code = "DRAWING_ALIGN_DIMENSIONS_PARTIAL"
    else:
        status = "pass"
        error_code = None
    return {
        "status": status,
        "stage": "arrange",
        "method": "IModelDocExtension.AlignDimensions",
        "mode": mode,
        "enum_value": ALIGN_DIMENSION_TYPES[mode],
        "spacing_m": spacing,
        "views": results,
        "selected_dimension_count": total_selected,
        "aligned_view_count": sum(1 for item in results if item["aligned"]),
        "manual_review_required": True,
        "retryable": bool(failed_results),
        "error_code": error_code,
        "limitations": ["官方排列接口不返回文字包围盒；排列后仍需 PDF/BMP 目视复核。"],
    }


def _finite_positive(value, default):
    """@brief 将 COM 数值转成有限正数，否则使用保守默认值。"""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default), False
    if not math.isfinite(number) or number <= 0:
        return float(default), False
    return number, True


def _dimension_text_evidence(display_dimension) -> dict:
    """@brief 收集尺寸文字片段；不伪造 SolidWorks 最终格式化文本。"""
    parts = []
    for index, label in ((0, "all"), (1, "prefix"), (2, "suffix"), (3, "callout_above"), (4, "callout_below")):
        value = str(_safe_member(display_dimension, "GetText", index, default="") or "")
        if value:
            parts.append({"index": index, "kind": label, "text": value})
    all_text = next((item["text"] for item in parts if item["kind"] == "all"), "")
    if all_text:
        lines = all_text.splitlines() or [all_text]
        source = "display_dimension_get_text_all"
        rendered_value_available = True
    else:
        explicit = [item["text"] for item in parts if item["kind"] != "all"]
        # GetText() 在 SW2026 常只返回用户前后缀，不返回格式化后的主尺寸值。
        # 用 8 个等宽字符作为主值占位，避免把空字符串估成零宽度。
        lines = ["".join(explicit) + "0000.000"]
        source = "explicit_parts_plus_conservative_value_placeholder" if explicit else "conservative_value_placeholder"
        rendered_value_available = False
    return {
        "parts": parts,
        "estimation_lines": lines,
        "source": source,
        "rendered_value_available": rendered_value_available,
    }


def estimate_dimension_text_box(display_dimension, *, padding_m=None) -> dict:
    """@brief 用 IAnnotation 锚点和 ITextFormat 保守估算尺寸文字边界。

    SW2026 没有尺寸文字的原生 bounding-box API。本函数输出任意旋转文字都能
    被覆盖的轴对齐外接方框，并明确标记 ``source=estimated``；不能作为原生几何证据。
    """
    annotation = _safe_member(display_dimension, "GetAnnotation")
    position = _as_sequence(_safe_member(annotation, "GetPosition", default=[]))
    try:
        x, y = float(position[0]), float(position[1])
        position_available = math.isfinite(x) and math.isfinite(y)
    except (IndexError, TypeError, ValueError):
        x = y = 0.0
        position_available = False

    text_format = _safe_member(annotation, "GetTextFormat", 0)
    format_source = "IAnnotation.GetTextFormat(0)"
    if text_format is None:
        text_format = _safe_member(display_dimension, "GetTextFormat")
        format_source = "IDisplayDimension.GetTextFormat()"
    char_height, char_height_available = _finite_positive(
        _safe_member(text_format, "CharHeight"),
        0.0035,
    )
    width_factor, width_factor_available = _finite_positive(
        _safe_member(text_format, "WidthFactor"),
        1.0,
    )
    spacing_factor, spacing_factor_available = _finite_positive(
        _safe_member(text_format, "CharSpacingFactor"),
        1.0,
    )
    text = _dimension_text_evidence(display_dimension)
    lines = text["estimation_lines"] or ["0000.000"]

    def line_units(line):
        """@brief 估算单行字宽；中文和全角字符按一个字高计。"""
        units = 0.0
        for character in line or " ":
            units += 1.0 if ord(character) > 0xFF else 0.62
        return max(units, 0.62)

    max_units = max(line_units(line) for line in lines)
    line_count = max(1, len(lines))
    estimated_width = max_units * char_height * width_factor * spacing_factor
    estimated_height = line_count * char_height * 1.25
    padding = max(0.001, char_height * 0.4) if padding_m is None else max(0.0, float(padding_m))
    # 尺寸文字角度未由 API 暴露；使用矩形对角线作为任意旋转下的方形包络。
    half_extent = math.hypot(estimated_width, estimated_height) / 2.0 + padding
    box = None
    if position_available:
        box = {
            "left": x - half_extent,
            "bottom": y - half_extent,
            "right": x + half_extent,
            "top": y + half_extent,
        }

    available_fields = sum((position_available, char_height_available, width_factor_available, spacing_factor_available))
    if position_available and available_fields == 4 and text["rendered_value_available"]:
        confidence = "medium"
    elif position_available:
        confidence = "low"
    else:
        confidence = "unavailable"
    return {
        "box": box,
        "source": "estimated",
        "confidence": confidence,
        "method": "annotation_position_text_format_arbitrary_rotation_envelope",
        "native_bounding_box_available": False,
        "position_m": [x, y] if position_available else None,
        "text_evidence": text,
        "text_format": {
            "source": format_source if text_format is not None else "conservative_defaults",
            "char_height_m": char_height,
            "width_factor": width_factor,
            "char_spacing_factor": spacing_factor,
            "char_height_available": char_height_available,
            "width_factor_available": width_factor_available,
            "char_spacing_factor_available": spacing_factor_available,
        },
        "estimated_unrotated_size_m": {"width": estimated_width, "height": estimated_height},
        "padding_m": padding,
        "orientation_assumption": "unknown_angle_conservative_square_envelope",
        "limitations": [
            "SolidWorks 2026 IAnnotation 不提供尺寸文字原生包围盒",
            "主尺寸格式化值可能不由 GetText 返回，缺失时使用保守占位宽度",
            "估算只能用于碰撞风险筛查，最终交付仍需 PDF/BMP 目视复核",
        ],
    }


def select_drawing_template(candidates, *, paper_size="A3", require_gbt=True) -> dict:
    """@brief 从本机候选中选择图幅匹配且具有 GB/T 标识的图框模板。

    仅把文件名和扩展名作为候选证据，不把命名匹配宣称为模板内容已合规。
    """
    paper_size = str(paper_size).upper()
    if paper_size not in PAPER_SIZES:
        raise ValueError(f"不支持的图幅: {paper_size}")
    inspected = []
    for raw_path in candidates or []:
        path = Path(raw_path).expanduser().resolve()
        name = path.stem.casefold()
        compact_name = re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", name)
        is_format = path.suffix.casefold() == ".slddrt"
        paper_match = paper_size.casefold() in name
        gbt_match = (
            "gbt" in compact_name
            or "国标" in compact_name
            or bool(re.search(r"(?:^|[^a-z0-9])gb(?:t)?(?:[^a-z0-9]|$)", name, re.IGNORECASE))
        )
        path_text = str(path).casefold()
        localized_candidate = any(token in path_text for token in ("chinese-simplified", "chinese_simplified", "简体中文"))
        score = int(path.is_file()) * 8 + int(is_format) * 4 + int(paper_match) * 2 + int(gbt_match) + int(localized_candidate) * 2
        inspected.append({
            "path": str(path),
            "exists": path.is_file(),
            "is_sheet_format": is_format,
            "paper_match": paper_match,
            "gbt_candidate": gbt_match,
            "localized_candidate": localized_candidate,
            "score": score,
        })
    eligible = [item for item in inspected if item["exists"] and item["is_sheet_format"] and item["paper_match"]]
    if require_gbt:
        eligible = [item for item in eligible if item["gbt_candidate"]]
    selected = max(eligible, key=lambda item: (item["score"], item["path"].casefold()), default=None)
    return {
        "status": "pass" if selected else "blocked",
        "paper_size": paper_size,
        "selected": selected["path"] if selected else None,
        "candidates": inspected,
        "gbt_content_verified": False,
        "manual_review_required": True,
        "error_code": None if selected else "DRAWING_GBT_TEMPLATE_MISSING" if require_gbt else "DRAWING_TEMPLATE_MISSING",
    }


def plan_standard_view_layout(
    model_size_m,
    *,
    paper_size="A3",
    projection="third_angle",
    requested_scale=None,
    margin_m=0.012,
    gap_m=0.018,
    title_block_width_m=0.180,
    title_block_height_m=0.055,
) -> dict:
    """@brief 为三视图计算不会侵入标题栏的自适应或指定比例布局。"""
    paper_size = str(paper_size).upper()
    projection = str(projection).lower()
    if projection not in {"first_angle", "third_angle"}:
        raise ValueError("projection 必须是 first_angle 或 third_angle")
    spec = PAPER_SIZES.get(paper_size)
    if spec is None:
        raise ValueError(f"不支持的图幅: {paper_size}")
    try:
        width, height, depth = (float(item) for item in model_size_m)
    except (TypeError, ValueError) as exc:
        raise ValueError("model_size_m 必须包含三个米制外形尺寸") from exc
    if min(width, height, depth) <= 0 or not all(math.isfinite(item) for item in (width, height, depth)):
        raise ValueError("模型外形尺寸必须为有限正数")

    sheet_width = spec["width_m"]
    sheet_height = spec["height_m"]
    working_left = margin_m
    working_bottom = margin_m + title_block_height_m + gap_m
    working_right = sheet_width - margin_m
    working_top = sheet_height - margin_m
    available_width = working_right - working_left
    available_height = working_top - working_bottom
    raw_scale = min(
        (available_width - gap_m) / (width + depth),
        (available_height - gap_m) / (height + depth),
    )
    if raw_scale <= 0:
        return {
            "status": "blocked",
            "paper_size": paper_size,
            "sheet": {"width_m": sheet_width, "height_m": sheet_height},
            "views": [],
            "manual_review_required": True,
            "retryable": True,
            "error_code": "DRAWING_LAYOUT_WORKING_AREA_INVALID",
        }
    if requested_scale is None:
        scale = next((item for item in STANDARD_DRAWING_SCALES if item <= raw_scale + 1e-12), raw_scale)
    else:
        try:
            if isinstance(requested_scale, str):
                numerator_text, denominator_text = requested_scale.split(":", 1)
                scale = float(numerator_text.strip()) / float(denominator_text.strip())
            else:
                scale = float(requested_scale)
        except (TypeError, ValueError, ZeroDivisionError):
            return {
                "status": "blocked",
                "paper_size": paper_size,
                "views": [],
                "manual_review_required": True,
                "retryable": False,
                "error_code": "DRAWING_SCALE_INVALID",
            }
        if scale <= 0 or not math.isfinite(scale):
            return {
                "status": "blocked",
                "paper_size": paper_size,
                "views": [],
                "manual_review_required": True,
                "retryable": False,
                "error_code": "DRAWING_SCALE_INVALID",
            }
        if scale > raw_scale + 1e-12:
            return {
                "status": "blocked",
                "paper_size": paper_size,
                "requested_scale": requested_scale,
                "maximum_fit_scale": raw_scale,
                "views": [],
                "manual_review_required": True,
                "retryable": True,
                "error_code": "DRAWING_SCALE_DOES_NOT_FIT",
            }

    front_w, front_h = width * scale, height * scale
    top_w, top_h = width * scale, depth * scale
    right_w, right_h = depth * scale, height * scale
    layout_w = front_w + gap_m + right_w
    layout_h = front_h + gap_m + top_h
    origin_x = working_left + max(0.0, (available_width - layout_w) / 2.0)
    origin_y = working_bottom + max(0.0, (available_height - layout_h) / 2.0)

    def view_record(name, left, bottom, view_width, view_height):
        """@brief 创建单个视图的中心点与边界框记录。"""
        return {
            "name": name,
            "center": [left + view_width / 2.0, bottom + view_height / 2.0],
            "box": {"left": left, "bottom": bottom, "right": left + view_width, "top": bottom + view_height},
        }

    if projection == "first_angle":
        # GB/T 第一角投影：俯视在主视下方，右视在主视左侧。
        views = [
            view_record("*Front", origin_x + right_w + gap_m, origin_y + top_h + gap_m, front_w, front_h),
            view_record("*Top", origin_x + right_w + gap_m, origin_y, top_w, top_h),
            view_record("*Right", origin_x, origin_y + top_h + gap_m, right_w, right_h),
        ]
    else:
        views = [
            view_record("*Front", origin_x, origin_y, front_w, front_h),
            view_record("*Top", origin_x, origin_y + front_h + gap_m, top_w, top_h),
            view_record("*Right", origin_x + front_w + gap_m, origin_y, right_w, right_h),
        ]
    title_box = {
        "left": sheet_width - margin_m - title_block_width_m,
        "bottom": margin_m,
        "right": sheet_width - margin_m,
        "top": margin_m + title_block_height_m,
    }
    return {
        "status": "pass",
        "paper_size": paper_size,
        "projection": projection,
        "gap_m": gap_m,
        "sheet": {"width_m": sheet_width, "height_m": sheet_height},
        "working_area": {"left": working_left, "bottom": working_bottom, "right": working_right, "top": working_top},
        "title_block_box": title_box,
        "scale": scale,
        "scale_ratio": list(_scale_ratio(scale)),
        "views": views,
        "manual_review_required": True,
    }


def _scale_ratio(scale):
    """@brief 将浮点比例转换为 SolidWorks 可接受的整数比。"""
    ratio = Fraction(float(scale)).limit_denominator(1000)
    return ratio.numerator, ratio.denominator


def _apply_view_layout(view, item, numerator, denominator) -> dict:
    """@brief 将已创建视图移动到规划中心并设置独立比例。"""
    center = [float(item["center"][0]), float(item["center"][1])]
    if hasattr(view, "UseParentScale"):
        view.UseParentScale = False
    if hasattr(view, "PositionLocked"):
        view.PositionLocked = False
    view.ScaleRatio = (int(numerator), int(denominator))
    position = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, center)
    method = getattr(view, "SetViewPosition", None)
    if method is not None:
        moved = bool(get_com_member(view, "SetViewPosition", position, False))
        if not moved:
            raise RuntimeError(f"SetViewPosition 返回失败: {center}")
    else:
        view.Position = tuple(center)
    actual_position = _view_position(view)
    position_verified = bool(
        actual_position
        and abs(actual_position[0] - center[0]) <= 1e-5
        and abs(actual_position[1] - center[1]) <= 1e-5
    )
    if not position_verified:
        raise RuntimeError(f"视图位置回读不一致: requested={center}, actual={actual_position}")
    return {
        "name": item["name"],
        "actual_name": str(_safe_member(view, "Name", default="")),
        "orientation": str(_safe_member(view, "GetOrientationName", default="")),
        "center": center,
        "actual_center": list(actual_position),
        "position_verified": True,
        "scale_ratio": [int(numerator), int(denominator)],
    }


def _normalise_orientation(value):
    """@brief 将 SolidWorks 标准视图方向统一为 front/top/right 键。"""
    compact = re.sub(r"[^a-z\u4e00-\u9fff]", "", str(value or "").casefold())
    aliases = {
        "front": "front",
        "top": "top",
        "right": "right",
        "frontview": "front",
        "topview": "top",
        "rightview": "right",
        "前视": "front",
        "主视": "front",
        "上视": "top",
        "俯视": "top",
        "右视": "right",
    }
    return aliases.get(compact)


def _view_position(view):
    """@brief 读取工程图视图中心位置。"""
    values = _as_sequence(_safe_member(view, "Position", default=[]))
    try:
        if len(values) < 2:
            return None
        return float(values[0]), float(values[1])
    except (IndexError, TypeError, ValueError):
        return None


def _set_view_center(view, center) -> list[float]:
    """@brief 移动视图并回读中心点，供真实包围盒二次排布复用。"""
    target = [float(center[0]), float(center[1])]
    position = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, target)
    method = getattr(view, "SetViewPosition", None)
    if method is not None:
        moved = bool(get_com_member(view, "SetViewPosition", position, False))
        if not moved:
            raise RuntimeError(f"SetViewPosition 返回失败: {target}")
    else:
        view.Position = tuple(target)
    actual = _view_position(view)
    if actual is None or abs(actual[0] - target[0]) > 1e-5 or abs(actual[1] - target[1]) > 1e-5:
        raise RuntimeError(f"视图位置回读不一致: requested={target}, actual={actual}")
    return [float(actual[0]), float(actual[1])]


def _refine_standard_view_spacing(view_objects, view_records, projection, gap_m=0.018) -> dict:
    """@brief 根据 SolidWorks 实际视图边界消除三视图之间的确认重叠。"""
    required = {"front", "top", "right"}
    if set(view_objects) < required:
        return {"status": "review_required", "method": "native_outline", "adjustments": [], "error_code": "DRAWING_VIEW_OUTLINES_INCOMPLETE"}
    boxes = {key: _normalise_box(_safe_member(view, "GetOutline")) for key, view in view_objects.items()}
    if any(box is None for box in boxes.values()):
        return {"status": "review_required", "method": "native_outline", "adjustments": [], "error_code": "DRAWING_VIEW_OUTLINES_INCOMPLETE"}
    try:
        gap = max(0.001, float(gap_m))
    except (TypeError, ValueError):
        gap = 0.018
    records = {item["name"]: item for item in view_records}
    names = {"front": "*Front", "top": "*Top", "right": "*Right"}
    adjustments = []

    def move_if_needed(axis, orientation, target_value):
        current_box = boxes[orientation]
        current_center = _view_position(view_objects[orientation])
        if current_center is None:
            return
        delta = float(target_value) - current_center[axis]
        if abs(delta) <= 1e-7:
            return
        new_center = list(current_center)
        new_center[axis] = float(target_value)
        actual_center = _set_view_center(view_objects[orientation], new_center)
        moved_box = _normalise_box(_safe_member(view_objects[orientation], "GetOutline"))
        boxes[orientation] = moved_box or current_box
        record = records.get(names[orientation])
        if record is not None:
            record["center"] = list(actual_center)
            record["actual_center"] = list(actual_center)
            record["layout_refined_from_native_outline"] = True
        adjustments.append({"view": names[orientation], "axis": "x" if axis == 0 else "y", "delta_m": delta, "center": list(actual_center)})

    front = boxes["front"]
    right = boxes["right"]
    top = boxes["top"]
    right_width = right["right"] - right["left"]
    top_height = top["top"] - top["bottom"]
    if projection == "first_angle":
        right_target_x = front["left"] - gap - right_width / 2.0
        top_target_y = front["bottom"] - gap - top_height / 2.0
    else:
        right_target_x = front["right"] + gap + right_width / 2.0
        top_target_y = front["top"] + gap + top_height / 2.0
    move_if_needed(0, "right", right_target_x)
    move_if_needed(1, "top", top_target_y)
    return {
        "status": "pass",
        "method": "native_outline",
        "projection": projection,
        "gap_m": gap,
        "adjustments": adjustments,
        "error_code": None,
        "manual_review_required": True,
    }


def _collect_drawing_views(drawing_model):
    """@brief 同时尝试 Sheet.GetViews 与 GetFirstView 链读取真实模型视图。"""
    sheet = _safe_member(drawing_model, "GetCurrentSheet")
    views = _as_sequence(_safe_member(sheet, "GetViews", default=[]))
    if len(views) >= 3:
        return views
    traversed = []
    sheet_view = _safe_member(drawing_model, "GetFirstView")
    current = _safe_member(sheet_view, "GetNextView")
    guard = 0
    while current is not None and guard < 1000:
        traversed.append(current)
        current = _safe_member(current, "GetNextView")
        guard += 1
    return traversed if len(traversed) >= len(views) else views


def _map_native_standard_views(views):
    """@brief 依据方向名、基准视图关系和原始位置映射第三角三视图。"""
    by_orientation = {}
    diagnostics = []
    for view in views:
        orientation_name = str(_safe_member(view, "GetOrientationName", default=""))
        orientation = _normalise_orientation(orientation_name)
        base_view = _safe_member(view, "GetBaseView")
        position = _view_position(view)
        diagnostics.append({
            "name": str(_safe_member(view, "Name", default="")),
            "orientation": orientation_name,
            "position": list(position) if position else None,
            "has_base_view": base_view is not None,
            "referenced_model": str(_safe_member(view, "GetReferencedModelName", default="")),
        })
        if orientation and orientation not in by_orientation:
            by_orientation[orientation] = view
    if set(by_orientation) >= {"front", "top", "right"}:
        return by_orientation, diagnostics, "orientation_name"

    positioned = [(view, _view_position(view), _safe_member(view, "GetBaseView")) for view in views]
    positioned = [item for item in positioned if item[1] is not None]
    if len(positioned) >= 3:
        base_candidates = [item for item in positioned if item[2] is None]
        front = min(base_candidates or positioned, key=lambda item: item[1][0] + item[1][1])
        remaining = [item for item in positioned if item[0] is not front[0]]
        top = max(remaining, key=lambda item: item[1][1] - front[1][1])
        right_candidates = [item for item in remaining if item[0] is not top[0]]
        if right_candidates:
            right = max(right_candidates, key=lambda item: item[1][0] - front[1][0])
            return {"front": front[0], "top": top[0], "right": right[0]}, diagnostics, "base_and_position"
    return by_orientation, diagnostics, "unresolved"


def _map_standard_views_from_sheet_views(sheet_views):
    """@brief 从整张图纸视图中筛出并映射前、俯、右三个标准视图。"""
    oriented_fronts = [
        view for view in sheet_views
        if _normalise_orientation(_safe_member(view, "GetOrientationName", default="")) == "front"
    ]
    base_candidates = oriented_fronts or [
        view for view in sheet_views
        if _safe_member(view, "Type", default=None) == 7 and _safe_member(view, "GetBaseView") is None
    ]
    standard_candidates = [*base_candidates, *[
        view for view in sheet_views if _safe_member(view, "Type", default=None) == 4
    ]]
    return _map_native_standard_views(standard_candidates)


def create_adaptive_standard_views(drawing_model, part_path, layout) -> dict:
    """@brief 按预先计算的布局创建前、俯、右三个真实工程图视图。"""
    created = []
    view_objects = {}
    numerator, denominator = layout.get("scale_ratio") or _scale_ratio(layout["scale"])
    for item in layout.get("views", []):
        center = item["center"]
        # ★★ 走 `_create_model_view`（不是直调）—— 它会在直调失败时按**本地化别名**重试
        #   （事实 494：中文界面的标准视图名是 `*前视`/`*上视`/`*右视`，照抄英文 `*Front` 必回 None）
        view = _create_model_view(drawing_model, part_path, item["name"], center[0], center[1])
        if view is None:
            if not created:
                projection = str(layout.get("projection", "third_angle")).lower()
                # 部分 SolidWorks 版本（包括当前 SW2026 COM 代理）没有
                # CreateFirstAngleViews2。先用可用的原生三视图 API 建立视图，
                # 再按 DrawingSpec 的第一角/第三角布局重新定位并回读位置。
                method_candidates = (
                    ("CreateFirstAngleViews2", "Create3rdAngleViews2")
                    if projection == "first_angle"
                    else ("Create3rdAngleViews2",)
                )
                native_created = False
                method_name = None
                for candidate in method_candidates:
                    if bool(_safe_member(drawing_model, candidate, str(part_path), default=False)):
                        native_created = True
                        method_name = candidate
                        break
                if native_created:
                    _safe_member(drawing_model, "ForceRebuild3", False)
                    _safe_member(drawing_model, "GraphicsRedraw2")
                    native_views = _collect_drawing_views(drawing_model)
                    by_orientation, diagnostics, mapping_method = _map_native_standard_views(native_views)
                    expected = {"front": "*Front", "top": "*Top", "right": "*Right"}
                    if set(by_orientation) >= set(expected):
                        layout_by_name = {entry["name"]: entry for entry in layout.get("views", [])}
                        try:
                            for orientation in ("front", "top", "right"):
                                view_objects[orientation] = by_orientation[orientation]
                                created.append(
                                    _apply_view_layout(
                                        by_orientation[orientation],
                                        layout_by_name[expected[orientation]],
                                        numerator,
                                        denominator,
                                    )
                                )
                        except Exception as exc:
                            return {
                                "status": "failed",
                                "stage": "layout",
                                "backend": f"native_{projection}",
                                "views": created,
                                "native_view_diagnostics": diagnostics,
                                "retryable": True,
                                "error_code": "DRAWING_VIEW_POSITION_FAILED",
                                "error": str(exc),
                            }
                        refinement = _refine_standard_view_spacing(
                            view_objects,
                            created,
                            projection,
                            layout.get("gap_m", 0.018),
                        )
                        backend = (
                            "native_3rd_angle"
                            if projection == "third_angle"
                            else "native_first_angle"
                            if method_name == "CreateFirstAngleViews2"
                            else "native_first_angle_via_3rd_angle"
                        )
                        return {
                            "status": "pass",
                            "stage": "create",
                            "backend": backend,
                            "creation_method": method_name,
                            "mapping_method": mapping_method,
                            "native_view_diagnostics": diagnostics,
                            "layout_refinement": refinement,
                            "views": created,
                            "view_count": len(created),
                            "retryable": False,
                            "error_code": None,
                            "manual_review_required": True,
                        }
                    return {
                        "status": "failed",
                        "stage": "map",
                        "backend": f"native_{projection}",
                        "views": [],
                        "orientations_found": sorted(by_orientation),
                        "mapping_method": mapping_method,
                        "native_view_diagnostics": diagnostics,
                        "retryable": True,
                        "error_code": "DRAWING_VIEW_ORIENTATION_MAP_FAILED",
                    }
            return {
                "status": "failed",
                "stage": "create",
                "views": created,
                "retryable": True,
                "error_code": "DRAWING_VIEW_CREATE_FAILED",
            }
        try:
            orientation = _normalise_orientation(item["name"])
            if orientation:
                view_objects[orientation] = view
            created.append(_apply_view_layout(view, item, numerator, denominator))
        except Exception as exc:
            return {
                "status": "failed",
                "stage": "layout",
                "backend": "individual_model_views",
                "views": created,
                "retryable": True,
                "error_code": "DRAWING_VIEW_POSITION_FAILED",
                "error": str(exc),
            }
    refinement = _refine_standard_view_spacing(
        view_objects,
        created,
        str(layout.get("projection", "third_angle")).lower(),
        layout.get("gap_m", 0.018),
    )
    return {
        "status": "pass",
        "stage": "create",
        "backend": "individual_model_views",
        "views": created,
        "layout_refinement": refinement,
        "view_count": len(created),
        "retryable": False,
        "error_code": None,
        "manual_review_required": True,
    }


def create_standard_views(drawing_model, part_path):
    """
    创建标准三视图（第三角投影法）

    参数:
        drawing_model: IDrawingDoc
        part_path: 零件文件路径
    """
    return drawing_model.Create3rdAngleViews2(part_path)


def create_standard_views_with_projection(drawing_model, part_path, projection="first_angle"):
    """@brief 按指定投影法创建原生三视图并返回明确失败状态。"""
    projection = str(projection).lower()
    if projection not in {"first_angle", "third_angle"}:
        raise ValueError("projection 必须是 first_angle 或 third_angle")
    method_name = "CreateFirstAngleViews2" if projection == "first_angle" else "Create3rdAngleViews2"
    method = getattr(drawing_model, method_name, None)
    if method is None:
        return {
            "status": "blocked",
            "projection": projection,
            "method": method_name,
            "error_code": "DRAWING_PROJECTION_API_UNAVAILABLE",
            "manual_review_required": True,
        }
    created = bool(method(part_path))
    return {
        "status": "pass" if created else "failed",
        "projection": projection,
        "method": method_name,
        "created": created,
        "error_code": None if created else "DRAWING_STANDARD_VIEWS_CREATE_FAILED",
        "manual_review_required": True,
    }


#: ★★ 标准视图名的**本地化别名表**（2026-10-03 真机实测，`docs/known-facts.md` **事实 494**）：
#:   · 官方 `IDrawingDoc.CreateDrawViewFromModelView3` 的 Remarks 逐字要求 `ViewName`
#:     "**exactly match** the name of the model view"，而它给的例子 **`"*Front"` 是英文界面**的取值
#:     ⇒ ★ **中文界面**下真名是 `*前视` / `*上视` / `*右视` … ⇒ ★ **照抄英文名必回 `None`**，
#:     且**无异常、无错误码**（从返回值完全看不出原因）。
#:   · ★ 真机单变量矩阵（同一零件 / 模板 / 位置，只变名字）：`*前视` 等 **6/7 建成**，`*Front` **回 None**。
#:   · ★ 顺序即优先级：**英文名在前** ⇒ ★ 英文界面下第一次就命中，**行为与改动前完全一致**。
_VIEW_NAME_ALIASES = {
    "front": ("*Front", "*前视", "*正视于"),
    "back": ("*Back", "*后视"),
    "left": ("*Left", "*左视"),
    "right": ("*Right", "*右视"),
    "top": ("*Top", "*上视"),
    "bottom": ("*Bottom", "*下视"),
    "isometric": ("*Isometric", "*等轴测"),
    "trimetric": ("*Trimetric", "*上下二等角轴测"),
    "dimetric": ("*Dimetric", "*左右二等角轴测"),
}


def _view_name_candidates(view_name):
    """★ 给一个视图名，回**候选序列**（原样排第一，随后是它的本地化/英文别名）。"""
    out = [view_name]
    for aliases in _VIEW_NAME_ALIASES.values():
        if view_name in aliases:
            out.extend(a for a in aliases if a not in out)
            break
    return out


def _create_model_view(drawing_model, part_path, view_name, x, y):
    """★ 建模型视图：**直调失败就按本地化别名重试，命中即止**（事实 494 的正解）。

    ★ 为什么用"别名重试"而不是"先问模型要名字"：★ 建视图时 `part_path` 指向的零件
      **未必是打开着的**，而 `IModelDoc2.GetModelViewNames()` 需要一个**模型文档对象**
      ⇒ ★ 别名重试**不依赖任何文档状态**，且英文界面下第一次就命中（行为不变）。
    ★ 判据：返回**非 None** 即成功；★ 所有候选都失败 ⇒ 返回 `None`（★ 不抛异常，交调用方处理）。
    """
    for candidate in _view_name_candidates(view_name):
        view = drawing_model.CreateDrawViewFromModelView3(part_path, candidate, x, y, 0)
        if view is not None:
            return view
    return None


def add_view(drawing_model, part_path, view_name, x, y, scale=None):
    """
    添加单个视图

    参数:
        view_name: 视图方向名称
            "*Front", "*Back", "*Top", "*Bottom",
            "*Left", "*Right", "*Isometric",
            "*Trimetric", "*Dimetric"
            ★★ **传英文名即可（推荐）** —— 中文界面下本函数会**自动改用本地化名**
            （`*前视` / `*上视` / `*右视` …）。★ 依据：`docs/known-facts.md` 事实 494。
        x, y: 视图放置位置（米）
        scale: 视图比例（如 0.5 表示 1:2），None 使用图纸默认
    """
    view = _create_model_view(drawing_model, part_path, view_name, x, y)
    if view and scale:
        view.ScaleRatio = (1.0, 1.0 / scale)
    return view


def add_section_view(drawing_model, x, y):
    """在当前选择的剖切线位置创建剖视图"""
    return drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md
#         交叉核对: D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\
#                  SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IDrawingDoc~CreateDetailViewAt4.html
# 定位:   局部详图创建入口。官方共 12 个参数：
#           (Double X, Double Y, Double Z, Int Style, Double Scale1, Double Scale2,
#            String LabelIn, Int Showtype, Boolean FullOutline, Boolean JaggedOutline,
#            Boolean NoOutline, Int ShapeIntensity)
# 本次改动: 原实现只传 7 个实参 (x, y, 0, 0, scale, 0, "")，与官方参数个数不符。
#           现补齐 12 参；scale 语义定为 Scale1(分子)、Scale2 固定 1.0，
#           故 scale=2 表示 2:1，与原 docstring 意图一致。
# 枚举来源: DET_VIEW_STYLES / DET_CIRCLE_SHOW_TYPES（见本文件上方来源块）
# 查证:   python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" \
#           member IDrawingDoc CreateDetailViewAt4
# ⚠ 本函数为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ ShapeIntensity 有效范围 1(最强)–5(最弱)，且仅在 jagged_outline=True
#   且 no_outline=False 时生效；此处默认 0 即「不生效」，非越界取值。
# ────────────────────────────────────────────────────────────────────
def add_detail_view(
    drawing_model,
    x,
    y,
    scale=2.0,
    *,
    style=DET_VIEW_STYLES["standard"],
    label="",
    show_type=DET_CIRCLE_SHOW_TYPES["profile"],
    full_outline=False,
    jagged_outline=False,
    no_outline=False,
    shape_intensity=0,
):
    """创建局部放大视图（局部详图）

    :param scale: 比例分子 Scale1；分母 Scale2 固定传 1.0，故 scale=2 表示 2:1
    :param style: ``DET_VIEW_STYLES`` 详图样式，默认 ``standard``(0)
    :param show_type: ``DET_CIRCLE_SHOW_TYPES`` 圆/轮廓类型，默认 ``profile``(0)
    :param shape_intensity: 锯齿轮廓强度，有效范围 1(最强)–5(最弱)，
        仅当 ``jagged_outline`` 为 True 且 ``no_outline`` 为 False 时有效

    .. note::
       **签名依据（本函数为静态签名比对后修正，未在本机实测，见 AGENTS.md 铁律 2）**

       官方签名 ``IDrawingDoc.CreateDetailViewAt4`` 共 **12 个参数**：
       ``(Double X, Double Y, Double Z, Int Style, Double Scale1, Double Scale2,
       String LabelIn, Int Showtype, Boolean FullOutline, Boolean JaggedOutline,
       Boolean NoOutline, Int ShapeIntensity)``
       依据 ``C:\\swapi\\types\\IDrawingDoc\\CreateDetailViewAt4.md``。

       ⚠ 修正前此处只传 7 个实参 ``(x, y, 0, 0, scale, 0, "")``，
       与官方参数个数不符；且第 4 个实参 ``0`` 会被当作 ``Style``
       （恰为 ``swDetViewSTANDARD``，值正确），第 5 个 ``scale`` 会被当作
       ``Scale1``（分子），原意得以保留，但缺失的 5 个尾参数无法补齐。

    .. note::
       枚举值来源 ``C:\\swapi\\enums\\swDetViewStyle_e.md``（5 项）与
       ``C:\\swapi\\enums\\swDetCircleShowType_e.md``（3 项），
       本模块顶部 ``swDetViewStyle_e`` / ``swDetCircleShowType_e`` 字典由此生成。
    """
    return drawing_model.CreateDetailViewAt4(
        float(x),
        float(y),
        0.0,
        int(style),
        float(scale),
        1.0,
        str(label),
        int(show_type),
        bool(full_outline),
        bool(jagged_outline),
        bool(no_outline),
        int(shape_intensity),
    )


def insert_dimensions(drawing_model, view=None):
    """
    自动标注尺寸（模型项目）

    参数:
        view: 目标视图对象，None 则标注所有视图
    """
    # SolidWorks 2024 新增 InsertModelAnnotations4，返回实际插入的 IAnnotation
    # 数组；旧版/动态代理仍可能只有 InsertModelAnnotations3。优先使用 4，
    # 再回退到 3，避免把“方法返回 True”误当成已经插入尺寸。
    # SW2024 swInsertAnnotation_e：32768=标记为工程图的模型尺寸。
    # 8 是通用尺寸类型、524288 是未标记尺寸；本机 SW2024 对二者组合静默
    # 返回 None，而 32768 会返回真实 IAnnotation 数组。
    args4 = (
        0,          # swImportModelItemsFromEntireModel
        32768,      # swInsertDimensionsMarkedForDrawing
        True, False, False, False,
        False, False,
    )
    args3 = args4[:6]
    # 官方 API 示例要求先激活一个工程图视图；未激活时 SW2024 会静默返回空结果。
    try:
        sheet = _safe_member(drawing_model, "GetCurrentSheet")
        views = _as_sequence(_safe_member(sheet, "GetViews", default=[]))
        if views:
            # 三视图第一个通常是前视图；通过对象 Name 读取失败时使用已知顺序，
            # 但仍要求 SelectByID2/ActivateView 真正返回成功。
            first_view = views[0]
            name = _safe_member(first_view, "Name", default="")
            if name:
                extension = getattr(drawing_model, "Extension", None)
                if extension is not None:
                    get_com_member(
                        extension, "SelectByID2",
                        name, "DRAWINGVIEW", 0, 0, 0, False, 0,
                        create_empty_dispatch_variant(), 0,
                    )
                get_com_member(drawing_model, "ActivateView", name)
    except Exception:
        # 激活失败仍继续尝试，让结构复核决定是否有真实尺寸证据。
        pass
    owners = (drawing_model, getattr(drawing_model, "Extension", None))
    for owner in owners:
        if owner is None:
            continue
        try:
            method4 = getattr(owner, "InsertModelAnnotations4", None)
            if method4 is not None:
                inserted = get_com_member(owner, "InsertModelAnnotations4", *args4)
                if inserted is not None:
                    return inserted
            method3 = getattr(owner, "InsertModelAnnotations3", None)
            if method3 is not None:
                return get_com_member(owner, "InsertModelAnnotations3", *args3)
        except (AttributeError, TypeError, pythoncom.com_error):
            continue
    # 新建三视图后 SW2024 有时尚未建立可导入的视图缓存；强制重建后仅重试
    # 一次。使用“标记为工程图”与消重语义，不会靠重复调用制造重复尺寸。
    try:
        get_com_member(drawing_model, "ForceRebuild3", False)
        get_com_member(drawing_model, "GraphicsRedraw2")
        for owner in owners:
            if owner is not None and getattr(owner, "InsertModelAnnotations4", None) is not None:
                inserted = get_com_member(owner, "InsertModelAnnotations4", *args4)
                if inserted is not None:
                    return inserted
    except (AttributeError, TypeError, pythoncom.com_error):
        pass
    # 调用方可以继续做结构复核，但必须把缺少真实尺寸证据显示为 warning。
    return False


def _note_text(note):
    """@brief 读取 INote 的实际文字，兼容动态 COM 未公开成员名称的情况。"""
    text = _safe_member(note, "GetText")
    if isinstance(text, str):
        return text
    ole_object = getattr(note, "_oleobj_", None)
    if ole_object is None:
        return ""
    try:
        # SW2026 sldworks.tlb: INote.GetText 的 DISPID 为 2，返回 BSTR。
        return str(ole_object.InvokeTypes(2, 0, 1, (8, 0), ()) or "")
    except Exception:
        return ""


def _note_annotation(note):
    """@brief 获取 INote 对应的 IAnnotation；动态 COM 不公开该成员时按类型库调用。"""
    annotation = _safe_member(note, "GetAnnotation")
    if annotation is not None:
        return annotation
    ole_object = getattr(note, "_oleobj_", None)
    if ole_object is None:
        return None
    try:
        # SW2026 sldworks.tlb: INote.GetAnnotation 的 DISPID 为 85。
        from win32com.client.dynamic import Dispatch

        return Dispatch(ole_object.InvokeTypes(85, 0, 1, (9, 0), ()))
    except Exception:
        return None


def _set_annotation_position(annotation, x, y, z=0.0):
    """@brief 设置 IAnnotation 的图纸坐标，返回 SolidWorks 的布尔结果。"""
    try:
        result = get_com_member(annotation, "SetPosition2", x, y, z)
        if isinstance(result, bool):
            return result
    except Exception:
        pass
    ole_object = getattr(annotation, "_oleobj_", None)
    if ole_object is None:
        return False
    try:
        # SW2026 sldworks.tlb: IAnnotation.SetPosition2 的 DISPID 为 91。
        return bool(ole_object.InvokeTypes(91, 0, 1, (11, 0), ((5, 1), (5, 1), (5, 1)), x, y, z))
    except Exception:
        return False


def _annotation_position(annotation):
    """@brief 回读 IAnnotation 图纸坐标，坐标不可用时返回 None。"""
    position = _safe_member(annotation, "GetPosition")
    values = _as_sequence(position)
    try:
        x, y = float(values[0]), float(values[1])
    except (IndexError, TypeError, ValueError):
        return None
    if not math.isfinite(x) or not math.isfinite(y):
        return None
    return [x, y, float(values[2]) if len(values) > 2 else 0.0]


def _note_box(note, annotation):
    """@brief 优先读取 INote 的图纸空间范围；没有时退回通用注释边界。"""
    extent = _safe_member(note, "GetExtent")
    if extent is None:
        ole_object = getattr(note, "_oleobj_", None)
        if ole_object is not None:
            try:
                # SW2026 sldworks.tlb: INote.GetExtent 的 DISPID 为 22。
                extent = ole_object.InvokeTypes(22, 0, 1, (12, 0), ())
            except Exception:
                extent = None
    return _normalise_box(extent) or _annotation_box(annotation)


def _note_evidence(note):
    """@brief 收集注释的文字、位置和边界，作为工程图结构证据。"""
    annotation = _note_annotation(note)
    return {
        "text": _note_text(note),
        "position_m": _annotation_position(annotation),
        "box": _note_box(note, annotation),
    }


def add_note(drawing_model, x, y, text):
    """@brief 创建并验证工程图文字注释。

    @param drawing_model SolidWorks IModelDoc2 工程图对象。
    @param x 注释锚点 X 坐标（米）。
    @param y 注释锚点 Y 坐标（米）。
    @param text 需要写入图纸的非空文字。
    @return 包含 COM 回读文字、坐标和边界的可审计结果。
    """
    expected_text = str(text)
    if not expected_text.strip() or not all(math.isfinite(float(value)) for value in (x, y)):
        return {
            "text": expected_text,
            "created": False,
            "status": "failed",
            "error_code": "DRAWING_NOTE_INPUT_INVALID",
        }
    note = _safe_member(drawing_model, "InsertNote", expected_text)
    if note is None:
        return {
            "text": expected_text,
            "created": False,
            "status": "failed",
            "error_code": "DRAWING_NOTE_INSERT_FAILED",
        }
    annotation = _note_annotation(note)
    positioned = _set_annotation_position(annotation, float(x), float(y)) if annotation is not None else False
    if positioned:
        # 刷新文字与坐标；边界仍必须在视图重枚举后的结构审查阶段读取。
        _safe_member(drawing_model, "ForceRebuild3", False)
    evidence = _note_evidence(note)
    position = evidence.get("position_m") or []
    text_matches = evidence.get("text") == expected_text
    position_matches = (
        len(position) >= 2
        and math.isclose(position[0], float(x), abs_tol=1e-6)
        and math.isclose(position[1], float(y), abs_tol=1e-6)
    )
    verified = bool(positioned and text_matches and position_matches)
    return {
        "text": expected_text,
        "created": True,
        "position_requested_m": [float(x), float(y), 0.0],
        "positioned": positioned,
        "text_evidence": evidence.get("text"),
        "position_evidence_m": position,
        "box": None,
        "box_source": "deferred_to_structure_inspection",
        "verified": verified,
        "status": "pass" if verified else "failed",
        "error_code": None if verified else "DRAWING_NOTE_COM_EVIDENCE_MISSING",
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IModelDocExtension\InsertBomTable4.md
# 定位:   BOM 表插入入口。定位过程（铁律 4「查不到就说查不到」的实际应用）：
#           1) sw_know.py member IDrawingDoc InsertBomTable4
#              → [SWK_NOT_FOUND]，按铁律 5 判定「IDrawingDoc 上无此成员」
#           2) sw_know.py suggest InsertBomTable4
#              → IBomTable / IBomTableSortData / IHoleTable / IBendTable，均非同类，排除
#           3) sw_know.py find InsertBomTable
#              → 命中 IModelDocExtension/InsertBomTable{,2,3,4} 与
#                IView/InsertBomTable{,2,3,4,5,6}
#           4) 官方 IModelDocExtension.InsertBomTable4 共 9 个参数：
#              (String TemplateName, Int X, Int Y, Int BomType,
#               String ConfigurationName, Boolean Hidden, Int IndentedNumberingType,
#               Boolean DetailedCutList, Boolean DissolvePartLevelRows)
#              其前 5 项与原实参逐一对应，据此确认作者本意即此版本。
# 本次改动: 原实现 drawing_model.InsertBomTable4(tpl, x, y, bom, cfg, "", False)
#           —— 对象错（挂在 IDrawingDoc 上）+ 实参 7 个 vs 官方 9 个，
#              且第 6 个实参 "" 会落到 Boolean Hidden 位、
#              第 7 个 False 会落到 Int IndentedNumberingType 位。
#           现改走 model.Extension.InsertBomTable4 并补齐 9 参。
# 未采用的替代入口: IView.InsertBomTable4（10 参，官方标注 Obsolete，
#           被 InsertBomTable5/6 取代）、IView.InsertBomTable6（12 参，当代）。
#           选 IModelDocExtension 版是因其与既有调用形态最贴近、补齐成本最低；
#           若需非废弃入口，应改走 view.InsertBomTable6 并同步调整参数。
# 枚举来源: BOM_TYPES（见本文件上方来源块）
# 查证:   python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" \
#           member IModelDocExtension InsertBomTable4
# ⚠ 本函数为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 官方文档未注明 X/Y 的单位（签名为 System.int，无单位说明）——按铁律 5
#   记「查不到」，故此处原样 int() 交由调用方标定，不做单位换算。
# ⚠ 官方 Remarks 原文：空 ConfigurationName 不会回落到 Default，必须显式指定；
#   故默认值由 "" 改为 "Default"。
# ────────────────────────────────────────────────────────────────────
def insert_bom_table(
    drawing_model,
    template_path,
    x,
    y,
    bom_type=BOM_TYPES["top_level_only"],
    config_name="Default",
    *,
    hidden=False,
    indented_numbering_type=0,
    detailed_cut_list=False,
    dissolve_part_level_rows=False,
):
    """在工程图中插入 BOM 表

    参数:
        template_path: BOM 模板路径（``.sldbomtbt``）
        x, y: 表格放置位置。**官方签名为 ``System.int``（整数）**，
            官方文档未注明单位 —— 查不到，故此处原样转 ``int`` 交由调用方决定标定，
            不做单位换算（见下方说明）。
        bom_type: ``BOM_TYPES`` 之一。
            ⚠ 官方 ``swBomType_e`` 取值为 **1=仅零件 / 2=仅顶层 / 3=缩进 / 4=扁平化**。
        config_name: 配置名称。**必须显式给出**（见下方 Remarks）。

    :raises AttributeError: 若文档对象取不到 ``Extension``。

    .. note::
       **签名依据（本函数为静态签名比对后修正，未在本机实测，见 AGENTS.md 铁律 2）**

       官方成员 ``InsertBomTable4`` **不在 ``IDrawingDoc`` 上**——
       ``sw_know.py member IDrawingDoc InsertBomTable4`` 返回 ``[SWK_NOT_FOUND]``，
       按铁律 5 判定「官方 API 无此成员」。全库检索定位到它只存在于
       ``IView`` 与 ``IModelDocExtension`` 两处。

       本函数改走 ``IModelDocExtension.InsertBomTable4``（9 个参数），因其参数表
       前 5 项与调用方既有实参一一对应：
       ``(String TemplateName, Int X, Int Y, Int BomType, String ConfigurationName,
       Boolean Hidden, Int IndentedNumberingType, Boolean DetailedCutList,
       Boolean DissolvePartLevelRows)``
       依据 ``C:\\swapi\\types\\IModelDocExtension\\InsertBomTable4.md``。

       ⚠ 修正前此处为 ``drawing_model.InsertBomTable4(template_path, x, y,
       bom_type, config_name, "", False)``：对象错（挂在 IDrawingDoc 上）+
       实参 7 个 vs 官方 9 个，且第 6 个实参 ``""`` 会被送到 ``Boolean Hidden``
       位置、第 7 个 ``False`` 会被送到 ``Int IndentedNumberingType`` 位置。

       未采用的替代入口：``IView.InsertBomTable4``（10 参，官方标注
       **Obsolete，被 InsertBomTable5/6 取代**）与 ``IView.InsertBomTable6``
       （12 参，当代）。选 ``IModelDocExtension`` 是因为它与既有调用形态最贴近、
       补齐成本最低；如需非废弃入口，应改走 ``view.InsertBomTable6``。

    .. note::
       官方 Remarks 原文警告：*"The system does not default to the Default
       configuration when you specify an empty string for Configuration.
       You must specify the configuration."* —— 即 ``config_name=""``
       **不会**回落到 Default，零件级/缩进式 BOM 会直接建不出来。
       故本函数默认值由 ``""`` 改为 ``"Default"``。
    """
    extension = _safe_member(drawing_model, "Extension")
    if extension is None:
        raise AttributeError("文档对象取不到 Extension，插入 BOM 表失败")
    return extension.InsertBomTable4(
        str(template_path),
        int(x),
        int(y),
        int(bom_type),
        str(config_name),
        bool(hidden),
        int(indented_numbering_type),
        bool(detailed_cut_list),
        bool(dissolve_part_level_rows),
    )


def set_sheet_format(drawing_model, format_path):
    """
    设置图纸格式（图框）

    参数:
        format_path: 图纸格式文件路径（.slddrt）
    """
    sheet = drawing_model.GetCurrentSheet()
    return sheet.SetTemplateName(format_path)


def add_sheet(drawing_model, paper_size=7, template_path="", first_angle=True):
    """
    添加新图纸

    参数:
        paper_size: 纸张大小
            0=A, 1=B, 2=C, 3=D, 4=E,
            5=A4, 6=A3, 7=A2, 8=A1, 9=A0
        template_path: 图纸格式模板路径
    """
    return drawing_model.NewSheet4(
        "", paper_size, 12, 1.0, 1.0, bool(first_angle), template_path, 0, 0, "", 0, 0, 0, 0, 0, 0
    )


def add_a3_sheet(drawing_model, template_candidates, *, require_gbt=True, projection="first_angle") -> dict:
    """@brief 选择本机 A3 图框并创建横向 A3 工程图页。"""
    selection = select_drawing_template(template_candidates, paper_size="A3", require_gbt=require_gbt)
    if selection["selected"] is None:
        return {
            **selection,
            "stage": "preflight",
            "retryable": True,
            "created": False,
        }
    created = bool(add_sheet(
        drawing_model,
        paper_size=PAPER_SIZES["A3"]["code"],
        template_path=selection["selected"],
        first_angle=str(projection).lower() == "first_angle",
    ))
    return {
        **selection,
        "status": "pass" if created else "failed",
        "stage": "create",
        "retryable": not created,
        "created": created,
        "projection": str(projection).lower(),
        "error_code": None if created else "DRAWING_A3_SHEET_CREATE_FAILED",
    }


def setup_current_sheet_as_a3(drawing_model, template_candidates, *, require_gbt=True, projection="first_angle") -> dict:
    """@brief 使用 IDrawingDoc.SetupSheet6 将当前页设置为横向 A3。"""
    selection = select_drawing_template(template_candidates, paper_size="A3", require_gbt=require_gbt)
    if selection["selected"] is None:
        return {
            **selection,
            "stage": "preflight",
            "retryable": True,
            "configured": False,
        }
    sheet = _safe_member(drawing_model, "GetCurrentSheet")
    sheet_name = str(_safe_member(sheet, "GetName", default="") or "")
    if not sheet_name:
        return {
            **selection,
            "status": "blocked",
            "stage": "preflight",
            "retryable": True,
            "configured": False,
            "error_code": "DRAWING_CURRENT_SHEET_MISSING",
        }
    projection = str(projection).lower()
    if projection not in {"first_angle", "third_angle"}:
        raise ValueError("projection 必须是 first_angle 或 third_angle")
    try:
        configured = bool(get_com_member(
            drawing_model,
            "SetupSheet6",
            sheet_name,
            PAPER_SIZES["A3"]["code"],
            12,
            1.0,
            1.0,
            projection == "first_angle",
            selection["selected"],
            0.0,
            0.0,
            "",
            False,
            0.0,
            0.0,
            0.0,
            0.0,
            0,
            0,
        ))
    except Exception as exc:
        return {
            **selection,
            "status": "failed",
            "stage": "create",
            "retryable": True,
            "configured": False,
            "error_code": "DRAWING_A3_SETUP_FAILED",
            "error": str(exc),
        }
    return {
        **selection,
        "status": "pass" if configured else "failed",
        "stage": "create",
        "retryable": not configured,
        "configured": configured,
        "sheet_name": sheet_name,
        "projection": projection,
        "error_code": None if configured else "DRAWING_A3_SETUP_FAILED",
    }


def get_all_views(drawing_model):
    """获取当前图纸上的所有视图"""
    sheet = get_com_member(drawing_model, "GetCurrentSheet")
    views = get_com_member(sheet, "GetViews")
    result = []
    if views:
        for view in views:
            result.append({
                "name": view.Name,
                "type": view.Type,
                "scale": view.ScaleRatio,
            })
    return result


def _paper_size_from_template(template_path):
    """@brief 从模板文件名推断标准图幅；无法判断时返回 None。"""
    name = Path(str(template_path or "")).stem.upper()
    for paper_size in PAPER_SIZES:
        if re.search(rf"(?:^|[^A-Z0-9]){paper_size}(?:[^A-Z0-9]|$)", name):
            return paper_size
    return None


TABLE_ANNOTATION_KINDS = {
    0: "general",
    1: "hole_chart",
    2: "bom",
    3: "revision",
    4: "weldment_cut_list",
    5: "title_block",
    6: "general_tolerance",
}


def _table_cell_text(table, row, column):
    """@brief 按新版优先、旧版回退的顺序读取表格显示文字。"""
    for member, args in (
        ("DisplayedText2", (row, column, False)),
        ("DisplayedText", (row, column)),
        ("Text2", (row, column, False)),
        ("Text", (row, column)),
    ):
        value = _safe_member(table, member, *args, default=None)
        if value is not None:
            return str(value)
    return ""


def _table_evidence(table, sheet_name):
    """@brief 回读表格类型、数据行、单元格及 BOM 配置证据。"""
    table_type = _safe_member(table, "Type", default=None)
    try:
        normalized_type = int(table_type)
    except (TypeError, ValueError):
        normalized_type = table_type
    try:
        row_count = int(_safe_member(table, "RowCount", default=0) or 0)
        column_count = int(_safe_member(table, "ColumnCount", default=0) or 0)
    except (TypeError, ValueError):
        row_count, column_count = 0, 0
    cells = []
    if 0 < row_count <= 500 and 0 < column_count <= 100 and row_count * column_count <= 5000:
        cells = [
            [_table_cell_text(table, row, column) for column in range(column_count)]
            for row in range(row_count)
        ]
    configuration = ""
    if normalized_type == 2:
        bom_feature = _safe_member(table, "BomFeature", default=None)
        configuration = str(_safe_member(bom_feature, "Configuration", default="") or "")
    return {
        "sheet": str(sheet_name),
        "type": normalized_type,
        "kind": TABLE_ANNOTATION_KINDS.get(normalized_type, "unknown"),
        "title": str(_safe_member(table, "Title", default="") or ""),
        "row_count": row_count,
        "column_count": column_count,
        "configuration": configuration,
        "cells": cells,
        "box": _annotation_box(table),
    }


def _annotation_text_parts(annotation_owner):
    """@brief 回读专业标注的可见文字片段，保留原始顺序。"""
    try:
        count = int(_safe_member(annotation_owner, "GetTextCount", default=0) or 0)
    except (TypeError, ValueError):
        count = 0
    if not 0 <= count <= 1000:
        count = 0
    parts = []
    for index in range(count):
        text = str(_safe_member(annotation_owner, "GetTextAtIndex", index, default="") or "")
        if text:
            parts.append(text)
    return parts


def _professional_annotation_record(owner, kind, view_record):
    """@brief 构造带所属视图、文字和边界的专业标注证据。"""
    return {
        "kind": kind,
        "sheet": view_record["sheet"],
        "view": view_record["name"],
        "semantic_view": view_record.get("semantic_view") or "",
        "text_parts": _annotation_text_parts(owner),
        "box": _annotation_box(owner),
    }


def _view_center_marks(view):
    """@brief 遍历视图中心标记，并兼容 SW2025 SP1 之前的回读接口。"""
    current = _safe_member(view, "GetFirstCenterMark2")
    if current is None:
        current = _safe_member(view, "GetFirstCenterMark")
    marks = []
    seen = set()
    while current is not None and len(marks) < 10000:
        identity = id(current)
        if identity in seen:
            break
        seen.add(identity)
        marks.append(current)
        current = _safe_member(current, "GetNext")
    if marks:
        return marks
    # GetCenterMarks 不能返回注解型中心标记，仅作为旧版本兼容回退。
    return _as_sequence(_safe_member(view, "GetCenterMarks", default=[]))


def _collect_view_professional_annotations(view, view_record):
    """@brief 使用 SW2026 Interop 已反射确认的 IView 回读接口收集专业标注。"""
    result = {
        "center_marks": [],
        "center_lines": [],
        "datum_tags": [],
        "geometric_tolerances": [],
        "surface_finish_symbols": [],
        "weld_symbols": [],
    }
    for owner in _view_center_marks(view):
        record = _professional_annotation_record(owner, "center_mark", view_record)
        record.update({
            "size_m": _safe_member(owner, "Size", default=None),
            "show_lines": _safe_member(owner, "ShowLines", default=None),
            "style": _safe_member(owner, "Style", default=None),
        })
        result["center_marks"].append(record)
    for owner in _as_sequence(_safe_member(view, "GetCenterLines", default=[])):
        result["center_lines"].append(_professional_annotation_record(owner, "center_line", view_record))
    for owner in _as_sequence(_safe_member(view, "GetDatumTags", default=[])):
        record = _professional_annotation_record(owner, "datum", view_record)
        record["label"] = str(_safe_member(owner, "GetLabel", default="") or "")
        result["datum_tags"].append(record)
    for owner in _as_sequence(_safe_member(view, "GetGTols", default=[])):
        record = _professional_annotation_record(owner, "geometric_tolerance", view_record)
        try:
            frame_count = int(_safe_member(owner, "GetFrameCount", default=0) or 0)
        except (TypeError, ValueError):
            frame_count = 0
        frame_count = frame_count if 0 <= frame_count <= 100 else 0
        record["datum_identifier"] = str(_safe_member(owner, "GetDatumIdentifier", default="") or "")
        record["frames"] = [
            {
                "index": index,
                "symbols": _as_sequence(_safe_member(owner, "GetFrameSymbols3", index, default=[])),
                "values": _as_sequence(_safe_member(owner, "GetFrameValues", index, default=[])),
            }
            for index in range(frame_count)
        ]
        result["geometric_tolerances"].append(record)
    for owner in _as_sequence(_safe_member(view, "GetSFSymbols", default=[])):
        record = _professional_annotation_record(owner, "surface_finish", view_record)
        record.update({
            "symbol_type": _safe_member(owner, "GetSymbolType", default=None),
            "symbol": _safe_member(owner, "GetSymbol", default=None),
            "direction_of_lay": _safe_member(owner, "GetDirectionOfLay", default=None),
        })
        result["surface_finish_symbols"].append(record)
    for owner in _as_sequence(_safe_member(view, "GetWeldSymbols", default=[])):
        result["weld_symbols"].append(_professional_annotation_record(owner, "weld_symbol", view_record))
    return result


def inspect_drawing_structure(drawing_model, *, paper_size_hint=None, title_block_box=None) -> dict:
    """@brief 读取工程图结构并返回可审计报告，不修改文档。"""
    sheets = _as_sequence(_safe_member(drawing_model, "GetSheetNames", default=[]))
    if not sheets:
        current_sheet = _safe_member(drawing_model, "GetCurrentSheet")
        current_name = _safe_member(current_sheet, "GetName", default="")
        if current_name:
            sheets = [current_name]
    views = []
    dimensions = []
    notes = []
    tables = []
    professional_annotations = {
        "center_marks": [],
        "center_lines": [],
        "hole_callouts": [],
        "datum_tags": [],
        "geometric_tolerances": [],
        "surface_finish_symbols": [],
        "weld_symbols": [],
    }
    for sheet_name in sheets or [""]:
        # ── 来源 ────────────────────────────────────────────────────────
        # 仓库:   同上（IDrawingDoc 参数化属性 Sheet，官方签名 Sheet get_Sheet(String)）
        # 定位:   按图纸名取页。完整推导与「原写法为何是静默无效果」见本文件
        #         中第一处同名修改上方的来源块，此处不重复。
        # ⚠ 本行为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
        # ────────────────────────────────────────────────────────────────
        sheet = _safe_member(drawing_model, "Sheet", sheet_name) or _safe_member(drawing_model, "GetCurrentSheet")
        sheet_views = _as_sequence(_safe_member(sheet, "GetViews", default=[]))
        mapped_views, _, _ = _map_standard_views_from_sheet_views(sheet_views)
        semantic_by_object = {id(view): name for name, view in mapped_views.items()}
        for view in sheet_views:
            view_record = {
                "sheet": str(sheet_name),
                "name": _safe_member(view, "Name", default=""),
                "type": _safe_member(view, "Type", default=None),
                "orientation": _safe_member(view, "GetOrientationName", default=""),
                "semantic_view": semantic_by_object.get(id(view), ""),
                "scale": _safe_member(view, "ScaleRatio", default=None),
                "box": _normalise_box(_safe_member(view, "GetOutline")),
            }
            views.append(view_record)
            view_annotations = _collect_view_professional_annotations(view, view_record)
            for key, records in view_annotations.items():
                professional_annotations[key].extend(records)
            view_dimensions = _view_display_dimensions(view)
            for dimension in view_dimensions:
                native_box = _annotation_box(dimension)
                estimated_box_evidence = estimate_dimension_text_box(dimension) if native_box is None else None
                dimension_record = {
                    "sheet": str(sheet_name),
                    "view": _safe_member(view, "Name", default=""),
                    "semantic_view": view_record["semantic_view"],
                    "name": (
                        _safe_member(dimension, "Name", default="")
                        or _safe_member(dimension, "GetNameForSelection", default="")
                        or _safe_member(_safe_member(dimension, "GetDimension"), "FullName", default="")
                    ),
                    "type": _safe_member(dimension, "Type", default=None),
                    "text": _safe_member(dimension, "GetText", 0, default=""),
                    "box": native_box or estimated_box_evidence.get("box"),
                    "box_source": "native" if native_box else estimated_box_evidence.get("source"),
                    "box_confidence": "high" if native_box else estimated_box_evidence.get("confidence"),
                    "box_evidence": {
                        "box": native_box,
                        "source": "native",
                        "confidence": "high",
                        "method": "annotation_get_box",
                    } if native_box else estimated_box_evidence,
                    "is_hole_callout": bool(_safe_member(dimension, "IsHoleCallout", default=False)),
                    "hole_callout_variables": _as_sequence(_safe_member(dimension, "GetHoleCalloutVariables", default=[])),
                }
                dimensions.append(dimension_record)
                if dimension_record["is_hole_callout"]:
                    professional_annotations["hole_callouts"].append({
                        "kind": "hole_callout",
                        "sheet": dimension_record["sheet"],
                        "view": dimension_record["view"],
                        "semantic_view": dimension_record["semantic_view"],
                        "name": dimension_record["name"],
                        "text_parts": [dimension_record["text"]] if dimension_record["text"] else [],
                        "variables": dimension_record["hole_callout_variables"],
                        "box": dimension_record["box"],
                    })
            for note in _as_sequence(_safe_member(view, "GetNotes", default=[])):
                note_evidence = _note_evidence(note)
                note_text = str(note_evidence.get("text") or "").strip()
                owner_view_type = view_record["type"]
                notes.append({
                    "sheet": str(sheet_name),
                    "owner_view": view_record["name"],
                    "owner_view_type": owner_view_type,
                    # ★ 2026-10-03：原为魔数 `in {2, 3}`，改引单一真源 `scripts/sw_drawing_view_types.py`
                    #   （官方 `swDrawingViewTypes_e`：2 = swDrawingSectionView · 3 = swDrawingDetailView
                    #    ⇒ **带标签的视图**）。⇒ 同一份知识不再两个家（另一处是 scripts/sw_review.py）。
                    "note_kind": "view_label" if owner_view_type in LABELLED_VIEW_TYPES and not note_text else "note",
                    **note_evidence,
                })
            for table in _as_sequence(_safe_member(view, "GetTableAnnotations", default=[])):
                tables.append(_table_evidence(table, sheet_name))
    current_sheet = _safe_member(drawing_model, "GetCurrentSheet")
    template = _safe_member(current_sheet, "GetTemplateName", default="")
    paper_size = str(paper_size_hint or _paper_size_from_template(template) or "").upper() or None
    spec = PAPER_SIZES.get(paper_size)
    inferred_title_box = title_block_box
    if inferred_title_box is None and spec is not None:
        inferred_title_box = {
            "left": spec["width_m"] - 0.012 - 0.180,
            "bottom": 0.012,
            "right": spec["width_m"] - 0.012,
            "top": 0.067,
        }
    compact_template_name = re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", Path(str(template or "")).stem.casefold())
    template_name = Path(str(template or "")).stem.casefold()
    gbt_candidate = (
        "gbt" in compact_template_name
        or "国标" in compact_template_name
        or bool(re.search(r"(?:^|[^a-z0-9])gb(?:t)?(?:[^a-z0-9]|$)", template_name, re.IGNORECASE))
    )
    outline_count = sum(item.get("box") is not None for item in views)
    dimension_box_count = sum(item.get("box") is not None for item in dimensions)
    native_dimension_box_count = sum(item.get("box_source") == "native" for item in dimensions)
    estimated_dimension_box_count = sum(item.get("box_source") == "estimated" and item.get("box") is not None for item in dimensions)
    low_confidence_dimension_box_count = sum(item.get("box_confidence") in {"low", "unavailable"} for item in dimensions)
    result = {
        "status": "pass" if views else "blocked",
        "stage": "review",
        "sheets": [str(item) for item in sheets],
        "views": views,
        "dimensions": dimensions,
        "notes": notes,
        "tables": tables,
        "professional_annotations": professional_annotations,
        "template_path": str(template or ""),
        "paper_size": paper_size,
        "sheet_size": {"width_m": spec["width_m"], "height_m": spec["height_m"]} if spec else None,
        "title_block": {
            "candidate": bool(template),
            "gbt_candidate": gbt_candidate,
            "content_verified": any(item.get("kind") == "title_block" and item.get("row_count", 0) > 0 for item in tables),
            "fields": {},
            "box": _normalise_box(title_block_box) if title_block_box is not None else inferred_title_box,
        },
        "view_count": len(views),
        "dimension_count": len(dimensions),
        "table_count": len(tables),
        "view_outline_count": outline_count,
        "dimension_box_count": dimension_box_count,
        "native_dimension_box_count": native_dimension_box_count,
        "estimated_dimension_box_count": estimated_dimension_box_count,
        "low_confidence_dimension_box_count": low_confidence_dimension_box_count,
        "manual_review_required": True,
        "retryable": not bool(views),
        "error_code": None if views else "DRAWING_VIEWS_MISSING",
        "checks": [
            {"id": "drawing-views", "status": "pass" if views else "fail", "message": "工程图包含视图" if views else "未读取到工程图视图"},
            {"id": "drawing-template", "status": "pass" if template else "warning", "message": "已读取图框模板" if template else "图框模板需要人工确认"},
            {"id": "drawing-a3-sheet", "status": "pass" if paper_size == "A3" else "warning", "message": "当前图幅识别为 A3" if paper_size == "A3" else "当前图幅不是 A3 或无法识别"},
            {"id": "drawing-gbt-template", "status": "pass" if gbt_candidate else "warning", "message": "模板名称是 GB/T 候选，内容仍需目视复核" if gbt_candidate else "未发现 GB/T 图框候选证据"},
            {"id": "drawing-dimensions", "status": "pass" if dimensions else "warning", "message": "已读取真实尺寸实体" if dimensions else "未读取到尺寸实体"},
            {"id": "drawing-view-outlines", "status": "pass" if views and outline_count == len(views) else "warning", "message": "已读取全部视图边界" if views and outline_count == len(views) else "部分视图缺少边界，无法完整检查碰撞"},
            {
                "id": "drawing-dimension-boxes",
                "status": "pass" if dimensions and native_dimension_box_count == len(dimensions) else "warning",
                "message": (
                    "已读取全部尺寸文字原生边界"
                    if dimensions and native_dimension_box_count == len(dimensions)
                    else f"原生边界 {native_dimension_box_count}/{len(dimensions)}，保守估算 {estimated_dimension_box_count}/{len(dimensions)}；估算不等于原生证据"
                ),
            },
        ],
    }
    return result


def auto_insert_center_marks(drawing_model, requirements) -> dict:
    """@brief 按视图自动插入中心标记，并以实体数量回读作为成功依据。"""
    requested = list(requirements or [])
    if not requested:
        return {
            "status": "not_requested",
            "requested": False,
            "requirements": [],
            "manual_review_required": False,
            "error_code": None,
        }

    sheet = _safe_member(drawing_model, "GetCurrentSheet")
    sheet_views = _as_sequence(_safe_member(sheet, "GetViews", default=[]))
    mapped_views, diagnostics, mapping_method = _map_standard_views_from_sheet_views(sheet_views)
    drawing_path = str(_safe_member(drawing_model, "GetPathName", default="") or "")
    results = []
    for requirement in requested:
        requirement_id = str(requirement.get("id") or "")
        orientation = _normalise_orientation(requirement.get("view"))
        expected_count = int(requirement.get("count") or 0)
        targets = list(requirement.get("targets") or [])
        insert_type = 0
        for target in targets:
            insert_type |= AUTO_CENTER_MARK_TARGETS.get(str(target), 0)
        view = mapped_views.get(orientation)
        if view is None or not orientation or insert_type == 0 or expected_count <= 0:
            results.append({
                "id": requirement_id,
                "status": "failed",
                "view": orientation or str(requirement.get("view") or ""),
                "targets": targets,
                "expected_count": expected_count,
                "before_count": 0,
                "after_count": 0,
                "created_count": 0,
                "api_returned": None,
                "error_code": "DRAWING_CENTER_MARK_REQUIREMENT_UNRESOLVED",
            })
            continue

        before_count = len(_view_center_marks(view))
        api_returned = None
        error = None
        if before_count < expected_count:
            view_name = str(_safe_member(view, "Name", default="") or "")
            if view_name:
                _safe_member(drawing_model, "ActivateView", view_name)
            try:
                api_returned = bool(get_com_member(
                    view,
                    "AutoInsertCenterMarks2",
                    insert_type,
                    0,      # swCenterMarkConnectionLine_None
                    True,   # 线性槽使用槽中心
                    True,   # 圆弧槽使用槽中心
                    True,   # 使用文档默认尺寸与间隙
                    0.0,
                    0.0,
                    False,
                    True,
                    0.0,
                ))
            except Exception as exc:
                error = str(exc)
            _safe_member(drawing_model, "ForceRebuild3", False)
            _safe_member(drawing_model, "GraphicsRedraw2")
        after_count = len(_view_center_marks(view))
        passed = after_count >= expected_count
        failure_code = None
        if not passed:
            failure_code = (
                "DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED"
                if api_returned is True and not drawing_path
                else "DRAWING_CENTER_MARK_INSERT_OR_READBACK_FAILED"
            )
        results.append({
            "id": requirement_id,
            "status": "pass" if passed else "failed",
            "view": orientation,
            "actual_view": str(_safe_member(view, "Name", default="") or ""),
            "targets": targets,
            "insert_type": insert_type,
            "expected_count": expected_count,
            "before_count": before_count,
            "after_count": after_count,
            "created_count": max(0, after_count - before_count),
            "api_returned": api_returned,
            "error": error,
            "error_code": failure_code,
        })

    failed = [item for item in results if item["status"] != "pass"]
    aggregate_error = None
    if failed:
        aggregate_error = (
            "DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED"
            if all(item.get("error_code") == "DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED" for item in failed)
            else "DRAWING_CENTER_MARK_INSERT_OR_READBACK_FAILED"
        )
    return {
        "status": "failed" if failed else "pass",
        "requested": True,
        "requirements": results,
        "mapping_method": mapping_method,
        "mapping_diagnostics": diagnostics,
        "drawing_path": drawing_path,
        "manual_review_required": True,
        "retryable": aggregate_error == "DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED",
        "error_code": aggregate_error,
    }


def export_sheet_to_pdf(model, output_path, sheet_names=None, sw_app=None):
    """
    将工程图导出为 PDF

    参数:
        model: IModelDoc2（工程图文档）
        output_path: 输出 PDF 路径
        sheet_names: 图纸名称列表，None=所有图纸
        sw_app: 可选的 SldWorks.Application 对象；传入会话对象可避免 SW2024
            动态 IModelDoc2 未暴露 GetSldWorksObject 的兼容性问题。
    """
    sw = sw_app
    if sw is None:
        for prog_id in ("SldWorks.Application.32", "SldWorks.Application"):
            try:
                sw = _win32com.GetActiveObject(prog_id)
                break
            except Exception:
                continue
    if sw is None:
        return False
    try:
        pdf_data = get_com_member(sw, "GetExportFileData", 1)  # 1 = swExportPDFData
    except Exception:
        return False

    if sheet_names is None:
        drawing = model
        sheet_names = get_com_member(drawing, "GetSheetNames")

    try:
        pdf_data.SetSheets(0, sheet_names)  # 0 = swExportData_ExportSpecifiedSheets
    except Exception:
        return False

    errors = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    success = model.Extension.SaveAs(output_path, 0, 1, pdf_data, errors, warnings)

    if success:
        print(f"PDF 导出成功: {output_path}")
    else:
        print(f"PDF 导出失败, 错误码: {errors.value}")
    return success


def setup_current_sheet(drawing_model, template_candidates, *, paper_size="A3", projection="first_angle", require_gbt=True) -> dict:
    """@brief 按 DrawingSpec 配置当前图纸页并回读基本配置证据。"""
    paper_size = str(paper_size).upper()
    projection = str(projection).lower()
    if paper_size not in PAPER_SIZES:
        raise ValueError(f"不支持的图幅: {paper_size}")
    if projection not in {"first_angle", "third_angle"}:
        raise ValueError("projection 必须是 first_angle 或 third_angle")
    selection = select_drawing_template(template_candidates, paper_size=paper_size, require_gbt=require_gbt)
    if not selection["selected"]:
        return {**selection, "status": "blocked", "stage": "preflight", "configured": False, "retryable": True}
    sheet = _safe_member(drawing_model, "GetCurrentSheet")
    sheet_name = str(_safe_member(sheet, "GetName", default="") or "")
    if not sheet_name:
        return {**selection, "status": "blocked", "stage": "preflight", "configured": False, "error_code": "DRAWING_CURRENT_SHEET_MISSING"}
    try:
        configured = bool(get_com_member(
            drawing_model,
            "SetupSheet6",
            sheet_name,
            PAPER_SIZES[paper_size]["code"],
            12,
            1.0,
            1.0,
            projection == "first_angle",
            selection["selected"],
            0.0,
            0.0,
            "",
            False,
            0.0,
            0.0,
            0.0,
            0.0,
            0,
            0,
        ))
    except Exception as exc:
        return {**selection, "status": "failed", "stage": "create", "configured": False, "projection": projection, "error_code": "DRAWING_SHEET_SETUP_FAILED", "error": str(exc)}
    return {
        **selection,
        "status": "pass" if configured else "failed",
        "stage": "create",
        "configured": configured,
        "paper_size": paper_size,
        "projection": projection,
        "sheet_name": sheet_name,
        "error_code": None if configured else "DRAWING_SHEET_SETUP_FAILED",
        "manual_review_required": True,
    }


def validate_generic_drawing_generation(spec) -> dict:
    """@brief 在修改文档前声明通用生成器无法可靠执行的 DrawingSpec 字段。"""
    issues = []
    views = dict(spec.get("views") or {})
    standard_views = {name for name in ("front", "top", "right") if name in views}
    if standard_views != {"front", "top", "right"}:
        issues.append({
            "code": "DRAWING_STANDARD_VIEW_SET_UNSUPPORTED",
            "path": "views",
            "message": "通用生成器当前只支持同时生成 front/top/right 三视图。",
        })
    unsupported_views = [name for name in ("bottom", "left", "isometric") if name in views]
    unsupported_views.extend(name for name in ("sections", "details") if views.get(name))
    if unsupported_views:
        issues.append({
            "code": "DRAWING_REQUESTED_VIEWS_UNSUPPORTED",
            "path": "views",
            "views": unsupported_views,
            "message": "通用生成器尚不能创建请求的辅助、轴测、剖视或局部视图。",
        })
    configured_views = [name for name in ("front", "top", "right") if views.get(name)]
    if configured_views:
        issues.append({
            "code": "DRAWING_VIEW_OPTIONS_UNSUPPORTED",
            "path": "views",
            "views": configured_views,
            "message": "通用生成器尚不能执行标准视图对象内的名称、方向或位置选项。",
        })
    if spec.get("requiredDimensions"):
        issues.append({
            "code": "DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED",
            "path": "requiredDimensions",
            "message": "通用生成器只能导入模型尺寸，不能可靠创建并绑定指定 ID、视图和语义的尺寸。",
        })
    if spec.get("holeRequirements"):
        issues.append({
            "code": "DRAWING_HOLE_REQUIREMENTS_UNSUPPORTED",
            "path": "holeRequirements",
            "message": "通用生成器尚不能创建孔标注或孔表；请使用专项脚本并回读证据。",
        })
    professional_annotations = dict(spec.get("professionalAnnotations") or {})
    unsupported_professional_fields = sorted(
        name for name, values in professional_annotations.items()
        if name != "centerMarks" and values
    )
    if unsupported_professional_fields:
        issues.append({
            "code": "DRAWING_PROFESSIONAL_ANNOTATIONS_UNSUPPORTED",
            "path": "professionalAnnotations",
            "fields": unsupported_professional_fields,
            "message": "通用生成器目前只支持已回读验证的自动中心标记；其余专业标注仍须使用专项脚本。",
        })
    title_fields = sorted(set((spec.get("titleBlock") or {})) - {"required", "format"})
    if title_fields:
        issues.append({
            "code": "DRAWING_TITLE_BLOCK_FIELDS_UNSUPPORTED",
            "path": "titleBlock",
            "fields": title_fields,
            "message": "通用生成器尚不能绑定标题栏业务字段。",
        })
    if spec.get("sheetMetal"):
        issues.append({
            "code": "DRAWING_SHEET_METAL_OPTIONS_UNSUPPORTED",
            "path": "sheetMetal",
            "message": "通用生成器尚不能执行展开图、折弯表或钣金专用选项。",
        })
    return {
        "status": "blocked" if issues else "pass",
        "stage": "capability_preflight",
        "issues": issues,
        "error_code": "DRAWING_SPEC_CAPABILITY_UNSUPPORTED" if issues else None,
        "manual_review_required": bool(issues),
    }


def generate_drawing_from_spec(drawing_model, spec, source_model_path, template_candidates=None) -> dict:
    """@brief 按已校验 DrawingSpec 创建标准工程图结构和制造标注入口。"""
    capability = validate_generic_drawing_generation(spec)
    if capability["status"] != "pass":
        return capability
    paper_size = str(spec.get("paperSize", "A3")).upper()
    projection = str(spec.get("projection", "first_angle")).lower()
    model_size_mm = spec.get("modelSizeMm")
    if not isinstance(model_size_mm, (list, tuple)) or len(model_size_mm) != 3:
        return {
            "status": "blocked",
            "stage": "planning",
            "error_code": "DRAWING_MODEL_SIZE_MISSING",
            "message": "DrawingSpec 必须提供 modelSizeMm，避免凭空推断工程图比例和视图布局。",
            "manual_review_required": True,
        }
    candidates = list(template_candidates or spec.get("templateCandidates") or [])
    sheet_setup = setup_current_sheet(
        drawing_model,
        candidates,
        paper_size=paper_size,
        projection=projection,
        require_gbt=spec.get("standard") == "GB_T",
    )
    if sheet_setup.get("status") != "pass":
        return {"status": sheet_setup.get("status", "blocked"), "stage": "sheet", "sheetSetup": sheet_setup, "error_code": sheet_setup.get("error_code"), "manual_review_required": True}
    model_size_m = tuple(float(value) / 1000.0 for value in model_size_mm)
    layout = plan_standard_view_layout(
        model_size_m,
        paper_size=paper_size,
        projection=projection,
        requested_scale=spec.get("scale"),
    )
    if layout.get("status") != "pass":
        return {"status": "blocked", "stage": "layout", "sheetSetup": sheet_setup, "layout": layout, "error_code": layout.get("error_code"), "manual_review_required": True}
    views = create_adaptive_standard_views(drawing_model, str(source_model_path), layout)
    if views.get("status") != "pass":
        return {"status": "failed", "stage": "views", "sheetSetup": sheet_setup, "layout": layout, "views": views, "error_code": views.get("error_code"), "manual_review_required": True}
    professional_annotations = dict(spec.get("professionalAnnotations") or {})
    center_marks = auto_insert_center_marks(drawing_model, professional_annotations.get("centerMarks"))
    if center_marks.get("status") == "failed":
        save_required = center_marks.get("error_code") == "DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED"
        return {
            "status": "blocked" if save_required else "failed",
            "stage": "professional_annotations",
            "professionalAnnotations": {"centerMarks": center_marks},
            "sheetSetup": sheet_setup,
            "layout": layout,
            "views": views,
            "error_code": center_marks.get("error_code"),
            "retryable": bool(center_marks.get("retryable")),
            "manual_review_required": True,
        }
    dimension_result = insert_dimensions(drawing_model) if spec.get("requiredDimensions") or spec.get("insertModelDimensions", True) else False
    arrangement = auto_arrange_drawing_dimensions(drawing_model) if dimension_result else {"status": "review_required", "error_code": "DRAWING_DIMENSIONS_NOT_REQUESTED"}
    bom_spec = spec.get("bom") or {}
    bom_requested = bool(bom_spec.get("required")) or spec.get("documentType") == "assembly"
    bom_result = {"requested": bom_requested, "created": False, "status": "not_requested"}
    if bom_requested:
        template_path = str(bom_spec.get("templatePath") or "")
        if not template_path or not Path(template_path).expanduser().is_file():
            return {"status": "blocked", "stage": "bom", "error_code": "DRAWING_BOM_TEMPLATE_MISSING", "message": "BOM 已要求但模板不存在，不能伪造表格交付。", "sheetSetup": sheet_setup, "layout": layout, "views": views, "manual_review_required": True}
        position = bom_spec.get("positionMm") or [250.0, 45.0]
        bom_table = insert_bom_table(drawing_model, template_path, float(position[0]) / 1000.0, float(position[1]) / 1000.0, int(bom_spec.get("bomType", 1)), str(bom_spec.get("configuration", "")))
        bom_result = {"requested": True, "created": bom_table is not None, "status": "pass" if bom_table is not None else "failed", "template_path": template_path, "position_mm": position, "error_code": None if bom_table is not None else "DRAWING_BOM_INSERT_FAILED"}
        if bom_table is None:
            return {"status": "failed", "stage": "bom", "bom": bom_result, "sheetSetup": sheet_setup, "layout": layout, "views": views, "manual_review_required": True}
    notes = []
    for index, note_text in enumerate(spec.get("notes") or []):
        note_result = add_note(drawing_model, 0.02, 0.02 + index * 0.006, str(note_text))
        notes.append(note_result)
        if note_result.get("status") != "pass":
            return {
                "status": "failed",
                "stage": "notes",
                "error_code": note_result.get("error_code") or "DRAWING_NOTE_COM_EVIDENCE_MISSING",
                "notes": notes,
                "sheetSetup": sheet_setup,
                "layout": layout,
                "views": views,
                "manual_review_required": True,
            }
    structure = inspect_drawing_structure(
        drawing_model,
        paper_size_hint=paper_size,
        title_block_box=layout.get("title_block_box"),
    )
    status = "pass" if structure.get("status") == "pass" and dimension_result else "review_required"
    return {
        "status": status,
        "stage": "review",
        "source_model": str(source_model_path),
        "standard": spec.get("standard"),
        "projection": projection,
        "sheetSetup": sheet_setup,
        "layout": layout,
        "views": views,
        "professionalAnnotations": {"centerMarks": center_marks},
        "dimensions": {"inserted": bool(dimension_result), "arrangement": arrangement},
        "bom": bom_result,
        "notes": notes,
        "structure": structure,
        "manual_review_required": True,
        "error_code": None if status == "pass" else "DRAWING_GENERATION_REVIEW_REQUIRED",
    }


# ══════════════════════════════════════════════════════════════════════
# 补齐工程图域此前未触及的 8 个接口族
# （见 docs/family-coverage.md：表注解 5 类 + ISectionViewData
#   + IAnnotationView + IModelViewManager 核实）
# ══════════════════════════════════════════════════════════════════════

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IDrawingDoc 段 + ITableAnnotation 段
# 定位:   表注解的创建与公共操作。官方签名：
#           TableAnnotation InsertTableAnnotation(Double X, Double Y, Int32 Type,
#                                               Int32 Row, Int32 Column)  ← 5 参
#           TableAnnotation InsertTableAnnotation2(Boolean UseAnchorPoint,
#                                               Double X, Double Y, Int32 Type,
#                                               String Template, Int32 Row,
#                                               Int32 Column)            ← 7 参
#           ITableAnnotation : Int32  get_RowCount() / get_ColumnCount()
#                               String get_Text(Int32 Row, Int32 Col)
#                               String get_DisplayedText(Int32, Int32)
#                               Boolean DeleteRow(Int32) / DeleteColumn(Int32)
#                               Void set_RowHidden(Int32, Boolean) 等
#           各具体表（见下方各族）另有 Sort(Int32, Boolean) 与
#           自定义属性读写（Get/SetColumnCustomProperty）。
# ⚠ InsertTableAnnotation 的 Int32 Type 决定表的种类（孔表/修订表/BOM…），
#   其枚举在两套官方源里都查不到（sw_know 检索无对应枚举定义），
#   故本模块**只做透传、不设默认类型**，由调用方按官方文档指定。
# 覆盖:   后续同级定义 —— 本块文档化本节新增的全部函数。
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def insert_table_annotation(
    drawing_model,
    x: float,
    y: float,
    table_type: int,
    row: int = 0,
    column: int = 0,
    *,
    template: str = "",
    use_anchor_point: bool = False,
):
    """在图纸坐标 (x, y) 插入表注解；给了 template 走 7 参版本，否则走 5 参版本。"""
    if drawing_model is None:
        raise ValueError("drawing_model 为 None")
    if template:
        return get_com_member(
            drawing_model, "InsertTableAnnotation2",
            bool(use_anchor_point), float(x), float(y),
            int(table_type), str(template), int(row), int(column),
        )
    return get_com_member(
        drawing_model, "InsertTableAnnotation",
        float(x), float(y), int(table_type), int(row), int(column),
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → ITableAnnotation 段
# 定位:   表注解的公共读写。**逐个属性显式赋值，不用 mapping 循环** ——
#         循环里的属性名是变量，静态审计与 family-coverage 无法归因，
#         会让这一族长期显示「未触及」（代码写了但工具看不见）。
#         官方签名（全部是属性，get/set 成对）：
#           Int32  get_RowCount() / get_ColumnCount() / get_AnchorType()
#           Boolean get_Anchored() / get_StopAutoSplitting()
#           String get_Text(Int32 Row, Int32 Col)
#           String get_DisplayedText(Int32 Row, Int32 Col)
#           Boolean get_RowHidden(Int32) / get_ColumnHidden(Int32)
#           Boolean DeleteRow(Int32) / DeleteColumn(Int32)
# ⚠ Text / DisplayedText 的下标是 0 基还是 1 基，两套官方源都未说明，
#   故本函数按原样透传，不做 ±1 猜测。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_table_text(table, row: int, column: int) -> str:
    """读表内一格文本。"""
    if table is None:
        raise ValueError("table 为 None")
    return str(get_com_member(table, "Text", int(row), int(column)) or "")


def get_table_shape(table) -> dict[str, Any]:
    """回读表的行列数与显隐状态。"""
    if table is None:
        raise ValueError("table 为 None")
    return {
        "rows": int(get_com_member(table, "RowCount") or 0),
        "columns": int(get_com_member(table, "ColumnCount") or 0),
        "anchored": bool(get_com_member(table, "Anchored")),
        "anchor_type": int(get_com_member(table, "AnchorType") or -1),
    }


def set_table_row_hidden(table, row: int, hidden: bool = True) -> bool:
    """显隐某一行。"""
    if table is None:
        raise ValueError("table 为 None")
    return bool(get_com_member(table, "RowHidden", int(row), bool(hidden)))


def set_table_column_hidden(table, column: int, hidden: bool = True) -> bool:
    """显隐某一列。"""
    if table is None:
        raise ValueError("table is None")
    return bool(get_com_member(table, "ColumnHidden", int(column), bool(hidden)))


def delete_table_row(table, row: int) -> bool:
    if table is None:
        raise ValueError("table 为 None")
    return bool(get_com_member(table, "DeleteRow", int(row)))


def delete_table_column(table, column: int) -> bool:
    if table is None:
        raise ValueError("table is None")
    return bool(get_com_member(table, "DeleteColumn", int(column)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IGeneralTableAnnotation / IHoleTableAnnotation /
#             IBendTableAnnotation / IWeldmentCutListAnnotation /
#             IRevisionTableAnnotation 段
# 定位:   5 个具体表族各取「底层表对象」。官方 getter 名逐条照录：
#           IGeneralTableAnnotation     : GeneralTableFeature get_GeneralTable()
#           IHoleTableAnnotation        : HoleTable get_HoleTable()
#           IBendTableAnnotation        : BendTable get_BendTable()
#           IWeldmentCutListAnnotation  : WeldmentCutListFeature get_WeldmentCutListFeature()
#           IRevisionTableAnnotation    : RevisionTableFeature get_RevisionTableFeature()
# ⚑ 逐个显式封装、**不用字典 + 变量名分发** —— 这是本项目第三次因
#   「属性名/成员名是变量」导致静态审计与 family-coverage 无法归因，
#   导致这几个族明明写了代码却长期显示「未触及」。显式写法同时更好读。
# ⚠ 取用路径: 各表注解对象由 IDrawingDoc.InsertTableAnnotation(2) 返回。
#   InsertTableAnnotation 的 Int32 Type 决定表种类，其枚举在两套官方源里
#   都查不到，故本模块只透传、不设默认类型。
# ⚠ IBendTableAnnotation **没有** Sort 成员（反射确认），故不提供 bend 表的排序封装。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_general_table(table):
    """``IGeneralTableAnnotation.GeneralTable``（属性）"""
    if table is None:
        raise ValueError("table 为 None")
    return get_com_member(table, "GeneralTable")


def get_hole_table(table):
    """``IHoleTableAnnotation.HoleTable``（属性）"""
    if table is None:
        raise ValueError("table 为 None")
    return get_com_member(table, "HoleTable")


def get_bend_table(table):
    """``IBendTableAnnotation.BendTable``（属性）"""
    if table is None:
        raise ValueError("table is None")
    return get_com_member(table, "BendTable")


def get_weldment_cutlist_table(table):
    """``IWeldmentCutListAnnotation.WeldmentCutListFeature``（属性）"""
    if table is None:
        raise ValueError("table 为 None")
    return get_com_member(table, "WeldmentCutListFeature")


def get_revision_table_feature(table):
    """``IRevisionTableAnnotation.RevisionTableFeature``（属性）"""
    if table is None:
        raise ValueError("table is None")
    return get_com_member(table, "RevisionTableFeature")


def get_table_custom_property_column(table, column: int) -> str:
    """读表的自定义属性列名。5 个表族共有该成员。"""
    if table is None:
        raise ValueError("table 为 None")
    return str(get_com_member(table, "GetColumnCustomProperty", int(column)) or "")


def set_table_custom_property_column(table, column: int, property_name: str) -> bool:
    """设表的自定义属性列名。5 个表族共有该成员。"""
    if table is None:
        raise ValueError("table 为 None")
    return bool(get_com_member(table, "SetColumnCustomProperty",
                               int(column), str(property_name)))


def sort_table(table, option: int, reverse: bool = False) -> bool:
    """排序。**孔表 / 通用表 / 焊接下料表 / 修订表族**共有 ``Sort(Int32, Boolean)``；
    折弯表 ``IBendTableAnnotation`` 反射确认**没有** Sort，故不做统一封装。"""
    if table is None:
        raise ValueError("table 为 None")
    return bool(get_com_member(table, "Sort", int(option), bool(reverse)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IRevisionTableAnnotation 段
# 定位:   修订表的增删与回读。官方签名：
#             Int32    AddRevision(String Revision)                    ← 1 参
#             Boolean  DeleteRevision(Int32 Index, Boolean MarkDeleted) ← 2 参
#             String   get_CurrentRevision()
#             Sheet    GetSheet()
# ⚠ 修订号字符串的格式（GB/T 的 A/B/C 还是 1/2/3）两套官方源都未说明，
#   故只透传字符串，不做格式校验或自动生成。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_revision(revision_table, revision: str) -> int:
    """新增一个修订号，返回官方给出的行号。"""
    if revision_table is None:
        raise ValueError("revision_table 为 None")
    return int(get_com_member(revision_table, "AddRevision", str(revision)) or -1)


def delete_revision(revision_table, index: int, mark_deleted: bool = True) -> bool:
    if revision_table is None:
        raise ValueError("revision_table 为 None")
    return bool(get_com_member(revision_table, "DeleteRevision",
                               int(index), bool(mark_deleted)))


def get_current_revision(revision_table) -> str:
    if revision_table is None:
        raise ValueError("revision_table 为 None")
    return str(get_com_member(revision_table, "CurrentRevision") or "")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISectionViewData 段
# 定位:   剖视图的显示样式与剖切参数（35 成员，本域此前未触及）。
#         官方签名（**全部是属性**，get/set 成对，无创建方法）：
#           Int32  get_FirstColor() / get_SecondColor() / get_ThirdColor()
#                  get_SectionedZones()
#           Double get_FirstOffset() / get_SecondOffset() / get_ThirdOffset()
#                  get_TransparencyValue()
#                  get_FirstRotationX() / get_FirstRotationY() 等
#           Object get_FirstPlane() / get_SecondPlane() / get_ThirdPlane()
#                  get_SelectiveSectioningList() / get_TransparencyList()
#           Boolean get_ShowSectionCap() / get_TransparentSection() /
#                  get_ZonalSection() / get_SelectiveSection() /
#                  get_GraphicsOnlySection() / get_KeepCapColor() /
#                  get_ExcludeSelectedItems() / get_Redraw() 等
#         取用路径：剖视图对象的 GetDefinition()（与 drawing_workflow 里
#         其它 Definition 取用同构）。
# ⚠ 本接口**无 InsertSectionView 之类的创建方法** —— 剖视图由
#   IDrawingDoc.CreateSectionViewAt5 创建（见 add_section_view），
#   本函数只做事后样式调整。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_section_view_data(section_view):
    """取剖视图的定义对象 ISectionViewData。"""
    if section_view is None:
        raise ValueError("section_view 为 None")
    return get_com_member(section_view, "GetDefinition")


def set_section_style(
    section_data,
    *,
    show_section_cap: bool | None = None,
    zonal_section: bool | None = None,
    transparent_section: bool | None = None,
    transparency_value: float | None = None,
    graphics_only_section: bool | None = None,
    keep_cap_color: bool | None = None,
    sectioned_zones: int | None = None,
    first_color: int | None = None,
    second_color: int | None = None,
    third_color: int | None = None,
    first_offset: float | None = None,
    second_offset: float | None = None,
    third_offset: float | None = None,
):
    """装配剖视显示样式。全部可选，**只设你显式给了值的那些**。

    ⚑ 逐项显式赋值，**不用 dict + 循环** —— 循环里属性名是变量，
    静态审计与 family-coverage 无法归因。这是本项目**第三次**因该写法
    让「已经写了代码」的族长期显示「未触及」。
    """
    if section_data is None:
        raise ValueError("section_data 为 None")
    applied = {}
    if show_section_cap is not None:
        get_com_member(section_data, "ShowSectionCap", bool(show_section_cap))
        applied["ShowSectionCap"] = bool(show_section_cap)
    if zonal_section is not None:
        get_com_member(section_data, "ZonalSection", bool(zonal_section))
        applied["ZonalSection"] = bool(zonal_section)
    if transparent_section is not None:
        get_com_member(section_data, "TransparentSection", bool(transparent_section))
        applied["TransparentSection"] = bool(transparent_section)
    if transparency_value is not None:
        get_com_member(section_data, "TransparencyValue", float(transparency_value))
        applied["TransparencyValue"] = float(transparency_value)
    if graphics_only_section is not None:
        get_com_member(section_data, "GraphicsOnlySection", bool(graphics_only_section))
        applied["GraphicsOnlySection"] = bool(graphics_only_section)
    if keep_cap_color is not None:
        get_com_member(section_data, "KeepCapColor", bool(keep_cap_color))
        applied["KeepCapColor"] = bool(keep_cap_color)
    if sectioned_zones is not None:
        get_com_member(section_data, "SectionedZones", int(sectioned_zones))
        applied["SectionedZones"] = int(sectioned_zones)
    if first_color is not None:
        get_com_member(section_data, "FirstColor", int(first_color))
        applied["FirstColor"] = int(first_color)
    if second_color is not None:
        get_com_member(section_data, "SecondColor", int(second_color))
        applied["SecondColor"] = int(second_color)
    if third_color is not None:
        get_com_member(section_data, "ThirdColor", int(third_color))
        applied["ThirdColor"] = int(third_color)
    if first_offset is not None:
        get_com_member(section_data, "FirstOffset", float(first_offset))
        applied["FirstOffset"] = float(first_offset)
    if second_offset is not None:
        get_com_member(section_data, "SecondOffset", float(second_offset))
        applied["SecondOffset"] = float(second_offset)
    if third_offset is not None:
        get_com_member(section_data, "ThirdOffset", float(third_offset))
        applied["ThirdOffset"] = float(third_offset)
    return applied


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISectionViewData 段
# 定位:   set_section_style 支持的属性名白名单。逐个照抄该接口的 setter 名，
#         不多不少（**白名单本身就是文档**：不在表里的属性名会被显式拒绝）。
# 覆盖:   后续同级定义
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SUPPORTED_SECTION_PROPERTIES = {
    "ExcludeSelectedItems", "FirstColor", "FirstOffset", "FirstPlane",
    "FirstReverseDirection", "FirstRotationX", "FirstRotationY",
    "GraphicsOnlySection", "KeepCapColor", "Redraw", "SecondColor",
    "SecondOffset", "SecondPlane", "SecondReverseDirection", "SecondRotationX",
    "SecondRotationY", "SectionedZones", "SectionTransparentItemsTransparent",
    "SelectiveSection", "SelectiveSectioningList", "ShowSectionCap",
    "ThirdColor", "ThirdOffset", "ThirdPlane", "ThirdReverseDirection",
    "ThirdRotationX", "ThirdRotationY", "TransparencyList",
    "TransparencyValue", "TransparentSection", "ZonalSection",
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IAnnotationView 段
# 定位:   注释视图（工程图里注释的嵌套层，17 成员，本域此前未触及）。
#         官方签名：
#           Boolean Activate() / ActivateAndReorient() / Orient()
#           Boolean Show() / Hide() / IsShown()
#           Int32   get_AnnotationCount()
#           Object  get_Annotations()
#           Object  GetAnnotations2(Boolean, Boolean)      ← 2 参
#           Boolean get_Always2D() / get_FlatPatternView() / get_UnassignedView()
#           Double  get_AngleMadeWithViewHorizontal()
#           Object  GetViewRotation()
#           Boolean MoveAnnotations(Object)                ← 1 参
# 取用路径: IAnnotation 的 GetAnnotationView? —— 本函数只接受**已取回的
#         注释视图对象**，不代为取回，避免猜测上游取用路径。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def activate_annotation_view(annotation_view, *, reorient: bool = False) -> bool:
    """激活注释视图（可选同时重定向）。"""
    if annotation_view is None:
        raise ValueError("annotation_view 为 None")
    method = "ActivateAndReorient" if reorient else "Activate"
    return bool(get_com_member(annotation_view, method))


def get_annotation_view_evidence(annotation_view) -> dict[str, Any]:
    """回读注释视图状态。"""
    if annotation_view is None:
        raise ValueError("annotation_view 为 None")
    return {
        "is_shown": bool(get_com_member(annotation_view, "IsShown")),
        "annotation_count": int(get_com_member(annotation_view, "AnnotationCount") or 0),
        "always_2d": bool(get_com_member(annotation_view, "Always2D")),
        "flat_pattern_view": bool(get_com_member(annotation_view, "FlatPatternView")),
        "unassigned_view": bool(get_com_member(annotation_view, "UnassignedView")),
        "angle_deg": float(
            get_com_member(annotation_view, "AngleMadeWithViewHorizontal") or 0.0
        ),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IModelViewManager 段
# 定位:   IModelViewManager 共 42 成员。本项目此前把它整体判为「范围外」，
#         经复核**该判定过宽** —— 它虽以 FeatureManager UI 为主，但确实带
#         工程图相关成员。这里只封装**与剖视图直接相关**的 4 个：
#             SectionViewData CreateSectionViewData()          ← 0 参
#             Boolean       CreateSectionView(SectionViewData) ← 1 参
#             SectionViewData GetSectionViewData(String)       ← 1 参
#             Boolean       RemoveSectionView()                ← 0 参
#         取用路径: IModelDoc2.GetModelViewManager()（属性）→ 本节函数。
# ⚠ 该接口另有 38 个成员属 **FeatureManager 界面自动化**（标签页 / 控件 /
#   窗口句柄 / 快照 / Manipulator），与工程图能力无关，逐条列在
#   MODEL_VIEW_MANAGER_UI_MEMBERS，**本项目刻意不封装**。需要时按该名单
#   自行加，本处不假装它们不存在。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: IModelViewManager 中属 FeatureManager 界面自动化、本项目**刻意不封装**的成员。
#: 列出来是为了「不假装它不存在」——需要时可按名单逐个加。
MODEL_VIEW_MANAGER_UI_MEMBERS = (
    "ActivateControlTab", "ActivateModelTab", "AddControl", "AddControl2",
    "AddControl3", "AddSnapShot", "CreateFeatureMgrControl",
    "CreateFeatureMgrControl2", "CreateFeatureMgrControl3",
    "CreateFeatureMgrControl4", "CreateFeatureMgrView", "CreateFeatureMgrView2",
    "CreateFeatureMgrWindowFromHandle", "CreateFeatureMgrWindowFromHandlex64",
    "CreateManipulator", "DeleteControlTab", "DeleteSnapShot",
    "DisplayWindowFromHandle", "DisplayWindowFromHandlex64",
    "GetConfigurationManagerTabIndex", "GetControl", "GetDimXpertManagerTabIndex",
    "GetDisplayManagerTabIndex", "GetFeatureManagerTabs",
    "GetFeatureManagerTreeTabIndex", "GetFeatureMgrViewHWnd",
    "GetFeatureMgrViewHWndx64", "GetPropertyManagerTabIndex", "GetSnapShot",
    "GetSnapShots", "IsControlTabActive", "IsModelTabActive",
    "ActiveFeatureManagerTabIndex", "Document", "FeatureManagerTabsVisible",
    "LinkedViews", "ViewportDisplay",
)


def get_model_view_manager(model):
    """取 IModelViewManager（属性，不是方法）。"""
    manager = get_com_member(model, "GetModelViewManager")
    if manager is None:
        raise RuntimeError("IModelDoc2.GetModelViewManager() 返回 None")
    return manager


def create_section_view_data(model):
    """创建剖视定义对象 ISectionViewData（0 参）。"""
    # ⚑ 先把 manager 存进局部变量，**不要**写成
    #   get_com_member(get_model_view_manager(model), "CreateSectionViewData") ——
    #   嵌套调用会让第一个实参里出现括号，静态审计的正则
    #   `get_com_member\(\s*[^,()]+,\s*["']...` 就匹配不到。
    #   这是「变量名/嵌套调用导致工具看不见」的**第四种形态**。
    manager = get_model_view_manager(model)
    return get_com_member(manager, "CreateSectionViewData")


def create_feature_manager_section_view(model, section_data) -> bool:
    """用 FeatureManager 路径创建剖视（1 参）。"""
    if section_data is None:
        raise ValueError("section_data 为 None：先用 create_section_view_data()")
    manager = get_model_view_manager(model)
    return bool(get_com_member(manager, "CreateSectionView", section_data))


def get_feature_manager_section_data(model, name: str):
    """按名字取剖视定义对象（1 参）。"""
    manager = get_model_view_manager(model)
    return get_com_member(manager, "GetSectionViewData", str(name))


def remove_feature_manager_section_view(model) -> bool:
    """删除当前剖视（0 参）。"""
    manager = get_model_view_manager(model)
    return bool(get_com_member(manager, "RemoveSectionView"))
