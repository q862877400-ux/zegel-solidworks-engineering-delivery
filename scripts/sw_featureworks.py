"""SolidWorks FeatureWorks 自动特征识别：IFeatureWorksApp 封装。

能力域
    域 14 · 路由 / Composer / PDM（需许可证）—— 本文件是其中 **FeatureWorks** 部分

模块分工（域 14，本仓库共五个）
--------------------------------
    sw_routing.py   SolidWorks Routers 线束/管线路由
    sw_costing.py   Composer 成本估算
    sw_pdm.py       Enterprise PDM 文档/配置/BOM 表
    sw_featureworks.py（本文件）FeatureWorks 自动特征识别
    fworks 程序集共 **2 个段 / 7 个成员** —— 是域 14 里最小的一块，
    但它是**独立能力**（一键识别实体特征），不是某个族的子集。

接口族覆盖（本模块 1 个接口 / 全库 2 个段）
    IFeatureWorksApp  7 个成员
    （另一个段 ``FeatureWorksApp`` 是 **coclass**，成员数为 0，
      定义在接口上，不是独立能力 —— 这与 swdocumentmgr 的 158 个
      coclass 段是同一形态）

⚠⚑ 取用路径：ProgID **查不到**
--------------------------
``IFeatureWorksApp`` 正常应由 ``ISldWorks.GetAddInObject(<ProgID>)`` 取得。
本机情况（2026-xx 核实）：
  · 读 ``HKLM:\\SOFTWARE\\SOLIDWORKS\\AddIns``（含 WOW6432Node 镜像）下
    Title/Description 匹配 FeatureWorks 的条目 → **0 条**
  · 反射清单里只有 coclass ``FeatureWorksApp`` 与接口 ``IFeatureWorksApp``，
    **没有任何加载项回调接口**（对比 Simulation 有 ``ICwAddincallback``）

⇒ 本模块**不硬编 ProgID、不代为取得**，全部函数**接收调用方传入的对象**。
   与 ``sw_simulation.py::SIMULATION_ADDIN_PROGID`` 的处理方式不同：
   那个 ProgID 有 MIT 项目作佐证（alisamsam/Solidworks-MCP），本模块**没有**，
   所以连「标注来源 + 待确认」都不给 —— 没有来源可标。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt
      —— 对 SolidWorks.Interop.fworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③「读官方程序集，不是实测」）。
         版本号已在反射清单头部标明：**34.4.1.1011**。

⚠ **本族官方 CHM 没有文档页**（四册 CHM 里没有 fworks 册），
  故只有签名、没有参数语义。各函数处逐条标注；不编「合理解释」。
  尤其 `CreateFeatures(Int16)` 的 Int16、`RecognizeFeatureAutomatic(Int32)`
  的 Int32 —— 两套源都未说明取值范围，故**不设默认值**、只透传。

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
# 文件:   scripts/sw_featureworks.py —— 本文件自身
# 定位:   模块导出清单与签名表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "FEATUREWORKS_ARITY",
    "recognize_and_create",
    "recognize_interactive",
    "set_advanced_options",
    "set_performance_options",
    "read_featureworks_state",
]

#: 反射确认的实参个数（7 个成员里 2 个是回调、0 参，不列入调用侧）
#: enum-gate: not-enum arity
#: arity-reflect: byref=excluded
FEATUREWORKS_ARITY: dict[str, int] = {
    "CreateFeatures": 1,
    "RecognizeFeatureAutomatic": 1,
    "RecognizeFeatureInteractive": 2,
    "SetAdvancedOptions": 1,
    "SetPerformanceOptions": 1,
}

#: 两个回调成员（不提供给调用方，签名见下方来源块）
CALLBACK_MEMBERS = ("BubbleTipCallback", "HelpErrCallback")


#: dispatch-guard: exempt internal-helper
def _checked(target, member: str, *args):
    """按签名表校核实参个数，通过后才发起调用（开发期护栏）。"""
    expected = FEATUREWORKS_ARITY.get(member)
    if expected is not None and expected != len(args):
        raise ValueError(
            f"{member} 官方签名是 {expected} 个实参，本次调用给了 {len(args)} 个"
        )
    if target is None:
        raise ValueError("featureworks 为 None：须先由调用方取得 IFeatureWorksApp 对象")
    return get_com_member(target, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（fworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_fworks.txt（版本 34.4.1.1011）
#           → IFeatureWorksApp 段（该接口共 7 个成员，全文照录）
# 定位:   特征识别的两个入口。官方签名逐条照抄：
#     Boolean CreateFeatures(Int16)                        → 1
#     Int32   RecognizeFeatureAutomatic(Int32)             → 1
#     Boolean RecognizeFeatureInteractive(String, Int32)   → 2
#     Boolean SetAdvancedOptions(Int16)                    → 1
#     Boolean SetPerformanceOptions(Int16)                 → 1
#     Void    BubbleTipCallback()                          ← 零参，**回调**
#     Void    HelpErrCallback(Int32, String, Int32, String) ← 回调
# ⚠ 两个 `*Callback` 成员是 SolidWorks 调回宿主用的**回调点**，
#   不是给脚本调的 API ⇒ 本模块**不提供封装**，只在
#   FEATUREWORKS_ARITY 之外单列 CALLBACK_MEMBERS 说明其存在。
# ⚠ `RecognizeFeatureInteractive` 的 String（第 1 参）是文件路径还是别的，
#   两套源都未说明；`Int32` 的返回值语义同样未说明。
#   ⇒ 本模块**只按位置透传**，不解释、不设默认值。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def recognize_and_create(featureworks, entity_type: int) -> bool:
    """自动识别特征并创建。⚠ Int16 的取值范围官方无文档。"""
    return bool(_checked(featureworks, "CreateFeatures", int(entity_type)))


def recognize_interactive(featureworks, target: str, option: int) -> bool:
    """交互式识别特征。

    ⚠ ``target``（官方 String）与 ``option``（官方 Int32）的语义官方无文档。
    """
    return bool(
        _checked(featureworks, "RecognizeFeatureInteractive", str(target), int(option))
    )


def set_advanced_options(featureworks, options: int) -> bool:
    """设高级选项。⚠ Int16 的位标志含义官方无文档，只透传。"""
    return bool(_checked(featureworks, "SetAdvancedOptions", int(options)))


def set_performance_options(featureworks, options: int) -> bool:
    """设性能选项。⚠ 同上。"""
    return bool(_checked(featureworks, "SetPerformanceOptions", int(options)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_routing.py::collect_routing_evidence）
# 定位:   状态证据回读。⚠ IFeatureWorksApp 的 7 个成员里
#   **没有一个是可读属性**（5 个带参方法 + 2 个零参回调），
#   所以「回读状态」在反射层面**做不到**。
#   本函数改为回读「本次会话调用过什么」的调用痕迹，
#   **不假装**能从 FeatureWorks 对象读出配置状态。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def read_featureworks_state(
    calls: list[tuple[str, tuple]] | None = None,
) -> dict[str, Any]:
    """回读本会话对 FeatureWorks 的调用痕迹。

    :param calls: 形如 ``[(成员名, 实参元组), ...]`` 的调用记录。
        ⚠ ``IFeatureWorksApp`` **没有可读属性**（反射确认 7 个成员全是方法），
        所以「状态」只能从调用侧记录拿 —— 传 None 就返回空痕迹，
        **不编造**任何来自 FeatureWorks 对象的字段。
    """
    recorded = list(calls or [])
    return {
        "call_count": len(recorded),
        "members": [name for name, _ in recorded],
        "has_recognize": any(
            name
            in (
                "CreateFeatures",
                "RecognizeFeatureAutomatic",
                "RecognizeFeatureInteractive",
            )
            for name, _ in recorded
        ),
        "callback_members_not_called": list(CALLBACK_MEMBERS),
    }
