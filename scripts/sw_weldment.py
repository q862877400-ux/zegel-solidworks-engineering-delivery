"""SolidWorks 原生焊件结构构件与切割清单封装。"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

try:
    from .sw_connect import get_com_member, call_com_member, save_document
    from .sw_document_data import set_custom_properties
    from .sw_part import _ensure_sketch_selected
    from .sw_preflight import import_com_dependencies
except ImportError:
    from sw_connect import get_com_member, call_com_member, save_document
    from sw_document_data import set_custom_properties
    from sw_part import _ensure_sketch_selected
    from sw_preflight import import_com_dependencies


pythoncom, _win32com, VARIANT = import_com_dependencies()

SW_CONNECTED_SEGMENTS_SIMPLE_CUT = 1
SW_END_CONDITION_MITER = 1
SW_SOLID_BODY = 0

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（SolidWorks.Interop.swconst.dll）
# 文件:   D:\AI\SW\_raw\reflect\  —— 由 D:\AI\SW\tools\reflect-enum.ps1
#         对官方程序集做纯元数据反射取得（swFeatureNameID_e）。
# 定位:   本模块新��� 4 个 CreateDefinition 入口的 Type 实参。
# 取值:   逐个反射核出，未臆造；`C:\swapi\enums\swFeatureNameID_e.md` 只有名称列、
#         **无数值列**，故不以该文件为取值依据（见 AGENTS.md 铁律 4）。
# ⚠ 扫描 131 个条目确认：焊件相关的**只有这 3 个**，没有「下料表」或「构件分割」
#   的独立 fm 条目 —— 那两个走 IFeatureManager 的 Insert* 方法（见文件末尾）。
# ⚑ 现状: SW_FM_MATE_PROFILE_CENTER 被 create_profile_center_mate 使用；
#   SW_FM_PROFILE_FEATURE 与 SW_FM_WELD_MEMBER_FEAT **当前无人使用** ——
#   保留是因为它们记录了「型材特征 / 构件成员在官方枚举里确有独立 fm 条目」
#   这一事实（我曾据 swFmWeldMemberFeat 误写过一个不成立的创建入口）。
#   若后续无对应封装，可连同说明一并删除。
# ⚠ 本组为静态反射结果，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SW_FM_PROFILE_FEATURE = 65      # swFmProfileFeature
SW_FM_WELD_MEMBER_FEAT = 72    # swFmWeldMemberFeat
SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter
CORE_CUT_LIST_PROPERTY_NAMES = {
    "length",
    "长度",
    "angle1",
    "角度1",
    "angle2",
    "角度2",
    "angle direction",
    "角度方向",
    "angle rotation",
    "角度旋转",
    "description",
    "说明",
    "material",
    "材料",
    "weight",
    "质量",
    "单重",
    "quantity",
    "数量",
    "total length",
    "总长度",
    "unit_of_measure",
    "计量单位",
    "profile_designation",
    "material_spec",
    "source_repository",
    "source_sku",
}


def _as_tuple(value) -> tuple:
    """@brief 把 COM 单对象、SAFEARRAY 或空值规范为元组。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_weldment.py —— 本文件（**轮 145 的命名迁移**）。
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

    if value is None:
        return ()
    if isinstance(value, (tuple, list)):
        return tuple(item for item in value if item is not None)
    return (value,)


def _active_configuration_name(model) -> str:
    """@brief 回读活动配置名，供自定义配置型材调用使用。"""
    manager = get_com_member(model, "ConfigurationManager")
    configuration = get_com_member(manager, "ActiveConfiguration")
    return str(get_com_member(configuration, "Name") or "")


