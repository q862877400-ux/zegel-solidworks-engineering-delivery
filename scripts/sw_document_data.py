"""SolidWorks 参数与自定义属性操作。

本模块只封装已由 SolidWorks 2024 Interop 和官方 API Help 核对的接口：
``IDimension.SetSystemValue3`` 与 ``ICustomPropertyManager.Add3/Get6``。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_document_data.py —— 本文件（**轮 145 的命名迁移**）。
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

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

try:
    from .sw_connect import get_com_member, call_com_member, save_document
    from .sw_preflight import import_com_dependencies
except ImportError:
    from sw_connect import get_com_member, call_com_member, save_document
    from sw_preflight import import_com_dependencies


pythoncom, _win32com, VARIANT = import_com_dependencies()

PROPERTY_TYPES = {
    "number": 3,
    "double": 5,
    "yes_no": 11,
    "text": 30,
    "date": 64,
}
SET_VALUE_MODES = {
    "current": 1,
    "all": 2,
    "specific": 3,
}
SET_VALUE_STATUS = {
    0: "successful",
    1: "failure",
    2: "invalid_value",
    3: "driven_dimension",
    4: "model_not_loaded",
    5: "frozen_feature_owner",
}


def _configuration_names(model) -> list[str]:
    """返回文档配置名，兼容 COM 返回 tuple/list/None。"""
    names = get_com_member(model, "GetConfigurationNames")
    return [str(name) for name in (names or [])]


def _resolve_configuration_name(names: Sequence[str], requested: str) -> str | None:
    """@brief 按 SolidWorks 配置名不区分大小写语义返回实际名称。"""
    matches = [str(name) for name in names if str(name).casefold() == requested.casefold()]
    if len(matches) > 1:
        raise RuntimeError(f"配置名大小写匹配不唯一: {requested}")
    return matches[0] if matches else None


def _active_configuration_name(model) -> str:
    """@brief 返回当前活动配置名；接口不可用时返回空字符串。"""
    try:
        manager = get_com_member(model, "ConfigurationManager")
        active = get_com_member(manager, "ActiveConfiguration")
        return str(get_com_member(active, "Name") or "")
    except Exception:
        return ""


def inspect_configurations(model) -> dict[str, Any]:
    """@brief 读取配置族清单并返回当前配置，配置修改仍需人工复核。"""
    names = _configuration_names(model)
    current = _active_configuration_name(model)
    return {
        "status": "pilot" if names else "blocked",
        "configurations": names,
        "active_configuration": current,
        "review_required": True,
        "limitations": ["未执行设计表创建/编辑和大型配置族批量变更", "配置间尺寸、属性、抑制状态和几何差异仍需人工复核"],
    }


def activate_configuration(
    model,
    configuration_name: str,
    *,
    rebuild: bool = True,
    save: bool = False,
) -> dict[str, Any]:
    """@brief 激活现有配置并通过活动配置名回读验证。"""
    requested_name = str(configuration_name).strip()
    if not requested_name:
        raise ValueError("configuration_name 不能为空")
    names = _configuration_names(model)
    name = _resolve_configuration_name(names, requested_name)
    if name is None:
        raise LookupError(f"找不到配置: {requested_name}")

    before = _active_configuration_name(model)
    api_called = before != name
    api_return = bool(get_com_member(model, "ShowConfiguration2", name)) if api_called else None
    after = _active_configuration_name(model)
    readback_verified = after == name
    api_success = readback_verified
    rebuild_success = bool(call_com_member(model, "EditRebuild3")) if rebuild and readback_verified else readback_verified
    save_success = bool(save_document(model)) if save and readback_verified and rebuild_success else not save
    success = readback_verified and rebuild_success and save_success
    return {
        "success": success,
        "configuration": name,
        "requested_configuration": requested_name,
        "before": before,
        "after": after,
        "api_called": api_called,
        "api_return": api_return,
        "api_success": api_success,
        "readback_verified": readback_verified,
        "rebuild_success": rebuild_success,
        "save_requested": save,
        "save_success": save_success,
        "review_required": True,
    }


def create_configuration(
    model,
    configuration_name: str,
    *,
    comment: str = "",
    alternate_name: str = "",
    options: int = 0,
    if_exists: str = "reuse",
    activate: bool = True,
    rebuild: bool = True,
    save: bool = False,
) -> dict[str, Any]:
    """@brief 使用 AddConfiguration3 创建配置，并校验清单及活动配置回读。

    ``options`` 对应官方 ``swConfigurationOptions2_e`` 位掩码。默认值 0 保持
    SolidWorks 默认行为；非零值必须由调用者基于目标版本枚举显式提供。
    """
    requested_name = str(configuration_name).strip()
    if not requested_name:
        raise ValueError("configuration_name 不能为空")
    if if_exists not in {"reuse", "error"}:
        raise ValueError("if_exists 只支持 reuse 或 error")
    if int(options) < 0:
        raise ValueError("options 不能为负数")

    before_names = _configuration_names(model)
    existing_name = _resolve_configuration_name(before_names, requested_name)
    existed = existing_name is not None
    name = existing_name or requested_name
    if existed and if_exists == "error":
        raise FileExistsError(f"配置已存在: {name}")

    created = None if existed else get_com_member(
        model,
        "AddConfiguration3",
        name,
        str(comment),
        str(alternate_name),
        int(options),
    )
    if not existed and created is None:
        raise RuntimeError(f"AddConfiguration3 未返回配置对象: {name}")

    after_names = _configuration_names(model)
    listed_name = _resolve_configuration_name(after_names, name)
    listed = listed_name is not None
    name = listed_name or name
    activation = (
        activate_configuration(model, name, rebuild=rebuild, save=False)
        if activate and listed
        else None
    )
    if activation:
        rebuild_success = bool(activation["rebuild_success"])
    elif rebuild and listed:
        rebuild_success = bool(call_com_member(model, "EditRebuild3"))
    else:
        rebuild_success = listed
    active_verified = activation["readback_verified"] if activation else True
    save_success = bool(save_document(model)) if save and listed and rebuild_success and active_verified else not save
    success = listed and rebuild_success and active_verified and save_success
    return {
        "success": success,
        "configuration": name,
        "requested_configuration": requested_name,
        "created": not existed,
        "reused": existed,
        "listed_after_create": listed,
        "configurations_before": before_names,
        "configurations_after": after_names,
        "options": int(options),
        "activation": activation,
        "save_requested": save,
        "save_success": save_success,
        "review_required": True,
    }


def _document_length_unit_scale(model) -> float:
    """★ 从**文档单位**推出「系统值 → 毫米」的倍数（★ 而不是硬编码 1000）。

    ★★★★ **为什么需要它（★ 2026-10-04 真机定案）**：★ `GetSystemValue3` / `SetSystemValue3`
      **吃的就是文档单位** —— ★ 真机实测（`tools/probe_dimension_unit.py` + 独立交叉核
      `output/extrude-depth-unit-evidence.json`）：
        · ★ 文档 `GetUnits() = [**0**, …]` ⇒ **`swLengthUnit_e = 0 = swMM`** ✓
        · ★ 一个**厚 20 mm** 的板 ⇒ `GetSystemValue3` 原始回 **`(20.0,)`** ✓
        · ★ 而**同一次**建出来的实体 `size = [100, 60, **20**]` ⇒ ★ **真的是 20 mm** ✓
      ⇒ ★★★ **所以在这份文档上，系统值 == 毫米 ⇒ 倍数应为 `1.0`，★ 而不是 `1000.0`** ✓
    ★★ **旧代码硬编码 `× 1000`** ⇒ ★ 把 20 mm 读成 **20000 mm**（★ 大 1000 倍）✓
    ★ **回退**：★ 读不到 ⇒ **维持旧行为 `1000.0`**（★ 米）✓
    """
    try:
        from sw_connect import get_com_member as _g
        raw = _g(model, "GetUnits")
        if raw is None:
            return 1000.0
        seq = list(raw)
        #: ★ `swLengthUnit_e`：0=swMM · 1=swCM · 2=swM · 3=swINCHES · 4=swFEET …
        return {0: 1.0, 1: 10.0, 2: 1000.0, 3: 25.4, 4: 304.8}.get(int(seq[0]), 1000.0)
    except Exception:                                                     # noqa: BLE001
        return 1000.0


def _dimension_value_mm(dimension, configuration_name: str | None = None, *,
                        model=None) -> float:
    """读取尺寸系统值并转为毫米。

    ★★★★ 2026-10-03（接手轮）**换走后继入口 + 处理"返回值是数组"** ——
      ★ 原来是 `dimension.GetSystemValue2(名)` 与 `get_com_member(dimension, "SystemValue")`，
        ★★ 两条都废弃（★ 官方逐字见下）。
      ★ `types/IDimension/GetSystemValue2.md` 逐字：
        「**Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].**」
      ★ `types/IDimension/SystemValue.md` 逐字：
        「**Obsolete. Superseded by [[IDimension::GetSystemValue3]], [[IDimension::IGetSystemValue3]], …**」
      ★★ 后继 `GetSystemValue3(WhichConfigurations, Config_names)`（2 参）；
        ★ `enums/swInConfigurationOpts_e.md` ⇒ **`swThisConfiguration = 1`** · `swAllConfiguration = 2`
        · **`swSpecifyConfiguration = 3`**。
      ★★★ **`Config_names` 传**空 VARIANT**** —— ★ 官方例子逐字
        （`examples/Change_Dimensions_of_Gear_Mate_Example_VB.md`）：
        ```vbnet
        dimValue_1 = swDim_1.GetSystemValue3(swInConfigurationOpts_e.swThisConfiguration, Empty)
        errors = swDim_1.SetSystemValue3(dimValue_1(0), …)   ' ★★★ 注意它取 (0)
        ```
      ★★★★ **最关键的一条**：★ **新入口回的是**数组/元组**，★ 不是标量** ⇒
        ★ 本函数原来是 `float(…)` 直接吃 ⇒ ★★ **换过去会 `TypeError`** ⇒
        ★ **必须多取一层 `[0]`** ✓（★ 本会话在 `GetExcludeFromBOM2` 上也见到同一形态）
      ★★★★★ 真机证据（`tools/probe_getsystemvalue_on_existing.py` ·
        `output/getsystemvalue-on-existing-evidence.json`，★ 用**仓里现成**的
        `output/_probe_drawing_part.SLDPRT` 上的真实尺寸 `D1@凸台-拉伸1`）：
        | ★ 调用 | ★ 读数 |
        |---|---|
        | 旧 `GetSystemValue2(名)` | ★ **0.01** |
        | 旧 `SystemValue` | ★ **0.01** |
        | ★★ 新 `GetSystemValue3(1, 空VARIANT)` | ★ **`(0.01,)`** |
        | ★★ 新 `GetSystemValue3(2, 空VARIANT)` | ★ **`(0.01,)`** |
        ⇒ ★★ **三者数值一致、且新的是元组 ⇒ 可换** ✓
    """
    #: ★★★★ 2026-10-04（接手轮）**修掉一个"从来跑不通"的导入** ——
    #:   ★ 病灶：★ 原来写 `from sw_connect import …`（★ **裸顶层名**）⇒
    #: ★★ 而测试用 `from scripts import sw_document_data` ⇒ ★ **`sw_connect` 不在 `sys.p
    #: ath`** ⇒
    #:     ★★★ `ModuleNotFoundError: No module named 'sw_connect'` ✓
    #:   ★★ **实测确认它是存量**（★ 不是本轮引入）：★ `git stash` 掉本轮全部改动后，
    #:     `pytest tests/test_sw_document_data.py` **同样 2 failed / 8 passed** ✓
    #: ★★★ 修法：★ **与模块其他部分一致**（★ `try: from .sw_connect … / except ImportErr
    #: or: …`）✓
    try:
        from .sw_connect import create_empty_dispatch_variant as _empty
        from .sw_connect import get_com_member as _g
    except ImportError:                                                   # pragma: no cover
        from sw_connect import create_empty_dispatch_variant as _empty     # type: ignore
        from sw_connect import get_com_member as _g                        # type: ignore

    if configuration_name:
        raw = _g(dimension, "GetSystemValue3", 3, [configuration_name])   #: ★ swSpecifyConfiguration
    else:
        raw = _g(dimension, "GetSystemValue3", 1, _empty())               #: ★ swThisConfiguration
    #: ★★ 新入口回**数组** ⇒ 取第一个（★ 官方例子也是这么取的：`dimValue_1(0)`）
    if isinstance(raw, (list, tuple)):
        raw = raw[0] if raw else 0.0
    #: ★★★★ 2026-10-04（接手轮）**修掉「硬编码 ×1000」** —— ★★ 它假定文档单位是**米**、
    #:   而**本机新建文档的单位是**毫米****（★ 真机实测 `GetUnits() = [0, 1, 8, 2, 0]`，
    #:   ★ 第 1 个 `swLengthUnit_e = 0 = swMM`）✓
    #:   ★★★ **真机证据（`tools/probe_dimension_unit.py`）**：★ 一个**厚 20 mm** 的板，
    #: ★ `GetSystemValue3` 原始回 **`(20.0,)`** ⇒ ★★ **它回的是**文档单位**（毫米），★ 
    #: 不是米** ✓
    #:   ★★★ **而另一份证据**（`output/extrude-depth-unit-evidence.json`）**独立确认**：
    #: ★ `extrude_boss(model, "Sketch1", 20.0)` 建出来的实体 **`size = [100, 60, **20**]
    #: `**
    #:    ⇒ ★★ **实体真的是 20 mm 厚** ⇒ ★ **`GetSystemValue3` 回 20.0 就是毫米** ✓
    #:   ⇒ ★ 修法：★ **按文档单位换算**（★ 读一次 `GetUnits()`，★ 不再假定）✓
    #: ★ 而 `model` 为 `None`（★ 老调用方）⇒ ★ **回退到旧行为 `× 1000`**（★ 不破坏既有调
    #: 用）✓
    scale = _document_length_unit_scale(model) if model is not None else 1000.0
    return float(raw) * scale


def update_dimension_mm(
    model,
    dimension_name: str,
    value_mm: float,
    *,
    configuration_mode: str = "current",
    configuration_names: Sequence[str] | None = None,
    rebuild: bool = True,
    save: bool = False,
) -> dict[str, Any]:
    """修改命名尺寸并返回可审计证据。

    ``configuration_mode`` 支持 ``current``、``all``、``specific``；specific
    必须提供配置名。SolidWorks API 内部单位为米。
    """
    if not dimension_name.strip():
        raise ValueError("dimension_name 不能为空")
    if value_mm <= 0:
        raise ValueError("value_mm 必须大于 0")
    if configuration_mode not in SET_VALUE_MODES:
        raise ValueError(f"不支持的配置范围: {configuration_mode}")

    dimension = model.Parameter(dimension_name)
    if dimension is None:
        raise LookupError(f"找不到尺寸: {dimension_name}")

    requested_names = [str(name).strip() for name in (configuration_names or []) if str(name).strip()]
    if configuration_mode == "specific" and not requested_names:
        raise ValueError("specific 模式必须提供 configuration_names")
    if configuration_mode == "all":
        evidence_names = _configuration_names(model)
    elif configuration_mode == "specific":
        evidence_names = requested_names
    else:
        evidence_names = []

    #: ★★★★ 2026-10-04（接手轮）**修正换算 —— 两处一起改**：
    #:   ★ **病灶**：★ `_dimension_value_mm` 硬编码 `× 1000`、★ 而这里硬编码 `/ 1000` ⇒
    #:     ★★ **两个相反方向的错、★ 互相掩盖**（★ 读回来的值**看起来对**）✓
    #:   ★★★ **真机定案**：★ `GetSystemValue3` / `SetSystemValue3` **吃的就是文档单位**
    #: （★ 实测：★ 毫米文档 + 厚 20mm 的板 ⇒ 回 `(20.0,)`；★ 而实体 `size=[100,60,**20**
    #: ]`）✓
    #:   ★★ 而 `model` 是**本函数已有**的入参 ⇒ ★ 用它读单位；★ `None` ⇒ 回退旧行为 ✓
    _scale = _document_length_unit_scale(model)
    before = (
        {name: _dimension_value_mm(dimension, name, model=model) for name in evidence_names}
        if evidence_names
        else {"current": _dimension_value_mm(dimension, model=model)}
    )
    names_variant = (
        VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_BSTR, requested_names)
        if configuration_mode == "specific"
        else None
    )
    status_code = int(
        dimension.SetSystemValue3(
            float(value_mm) / _scale,
            SET_VALUE_MODES[configuration_mode],
            names_variant,
        )
    )
    rebuild_success = (
        bool(call_com_member(model, "EditRebuild3"))
        if rebuild and status_code == 0
        else status_code == 0
    )
    after = (
        {name: _dimension_value_mm(dimension, name, model=model) for name in evidence_names}
        if evidence_names
        else {"current": _dimension_value_mm(dimension, model=model)}
    )
    save_success = bool(save_document(model)) if save and status_code == 0 and rebuild_success else not save
    success = status_code == 0 and rebuild_success and save_success
    return {
        "success": success,
        "dimension": dimension_name,
        "configuration_mode": configuration_mode,
        "configuration_names": requested_names,
        "requested_mm": float(value_mm),
        "before_mm": before,
        "after_mm": after,
        "set_status": status_code,
        "set_status_label": SET_VALUE_STATUS.get(status_code, f"unknown_{status_code}"),
        "rebuild_success": rebuild_success,
        "save_requested": save,
        "save_success": save_success,
    }


def _property_manager(model, configuration_name: str = ""):
    manager = model.Extension.CustomPropertyManager(configuration_name)
    if manager is None:
        scope = configuration_name or "文件级"
        raise RuntimeError(f"无法取得 {scope} 自定义属性管理器")
    return manager


def read_custom_property(model, name: str, *, configuration_name: str = "") -> dict[str, Any]:
    """读取一个文件级或配置级自定义属性。"""
    manager = _property_manager(model, configuration_name)
    raw_value = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    resolved_value = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    was_resolved = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    is_linked = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    status = int(manager.Get6(name, False, raw_value, resolved_value, was_resolved, is_linked))
    return {
        "name": name,
        "configuration": configuration_name,
        "status": status,
        "exists": status != 1,
        "raw": str(raw_value.value or ""),
        "resolved": str(resolved_value.value or ""),
        "was_resolved": bool(was_resolved.value),
        "is_linked": bool(is_linked.value),
    }


def set_custom_properties(
    model,
    properties: Mapping[str, Any],
    *,
    configuration_name: str = "",
    property_type: str = "text",
    save: bool = False,
) -> dict[str, Any]:
    """写入文件级或配置级属性，并逐项回读验证。"""
    if not properties:
        raise ValueError("properties 不能为空")
    if property_type not in PROPERTY_TYPES:
        raise ValueError(f"不支持的属性类型: {property_type}")
    manager = _property_manager(model, configuration_name)
    results = []
    for raw_name, raw_value in properties.items():
        name = str(raw_name).strip()
        if not name:
            raise ValueError("属性名不能为空")
        value = str(raw_value)
        add_status = int(manager.Add3(name, PROPERTY_TYPES[property_type], value, 2))
        readback = read_custom_property(model, name, configuration_name=configuration_name)
        verified = add_status == 0 and readback["exists"] and readback["raw"] == value
        results.append({
            "name": name,
            "requested": value,
            "add_status": add_status,
            "verified": verified,
            "readback": readback,
        })
    save_success = bool(save_document(model)) if save and all(item["verified"] for item in results) else not save
    return {
        "success": all(item["verified"] for item in results) and save_success,
        "configuration": configuration_name,
        "property_type": property_type,
        "properties": results,
        "save_requested": save,
        "save_success": save_success,
    }


# ── 规格 209（规格 207 的 18 条采纳候选 · B1 批）：**引用文档（依赖清单）** ───────────
# ─────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_document_data.py —— 追加 `document_dependencies`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B1 批** · 外部项目 idx **244 `refere
#           nced_documents`**。
#   ★ 裁决书（`docs/recon-207/adjudication.md` §一）逐字：「补齐 `solidworks_pack_and_go`
# 一直枚举却不暴露的**读侧**」✓ ★ 落点由我先确认本模块职责后选定（该模块 = 文档数据读/写
# ）。
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
#   · `C:\swapi\types\ISldWorks\GetDocumentDependencies2.md` ——
# `System.object GetDocumentDependencies2(System.string Document, System.bool Traversefl
# ag,
#      System.bool Searchflag, System.bool AddReadOnlyInfo)`
# ★ `## Returns` 逐字：「Array of strings with **two strings for each document** … ① Fil
# e name
# ② Filename with the complete pathname; this combination repeats itself for each depend
# ent file」
# ★ `## Remarks` 逐字 ①：「calling this method on a drawing document returns a list of a
# ll the
#       part and assemblies used in the drawing」②「**Suppressed components are recognized and
# returned by this method as a dependent file.**」③ ★★ **盲区**：「Be aware that **Libra
# ry
# features are completely unassociated**. … Therefore, **this method would not return Li
# brary
#       features**.」④ `AddReadOnlyInfo=True` 时每个文档后**多一个** `"Read-Only"` 串
# （★ 且**只读**的那个才有，非只读的是**空串** —— 官方例子逐字 `… "SubAssem1", "c:\…", "
# " `）
#   · ⚠ `C:\swapi\types\ISldWorks\GetDocumentDependenciesCount.md` —— ★ 该页逐字写着
# **「Obsolete. Superseded by `ISldWorks::IGetDocumentDependenciesCount2`」** ⇒ ★★ 本函
# 数
# **不去调它**（★ `I` 前缀那族是给进程内 C++ 的指针变体，且我们**本来也不需要预取个数** 
# ——
#     `GetDocumentDependencies2` 一次就回**完整数组**）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **裁决书点名的硬约束**：「官方逐字：**Library features 不会返回** ⇒ doc **必须写明
# 这个盲区**
# （不写就是静默的错答案）」✓ ⇒ ★ 见 `LIMITATIONS`，且**随返回值一起**带出去（★ 不让调用
# 方漏读）。

#: ★ 本能力的**已知盲区**（★ 官方 `## Remarks` 逐字）—— ★ **随返回值一起回给调用方**
DOCUMENT_DEPENDENCIES_LIMITATIONS = (
    "★★ **库特征（Library features）不会出现在结果里** —— 官方 `GetDocumentDependencies2` 的 "
    "`## Remarks` 逐字：「Library features are completely unassociated. They do not require the "
    "library nor do they update when changes are made to the Library feature. Therefore, this "
    "method would not return Library features.」⇒ ★ **把本函数的清单当「完整依赖」是错的** ✓",
    "★ `Traverseflag=False` 只回**最上一层**：官方逐字「false if you want only the highest level "
    "within the dependencies」⇒ ★ 要**递归到零件**必须传 `traverse=True` ✓",
    "★ `Searchflag=True` 会**改变当前目录**（官方 NOTE 逐字：「then the current directory is set to "
    "the directory of the document file」）—— ★ 有副作用，默认 **False** ✓",
    "★ 官方原话「**Suppressed components are recognized and returned**」⇒ ★ **被压缩的组件也在清单里**，"
    "★ 别把「出现了」当成「生效了」 ✓",
    "★★★ **官方例子与真机读数不一致（本能力实测抓到，★ 照例子写判据会判反）**：官方例子说开了 "
    "`AddReadOnlyInfo` 之后，**非只读**的文档跟的是**空串** "
    "（逐字 `[ \"Part1\", \"C:\\temp\\Part1.SLDPRT\", \"Read-Only\", \"SubAssem1\", "
    "\"c:\\temp\\SubAssem1.SLDASM\", \"\" ]`）；"
    "★ 而**本机实测（2026-10-06，SW 2026 SP4.1）回的是字符串 `\"FALSE\"`** —— "
    "⇒ ★★ **若按「非空即只读」写判据，会把非只读的文档判成只读**（`bool(\"FALSE\")` 是 `True`）✓ "
    "⇒ ★ 本函数的 `read_only_flag` 于是**按白名单判**：`\"Read-Only\"` ⇒ `True`；"
    "`\"\"` / `\"FALSE\"` / `\"0\"` ⇒ `False`；**其余一律 `None`（不猜）** ✓ "
    "★ 原始串**原样**留在 `read_only` 字段里，调用方可以自己核 ✓",
)

#: ★ 只读信息串的**判读白名单**（★ 依据：官方例子给 `""`、本机实测给 `"FALSE"`）
READ_ONLY_TRUE_LITERAL = "read-only"
READ_ONLY_FALSE_LITERALS = ("", "false", "0")


def _read_only_flag(text):
    """★ 把只读信息串判成 `True` / `False` / `None`（**认不出就 `None`** —— ★ 不拿"非空"当判据）。"""
    token = str(text or "").strip().casefold()
    if token == READ_ONLY_TRUE_LITERAL:
        return True
    if token in READ_ONLY_FALSE_LITERALS:
        return False
    return None


def document_dependencies(
    sw_app,
    document: str,
    *,
    traverse: bool = True,
    search: bool = False,
    add_read_only_info: bool = False,
) -> dict[str, Any]:
    """★ **列出一个文档的引用（依赖）清单**（★ 官方 `ISldWorks::GetDocumentDependencies2`）。

    :param sw_app: `ISldWorks`（★ 本函数的注入键是 `sw_app` —— 官方成员在 `ISldWorks` 上，不在文档上）。
    :param document: 文档名（★ 官方 `Parameters` 逐字只有「Name of the document」⇒
        ★ 本函数**原样透传**、不替它猜要不要全路径）。
    :param traverse: `True` = 递归进所有被依赖的文件（官方 `Traverseflag`）。
    :param search: `True` = 用搜索规则找依赖（★ **会改当前目录** —— 见 `LIMITATIONS`）。
    :param add_read_only_info: `True` = 每个文档后**多一个**只读信息串（官方 `AddReadOnlyInfo`）。
    :returns: `{ok, document, count, entries: [{name, path, read_only}], raw, limitations, error}`

    ★ **判据（规则 6）**：官方返回值是**扁平字符串数组**（每个文档 **2** 个串、开了 `add_read_only_info`
    再加 **1** 个）⇒ ★ 本函数**先按官方声明的步长还原成记录**，**再校验**「数组长度能被步长整除」——
    ★ 除不尽 ⇒ `ok=False` 并**如实报**（★ 不硬凑、不猜哪个串是谁的）✓
    ★ 记录里 `read_only` 的语义**逐字照官方**：`"Read-Only"` 或**空串**（★ 空串 ≠ 未知，官方例子里
    非只读的文档就是空串）✓
    ★★ **而本机实测回的是 `"FALSE"`**（官方例子给的是空串）⇒ `read_only_flag` **按白名单判**、
    认不出就 `None`（★ 见 `LIMITATIONS` 第 5 条 —— **照例子写判据会判反**）✓
    """
    out: dict[str, Any] = {
        "ok": False, "document": str(document), "traverse": bool(traverse),
        "search": bool(search), "add_read_only_info": bool(add_read_only_info),
        "count": 0, "entries": [], "raw_len": None, "raw": None,
        "limitations": list(DOCUMENT_DEPENDENCIES_LIMITATIONS), "error": None,
        "★": "官方 Returns 逐字：每个文档 **2** 个串（名字 + 全路径）；"
             "`AddReadOnlyInfo=True` 时**再加 1** 个只读信息串（官方例子里非只读的是**空串**）",
    }
    if not str(document).strip():
        out["error"] = "document 不能为空（★ 官方 Parameters 只写「Name of the document」，本函数原样透传）"
        return out
    try:
        raw = get_com_member(sw_app, "GetDocumentDependencies2", str(document),
                             bool(traverse), bool(search), bool(add_read_only_info))
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    items = [str(x) for x in (raw or [])]
    out["raw"] = items
    out["raw_len"] = len(items)
    step = 3 if add_read_only_info else 2
    if not items:
        #: ★ 空数组**是合法读数**（无依赖文档）—— ★ 但要说清"这可能是真没依赖、也可能是
        #: 文档名不对"
        out["ok"] = True
        out["error"] = None
        out["note"] = ("返回**空数组**：★ 可能是该文档**确实没有依赖**（例如未保存的新零件），"
                       "★ 也可能是 `document` 这个名字 SW 找不到 ⇒ ★ 本函数**不区分这两种**（如实记）")
        return out
    if len(items) % step:
        out["error"] = ("官方声明的步长是 %d（每个文档 %s），而数组长度 %d **除不尽** ⇒ "
                        "★ 本函数不硬凑、不猜哪个串是谁的（如实报）"
                        % (step, "名字+全路径+只读信息" if add_read_only_info else "名字+全路径",
                           len(items)))
        return out
    entries = []
    for i in range(0, len(items), step):
        entry = {"name": items[i], "path": items[i + 1],
                 "read_only": (items[i + 2] if add_read_only_info else None)}
        entry["read_only_flag"] = (None if step == 2
                                   else _read_only_flag(entry["read_only"]))
        entries.append(entry)
    out["entries"] = entries
    out["count"] = len(entries)
    out["ok"] = True
    return out
