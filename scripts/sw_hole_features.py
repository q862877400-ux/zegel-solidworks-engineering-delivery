"""@brief SolidWorks 复杂孔、复合孔和半圆端槽的稳定草图切除封装。"""


from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

try:
    from .sw_connect import get_com_member
    from .sw_part import _select_com_object, extrude_cut, sketch, sketch_circle, sketch_slot
except ImportError:
    from sw_connect import get_com_member, set_com_member
    from sw_part import _select_com_object, extrude_cut, sketch, sketch_circle, sketch_slot


# ── 来源 ───────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_hole_features.py
# 定位:   本模块的证据数据类与入参校验（★ `HoleFeatureEvidence` / `_positive` / `_center`）。
# 官方依据: `ISketchManager` / `ICurve` 族（★ 见本文件各段自己的来源块）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 未在本机实测: 见各条 `limitations`。
# 覆盖:   后续同级定义
# ──────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HoleFeatureEvidence:
    """@brief 创建侧参数证据；长度统一使用米。"""

    feature_kind: str
    center_m: tuple[float, float]
    diameter_mm: float
    depth_m: float | None
    through: bool
    plane_name: str
    feature_names: tuple[str, ...]
    counterbore_diameter_mm: float | None = None
    counterbore_depth_mm: float | None = None
    countersink_diameter_mm: float | None = None
    countersink_angle_deg: float | None = None

    def to_dict(self) -> dict:
        """@brief 返回可序列化证据，并附加毫米值。"""
        value = asdict(self)
        value["center_mm"] = [round(item * 1000.0, 6) for item in self.center_m]
        for key in ("diameter_mm", "depth_mm", "counterbore_diameter_mm", "counterbore_depth_mm", "countersink_diameter_mm"):
            if value.get(key) is not None:
                value[key.replace("_m", "_mm")] = round(value[key] * 1000.0, 6)
        return value


def _positive(name: str, value: float) -> float:
    """@brief 校验正有限长度。"""
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
            raise ValueError("center 必须包含两个草图平面坐标，单位为米")
    return number


def _center(center: Sequence[float]) -> tuple[float, float]:
    """@brief 校验二维孔中心坐标。"""
    if len(center) != 2:
        raise ValueError(
            "center 必须是**两个**草图平面坐标（★ 本模块单位：**毫米**）；"
            "★ 本检查只管**维度**，不管单位"
        )
    values = (float(center[0]), float(center[1]))
    if not all(math.isfinite(value) for value in values):
        raise ValueError("center 必须是有限值")
    return values


def _feature_name(feature, fallback: str) -> str:
    """@brief 设置并回读特征名称；COM 不允许改名时返回当前名称或兜底名。"""
    if feature is None:
        raise RuntimeError(f"SolidWorks 未创建特征: {fallback}")
    try:
        feature.Name = fallback
    except Exception:
        pass
    try:
        return str(feature.Name or fallback)
    except Exception:
        return fallback


def _circle_cut(model, plane_name: str, center: tuple[float, float], diameter: float, depth: float, feature_name: str):
    """@brief 创建单个圆形草图并执行定深或贯穿切除。"""
    with sketch(model, plane_name) as sketch_name:
        segment = sketch_circle(model, center[0], center[1], diameter / 2.0)
        if segment is None:
            raise RuntimeError(f"创建圆草图失败: {feature_name}")
    feature = extrude_cut(model, sketch_name, depth)
    return _feature_name(feature, feature_name)


def _entry_point_3d(plane_name: str, center: tuple[float, float]) -> tuple[float, float, float]:
    """@brief 把标准基准面的二维坐标映射到入口平面三维点。"""
    normalized = str(plane_name).strip().lower()
    if "top" in normalized or "上视" in normalized:
        return center[0], 0.0, center[1]
    if "right" in normalized or "右视" in normalized:
        return 0.0, center[0], center[1]
    return center[0], center[1], 0.0


def _chamfer_hole_entry(model, plane_name, center, hole_diameter, countersink_diameter, half_angle_rad, feature_name):
    """@brief 选择通孔入口圆边并创建角度/距离倒角。"""
    edge = _find_hole_entry_edge(model, plane_name, center, hole_diameter / 2.0)
    model.ClearSelection2(True)
    if not _select_com_object(edge, append=False, mark=0):
        raise RuntimeError(f"选择沉头孔入口圆边失败: {feature_name}")
    radial_distance = (countersink_diameter - hole_diameter) / 2.0
    feature = model.FeatureManager.InsertFeatureChamfer(
        4, 1, radial_distance, half_angle_rad, 0.0, 0.0, 0.0, 0.0
    )
    model.ClearSelection2(True)
    return _feature_name(feature, feature_name)


def create_blind_hole(model, center, diameter, depth, plane_name="Front Plane", name="盲孔") -> dict:
    """@brief 创建定深盲孔，并返回创建参数证据。"""
    center = _center(center)
    diameter = _positive("diameter", diameter)
    depth = _positive("depth", depth)
    feature_name = _circle_cut(model, plane_name, center, diameter, depth, name)
    return HoleFeatureEvidence("blind", center, diameter, depth, False, plane_name, (feature_name,)).to_dict()


def create_through_hole(model, center, diameter, plane_name="Front Plane", name="通孔") -> dict:
    """@brief 创建完全贯穿圆孔，并返回创建参数证据。"""
    center = _center(center)
    diameter = _positive("diameter", diameter)
    feature_name = _circle_cut(model, plane_name, center, diameter, 0.0, name)
    return HoleFeatureEvidence("through", center, diameter, None, True, plane_name, (feature_name,)).to_dict()


def create_counterbore_hole(
    model,
    center,
    hole_diameter,
    counterbore_diameter,
    counterbore_depth,
    plane_name="Front Plane",
    name="沉孔",
) -> dict:
    """@brief 创建通孔加同轴圆柱沉孔的两级复合孔。"""
    center = _center(center)
    hole_diameter = _positive("hole_diameter", hole_diameter)
    counterbore_diameter = _positive("counterbore_diameter", counterbore_diameter)
    counterbore_depth = _positive("counterbore_depth", counterbore_depth)
    if counterbore_diameter <= hole_diameter:
        raise ValueError("counterbore_diameter 必须大于 hole_diameter")
    through_name = _circle_cut(model, plane_name, center, hole_diameter, 0.0, f"{name}_通孔")
    recess_name = _circle_cut(model, plane_name, center, counterbore_diameter, counterbore_depth, f"{name}_沉孔")
    return HoleFeatureEvidence(
        "counterbore", center, hole_diameter, None, True, plane_name, (through_name, recess_name),
        counterbore_diameter_mm=counterbore_diameter,
        counterbore_depth_mm=counterbore_depth,
    ).to_dict()