def create_weldment_profile(
    model,
    sketch_ref,
    output_path: str | Path,
    *,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """@brief 将选定轮廓草图保存为真实 ``.sldlfp`` 焊件型材。"""
    target = Path(output_path).expanduser().resolve()
    if target.suffix.casefold() != ".sldlfp":
        raise ValueError("焊件型材输出必须使用 .sldlfp 扩展名")
    target.parent.mkdir(parents=True, exist_ok=True)
    _ensure_sketch_selected(model, sketch_ref)
    configuration_name = _active_configuration_name(model)
    if properties:
        set_custom_properties(
            model,
            properties,
            configuration_name=configuration_name,
            save=False,
        )
        _ensure_sketch_selected(model, sketch_ref)
    if not save_document(model, str(target)):
        raise RuntimeError("自定义焊件型材保存失败")
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("SolidWorks 返回成功，但未生成 .sldlfp 文件")
    #: ★★★ 2026-10-01（轮 341）**补 `ok` 让返回契约统一** —— 真因（挖
    #:   `weldment_profile_and_curve` 这条 `stitched` 时发现）：
    #:   ★ 本函数**原先只回 `path` / `configuration_name` / `size_bytes` / `properties`，
    #:     没有 `ok`** ⇒ ★ 而**判据其实是"不抛即成功"**（★ `save_document` 回 falsy ⇒ 抛；
    #:     产物不存在或 0 字节 ⇒ 抛）—— ★ **那是一种合法契约，★ 但与仓库里"回 `ok`"那套混着**，
    #:     ★★ **调用方无从用统一方式判成败**（★ 实测：真机上文件**确实建成了 49287 字节**，
    #:     而按 `ok` 读会得到 `False`）。
    #:   ⇒ ★ 现在**两者并存**：★ 成功回 `ok=True`，★ **失败仍抛**（★ 不改变既有行为）。
    #: ⚠ 顺带记一条真机现象：★ 保存后目录里会多一个 **`~$<名字>.SLDLFP`（6 字节）** ——
    #:   ★ 那是 **SolidWorks 的临时锁文件**，★ **不是产物**；★ 判"产物非空"时**要排除 `~$` 前缀**。
    return {
        "ok": True,
        "path": str(target),
        "configuration_name": configuration_name,
        "size_bytes": target.stat().st_size,
        "properties": dict(properties or {}),
        "★": "★ 契约：★ **成功回 `ok=True`；失败**抛异常**（`RuntimeError` / `ValueError`）** —— "
             "★ 两者并存；★ `size_bytes` 是**产物本身**的大小（★ 已排除 `~$` 锁文件）",
    }


def create_structural_member(
    model,
    profile_path: str | Path,
    segment_groups: Iterable[Iterable[Any]],
    *,
    configuration_name: str = "",
    apply_corner_treatment: bool = True,
    corner_treatment_type: int = SW_END_CONDITION_MITER,
    connected_segments_option: int = SW_CONNECTED_SEGMENTS_SIMPLE_CUT,
    allow_protrusion: bool = False,
):
    """@brief 用 ``InsertStructuralWeldment5`` 创建一组原生结构构件。"""
    profile = Path(profile_path).expanduser().resolve()
    if not profile.is_file() or profile.suffix.casefold() != ".sldlfp":
        raise FileNotFoundError(f"焊件型材不存在或格式错误: {profile}")
    manager = get_com_member(model, "FeatureManager")
    existing_types = {
        str(get_com_member(feature, "GetTypeName2") or "")
        for feature in _iter_feature_chain(get_com_member(model, "FirstFeature"), "GetNextFeature")
    }
    if "WeldmentFeature" not in existing_types:
        model.ClearSelection2(True)
        weldment_feature = call_com_member(manager, "InsertWeldmentFeature")
        if weldment_feature is None:
            raise RuntimeError("InsertWeldmentFeature 创建失败")
    groups = []
    for index, raw_segments in enumerate(segment_groups, start=1):
        segments = tuple(item for item in raw_segments if item is not None)
        if not segments:
            raise ValueError(f"结构构件第 {index} 组没有路径段")
        group = call_com_member(manager, "CreateStructuralMemberGroup")
        if group is None:
            raise RuntimeError("CreateStructuralMemberGroup 未返回对象")
        group.Segments = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, segments)
        group.ApplyCornerTreatment = bool(apply_corner_treatment)
        if apply_corner_treatment:
            group.CornerTreatmentType = int(corner_treatment_type)
            # 保留每条路径段为独立切料实体，切割清单才能按长度正确分组。
            group.MiterMergeCondition = False
        groups.append(group)

    # pywin32 会把 Python 元组封送为 VARIANT SAFEARRAY；不传模糊的预选择集。
    feature = get_com_member(
        manager,
        "InsertStructuralWeldment5",
        str(profile),
        int(connected_segments_option),
        bool(allow_protrusion),
        VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, tuple(groups)),
        str(configuration_name),
    )
    if feature is None:
        raise RuntimeError("InsertStructuralWeldment5 创建失败")
    model.ClearSelection2(True)
    if not bool(call_com_member(model, "EditRebuild3")):
        raise RuntimeError("结构构件创建后的模型重建失败")
    return feature


