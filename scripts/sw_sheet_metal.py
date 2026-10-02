"""SolidWorks 原生钣金特征创建与证据回读。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from .sw_connect import get_com_member, call_com_member
    from .sw_part import _ensure_sketch_selected
except ImportError:
    from sw_connect import get_com_member, call_com_member
    from sw_part import _ensure_sketch_selected


SW_FM_BASE_FLANGE = 34
SW_END_COND_BLIND = 0
SW_BEND_ALLOWANCE_K_FACTOR = 2
SW_SHEET_METAL_RELIEF_RECTANGULAR = 1
SW_SOLID_BODY = 0


@dataclass(frozen=True)
class BaseFlangeSpec:
    """@brief 基体法兰的可制造参数，全部长度单位为米。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_sheet_metal.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────


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


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**真机实测结论**，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_sheet_metal_e2e.py（证据脚本）
# 定位:   模块级**运行期实测状态表**（2026-10-01，SW 2026 SP4.1）。
#  ⚠⚠ 结论：本模块 6 个创建入口里**只有 2 个能跑**；另 4 个已作为 MCP 工具暴露
#    （T-011 接线）但真机失败。失败原因见下表 —— **不是「未测」，是「测了，不行」**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
#         ↑ 本块说明 `SHEET_METAL_RUNTIME_STATUS`（常量）与 `require_verified`（函数）
#         **两个**代码单元。⚠ 标记必须写成**裸的** `覆盖: 后续同级定义` ——
#         加 markdown 粗体会让正则 `r"覆盖\s*[:：]\s*后续同级定义"` 匹配不到。
#         ⚠ 本会话第 **5** 次踩这个覆盖范围坑，见 `check_provenance` 的诊断。
# ⚠ 本表只覆盖**本机实测过**的入口；未测的按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
#: 入口名 → (是否可用, 真机失败原因或成功证据)
SHEET_METAL_RUNTIME_STATUS = {
    # ✓ 实测可跑
    "create_base_flange": (True,
        "**闭轮廓**真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」。"
        "⚠ **开放折线（轮廓法兰）真机失败**：`CreateFeature(IBaseFlangeFeatureData) 创建失败`"
        "（2026-10-01 补测，见 probe_gusset_with_bend.py）⇒ **`True` 仅对闭轮廓成立**"),
    "sheet_metal_evidence": (True,
        "真机读回正确：thickness_m=0.002、has_base_flange=True、"
        "all_solid_bodies_are_sheet_metal=True"),
    # ✗ 实测失败（原因是真机报错原文）
    # ⚠⚠ 以下 4 条的**根因层次**已由真机测清（2026-10-01，`probe_featuredata_access.py`）：
    #   ① `CreateDefinition(fm)` 实测：34/37/118 → 非 None；**3/33 → None**
    #      ⇒ **Draft 与 OneBend 不走 `CreateDefinition`**（反射里有专用入口
    #        `InsertSheetMetal3dBend` / `IInsertSheetMetalEdgeFlange2` 等，**均存在**）。
    #   ② `AccessSelections(model, Component)` **被否证**：三种 Component 形式
    #      （`None` / `VARIANT(VT_DISPATCH,None)` / `False`）全失败
    #      ⇒ 官方文档说它是「取得描述**该特征**的选区」= **编辑**用，不是创建用。
    #   ③ `ReverseDirection` 的跨接口泄漏**已修复**（见 `create_edge_flange` 的 `_apply`）：
    #      删掉后报错**从** `Property ... can not be set` **变为** `CreateFeature(37) 创建失败`
    #      ⇒ **属性那一层确实通了**。
    #   **⇒ 仍未查明**：`create_gusset` 在**能**拿到 FeatureData 时为何 `Thickness` 仍设不上；
    #     以及这 4 个的**正确创建路径**（是否该改用专用 `Insert*` 入口）。**不猜、不硬改。**
    "create_one_bend": (False,
        "⚠ **真因已查明（2026-10-01，有官方依据）**：`swFmOneBend(33)` 是合法枚举成员，"
        "但**不在** `CreateDefinition` 接受的 35 个常量里（官方 `CreateDefinition.md` 的 "
        "Parameters 段）⇒ 返回 None **是应然的**。"
        "**正确入口**是 `swFmSketchBend(35)`（**已改用**），接口 `ISketchedBendFeatureData`。"
        "真机已验证 `CreateDefinition(35)` 返回**非 None**，且属性读回与该接口成员逐一吻合。"
        "**⚠ 仍缺**「选中折弯线 / 固定面」这一步 ⇒ 仍标不可用，但**原因已具体化**"
        "（不再是「未查明」）。原记法：`CreateDefinition(33) 返回 None ⇒ 不走 CreateDefinition`；"
        "正确入口未查明（反射里有 `InsertSheetMetal3dBend`）"),
    "create_draft": (False,
        "CreateDefinition(3) 返回 None ⇒ **该类型不走 `CreateDefinition`**；"
        "正确入口未查明"),
    "create_edge_flange": (False,
        "⚠ 属性层**已修**（原设的 `ReverseDirection` **不属于** `IEdgeFlangeFeatureData` —— "
        "跨接口泄漏，已删；报错已从 `Property ... can not be set` 变为 `CreateFeature(37) 创建失败`）"
        "⇒ **剩最后一层：`CreateFeature` 需要选择状态**（官方文档在同类特征上明写"
        "「select ... **with a Mark of 1**」）—— **未查明**"),
    "create_gusset": (False,
        "⚠ 属性层**已修**（**接口用错了**：钣金加强筋的接口是 **`ISMGussetFeatureData`**"
        "（`category: Sheet Metal`，28 属性），原代码用了 **`IGussetFeatureData`**"
        "（`category: Weldments`，19 成员）——**两者共有成员只有 3 个**，"
        "原设的 `Thickness`/`ProfileDistance1`/`ProfileDistance2`/`ProfileAngle` **全是焊件名**。"
        "改用 `GussetThickness`/`ProfileHeightDim`/`ProfileLengthDim`/`ProfileAngleDim` 后"
        "**真机读回全部成功**（0.002 / 0.01 / 0.01 / 45.0）；报错已变为 `CreateFeature(118) 创建失败`）"
        "⇒ **最后一层的性质已查明**：官方 `ISMGussetFeatureData` 的 Remarks 明写创建步骤 ——"
        "「Call `IFeatureManager::CreateDefinition` … **pre-select** …         Two flat faces of a **bend**」⇒ **必须预先选中「一个折弯的两个平面」**。"         "**⚠ 而本模块原本用的 `CreateDefinition`+`CreateFeature` 路线是**现代的**："         "官方的 `InsertSheetMetalGussetFeature3` 已被标注 "         "「**Obsolete. Superseded by CreateDefinition and CreateFeature.**」"         "⇒ **代码路线正确，缺的是「折弯的两个面」这个前置** —— 而测试夹具（平板基体法兰）"         "根本造不出折弯 ⇒ **本轮未定性**（不宣称它能跑，也不宣称它不行）"),
    # 未测（需要扫掠路径 + 轮廓两个选择，本轮没造出来）
    "create_swept_flange": (None, "未在本机实测（需要扫掠路径与轮廓两个选择）"),
}


