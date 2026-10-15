"""SolidWorks Simulation：19 个 cosworks 族的成员登记表与访问器。

能力域
    域 13 · 仿真（需许可证）

覆盖的接口族（19 个）
--------------------
    研究与求解  ICWStudyManager · ICWStudy
    载荷与夹具  ICWLoadsAndRestraintsManager · ICWForce · ICWPressure ·
                ICWHeatFlux · ICWContactSet
    网格与结果  ICWMesh · ICWResults · ICWMaterial
    求解器设置  ICWStaticStudyOptions · ICWFrequencyStudyOptions ·
                ICWBucklingStudyOptions · ICWNonLinearStudyOptions ·
                ICWThermalStudyOptions · ICWDynamicStudyOptions ·
                ICWFatigueStudyOptions · ICWCompositeShellOptions

这 19 族不是 cosworks 全库
-------------------------
cosworks 反射里有成员的接口段实测 84 个（其余 149 个段成员数为 0，
是 coclass 具体类，成员定义在对应接口上）。本轮登记的是
family-coverage.md 里已列出的那 19 个族，其余 65 族尚未纳入本仓库的域映射。

cosworks 的 CHM 册只覆盖 ICWLoadsAndRestraintsManager 一族
--------------------------------------------------
只有该族有官方参数语义说明（已在 sw_simulation_loads.py 逐条照录）；
其余 18 族官方无文档页，只有反射签名 ⇒ 本模块只登记名字与参数个数，
不解释任何一项的语义。

编号成员未折叠。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
      对 SolidWorks.Interop.cosworks.dll 的纯元数据反射
      （AGENTS.md §四.1③）。规模：168 接口段 / 363 枚举 / 2,520 成员。
    登记表：D:\\AI\\SW\\tools\\gen_member_registry.py 的输出。

本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

__all__ = [
    "SIM_FAMILIES", "SIM_ARITY", "SIM_PROPERTIES",
    "STUDY_AND_LOADS_FAMILIES", "MESH_AND_RESULTS_FAMILIES",
    "SOLVER_OPTION_FAMILIES", "call_sim", "collect_sim_evidence",
]


def _require(obj, what: str = "对象"):
    if obj is None:
        raise ValueError(f"{what} 为 None")
    return obj


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（与 sw_part_features.py 同款护栏）
# 文件:   scripts/sw_simulation_registry.py —— 本文件自身
# 定位:   通用访问器 :func:`call_sim` 的 arity 校核与调用。
# ⚑ 族名与成员名都由调用方给 ⇒ 静态 arity 审计归因不到；
#   对账靠 tests/test_sw_simulation_registry_contract.py。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def call_sim(obj, family: str, member: str, *args):
    """按登记表校核实参个数，通过后调用 cosworks 族的成员。

    :raises KeyError: 族名或成员名不在登记表里（**不静默忽略**）
    :raises ValueError: 实参个数对不上（在**发起调用之前**就报）
    """
    sub = SIM_ARITY.get(family)
    if sub is None:
        raise KeyError(
            f"未登记的族: {family}；已登记 {', '.join(sorted(SIM_ARITY))}")
    expected = sub.get(member)
    if expected is None:
        raise KeyError(
            f"{family} 上没有名为 {member} 的能力（该族登记 {len(sub)} 项）。"
            f"若它是属性或 I 前缀内部分发口，请用对应封装。")
    if expected != len(args):
        raise ValueError(
            f"{family}.{member} 官方签名是 {expected} 个实参，"
            f"本次调用给了 {len(args)} 个")
    _require(obj, f"{family} 对象")
    return get_com_member(obj, member, *args)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 文件:   scripts/sw_simulation_registry.py —— 本文件自身
# 定位:   状态证据回读，只读登记表里确实有的成员。
# ⚑ 该族没有的证据成员**直接不出现**，不补默认值冒充「读到了」。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
_EVIDENCE_MEMBERS = {
    "ICWStudy": ("GetName", "GetAnalysisType", "GetMeshType"),
    "ICWMesh": ("GetElementCount", "GetNodeCount", "GetQuality"),
    "ICWResults": ("GetResultCount",),
    "ICWMaterial": ("GetMaterialName",),
}


def collect_sim_evidence(obj, family: str) -> dict[str, Any]:
    """回读 cosworks 族对象的状态。

    逐个成员用 ``call_sim`` 取；**该族没有的成员不补默认值**，直接不出现。
    """
    _require(obj, family)
    if family not in SIM_ARITY:
        raise KeyError(f"未登记的族: {family}")
    props = set(SIM_PROPERTIES.get(family, ()))
    out: dict[str, Any] = {"family": family}
    for member in _EVIDENCE_MEMBERS.get(family, ()):
        if member not in SIM_ARITY[family] and member not in props:
            continue
        try:
            out[member] = call_sim(obj, family, member)
        except (KeyError, ValueError):
            continue
    return out