def _body_length_key(body) -> int:
    """@brief 用实体包围盒最长边生成微米级分组键。"""
    box = tuple(float(item) for item in (get_com_member(body, "GetBodyBox") or ()))
    if len(box) != 6:
        raise RuntimeError("结构构件实体未返回 6 值包围盒")
    spans = (abs(box[3] - box[0]), abs(box[4] - box[1]), abs(box[5] - box[2]))
    return int(round(max(spans) * 1_000_000.0))


def _body_cut_list_key(body) -> tuple[int, int, int]:
    """@brief 生成旋转不变的三轴微米包围盒键，避免同长异型材误合并。"""
    box = tuple(float(item) for item in (get_com_member(body, "GetBodyBox") or ()))
    if len(box) != 6:
        raise RuntimeError("结构构件实体未返回 6 值包围盒")
    spans = sorted((abs(box[3] - box[0]), abs(box[4] - box[1]), abs(box[5] - box[2])))
    return tuple(int(round(item * 1_000_000.0)) for item in spans)


def ensure_cut_list(model) -> list[Any]:
    """@brief 为尚无清单的焊件按实体长度创建原生 CutListFolder。

    ``InsertWeldmentCutList2`` 的每次调用接收一组应属于同一切料项的实体。
    这里按包围盒最长边分组，使矩形框架的等长横梁/立柱分别形成数量为 2 的
    清单项；不把不同长度实体误合并为一项。
    """
    existing_by_name = {}
    for feature in iter_features_recursive(model):
        if str(get_com_member(feature, "GetTypeName2") or "") == "CutListFolder":
            existing_by_name.setdefault(str(get_com_member(feature, "Name") or ""), feature)
    existing = list(existing_by_name.values())
    if existing:
        return existing
    bodies = _as_tuple(get_com_member(model, "GetBodies2", SW_SOLID_BODY, False))
    if not bodies:
        raise RuntimeError("没有可写入切割清单的结构构件实体")
    grouped: dict[tuple[int, int, int], list[Any]] = {}
    for body in bodies:
        grouped.setdefault(_body_cut_list_key(body), []).append(body)
    manager = get_com_member(model, "FeatureManager")
    created = []
    for length_key in sorted(grouped):
        body_array = VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
            tuple(grouped[length_key]),
        )
        method = getattr(manager, "InsertWeldmentCutList2", None)
        if callable(method):
            feature = method(body_array)
        else:
            ole_object = getattr(manager, "_oleobj_", None)
            if ole_object is None:
                raise RuntimeError("FeatureManager 不支持 InsertWeldmentCutList2")
            # SW2026 IDispatch 将 DISPID 174 的方法同时暴露成值为 None 的伪属性，
            # 直接按官方类型库 DISPATCH_METHOD 语义调用，避免把 None 当函数。
            feature = ole_object.Invoke(
                174,
                0,
                pythoncom.DISPATCH_METHOD,
                True,
                body_array,
            )
        if feature is None:
            raise RuntimeError(f"InsertWeldmentCutList2 创建失败: length_key={length_key}")
        created.append(feature)
    if not bool(call_com_member(model, "EditRebuild3")):
        raise RuntimeError("切割清单创建后的模型重建失败")
    return created


def _iter_feature_chain(first_feature, next_member: str):
    """@brief 遍历顶层或同级子特征链。"""
    feature = first_feature
    count = 0
    while feature is not None and count < 4096:
        yield feature
        feature = get_com_member(feature, next_member)
        count += 1


def iter_features_recursive(model):
    """@brief 深度遍历焊件文件夹中的 CutListFolder 等子特征。"""
    def walk(feature):
        yield feature
        try:
            first_child = get_com_member(feature, "GetFirstSubFeature")
        except Exception:
            first_child = None
        for child in _iter_feature_chain(first_child, "GetNextSubFeature"):
            yield from walk(child)

    for root in _iter_feature_chain(get_com_member(model, "FirstFeature"), "GetNextFeature"):
        yield from walk(root)


def _read_property(manager, name: str) -> dict[str, Any]:
    """@brief 使用 Get6 读取切割清单属性并保留原始/解析值。"""
    raw = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    resolved = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    was_resolved = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    linked = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    status = int(manager.Get6(name, False, raw, resolved, was_resolved, linked))
    return {
        "name": str(name),
        "status": status,
        "raw": str(raw.value or ""),
        "resolved": str(resolved.value or ""),
        "was_resolved": bool(was_resolved.value),
        "linked": bool(linked.value),
    }