def require_verified(entry: str) -> None:
    """**调用前**的守卫：该入口若在本机实测失败/未测，就抛**带原因**的错误。

    ⚠ 为什么必须这样：那 4 个入口已经作为 MCP 工具暴露给用户，
    失败时用户看到的是裸 COM 错误（`Property ... can not be set`），
    **完全指向不了真因**，也**无从知道这是已知问题**。
    """
    status = SHEET_METAL_RUNTIME_STATUS.get(entry)
    if status is None:
        return                       # 表里没有 ⇒ 不阻止（宁放行不误杀）
    ok, reason = status
    if ok is True:
        return
    if ok is None:
        raise RuntimeError(
            "%s **未在本机实测**（%s）—— 先在真机上验证再依赖它。"
            % (entry, reason)
        )
    raise RuntimeError(
        "%s **在本机实测失败，已知不可用**（2026-10-01，SW 2026 SP4.1）：%s。"
        "⇒ 正确形状尚未查明（是 swFm 取值错？FeatureData 属性名错？缺 AccessSelections？）；"
        "见 scripts/sw_sheet_metal.py 的 SHEET_METAL_RUNTIME_STATUS 与 "
        "D:\\\\AI\\\\SW\\\\probe_sheet_metal_e2e.py。" % (entry, reason)
    )


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

    bend_allowance = call_com_member(manager, "CreateCustomBendAllowance")
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
#: ⚠ `swFmOneBend(33)` 是**合法枚举成员**，但**不在** `CreateDefinition` 接受的 35 个常量里
#: ⇒ `CreateDefinition(33)` 返回 None **是应然的**（已知事实 34 的真因，2026-10-01 查明）。
#: 「一个折弯」的**正确入口**是下面这个（官方名单里有，接口 `ISketchedBendFeatureData`）。
#: 数值来源：`D:\AI\SW\_raw\**\enum_values_sldworks.txt`（反射，130 个成员）。
SW_FM_SKETCH_BEND = 35