def create_countersink_hole(
    model,
    center,
    hole_diameter,
    countersink_diameter,
    included_angle_deg=90.0,
    plane_name="Front Plane",
    name="沉头孔",
) -> dict:
    """@brief 创建通孔加锥形沉头；角度为沉头包含角。"""
    center = _center(center)
    hole_diameter = _positive("hole_diameter", hole_diameter)
    countersink_diameter = _positive("countersink_diameter", countersink_diameter)
    angle = float(included_angle_deg)
    if countersink_diameter <= hole_diameter:
        raise ValueError("countersink_diameter 必须大于 hole_diameter")
    if not math.isfinite(angle) or not 10.0 <= angle < 170.0:
        raise ValueError("included_angle_deg 必须在 [10, 170) 范围内")
    half_angle = math.radians(angle / 2.0)
    through_name = _circle_cut(model, plane_name, center, hole_diameter, 0.0, f"{name}_通孔")
    sink_name = _chamfer_hole_entry(
        model, plane_name, center, hole_diameter, countersink_diameter, half_angle, f"{name}_锥面"
    )
    return HoleFeatureEvidence(
        "countersink", center, hole_diameter, None, True, plane_name, (through_name, sink_name),
        countersink_diameter_mm=countersink_diameter,
        countersink_angle_deg=angle,
    ).to_dict()


def create_semicircular_slot(
    model,
    start,
    end,
    width,
    depth=0.0,
    plane_name="Front Plane",
    name="半圆端槽",
) -> dict:
    """@brief 创建两端为半圆的直槽；depth=0 表示贯穿。"""
    start = _center(start)
    end = _center(end)
    width = _positive("width", width)
    depth = 0.0 if float(depth) == 0.0 else _positive("depth", depth)
    if math.dist(start, end) <= 1e-12:
        raise ValueError("槽起点和终点不能重合")
    with sketch(model, plane_name) as sketch_name:
        segments = sketch_slot(model, start[0], start[1], end[0], end[1], width / 2.0)
        if segments is None:
            raise RuntimeError(f"创建半圆端槽草图失败: {name}")
    feature_name = _feature_name(extrude_cut(model, sketch_name, depth), name)
    return {
        "feature_kind": "semicircular_slot",
        "start_mm": list(start),
        "end_mm": list(end),
        "start_mm": [round(value * 1000.0, 6) for value in start],
        "end_mm": [round(value * 1000.0, 6) for value in end],
        "width_mm": width,
        "width_mm": round(width * 1000.0, 6),
        "depth_mm": None if depth == 0.0 else depth,
        "depth_mm": None if depth == 0.0 else round(depth * 1000.0, 6),
        "through": depth == 0.0,
        "plane_name": plane_name,
        "feature_names": [feature_name],
    }


def create_hole_pattern(model, positions: Iterable[Sequence[float]], creator, **kwargs) -> list[dict]:
    """@brief 按显式孔位逐个创建孔；creator 为本模块任一孔创建函数。"""
    evidence = []
    for index, position in enumerate(positions, start=1):
        item_kwargs = dict(kwargs)
        base_name = str(item_kwargs.pop("name", "孔"))
        evidence.append(creator(model, position, name=f"{base_name}_{index}", **item_kwargs))
    if not evidence:
        raise ValueError("positions 至少包含一个孔位")
    return evidence


# ══════════════════════════════════════════════════════════════════════
# 补齐此前未触及的 3 个孔与螺纹接口族
# （见 docs/family-coverage.md；本文件原有 8/11）
# ══════════════════════════════════════════════════════════════════════


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_hole_features.py —— 「紧固件链路」这一段（轮 125）。
# 定位:   把 `get_fastener_types` / `get_fastener_table_types` / `get_fastener_table`
#         三个包装接成可用的高层入口（它们此前同样**没有调用方**）。
#         链路：标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Boolean GetFastenerTypes(String, Object&, Object&)` ·
#             `Boolean GetFastenerTableTypes(String, Int32, Object&)` ·
#             `Boolean GetFastenerTable(String, Int32, Int32, out Object)`
#           ② `C:\swapi\types\IHoleStandardsData\GetFastenerTable.md`
#             （第 4 参是 `out System.object HoleTable`，类型 `[[IHoleDataTable]]`）
#           ③ ★ **必须热身的约束**是**真机查出**的，官方**未写**
#             （`_probe_fastener_ordering.py` 四组对照 A/B/C/D）
#           ④ ★ 出参读回来是 `tuple`、两组一一对应（`tools/verify_hole_standards_smoke.py` 11/11）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本段与文件里**已有**的来源块交错，用「后续同级定义」会被
#         下一个来源块截断（**轮 125 实测踩到**）⇒ 这里用「全文件」以保证覆盖。
# ─────────────────────────────────────────────────────────────────────

def list_fastener_types(sw, standard_name: str, hole_type_id: int = 0):
    """列出某孔标准下的**紧固件类型**（官方 `IHoleStandardsData.GetFastenerTypes`）。

    ★ 真机量到：出参是两组**各 14 元**的 `tuple` —— 一个是 **ID**、一个是**名称**，
    **一一对应**。⚠ **名称随 UI 语言变**（本机中文 UI ⇒ 拿到 `'六角精致螺栓'` 这样的中文）。

    :param standard_name: 孔标准名，取自 `list_hole_standards()` 的 `name`
        （例 `'ANSI Inch'` / `'ISO'`）。
    :returns: `[{"id": int, "name": str}, …]`。
    :raises RuntimeError: 拿不到 `IHoleStandardsData`，或官方返回 `False`。
    """
    data = _hole_standards_data(sw, hole_type_id)
    ids, names = _out_container(), _out_container()
    ok = get_com_member(data, "GetFastenerTypes", str(standard_name), ids, names)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTypes(%r) 返回 False —— "
            "常见原因：标准名拼错（用 `list_hole_standards()` 里的 `name`）" % standard_name
        )
    return _pair(ids, names, "FastenerTypes")