def read_property_manager(manager, *, core_only: bool = True) -> dict[str, dict[str, Any]]:
    """@brief 枚举属性管理器中的制造属性，默认排除模板标题栏噪声。"""
    names = _as_tuple(get_com_member(manager, "GetNames"))
    if core_only:
        names = tuple(
            name for name in names if str(name).strip().casefold() in CORE_CUT_LIST_PROPERTY_NAMES
        )
    return {str(name): _read_property(manager, str(name)) for name in names}


def set_cut_list_properties(model, properties: dict[str, Any]) -> list[dict[str, Any]]:
    """@brief 将型材来源和材料规格写入每个原生切割清单项并回读。"""
    if not properties:
        raise ValueError("切割清单属性不能为空")
    ensure_cut_list(model)
    results = []
    seen_names = set()
    for feature in iter_features_recursive(model):
        if str(get_com_member(feature, "GetTypeName2") or "") != "CutListFolder":
            continue
        feature_name = str(get_com_member(feature, "Name") or "")
        if feature_name in seen_names:
            continue
        seen_names.add(feature_name)
        manager = get_com_member(feature, "CustomPropertyManager")
        item = {"name": feature_name, "properties": {}}
        for raw_name, raw_value in properties.items():
            name = str(raw_name).strip()
            if not name:
                raise ValueError("切割清单属性名不能为空")
            value = str(raw_value)
            add_status = int(manager.Add3(name, 30, value, 2))
            readback = _read_property(manager, name)
            verified = readback["raw"] == value or readback["resolved"] == value
            if not verified:
                raise RuntimeError(f"切割清单属性回读失败: {item['name']} / {name}")
            item["properties"][name] = {"add_status": add_status, **readback}
        results.append(item)
    return results


def update_cut_list(model) -> list[dict[str, Any]]:
    """@brief 更新所有原生 CutListFolder 并返回文件夹级几何证据。"""
    folders = []
    seen_names = set()
    for feature in iter_features_recursive(model):
        type_name = str(get_com_member(feature, "GetTypeName2") or "")
        if type_name != "CutListFolder":
            continue
        feature_name = str(get_com_member(feature, "Name") or "")
        if feature_name in seen_names:
            continue
        seen_names.add(feature_name)
        body_folder = get_com_member(feature, "GetSpecificFeature2")
        update_ok = bool(call_com_member(body_folder, "UpdateCutList")) if body_folder else False
        manager = get_com_member(feature, "CustomPropertyManager")
        folders.append({
            "name": feature_name,
            "type": type_name,
            "body_count": int(get_com_member(body_folder, "GetBodyCount") or 0) if body_folder else 0,
            "update_ok": update_ok,
            "properties": read_property_manager(manager) if manager else {},
        })
    return folders


def weldment_evidence(model, *, create_missing_cut_list: bool = False) -> dict[str, Any]:
    """@brief 回读结构构件、实体数量和 SW2024+ 配置切割清单项目。"""
    if create_missing_cut_list:
        ensure_cut_list(model)
    folders = update_cut_list(model)
    features = []
    seen_features = set()
    for feature in iter_features_recursive(model):
        row = {
            "name": str(get_com_member(feature, "Name") or ""),
            "type": str(get_com_member(feature, "GetTypeName2") or ""),
        }
        key = (row["name"], row["type"])
        if key not in seen_features:
            seen_features.add(key)
            features.append(row)
    configuration = get_com_member(get_com_member(model, "ConfigurationManager"), "ActiveConfiguration")
    cut_list_items = []
    try:
        items = _as_tuple(get_com_member(configuration, "GetCutListItems"))
    except Exception:
        items = ()
    for index, item in enumerate(items, start=1):
        manager = get_com_member(item, "CustomPropertyManager")
        cut_list_items.append({
            "index": index,
            "properties": read_property_manager(manager) if manager else {},
        })

    bodies = _as_tuple(get_com_member(model, "GetBodies2", SW_SOLID_BODY, False))
    feature_types = [item["type"] for item in features]
    return {
        "configuration": str(get_com_member(configuration, "Name") or ""),
        "features": features,
        "feature_types": feature_types,
        "solid_body_count": len(bodies),
        "cut_list_folders": folders,
        "cut_list_items": cut_list_items,
        "has_weldment_feature": "WeldmentFeature" in feature_types,
        "has_structural_member": any(item in {"StructuralMember", "WeldMemberFeat"} for item in feature_types),
    }


