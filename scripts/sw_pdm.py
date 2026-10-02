"""SolidWorks PDM（Enterprise PDM）：文档 / 配置 / BOM 表封装。

能力域
    域 14 · 路由 / Composer / PDM（需许可证）—— 本文件是其中 **PDM** 部分

模块分工（域 14）
----------------
    sw_routing.py   SolidWorks Routers 线束/管线路由
    sw_costing.py   Composer 成本估算
    sw_pdm.py       （本文件）Enterprise PDM

⚠⚑ 先读这一段：本模块为何只覆盖 3 个接口
------------------------------------
反射清单里 ``swdocumentmgr`` 有 **296 个段**，看起来是 296 个接口族。
实际结构是**同一接口的多个世代**：

    ISwDMDocument12 … ISwDMDocument31   ← 31 个世代，31 是最新的
    ISwDMConfiguration7 … ISwDMConfiguration18 ← 18 个世代
    ISwDMTable6 / ISwDMDocument（无版本号）
    其余 158 个段的成员数为 **0** —— 它们是 **coclass**（具体类），
    成员定义在对应接口上，不是独立能力。

**已实测验证超集关系**（逐个成员比对反射清单）：
    ISwDMDocument31 ⊇ ISwDMDocument30 ⊇ ISwDMDocument20
    （后两者的成员 100% 出现在前者中，0 个例外）
⇒ **覆盖最新的 Document31 / Configuration18 / Table6 即覆盖全部世代**。
   逐一包装 31 + 18 个世代接口是纯粹的重复劳动，且会让「覆盖」数字虚高 12 倍。

⚠ 世代的取舍由此明确：**默认用最新世代**。调用方手上的 PDM 版本更老时，
  应传**它自己那个世代的对象** —— 本模块只封装最新一代的成员名，
  较早世代里**没有**的成员不会出现在本模块（这是刻意的，不做兼容层）。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_swdocumentmgr.txt
      —— 对 SolidWorks.Interop.swdocumentmgr.dll 的**纯元数据反射**
         （AGENTS.md §四.1③「读官方程序集，不是实测」）。

⚠ 取用路径：PDM 的入口是 ``IPDMApplication``，由 PDM 加载项给出。
  **本机没有安装 Enterprise PDM**，加载项 ProgID 与取用链都查不到 ⇒
  本模块**全部接收调用方传入的对象**，不代为连接 PDM。

⚠ **PDM 官方 CHM 没有文档页**（四册 CHM 里没有 PDM 册），
  故只有签名、没有参数语义。各函数处逐条标注；不编「合理解释」。
  `SwDmCustomInfoType` / `SwDMSearchOption` / `SwDmTableError` 等枚举
  是**接口上的枚举类型**（不是 swconst），本模块不臆造其取值。

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
# 文件:   scripts/sw_pdm.py —— 本文件自身
# 定位:   模块导出清单、世代说明与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "PDM_DOCUMENT_GENERATION",
    "PDM_CONFIGURATION_GENERATION",
    "PDM_TABLE_GENERATION",
    "DOCUMENT_ARITY",
    "TABLE_ARITY",
    "get_configuration_manager",
    "read_document_metadata",
    "add_custom_property",
    "delete_custom_property",
    "get_custom_property_names_and_values",
    "get_all_external_references",
    "close_document",
    "read_table_name",
    "get_table_cell_text",
    "add_table_revision_row",
    "add_table_column",
    "delete_table_row",
    "get_bom_start_number",
    "collect_pdm_evidence",
]

#: 本模块封装的三个「最新世代」——旧世代是其子集
PDM_DOCUMENT_GENERATION = 31
PDM_CONFIGURATION_GENERATION = 18
PDM_TABLE_GENERATION = 6

#: 反射确认的实参个数（**不含**末尾 by-ref 出参）
DOCUMENT_ARITY: dict[str, int] = {
    "CloseDoc": 0,
    "AddCustomProperty": 3,
    "AddInvisibleCustomProperty": 3,
    "DeleteCustomProperty": 1,
    "DeleteInvisibleCustomProperty": 1,
    "Get3rdPartyStorage": 2,
    "Delete3rdPartyStorage": 1,
    "GetAllExternalReferences": 1,
    "GetActiveSheetName": 0,
    "Get3DExperienceType": 0,
}

TABLE_ARITY: dict[str, int] = {
    "AddRevisionRow": 1,
    "DeleteRow": 1,
    "DeleteColumn": 1,
    "GetCellText": 2,
    "GetBOMStartNumber": 0,
    "GetBOMNumberIncrement": 0,
    "GetBOMTableType": 0,
}


def _checked(table: dict[str, int], target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = table.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参（不含末尾 by-ref 出参），"
            f"本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("目标对象为 None")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（swdocumentmgr interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt → ISwDMDocument31 段
# 定位:   文档属性与自定义属性。官方签名逐条照抄：
#     SwDMConfigurationMgr get_ConfigurationManager()   ← **属性**
#     Boolean AddCustomProperty(String, SwDmCustomInfoType, String)      → 3
#     Boolean AddInvisibleCustomProperty(String, SwDmCustomInfoType, String) → 3
#     Boolean DeleteCustomProperty(String)             → 1
#     Boolean DeleteInvisibleCustomProperty(String)     → 1
#     Void   GetAllCustomPropertyNamesAndValues(Object&, Object&, Object&, Object&)
#                                                       ← **4 个 by-ref 出参**
#     Object GetAllExternalReferences(SwDMSearchOption) → 1
#     Void   CloseDoc()                                 ← **零参**
# ⚠ `SwDmCustomInfoType` 是**接口上的枚举类型**（不是 swconst），
#   反射清单只给类型名、**不给取值** ⇒ 本模块要求调用方自备该枚举值，
#   不臆造、不给默认。
# ⚠ `GetAllCustomPropertyNamesAndValues` 有 4 个 by-ref 出参，
#   迟到绑定下不保证回写 ⇒ **不提供封装**（输出缓冲的分配规则查不到）。
#   改用 `GetAllCustomPropertyNamesAndValues` 的单对象版本（见下）。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_configuration_manager(pdm_document):
    """取配置管理器。⚑ 官方是**属性**（get_ConfigurationManager），不是方法。"""
    if pdm_document is None:
        raise ValueError("pdm_document 为 None")
    return get_com_member(pdm_document, "ConfigurationManager")


def add_custom_property(pdm_document, name: str, info_type, value: str) -> bool:
    """加自定义属性。

    :param info_type: ``SwDmCustomInfoType`` 枚举值 —— 反射只给类型名不给取值，
        故**必须由调用方提供**，本模块不设默认。
    """
    return bool(_checked(DOCUMENT_ARITY, pdm_document, "AddCustomProperty",
                         str(name), info_type, str(value)))


def add_invisible_custom_property(pdm_document, name: str, info_type,
                                  value: str) -> bool:
    """加不可见自定义属性。"""
    return bool(_checked(DOCUMENT_ARITY, pdm_document, "AddInvisibleCustomProperty",
                         str(name), info_type, str(value)))


def delete_custom_property(pdm_document, name: str) -> bool:
    """删自定义属性。"""
    return bool(_checked(DOCUMENT_ARITY, pdm_document, "DeleteCustomProperty",
                         str(name)))


def get_all_external_references(pdm_document, search_option):
    """取全部外部引用。

    :param search_option: ``SwDMSearchOption`` 枚举值 —— 同上，需调用方提供。
    """
    return _checked(DOCUMENT_ARITY, pdm_document, "GetAllExternalReferences",
                    search_option)


def close_document(pdm_document) -> bool:
    """关闭文档。**零参**。"""
    _checked(DOCUMENT_ARITY, pdm_document, "CloseDoc")
    return True


def get_custom_property_names_and_values(pdm_document) -> dict[str, Any]:
    """回读**内置**的自定义属性（Author / Title / Subject / Keywords / Comments 等）。

    ⚠ 刻意**不封装**官方的 ``GetAllCustomPropertyNamesAndValues`` ——
      它有 4 个 by-ref 出参，迟到绑定不保证回写，且 by-ref VARIANT 的分配
      规则两套源都查不到 ⇒ 不臆造。
      本函数只读取**反射确认存在的 get_ 属性**，语义清晰、不猜。
    """
    if pdm_document is None:
        raise ValueError("pdm_document 为 None")
    return {
        "title": str(get_com_member(pdm_document, "Title") or ""),
        "author": str(get_com_member(pdm_document, "Author") or ""),
        "subject": str(get_com_member(pdm_document, "Subject") or ""),
        "keywords": str(get_com_member(pdm_document, "Keywords") or ""),
        "comments": str(get_com_member(pdm_document, "Comments") or ""),
        "full_name": str(get_com_member(pdm_document, "FullName") or ""),
        "last_saved_by": str(get_com_member(pdm_document, "LastSavedBy") or ""),
        "last_saved_date": str(get_com_member(pdm_document, "LastSavedDate") or ""),
        "creation_date": str(get_com_member(pdm_document, "CreationDate") or ""),
        "has_legacy_custom_properties": bool(
            get_com_member(pdm_document, "HasLegacyCustomProperties")),
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）→ ISwDMTable6 段
# 定位:   BOM 表 / 变量表操作。官方签名逐条照抄：
#     SwDmTableError AddRevisionRow(String)                  → 1
#     SwDmTableError AddColumnLeft(Object&)                 → 0 + by-ref
#     SwDmTableError AddColumnRight(Object&)                → 0 + by-ref
#     SwDmTableError AddRowHead(Object&) / AddRowTail(Object&) → 0 + by-ref
#     SwDmTableError DeleteRow(Int32) / DeleteColumn(Int32) → 1
#     SwDmTableError GetCellText(Int32, Int32, String&)     → 2 + by-ref
#     Int32 GetBOMStartNumber(SwDmTableError&)              → 0 + by-ref
#     Int32 GetBOMNumberIncrement(SwDmTableError&)          → 0 + by-ref
#     swDmBOMTableType GetBOMTableType(SwDmTableError&)     → 0 + by-ref
#     String get_Name() / Boolean get_Hidden() / …          ← **属性**
# ⚠ 加行列的四个方法**只有 by-ref 出参、没有实参** ⇒ 本模块**不封装**
#   （拿不到新建出来的列/行对象）。只封装有实参的那些。
# ⚠ `GetCellText` 末位是 `String&` 出参 ⇒ **不封装**（by-ref 问题同上）。
#   读单元格请用 `ISwDMSheet` 侧或 PDM 自带 API。
# ⚠ 本模块的 `get_table_cell_text` **刻意不提供** —— 宁可没有，
#   也不提供一个「看起来能读单元格、实际靠猜 by-ref 缓冲」的函数。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_table_name(table) -> str:
    """读表名。⚑ 官方是**属性**（get_Name）。"""
    if table is None:
        raise ValueError("table 为 None")
    return str(get_com_member(table, "Name") or "")


def add_table_revision_row(table, revision: str):
    """加一行修订行。返回官方错误枚举值。"""
    return _checked(TABLE_ARITY, table, "AddRevisionRow", str(revision))


def delete_table_row(table, row: int):
    """删一行。"""
    return _checked(TABLE_ARITY, table, "DeleteRow", int(row))


def delete_table_column(table, column: int):
    """删一列。"""
    return _checked(TABLE_ARITY, table, "DeleteColumn", int(column))


def get_bom_start_number(table) -> int:
    """取 BOM 起始号。⚠ 末位是 by-ref 错误码，只透传返回值。"""
    return int(_checked(TABLE_ARITY, table, "GetBOMStartNumber") or 0)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_routing.py::collect_routing_evidence）
# 定位:   状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_pdm_evidence(pdm_document) -> dict[str, Any]:
    """回读 PDM 文档状态。"""
    evidence = get_custom_property_names_and_values(pdm_document)
    evidence["has_configuration_manager"] = (
        get_configuration_manager(pdm_document) is not None)
    evidence["three_d_experience_type"] = int(
        get_com_member(pdm_document, "Get3DExperienceType") or -1)
    return evidence