def list_fastener_table_types(sw, standard_name: str, fastener_id: int,
                              hole_type_id: int = 0):
    """列出某紧固件的**表类型 ID**（官方 `IHoleStandardsData.GetFastenerTableTypes`）。

    ⚠ **官方第 2 参是 `Int32`（紧固件 ID），不是尺寸名** ——
    真机第一版就栽在这（传尺寸名 ⇒ 「类型不匹配」，位置 2）。
    紧固件 ID 取自 `list_fastener_types()` 的 `id`。

    :returns: `[int, …]`（本机实测：`GetFastenerTableTypes('ANSI Inch', 4)` ⇒ `[0, 1, 2]`）。
    :raises RuntimeError: 拿不到数据、或官方返回 `False`。
    """
    data = _hole_standards_data(sw, hole_type_id)
    out = _out_container()
    ok = get_com_member(data, "GetFastenerTableTypes", str(standard_name),
                        int(fastener_id), out)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTableTypes(%r, %r) 返回 False —— "
            "常见原因：`fastener_id` 不在 `list_fastener_types()` 返回的 id 里"
            % (standard_name, fastener_id)
        )
    return _as_list(out)


def get_fastener_table(sw, standard_name: str, fastener_id: int, table_id: int,
                       hole_type_id: int = 0):
    """取某紧固件的**孔表本体**（官方 `IHoleStandardsData.GetFastenerTable`）。

    ⚠⚠ **本函数当前「不可用」（2026-10-01 轮 125 真机实测）** ——
    官方签名 `Boolean GetFastenerTable(String StandardName, Int32 FastenerID,
    Int32 TableID, **out Object** HoleTable)`，第 4 参是 `out IHoleDataTable`。
    用**同一套**已经验过的容器形态 `VARIANT(VT_BYREF|VT_VARIANT, None)` 传：
    ```
    GetFastenerTable('ANSI Inch', 4, 0) ⇒ com_error -2147352571「类型不匹配」**位置 4**
    GetFastenerTable('ANSI Inch', 4, 1) ⇒ 同上
    GetFastenerTable('ANSI Inch', 4, 2) ⇒ 同上
    ```
    ★ **同族的另外三个成员用同一形态都通**（`GetHoleStandards` / `GetFastenerTypes` /
    `GetFastenerTableTypes`）⇒ **只有这一个到不了**。
    ⚠ **按事实 53 停手**（不再变着法试）；保留本函数作**可复算的证据**。

    :raises RuntimeError: 取不到表（当前必然）。
    """
    data = _hole_standards_data(sw, hole_type_id)
    out = _out_container()
    ok = get_com_member(data, "GetFastenerTable", str(standard_name),
                        int(fastener_id), int(table_id), out)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetFastenerTable(%r, %r, %r) 返回 False —— "
            "⚠ 真机实测该成员**在 pywin32 后台上报「类型不匹配（位置 4）」**，"
            "属同族里唯一到不了的一个（见模块来源块与已知事实）"
            % (standard_name, fastener_id, table_id)
        )
    return _out_value(out)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_hole_features.py —— 「把孤儿包装接成可用 API」这一段。
# 定位:   2026-10-01（轮 124）补：`get_hole_standards` 等 4 个包装**在仓库里没有调用方**
#         （它们把出参甩给调用方）⇒ 本节提供自己造容器、自己读回来的高层入口。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Object GetHoleStandardsData(Int32)`（在 `ISldWorks` 上）
#             `Boolean GetHoleStandards(Object&, Object&)`（在 `IHoleStandardsData` 上）
#           ② `C:\swapi\types\ISldWorks\GetHoleStandardsData.md`
#             （`HoleTypeID` 取自 `swWzdGeneralHoleTypes_e`；**= 5 `swWzdLegacy` 时返回 null**）
#           ③ `C:\swapi\types\IHoleStandardsData\GetHoleStandards.md`
#           ④ ★ **出参传法**取自真机裁断（已知事实 68，
#             `tools/probe_outparam_object_byref.py`）：只有 `VT_BYREF|VT_VARIANT` 可用。
#           ⑤ ★ **出参读回来是 tuple**：真机量到两组各 15 元、**一一对应**
#             （`tools/verify_hole_standards_smoke.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `_out_container` / `_out_value` / `_as_list` /
#         `list_hole_standards` 四个单元。
# ─────────────────────────────────────────────────────────────────────

# ── 可用入口：把"孤儿包装"接成能用的 API（2026-10-01 轮 124）──────────
#
# ⚑ **为什么加这一段**：`get_hole_standards` 等 4 个包装**在仓库里没有调用方** ——
#   它们把**出参甩给调用方**，而调用方得自己造 by-ref VARIANT，**没人愿意这么用**。
#   ⇒ 本节提供「**自己造容器、自己读回来**」的高层入口，**调用方只拿结果**。
#
# ★★ **出参的正确传法**（真机裁断，见已知事实 68）：
#     裸 `None` / `VARIANT(VT_BYREF|VT_DISPATCH, None)` 都报「类型不匹配」
#     **`VARIANT(VT_BYREF|VT_VARIANT, None)` 才行**
#
# ★★ **读回来是 `tuple`**（真机量到）：
#     `GetHoleStandards` 的两个出参各是一个 **15 元的 tuple** ——
#     一个是 ID（`(0, 1, 16, …)`）、一个是名称（`('ANSI Inch', 'ANSI Metric', …)`），
#     **一一对应**。⇒ 本节的入口把它们配对成 `[{id, name}, …]`。

def _out_container():
    """造一个**容器出参**（`Object&` / `Variant&` 用）。

    ★ 真机裁断：`VARIANT(VT_BYREF|VT_VARIANT, None)` 是唯一能用的形态
    （裸 `None` 与 `VT_BYREF|VT_DISPATCH` 都报「类型不匹配」，见已知事实 68）。
    """
    import pythoncom
    from win32com.client import VARIANT
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def _out_value(v):
    """从容器出参里**把值读出来**（真机量到的是 `tuple`）。

    ⚠ 用 `try/except AttributeError` 而不是 `hasattr` —— 后者的属性描述符
    在某些 COM 对象上会**掩盖真实异常**。
    """
    try:
        return v.value
    except AttributeError:
        return None


def _as_list(v):
    """把出参的值规整成 `list`（`None` → `[]`；标量 → 单元素表）。"""
    val = _out_value(v)
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return list(val)
    return [val]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_hole_features.py —— 「紧固件链路」这一段（轮 125）。