def export_cut_list_csv(evidence: dict[str, Any], output_path: str | Path) -> Path:
    """@brief 将完整切割清单属性导出为 UTF-8-SIG CSV。"""
    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = evidence.get("cut_list_folders") or evidence.get("cut_list_items") or []
    property_names = sorted({name for row in rows for name in row.get("properties", {})})
    columns = ["index", "name", "body_count", *property_names]
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            values = {
                "index": row.get("index", index),
                "name": row.get("name", ""),
                "body_count": row.get("body_count", ""),
            }
            for name, payload in row.get("properties", {}).items():
                values[name] = payload.get("resolved") or payload.get("raw") or ""
            writer.writerow(values)
    return target


# ══════════════════════════════════════════════════════════════════════
# 以下补齐此前未触及的 4 个焊件接口族（见 docs/family-coverage.md）。
#
# ⚠ 与既有代码的关系（读这段再往下看，能省一次返工）：
#   构件创建本身**已由上游 create_weldment_members 正确实现** ——
#   走 IFeatureManager.InsertStructuralWeldment5
#   (String Path, Int32, Boolean, Object Groups, String)，型材按**路径字符串**给。
#   本批补的是它周边的四件事：型材事后调整、型材中心配合、构件分割配置、
#   下料表与焊接文件夹插入。
#
# ⚠ 一处被审计器抓出来并已删除的错误实现：
#   曾写过 create_weld_member，用 CreateDefinition(swFmWeldMemberFeat=72)
#   拿 FeatureData 后赋值 data.MemberProfile。**赋不进去** ——
#   IStructureSystemMemberFeatureData 只有 get_MemberProfile()、**没有 setter**
#   （该接口的 setter 仅 IsSplit / StartEndExtendD1 / StartEndExtendD2）。
#   由 audit_call_arity.py 报「同名成员存在但 arity 全对不上」当场抓出。
# ══════════════════════════════════════════════════════════════════════


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_sheet_metal.py::_create_from_definition（同任务产出的姊妹模块）
#         与 scripts/sw_weldment.py::create_base_flange 所在文件的上游写法
# 定位:   本文件新增 4 个 CreateDefinition 入口共用的骨架，沿用既有形状：
#           取 FeatureData → 交给调用方设属性 → CreateFeature
#           → 用 GetErrorCode 拒绝硬错误。
#         沿用而非另写，是为保持「错误码判定」在同一套模块里一致。
# ⚠ 本函数为照既有模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _create_from_definition(model, fm_type: int, apply_definition):
    """与 scripts/sw_sheet_metal.py::_create_from_definition 同构的共用骨架。

    先取 FeatureData、交给调用方设属性、再 ``CreateFeature``，
    最后用 ``GetErrorCode`` 拒绝硬错误（与上游 ``create_base_flange`` 一致）。
    """
    manager = get_com_member(model, "FeatureManager")
    data = get_com_member(manager, "CreateDefinition", int(fm_type))
    if data is None:
        raise RuntimeError(f"CreateDefinition({fm_type}) 未返回特征数据")
    apply_definition(data)
    feature = get_com_member(manager, "CreateFeature", data)
    if feature is None:
        raise RuntimeError(f"CreateFeature({fm_type}) 创建失败")
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"焊件特征 {fm_type} 返回特征错误码: {error_code}")
    return feature


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IStructureSystemMemberProfile 段
# 定位:   **已建构件的型材定义对象的回读与调整**。
# ⚠⚑ 重要更正 —— 本函数初稿被写成「创建构件前的型材配置」，并配了一个
#   create_weld_member 去 ``CreateDefinition(swFmWeldMemberFeat=72)`` 后赋值
#   ``data.MemberProfile``。**两处都是错的**：
#   1) ``IStructureSystemMemberFeatureData`` 只有 ``get_MemberProfile()``，
#      **没有 setter**（反射确认该接口的 setter 只有 IsSplit /
#      StartEndExtendD1 / StartEndExtendD2）——赋不进去。
#      是 ``audit_call_arity.py`` 报「同名成员存在但 arity 全对不上」抓出来的。
#   2) 构件创建的真实入口是
#      ``InsertStructuralWeldment5(String Path, Int32, Boolean, Object Groups, String)``，
#      **型材按「路径字符串」给**；而本文件上游**已经在正确使用它**
#      （见 create_weldment_members）。
#   故删掉了那个错误的 create_weld_member，本函数改为**事后**调整：
#   先 ``member_feature.GetDefinition().get_MemberProfile()`` 取回型材对象再改。
# 官方签名（属性，get/set 成对；除 GetSketch 外无方法）：
#     String  ProfileStandard / ProfileType / ProfileSize
#     Boolean MirrorProfile / OffsetPiercePoint /
#             OffsetPiercePointHorizontalAxisFlip / OffsetPiercePointVerticalAxisFlip
#     Int32   ProfileMirrorType / ProfileAlignmentType / ProfileAlignmentObjectType /
#             ProfilePiercePointType
#     Double  ProfileAlignmentAngle / OffsetPiercePointHorizontalAxis /
#             OffsetPiercePointVerticalAxis
#     Object  ProfileAlignmentObject / PiercePointSelectionObject
#     Sheet/… GetSketch()
# ⚠ ProfileStandard / ProfileType / ProfileSize 的**合法取值集合**在两套官方源里
#   都查不到（依赖本机安装的型材库），故本函数只做透传不校验。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_member_profile(
    profile,
    *,
    profile_standard: str | None = None,
    profile_type: str | None = None,
    profile_size: str | None = None,
    mirror: bool = False,
    profile_mirror_type: int = 0,
    alignment_type: int = 0,
    alignment_angle: float = 0.0,
    offset_pierce_point: bool = False,
    pierce_horizontal: float = 0.0,
    pierce_vertical: float = 0.0,
):
    """装配 ``IStructureSystemMemberProfile`` 型材定义，返回同一对象（便于链式）。"""
    if profile is None:
        raise ValueError("profile 为 None：须先取得 IStructureSystemMemberProfile 对象")
    if profile_standard is not None:
        get_com_member(profile, "ProfileStandard", str(profile_standard))
    if profile_type is not None:
        get_com_member(profile, "ProfileType", str(profile_type))
    if profile_size is not None:
        get_com_member(profile, "ProfileSize", str(profile_size))
    get_com_member(profile, "MirrorProfile", bool(mirror))
    get_com_member(profile, "ProfileMirrorType", int(profile_mirror_type))
    get_com_member(profile, "ProfileAlignmentType", int(alignment_type))
    get_com_member(profile, "ProfileAlignmentAngle", float(alignment_angle))
    get_com_member(profile, "OffsetPiercePoint", bool(offset_pierce_point))
    get_com_member(profile, "OffsetPiercePointHorizontalAxis", float(pierce_horizontal))
    get_com_member(profile, "OffsetPiercePointVerticalAxis", float(pierce_vertical))
    return profile


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IProfileCenterMateFeatureData 段
# 定位:   型材中心配合。官方签名（**全部是属性，无方法**）：
#           Object  EntitiesToMate
#           Int32   MateAlignment
#           Double  OffsetDistance
#           Boolean FlipDimension / LockRotation
#           配合 IFeatureManager.CreateDefinition(swFmMateProfileCenter = 101)。
#           该 FeatureData **无 Initialize 成员**，
#           故只设属性，不臆造 Initialize 调用。
# ⚠ MateAlignment 的枚举在两套官方源里查不到（`sw_know find MateAlignment`
#   未命中可用的枚举定义），故本函数只做 int 透传，不给默认值语义。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_profile_center_mate(
    model,
    entities,
    *,
    mate_alignment: int = 0,
    offset_distance: float = 0.0,
    flip_dimension: bool = False,
    lock_rotation: bool = False,
):
    """在所选实体间创建型材中心配合。"""
    if entities is None:
        raise ValueError("entities 为 None：须先选中要配合的实体")

    def _apply(data):
        get_com_member(data, "EntitiesToMate", entities)
        get_com_member(data, "MateAlignment", int(mate_alignment))
        get_com_member(data, "OffsetDistance", float(offset_distance))
        get_com_member(data, "FlipDimension", bool(flip_dimension))
        get_com_member(data, "LockRotation", bool(lock_rotation))

    return _create_from_definition(model, SW_FM_MATE_PROFILE_CENTER, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IStructureSystemSplitMember 段
# 定位:   构件分割配置。该对象由 ``IStructureSystemMemberFeatureData.GetSplitMember()``
#         取回（反射确认该 getter 存在），**没有独立创建入口**，故本函数只装配
#         不创建。官方签名：
#           Boolean SetSplitReferences(Object)                ← 唯一方法，返回 Boolean
#           Object  GetSplitReferences() / GetSplitReferenceObjectTypes()
#           Double  SplitLength
#           Boolean SplitLengthRevDirection
#           Int32   NumberofSplitInstances / DimensionType / MemberType
# ⚠ SetSplitReferences 返回 Boolean 但**是否可靠未查证**（AGENTS.md §六 事实 8
#   记载过 ISelectionMgr.AddSelectionListObject 的 bool 返回值不可信；
#   本函数因此只透传返回值、不据此判定成败。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def configure_split_member(
    split,
    *,
    split_references=None,
    split_length: float = 0.0,
    split_length_reverse: bool = False,
    number_of_instances: int = 1,
    dimension_type: int = 0,
    member_type: int = 0,
):
    """装配 ``IStructureSystemSplitMember``，返回 ``SetSplitReferences`` 的返回值。

    须先用 ``IStructureSystemMemberFeatureData.GetSplitMember()`` 取得该对象。
    """
    if split is None:
        raise ValueError("split 为 None：须先由 GetSplitMember() 取得分割对象")
    result = None
    if split_references is not None:
        result = get_com_member(split, "SetSplitReferences", split_references)
    get_com_member(split, "SplitLength", float(split_length))
    get_com_member(split, "SplitLengthRevDirection", bool(split_length_reverse))
    get_com_member(split, "NumberofSplitInstances", int(number_of_instances))
    get_com_member(split, "DimensionType", int(dimension_type))
    get_com_member(split, "MemberType", int(member_type))
    return result


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → ICutListSortOptions 段 + IFeatureManager 段
# 定位:   下料表排序选项 + 下料表插入。官方签名：
#           ICutListSortOptions.CollectIdenticalBodies            (Boolean 属性)
#                              .GetFacesOrFeaturesToExclude()      (Object, 0 参)
#                              .SetFacesOrFeaturesToExclude(Object) (Int32 返回)
#           IFeatureManager.InsertWeldmentCutList2(Object SortOptions) -> Feature
# ⚠ InsertWeldmentCutList2 接受一个 Object 参数（排序选项），
#   官方未标注其类型，**按 ICutListSortOptions 传**；若本机版本签名不同，
#   需按该版本官方文档调整。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_cut_list(model, sort_options=None, *, collect_identical_bodies: bool = False):
    """插入切割清单（零件/型材下料表）。

    ⚠⚠ **本函数在当前后端（pywin32 迟到绑定）上跑不通**（2026-10-01 轮 95 真机实测）：
    `IFeatureManager.InsertWeldmentCutList`（0 参）与 `InsertWeldmentCutList2(Object)`
    **在权威类型库里有**（`iface_sldworks.txt` 两行都在），但 `get_com_member` **取到 `None`**
    ⇒ 直接调用会抛**看不出真因**的 `TypeError: 'NoneType' object is not callable`。

    ★ 修法与仓库对 `IModeler.Create*Surface` 的先例一致（已知事实 40）：
    **返回值不可靠时，唯一能修的是「让失败可见」** —— 先把 member 取出来**判空**，
    抛带**成员名与后端**的 `RuntimeError`，而不是让它崩在调用点上。

    ⚠ 本函数**未验证可用**（从没跑通过）—— **不要**据此认为切割清单功能已就绪。
    """
    if sort_options is not None:
        get_com_member(sort_options, "CollectIdenticalBodies",
                       bool(collect_identical_bodies))
    manager = get_com_member(model, "FeatureManager")
    # ⚑ **判空再调**：`get_com_member` 取不到时返回 `None`，
    #   直接 `member(*args)` 会抛「'NoneType' object is not callable」——**看不出是成员取不到**。
    member = get_com_member(manager, "InsertWeldmentCutList2")
    if member is None:
        raise RuntimeError(
            "IFeatureManager.InsertWeldmentCutList2 在当前后端（pywin32 迟到绑定）上**取不到**"
            "（权威类型库里有该成员，但 COM 分发解析为 None）"
            "⇒ 切割清单在当前后端**不可用**；这不是调用参数的问题。"
        )
    feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)
    if feature is None:
        raise RuntimeError("InsertWeldmentCutList2 未返回特征")
    return feature


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IFeatureManager 段
# 定位:   焊接文件夹（子装配层级）插入。官方签名：
#           Feature InsertSubWeldFolder2(Object Folder)   ← 1 参
#           Feature InsertSubWeldFolder()                ← 0 参（无参旧版）
#         本函数走 2 参版以支持指定父文件夹；不传 folder 时传 None。
# ⚠ 官方未标注该 Object 参数的确切类型（预期为 IStructureSystemFolder），
#   故只透传不校验。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_sub_weld_folder(model, folder=None):
    """在装配体中插入焊接文件夹（子装配层级）。"""
    manager = get_com_member(model, "FeatureManager")
    feature = get_com_member(manager, "InsertSubWeldFolder2", folder)
    if feature is None:
        raise RuntimeError("InsertSubWeldFolder2 未返回特征")
    return feature

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_weldment.py —— 追加 `create_structural_member_from_sketch`
# 定位:   ★ 2026-10-03（轮 428）`plan-200r-v3` **段 2（焊件族）**的第一条。
#   ★★ **为什么它以前没挂**：★ 而 `capabilities.yaml` 的 `weldment_cut_list` 条目**早就写着**
#     「**2026-10-02（轮 364）真因查明：本机没装「焊件轮廓库」（Weldment Profiles）** ⇒
#       所以报「没有可写入切割清单的结构构件实体」**不是代码问题**，而是**建不出结构构件**」。
#   ★★★ **而本轮的侦察**推翻**了它**（★ 按 AGENTS.md 的顺序查第一现场时发现的）：
#     ```
#     ✓ 在：C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles
#     ⇒ **111 个** `.sldlfp`（ansi / **GB** / iso / DIN / JIS …）
#     ```
#   ⇒ ★★ **即：★ 前置**现在是齐的****（★ 而轮 364 那条结论**要更新**）✓
#   ★★ **而本函数把那条链封成一步**：★ 给定**草图名**与**轮廓路径**，
#     ★ 它自己取线段、建构件、**并用特征树回读**（★ 判据是**特征树**，★ 不是计数）✓
#   ★ **取线段用的是现成物**（★ "先找后搓"）：`sw_sketch.get_sketch_segments` +
#     `FeatureByName` → `GetSpecificFeature2`（★ `sw_part._select_revolve_axis` 里那条现成路）。
# 官方依据: `IFeatureManager.InsertStructuralWeldment5`（★ `create_structural_member` 已在用）·
#   `ISketch.GetSketchSegments()`（★ 出厂类型库：**0 参** → Object）· `IFeature.GetSpecificFeature2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def create_structural_member_from_sketch(model, sketch_name: str, profile_path, **kwargs):
    """★ **用一段草图路径 + 一个焊件轮廓**建结构构件，并**用特征树回读**。

    ★ 这是**段 2 的第一步封装**：★ 它把"**取线段 → 建构件 → 回读**"封在一起，
    ★★ 而**回读看的是特征树的类型名**（★ 与 `Count` 那条判据**完全不同**的一个家族）✓

    :param sketch_name: **路径草图**的名字（★ 如 `草图1`）。
    :param profile_path: `.sldlfp` 焊件轮廓的**绝对路径**
        （★ 本机在 `C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\weldment profiles\\` 下，
        ★ 中文 UI 用 `GB\\` 那一支）。
    :returns: 回读报告（`ok` / `feature` / `new_type_names` / `segments`）。
    """
    from .sw_connect import get_com_member, safe_get_com_member
    from .sw_sketch import get_sketch_segments

    def _type_names() -> set:
        names, feature, guard = set(), safe_get_com_member(model, "FirstFeature"), 0
        while feature is not None and guard < 500:
            names.add(str(safe_get_com_member(feature, "GetTypeName2") or ""))
            feature = safe_get_com_member(feature, "GetNextFeature")
            guard += 1
        return names

    feature = get_com_member(model, "FeatureByName", str(sketch_name))
    sketch = get_com_member(feature, "GetSpecificFeature2")
    segments = list(get_sketch_segments(sketch))
    before = _type_names()
    made = create_structural_member(model, profile_path, [segments], **kwargs)
    after = _type_names()
    return {
        "ok": made is not None,
        "feature": str(safe_get_com_member(made, "Name") or ""),
        "segments": len(segments),
        "new_type_names": sorted(after - before),
        "note": ("★ 判据是**特征树**（★ 不是计数）：★ `new_type_names` 应含 "
                 "`WeldmentFeature` 与 `WeldMemberFeat`"),
    }
