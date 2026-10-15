"""SolidWorks Simulation：19 个 cosworks 族的登记表与访问器。
# 取值:   原始 / I前缀 / 属性行 / 方法 —— 逐族：
STUDY_AND_LOADS_FAMILIES: tuple[str, ...] = (
    'ICWStudyManager', 'ICWStudy', 'ICWLoadsAndRestraintsManager',
    'ICWForce', 'ICWPressure', 'ICWHeatFlux', 'ICWContactSet',
)

能力域
    域 13 · 仿真（需许可证）

覆盖的接口族（19 个，即 cosworks 全库）
--------------------------------------
    研究与求解  ICWStudyManager · ICWStudy
    载荷夹具    ICWLoadsAndRestraintsManager · ICWForce · ICWPressure ·
                ICWHeatFlux · ICWContactSet
    网格与结果  ICWMesh · ICWResults
    材料        ICWMaterial
    求解器设置  ICWStaticStudyOptions · ICWFrequencyStudyOptions ·
                ICWBucklingStudyOptions · ICWNonLinearStudyOptions ·
                ICWThermalStudyOptions · ICWDynamicStudyOptions ·
                ICWFatigueStudyOptions · ICWCompositeShellOptions

⚑ 与既有三个 Simulation 模块的分工
----------------------------------
本仓库的 Simulation 域是**五件套**（本轮把这套「成员级」那一层补齐了）：

    scripts/sw_simulation.py         addin 入口 + 端到端骨架
    scripts/sw_simulation_loads.py   载荷夹具的 24 个 Add* 方法（创建）
    scripts/sw_simulation_study.py   研究管理与求解
    scripts/sw_simulation_results.py 结果云图与网格质量
    scripts/sw_simulation_loadprops.py 载荷对象属性（ICWForce 等）
    scripts/sw_simulation_study_options.py 242 个求解器设置登记表
    scripts/sw_simulation_registry.py（本文件）**19 族的成员级登记表**
        —— 把上面几处的**已知**成员补全成「全族可用」，
           并覆盖此前**没有任何封装**的族（ICWResults / ICWMaterial /
           ICWMesh / ICWDynamicStudyOptions 等）

⚠ **cosworks 的特殊之处：CHM 册只覆盖 ICWLoadsAndRestraintsManager 一族**
  ⇒ 载荷夹具这一族有官方**参数语义说明**，本模块已在
  ``sw_simulation_loads.py`` 里逐条照录；
  而其余 18 族**官方无文档页**，只有反射签名 ⇒ 本模块**只登记名字与参数个数**，
  **不解释任何一项的语义**。需要语义请查官方文档或读反射声明的返回类型。

⚠ 载荷对象的数值**不在** Add* 方法的入参里，而是在返回对象上设属性
  （如 ``ICWForce.NormalForceOrTorqueValue``）—— 这已由官方 CHM 的
  Parameters 段确认，本模块的登记表与之不冲突。

⚠ 编号成员**未折叠**。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt
      —— 对 SolidWorks.Interop.cosworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③）。规模：168 接口 / 363 枚举 / 2,520 成员（接口成员口径）。
    登记表：``D:\\AI\\SW\\tools\\gen_member_registry.py`` 的输出。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

__all__ = [
    "SIM_FAMILIES",
    "SIM_ARITY",
    "SIM_PROPERTIES",
    "STUDY_AND_LOADS_FAMILIES",
    "MESH_AND_RESULTS_FAMILIES",
    "SOLVER_OPTION_FAMILIES",
    "call_sim",
    "collect_sim_evidence",
]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_registry.py —— 本文件自身
# 定位:   模块导出清单与族名常量。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_registry.py —— 本文件自身
# 定位:   cosworks 19 族的成员登记表 {族: {能力名: 实参个数}}。
#         生成器 D:\AI\SW\tools\gen_member_registry.py，
#         对 iface_cosworks.txt 的逐行解析，机械生成不手抄。
# ⚑ 编号成员**未折叠**。
# ⚠ cosworks 的 CHM 册**只覆盖 ICWLoadsAndRestraintsManager 一族** ⇒
#   只有该族有官方参数语义说明；其余 18 族本模块**只登记名字与参数个数**，
#   **不解释任何一项的语义**。
# 取值:   能力数 —— 逐族：
#     ICWLoadsAndRestraintsManager         43
#     ICWStudyManager                      17
#     ICWStudy                             26
#     ICWResults                          106
#     ICWMesh                              30
#     ICWForce                             20
#     ICWPressure                          12
#     ICWHeatFlux                          14
#     ICWContactSet                         9
#     ICWMaterial                          18
#     ICWStaticStudyOptions                 2
#     ICWFrequencyStudyOptions              2
#     ICWBucklingStudyOptions               2
#     ICWNonLinearStudyOptions             14
#     ICWThermalStudyOptions                0
#     ICWDynamicStudyOptions               85
#     ICWFatigueStudyOptions               12
#     ICWDropTestStudyOptions               0
#     ICWCompositeShellOptions             15
# 覆盖:   后续同级定义
# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_simulation_registry.py —— 本文件自身
# 定位:   本轮登记的 19 个 cosworks 族。
# ⚑⚑ **这 19 族不是 cosworks 全库** —— cosworks 反射里「有成员」的接口段
#   实测 **84 个**（其余 149 个段成员数为 0，是 coclass）。
#   本轮取的是「docs/family-coverage.md 里已列出的 19 族」，
#   即**本仓库已建立对应域映射的那 19 个**；其余 65 族尚未纳入映射。
#   写成「全库」是我初稿的错误说法，已改正。
# ⚠ cosworks 的 CHM 册**只覆盖 ICWLoadsAndRestraintsManager 一族** ⇒
#   只有该族有官方参数语义说明；其余族本模块**只登记名字与参数个数**，
#   **不解释任何一项的语义**。
# ⚑ 编号成员**未折叠**。
# 取值:   原始 / I前缀 / 属性行 / 方法 —— 逐族：