# 定位:   把 `get_fastener_types` / `get_fastener_table_types` / `get_fastener_table`
#         三个包装接成可用的高层入口（它们此前同样**没有调用方**）。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Object GetHoleStandardsData(Int32)` ·
#             `Boolean GetFastenerTypes(String, Object&, Object&)` ·
#             `Boolean GetFastenerTableTypes(String, Int32, Object&)` ·
#             `Boolean GetFastenerTable(String, Int32, Int32, out Object)`
#           ② `C:\swapi\types\IHoleStandardsData\GetFastenerTable.md`
#             （正式签名里第 4 参是 `out System.object HoleTable`，类型是 `[[IHoleDataTable]]`）
#           ③ ★ **必须热身的约束**是本轮**真机查出**的，官方**未写**
#             （`_probe_fastener_ordering.py` 四组对照 A/B/C/D）。
#           ④ ★ 出参读回来是 `tuple`、两组一一对应（`tools/verify_hole_standards_smoke.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `_hole_standards_data` / `_pair` /
#         `list_fastener_types` / `list_fastener_table_types` / `get_fastener_table` 五个单元。
# ─────────────────────────────────────────────────────────────────────

def _hole_standards_data(sw, hole_type_id: int, *, initialize: bool = True):
    """取 **并初始化** `IHoleStandardsData`（官方 `ISldWorks.GetHoleStandardsData`）。

    ⚑⚑ **2026-10-01（轮 125）真机查出的行为约束：这个对象必须"先热身"。**
    拿到它之后**直接**调 `GetFastenerTypes` ⇒ **返回 `False`**；
    **先调一次 `GetHoleStandards`** 再调 ⇒ **返回 `True`**。
    实测排除了两种替代解释（同一个未热身对象**再调也不会变 True**；换个标准名也一样）。
    ⇒ ★ 所以本函数默认**顺手调一次 `GetHoleStandards` 当初始化**，
    让后面几个查询成员**不必各自记住这个顺序**。
    ⚠ 官方文档**没有**写这个约束（它只写了各方法自己的前置）。

    :param initialize: 默认 `True`；`False` 时只取不热身（给"只想列标准"的调用方省一次调用）。
    :raises RuntimeError: 返回 `None` —— 官方写明 **HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    """
    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
    if data is None:
        raise RuntimeError(
            "ISldWorks.GetHoleStandardsData(%r) 返回 None ⇒ 拿不到 IHoleStandardsData。"
            "官方写明：**HoleTypeID = 5（swWzdLegacy）时返回 null**。" % hole_type_id
        )
    if initialize:
        # ⚑ 真机查出的热身步骤（见 docstring）；⚠ 结果丢弃，只是为了让对象进入可用状态
        get_com_member(data, "GetHoleStandards", _out_container(), _out_container())
    return data


def _pair(ids_v, names_v, what: str):
    """把**两个出参**按位配成 `[{"id", "name"}, …]`。

    ⚠ 长度不一致时**抛** —— 不静默截断、不猜配对（铁律 5）。
    """
    a, b = _as_list(ids_v), _as_list(names_v)
    if len(a) != len(b):
        raise RuntimeError(
            "%s 的两个出参长度不一致（%d vs %d）⇒ 无法按位配对，**不猜**" % (what, len(a), len(b))
        )
    return [{"id": i, "name": str(n)} for i, n in zip(a, b)]



def list_hole_standards(sw, hole_type_id: int = 0):
    """列出某类孔向导孔可用的**孔标准**（官方 `ISldWorks.GetHoleStandardsData` +
    `IHoleStandardsData.GetHoleStandards`）。

    :param sw: `ISldWorks` 对象。
    :param hole_type_id: `swWzdGeneralHoleTypes_e`；⚠ 官方写明
        **HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    :returns: `[{"id": int, "name": str}, …]`（两组出参**按位配对**）。
    :raises RuntimeError: 拿不到 `IHoleStandardsData`，或官方返回 `False`。
    """
    data = _hole_standards_data(sw, hole_type_id)
    ids, names = _out_container(), _out_container()
    ok = get_com_member(data, "GetHoleStandards", ids, names)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetHoleStandards 返回 False（失败）—— "
            "两个出参必须是 `VARIANT(VT_BYREF|VT_VARIANT, None)`"
        )
    return _pair(ids, names, "GetHoleStandards")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IStraightTapElementData 段 + ITaperedTapElementData 段
# 定位:   攻丝（Tap）参数。官方签名（**全部是属性**，get/set 成对，无方法）：
#     IStraightTapElementData : Int32   CustomSizing / EndShape / Equation /
#                                       ThreadClass
#                                : Boolean DrillPointAngleOverride /
#                                       ThreadClassOverride
#                                : Double DrillPointAngle
#     ITaperedTapElementData  : Int32   CustomSizing / ThreadClass
#                                : Boolean EndConditionOverride /
#                                       ThreadClassOverride / UseStandardDepth
# ⚠ 这些属性挂在**已建好的攻丝特征**上，本模块只做装配、不提供创建。
# ⚠ CustomSizing / EndShape / Equation / ThreadClass 的枚举取值在两套官方源里
#   都查不到（sw_know 检索无对应枚举定义），故只做 int 透传、不设默认值。
# 覆盖:   后续同级定义 —— 本块文档化 configure_straight_tap 与
#         configure_tapered_tap 两个函数（同一个接口族的直/锥两面），
#         覆盖到下一个来源块为止。
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_straight_tap(
    element,
    *,
    custom_sizing: int | None = None,
    end_shape: int | None = None,
    equation: int | None = None,
    thread_class: int | None = None,
    thread_class_override: bool | None = None,
    drill_point_angle: float | None = None,
    drill_point_angle_override: bool | None = None,
):
    """装配 ``IStraightTapElementData``（直螺纹攻丝参数），返回同一对象。"""
    if element is None:
        raise ValueError("element 为 None：须先取得攻丝元素数据")
    # 显式逐项赋值而非 mapping 循环：循环里的属性名是变量，
    # 静态签名审计（audit_call_arity.py）无法归因，会让这 3 个族在
    # docs/family-coverage.md 里显示为「未触及」。显式写同时也更好读。
    if custom_sizing is not None:
        set_com_member(element, "CustomSizing", int(custom_sizing))
    if end_shape is not None:
        set_com_member(element, "EndShape", int(end_shape))
    if equation is not None:
        set_com_member(element, "Equation", int(equation))
    if thread_class is not None:
        set_com_member(element, "ThreadClass", int(thread_class))
    if thread_class_override is not None:
        set_com_member(element, "ThreadClassOverride", bool(thread_class_override))
    if drill_point_angle is not None:
        set_com_member(element, "DrillPointAngle", float(drill_point_angle))
    if drill_point_angle_override is not None:
        set_com_member(element, "DrillPointAngleOverride",
                       bool(drill_point_angle_override))
    return element


