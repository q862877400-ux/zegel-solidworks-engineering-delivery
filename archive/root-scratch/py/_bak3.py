"""SolidWorks 原生钣金特征创建与证据回读。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .sw_connect import get_com_member
    from .sw_part import _ensure_sketch_selected
except ImportError:
    from sw_connect import get_com_member
    from sw_part import _ensure_sketch_selected


SW_FM_BASE_FLANGE = 34
SW_END_COND_BLIND = 0
SW_BEND_ALLOWANCE_K_FACTOR = 2
SW_SHEET_METAL_RELIEF_RECTANGULAR = 1
SW_SOLID_BODY = 0


@dataclass(frozen=True)
class BaseFlangeSpec:
    """@brief 基体法兰的可制造参数，全部长度单位为米。"""

    thickness: float
    bend_radius: float
    depth: float
    k_factor: float = 0.42
    relief_ratio: float = 0.5
    reverse_direction: bool = False
    reverse_thickness: bool = False

    def validate(self) -> None:
        """@brief 在进入 COM 前拒绝明显无效的制造参数。"""
        if self.thickness <= 0:
            raise ValueError("钣金厚度必须大于 0")
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.depth <= 0:
            raise ValueError("基体法兰深度必须大于 0")
        if not 0 < self.k_factor < 1:
            raise ValueError("K 因子必须位于 0 与 1 之间")
        if self.relief_ratio <= 0:
            raise ValueError("卸料槽比例必须大于 0")


def _feature_type(feature: Any) -> str:
    """@brief 安全读取特征类型名。"""
    try:
        return str(get_com_member(feature, "GetTypeName2") or "")
    except Exception:
        return ""


def iter_features(model):
    """@brief 顺序遍历特征树，兼容 pywin32 的属性/方法两种投影。"""
    feature = get_com_member(model, "FirstFeature")
    # pywin32 可能为不同 COM 对象复用短生命周期包装器的 Python id，不能
    # 用 id 去重；以硬上限防御异常的特征链循环。
    count = 0
    while feature is not None and count < 4096:
        yield feature
        feature = get_com_member(feature, "GetNextFeature")
        count += 1


def create_base_flange(model, sketch_ref, spec: BaseFlangeSpec):
    """@brief 使用现代 FeatureData API 从开放或闭合草图创建原生基体法兰。

    开放折线路径会生成轮廓法兰；闭合轮廓会生成平板基体。返回真实
    ``IFeature``，失败时抛出异常，不把空返回值包装为成功。
    """
    spec.validate()
    _ensure_sketch_selected(model, sketch_ref)
    manager = get_com_member(model, "FeatureManager")

    bend_allowance = get_com_member(manager, "CreateCustomBendAllowance")
    if bend_allowance is None:
        raise RuntimeError("CreateCustomBendAllowance 未返回对象")
    bend_allowance.Type = SW_BEND_ALLOWANCE_K_FACTOR
    bend_allowance.KFactor = float(spec.k_factor)

    data = get_com_member(manager, "CreateDefinition", SW_FM_BASE_FLANGE)
    if data is None:
        raise RuntimeError("CreateDefinition(swFmBaseFlange) 未返回特征数据")

    data.Initialize(
        False,
        True,
        bend_allowance,
        True,
        SW_SHEET_METAL_RELIEF_RECTANGULAR,
        True,
        float(spec.relief_ratio),
        0.0,
        0.0,
    )
    data.D1EndConditionType = SW_END_COND_BLIND
    data.D1EndConditionDistance = float(spec.depth)
    data.D2EndConditionType = SW_END_COND_BLIND
    data.D2EndConditionDistance = 0.0
    data.OverrideDefaultSheetMetalParameters = True
    data.Thickness = float(spec.thickness)
    data.BendRadius = float(spec.bend_radius)
    data.ReverseDirection = bool(spec.reverse_direction)
    data.ReverseThickness = bool(spec.reverse_thickness)

    feature = get_com_member(manager, "CreateFeature", data)
    if feature is None:
        raise RuntimeError("CreateFeature(IBaseFlangeFeatureData) 创建失败")
    # GetErrorCode2 还带一个 by-ref ``isWarning`` 参数；此处只需拒绝硬错误，
    # 使用无歧义的 GetErrorCode 可兼容 pywin32 静态与动态代理。
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"基体法兰返回特征错误码: {error_code}")
    return feature


def sheet_metal_evidence(model) -> dict[str, Any]:
    """@brief 回读原生特征、实体与关键钣金参数，形成可审计证据。"""
    feature_rows = []
    base_parameters = []
    for feature in iter_features(model):
        type_name = _feature_type(feature)
        name = str(get_com_member(feature, "Name") or "")
        feature_rows.append({"name": name, "type": type_name})
        if type_name in {"BaseFlange", "SMBaseFlange", "Base-Flange"}:
            definition = get_com_member(feature, "GetDefinition")
            if definition is not None:
                base_parameters.append({
                    "name": name,
                    "thickness_m": float(get_com_member(definition, "Thickness") or 0.0),
                    "bend_radius_m": float(get_com_member(definition, "BendRadius") or 0.0),
                    "depth_m": float(get_com_member(definition, "D1EndConditionDistance") or 0.0),
                    "k_factor": float(get_com_member(definition, "KFactor") or 0.0),
                })

    bodies = tuple(get_com_member(model, "GetBodies2", SW_SOLID_BODY, False) or ())
    body_rows = []
    for body in bodies:
        is_sheet_metal = False
        try:
            is_sheet_metal = bool(get_com_member(body, "IsSheetMetal"))
        except Exception:
            pass
        body_rows.append({
            "name": str(get_com_member(body, "Name") or ""),
            "is_sheet_metal": is_sheet_metal,
        })

    type_names = [row["type"] for row in feature_rows]
    return {
        "features": feature_rows,
        "feature_types": type_names,
        "base_flange_parameters": base_parameters,
        "bodies": body_rows,
        "has_sheet_metal_feature": any("SheetMetal" in item for item in type_names),
        "has_base_flange": bool(base_parameters),
        "all_solid_bodies_are_sheet_metal": bool(body_rows) and all(
            row["is_sheet_metal"] for row in body_rows
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 以下为「原生钣金特征扩写」批次。
# 模式说明：与基体法兰不同，本批 5 个 FeatureData 接口在 C:\swapi 中
# **均无 Initialize 成员**（sw_know.py 逐一报 [SWK_NOT_FOUND]），
# 故走「CreateDefinition(swFmXxx) → AccessSelections → 设属性 →
# CreateFeature → ReleaseSelectionAccess」路径，不臆造 Initialize 调用。
# ══════════════════════════════════════════════════════════════════════

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（非开源项目，无第三方许可）
# 文件:   托管程序集 SolidWorks.Interop.swconst.dll（34.4.1.1011）中的
#         swFeatureNameID_e，取值由纯元数据反射取得
# 定位:   IFeatureManager.CreateDefinition(Int Type) 的 Type 实参。
#         官方签名：C:\swapi\types\IFeatureManager\CreateDefinition.md
#                  `System.object CreateDefinition( System.int Type )`
# 取值:   本批新增 5 个，逐个反射核出；swFmBaseFlange=34 与上游既有常量
#         SW_FM_BASE_FLANGE 一致，已交叉确认上游该常量无误。
# 查证:   pwsh -File D:\AI\SW\tools\reflect-enum.ps1 `
#           -Assembly swconst -Enum swFeatureNameID_e
#         （C:\swapi\enums\swFeatureNameID_e.md 只有名称列、无数值列，
#           故不以该文件为取值依据 —— 见 AGENTS.md 铁律 4「枚举值必须查」）
# ⚠ 本表为静态反射结果，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 查不到故不编: swFeatureNameID_e 中**没有** Hem / MiterFlange 对应项，
#   故本批不提供翻边与斜接法兰的 CreateDefinition 入口。
# ────────────────────────────────────────────────────────────────────
SW_FM_DRAFT = 3
SW_FM_ONE_BEND = 33
SW_FM_EDGE_FLANGE = 37
SW_FM_SWEPT_FLANGE = 117
SW_FM_SM_GUSSET = 118

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IFeatureManager\CreateFeature.md
#         C:\swapi\types\IFeatureManager\CreateDefinition.md
# 定位:   本批 5 个特征共用的「定义 → 建特征」骨架，与上游 create_base_flange
#         保持同一写法（上游已用于基体法兰且经静态比对通过）。
# 官方签名:
#           System.object  CreateDefinition( System.int Type )
#           Feature        CreateFeature( System.object FeatureData )
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _create_from_definition(model, fm_type: int, apply_definition):
    """由 FeatureData 定义创建特征，失败一律抛异常，不把空返回包装成成功。

    ``apply_definition`` 收到 FeatureData 对象，负责设属性；
    边/面引用类特征须在其内部自行配对 AccessSelections / ReleaseSelectionAccess。
    """
    manager = get_com_member(model, "FeatureManager")
    data = get_com_member(manager, "CreateDefinition", int(fm_type))
    if data is None:
        raise RuntimeError(f"CreateDefinition({fm_type}) 未返回特征数据")

    apply_definition(data)

    feature = get_com_member(manager, "CreateFeature", data)
    if feature is None:
        raise RuntimeError(f"CreateFeature({fm_type}) 创建失败")
    # GetErrorCode2 多一个 by-ref isWarning 参数；此处只需拒绝硬错误，
    # 用无歧义的 GetErrorCode 兼容 pywin32 静态与动态代理（同上游注释）。
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"钣金特征 {fm_type} 返回特征错误码: {error_code}")
    return feature


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_sheet_metal.py::BaseFlangeSpec（同文件既有类，@brief + 冻结
#         dataclass + validate() 在进入 COM 前拒绝无效制造参数）
# 定位:   下方 4 个 spec 数据类沿用 BaseFlangeSpec 的形状与命名习惯，
#         只增补各自领域的字段与校验，不引入新范式。
# ⚠ 字段语义取自 C:\swapi 对应 FeatureData 的成员目录（见各 create_* 的来源块）。
# ⚠ 本组为照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class OneBendSpec:
    """@brief 单折弯的可制造参数，长度单位为米。"""

    bend_radius: float
    angle: float
    reverse_direction: bool = False
    use_default_radius: bool = True

    def validate(self) -> None:
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if not 0 < self.angle < 360:
            raise ValueError("折弯角度必须位于 0 与 360 度之间")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec，见上一来源块）
# 定位:   边法兰 spec，沿用 BaseFlangeSpec 的 @brief + 冻结 dataclass +
#         validate() 形状。字段对应 IEdgeFlangeFeatureData 的
#         BendRadius / BendAngle / ReverseDirection / UseDefaultBendRadius。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class EdgeFlangeSpec:
    """@brief 边法兰的可制造参数，长度单位为米，角度为度。"""

    bend_radius: float
    flange_length: float
    angle: float = 90.0
    use_default_radius: bool = True
    reverse_direction: bool = False

    def validate(self) -> None:
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.flange_length <= 0:
            raise ValueError("法兰长度必须大于 0")
        if not 0 < self.angle <= 180:
            raise ValueError("边法兰角度必须位于 0 与 180 度之间")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec）
# 定位:   拔模 spec。字段 Angle / ReverseDirection 取自 swFmDraft(3) 对应的
#         特征数据；深度 depth 属工艺意图字段，不直接落到 COM 属性
#         （原因见 create_draft 来源块的 ⚠ 条）。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class DraftFeatureSpec:
    """@brief 拔模的可制造参数，角度为度、深度为米。"""

    angle: float
    depth: float
    reverse_direction: bool = False

    def validate(self) -> None:
        if not 0 < self.angle <= 180:
            raise ValueError("拔模角度必须位于 0 与 180 度之间")
        if self.depth <= 0:
            raise ValueError("拔模深度必须大于 0")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec）
# 定位:   加强筋 spec。字段逐项对应 C:\swapi\types\IGussetFeatureData\ 的
#         Thickness / ProfileDistance1 / ProfileDistance2 / ProfileAngle。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class GussetSpec:
    """@brief 钣金加强筋参数，长度单位为米、角度为度。"""

    thickness: float
    profile_distance_1: float
    profile_distance_2: float = 0.0
    profile_angle: float = 0.0

    def validate(self) -> None:
        if self.thickness <= 0:
            raise ValueError("加强筋厚度必须大于 0")
        if self.profile_distance_1 <= 0:
            raise ValueError("加强筋轮廓距离必须大于 0")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IOneBendFeatureData\
#           （成员 33 项：BendAngle / BendRadius / ReverseDirection /
#             UseDefaultBendRadius / ReliefType / ReliefRatio …）
# 定位:   swFmOneBend(33) 的属性装配。属性名逐项取自上述成员目录，
#         未使用任何未经证实的属性名。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_one_bend(model, sketch_ref, spec: OneBendSpec):
    """@brief 在草图轮廓上创建原生单折弯特征。"""
    spec.validate()
    _ensure_sketch_selected(model, sketch_ref)

    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)

    return _create_from_definition(model, SW_FM_ONE_BEND, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IEdgeFlangeFeatureData\
#           （成员 43 项：AddEdges / ISetEdges / BendAngle / BendRadius /
#             FlangePosition / PositionType / UseDefaultBendRadius /
#             UseDefaultBendAllowance / UseReliefRatio / ReliefRatio …）
# 定位:   swFmEdgeFlange(37) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member IEdgeFlangeFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性，不臆造 Initialize 调用。
# ⚠ 边集合由调用方在创建前用 SelectByID2 选好；本函数不代为选边，
#   沿用上游 sw_part._select_by_id 的选区惯例（见 AGENTS.md §三）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_edge_flange(model, spec: EdgeFlangeSpec):
    """@brief 在已选中的边上创建原生边法兰。

    调用前必须先用 ``sw_part._select_by_id`` 把目标边选入选区。
    """
    spec.validate()

    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)
        data.UseDefaultBendAllowance = True

    return _create_from_definition(model, SW_FM_EDGE_FLANGE, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IDraftFeatureData2\  +  swFeatureNameID_e(swFmDraft=3)
# 定位:   swFmDraft(3) 的属性装配。
# ⚠ IDraftFeatureData2 的成员名未逐项核到（该接口在 C:\swapi 中收录不完整），
#   故本函数只使用经反射确认存在的最小属性集 Angle / ReverseDirection，
#   深度改用草图侧的拉伸控制表达，不臆造 Depth 属性名。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_draft(model, face_ref, spec: DraftFeatureSpec):
    """@brief 在已选中的面上创建原生拔模特征。"""
    spec.validate()

    def _apply(data):
        data.Angle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)

    return _create_from_definition(model, SW_FM_DRAFT, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IGussetFeatureData\
#           （成员 19 项：SetSupportingFaces / GetSupportingFaces /
#             ProfileType / ProfileDistance1..4 / ProfileAngle /
#             Thickness / ThicknessType / UseAngle / ProfileLocation /
#             OffsetUsed / FlipOffsetDirection …）
# 定位:   swFmSMGusset(118) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member IGussetFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性。上列属性名逐项取自 C:\swapi 成员目录，未臆造。
# ⚠ 支撑面须由调用方先用 SelectByID2 选好；本函数不代为选面。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_gusset(model, spec: GussetSpec):
    """@brief 在已选中的支撑面区域创建原生钣金加强筋。"""
    spec.validate()

    def _apply(data):
        data.Thickness = float(spec.thickness)
        data.ProfileDistance1 = float(spec.profile_distance_1)
        data.ProfileDistance2 = float(spec.profile_distance_2)
        data.ProfileAngle = float(spec.profile_angle)

    return _create_from_definition(model, SW_FM_SM_GUSSET, _apply)
