"""标准外啮合直齿圆柱齿轮的渐开线几何与 SolidWorks 建模工具。"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Iterable


@dataclass(frozen=True)
class SpurGearSpec:
    """@brief 标准全齿高外啮合直齿轮输入，尺寸单位均为毫米。"""

    module_mm: float
    teeth: int
    face_width_mm: float
    pressure_angle_deg: float = 20.0
    bore_diameter_mm: float = 0.0
    involute_segments: int = 12
    tip_arc_segments: int = 4
    root_arc_segments: int = 5


@dataclass(frozen=True)
class SpurGearGeometry:
    """@brief 经过校验的齿轮解析尺寸和闭合外轮廓。"""

    spec: SpurGearSpec
    pitch_diameter_mm: float
    base_diameter_mm: float
    outside_diameter_mm: float
    root_diameter_mm: float
    circular_pitch_mm: float
    tooth_thickness_at_pitch_mm: float
    minimum_teeth_without_undercut: int
    undercut_risk: bool
    outline_points_m: tuple[tuple[float, float], ...]
    warnings: tuple[str, ...]

    def evidence(self) -> dict:
        """@brief 返回可序列化的输入、解析尺寸和近似精度证据。"""
        return {
            "gear_type": "standard_external_spur_involute",
            "input": asdict(self.spec),
            "dimensions_mm": {
                "pitch_diameter": self.pitch_diameter_mm,
                "base_diameter": self.base_diameter_mm,
                "outside_diameter": self.outside_diameter_mm,
                "root_diameter": self.root_diameter_mm,
                "circular_pitch": self.circular_pitch_mm,
                "tooth_thickness_at_pitch": self.tooth_thickness_at_pitch_mm,
                "face_width": self.spec.face_width_mm,
                "bore_diameter": self.spec.bore_diameter_mm,
            },
            "profile": {
                "curve": "involute_of_base_circle",
                "addendum_coefficient": 1.0,
                "dedendum_coefficient": 1.25,
                "profile_shift_coefficient": 0.0,
                "root_form": "radial_transition_plus_root_arc",
                "involute_segments_per_flank": self.spec.involute_segments,
                "outline_segment_count": len(self.outline_points_m),
            },
            "minimum_teeth_without_undercut": self.minimum_teeth_without_undercut,
            "undercut_risk": self.undercut_risk,
            "warnings": list(self.warnings),
        }


def _finite_positive(value: float, name: str) -> float:
    """@brief 校验有限正数并返回浮点值。"""
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"{name} 必须是有限正数")
    return number


def _involute_angle(t: float) -> float:
    """@brief 返回 inv(alpha)=tan(alpha)-alpha 的参数形式。"""
    return float(t) - math.atan(float(t))


def _polar(radius_m: float, angle_rad: float) -> tuple[float, float]:
    """@brief 把极坐标转换为草图平面笛卡尔坐标。"""
    return radius_m * math.cos(angle_rad), radius_m * math.sin(angle_rad)


def _append_unique(points: list[tuple[float, float]], point: tuple[float, float]) -> None:
    """@brief 避免相邻重复点产生零长度草图线。"""
    if points and math.dist(points[-1], point) <= 1e-12:
        return
    points.append(point)


def _sample_angles(start: float, end: float, segments: int) -> Iterable[float]:
    """@brief 返回圆弧内部采样角；端点由相邻轮廓负责。"""
    for index in range(1, segments):
        yield start + (end - start) * index / segments


def calculate_external_spur_gear(spec: SpurGearSpec) -> SpurGearGeometry:
    """@brief 计算标准全齿高外啮合直齿轮的离散渐开线闭合轮廓。

    采用 ``d=m*z``、``db=d*cos(alpha)``、``da=d+2m``、
    ``df=d-2.5m``。齿廓从基圆或齿根圆中较大者开始，齿根低于基圆时使用
    径向过渡；这不是滚刀生成的精确齿根过渡曲线，因此结果必须保持 reviewed。
    """
    module_mm = _finite_positive(spec.module_mm, "模数")
    face_width_mm = _finite_positive(spec.face_width_mm, "齿宽")
    if isinstance(spec.teeth, bool) or int(spec.teeth) != spec.teeth:
        raise ValueError("齿数必须是整数")
    teeth = int(spec.teeth)
    if teeth < 6 or teeth > 300:
        raise ValueError("齿数必须位于 6..300；更大轮廓应使用专用齿轮软件或原生插件")
    pressure_angle_deg = float(spec.pressure_angle_deg)
    if not math.isfinite(pressure_angle_deg) or not 10.0 <= pressure_angle_deg <= 35.0:
        raise ValueError("压力角必须位于 10..35 度")
    bore_diameter_mm = float(spec.bore_diameter_mm)
    if not math.isfinite(bore_diameter_mm) or bore_diameter_mm < 0.0:
        raise ValueError("轴孔直径不能为负数")
    for value, name, lower, upper in (
        (spec.involute_segments, "单侧渐开线段数", 4, 64),
        (spec.tip_arc_segments, "齿顶圆弧段数", 2, 32),
        (spec.root_arc_segments, "齿根圆弧段数", 2, 32),
    ):
        if isinstance(value, bool) or int(value) != value or not lower <= int(value) <= upper:
            raise ValueError(f"{name} 必须位于 {lower}..{upper}")

    alpha = math.radians(pressure_angle_deg)
    pitch_radius_mm = module_mm * teeth / 2.0
    base_radius_mm = pitch_radius_mm * math.cos(alpha)
    outside_radius_mm = pitch_radius_mm + module_mm
    root_radius_mm = pitch_radius_mm - 1.25 * module_mm
    if root_radius_mm <= 0.0:
        raise ValueError("齿根圆半径非正；请增大齿数或调整齿制")
    if bore_diameter_mm >= 2.0 * root_radius_mm:
        raise ValueError("轴孔直径必须小于齿根圆直径")

    pitch = 2.0 * math.pi / teeth
    pitch_involute = _involute_angle(math.tan(alpha))
    base_half_angle = math.pi / (2.0 * teeth) + pitch_involute
    start_radius_mm = max(root_radius_mm, base_radius_mm)
    start_t = math.sqrt(max(0.0, (start_radius_mm / base_radius_mm) ** 2 - 1.0))
    tip_t = math.sqrt(max(0.0, (outside_radius_mm / base_radius_mm) ** 2 - 1.0))
    start_half_angle = base_half_angle - _involute_angle(start_t)
    tip_half_angle = base_half_angle - _involute_angle(tip_t)
    if tip_half_angle <= 0.0:
        raise ValueError("齿顶厚度退化为零；该参数组合需要变位或其他齿制")
    if pitch - 2.0 * start_half_angle <= 0.0:
        raise ValueError("相邻齿根轮廓相交；该参数组合不可用于当前标准齿形")

    estimated_segments = teeth * (
        2 * (int(spec.involute_segments) + 1)
        + int(spec.tip_arc_segments)
        + int(spec.root_arc_segments)
        + 2
    )
    if estimated_segments > 12_000:
        raise ValueError("齿廓离散段数超过 12000；请降低齿数或采样密度")

    points: list[tuple[float, float]] = []
    scale = 0.001
    for tooth_index in range(teeth):
        center = tooth_index * pitch
        left_start_angle = center - start_half_angle
        right_start_angle = center + start_half_angle

        if root_radius_mm < start_radius_mm:
            _append_unique(points, _polar(root_radius_mm * scale, left_start_angle))

        for index in range(int(spec.involute_segments) + 1):
            ratio = index / int(spec.involute_segments)
            parameter = start_t + (tip_t - start_t) * ratio
            radius_mm = base_radius_mm * math.sqrt(1.0 + parameter * parameter)
            half_angle = base_half_angle - _involute_angle(parameter)
            _append_unique(points, _polar(radius_mm * scale, center - half_angle))

        for angle in _sample_angles(
            center - tip_half_angle,
            center + tip_half_angle,
            int(spec.tip_arc_segments),
        ):
            _append_unique(points, _polar(outside_radius_mm * scale, angle))

        for index in range(int(spec.involute_segments), -1, -1):
            ratio = index / int(spec.involute_segments)
            parameter = start_t + (tip_t - start_t) * ratio
            radius_mm = base_radius_mm * math.sqrt(1.0 + parameter * parameter)
            half_angle = base_half_angle - _involute_angle(parameter)
            _append_unique(points, _polar(radius_mm * scale, center + half_angle))

        if root_radius_mm < start_radius_mm:
            _append_unique(points, _polar(root_radius_mm * scale, right_start_angle))

        next_left_angle = center + pitch - start_half_angle
        for angle in _sample_angles(
            right_start_angle,
            next_left_angle,
            int(spec.root_arc_segments),
        ):
            _append_unique(points, _polar(root_radius_mm * scale, angle))

    if len(points) < teeth * 8:
        raise RuntimeError("生成的齿廓点数异常")
    area = 0.5 * sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
    )
    if area <= 0.0:
        raise RuntimeError("齿廓方向或闭合顺序异常")

    minimum_teeth = math.ceil(2.0 / (math.sin(alpha) ** 2))
    undercut_risk = teeth < minimum_teeth
    warnings: list[str] = [
        "齿根采用径向过渡和齿根圆弧，不等同于滚刀生成的精确 trochoid 齿根。",
        "未包含变位、侧隙、齿顶修缘、齿向修形、公差、材料和强度校核。",
    ]
    if undercut_risk:
        warnings.append(
            f"齿数 {teeth} 小于当前压力角的理论无根切下限 {minimum_teeth}，存在根切风险。"
        )

    return SpurGearGeometry(
        spec=spec,
        pitch_diameter_mm=2.0 * pitch_radius_mm,
        base_diameter_mm=2.0 * base_radius_mm,
        outside_diameter_mm=2.0 * outside_radius_mm,
        root_diameter_mm=2.0 * root_radius_mm,
        circular_pitch_mm=math.pi * module_mm,
        tooth_thickness_at_pitch_mm=math.pi * module_mm / 2.0,
        minimum_teeth_without_undercut=minimum_teeth,
        undercut_risk=undercut_risk,
        outline_points_m=tuple(points),
        warnings=tuple(warnings),
    )


def create_external_spur_gear(model, spec: SpurGearSpec, plane_name: str = "Front Plane"):
    """@brief 在活动零件中绘制完整渐开线齿廓并一次拉伸成直齿轮。

    @param model SolidWorks IModelDoc2/IPartDoc。
    @param spec 标准外啮合直齿轮规格。
    @param plane_name 建模基准面，中英文名称由 ``sw_part`` 兼容。
    @return ``(feature, evidence)``；feature 为空时抛出异常。
    """
    geometry = calculate_external_spur_gear(spec)
    try:
        from .sw_part import extrude_boss, sketch, sketch_circle, sketch_line
    except ImportError:
        from sw_part import extrude_boss, sketch, sketch_circle, sketch_line

    sketch_manager = model.SketchManager
    old_add_to_db = None
    old_display = None
    with sketch(model, plane_name) as sketch_name:
        try:
            old_add_to_db = bool(sketch_manager.AddToDB)
            old_display = bool(sketch_manager.DisplayWhenAdded)
            sketch_manager.AddToDB = True
            sketch_manager.DisplayWhenAdded = False
        except Exception:
            old_add_to_db = None
            old_display = None
        try:
            points = geometry.outline_points_m
            profile_entity_count = 0
            #: ★★★★★ 2026-10-10 **修一处 1000× 单位 bug**（★ 业主点破 + 真机裁决）：
            #:   ★ 业主原话：「★ **那你再画个齿轮，看看是否和最初画行星减速太阳齿轮一样犯错误**」✓
            #:   ★★ **真机读数**（★ 证据 `output/_probe_gear_units.json` · ★ 走 `sw_guard`）：
            #:     · ★ 解析外径 **22.000 mm**（★ 独立算的）
            #:     · ★ `outline_points_m` 的最大半径 = **0.011000 m = 11.000 mm** ✓（★ **米**）
            #:     · ★★ 建件**失败**：`RuntimeError: 创建齿廓离散线段失败`
            #:     · ★★★ 回读包围盒 = **0.0039 × 0.0076 mm** ⇒ 比值 **0.000177** ≈ **1/1000** ✗
            #:   ★★★ **根因（两条，都在本函数里）**：
            #:     ① ★ `sketch_line` 的契约是**毫米**（★ 它内部再乘 `_MM_TO_M`）——
            #:        ★★ 而 `outline_points_m` 是**米** ⇒ ★ **又被除了一次 1000** ✗
            #:     ② ★ `sketch_circle` 同病：★ `bore_diameter_mm / 2000.0` 把 mm 先变成**米**，
            #:        ★★ 再当**毫米**传进去 ⇒ ★ **同样 1000×** ✗
            #:   ★★★ **正解**：★ 送进 `sketch_*` 之前**乘 1000**（★ 米 → 毫米）；
            #:     ★ 且**不要**再除 —— ★ 契约是「对外毫米」✓
            #:   ★★ **注意第三处是对的**：★ `extrude_boss` **确实收米**（★ 官方 `D1` = meters）
            #:     ⇒ ★ 那里保留 `face_width_mm / 1000.0` ✓（★ 三处口径**互不相同**，★ 别一刀切）
            for start, end in zip(points, points[1:] + points[:1]):
                if sketch_line(model,
                               start[0] * 1000.0, start[1] * 1000.0,
                               end[0] * 1000.0, end[1] * 1000.0) is None:
                    raise RuntimeError("创建齿廓离散线段失败")
                profile_entity_count += 1
            if spec.bore_diameter_mm > 0.0:
                #: ★★ 轴孔：★ `sketch_circle` 收**毫米** ⇒ ★ 直接传 `bore/2`（★ 不是 `/2000`）✓
                if sketch_circle(model, 0.0, 0.0, spec.bore_diameter_mm / 2.0) is None:
                    raise RuntimeError("创建齿轮轴孔草图失败")
                profile_entity_count += 1
        finally:
            try:
                if old_add_to_db is not None:
                    sketch_manager.AddToDB = old_add_to_db
                if old_display is not None:
                    sketch_manager.DisplayWhenAdded = old_display
            except Exception:
                pass

    feature = extrude_boss(model, sketch_name, spec.face_width_mm / 1000.0)
    if feature is None:
        raise RuntimeError("齿轮齿廓拉伸失败")
    feature_name = f"SpurGear_m{spec.module_mm:g}_z{spec.teeth}"
    try:
        feature.Name = feature_name
    except Exception:
        pass
    model.ForceRebuild3(False)
    evidence = geometry.evidence()
    evidence.update({
        "status": "review_required",
        "feature_name": feature_name,
        "plane_name": plane_name,
        "solidworks_profile_entity_count": profile_entity_count,
        "solidworks_flank_entity": "polyline_chord_approximation",
        "solidworks_tip_root_entities": "polyline_chord_approximation",
    })
    return feature, evidence


# ── 24h 计划 段 5/6 续（Spec Kit `158`）：**dict → SpurGearSpec 的包装** ─────────────
# ★★★★ 为什么包一层：★ 真机实测（轮 281）`calculate_external_spur_gear(spec)` 传 **dict** 时
#   报 **`'dict' object has no attribute 'module_mm'`** ⇒ ★★ **它要一个 `SpurGearSpec` 对象**。
# ★ 而**工具层的入参只能是 JSON**（★ dict）⇒ ★★ 所以正解是**在能力层做转换**
#    （★ 与孔族的 `*_at_selection`、求解器设置的 `*_report` **同一手法** —— 这是第三次）。
#
# ★ 判据：★ **转换失败要如实报**（★ 缺哪个键、非法值）—— ★ 不静默用默认值。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_gear.py —— 本段
# 定位:   段 5/6 续：让齿轮几何能从**工具层**（JSON 入参）表达。
# 官方依据: 渐开线直齿轮几何（★ 见 `scripts/sw_gear.py` 既有来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖: 后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _gear_spec_from_dict(spec):
    """★ 把 dict 变成 `SpurGearSpec`（★ **缺键/非法就抛**，不静默补默认）。"""
    if isinstance(spec, SpurGearSpec):
        return spec
    if not isinstance(spec, dict):
        raise TypeError("spec 必须是 dict 或 SpurGearSpec，收到 %s" % type(spec).__name__)
    import inspect as _inspect
    fields = {}
    try:
        params = _inspect.signature(SpurGearSpec).parameters
    except Exception:                                          # noqa: BLE001
        params = {}
    for name, p in params.items():
        if name in ("self",) or p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL):
            continue
        if name in spec:
            fields[name] = spec[name]
        elif p.default is _inspect.Parameter.empty:
            raise KeyError("spec 缺少必填字段 %r（★ 合法字段：%s）"
                           % (name, ", ".join(k for k in params if k != "self")))
    #: ★ 多余键也报出来（★ 否则调用方会以为它生效了）
    extra = [k for k in spec if k not in params]
    if extra:
        raise KeyError("spec 含未登记字段 %s（★ 合法字段：%s）"
                       % (extra, ", ".join(k for k in params if k != "self")))
    return SpurGearSpec(**fields)


def calculate_external_spur_gear_report(spec) -> dict:
    """★ **算外啮合直齿轮几何**（★ 吃 dict；★ 判据对**解析式**）。"""
    try:
        s = _gear_spec_from_dict(spec)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "spec", "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        g = calculate_external_spur_gear(s)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "calculate",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    out = {}
    for name in ("pitch_diameter_mm", "base_diameter_mm", "outer_diameter_mm",
                 "root_diameter_mm", "teeth", "module_mm"):
        try:
            out[name] = getattr(g, name, None)
        except Exception:                                      # noqa: BLE001
            out[name] = None
    #: ★ 解析式核对：★ pitch = module × teeth（★ 事实 204/§5.0：期望值用几何推出的公式）
    try:
        pd, mm_, z = float(out.get("pitch_diameter_mm")), float(s.module_mm), float(s.teeth)
        out["_check_pitch_equals_module_times_teeth"] = abs(pd - mm_ * z) < 1e-6
    except Exception:                                          # noqa: BLE001
        out["_check_pitch_equals_module_times_teeth"] = None
    return {"ok": True, "readback": out}


def create_external_spur_gear_report(model, spec, plane_name: str = "Front Plane") -> dict:
    """★ **建外啮合直齿轮实体**（★ 吃 dict；★ 判据是**特征树变化** —— 规则 6）。"""
    try:
        s = _gear_spec_from_dict(spec)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "spec", "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        from sw_feature_readback import feature_names as _fn
        before = _fn(model)
    except Exception:                                          # noqa: BLE001
        before = None
    try:
        r = create_external_spur_gear(model, s, plane_name=plane_name)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "create",
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:220])}
    try:
        after = _fn(model)
    except Exception:                                          # noqa: BLE001
        after = None
    new = [x for x in (after or []) if x not in (before or [])] if before is not None and after is not None else []
    return {"ok": bool(new), "plane_name": plane_name, "new_features": new[:6],
            "returned": str(r)[:80]}