def configure_tapered_tap(
    element,
    *,
    custom_sizing: int | None = None,
    thread_class: int | None = None,
    thread_class_override: bool | None = None,
    end_condition_override: bool | None = None,
    use_standard_depth: bool | None = None,
):
    """装配 ``ITaperedTapElementData``（锥螺纹攻丝参数），返回同一对象。"""
    if element is None:
        raise ValueError("element 为 None：须先取得锥螺纹攻丝元素数据")
    # 显式逐项赋值，原因同 configure_straight_tap（见上方注释）
    if custom_sizing is not None:
        set_com_member(element, "CustomSizing", int(custom_sizing))
    if thread_class is not None:
        set_com_member(element, "ThreadClass", int(thread_class))
    if thread_class_override is not None:
        set_com_member(element, "ThreadClassOverride", bool(thread_class_override))
    if end_condition_override is not None:
        set_com_member(element, "EndConditionOverride", bool(end_condition_override))
    if use_standard_depth is not None:
        set_com_member(element, "UseStandardDepth", bool(use_standard_depth))
    return element


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IHoleStandardsData 段
# 定位:   孔标准查询。官方签名（**全部是方法**，均带 by-ref 出参）：
#             Boolean GetHoleStandards(Object& Standards, Object& Types)
#             Boolean GetFastenerTypes(String, Object& Types, Object& Sizes)
#             Boolean GetFastenerTableTypes(String, Int32, Object& TableTypes)
#             Boolean GetFastenerTable(String, Int32, Int32, Object& TableData)
# ⚠ 4 个方法的末位都是 by-ref 出参，pywin32 迟到绑定下**不保证回写**
#   （与 AGENTS.md §六 事实 8 记载的 ISelectionMgr bool 返回值不可信同源）。
#   故本函数**只透传返回值、不据此判定查询成功**，也不代为分配输出对象 ——
#   by-ref VARIANT 的分配规则在两套官方源里都查不到，不臆造。
# 覆盖:   后续同级定义 —— 本块文档化方法名常量与 query_hole_standards 两个单元。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
HOLE_STANDARDS_METHODS = (
    "GetHoleStandards",
    "GetFastenerTypes",
    "GetFastenerTableTypes",
    "GetFastenerTable",
)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本文件上方同一接口族的签名来源块
# 定位:   IHoleStandardsData 的 4 个查询方法，**逐个显式封装**。
#         初稿用 `method` 变量分发（getattr 式），成员名不是字符串字面量，
#         静态审计与 family-coverage 都无法归因 ⇒ 那一族会一直显示「未触及」
#         （代码写了但工具看不见）。显式封装同时更好读、更易核对。
# ⚠ 4 个方法的末位都是 by-ref 出参，**本模块只透传返回值**，
#   不判断查询是否成功，也不代为分配输出缓冲（规则查不到，不臆造）。
# 覆盖:   后续同级定义 —— 本块文档化 4 个查询函数单元。
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_hole_standards(standards_data, standards_out, types_out):
    """``Boolean GetHoleStandards(Object& Standards, Object& Types)``"""
    if standards_data is None:
        raise ValueError("standards_data 为 None：须先取得 IHoleStandardsData")
    return get_com_member(standards_data, "GetHoleStandards",
                          standards_out, types_out)


def get_fastener_types(standards_data, table_name, types_out, sizes_out):
    """``Boolean GetFastenerTypes(String, Object& Types, Object& Sizes)``"""
    if standards_data is None:
        raise ValueError("standards_data 为 None")
    return get_com_member(standards_data, "GetFastenerTypes",
                          str(table_name), types_out, sizes_out)


def get_fastener_table_types(standards_data, table_name, size, table_types_out):
    """``Boolean GetFastenerTableTypes(String, Int32, Object& TableTypes)``"""
    if standards_data is None:
        raise ValueError("standards_data 为 None")
    return get_com_member(standards_data, "GetFastenerTableTypes",
                          str(table_name), int(size), table_types_out)


def get_fastener_table(standards_data, table_name, size, kind, table_data_out):
    """``Boolean GetFastenerTable(String, Int32, Int32, Object& TableData)``"""
    if standards_data is None:
        raise ValueError("standards_data 为 None")
    return get_com_member(standards_data, "GetFastenerTable",
                          str(table_name), int(size), int(kind), table_data_out)


# ── 24h 计划 段 4 续（Spec Kit `151`）：**声明式建孔**（★ 规则 3 的精神）──────────────
# ★★★★ 为什么要有这一族（★ 而它比"把既有函数挂上去"更好）：
#   · 能力层既有的 `create_through_hole(model, center, ...)` 吃 **`center`（坐标元组）**；
#   · ★ 而**上游**的统一建孔工具 `solidworks_create_hole_feature`（`mcp-server/server.py` L2244）
#     吃的是 **`center_x_mm` / `center_y_mm`** —— ★★ **那是**裸坐标参数名****（规则 3 的**字面**红线）。
#   ⇒ ★★★ **所以本族是"规则 3 合规版"**：★ **只吃声明式 `selection`**，★ **内部用
#     `sw_selection_spec.selection_point` 从选区读点** ⇒ ★ **工具参数里没有坐标**。
#   ★ 而单位已由真机对照实验定死（★ 轮 267：`GetSelectionPoint2` 回的是**毫米**）。
#
# ★ 覆盖 5 种（★ 与能力层既有的一一对应）：通孔 · 盲孔 · 沉头孔 · 锥沉孔 · 半圆端槽。
# ⚠ **判据**：★ 每个包装都回**能力层既有的** `HoleFeatureEvidence`（★ 它本来就是回读证据）——
#   ★ 再套一层"选区点的坐标"（★ 于是调用方能看出**它建在哪个点上**）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_hole_features.py —— 本段
# 定位:   段 4 的"声明式建孔"（★ 规则 3 合规版，替代上游的裸坐标入口）。
# 官方依据: `IModelDoc2.HoleWizard5` 族（★ 既有函数的来源块）·
#          `ISelectionMgr.GetSelectionPoint2(Index, Mark)`（★ 读点，Index 从 1 起）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 5 个包装 + 1 个助手
# ─────────────────────────────────────────────────────────────────────────────