#: `swSheetMetalGussetProfileDimType_e` 的取值（官方枚举页）：
#: `IndentDepth = 0` · **`ProfileDimensions = 1`**。
#: 钣金加强筋的 `ProfileDimensionScheme` **必须显式指定** —— 官方
#: `ISMGussetFeatureData` 的 Remarks 把它列为创建步骤 3 的**头一句**。
#: 数值来源：`C:\swapi\enums\swSheetMetalGussetProfileDimType_e.md`。
GUSSET_PROFILE_DIMENSIONS = 1
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
# 文件:   C:\swapi\types\ISketchedBendFeatureData\
#           （16 个成员：BendAngle / BendRadius / ReverseDirection /
#             UseDefaultBendRadius / UseDefaultBendAllowance / UseGaugeTable /
#             SetFixedFace / GetFixedFace / SetCustomBendAllowance / …）
# 定位:   **`swFmSketchBend(35)`** 的属性装配。
#         ⚠ **本注释原先写的是 `IOneBendFeatureData` / `swFmOneBend(33)`** ——
#         2026-10-01 查明 `swFmOneBend(33)` **不在 `CreateDefinition` 接受的
#         35 个常量里**，已改用 `swFmSketchBend(35)`，**注释随之更正**。
#         **⇒ 文档与代码不符比没有文档更糟 —— 本轮一并修掉这一处。**
#         属性名逐项取自上述成员目录，未使用任何未经证实的属性名。
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

    # ⚠⚠ **原为 `SW_FM_ONE_BEND(33)`** —— 那是**合法枚举成员**，
    #   但**不在** `CreateDefinition` 接受的 35 个常量里（见常量定义处的注释），
    #   所以 `CreateDefinition(33)` 返回 None 是**应然的**。
    #   官方名单里「一个折弯」对应的是 `swFmSketchBend(35)`。
    #   ⇒ 真机已验证：`CreateDefinition(35)` 返回**非 None**，且读回的属性与
    #     `ISketchedBendFeatureData` 的成员逐一吻合。
    #   ⚠ **仍缺**「选中折弯线/固定面」这一步 ⇒ 不宣称整条路已通。
    return _create_from_definition(model, SW_FM_SKETCH_BEND, _apply)


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
        # ⛔ 原代码在此设 `data.ReverseDirection` —— **该属性不属于本接口**。
        #    `IEdgeFlangeFeatureData` 的 43 个成员里没有它；
        #    它是 `IDraftFeatureData2`（拔模）的成员（**跨接口属性泄漏**）。
        #    真机表现：`Property '<unknown>.ReverseDirection' can not be set`。
        #    ⚠ **不臆造替代**：最接近的 `ReverseOffset` / `ReversePositionOffset`
        #    是**偏置**方向，语义不同 —— 边法兰没有「反向」这个开关。
        #    见 `C:\swapi\types\IEdgeFlangeFeatureData\`（43 个成员名）。
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
        # ⚠ 本函数甚至**拿不到 FeatureData**：`CreateDefinition(3)` 返回 None
        #   （真机实测；同族里 34/37/118 都正常返回）⇒ **Draft 不走 `CreateDefinition`**。
        #   反射里有专用入口，但本轮**未查明**正确用法 ⇒ 见 `SHEET_METAL_RUNTIME_STATUS`。
        data.Angle = float(spec.angle)
        # ⚠ `ReverseDirection` **是** `IDraftFeatureData2` 的成员（这里用对了）；
        #   注意它**不是** `IEdgeFlangeFeatureData` 的成员 —— 见 `create_edge_flange` 的注释。
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
        # ⚠⚠⚠ **完整根因（2026-10-01 真机 + 官方类型表确证）**：
        #   本函数创建的是 **钣金**加强筋（`swFmSMGusset=118`，枚举描述明写
        #   "**Sheet metal** gusset"），其特征数据接口是
        #   **`ISMGussetFeatureData`**（`category: Feature Interfaces/Sheet metal`，
        #   28 个属性）；而**原代码用的是 `IGussetFeatureData`** ——
        #   那是 **`Feature Interfaces/Weldments`**（焊件）的接口（19 个成员）。
        #
        #   **两个接口共有成员只有 3 个**（`AccessSelections` / `ProfileType` /
        #   `ReleaseSelectionAccess`）⇒ 原设的 4 个属性名**全部来自焊件接口**
        #   ⇒ 拿到的对象**不是那个接口** ⇒ **对任何成员都没反应**
        #   （真机实测：连**读**都读不到），表现为
        #   `Property '<unknown>.Thickness' can not be set`。
        #
        #   **⇒ 改名为 SM 接口的成员**（映射见下），长度/角度语义不变。
        # ⚠⚠ **官方 `ISMGussetFeatureData` 的 Remarks 把创建步骤写成 4 步，
        #   而第 3 步的**头一句**是「Specify `ProfileDimensionScheme`」——
        #   本函数原先**从未设过它**（只设了 4 个尺寸属性）。**
        #   官方 `UseAngleDimForProfile` 更明写「**valid only if
        #   ProfileDimensionScheme is set to 1**」⇒ 不设 scheme 就设角度维，
        #   那个属性**可能根本不生效**。⇒ 先设 scheme。
        data.ProfileDimensionScheme = GUSSET_PROFILE_DIMENSIONS
        data.GussetThickness = float(spec.thickness)          # 原 Thickness（焊件名）
        # ⚠ 官方 Remarks 在 scheme=1 下给了**两种互斥的**标注方案，二选一：
        #   · **两条腿**：`ProfileLengthDim`(d1) + `ProfileHeightDim`(d2)
        #     + **`UseAngleDimForProfile = false`**
        #   · **d1 腿 + 它与加强筋的夹角**：`ProfileLengthDim` + `ProfileAngleDim`
        #     + **`UseAngleDimForProfile = true`**
        #   ⇒ **按 spec 有没有给角度来选**，不无条件置 true。
        #     （无条件置 true 而 `ProfileAngleDim` 是 0，是**自相矛盾**的标注方案。）
        _has_angle = bool(spec.profile_angle)
        data.UseAngleDimForProfile = _has_angle
        data.ProfileLengthDim = float(spec.profile_distance_2)   # 原 ProfileDistance2
        if _has_angle:
            data.ProfileAngleDim = float(spec.profile_angle)     # 原 ProfileAngle
        else:
            data.ProfileHeightDim = float(spec.profile_distance_1)  # 原 ProfileDistance1
        # 官方 `UseOffset`：「**After setting this property to true, set the offset
        #   distance.** **If a reference point is not set, the offset is applied to an
        #   assumed reference point.**」+ Remarks 第 2 步：「**If you do not pre-select
        #   any of these entities, then you must set `UseOffset` to true**」
        #   ⇒ 本函数**不预选参照点** ⇒ **必须**置 true，并设 offset 距离。
        data.UseOffset = True
        data.OffsetDistance = 0.0

    return _create_from_definition(model, SW_FM_SM_GUSSET, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec / OneBendSpec 等）
# 定位:   扫掠法兰 spec。字段逐项对应 C:\swapi\types\ISweptFlangeFeatureData\
#         的 Thickness / StartOffset / EndOffset / BendRadius / ReliefRatio。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（SolidWorks.Interop.swconst.dll）
# 文件:   C:\swapi\enums\swSweptFlangePositionTypes_e.md
# 定位:   ISweptFlangeFeatureData.FlangePosition 的取值域。
# 官方示例: C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md
#           第 75 行 `swFeatData.FlangePosition =
#             swSweptFlangePositionTypes_e.swSweptFlangePositionType_MaterialInside`
# 取值:   官方 3 项全量照录。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_SWEPT_FLANGE_POSITIONS = {
    "material_inside": 1,     # swSweptFlangePositionType_MaterialInside
    "material_outside": 2,    # swSweptFlangePositionType_MaterialOutside
    "bend_outside": 3,        # swSweptFlangePositionType_BendOutside
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 使用示例（非开源项目，无第三方许可）
# 文件:   C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md 第 74-87 行
# 定位:   SweptFlangeSpec 的字段集与默认值，**逐条对应官方示例所设的 14 个属性**：
#           EndOffset=0 / StartOffset=0 / FlangePosition=MaterialInside /
#           FlattenAlongPath=False / TrimSideBends=False / ReverseDirection=False /
#           UseDefaultBendAllowance=True / UseDefaultBendRelief=True /
#           UseGaugeTable=False / UseMaterialSheetMetalParameters=False /
#           OverrideDefaultSheetMetalParameters=False
#           以及官方**不设**的两项：
#           · Thickness      → 厚度从基体法兰继承，故本类 thickness 默认 None
#           · ReliefRatio    → 官方走 UseDefaultBendRelief=True，不设此属性
#         另加 BendRadius / UseDefaultRadius（官方示例设 UseDefaultRadius=False
#         但未设 BendRadius，靠 SolidWorks 自身默认值兜底；本类默认 True 更稳，
#         这属于本仓库的工程判断，已在 examples/09_sheet_metal.py 末尾标注）。
# ⚠ 本类为照官方示例新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class SweptFlangeSpec:
    """@brief 扫掠法兰参数，长度单位为米。

    ⚠ ``thickness`` 默认为 ``None``：**官方示例并不设 Thickness**，
      而是用 ``UseMaterialSheetMetalParameters=False`` +
      ``OverrideDefaultSheetMetalParameters=False`` 让厚度**从基体法兰继承**
      （见 ``C:\\swapi\\examples\\Create_Swept_Flange_Example_VBNET.md``）。
      传 None 即复现官方行为；确有独立厚度时才显式给值。
    """

    start_offset: float
    end_offset: float = 0.0
    thickness: float | None = None
    bend_radius: float = 0.0
    use_default_radius: bool = True
    flange_position: int = SWS_SWEPT_FLANGE_POSITIONS["material_inside"]
    flatten_along_path: bool = False
    trim_side_bends: bool = False
    use_default_bend_relief: bool = True
    use_gauge_table: bool = False
    use_material_parameters: bool = False
    override_default_sheet_metal_parameters: bool = False
    reverse_direction: bool = False

    def validate(self) -> None:
        if self.thickness is not None and self.thickness <= 0:
            raise ValueError("扫掠法兰厚度必须大于 0")
        if self.start_offset < 0:
            raise ValueError("扫掠法兰起始偏移不能小于 0")
        if self.end_offset < 0:
            raise ValueError("扫掠法兰结束偏移不能小于 0")
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.flange_position not in SWS_SWEPT_FLANGE_POSITIONS.values():
            raise ValueError(
                "flange_position 必须是 SWS_SWEPT_FLANGE_POSITIONS 中的值"
            )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名 + ★ 官方使用示例
# 文件:   签名: C:\swapi\types\ISweptFlangeFeatureData\（32 成员）
#         示例: C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md
#               C:\swapi\examples\Create_Swept_Flange_Using_Gauge_Table_Example_CSharp.md
# 定位:   swFmSweptFlange(117) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member ISweptFlangeFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性。属性集合与顺序**照官方示例逐行对齐**。
# 官方调用序列（Example_VBNET 第 37-88 行，摘录）:
#         1) Part.FeatureManager.InsertSheetMetalBaseFlange2(...)   ← 前置：先有基体法兰
#         2) 选轮廓草图 → GetSelectedObject6 → ClearSelection2
#         3) 选路径边   → GetSelectedObject6 → ClearSelection2
#         4) swFeatMgr.CreateDefinition(swFeatureNameID_e.swFmSweptFlange)
#         5) 逐个设 EndOffset / FlangePosition / FlattenAlongPath /
#            OverrideDefaultSheetMetalParameters / Path / Profile /
#            ReverseDirection / StartOffset / TrimSideBends /
#            UseDefaultBendAllowance / UseDefaultBendRelief /
#            UseDefaultRadius / UseGaugeTable / UseMaterialSheetMetalParameters
#         6) swFeatMgr.CreateFeature(swFeatData)
# 本次改动: 初版只设了 7 个属性且**错误地设了 Thickness**。对照官方示例后：
#         · 删掉 Thickness（官方不设，厚度从基体法兰继承）
#         · 补齐 FlangePosition / FlattenAlongPath / TrimSideBends /
#           UseDefaultBendRelief / UseGaugeTable / UseMaterialSheetMetalParameters /
#           OverrideDefaultSheetMetalParameters 共 7 个
#         · 删掉 ReliefRatio（官方示例走 UseDefaultBendRelief=True，不设此属性）
# ⚠ 官方示例**没有**为这条路径调用 AccessSelections / ReleaseSelectionAccess
#   （与 Access_Selections_Example 那类需要编辑选区的示例不同），
#   故本函数同样不调，避免多余副作用。
# ⚠ 本函数为照官方签名与官方示例新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_swept_flange(model, path_ref, profile_ref, spec: SweptFlangeSpec):
    """@brief 沿路径扫掠创建原生扫掠法兰（属性装配照官方示例对齐）。

    :param path_ref: 扫掠路径（边）。官方示例用 ``SelectByRay`` 选边后
        ``SelectionManager.GetSelectedObject6(1, -1)`` 取得。
    :param profile_ref: 扫掠轮廓（草图）。
    :note: **调用前必须已有基体法兰**（``swFmBaseFlange``）——
        官方示例正是先建基体法兰再建扫掠法兰，否则厚度无从继承。
    """
    spec.validate()

    def _apply(data):
        data.EndOffset = float(spec.end_offset)
        data.StartOffset = float(spec.start_offset)
        data.FlangePosition = int(spec.flange_position)
        data.FlattenAlongPath = bool(spec.flatten_along_path)
        data.TrimSideBends = bool(spec.trim_side_bends)
        data.ReverseDirection = bool(spec.reverse_direction)
        data.UseDefaultRadius = bool(spec.use_default_radius)
        if not spec.use_default_radius:
            data.BendRadius = float(spec.bend_radius)
        data.UseDefaultBendAllowance = True
        data.UseDefaultBendRelief = bool(spec.use_default_bend_relief)
        data.UseGaugeTable = bool(spec.use_gauge_table)
        data.UseMaterialSheetMetalParameters = bool(spec.use_material_parameters)
        data.OverrideDefaultSheetMetalParameters = bool(
            spec.override_default_sheet_metal_parameters
        )
        # 厚度：官方示例不设，走基体法兰继承；调用方显式给值时才覆盖。
        if spec.thickness is not None:
            data.Thickness = float(spec.thickness)
        if path_ref is not None:
            data.Path = path_ref
        if profile_ref is not None:
            data.Profile = profile_ref

    return _create_from_definition(model, SW_FM_SWEPT_FLANGE, _apply)
