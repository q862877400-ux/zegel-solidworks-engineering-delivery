"""SolidWorks Composer 成本估算：ICostManager / ICostPart / ICostAnalysis 等封装。

能力域
    域 14 · 路由 / Composer / PDM（需许可证）—— 本文件是其中 **Composer 成本** 部分

模块分工（域 14）
----------------
    sw_routing.py     SolidWorks Routers 线束/管线路由（本仓库域 14 首份真实封装）
    sw_costing.py     （本文件）Composer 成本估算
    PDM（swdocumentmgr，296 接口 / 3771 成员）尚未覆盖

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_sldcostingapi.txt
      —— 对 SolidWorks.Interop.sldcostingapi.dll 的**纯元数据反射**
         （AGENTS.md §四.1③「读官方程序集，不是实测」）。
         实测规模：**28 接口 / 296 成员**（其中 12 个是接口、16 个是 coclass）。

接口族覆盖（本模块 4 个 / 全库 12 个接口）
    ICostManager(7) · ICostPart(13) · ICostAnalysis(23) · ICostingDefaults(22)
    另含 ICostBody(7) 的只读回读

⚠ 反射清单里有 16 个**成员数为 0** 的段（CostManager / CostPart /
  CostAnalysis / CostBody / CostBlankSize / CostAnalysisStructural /
  CostAnalysisSheetMetal / CostAnalysisPlastic / CostAnalysisMachining /
  CostAnalysisCasting / CostAnalysis3dPrinting / TemplateOverrides /
  CostingDefaults / CostFeature …）—— 那些是 **coclass**（具体类），
  成员定义在它对应的接口上。⇒ 取用时按接口类型标注。

⚠ **本族官方 CHM 没有文档页**（四册 CHM 里没有 costing 册），
  故**只有签名、没有参数语义**。各函数处逐条标注；不编「合理解释」。
  尤其 `CostingType` / `MarkUpType` / `BodyStatus` / `LengthUnit` 等
  整型取值的含义两套源都查不到 ⇒ 一律原样透出，不解释、不换算。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_costing.py —— 本文件自身
# 定位:   模块导出清单与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "COSTING_ARITY",
    "get_costing_defaults",
    "get_costing_model",
    "list_templates",
    "get_bodies",
    "get_body_count",
    "include_body",
    "set_costing_method",
    "create_cost_analysis",
    "get_cost_analysis",
    "update_cost_for_all_bodies",
    "set_lot_size",
    "set_markup",
    "read_cost_analysis",
    "set_default_lot_size",
    "set_default_template",
    "collect_costing_evidence",
]

#: 反射确认的实参个数（**不含**末尾 by-ref 出参）
COSTING_ARITY: dict[str, int] = {
    # ICostManager
    "Close": 0,
    "WaitForUIUpdate": 0,
    "GetTemplateCount": 1,
    "GetTemplatePathnames": 1,
    # ICostPart
    "GetBodyCount": 0,
    "GetBodies": 0,
    "IncludeBody": 2,
    "SetCostingMethod": 2,
    "GetCostingMethod": 1,
    "ActivateBody": 1,
    "CreateCostAnalysis": 1,
    "GetCostAnalysis": 0,
    "UpdateCostForAllBodies": 0,
    # ICostAnalysis
    "GetFirstCostFeature": 0,
    "GetSpecificAnalysis": 0,
    # ICostBody
    "AssignCustomCost": 1,
    "GetSWBody": 0,
    # ICostingDefaults
    "SetManufacturingMethod": 2,
    "SetMaterialClass": 2,
    "SetMaterialName": 2,
    "SetTemplateName": 2,
    "GetManufacturingMethod": 1,
    "GetMaterialClass": 1,
    "GetMaterialName": 1,
    "GetTemplateName": 1,
}


def _checked(target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = COSTING_ARITY.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("目标对象为 None")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldcostingapi interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt → ICostManager 段
# 定位:   成本管理器与模板枚举。官方签名逐条照抄：
#     Void   Close()                    ← **零参**
#     Void   WaitForUIUpdate()          ← **零参**
#     Int32  GetTemplateCount(Int32)    → 1
#     Object GetTemplatePathnames(Int32)→ 1
#     Object get_CostingModel()         ← **属性**（返回 CostingModel 对象）
#     Object get_CostingDefaults()      ← **属性**（返回 CostingDefaults coclass）
# ⚠ `GetTemplateCount` / `GetTemplatePathnames` 的 Int32 参数语义官方无文档
#   （是「页码」还是「类别」？）。本模块**只透传**，不设默认值。
# ⚠ 取用路径：CostManager 由 Composer 加载项给出（类似 Routers 的
#   `ISldWorks.GetAddInObject(<ProgID>)`）。**本机也没装 Composer**，
#   ProgID 查不到 ⇒ 本模块**接收调用方传入的对象**，不代为取得。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_costing_defaults(cost_manager):
    """取成本默认值对象（属性）。"""
    if cost_manager is None:
        raise ValueError("cost_manager 为 None")
    return get_com_member(cost_manager, "CostingDefaults")


def get_costing_model(cost_manager):
    """取成本模型对象（属性）。"""
    if cost_manager is None:
        raise ValueError("cost_manager 为 None")
    return get_com_member(cost_manager, "CostingModel")


def list_templates(cost_manager, category: int = 0):
    """取某类别的模板清单。⚠ Int32 的语义官方无文档。"""
    return _checked(cost_manager, "GetTemplatePathnames", int(category))


def close_costing(cost_manager) -> bool:
    """关闭成本管理器。**零参**。"""
    _checked(cost_manager, "Close")
    return True


def wait_for_ui_update(cost_manager) -> bool:
    """等待 UI 更新。**零参**（用于批处理脚本等计算完成）。"""
    _checked(cost_manager, "WaitForUIUpdate")
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ICostPart 段
# 定位:   零件级操作。官方签名逐条照抄：
#     Int32     GetBodyCount()                    ← **零参**
#     Object    GetBodies()                       ← **零参**
#     Int32     IncludeBody(String, Boolean)      → 2
#     CostBody  SetCostingMethod(String, Int32)   → 2
#     Int32     GetCostingMethod(String)          → 1
#     CostBody  ActivateBody(String, Int32&)     → 1 + by-ref
#     CostAnalysis CreateCostAnalysis(String)    → 1
#     CostAnalysis GetCostAnalysis()             ← **零参**
#     Object    UpdateCostForAllBodies()         ← **零参**
# ⚠ 反射里还有 `IUpdateCostForAllBodies(Int32)` 这种 I 前缀成员，
#   那是 COM 内部分发入口，**不提供给调用方**。
# ⚠ `SetCostingMethod` 第 2 参（Int32）与 `GetCostingMethod` 的取值
#   官方无文档；`IncludeBody` 的 Boolean 语义（是否累加？）也未注明。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_body_count(cost_part) -> int:
    """零件下的实体数。**零参**。"""
    return int(_checked(cost_part, "GetBodyCount") or 0)


def get_bodies(cost_part):
    """零件下的实体清单。**零参**。"""
    return _checked(cost_part, "GetBodies")


def include_body(cost_part, body_name: str, include: bool = True) -> int:
    """把某个实体纳入成本计算。"""
    return _checked(cost_part, "IncludeBody", str(body_name), bool(include))


def set_costing_method(cost_part, method_name: str, method: int):
    """设成本方法。⚠ Int32 的取值官方无文档。"""
    return _checked(cost_part, "SetCostingMethod", str(method_name), int(method))


def get_costing_method(cost_part, method_name: str) -> int:
    """读成本方法。"""
    return _checked(cost_part, "GetCostingMethod", str(method_name))


def create_cost_analysis(target, name: str):
    """建成本分析。``target`` 可为 ICostPart 或 ICostBody（两者都有此方法）。"""
    return _checked(target, "CreateCostAnalysis", str(name))


def get_cost_analysis(cost_part):
    """取该零件的成本分析。**零参**。"""
    return _checked(cost_part, "GetCostAnalysis")


def update_cost_for_all_bodies(cost_part):
    """对全部实体重算。**零参**。"""
    return _checked(cost_part, "UpdateCostForAllBodies")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ICostAnalysis 段
# 定位:   成本分析的参数与结果读取。官方签名逐条照抄：
#     Int32 get_CostingType() / get_LotSize() / get_MarkUpType() /
#           get_MassUnit() / get_LengthUnit() / get_TotalQuantity() /
#           get_UnitSystem()
#     Double get_MarkUpPercent()
#     String get_CostingTemplateName() / get_CurrencyCode() /
#            get_CurrencyName() / get_CurrencySeparator()
#     Void set_LotSize(Int32) / set_MarkUpType(Int32) /
#          set_MarkUpPercent(Double) / set_TotalQuantity(Int32)   ← **属性**
#     Double GetManufacturingCost() / GetMaterialCost() / GetSetupCost() /
#            GetTotalCostToCharge() / GetTotalCostToManufacture()  ← **零参**
#     CostFeature GetFirstCostFeature()                          ← **零参**
#     Object GetSpecificAnalysis()                               ← **零参**
# ⚠ ⚑ 官方参数名**拼写不一致**，照抄之：`MarkUpPercent`（大写 U）
#   与 `SetFactoryCost` 之类。改「整齐」了反而对不上官方。
# ⚠ 五个 Get*Cost 方法的**货币单位**由 get_CurrencyCode 决定，
#   本模块只透传原始数字，**不换算、不解释**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_lot_size(cost_analysis, lot_size: int) -> bool:
    """设批量大小。⚑ 官方是**属性**（set_LotSize），不是方法。"""
    if cost_analysis is None:
        raise ValueError("cost_analysis 为 None")
    get_com_member(cost_analysis, "LotSize", int(lot_size))
    return True


def set_markup(cost_analysis, markup_type: int | None = None,
               markup_percent: float | None = None) -> bool:
    """设加价。⚑ MarkUpType / MarkUpPercent 都是**属性**。

    ⚠ `MarkUpType` 的取值（按成本/按价格/按数量？）两套源都查不到。
    """
    if cost_analysis is None:
        raise ValueError("cost_analysis 为 None")
    if markup_type is not None:
        get_com_member(cost_analysis, "MarkUpType", int(markup_type))
    if markup_percent is not None:
        get_com_member(cost_analysis, "MarkUpPercent", float(markup_percent))
    return True


def read_cost_analysis(cost_analysis) -> dict[str, Any]:
    """回读成本分析的全部可读项。"""
    if cost_analysis is None:
        raise ValueError("cost_analysis 为 None")
    return {
        "template": str(get_com_member(cost_analysis, "CostingTemplateName") or ""),
        "costing_type": int(get_com_member(cost_analysis, "CostingType") or -1),
        "lot_size": int(get_com_member(cost_analysis, "LotSize") or 0),
        "total_quantity": int(get_com_member(cost_analysis, "TotalQuantity") or 0),
        "markup_type": int(get_com_member(cost_analysis, "MarkUpType") or -1),
        "markup_percent": float(get_com_member(cost_analysis, "MarkUpPercent") or 0.0),
        "currency_code": str(get_com_member(cost_analysis, "CurrencyCode") or ""),
        "currency_name": str(get_com_member(cost_analysis, "CurrencyName") or ""),
        "currency_separator": str(
            get_com_member(cost_analysis, "CurrencySeparator") or ""),
        "length_unit": int(get_com_member(cost_analysis, "LengthUnit") or -1),
        "mass_unit": int(get_com_member(cost_analysis, "MassUnit") or -1),
        "unit_system": int(get_com_member(cost_analysis, "UnitSystem") or -1),
        "material_cost": float(get_com_member(cost_analysis, "GetMaterialCost") or 0.0),
        "manufacturing_cost": float(
            get_com_member(cost_analysis, "GetManufacturingCost") or 0.0),
        "setup_cost": float(get_com_member(cost_analysis, "GetSetupCost") or 0.0),
        "total_to_manufacture": float(
            get_com_member(cost_analysis, "GetTotalCostToManufacture") or 0.0),
        "total_to_charge": float(
            get_com_member(cost_analysis, "GetTotalCostToCharge") or 0.0),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ICostingDefaults 段
# 定位:   全局成本默认值。官方签名逐条照抄：
#     Int32  get_LotSizeForSingleBody() / get_LotSizeForMultibody() /
#            get_TotalNumberOfPartsForSingleBody() / …ForMultibody() /
#            get_MachiningStockBodyType() / get_SheetmetalBlankSizeType() /
#            get_StructuralMemberStockType()
#     Void   set_LotSizeForSingleBody(Int32) / set_LotSizeForMultibody(Int32) / …
#     Void   SetTemplateName(Int32, String) / SetMaterialName(Int32, String) /
#            SetMaterialClass(Int32, String) / SetManufacturingMethod(Int32, Int32)
#     String GetTemplateName(Int32) / GetMaterialName(Int32) /
#            GetMaterialClass(Int32)
#     Int32  GetManufacturingMethod(Int32)
# ⚠ 这些 `Set*` 首参的 Int32 语义（是「页签序号」还是「模板类别」？）未注明。
# ⚠ 批量/单实体、总数/多实体 四组是成对的，命名规律是
#   ``…ForSingleBody`` / ``…ForMultibody``，本模块照抄不改名。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_default_lot_size(defaults, single_body: int, multibody: int) -> dict[str, Any]:
    """设单实体 / 多实体的默认批量。⚑ 官方是**属性**。"""
    if defaults is None:
        raise ValueError("defaults 为 None")
    get_com_member(defaults, "LotSizeForSingleBody", int(single_body))
    get_com_member(defaults, "LotSizeForMultibody", int(multibody))
    return {"LotSizeForSingleBody": int(single_body),
            "LotSizeForMultibody": int(multibody)}


def set_default_template(defaults, category: int, template_name: str) -> bool:
    """设某类别的默认模板。"""
    _checked(defaults, "SetTemplateName", int(category), str(template_name))
    return True


def get_default_template(defaults, category: int) -> str:
    """读某类别的默认模板。"""
    return str(_checked(defaults, "GetTemplateName", int(category)) or "")


def set_default_material(defaults, category: int, material_name: str) -> bool:
    """设某类别的默认材料。"""
    _checked(defaults, "SetMaterialName", int(category), str(material_name))
    return True


def set_default_manufacturing_method(defaults, category: int, method: int) -> bool:
    """设某类别的默认制造方法。"""
    _checked(defaults, "SetManufacturingMethod", int(category), int(method))
    return True


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_routing.py::collect_routing_evidence）
# 定位:   成本状态证据回读，沿用「只取已核实成员」的写法。
#         读取的成员全部是 ICostBody 上反射确认存在的那些。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_cost_body(cost_body) -> dict[str, Any]:
    """回读单个成本实体的信息。"""
    if cost_body is None:
        raise ValueError("cost_body 为 None")
    return {
        "name": str(get_com_member(cost_body, "GetName") or ""),
        "body_type": int(get_com_member(cost_body, "GetBodyType") or -1),
        "body_status": int(get_com_member(cost_body, "BodyStatus") or -1),
        "has_sw_body": get_com_member(cost_body, "GetSWBody") is not None,
        "has_cost_analysis": get_com_member(cost_body, "GetCostAnalysis") is not None,
    }


def assign_custom_cost(cost_body, amount: float) -> bool:
    """给实体指定自定义成本。⚠ 与哪些费用项相加/相抵，官方无说明。"""
    _checked(cost_body, "AssignCustomCost", float(amount))
    return True


def collect_costing_evidence(cost_part) -> dict[str, Any]:
    """回读零件的成本状态概览。"""
    if cost_part is None:
        raise ValueError("cost_part 为 None")
    return {
        "body_count": get_body_count(cost_part),
        "has_cost_analysis": get_cost_analysis(cost_part) is not None,
    }