def _point_from_selection(model, selection: str):
    """★ **按声明式选择选点并读它的坐标**（毫米）—— 本族所有包装的前置。

    ★ 用法：★ `selection` 传 `index:N`（选第 N 个可选实体）或 `__current_selection__`
      （★ 用界面上已选好的）。★ **不传坐标**（★ 规则 3）。
    ⇒ 返回 `(point_tuple, err)`：★ 成功时 `err is None`。
    """
    try:
        from .sw_selection_spec import resolve_selection, selection_point
    except ImportError:                                        # pragma: no cover
        from sw_selection_spec import resolve_selection, selection_point
    if str(selection) == "__current_selection__":
        #: ★ 已选好的直接用（★ 与 `sw_part._ensure_sketch_selected` 同约定）
        pass
    else:
        #: ★★★ 2026-10-01 轮 268 真机实测：★ **必须优先选**面（FACE）**** ——
        #:   · 选**面**时 `GetSelectionPoint2(1, -1)` **成功**（★ 轮 266/267 两次拿到点，
        #:     且三点对照把单位定死为**毫米**）；
        #:   · 而选 **VERTEX / EDGE** 时它报 **`(-2147352562, '无效的参数数目。')`**
        #:     （★ `DISP_E_BADPARAMCOUNT`）—— ★★ 而那**不是**"签名有两个参数"错了，
        #:     是**该对象类型下这个重载不吃那两个参数**（★ 与事实 47 同族：★ 对象类型决定可达性）。
        #:   ⇒ ★ 所以本助手**按面优先**试，★ 每次失败**记下来**（★ 便于下一步收敛）。
        errs = []
        for _kind in ("FACE", "EDGE", "VERTEX"):
            try:
                resolve_selection(model, str(selection), _kind)
                break
            except Exception as exc:                           # noqa: BLE001
                errs.append("%s:%s" % (_kind, str(exc)[:60]))
        else:
            return None, "选择 %r 三种类型都失败：%s" % (selection, " | ".join(errs)[:200])
    r = selection_point(model)
    if not r.get("ok"):
        return None, "读不到点：%s" % str(r.get("error"))[:150]
    pt = tuple(r["point_mm"])
    #: ★★★★ 2026-10-01 轮 268：**两处换算都在这里做（这就是规则 2 说的"边界"）**：
    #:   ① ★ **降维** —— `_center` 的实现**只检查长度是 2**（★ 而它的报错信息写"单位为米"，
    #:      ★★ **那误导了我一轮**：真因是**维度**，★ 不是单位）；
    #:   ② ★ **单位** —— 建孔函数的 `center` 要**米**（★ `sw_connect.mm()` 的 docstring 写明
    #:      「毫米转米（SolidWorks API 单位）」），★ 而 `selection_point` 回的经三点对照
    #:      确证是**毫米**（★ 轮 267）。
    #:   ⇒ ★ 所以：★ `selection_point`（毫米，3 维） ⇒ **`mm()` + 取前两维** ⇒ `center`（米，2 维）。
    #: ★★★★★ 2026-10-01（轮 298）**真机推翻了上面那段注释（而它是一个**真 bug**）**：
    #:   旧注释写「**建孔函数的 `center` 要**米**」⇒ 于是本函数用 `mm()` 换算。
    #:   ★★ 而真机证据：★ **用毫米调 `create_countersink_hole` ⇒ 2/2 PASS**
    #:     （树 7→10 · 10→13）；★ 用米调 ⇒ 报「创建圆草图失败」
    #:     （★ 因为它变成了**亚微米圆**）。
    #:   ★ 而链条是：`_circle_cut` ⇒ `sketch_circle(model, center[0], center[1], diameter/2)`
    #:     ⇒ ★ **`sketch_circle` 是 `sw_part` 的**，而那个模块的单位**就是毫米**
    #:     （★ 它自己的 docstring 明写）⇒ ★★ **所以整条链都是毫米**。
    #:   ⇒ ★★★ **修法：去掉 `mm()`，直接回毫米**。
    #:   ⚠ 而这个错之前**没被发现**，是因为 `through`/`blind`/`counterbore`
    #:     恰好在**亚微米尺度上也能建出来** ⇒ ★★ **它们同样错，只是没暴露**。
    center = (float(pt[0]), float(pt[1]))
    return center, None


def create_through_hole_at_selection_report(model, selection: str, diameter_mm: float,
                                            plane_name: str = "Front Plane",
                                            name: str = "通孔") -> dict:
    """★ **声明式建通孔**：★ 从 `selection` 读点 ⇒ 建完全贯穿圆孔 ⇒ 回**回读证据 + 用的那个点**。

    ★★ 与 `create_through_hole` 的**唯一区别**：★ **它不要坐标**（★ 规则 3）。
    """
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "through", "selection": str(selection), "error": err}
    ev = create_through_hole(model, pt, diameter_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "center_sent_mm": list(pt), "★_units": "从选区读到毫米 ⇒ 换算成米 ⇒ 取前两维（规则 2 的边界）",
                "★": "点来自**声明式选择**（不是调用方传坐标）—— 规则 3"})
    return out


def create_blind_hole_at_selection_report(model, selection: str, diameter_mm: float, depth_mm: float,
                                          plane_name: str = "Front Plane",
                                          name: str = "盲孔") -> dict:
    """★ **声明式建盲孔**（★ 吃 `selection` 与 `depth_mm`，★ 不要坐标）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "blind", "selection": str(selection), "error": err}
    ev = create_blind_hole(model, pt, diameter_mm, depth_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_counterbore_hole_at_selection_report(model, selection: str, hole_diameter_mm: float,
                                               counterbore_diameter_mm: float,
                                               counterbore_depth_mm: float,
                                               plane_name: str = "Front Plane",
                                               name: str = "沉头孔") -> dict:
    """★ **声明式建沉头孔**（★ 不要坐标）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "counterbore", "selection": str(selection), "error": err}
    ev = create_counterbore_hole(model, pt, hole_diameter_mm, counterbore_diameter_mm,
                                 counterbore_depth_mm, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_countersink_hole_at_selection_report(model, selection: str, hole_diameter_mm: float,
                                               countersink_diameter_mm: float,
                                               included_angle_deg: float = 90.0,
                                               plane_name: str = "Front Plane",
                                               name: str = "锥沉孔") -> dict:
    """★ **声明式建锥沉孔**（★ 不要坐标；★ 角度参数带 `_deg`，规则 2）。"""
    pt, err = _point_from_selection(model, selection)
    if err:
        return {"ok": False, "kind": "countersink", "selection": str(selection), "error": err}
    ev = create_countersink_hole(model, pt, hole_diameter_mm, countersink_diameter_mm,
                                 included_angle_deg, plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "selection": str(selection), "point_from_selection_mm": list(pt),
                "★": "点来自**声明式选择** —— 规则 3"})
    return out


def create_semicircular_slot_at_selection_report(model, start_selection: str, end_selection: str,
                                                width_mm: float, depth_mm: float = 0.0,
                                                plane_name: str = "Front Plane",
                                                name: str = "半圆端槽") -> dict:
    """★ **声明式建半圆端槽**：★ **两端各用一次声明式选择**（★ 于是**两个点都不是坐标参数**）。"""
    pts = []
    for sel in (start_selection, end_selection):
        pt, err = _point_from_selection(model, sel)
        if err:
            return {"ok": False, "kind": "semicircular_slot", "selection": str(sel), "error": err}
        pts.append(pt)
    ev = create_semicircular_slot(model, pts[0], pts[1], width_mm, depth_mm,
                                  plane_name=plane_name, name=name)
    out = dict(ev) if isinstance(ev, dict) else {"evidence": ev}
    out.update({"ok": True, "start_selection": str(start_selection),
                "end_selection": str(end_selection),
                "centers_sent_mm": [list(p) for p in pts], "★_units": "同族：毫米 ⇒ 米 + 取前两维",
                "★": "两个点都来自**声明式选择** —— 规则 3"})
    return out


# ── 24h 计划 段 4 续（Spec Kit `163`）：**让"找不到入口圆边"的失败可见** ──────────────
# ★★★★★ 2026-10-01（轮 297）真凶：`_find_hole_entry_edge` 用 `except Exception: continue`
#   **把"断在哪一环"吞掉了** —— ★ 于是真机上只看到一句
#   「无法按圆心和半径找到沉头孔入口圆边」，★ **而看不出**是
#   ① `GetBodies2` 空 · ② `GetFaces` 空 · ③ `GetEdges` 空 · ④ `GetCurve` 空 ·
#   ⑤ `IsCircle` 假 · ⑥ `CircleParams` 不足 7 个 · ⑦ 半径不匹配 —— **七种可能之一**。
#   ⇒ ★★ 这正是本项目一贯要防的"静默吞错"（事实 185/187/198 一族）。
#
# ★ 判据：★ **不改判定逻辑**（★ 仍然找同一条边、仍然用同样的容差），
#   ★★ **只把每一环的计数与第一个异常记下来**，★ 并在失败时**回一个带诊断的 `RuntimeError`**。
#   ⇒ ★ **于是"下一次"能一眼看出断在哪**（★ 而不是再猜一轮）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_hole_features.py —— 本段
# 定位:   段 4 续：把 `_find_hole_entry_edge` 的静默吞错改成**带诊断的失败**。
# 官方依据: `IBody2.GetFaces` · `IFace2.GetEdges` · `IEdge.GetCurve` ·
#          `ICurve.IsCircle` / `ICurve.CircleParams`（★ 见 `scripts/sw_hole_features.py` 既有来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────


def _find_hole_entry_edge(model, plane_name: str, center: tuple[float, float], radius: float,
                          tolerance: float = 1e-6):
    """★ **按圆心和半径寻找通孔在草图基准面一侧的圆边**（★ 带**逐环诊断**的版本）。

    ★★ 与旧版的差别**只在失败路径**：★ 旧版 `except Exception: continue` 把原因吞了，
    于是失败时只有一句"找不到"；本版**记下每环的计数与第一个异常**，
    并在失败时把它们放进 `RuntimeError`（★ **判定逻辑一字未改**）。
    """
    target = _entry_point_3d(plane_name, center)
    diag = {"bodies": 0, "faces": 0, "edges": 0, "curves": 0, "circles": 0,
            "params_ok": 0, "first_error": None}
    candidates = []

    def _note(stage, exc):
        if diag["first_error"] is None:
            diag["first_error"] = "%s: %s: %s" % (stage, type(exc).__name__, str(exc)[:160])

    try:
        bodies = list(get_com_member(model, "GetBodies2", 0, False) or [])
    except Exception as exc:                                   # noqa: BLE001
        _note("GetBodies2", exc)
        bodies = []
    diag["bodies"] = len(bodies)
    for body in bodies:
        try:
            faces = list(get_com_member(body, "GetFaces") or [])
        except Exception as exc:                               # noqa: BLE001
            _note("GetFaces", exc)
            continue
        diag["faces"] += len(faces)
        for face in faces:
            try:
                edges = list(get_com_member(face, "GetEdges") or [])
            except Exception as exc:                           # noqa: BLE001
                _note("GetEdges", exc)
                continue
            diag["edges"] += len(edges)
            for edge in edges:
                try:
                    curve = get_com_member(edge, "GetCurve")
                except Exception as exc:                       # noqa: BLE001
                    _note("GetCurve", exc)
                    continue
                if curve is None:
                    continue
                diag["curves"] += 1
                try:
                    if not bool(get_com_member(curve, "IsCircle")):
                        continue
                except Exception as exc:                       # noqa: BLE001
                    _note("IsCircle", exc)
                    continue
                diag["circles"] += 1
                try:
                    params = list(get_com_member(curve, "CircleParams") or [])
                except Exception as exc:                       # noqa: BLE001
                    _note("CircleParams", exc)
                    continue
                if len(params) < 7:
                    continue
                try:
                    if abs(float(params[6]) - radius) > tolerance:
                        continue
                except Exception as exc:                       # noqa: BLE001
                    _note("params[6]", exc)
                    continue
                diag["params_ok"] += 1
                try:
                    distance = math.dist([float(value) for value in params[:3]], target)
                except Exception as exc:                       # noqa: BLE001
                    _note("math.dist", exc)
                    continue
                candidates.append((distance, edge))
    if not candidates:
        raise RuntimeError(
            "无法按圆心和半径找到沉头孔入口圆边 —— ★ 逐环诊断（★ 判定逻辑未改，只加诊断）："
            "bodies=%d · faces=%d · edges=%d · curves=%d · circles=%d · params_ok=%d · "
            "target=%s · radius=%r · first_error=%s"
            % (diag["bodies"], diag["faces"], diag["edges"], diag["curves"],
               diag["circles"], diag["params_ok"], target, radius, diag["first_error"]))
    candidates.sort(key=lambda item: item[0])
    if candidates[0][0] > max(tolerance * 10.0, 1e-5):
        raise RuntimeError(f"找到的圆边偏离沉头入口位置: {candidates[0][0] * 1000.0:.3f} mm")
    return candidates[0][1]

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_hole_features.py —— 追加 hole_pattern_report
# 定位:   ★ 2026-10-03（轮 401）24h 计划 v2 段 4（孔族）。★ 来源是 `create_hole_pattern`
#   —— ★ 它**已经有真实调用者**（`tests/test_sw_hole_features.py` 用过），★ 而它
#   **吃一个 `creator` 可调用对象** ⇒ ★ MCP 层给不出函数对象 ⇒ 本包装把它换成**具名的种类**（`kind`）。
#   ★★ 同族的 `configure_straight_tap` / `configure_tapered_tap` 本轮**不挂** ——
#     它们吃的是 `IStraightTapElementData` / `ITaperedTapElementData` **COM 元素对象**，
#     而本仓**没有任何路径能从孔特征拿到那个元素**（只在 mock 测试里出现过）
#     ⇒ ★ MCP 层**给不出** ⇒ 记「内部件」并把理由写清（★ 而不是挂一个调不通的按钮）。
# 官方依据: `IFeatureManager.HoleWizard5`（各 `create_*_hole` 走它）· `IWizardHoleFeatureData2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

#: ★ 本工具支持的孔种类 ⇒ 对应的`creator`（★ 只收**签名简单且已真机验过**的那两个）。
_HOLE_PATTERN_CREATORS = {
    "through": "create_through_hole",
    "blind": "create_blind_hole",
}


def hole_pattern_report(model, positions, *, kind: str = "through", diameter_mm: float = 8.0,
                        depth_mm: float | None = None, plane_name: str = "Front Plane",
                        name: str = "孔") -> dict:
    """★ **按显式孔位一次创建一组孔**（★ 把 `create_hole_pattern` 的 `creator` 换成**具名种类**）。

    ★★ **为什么需要这一层**：`create_hole_pattern(model, positions, creator, **kwargs)` 收的是
    **一个可调用对象** —— ★ 而 MCP 层**给不出函数** ⇒ 包装把它换成 `kind`（★ 白名单里的名字）。

    :param positions: 孔位列表，每项 `[x_mm, y_mm]`（★ **毫米**，★ 坐标是规则 3 的书面例外：草图图元）。
    :param kind: `through`（通孔）/ `blind`（盲孔）。
    :param diameter_mm: 孔径（毫米）。
    :param depth_mm: 盲孔深度（毫米）—— ★ `kind="blind"` 时**必填**。
    :returns: `{ok, kind, requested, holes, tree_before, tree_after, new_features, error}` ——
        ★★ **判据两条都要**：★ 每个孔位都回了证据 **且** **特征树真的长了**（★ 规则 6 ——
        ★ 本会话已见过"回对象而什么都没发生"的空存根）。
    """
    out: dict = {"ok": False, "kind": str(kind), "requested": None, "holes": [],
                 "tree_before": None, "tree_after": None, "new_features": [], "error": None}
    if kind not in _HOLE_PATTERN_CREATORS:
        out["error"] = ("kind 只支持 %r（★ counterbore / countersink 另有必填参数，"
                        "★ 未在本工具暴露）" % sorted(_HOLE_PATTERN_CREATORS))
        return out
    #: ★ 规整 + 校验孔位（★ 每个必须是至少两个数的序列）
    try:
        pairs = []
        for item in (positions or []):
            seq = list(item)
            if len(seq) < 2:
                out["error"] = "每个孔位至少要有 x / y 两个数：%r" % (item,)
                return out
            pairs.append([float(seq[0]), float(seq[1])])
    except (TypeError, ValueError) as exc:
        out["error"] = "positions 必须是「每项两个数的列表」：%s" % str(exc)[:110]
        return out
    if not pairs:
        out["error"] = "positions 至少包含一个孔位"
        return out
    out["requested"] = len(pairs)
    kwargs: dict = {"diameter": float(diameter_mm), "plane_name": str(plane_name), "name": str(name)}
    if kind == "blind":
        if depth_mm is None:
            out["error"] = "kind=blind 时 depth_mm 必填"
            return out
        kwargs["depth"] = float(depth_mm)
    import sw_hole_features as _self                               #: ★ 自引用取 creator（避免循环导入的写法）
    creator = getattr(_self, _HOLE_PATTERN_CREATORS[kind])
    from sw_feature_readback import feature_names
    before = feature_names(model)
    try:
        evidence = creator and create_hole_pattern(model, pairs, creator, **kwargs)
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "建孔失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    after = feature_names(model)
    out["tree_before"] = len(before)
    out["tree_after"] = len(after)
    out["new_features"] = [x for x in after if x not in before]
    #: ★ 每个孔的证据（★ 只留可 JSON 序列化的摘要 —— ★ 证据项可能是 dataclass）
    for item in (evidence or []):
        if isinstance(item, dict):
            out["holes"].append({k: v for k, v in item.items()
                                 if isinstance(v, (str, int, float, bool, type(None)))})
        else:
            out["holes"].append({"repr": str(item)[:80]})
    built = len(out["holes"])
    out["ok"] = (built == len(pairs)) and len(after) > len(before)
    if not out["ok"] and built == len(pairs):
        out["error"] = ("每个孔位都回了证据而**特征树没长**（%d → %d）⇒ 孔**没真建成**"
                        "（★ 规则 6：不许只看返回值）" % (len(before), len(after)))
    elif not out["ok"]:
        out["error"] = "只回了 %d 条证据（请求 %d 个孔位）" % (built, len(pairs))
    return out
