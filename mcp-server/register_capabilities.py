"""把声明式批次（`tool_specs_batch*.py`）注册进**真实的** MCP server。

## 为什么要有这个文件（而不是直接在 `server.py` 里写）
`mcp-server/server.py` 是**上游的**（AGENTS.md 已知事实 26：「104 KB，45 个工具的实现，
我们一行没改」）。**接线必然要动它一行** —— 所以：
* **`server.py` 只加两句**（一个 import + 一次 `register_capabilities(mcp)`），
* **全部接线逻辑放本文件** ⇒ 上游文件的改动**最小、可秒级审查**，
* **改了这个事实就要更新它**（已知事实 26 原本写「一行没改」）。

## 注入解析器（`tool_registry` 不硬编码宿主 API，由这里供给）
| 注入名 | 解析器 | 说明 |
|---|---|---|
| `model` | 活动文档 | 取不到就**报错**（不返回 None 让下游崩在别处） |
| `sw_app` | `ISldWorks` | |
| `study` | 按 `study_name` 解析 | 空名取第一个 |

## ⚠ 失败策略：**响亮地失败**
任一批次的声明**过不了门禁**（`check_spec`），`register()` 就**整体不注册**并抛错。
**⇒ 不让「半套工具」进到运行期**（那是比不注册更糟的状态）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（接线层，非第三方移植）
# 文件:   mcp-server/register_capabilities.py
# 定位:   T-011 的**接入点**。`docs/T-011-expose-capabilities-assessment.md`
#         里 20 条声明从此**真的可用**（此前只是声明）。
# 官方签名依据: 不适用（不引入新的 COM 调用；各批次声明的依据在其被搬运函数的源码块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 接线本身未在本机实测（**MCP 客户端没跑过**）；但「注册后工具数」与
#   「每个工具的 input schema 可构造」两件事在 `tests/test_server_wiring.py` 里静态验。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from tool_registry import register  # noqa: E402


# ── 注入解析器 ──────────────────────────────────────────────────────
def _connect():
    from scripts.sw_connect import connect_solidworks

    return connect_solidworks(wait_seconds=20, return_metadata=True)


def resolve_model(_params: Any):
    """注入**活动文档**。取不到就报错 —— 不返回 None 让下游崩在别处。"""
    _sw, model, _meta = _connect()
    if model is None:
        raise RuntimeError(
            "没有活动文档 —— 请先在 SolidWorks 里打开一个零件/装配体/工程图"
        )
    return model


def resolve_sw_app(_params: Any):
    """注入 `ISldWorks`。"""
    sw, _model, _meta = _connect()
    return sw


def resolve_study(params: Any):
    """按 `study_name` 解析研究；空名取第一个。"""
    from scripts.sw_simulation import get_study_by_name, iter_studies

    sw, _model, _meta = _connect()
    name = (getattr(params, "study_name", "") or "").strip()
    #: ★★★★★ 2026-10-01（轮 346）**修一处一行之差** —— 真因（挖 `simulation_solver_optio
    #: ns` 时发现）：
    #:   `iter_studies(sw_app)` 是 **`yield index, study`**（★ **二元组**），
    #:   而原先写的是 `next(iter(iter_studies(sw)), None)` —— ★★ **没有解包** ⇒
    #:   把 `(0, <study>)` **元组**当成 study 传下去 ⇒ 下游 `study.StaticStudyOptions` 报
    #: `取 options 失败（family=ICWStaticStudyOptions）：SldWorks.Application.StaticStud
    #: yOptions`
    #:   （★ 那个对象名是**元组外面**的东西，★ 所以错误信息**看不出是元组问题**）。
    #:   ★★ 而这条**正好是「空名」那条路** ⇒ ★ **凡是没声明 `study_name` 的工具全部中招**
    #:     （★ 那 5 个求解器配置工具就没声明）⇒ ★ 那是一整片工具**一直没跑通**的原因。
    #: ⇒ ★ 修法：★ **取出来再解包**（★ 并用 `(None, None)` 兜底，★ 不与「None 当元组」混
    #: 淆）。
    if name:
        study = get_study_by_name(sw, name)
    else:
        _first = next(iter(iter_studies(sw)), (None, None))
        study = _first[1] if isinstance(_first, tuple) else _first
    if study is None:
        raise RuntimeError(
            "没找到研究（study_name=%r）—— 该文档里可能还没有 Simulation 研究" % name
        )
    return study


#: 注入名 → 解析器。`tool_registry` **不硬编码宿主 API**，全从这里供给。
def resolve_manager(params: Any):
    """按 `study_name` 解析**载荷与夹具管理器**（`ICWStudy.LoadsAndRestraintsManager`）。

    ★★ 为什么需要它（与 W6 给 `asm_model` 加一行的同一个理由，见 known-facts 169）：
      **注入名只能是这张表的键** ⇒ 而 `scripts/sw_simulation_loads.py` 里那批函数的
      首参叫 **`manager`**（不是 `study`）⇒ ★ 不加这一行它们就**挂不上**。
    ★ 解析链：连 SolidWorks → 按名字取研究（**复用 `resolve_study` 的逻辑**）→
      取该研究的载荷管理器。
    ⚠ 取不到时**抛错**（★ 不静默返回 None —— 否则会挂成一个「永远失败」的工具）。
    """
    from scripts.sw_simulation import _loads_and_restraints_manager

    return _loads_and_restraints_manager(resolve_study(params))


#: ★★ 2026-10-03（接手轮）· **修一批「注入键 ≠ 函数首参名」的工具（共 11 条）** ——
#: ★ 规范（本表的设计意图，逐字见下面 `manager` 那条注释）是：**`inject` 必须等于目标函
#: 数的首参名**。
#: ★ 依据（逐字核过源码）：`tool_registry.py:507` 是 `kwargs[inject_as or inj] = resolve
#: r(params)`，
#: 而 `register()`（同文件 `:559`）**不往下传 `inject_as`** ⇒ ★ **注入键字面上等于 `inje
#: ct` 的值**。
#:   ★★ **而仓内门禁 `scripts/check_param_binding.py` 抓不到这一类**：它的判据是
#:     「声明名 ∈ 形参 **或** ∈ `param_alias`」＋「**注入名是解析器的键**」
#:     ⇒ ★ **它从不检查「注入键等不等于目标函数的形参名」** ⇒ 这 11 条**全部漏过**。
#:   ★★★ **真机实测证据**：`solidworks_hole_standards` 按注册器真路径调 ⇒
#:     `TypeError: list_hole_standards() got an unexpected keyword argument 'sw_app'`
#:     （`output/inject-key-evidence.json`）。
def resolve_sw(_params: Any):
    """注入 `ISldWorks` —— ★ 供**首参名叫 `sw`** 的那批函数（★ 与 `sw_app` 是同一个对象）。"""
    return resolve_sw_app(_params)


def resolve_cost_manager(_params: Any):
    """注入 **Costing 管理器** —— ★ 供**首参名叫 `cost_manager`** 的那批函数。

    ★★ **为什么不复用 `manager`**：`resolve_manager` 的 docstring 逐字写着它解析的是
      **`ICWStudy.LoadsAndRestraintsManager`**（★ **Simulation 的**载荷与夹具管理器）
      ⇒ ★ **与 Costing 毫无关系** —— 那 8 条 Costing 工具**即便键名对上，也会注错对象**
      （★ 真机实测：报的是「没找到研究」）。
    """
    from scripts.sw_costing import get_costing_manager

    return get_costing_manager(resolve_model(_params))


#: ★★★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」）：**三个「从 study 取子对象」的解析
#: 器**。
#:
#: 为什么（★ 机械预筛给的判据）：★ **A/B 类（首参是标量或已有注入键）已被前三坡吃干** ——
#: 要到 SC-001 的 400 就必须解锁 **C 类（351 个，首参像 COM 对象）**；
#: ★ 而 C 类里 **~90 个**只需要几个**语义无歧义**的解析器，其中这三个最干净：
#:   · `results` ⇒ `ICWStudy.Results`（研究的**结果**对象）
#:   · `mesh`    ⇒ `ICWStudy.Mesh`（研究的**网格**对象）
#:   · `options` ⇒ 研究**选项**对象（★ 读参数里的 `study_name` 与 `family`）
#: ★ 与 `resolve_study` 同手法（都按 `study_name` 定位），只是**多走一步**取子对象 ✓
#: ⚠ **与「危险旋钮」的区别**：★ 这三个只**取对象**、不替调用方改设置 ⇒ 安全；
#: ★ 批 82 删掉的 `configure_mesh_settings` / `mesh_safety_apply` 是**会改设置**的原始旋
#: 钮
#:   （事实 526 的 40 GB 事故）⇒ ★ 那条禁令不受本次影响 ✓


def resolve_results(params: Any):
    """注入**研究的 `Results` 对象**（`ICWStudy.Results`）—— ★ 供首参名叫 `results` 的那批函数。

    ★ 定位方式与 `resolve_study` **完全一致**（读 `study_name`；空名取第一个研究）✓
    :raises RuntimeError: 研究上取不到 `Results`（★ 不返回 None 让下游崩在别处）
    """
    from scripts.sw_connect import get_com_member

    study = resolve_study(params)
    try:
        res = get_com_member(study, "Results")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "研究上取不到 `Results`（%s: %s）—— ★ 先跑一次求解再读结果"
            % (type(exc).__name__, str(exc)[:120])
        )
    if res is None:
        raise RuntimeError(
            "研究上 `Results` 为 None —— ★ 该研究**还没算出结果**"
            "（先 `solidworks_simulation_run_analysis`）"
        )
    return res


def resolve_mesh(params: Any):
    """注入**研究的 `Mesh` 对象**（`ICWStudy.Mesh`）—— ★ 供首参名叫 `mesh` 的那批函数。"""
    from scripts.sw_connect import get_com_member

    study = resolve_study(params)
    try:
        mesh = get_com_member(study, "Mesh")
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "研究上取不到 `Mesh`（%s: %s）—— ★ 先建网格"
            % (type(exc).__name__, str(exc)[:120])
        )
    if mesh is None:
        raise RuntimeError(
            "研究上 `Mesh` 为 None —— ★ 该研究**还没建网格**"
            "（用 `solidworks_simulation_create_mesh_safely`）"
        )
    return mesh


def resolve_view(params: Any):
    """注入**活动文档的活动视图**（`IModelView`）—— ★ 供首参名叫 `view` 的 `sw_view` 族函数。

    :raises RuntimeError: 活动视图取不到（★ 不返回 None 让下游崩在别处）
    """
    from scripts.sw_view import get_active_view

    return get_active_view(resolve_model(params))


# ── 墓碑（2026-10-07 接手轮 · 规格 214 T-214-03）─────────────────────────────
# ★ 这里原有 `resolve_active_sketch(params)`：注入**活动草图**（`IModelDoc2.GetActiveSke
# tch2`），
#   ★ 供首参叫 `sketch` 的那批函数（`scripts/sw_sketch.py` 的 25 个只读内省）✓
# ★★ **已删** —— 依据是 `tests/test_registry_wiring.py::test_no_unused_resolver`
#   （★ 方向与 `test_every_inject_name_has_a_resolver` 相反：**防"多"**）：
# ★ 它 **2026-10-04 加进来、却始终没有任何 spec 用**（实测 `inject="sketch"` 在 `mcp-ser
# ver/` 里 **0 处**）✗
#   ⇒ ★ 那条测试自己写着两条路：「**要么接上、要么删掉并说明**」⇒ ★ **本处走第二条** ✓
# ⚠ **为什么不是"接上"**（★ 那本来才更该做）：接上 = 把那 25 个函数挂成工具 ⇒
# ★ 那是**覆盖规格**的活，★★ 而它要**真机证据三件套**（`ToolSpec` + `capabilities.yaml`
# +
#   `output/*-evidence.json`）⇒ ★ **与规格 214 的硬约束「零真机」直接冲突** ✗
# ★★ **所以记在这里、不丢掉**：要接上时，照下面 `resolve_selection_manager` 的形状写一个
# 即可
#   （★ 语义与"没有活动草图就响亮报错、绝不猜用哪张草图"的文案见 git 历史）✓
# ★ 候选函数（`scripts/sw_sketch.py` 里首参为 `sketch`、当前未挂的）：`get_lines` · `get
# _arcs` ·
#   `get_ellipses` · `get_sketch_points` · `get_user_points` · `get_sketch_contours` ·
# `get_sketch_regions` · `get_relation_manager` · `get_model_to_sketch_transform` …（共
# 25 个）✓


def resolve_selection_manager(params: Any):
    """注入**活动文档的 `SelectionManager`** —— ★ 供首参叫 `selection` 的那批。

    ★ `IModelDoc2.SelectionManager` 是**文档自己的**选择管理器 ⇒ ★ **语义唯一**（不需要猜）✓
    """
    from scripts.sw_connect import get_com_member

    model = resolve_model(params)
    mgr = get_com_member(model, "SelectionManager")
    if mgr is None:
        raise RuntimeError(
            "文档上取不到 `SelectionManager` ⇒ `selection` 注入键无法解析"
        )
    return mgr


def resolve_cost_part(params: Any):
    """注入 **Costing 的「成本模型」对象**（`ICostModel`）—— ★ 供首参名叫 `cost_part` 的那批函数。

    ★ 依据（★ 仓里既有代码给的，不是猜的）：`scripts/sw_costing.py` 的
      `get_body_count_report(cost_manager)` 里逐字写着
      ``m, _d, err = _costing_chain(cost_manager)`` 然后 ``get_body_count(m)``
      —— 而 `get_body_count(cost_part)` 的首参就叫 `cost_part`
      ⇒ ★★ **`cost_part` 就是 `cost_manager` 取出来的那个「成本模型」对象** ✓
    """
    from scripts.sw_costing import get_costing_model

    return get_costing_model(resolve_cost_manager(params))


def resolve_cost_analysis(params: Any):
    """注入 **Costing 的「成本分析」对象**（`ICostAnalysis`）—— ★ 供首参名叫 `cost_analysis` 的那批。

    ★ 取法：`cost_part`（成本模型）→ `GetCostAnalysis` ✓（★ 与 `cost_part` 同一条链，不是猜的）
    ⚠ ★ **零件上还没有成本分析就没有** ⇒ **响亮报错**并说清先做什么 ✓
    """
    from scripts.sw_costing import get_cost_analysis

    analysis = get_cost_analysis(resolve_cost_part(params))
    if analysis is None:
        raise RuntimeError(
            "该零件上**还没有成本分析** ⇒ `cost_analysis` 注入键无法解析。"
            "★ 请先建一个成本分析（`sw_costing.create_cost_analysis`）"
        )
    return analysis


def resolve_cost_body(params: Any):
    """注入**成本实体**（`ICostBody`）—— ★ 供首参名叫 `cost_body` 的那批函数。

    ★ 定位规则（★ 与 `motion_study` 同一手法：**能唯一确定才给，否则响亮报错**）：
      ① 传了 `body_name` ⇒ 按名在 `get_bodies(cost_part)` 的清单里找 ✓
      ② 没传：清单长度 **== 1** ⇒ 就那一个；**0** 或 **>1** ⇒ ★ 报错并列出可用的名字 ✓
    """
    from scripts.sw_costing import get_bodies

    name = str(getattr(params, "body_name", "") or "").strip()
    bodies = list(get_bodies(resolve_cost_part(params)) or [])
    if not bodies:
        raise RuntimeError(
            "该零件的成本模型上**没有成本实体** ⇒ `cost_body` 注入键无法解析"
        )
    if name:
        for b in bodies:
            try:
                got = str(sw_get_member_name(b))
            except Exception:  # noqa: BLE001
                got = ""
            if got == name:
                return b
        raise RuntimeError(
            "没有名为 %r 的成本实体；现有：%r"
            % (name, [sw_get_member_name(b) for b in bodies][:10])
        )
    if len(bodies) > 1:
        raise RuntimeError(
            "该零件有 **%d 个**成本实体 ⇒ ★ **本解析器不替你猜**，"
            "请显式传 `body_name`（现有：%r）"
            % (len(bodies), [sw_get_member_name(b) for b in bodies][:10])
        )
    return bodies[0]


def sw_get_member_name(obj: Any) -> str:
    """★ 小助手：取成本实体的名字（官方 `GetName`）—— ★ 取不到就回空串（不抛）。"""
    from scripts.sw_connect import get_com_member

    try:
        return str(get_com_member(obj, "GetName") or "")
    except Exception:  # noqa: BLE001
        return ""


def resolve_motion_study(params: Any):
    """注入**运动算例**（`IMotionStudy`）—— ★ 供首参名叫 `motion_study` 的那批函数。

    ★ 定位规则（★ **能唯一确定才给，否则响亮报错** —— 与我给 `family` 的处理同一手法）：
      ① 传了 `motion_study_name` ⇒ 按名取（官方 `GetMotionStudy(String MotionStudyName)`）✓
      ② 没传：算例数 **== 1** ⇒ 就那一个；**0** 或 **>1** ⇒ ★ **报错并说清该怎么办** ✓
         （★ 0 ⇒ 先 `solidworks_motion_create_study`；★ >1 ⇒ 请补 `motion_study_name`）✓
    """
    from scripts.sw_motion import get_motion_study_manager, motion_member

    name = str(getattr(params, "motion_study_name", "") or "").strip()
    #: ★ 注：本解析器需要**装配体**（运动算例挂在装配上）⇒ 用 `asm_model` 那条口子取文档
    model = resolve_model(params)
    mgr = get_motion_study_manager(model)
    if mgr is None:
        raise RuntimeError(
            "取不到 `MotionStudyManager` ⇒ ★ 先确认 Motion 加载项可用"
            "（`solidworks_motion_ensure_type_library`）"
        )
    if name:
        study = motion_member(mgr, "GetMotionStudy", name)
        if study is None:
            names = motion_member(mgr, "GetMotionStudyNames") or []
            raise RuntimeError(
                "没有名为 %r 的运动算例；现有：%r" % (name, list(names)[:10])
            )
        return study
    count = int(motion_member(mgr, "GetMotionStudyCount") or 0)
    if count == 0:
        raise RuntimeError(
            "该装配上**没有运动算例** ⇒ `motion_study` 注入键无法解析。"
            "★ 请先 `solidworks_motion_create_study`"
        )
    if count > 1:
        names = motion_member(mgr, "GetMotionStudyNames") or []
        raise RuntimeError(
            "该装配上有 **%d 个**运动算例 ⇒ ★ **本解析器不替你猜用哪一个**，"
            "请显式传 `motion_study_name`（现有：%r）" % (count, list(names)[:10])
        )
    return motion_member(
        mgr,
        "GetMotionStudy",
        str(list(motion_member(mgr, "GetMotionStudyNames") or [])[0]),
    )


def resolve_costing_defaults(params: Any):
    """注入 **Costing 的默认值对象** —— ★ 供首参名叫 `defaults` 的 `sw_costing` 族函数。

    ★ 由 `cost_manager` 取（复用 `resolve_cost_manager`，它已处理「本机有没有 Costing 加载项」）✓
    """
    from scripts.sw_costing import get_costing_defaults

    return get_costing_defaults(resolve_cost_manager(params))


def resolve_selected_component(params: Any):
    """注入**当前选中的第一个组件**（`IComponent2`）—— ★ 供首参名叫 `component` 的那批函数。

    ⚠ ★ **没有选中就没有** ⇒ ★ **响亮报错**，★ **绝不猜**（"取第一个组件"是另一种对象，
      语义不同 —— 事实 36 那一族）✓
    """
    from scripts.sw_selection import get_selected_component
    from scripts.sw_connect import get_com_member

    model = resolve_model(params)
    #: ★★★ 2026-10-04（接手轮 · **真机探针**发现并修）：这里原先把 **`model`** 当 `selec
    #: tion` 传进去
    #:   —— ★ 而 `get_selected_component` 的首参要的是 **`ISelectionMgr`**（选区管理器），
    #:   不是文档 ⇒ ★★ 真机上报 `<unknown>.GetSelectedObjectsComponent3/4`
    #:   （★ 事实 36 那一族的形态：**对象错了，表现是"这个成员不存在"**）✓
    #: ⇒ 正解：先取 `model.SelectionManager`，再交给它 ✓（与 `resolve_selection_manager`
    #:  同一步）
    sel = get_com_member(model, "SelectionManager")
    if sel is None:
        raise RuntimeError(
            "文档上取不到 `SelectionManager` ⇒ `component` 注入键无法解析"
        )
    #: ★★★ 2026-10-04（真机探针）：`ISelectionMgr` 的 **Index 是 1 基** ——
    #: 实测（`output/selectionmgr-member-probe.json`）：`GetSelectedObjectCount2(-1)` 回
    #:  **1**、
    #: 而 `GetSelectedObjectsComponent4(**0**, 0)` 回 `None`、`GetSelectedObject6(**1**,
    #:  -1)` 回得到对象
    #:   ⇒ ★★ 取「第一个选中的东西」要用 **1** 而不是 0（★ 我原先传 0 ⇒ 静默拿到 `None`）✓
    comp = get_selected_component(sel, 1)
    if comp is None:
        raise RuntimeError(
            "当前**没有选中的组件** ⇒ `component` 注入键无法解析。"
            "★ 请先在装配里选中一个组件（★ 本键**不替你猜**该用哪一个）"
        )
    return comp


def resolve_study_options(params: Any):
    """注入**研究选项对象** —— ★ 供首参名叫 `options` 的那批函数。

    ★ 读两个参数：`study_name`（定位研究，空名取第一个）与 `family`（选项族）✓

    ★★★ 2026-10-04（接手轮）**收掉一个静默陷阱**（★ 由 Bunny 扇出**如实上报**后我核实的）：
      第一版把 `family` **缺省成 `ICWStaticStudyOptions`** —— ★ 而 `sw_simulation_study_options`
      里那几个原始函数（`configure_static_solver` / `configure_frequency_solver` /
      `configure_buckling_solver`）**各自硬编码自己的族**、**形参里根本没有 `family`** ⇒
      ★★ 若将来有人把这类函数挂成工具，缺省值会**静默地把频率/屈曲选项注成"静态选项对象"**
      （★ 事实 36 那一族的形态：**对象错了，表现是"什么都没发生"**）✓
    ⇒ ★ 改为**响亮失败**：拿不到 `family` 就报错并说清"要么把它声明成参数、要么别用 `options` 键" ✓
      ★ 代价为零 —— 现有用 `options` 键的两个工具（`set_option` / `set_options`）**都声明了 `family`** ✓
    """
    from scripts.sw_simulation_study_options import study_options_of

    family = str(getattr(params, "family", "") or "").strip()
    if not family:
        raise RuntimeError(
            "`options` 注入键拿不到**选项族 `family`** ⇒ 无法确定该注哪个选项对象。"
            "★ 这**不能靠猜**：不同族（静态/频率/屈曲）是**不同的对象**，注错了表现为"
            "「什么都没发生」（事实 36 那一族）。"
            "★ 正解二选一：① 把 `family` 声明成工具参数（既有两个工具就是这么做的）；"
            "② 若目标函数**自己**硬编码了族，就别用 `options` 键 —— ★ 本解析器**不替它猜**"
        )
    study = resolve_study(params)
    opts = study_options_of(study, family)
    if opts is None:
        raise RuntimeError("取不到研究选项族 %r —— ★ 该研究可能不属于这一族" % family)
    return opts


RESOLVERS: dict[str, Any] = {
    "model": resolve_model,
    "sw_app": resolve_sw_app,
    "study": resolve_study,
    #: ★ 轮 237（砌墙 W6 / Spec Kit `139`）：**注入名只能是这张表的键**（见 known-facts
    #: 169）
    #: —— 而 `scripts/sw_assembly.py` 里有一批函数的首参叫 **`asm_model`**（不是 `model`
    #: ）。
    #: ★ 装配文档**同样是 `IModelDoc2`** ⇒ 复用同一个解析器；★ 不动 `tool_registry`（它
    #: 明确
    #:   「不硬编码宿主 API，全从这里供给」）⇒ **加一行正是这张表的设计用途**。
    "asm_model": resolve_model,
    #: ★ 24h 计划 段 2.1（Spec Kit `143`）：`sw_simulation_loads` 那批函数首参是 `manage
    #: r`
    #: ⇒ 加一行即可挂（★ 这条表**就是**为「注入名各不相同」而设计的，见 known-facts 169
    #: ）。
    "manager": resolve_manager,
    #: ★ 2026-10-03（接手轮）：**工程图 subskill 里的函数首参叫 `drawing_model`**
    #: —— 实现文件 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py
    #: `，
    #: 经 `scripts/sw_drawing.py`（`spec_from_file_location` 按路径加载后再逐个导出公开
    #: 名）可达。
    #: ★ 依据（逐字核过源码）：`tool_registry.py:507` 是 `kwargs[inject_as or inj] = res
    #: olver(params)`，
    #: 而 `register()`（同文件 `:559`）**不往下传 `inject_as`** ⇒ **注入键字面上等于 `in
    #: ject` 的值**；
    #: ★ 而那个文件的父目录名 `solidworks-engineering-drawing` **带连字符**（非合法标识
    #: 符）
    #: ⇒ 无法写进 `module=`（`tool_registry.py:524` 是 `__import__("scripts.%s" % spec.m
    #: odule, …)`）。
    #:   ⇒ ★ 不在这里加这一行，任何挂它的工具都会在运行期
    #:     **`TypeError: unexpected keyword argument 'model'`**。
    #: ★ 工程图文档同样是 `IModelDoc2` ⇒ **复用 `resolve_model`**，与 `asm_model` 同一手
    #: 法。
    #:   ★ 本条由 space-bunny 的 L3 档实测发现、Lead 逐条核源码确认
    #:     （见 `specs/202-user-coverage-gaps/recon/bunny-L3-toolspec-draft.py.txt`）。
    "drawing_model": resolve_model,
    #: ★★ 2026-10-03（接手轮）：修「注入键 ≠ 函数首参名」那 11 条 —— 见上面两个新函数前
    #: 的长注释。
    #:   `sw`：`batch10` 的 3 条（孔标准/紧固件类型/紧固件表类型）函数首参叫 **`sw`**；
    #:   `cost_manager`：`batch38` 的 8 条 Costing 工具首参叫 **`cost_manager`**
    #:     （★ 它们原先声明 `inject="manager"` —— 而那是 **Simulation** 的解析器）。
    "sw": resolve_sw,
    "cost_manager": resolve_cost_manager,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 204 的批 79）：**`doc`** ——
    #:   ★ 那一批是**装配爆炸视图 9 个**（`scripts/sw_assembly_doc.py` 里新增的包装）——
    #: ★★ **它们的首参叫 `doc`**（该模块**既有**的 `add_mate(doc)` / `hide_component(doc
    #: , …)`
    #:     一律用 `doc`），★ 而 `RESOLVERS` 里**只有 `model` / `asm_model`，没有 `doc`** ⇒
    #:   ★★★ 我第一版写 `inject="asm_model"` ⇒ `check_param_binding` **当场报**：
    #: 「`inject='asm_model'` **不在函数的形参表里**（形参：['doc']）—— ★ `register()`
    #: 不传
    #:      `inject_as` ⇒ **注入键字面上等于 inject 的值** ⇒ 调用时必
    #: `TypeError: unexpected keyword argument 'asm_model'`」（★ 事实 502/169 的同一回事
    #: ）✓
    #:   ⇒ ★ 按那张表**自己的设计意图**加这一行（"注入名各不相同 ⇒ 加一行正是它的用途"），
    #:     ★ **而不是去改包装的形参名**（那会让 `sw_assembly_doc.py` 内部风格分裂）✓
    #: ★ 装配/零件文档都是 `IModelDoc2` ⇒ **复用 `resolve_model`**，与上面 `asm_model`
    #: 同一手法 ✓
    "doc": resolve_model,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205 的批 80）：**`sldworks`** ——
    #: ★ `scripts/sw_automation_knowledge.py` 那 6 个函数（命令锁 / 首选项开关 / 自弹提
    #: 示）
    #: 的**首参叫 `sldworks`**（★ 它们是 `ISldWorks` 上的操作）⇒ 白名单里既没有 `sldwork
    #: s`
    #:     也没有它等价的键名 ⇒ ★ 事实 502（注入键**字面当关键字**传入）下必 `TypeError` ✓
    #:   ★ 复用 `resolve_sw`（= `resolve_sw_app`，回 `ISldWorks`）——
    #:     ★ 与该表既有的 `sw` 键**同一手法**（`sw` 也是为此加的，见上方 `"sw"` 那条）✓
    "sldworks": resolve_sw,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205 的「解锁 C 类」）：**`results` / `mesh` / `op
    #: tions`** ——
    #: ★★ 为什么要加（★ 机械预筛给的判据）：★ A/B 类（首参是标量或已有注入键）**已被前三
    #: 坡吃干**，
    #:     要到 400 必须解锁 **C 类（351 个，首参像 COM 对象）**；
    #:   ★ 而 C 类里 **~90 个**只需几个「**从 study 取**」的解析器 —— ★ **语义无歧义**：
    #:     · `results` ⇒ `ICWStudy.Results`（研究的**结果**对象）
    #:     · `mesh`    ⇒ `ICWStudy.Mesh`（研究的**网格**对象）
    #: · `options` ⇒ 研究**选项**对象（★ 与 `resolve_study` 同手法：**读参数**里的 `stud
    #: y_name`
    #:       与 `family`，缺省取第一个研究 / `ICWStaticStudyOptions`）✓
    #: ★ 它们与 `resolve_study` 是**同一种**解析器（都按 `study_name` 定位），只是**多走
    #: 一步**
    #:     从 study 上取子对象 ⇒ ★ 与事实 169 那张表的设计意图一致 ✓
    #:   ⚠ **与「危险旋钮」的区别**：★ 这三个只**取对象**、不替调用方改设置 ⇒ 安全；
    #: ★ 而批 82 删掉的 `configure_mesh_settings` / `mesh_safety_apply` 是**会改研究设置
    #: **的
    #:     原始旋钮（事实 526 的 40 GB 事故）⇒ ★ 那条禁令不受本次影响 ✓
    "results": resolve_results,
    "mesh": resolve_mesh,
    "options": resolve_study_options,
    #: ★★★★★ **`view`** —— ★ 解锁 `sw_view.py` 的 **26 个**候选（它们的首参都叫 `view`，
    #: 是
    #: **`IModelView`**，而"活动文档的活动视图"**语义唯一**）⇒ ★ 仓里已有 `sw_view.get_a
    #: ctive_view` ✓
    #: ⚠⚠ **禁忌（可执行）**：★ `sw_drawing_view.py` 里那些首参**也叫 `view`**，但它们是
    #:   **`IView`（图纸视图）**、**不是** `IModelView` ⇒ ★ 用本键注给它们会**注错对象**
    #:   （★ 事实 36 那一族：接口/对象错了表现为「什么都没反应」，最难看）
    #:   ⇒ ★ 由 `tools/check_bunny_toolspec_rows.py` 的 **⑪** 挡住：
    #:     `module == "sw_drawing_view"` ∧ `inject == "view"` ⇒ **判废** ✓
    #: ★ 要挂 `sw_drawing_view` 那族，得**另加**一个按名字取 `IView` 的解析器（本轮未加
    #: ）✓
    "view": resolve_view,
    #: ★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」第二批）：**`defaults` / `component
    #: `** ——
    #:   ★ 两个都**语义唯一**（不是「取哪一个」的猜测）：
    #:     · `defaults` ⇒ **Costing 的默认值对象**（★ 由 `cost_manager` 取，仓里已有
    #:       `sw_costing.get_costing_defaults(cost_manager)`）⇒ 解锁 5 个 `sw_costing` 候选 ✓
    #: · `component` ⇒ **当前选中的第一个组件**（★ 仓里已有 `sw_selection.get_selected_c
    #: omponent`；
    #:       ★ **没有选中就没有** ⇒ 响亮报错，**不猜**）⇒ 解锁 9 个候选 ✓
    #: ⚠ 与之相对：★ `win` / `hwnd` / `ctrl` / `obj` / `sketch` / `selection` 那几组**一
    #: 律不碰**
    #:     —— ★ 它们是「取哪一个？」的问题（事实 36 那一族）；
    #: ★★ 特别地 `obj`（18 个）**出在 `sw_api_*.py`** —— ★ 那些是**反射转储**、不是能力
    #: 实现
    #:     ⇒ ★ 已把 `sw_api_*` 加进选域黑名单（它们**不该**出现在候选里）✓
    "defaults": resolve_costing_defaults,
    "component": resolve_selected_component,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」第三批）：**`sketch` / `selection
    #: `** ——
    #: ★★ 这两组是 C 类里**剩下的最大两块**，而它们的语义**同样唯一**（不是「取哪一个」
    #: 的猜测）：
    #: · `sketch`    ⇒ **活动草图**（`IModelDoc2.GetActiveSketch2`）—— ★ 解锁 `sw_sketch
    #: .py`
    #:       那 **~20 个只读内省函数**（取线/弧/椭圆/样条/点/轮廓/区域/块实例/关系管理器/
    #:       是否 3D 草图/模型到草图变换…）✓
    #: · `selection` ⇒ **活动文档的 `SelectionManager`**（`IModelDoc2.SelectionManager`
    #: ）——
    #:       ★ 解锁 `sw_selection.py` 那批（选择集读数 / 按对象选 / 清选 …）✓
    #:   ⚠ 两者**没有**就先**响亮报错**（★ 不猜、不静默失败）✓
    #: ★★★ 2026-10-07（接手轮 · 规格 214 T-214-03）：**`"sketch"` 这一行已删** ——
    #:   ★ 判据 `tests/test_registry_wiring.py::test_no_unused_resolver`（**防"多"**）：
    #: ★★ 它 2026-10-04 加进来，**却始终没有任何 spec 用**（`inject="sketch"` 实测 **0
    #: 处**）✗
    #:   ⇒ ★ 该测试给的两条路（**接上 / 删掉并说明**）里，本处走第二条 ——
    #: ★★ 理由：**接上要真机三件套**，与规格 214 的「零真机」冲突 ⇒ ★ 它属于**覆盖规格**
    #: 的活 ✓
    #: ★ 要接上时照 `resolve_selection_manager` 的形状写即可；★ 墓碑与候选函数清单在**上
    #: 面**
    #:     （`resolve_active_sketch` 原来所在处）✓
    "selection": resolve_selection_manager,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」第四批）：**`cost_part` / `motion
    #: _study`** ——
    #:   ★ C 类里**最后两组语义无歧义**的：
    #: · `cost_part` ⇒ **Costing 的成本模型对象**（★ 依据在仓里：`get_body_count_report`
    #:  里
    #: 逐字把 `_costing_chain(cost_manager)` 取出的对象喂给 `get_body_count(cost_part)`
    #: ）✓
    #: · `motion_study` ⇒ **运动算例**（★ 按 `motion_study_name` 取；未传时**只在算例数
    #: == 1**
    #:       才给，0 或 >1 都**响亮报错** ⇒ 不猜）✓ —— ★ AVI 导出是三个**护城河域**之一 ✓
    #: ⚠ 其余 C 类组（`win`/`hwnd`/`ctrl`/`obj`/`target`/`route_manager`/`sketch` 的图纸
    #: 侧…）
    #:     **一律不碰** —— ★ 它们是「取哪一个？」的问题（事实 36 那一族）✓
    "cost_part": resolve_cost_part,
    "motion_study": resolve_motion_study,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」第五批）：**`cost_analysis` / `co
    #: st_body`** ——
    #: ★ 勘探（`output` 的 C 类普查）显示：C 类里**剩下 97 个是「取哪一个」的歧义组**（
    #: 一律不碰）；
    #:     而 `cost_analysis`(3) + `cost_body`(2) 这 **5 个**仍可加键 ⇒ 组内**真新 3 个** ✓
    #:     · `cost_analysis` ⇒ `cost_part` → `GetCostAnalysis`（★ 同一条链，不是猜的）✓
    #:     · `cost_body` ⇒ 按 `body_name` 在 `get_bodies(cost_part)` 清单里找；
    #: **没传名时只在清单长度 == 1** 才给，0 或 >1 都**响亮报错**（★ 与 `motion_study`
    #: 同手法）✓
    "cost_analysis": resolve_cost_analysis,
    "cost_body": resolve_cost_body,
}

#: 全部批次（**按注册顺序**）。新增批次只在这里加一行。
BATCH_MODULES = (
    "tool_specs_batch1",
    "tool_specs_batch2",
    "tool_specs_batch3",
    "tool_specs_batch4",
    "tool_specs_batch5",  # 轮 90：孤立能力暴露的第一步（只读/视图/选择）
    "tool_specs_batch6",  # 轮 93：孤立能力暴露的第二步（无参选择器 / BOM）
    "tool_specs_batch7",  # 轮 96：孤立能力暴露的第三步（预览准备 / 场景刷新）
    "tool_specs_batch8",  # 轮 97：**换池子** —— 从未暴露且「只被测试调用」的那批取
    "tool_specs_batch9",  # 轮 98：模具域「已实现 + 有测试 + 未暴露」的 3 个
    "tool_specs_batch10",  # 轮 128：把轮 123~127 **查证并真机跑过**的 4 个高层入口接出去
    #: 轮 204（Spec Kit `123`）：★ **候选先变成「可复现的全量清单」再选** ——
    #: `probe_unexposed_functions.py` 此前只印前 30（302 里 87% 看不见）⇒ 本轮先给它加结
    #: 构化输出，
    #: 再从「首参可注入」的 51 个里取**拓扑的目标/约束/控制**这一族 4 个。
    "tool_specs_batch11",
    #: 轮 205（Spec Kit `124`）：★ **先把枚举核清再挂** —— 上批因「枚举值未核」留批的三
    #: 个
    #: （脱模方向 / 应力比较器 / 对称类型），取值来自出厂反射转储 + 官方 VBA 示例。
    "tool_specs_batch12",
    #: 轮 206（Spec Kit `125`）：仿真研究的报告 / 按控制划网格 / 建议网格尺寸 3 个；
    #: ★ 并把一处"两源冲突"（units=-1 到底行不行）**原样写进参数描述**，不合并成一种说法
    #: 。
    "tool_specs_batch13",
    #: 轮 207（Spec Kit `126`）：视图读取 + 体上实体枚举 2 个；
    #: ★ 队列原本列了 4 个，实测另 2 个（activate_view / add_perspective）首参是 `view`
    #:   ⇒ 既有注入器没有它 ⇒ **不硬挂**，记进 A10（先定行为再做包装层）。
    "tool_specs_batch14",
    #: 轮 208（Spec Kit `127`）：结构化审查报告 1 个；
    #: ★ 队列原本列 2 个 —— 另一个 activate_plot 首参是 `results`/ICWResults，不在注入点
    #: 里
    #: ⇒ **不硬挂**（记进 A10）；本批也**不暴露** views/expected_outputs（**list 型无先
    #: 例**）。
    "tool_specs_batch15",
    #: 轮 209（Spec Kit `128`）：草图几何关系 + 镜像特征 2 个；
    #: ★ 队列 A5 原写 add_sketch_relation/add_dimension —— 实测 add_dimension **碰规则 3
    #: **（裸坐标）⇒ 留批；
    #:   而「干净」里的 insert_composite_curve **本来就坏**（事实 121/124）⇒ **不挂**。
    "tool_specs_batch16",
    #: 轮 211（Spec Kit `130`）：圆形阵列 + 旋转凸台 2 个；
    #: ★ 并**落定规则 2 的角度换算边界** —— `_consumed(angle_deg)` + `derived_args` 用
    #:   `sw_connect.deg()` 换算一次（**改名不换算会把「度」当「弧度」静默传进去**）。
    "tool_specs_batch17",
    #: 轮 222（砌墙 W1 / Spec Kit `131`）：草图只读查询 4 个；
    #: ★ 取草图对象**只能按名取**（真机探针：GetActiveSketch2/ActiveSketch 在草图关闭后
    #: 均 None）；
    #: ★ 挂的是「只回读数」的薄函数（get_lines 返回数值数组，AI 没法从 36 个 float 判断
    #: 几条线）。
    "tool_specs_batch18",
    #: 轮 224（砌墙 W2 / Spec Kit `132`）：当前活动工程图的轻量只读读数 3 个；
    #: ★ 与 `solidworks_inspect_drawing` 的分工是「**不**要路径、**不**开件、**不**出预
    #: 览」；
    #: ★ 两点真机坑已处理：宽高是**米**（已换算成 mm）· 图纸本身会被当成假视图（已过滤）
    #: 。
    "tool_specs_batch19",
    #: 轮 227（砌墙 W3 / Spec Kit `133`）：**读文件自定义属性** 2 个；
    #: ★ 补的是真空白 —— 本仓库能「写」属性（上游工具）却**读不回来验**；
    #: ★ 两个真机坑：`Extension.CustomPropertyManager` **必须当方法调用**；
    #:   读值只能用 `Get(name)`（`Get2..Get6` 的 by-ref out 在 pywin32 下报类型不匹配）。
    "tool_specs_batch20",
    #: 轮 229（砌墙 W4 / Spec Kit `135`）：**建草图 + 画几何** 5 个；
    #: ★ 本批补的是**最底层的短板** —— 此前 MCP 里连草图都建不了，
    #:   以致已挂的 revolve_boss / create_hole_feature / 钣金 base_flange **全都用不了**；
    #: ★ 画几何必须给平面内坐标 ⇒ 参数用**语义名 + _mm**（规则 2 合规 + 规则 3 的豁免路
    #: 径）。
    "tool_specs_batch21",
    #: 轮 230（砌墙 W4 续 / Spec Kit `136`）：**拉伸族** 3 个；
    #: ★ **第一批能建出实体**的工具 —— 与 batch21（建草图）合起来才是完整建模闭环；
    #: ★ `depth`/`total_depth` 用 param_alias 改成 `_mm`（能力层一行未改）；★ 不做换算（
    #: 毫米）；
    #: ★ chamfer/fillet 不在本批 —— 它们要**选择**（selection 包装层），单独一批做。
    "tool_specs_batch22",
    #: 轮 231（砌墙 W4 续 / Spec Kit `137`）：**倒角 / 圆角** 2 个；
    #: ★ **第一次用规则 3 的声明式 `selection` 驱动「建特征」工具** ——
    #:   能力层两个函数**都没有 edges 参数** ⇒ 它们作用在**当前选择**上 ⇒
    #:   对外的 selection 由 `pre_call` 解析成真实选区（复用 batch4 的既有机制）。
    "tool_specs_batch23",
    #: 轮 234（砌墙 W5 / Spec Kit `138`）：**读质量属性** 1 个；
    #: ★ 又一个「能写不能读」的真空白（有 set_mass_property_override 却读不出实际值）；
    #: ★ 单位是**毫米系**（实测，非 SI 米）⇒ 不做换算；
    #: ⚠⚠ **`mass` 的物理单位未确证**（volume×density 量纲不成立）⇒ 说明里明写，不猜。
    "tool_specs_batch24",
    #: 轮 237（砌墙 W6 / Spec Kit `139`）：**装配只读** 3 个；
    #: ★ 本批第一次用 `inject="asm_model"` —— 为此给 RESOLVERS **加了一行**；
    #: ★★ 干涉检查那个函数**修过三处成员名却从没验过**（其注释自述「此前静默降级」）
    #:   ⇒ 本批的真机验证是它的**第一次验证**，且设计成**一正一反两个场景**。
    "tool_specs_batch25",
    #: 轮 238（砌墙 W7 / Spec Kit `140`）：**仿真载荷包装层** 2 个 —— ★★ **护城河**。
    #: ★ 核实过：四家合计只有 4 个仿真工具，且**全是"建研究/跑"**，**没有一个挂载荷/约束
    #: **。
    #: ★ 而能力层**早已包装好**（`apply_fixed_restraint(study, …)` / `apply_normal_force
    #: (study, …)`）
    #:   ⇒ 本批即目标里那句「**有就直接挂**」。
    #: ★ 包装形状是**三种机制的组合**：`inject="study"` + `pre_call`（先选面）+ `derived
    #: _args`（补 model）。
    "tool_specs_batch26",
    #: 轮 239（24h 计划 段 1.1 / Spec Kit `141`）：**仿真研究族** 3 个（建/取/列）——
    #: ★★ **补 W7 的硬前置**（此前 `study_name` 只能引用已存在的研究）。
    #: ★ 3 个薄函数包既有四个：`create_static_study` 回**三元组**（含 COM 对象 + `entry_
    #: name`）、
    #: `iter_studies` yield **`(index, study)` 元组**、`get_study_by_name` 回**对象或 No
    #: ne**
    #:   ⇒ ★ 都不可直接挂（MCP 回不了对象）⇒ 各包一层只回可 JSON 化的东西。
    "tool_specs_batch27",
    #: ⚠⚠⚠ **轮 240：`tool_specs_batch28.py`（网格/求解/读数 4 个）**已注册但**未真机验
    #: 证**** ——
    #:   ★ 真机验证**三次都触发 Simulation 的模态框**「未定义载荷或规定的位移」
    #: （框内原文：「**固定-刚性零件上的载荷将不处于活动状态**」）⇒ **COM 挂起、救不回来
    #: **；
    #: 加了两道前置门（材料回读非空 + `LoadsAndRestraintsManager.Count >= 2`）**仍然弹**
    #: 。
    #:   ⇒ ★ 按 `AGENTS.md` 硬约束③：**明确标注「未真机验证」**（★ 不谎称验证过），
    #:     能力条目等级 = **`stitched`**（不是 `verified`）。
    #: ★ 查清的正路 = **对照实验逐个分离变量**（事实 165 第 12 条）—— 见 known-facts 174
    #: 。
    #: ★★★★★ **2026-10-04（接手轮）本条已被查清并推翻 —— 留此仅为可追溯**（★ 事实 528）
    #: ：
    #: ★ 真根因**不是**"前置门不够"，而是**力的面选不中** —— 配方用 `select_face_at(0,0,
    #: 0)`
    #:       而**原点在实体内部** ⇒ `SelectByID2("","FACE",0,0,0,…)` 回**选区计数 0**
    #:       （★ 这条真机对比**就写在本仓 `sw_simulation.select_face_at` 的注释里**）
    #:       ⇒ 空 `DispArray` ⇒ **载荷建成也无效** ⇒ 那个框 + `Results` 为空 ✓
    #: ★★ 处置：两个 apply 新增 **`face_selector`**（声明式、零坐标）⇒ **选不中就拒绝**
    #: ；
    #:       探针/配方改用 `-z`/`+z` ⇒ ★ **一跑成功**：网格 6541 单元 / 求解 **2.6 s** ·
    #:       **`results_present=True` · `plot_count=4`** ✓
    #: ★ 所以 `analysis_run_readback` 已由 `stitched` **升为 `verified`**；★ 本批 4 个工
    #: 具
    #:       **不必再挂着"未真机验证"** —— ★ 而**推荐入口**见 `tool_specs_batch78`（安全链）✓
    "tool_specs_batch28",
    #: ★ 24h 段 2.1（Spec Kit `143`）：载荷族广度 4 个（压力/力矩/重力/离心力）
    #:   —— ★ 首参是 `manager` ⇒ 靠上面新加的 `"manager"` 解析键注入。
    "tool_specs_batch29",
    #: ★ 24h 段 2.2（Spec Kit `144`）：拓扑读数与参数 6 个
    #:   —— ★ 只读数/设参数，**不跑求解** ⇒ 无挂起风险。
    "tool_specs_batch30",
    #: ★ 24h 段 5「修地基」（Spec Kit `145`）：建网格前的**地基闸门** 1 个
    #: —— ★ 把「跑求解必挂」掐断在网格之前（与 `sw_isolate` 互补：一个防发生、一个防外溢
    #: ）。
    "tool_specs_batch31",
    #: ★ 24h 段 3（Spec Kit `146`）：建模闭环补全 4 个
    #:   —— ★ 四个都**不吃裸坐标**（规则 3），且**统一回读确认**（规则 6）。
    "tool_specs_batch32",
    #: ★ 24h 段 4（Spec Kit `147`）：**配置族 6 + 导出族 6**
    #:   —— ★ 两族**全无裸坐标**（规则 3）· 配置族能力层回 dict ⇒ 直挂；
    #:     导出族按铁律包成「**文件存在且非空**」的回读报告。
    "tool_specs_batch33",
    #: ★ 24h 段 4 续（Spec Kit `151`）：**声明式建孔 5 个** —— ★ 规则 3 合规版
    #: （★ 上游那个 `solidworks_create_hole_feature` 吃裸坐标 `center_x_mm/center_y_mm`
    #: ）。
    "tool_specs_batch34",
    #: ★ 24h 段 4 续（Spec Kit `152`）：**焊件读数与切割清单 6 个**
    #:   —— ★ 10 个未挂里按「入参能不能表达」筛出的 6 个（★ 全无裸坐标）。
    "tool_specs_batch35",
    #: ★ 24h 段 4/5 续（Spec Kit `153`）：**读数与纯数据 11 个**
    #:   —— ★ 薄模块里按「入参能不能表达」筛出（★ 全无裸坐标）。
    "tool_specs_batch36",
    #: ★ 24h 段 1 续（Spec Kit `154`）：**求解器设置 5 个**
    #:   —— ★ 注入 `study` + 包装内部取 options（★ **不动 RESOLVERS**）。
    "tool_specs_batch37",
    #: ★ 24h 段 4 续（Spec Kit `155`）：**Costing 读数 8 个**
    #:   —— ★ 护城河域（三个全网空白域之一）；★ 注入 manager + 内部取下游。
    "tool_specs_batch38",
    #: ★ 24h 段 5 续（Spec Kit `156`）：**方程 4 + 螺旋 1 + 形位公差 1**
    #:   —— ★ 填 `equations` / `helix_and_spiral` / `gtol_insert` 三条**空条目**。
    "tool_specs_batch39",
    #: ★ 24h 段 5 续（Spec Kit `157`）：**运动算例 6 个**
    #:   —— ★ 填 `motion_study`（verified 却 0 工具）；用已有的 `asm_model` resolver。
    "tool_specs_batch40",
    #: ★ 24h 段 5/6 续（Spec Kit `158`）：**齿轮 2 + Toolbox 4 + 草图编辑 3**
    #: —— ★ 填三条空条目（external_spur_gear_geometry / standard_parts_toolbox / sketch_
    #: chamfer）。
    "tool_specs_batch41",
    #: ★ 24h 段 6 续（Spec Kit `159`）：**工程图读数 2 个**
    #:   —— ★ 它们的函数一直在（sw_drawing_query），只是没挂工具。
    "tool_specs_batch42",
    #: ★ 24h 段 6 续（Spec Kit `160`）：**工程图视图 4 个**
    #:   —— ★ sw_drawing_view 的 12 个函数**一个都没挂**。
    "tool_specs_batch43",
    #: ★ 24h 段 6 续（Spec Kit `164`）：**图纸比例的读与写 2 个**
    #:   —— ★ 它补上了一个真空：★★ `IView.ScaleRatio` 读得到、**写不进**（事实 227/294），
    #:   ★ 而 `ISheet.SetScale` **写得进** ⇒ ★ **想改比例就改图纸的比例**。
    "tool_specs_batch44",
    #: ★ 24h 段 6 续（Spec Kit `166`）：**曲面特征（第一条）**
    #:   —— ★ 把「不做曲面族」拆成两半：★ `IModeler.Create*Surface`（造曲面**体**）
    #: **仍然不做**（事实 40）；★★ `FeatureExtruRefSurface3`（建曲面**特征**）**真机通过
    #: **。
    "tool_specs_batch45",
    #: ★ 24h 段 6 续（Spec Kit `167`）：**几何量测**
    #: —— ★ 补「四家有我们没有」的真缺：★ 全仓 grep `measure`/`area`/`distance` **均为 0
    #: **。
    "tool_specs_batch46",
    #: ★ 24h 段 6 续（Spec Kit `168`）：**放样**
    #:   —— ★ 补「四家有我们没有」的真缺：★ 全仓 grep `loft` **工具 0 · 函数 0**。
    "tool_specs_batch47",
    #: ★ 24h 段 6 续（Spec Kit `169`）：**扫描**
    #:   —— ★ 与 `loft` 同批：★ 全仓 grep `sweep` **工具 0 · 函数 0**。
    "tool_specs_batch48",
    #: ★ 24h 段 6 续（Spec Kit `170`）：**参考轴**
    #:   —— ★ 环形阵列的前置（官方 mark 表 `1 = 方向轴`）+ §五 域② 缺口。
    "tool_specs_batch49",
    #: ★ ... ★ 24h 段 6 续（Spec Kit `171`）：**包覆**
    #:   —— ★ 补「四家有我们没有」的真缺：★ 全仓 grep `wrap` **工具 0 · 函数 0**。
    "tool_specs_batch50",
    #: ★ 24h 段 6 续（Spec Kit `172`）：**传感器（读）**
    #:   —— ★ 补「四家有我们没有」的真缺：★ 全仓 grep `sensor` **工具 0 · 函数 0**。
    "tool_specs_batch51",
    #: ★ 24h 段 6 续（Spec Kit `173`）：**文档单位**
    #:   —— ★ 补「四家有我们没有」的**最后一条**真缺。
    "tool_specs_batch52",
    "tool_specs_batch53",  # 轮 397：选择底座（真缺口批量挂柜台·段 1）
    "tool_specs_batch54",  # 轮 398：草图图元（段 2）
    "tool_specs_batch55",  # 轮 399：零件读/自动标注（段 3）
    "tool_specs_batch57",  # 轮 401：孔族（段 4）
    "tool_specs_batch58",  # 轮 402：仿真简单载荷 6 条（段 5）
    "tool_specs_batch59",  # 轮 403：导出（图片 + 钣金展开 DXF）（段 6）
    "tool_specs_batch56",  # 轮 405：恢复 add_dimension（穷举表证实能建）
    "tool_specs_batch60",  # 轮 414：A 组收尾（分布质量 + 力）
    "tool_specs_batch61",  # 轮 425：B 组第一条（刚性连接件）
    "tool_specs_batch62",  # 轮 428：焊件族第一条（结构构件）
    "tool_specs_batch63",  # 轮 452：按声明式选择器选面
    "tool_specs_batch64",  # 轮 459：连接件族第三条（link · 两个顶点）
    "tool_specs_batch65",  # 轮 464：B1 批草图图元（3点矩形/平行四边形/切线弧/3点圆弧/部分椭圆/抛物线/圆锥/周边圆）
    "tool_specs_batch66",  # 轮 465：B3 批草图编辑 6 个（剪裁/延伸/等距/圆角/线性阵列/圆周阵列）
    #: ★ 2026-10-03（轮 472）：B4 批草图编辑·移动族 5 个（移动/旋转/缩放/伸展/镜像）。
    #:   ★ 真机 **5/5**（`output/b4-sketch-modify-evidence.json`）。
    #:   ★★ 判据**按操作分**：改坐标系的（移动/旋转/镜像）看
    #:     `ModelToSketchTransform.ArrayData`；改几何的（缩放/伸展）看草图端点的 bbox。
    "tool_specs_batch67",
    #: ★ 2026-10-03（轮 474）：B6-a 曲面编辑 5 个
    #:   （平面区域 / 等距曲面 / 直纹曲面 / 删除面 / 替换面）。
    #:   ★ 真机 **5/5**（`output/b6a-surface-edit-evidence.json`）。
    "tool_specs_batch68",
    #: ★ 2026-10-03（轮 476）：B6-b 曲面特征——**只登记真机建成的那一条**（放样曲面）。
    #: ★ 旋转曲面前置试了 4 种未成（★ 最后量到 `轴选中数=5`）⇒ 按 A4 不进 `verified`、**
    #: 不登记成工具**。
    "tool_specs_batch69",
    #: ★ 2026-10-03（轮 479）：B8 参考几何体 —— **只登记真机建成的 3 条**
    #:   （质心 / 边界框 / 坐标系）。
    #: ★ 基准面与点**前置未成**（★ 官方要求先按 mark 选参考实体，而 mark 表未给）⇒ 不登
    #: 记。
    "tool_specs_batch70",
    #: ★ 2026-10-03（轮 481）：B7 特征下拉 —— **只登记契约能表达的那一条**（通过参考点的
    #: 曲线）。
    #:   ★ 配合参考实现层**已真机建成**，★ 而它第 2 个形参是 **`IEntity` 对象**，
    #:     `Param` 表达不了 ⇒ 留待接声明式选择器（★ 不假装）。
    "tool_specs_batch71",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 T201/T401：
    #:   把 `docs/user-feature-coverage.md` §八 缺口项里**真有实现**的接成工具 ——
    #: 旋转曲面 · 孔向导 · 完全定义检查（★ 三个都带真机证据：`output/coverage-gap-batch1
    #: -evidence.json`）。
    #:   ⚠ 判据来自 `tools/audit_gap_implementations.py`（**AST**，★ 不用 grep ——
    #:     grep 会把来源块里引用的官方成员名算成「有实现」）。
    "tool_specs_batch72",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 R2：**工程图真缺口
    #: ** 4 个 ——
    #:   断裂视图 · 辅助视图 · 表面粗糙度符号 · 基准符号。
    #:   ★★ 与 batch72 **性质不同**：batch72 接的是「AST 量出**已有实现**」的，
    #: ★ 而这 4 项**本仓一个都没有** ⇒ ★ 先写能力层 `scripts/sw_drawing_create_missing.p
    #: y`，
    #:     ★ 再在这里声明成工具（`module="sw_drawing_create_missing"`、`inject="model"`）。
    #: ★ 第 5 项「气泡序号」**故意不在这里**：它的形参是 `AutoBalloonOptions` **COM 对象
    #: **，
    #:     `Param` 表达不了 ⇒ ★ 能力层已实现、待将来走 `extra_op`。
    #: ★★ **真机前置已逐条写进能力层**（`InsertBreak3` 非废弃那一代 / 辅助视图要**先选一
    #: 条边** /
    #: 粗糙度"位置参数**仅当** leaderType != swNO_LEADER" / 基准符号 `InsertDatumTag2` *
    #: *零参**）。
    "tool_specs_batch73",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 **R1**：**工程图「
    #: 已实现却没挂」的 8 项** ——
    #: 投影视图 · 剖面视图 · 局部视图 · 图纸格式/模板 · 注释/文字 · 孔表 · 修订表 · 中心
    #: 符号线。
    #:   ★★ **本批一行实现逻辑都不新写**（"缝合优先不发明"）—— 依据
    #:     `recon/drawing-existing-coverage.md`：那 13 项里**已实现 8 项、挂出的只有 4 项**
    #:     （且全靠同一个 `solidworks_drawing`）⇒ ★ 本批只做**转接 + 单位边界**。
    #: ★ 转接层 `scripts/sw_drawing_expose.py`：对外收**毫米**（规则 2 的换算**只在那里
    #: 发生一次**），
    #:     并把**前置回读**带回来（事实 496：前置与能力必须分开记）。
    #:   ★★ `inject="drawing_model"` —— 该键已在 `RESOLVERS` 里（事实 491）。
    #: ⚠ 其中「中心符号线」那条走**批量**入口，★ **尚未单独真机验证**（单点入口已实测为
    #: 阴性）。
    "tool_specs_batch75",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 **R3**：**钣金/焊
    #: 件 4 条** ——
    #:   斜接法兰 · 闭合角 · 顶端盖 · 角撑板（焊件）。
    #:   ★★ **本批的三条废弃链查证（队友逐条核官方页）**：
    #:     ① `IModelDoc2.InsertSheetMetalMiterFlange`（**11 参**·回 `void`）**废弃**
    #:        → **`IFeatureManager.InsertSheetMetalMiterFlange`（14 参·回 `Feature`）**
    #:        ⇒ ★ **同名两份、参数个数不同** —— 用错**不只是「没反应」，而是个数对不上**；
    #: ② `InsertEndCapFeature` → `…3`，★ 而 **`InsertEndCapFeature2` 不在链上**（其官方
    #: 页**无 Obsolete 句**）
    #:        ⇒ ★ **不是 1→2→3 线性**；
    #: ③ `InsertGussetFeature` → **`…3`**，★ 而 `…2` 的官方页**无 Obsolete 句** ⇒ ★ **中
    #: 间代状态官方没写**。
    #: ★ 第 5 项「中面」**不在这里**：`insert_mid_surface(model, **body**, **part_doc**,
    #:  …)` 的
    #: 第 2/3 个形参是 **`Body2`/`ModelDoc2` 对象** ⇒ `Param` 表达不了 ⇒ ★ 能力层有、**
    #: 工具层不建**。
    #:   ⚠⚠ **本批的 4 条工具尚未真机验证**（★ 与 batch72/73 一样，★ 注册 ≠ 能跑）——
    #: ★ 待下一轮用工具层 e2e 探针补读数，★ **在那之前不许把它们的 level 写成 verified**
    #: 。
    "tool_specs_batch74",
    #: ★ 2026-10-03（接手轮）· **R6+**：把「**已真机证明、代码却只在 `tools/prove_*.py`
    #: 里**」的直入法挂成工具。
    #: ★ 判据逐字来自 `recon/scan-S2b-ledger-vs-tools.md` 的 **A 表**（台账有、`mcp_tool
    #: s` 无挂 —— 41 条），
    #: ★ 而它的 `limitations` **自己写着**「⚠ 本包装未接进 MCP 工具层」⇒ ★ 挂出来就是**
    #: 台账写明的下一步**。
    #: ★★ **不发明**：`scripts/sw_feature_entry_ops.py` 的调用序**照抄那次建成的真机探针
    #: **。
    #:   本批 1 条：**特征/螺纹**（`InsertCosmeticThread3`，7 参 · 未废弃）。
    #:   ⚠ **尚未经工具层端到端验证**（★ 真机证据目前只在**探针**那一级）——
    #:     ★ 在 e2e 读数出来之前，★ **不许**写成「经工具层已验证」。
    "tool_specs_batch76",
    #: ★★★★★★ 轮 103：★ **补我自己造成的一个缺口** ——
    #:   ★ 任务书阶段 5 逐字「建能力 → **挂 ToolSpec** → 真机验证」⇒
    #:   ★★ 我在轮 95–102 补了 6 个**回读能力**、★ 做了建能力与真机验证、
    #:     ★★★ **却没挂 ToolSpec** ⇒ 真机查（★ `output/_check_readback_toolspecs.py`）：
    #: ★ **6 个全部「没有」** · ★★ **与 `feature_readback` 相关的 ToolSpec 一个都没有**
    #: ✓
    #:   ★★★★ **⇒ 那 6 个能力**只在 Python 层可用、★ MCP 层调不到**** ✓
    #:   ★★★★★ **判据**：★★★ **「建成了能力」与「能力能被调」是两件事** ——
    #:     ★ 前者看**函数存在 + 真机读数**、★ 后者看**ToolSpec 清单里有没有它** ✓
    "tool_specs_batch77",
    #: ★★★★★★ 轮 104：★ **把「安全链」从探针搬进工具层** ——
    #: ★ 业主原话：★「修好，而且要**站在未来别的人使用我们项目的时候也能生效**的角度**根
    #: 因修复**」✓
    #:   ★★ 事实 526/528 把「网格爆内存」与「求解不出结果」修在了**能力层与探针**里，
    #:     ★★ **而工具层（别人真正会调的那一层）拿到的仍是裸的 `create_mesh_report`**：
    #:       · 不设安全档 ⇒ 曲率自适应 + `MinElementSize=0` ⇒ **网格规模不受控**；
    #: · 无求解前内存闸 ⇒ **超预算也照跑**；· 不过忙检 ⇒ **SW 忙时照样下发调用**（卡死路
    #: 径）✓
    #: ⇒ ★ 本批 2 个：`..._create_mesh_safely`（量闸 → 安全档 → 建网格 → 真读数 → 内存闸
    #:  → **还原**）
    #: + `..._solver_type`（★ 让调用方**看得见求解器**，免得把 FFEPlus 的内存换算过度外
    #: 推 —— 事实 529）✓
    "tool_specs_batch78",
    #: ★★★★★★ 轮 105：**规格 204 的批 79 —— FR-008 的两半**（`specs/204-tool-ramp/`）：
    #:   ★ 规格 202 的 FR-008 逐字要求「装配**爆炸视图**与**宏/VBA 执行** MUST 可用」，
    #: ★★ 而实测 `capabilities.yaml` 搜 `Explode`/`RunMacro` = **0 命中** ⇒ 两块**完全空
    #: 白** ✓
    #: · ① **爆炸视图 9 个**：`sw_assembly_doc` 里**新增** 9 个包装（成员名与 arity 取自
    #: 该模块
    #:     机械生成的登记表 → `call_assembly_doc` 会**在调用前**核实参个数）·
    #: · ② **宏 8 个**：新建 `scripts/sw_macro.py`（`ISldWorks.RunMacro2`，★ 官方签名 **
    #: 4 入 + 1 out**）
    #: + `sw_macro_guard` 的 7 个**纯文本**函数（生成/抽取/校验/选模板/落盘；它们此前一
    #: 个都没挂）✓
    #:   ★ 本批 **17 个** ⇒ 工具数 296 → **313**（规格 204 的 SC-001 第一段）✓
    #: ★ 与既有工具**零重叠**（SC-004）：既有 296 个里没有爆炸视图、也没有宏**执行**工具
    #:  ✓
    "tool_specs_batch79",
    #: ★★★★★★ 轮 106：**规格 205 的批 80 —— 自动化诊断知识 + 会话忙闲检测**（12 个）：
    #:   · `sw_automation_knowledge` 6 个（HRESULT 释义 / 命令锁 3 / 首选项开关 2）——
    #: ★ 它们的首参叫 **`sldworks`** ⇒ ★ 本批**新加了一个注入键** `"sldworks": resolve_s
    #: w`
    #:     （★ 与既有的 `"sw"` 键同一手法 —— 事实 169 那张表的设计用途）✓
    #: · `sw_com_traps` 2 个**纯函数**（`deprecated_successor` / `find_real_implementati
    #: ons`）——
    #:     ★ 同一批里另 7 个**明确不做**（弹框的 `send_message` · 重复的 `explain` ·
    #: 无独立价值的 `is_type_mismatch` · 内部管道 `byref_*` · 收可调用的 `adaptive_arity
    #: ` ·
    #: 收字节的 `is_swp_macro` · generator 的 `iter_real_sources`）⇒ ★ 原因逐条写在批次
    #: 文件头 ✓
    #:   · `sw_busy` 4 个（忙闲 / 卡死 / 求解器进程 / 等空闲）—— ★ 本会话新建的模块，
    #:     ★★ 它的判据正是事实 526 的教训（忙碌要**归属家族进程**，否则孤儿窗口假阳性）✓
    #:   ★ 本批 **12 个** ⇒ 工具数 313 → **325** ✓
    #: ★ 选域依据：机械预筛（`output/prescreen-deduped.json`）—— ★ 不再按「候选数」排序
    #: ，
    #:     而按「**去重后可挂数**」排序（★ 这是 v3 批序的由来，见规格 §8.2）✓
    "tool_specs_batch80",
    #: ★★★★★★ 轮 107：**规格 205 的批 81 —— 由 Bunny 扇出产出、经机器门禁过滤**（18 个）
    #: ：
    #: ★ 这是**第一次**用"60 路 Bunny 扇出 → 门禁逐行核 → 转换器生成批次文件"这条路做的
    #: 批次 ✓
    #: · 域：`sw_review`（10）· `sw_feature_readback`（3）· `sw_import_mesh_reference`（
    #: 2）·
    #: `sw_preflight` / `sw_sketch_dimensions` / `sw_misumi` / `sw_automation_knowledge`
    #:  /
    #:     `sw_com_traps`（各 1）✓
    #:   ★★ 门禁挡下的与**主线明确不做**的都不进来：
    #:     · `solidworks_dialog_send_message`（弹模态框）· `solidworks_com_is_type_mismatch`
    #: （无独立价值）—— ★ 由 `tools/build_toolspec_batch_from_rows.py` 生成后**主线再删*
    #: * ✓
    #:   ★ 本批文件**由 `tools/build_toolspec_batch_from_rows.py` 生成**（★ 只收过门禁且
    #: `exposable=True` 的行，并按构造保证规则 2 —— 长度缺 `_mm` 就自动改名 + 补 `param_
    #: alias`）✓
    "tool_specs_batch81",
    #: ★★★★★★ 轮 108：**规格 205 的批 82 —— 第二坡扇出（仿真/装配/导出域）**（13 个）：
    #:   ★ 生成器产出 **19** 个 ⇒ ★ 主线按 **FR-006 语义去重**删掉 **6** 个：
    #: · `export_pdf` / `export_flat_pattern_dxf` / `…_report` —— ★ `export_active` 已含
    #:  PDF、
    #:       `export_dxf` **就是**钣金展开导出（其 doc 逐字这么写）⇒ **真重复** ✓
    #:     · `assembly_add_distance_mate_by_name` —— `add_distance_mate` 已覆盖 ✓
    #:     · ★★ **`simulation_configure_mesh_settings` / `simulation_mesh_safety_apply`** ——
    #: ★ 它们是**未护栏的原始网格旋钮**：★ 事实 526 的 **40 GB 事故**正是**盲设它们**造
    #: 成的；
    #:       批 78 已定「安全入口 = `create_mesh_safely`」（自动设安全档 + 事后还原）
    #:       ⇒ ★ **不单独发旋钮**（D-1 宁缺毋滥）—— ★ 这是**安全**判断，不是数量判断 ✓
    #:   ★ 留下的 13 个覆盖：装配（含 5 种配合/抑制/替换/平行）· 导出 · 外观渲染材质删除 ·
    #:     仿真（加载项 / 研究管理器 / 按类型建研究 / 内存预算 / 网格设置报表 / 校验）✓
    "tool_specs_batch82",
    #: ★★★★★ 轮 109：**规格 205 的批 83 —— 第二坡的「真新」残余**（4 个）：
    #: ★ 第二坡 92 行里，**33 条是"已建过「**（★ 门禁的 ⑧ 分支把」已建「与」真撞名"分开
    #: 之后
    #:   才读得出来）、6 条是主线按 FR-006/安全判掉的 ⇒ ★ **真正新的只有这 4 个** ✓
    #:   · `solidworks_simulation_get_loads_manager` / `get_results` —— ★ 仿真**读数**入口
    #:     （★ 与批 78 的「安全建网格」配套：建完要能读结果）✓
    #:   · `solidworks_simulation_solve_memory_preflight` —— ★ **只读**内存预算前置闸
    #: （★ 与危险旋钮不同：**它只算不设**，故单独发它是安全的 —— 对比批 82 删掉的那两个
    #: ）✓
    #:   · `solidworks_simulation_get_edge_weld_connector` —— 边焊缝连接件读数 ✓
    "tool_specs_batch83",
    #: ★★★★★ 轮 110：**规格 205 的批 84 —— 第三坡（残余 40 模块）产出**（7 个）：
    #: ★ 第三坡是**薄模块**（`sw_part` / `sw_hole_features` / `sw_costing` / `sw_sketch`
    #:  /
    #:     `sw_surface_features` / `sw_weldment` / `sw_ref_geometry` / `sw_gui_*` …）——
    #:     ★★ 实测**可暴露率偏低**（45 行里只有 9 行 exposable）⇒ ★ 真正新的 7 个 ✓
    #: · ★ 真建模能力：`solidworks_revolve_cut`（旋转切除）· `solidworks_surface_cut`（
    #: 曲面切除）·
    #:     `solidworks_ref_geometry_create_3d_bounding_box`（3D 边界框）·
    #:     `solidworks_sketch_select_segment`（按序号选草图段 —— ★ 声明式，不收坐标）✓
    #: · 诊断/取证：`solidworks_gui_get_foreground_window` · `solidworks_gui_screen_png`
    #:  ·
    #:     `solidworks_weldment_iter_features`（焊件特征树遍历）✓
    "tool_specs_batch84",
    #: ★★★★★ 轮 111：**规格 205 的批 85 —— 两条"真能力"**（2 个）：
    #:   · `solidworks_drawing_create_three_standard_views` —— ★ **三视图布局**
    #: （★ 这一条有历史：`capabilities.yaml` 曾把它记成 `blocked / DRAWING_PROJECTION_AP
    #: I_UNAVAILABLE`，
    #: 而 2026-10-04 查明真因是**成员名拼错** —— 官方真名 `Create1stAngleViews2`（`1st`
    #: 非 `First`）
    #:     ⇒ 已在 `drawing_workflow.py` 修正；★ 本工具挂的是**修好之后**的入口）✓
    #: · `solidworks_costing_defaults` —— Costing 默认值读数（★ Costing 是本仓三个**护城
    #: 河域**之一）✓
    "tool_specs_batch85",
    #: ★★★★★★ 轮 112：**规格 205 的批 86 —— 第四坡（解锁 C 类！）产出 30 个**：
    #: ★★ 这一批是「**加解析器换工具**」这条路走通的证明：★ 给我 `view`/`results`/`mesh`
    #: /`options`
    #: 四个**语义无歧义**的解析器之后，同一坡扇出的 **38 行里 30 行可暴露、门禁 37/37 全
    #: 过**
    #:     （★ 对比第三坡「薄模块」：45 行只 9 行可暴露）✓
    #: · `sw_view` **23 个** —— 视图族（激活 / 重画 / 着色初始化 / 取帧 / 显示模式 / 比
    #: 例 /
    #:     缩放平移旋转 / 相机 / 透视 / 动态 / 收集视图证据…）★ 全走**活动视图**注入键 ✓
    #: · `sw_simulation_results` **6 个** —— 网格证据 / 屈曲载荷因子 / 最差雅可比比 / 单
    #: 元失败判定 /
    #:     激活与删除图（★ 走 `results`/`mesh` 键）✓
    #: · `sw_simulation_study_options` **1 个** —— 按注册名设研究选项（★ 走 `options` 键
    #: ）✓
    #:   ★★ 计数：369 → **399**（★ **差 1 个**到 SC-001 的 400 ⇒ 第五坡/余量里补）✓
    "tool_specs_batch86",
    #: ★★★★★★★ 轮 113：**规格 205 的批 87 —— 跨过 SC-001 的 400！**（2 个）：
    #:   ★ 第六坡（`sketch`/`selection` 两组 C 类，29 路）头 8 份里只有 **2 行真新** ——
    #:     ★★ 其余 12 行 Bunny 判「不做」且**理由都成立**（★ 我逐条复核过、**不推翻**）：
    #:       · `sketch_get_lines` / `get_arcs` / `get_polylines` / `get_splines` /
    #:         `contour_edges` / `contours` / `set_automatic_solve` —— **既有工具已做同一件事**
    #:         （`solidworks_sketch_count_*`），★ 且 `tool_specs_batch2.py` 的分类表里
    #:         早把它们列进 **`D_不该暴露`**（★ 仓库自己的既有裁决）✓
    #:       · `selection_get_component` —— ★ 官方**逐字标 Obsolete**（铁律 4）✓
    #:       · `selection_get_view` —— 返回值是 **COM 对象**，过不了 MCP 的 JSON 边界 ✓
    #: · `sketch_set_model_to_sketch_transform` —— ★ 官方页逐字写该属性**只读**（get-onl
    #: y）✓
    #:       · `selection_point_*` —— 与既有 `solidworks_selection_point` **重复**（FR-006）✓
    #:   · 本批 2 个：`solidworks_selection_clear_colors`（清选择集颜色）·
    #: `solidworks_costing_set_default_template`（设 Costing 默认模板 —— ★ 护城河域之一
    #: ）✓
    #:   ★★ 计数：399 → **401** ⇒ ★ **SC-001（≥400）达成** ✓
    "tool_specs_batch87",
    #: ★★★★★★ 轮 114：**规格 205 的批 88 —— 第六坡（`sketch`/`selection` 两组 C 类）产出
    #: **（17 个）：
    #:   ★ 第六坡 29 路（24 路回、48 行、17 行判可暴露）⇒ ★ **真新 17 个** ✓
    #: · `sw_selection` **8** —— 选择族：挂起选择清单 / 设对象 mark / 开关选择 / 开关轮
    #: 廓选择 /
    #: 坐标系列元素判定 / 是否在编辑目标内 / 收集选择证据 / 取消选择（★ 走 `selection`
    #: 注入键）✓
    #: · `sw_costing` **3** —— 设默认批量 / 默认材料 / 默认制造方法（★ **护城河域** + `d
    #: efaults` 键）✓
    #:   · `sw_sketch` **2** —— 关系管理器 / 模型到草图变换（★ 走 `sketch` 键）✓
    #:   · `sw_assembly` **3** + `sw_assembly_doc` **1** —— 取组件特征 / 取特征实体 /
    #:     施加组件变换 / 外部参考计数 ✓
    #: ⚠ ★ **留给复核的一点**：`get_component_feature` / `get_component_feature_entity`
    #: 与
    #: `get_relation_manager` / `get_model_to_sketch_transform` 的**返回可能是 COM 对象*
    #: *
    #:     （★ 那样过不了 MCP 的 JSON 边界）—— ★ 本门禁**静态查不到这一条**（它只看入参），
    #: 故**如实标注**：真机调用时若报序列化错，应改为「报告式」包装（★ 与既有 `*_report`
    #:  手法一致）✓
    #:   ★★ 计数：401 → **418** ✓
    "tool_specs_batch88",
    #: ★★★★★ 轮 115：**规格 205 的批 89 —— C 类最后两组语义无歧义的解锁**（5 个）：
    #:   ★ 走「**加解析器换工具**」那条路：同笔加两个注入键
    #:     `"cost_part"`（Costing 的成本模型对象）· `"motion_study"`（运动算例，按名字取、
    #:     **只在算例数 == 1 时才给**、0 或 >1 都响亮报错 ⇒ 不猜）✓
    #:   · Costing **写侧 3 个** —— 纳入实体 / 设成本方法 / 全部实体重算
    #: （★ 官方依据：`C:\swapi\types` **无这三页** ⇒ 真源如实标为**本仓** `scripts/sw_co
    #: sting.py`，
    #:      其来源块写明依据是「反射确认的实参个数」）✓
    #:   · 运动算例 **2 个** —— 计算(可选播放) · ★★ **导出 AVI**（★ **护城河域**之一，
    #: 官方页逐字 `IMotionStudy\SaveToAVI.md` ⇒ `System.bool SaveToAVI( System.string Fi
    #: leName,
    #:     AVIParameter Parameter )`）✓
    #:   ★★ 本批**不做**的（FR-006/D-5，逐条写在批次文件头）：Costing 那 5 个只读候选
    #: **各自的 `*_report` 包装已挂成工具**；motion 的 `add_constant_speed_rotary_motor*
    #: `
    #:     被**上游遗留工具** `solidworks_add_rotary_motor` 覆盖 ✓
    #:   ★ 计数：414 → **419**
    "tool_specs_batch89",
    #: ★★★★★ 轮 116：**规格 205 的批 90 —— Costing 写侧收尾**（3 个）：
    #:   ★ 选域依据是 **SC-009 要求的预筛**（C 类普查）：未覆盖候选 281 个里
    #: **97 个属「取哪一个」的歧义组**（一律不碰）；`cost_analysis`(3)+`cost_body`(2) 可
    #: 加键
    #:     ⇒ ★ **组内真新 3 个** ⇒ 达 SC-009 的门槛 ⇒ 开工 ✓
    #:   · `solidworks_costing_set_lot_size`（批量）· `set_markup`（加价类型+百分比）·
    #:     `assign_custom_cost`（给一个成本实体指定自定义成本）✓
    #:   ★ 同笔加两个注入键 `"cost_analysis"`（`cost_part`→`GetCostAnalysis`）·
    #:     `"cost_body"`（按 `body_name` 找；**没传名时只在清单长度 == 1** 才给、否则报错）✓
    #:   ★★ 本批**不做**：`read_cost_analysis` / `read_cost_body` —— ★ 早已挂成
    #: `solidworks_costing_read_analysis` / `…_read_body`（只读侧一早就建好了）⇒ 只取写
    #: 侧 ✓
    #:   ★ 计数：419 → **422**
    "tool_specs_batch90",
    #: ★★★★★ 轮 117：**规格 205 的批 91 —— 弹窗护栏 / 焦点 / 倒角几何 / 曲面运行时**（11
    #:  个）：
    #:   ★★ 本批的选域依据是**漏斗勘探**（`tools/bunny_toolspec_pipeline.py survey`）——
    #:     我把未覆盖候选按「**参数是否全是显式标量**」筛过 ⇒ 只剩 **25 个**，再剔掉
    #: 基础设施/内部件（`sw_connect` / `sw_isolate` / `sw_sensor` 出参工厂 …）⇒ ★ 本批 1
    #: 1 个 ✓
    #:   · ★★ **`sw_gui_modal` 4 个 —— 弹窗护栏本体**（`find_modals` / `modal_report` /
    #:     `assert_no_modal` / `close_modals`）：★ 弹窗把 COM 调用**冻住**是本仓的头号死因
    #:     ⇒ ★ 让 agent 能**查 / 判 / 关**弹窗，正是事实 527 那套常驻监控的工具化 ✓
    #:   · `sw_chamfer_geometry` 3 个 —— ★ **纯计算**（倒角切掉的体积 + 断言报表）✓
    #: · `sw_gui_focus` 3 个 —— 焦点断言/修复（与既有 `gui_get_foreground_window` 同族不
    #: 同面）✓
    #: · `sw_surface.runtime_available` —— ★ **只读**前置检查（事实 40 那张实测表的读侧
    #: ）✓
    #: ★ 全部 `inject=""`（首参是标量或**窗口句柄** —— ★ 句柄不是几何坐标 ⇒ **不违反规则
    #:  3**）✓
    #:   ★★ 本批**不做**：`sw_capture.capture`（返回 PIL Image，过不了 JSON 边界）·
    #: `sw_sensor.out_*`（COM 出参工厂）· `sw_isolate`/`sw_simulation_worker`（基础设施
    #: ，FR-007）✓
    #:   ★ 计数：422 → **433**
    "tool_specs_batch91",
    #: ★★★★★ 2026-10-06：**规格 209 的批 92 —— B1 批**（5 个）：★ 来源是**规格 207 的 18
    #:  条采纳候选**
    #:   （`docs/recon-207/adjudication.md` 的 **B1 批**）—— 本批取其中最干净的 4 件活：
    #: · **idx 235 + 236 重建** ⇒ ★ 裁决书强制「**合并成一条工具**（三档 mode），**不建
    #: 两条**」✓
    #:   · **idx 79 构造几何** ⇒ ★ 落 `sw_sketch_edit_ops`，**复用**已有的声明式选段包装 ✓
    #: · **idx 97 显示状态** ⇒ 读 + 激活两条（★ 读侧落 `sw_render_material` —— 事实 286
    #: 已真机 PASS）✓
    #: · **idx 244 引用文档** ⇒ ★ 补 `solidworks_pack_and_go` 一直枚举却不暴露的**读侧**
    #:  ✓
    #:   ★★ 三条**官方逐字**被当成硬约束写进实现（不是我们自己的口径）：
    #: ① `EditRebuild3` 是**方法**（三家外部项目当属性读 ⇒ bound method ⇒ **判据恒真**）
    #: ；
    #: ② `GetDisplayStates` 的「first name = active」**只在没有多个显示状态同时活动时**
    #: 成立
    #:        ⇒ 装配里必须给 `ambiguous`；
    #: ③ `GetDocumentDependencies2`「**Library features 不会返回**」⇒ 盲区要**随返回值**
    #: 带出去。
    #: ★ 计数：433 → **439**（★ 后补 idx 209 `move_body` —— 裁决书称它是「本批最干净的一
    #: 条」）
    "tool_specs_batch92",
    #: ★★★ 2026-10-06：**规格 209 的批 93 —— 钣金展开 / 折叠 / 折边**（3 个）：
    #:   ★ 来源是**规格 207 的 18 条采纳候选**的 **B2-1（idx 336 unfold）** ·
    #:     **B4-4（idx 155 fold）** · **B4-2（idx 173 hem）** ⇒ 三条都落**已有模块**
    #:     `scripts/sw_sheet_metal.py`（铁律 3）✓
    #:   ★★ **诚实边界（别读成「三个都成了」）**：
    #:     · `create_unfold` / `create_fold` —— ★ **真机建成了**（`展开1` / `折叠1`，
    #:       marks 逐条 **`[1, 4]`**、特征树各 +1）✓
    #:     · `create_hem` —— ★★ **真机五种形态全部回 `None`** ⇒ 能力标 `stitched`；
    #: ★ 工具**仍然挂出来**（与既有 4 个失败入口同策：★ 由 `require_verified` 在**调用前
    #: **
    #:       抛**带原因**的错误，而不是让用户吃一个裸 COM 错误）✓
    #:   ★ 计数：439 → **442**
    "tool_specs_batch93",
    #: ★★★ 2026-10-06：**规格 209 的批 94 —— 隐藏/显示选中的草图**（1 个）：
    #: ★ 来源 idx **175 `blank_sketch`**（★★ 裁决书：官方 `BlankSketch` 逐字是「Hides th
    #: e
    #:     **selected** sketches」⇒ **官方没有「全部」这个语义** ⇒ ★ 工具名**不许叫
    #:     `hide_all_sketches`**）⇒ ★ 本批叫 **`solidworks_sketch_set_blanked`**、
    #:     收**声明式选择器**、★ 并且**不新开「全隐藏」那条官方没有的路** ✓
    #:   ★★ 判据：① 选区计数 ② **`IFeature::Visible` 的前后读数**（`swVisibilityState_e`）
    #: —— ★ 官方示例里**只有肉眼**；★ 本批把那个**回读入口**定出来（裁决书点名的真风险）
    #: ✓
    #:   ★ 计数：442 → **443**
    "tool_specs_batch94",
    #: ★★★ 2026-10-06：**规格 209 的批 95 —— 相交特征**（1 个）：★ 来源 idx **181 `inter
    #: sect`**。
    #:   ★ 官方**两步**：`IFeatureManager::PreIntersect2` → `PostIntersect`（★ 不是一步）✓
    #:   ★★ 裁决书点名「**唯一要实测的只有 `System.object` 布尔 SafeArray 的包装**」——
    #:     ★ **已验**：包 `VARIANT(VT_ARRAY | VT_BOOL)`，★ 真机**双向成立**
    #:     （不排除 ⇒ 建出 `相交1`；**排除唯一的体** ⇒ `PostIntersect` 回 `None`、
    #:      特征没建出来 ⇒ ★★ 说明那个 `True` **真被 SW 读走了**）✓
    #: ★ 落点 `scripts/sw_boolean_ops.py`（**新建** —— 本仓既有零件特征模块里没有多体/布
    #: 尔这一族）
    #:   ★ 计数：443 → **444**
    "tool_specs_batch95",
    #: ★★★ 2026-10-06：**规格 209 的批 96 —— 把模型标注插进工程图视图**（1 个）：
    #: ★ 来源 idx **205 `model_annotations`**（官方 `IDrawingDoc::InsertModelAnnotations
    #: 4`，**8 参**）✓
    #:   ★★ **诚实边界：本条只验到"可达 + 回读可用"** —— ★ 真机**没能产出非空插入**，
    #:     原因已查明：我们的零件是**纯坐标画出来的**（**一个尺寸都没有**），
    #:     而本仓的尺寸助手需要**先选中实体**才建得出尺寸 ⇒ ★ **夹具里没有可插的东西**。
    #:     ★ 这是**数据相关**的失败、**不是**后端到不了 ⇒ 能力标 **`stitched`**、
    #:     ★ 且**不设**硬闸（硬闸会误杀）✓
    #: ★★ **落点偏离裁决书建议**：它说 `scripts/sw_drawing.py` —— ★ 而那是 **29 行的桥接
    #: 壳**
    #:     （`exec_module` 加载 subskill 再 `globals().update`）⇒ 往里加会被覆盖；
    #: ★ 落 `sw_drawing_create_missing.py`（★ 裁决书自己要求"复用该文件已有的读侧助手"）
    #: ✓
    #:   ★ 计数：444 → **445**
    "tool_specs_batch96",
    #: ★★★ 2026-10-06：**规格 209 的批 97 —— BOM 气泡**（1 个）：★ 来源 idx **34 `balloo
    #: n`**。
    #:   ★★ 裁决书点名要"真机定案"（两家外部项目结论互相矛盾）⇒ ★ **已定案**：
    #: 装配工程图上**有没有 BOM 表都插得进去**（各 Δ=1）⇒ ★ Slacker-LLC 的「静默无效」不
    #: 成立、
    #: ★ Eduardof0nt 的 `bool(result)` 也不能当判据 ⇒ ★★ **判据只能是 `GetNoteCount` 的
    #: 增量** ✓
    #:   ★ 本批同时**收紧了原函数的 `ok`**（它原先依赖返回数组、且 `delta >= 0` 太松）✓
    #:   ★★ 原函数自述"不建 ToolSpec"的理由**已过期**：那句说的是**底层成员**的
    #:     `AutoBalloonOptions` COM 形参；★ 而**包装函数的形参全是标量** ⇒ ★ 能挂 ✓
    #:   ★ 计数：445 → **446**
    "tool_specs_batch97",
    #: ★★★ 2026-10-06：**规格 209 的批 98 —— 工程图中心线**（1 个）：★ 来源 idx **52 `ce
    #: nterline`**。
    #:   ★★ 裁决书要求「须真机定案」（两家外部项目结论矛盾）⇒ ★ **已定案**：
    #:     圆柱零件的工程图视图里 `edge=1 · face=1` 可见、`Select4` 选中后**选区回读 1**，
    #: 而 `InsertCenterLine2` **回 `None`**、`GetCenterLineCount` **Δ=0** ⇒ ★ **选中了也
    #: 没产出** ✓
    #:     ⇒ ★ **两家各对一半**：说"静默无效"的**不准确**（它并不静默，返回 None）；
    #:       说 `bool(result)` 的**恰好对**，但★ **不能通用**（只有回读抓得住几何没变的情形）✓
    #:   ★★ **裁决书建议"与 idx 30 合并成一条工具两模式"—— 未照做**（入参形状不同：
    #: `auto_center_marks` 收结构化 requirements 列表 ⇒ `Param` 表达不了）⇒ ★ 偏离已记 t
    #: asks.md ✓
    #:   ★ 计数：446 → **447**
    "tool_specs_batch98",
    #: ★★★ 2026-10-06：**规格 209 的批 99 —— 原生宏录制**（1 个）：★ 来源 idx **211
    #:   `native_macro_recording`**（`ISldWorks::RecordLine` + `RunCommand`）。
    #:   ★★★ **裁决书点名的头号风险已绕开**：`swCommands_StopMacro`(31) 官方枚举页**逐字**
    #:     标注「**opens the Save As dialog**」⇒ ★ 本模块**永不调 31**，
    #:     改用 `swCommands_RecordPauseMacro`(29) 这个**切换**成对开关录制 ✓
    #: ★★★ **真机硬证据（也是标 `stitched` 的理由）**：官方 Remarks 说"只有录制开着才写
    #: 得进去"，
    #: 而★ **真机"未开录制"时 `RecordLine` 也回 `True`** ⇒ ★★ **那个 bool 证明不了任何事
    #: **；
    #: ★ 要真证得**落盘的宏文件**，那要 31 的 Save As ⇒ ★ 本条只到「成对调用可达」这一级
    #:  ✓
    #:   ★ 计数：447 → **448**
    "tool_specs_batch99",
    #: ★★ 规格 213 · B1 —— A 类 6 项「**实现已有、只差 ToolSpec**」✓
    #:   ★ 起因：★★ `docs/user-feature-coverage.md` 只量三列里的**第一列「有入口」**，
    #:     而它的来源是 `all_specs()` 的**工具名集合** ✓
    #:     ⇒ ★★★ 规格 211 做成 `verified` 的能力**没有任何 ToolSpec 引用它们** ✗
    #:       ⇒ ★★ 从「用户可发现、可调用」口径看它们**等于不存在** ✓
    #: ★ 六项：`section_properties` · `scale_feature` · `untrim_surface` · `sweep_surfac
    #: e` ·
    #:     `weldment_trim` · `flat_pattern_dxf` ✓
    #: ★★ **本批被门禁教了一次**：★ `scale_feature` 的入参原名 `x`/`y`/`z` **被规则 3 拦
    #: 下** ✗
    #:     （逐字：「入参 `x` 是**裸坐标** —— 必须改用具名实体 + 声明式 selection」）✓ ——
    #: ★ 而它们其实是**无量纲缩放比例** ⇒ ★ 改名 `*_factor` + ★ `param_alias` 映射回形参
    #:  ✓
    #:   ★ 计数：448 → **454**
    "tool_specs_batch100",
    #: ★★ 规格 213 · B3（前半）—— B 类 5 项里的 **`weld_symbol`** 与 **`forming_tool`**
    #: ✓
    #:   ★ B 类的两步：★ **B2 先把探针里已证实的调用序缝进模块**（已完成 ✓）·
    #:     本批 **把模块函数挂成 ToolSpec** ✓
    #:   ★★ 两项各自的价值（★ 都值得单独记）：
    #:     · `weld_symbol` —— ★★ **「真入口是另一条 API」的实证**：★ 原先走
    #:       `IDrawingDoc::InsertWeldSymbol`（10 参、**静默无效、12 组 0→0**）✗；
    #:       ★ 官方示例走 **`IModelDoc2::InsertWeldSymbol3()`（零参）** ✓
    #:     · `forming_tool` —— ★ 官方 `## Remarks` 逐字要求**先选一个面** ✗，
    #:       ★ 没选时回 `None`、★ **与「建不出来」长得一样** ✓
    #:   ★ 计数：454 → **456**
    "tool_specs_batch101",
    #: ★★ 规格 213 · B3（后半）—— B 类余下三项 ✓
    #:   · `explode_line_sketch`（★ 真机建成 ⇒ `verified` ✓）
    #:   · `speedpak`（★ 真机建成 ⇒ `verified` ✓）
    #: · ★★ `curve_driven_pattern`（★ **官方页第一行就是 `Obsolete`** ✗ 且真机两档有效读
    #: 数皆不建
    #:     ⇒ ★ **只到 `stitched`** ✓ —— ★ A7：★ 不许把 `stitched` 写成 `verified` ✓）
    #:   ★ 计数：456 → **459**
    "tool_specs_batch102",
    #: ★ 规格 217 · B1（前半）—— 「已实现但没暴露」的 5 个草图读数/关系/相交曲线 ✓
    #: · `count_sketch_relations` / `delete_all_sketch_relations` / `delete_sketch_relat
    #: ion`
    #:   · `sketch_by_name` / `sketch_intersect_curves`
    #: ★★ **只增加暴露面** —— ★ **不动台账任何 `level`**（挂柜台：暴露成功/可运行/返回语
    #: 义已验证是三件事；
    #:      ★★ 规格 204 的 P4–P6 曾把 339 暴露面缺口误当真实能力缺口而整阶段作废）✓
    #:   ★ 计数：459 → **464**
    "tool_specs_batch103",
    #: ★ 规格 217 · B3+B4 —— 工程图全图视图清单 + 质量属性/截面/筋参数三个读侧 ✓
    #:   · `list_drawing_views_report` / `mass_property_object` /
    #:     `section_area_crosscheck` / `rib_params`
    #:   ★★ **只增加暴露面** —— ★ **不动台账任何 `level`** ✓
    #:   ★ 四个都是**读侧**（★ 不需要预选 ⇒ 不触发预选族门禁）✓
    #:   ★ 计数：463 → **467**
    "tool_specs_batch104",
    #: ★ 规格 217 · B5/B6 —— 钣金特征遍历 + topology 约束读侧（2 个纯读）✓
    #:   · `sheet_metal_iter_features` / `topology_constraints_report`
    #:   ★★ **只增加暴露面** —— ★ **不动台账任何 `level`** ✓
    #:   ★ 两个都**无选区信号**（★ 第 7 轮定的预检闸已过）⇒ 可作纯暴露 ✓
    #:   ★ 计数：467 → **469**
    "tool_specs_batch105",
    #: ★ 规格 217 · B5 收尾 —— 最后 3 个纯暴露（特征阵列读数 / 配合参考 / 装配特征树遍历
    #: ）✓
    #:   · `linear_pattern_report` / `insert_mate_reference` / `iter_feature_tree`
    #:   ★★ **只增加暴露面** —— ★ **不动台账任何 `level`** ✓
    #:   ★ 三个都**无选区信号**（第 7 轮的预检闸）⇒ 可作纯暴露 ✓
    #:   ★ 计数：469 → **472**
    "tool_specs_batch106",
    #: ★ 规格 219 · 边界凸台 + 边界曲面（官方 InsertNetBlend，Type 区分）✓
    #:   ★★ 等级如实 stitched —— 两个都尚未真机验证（红线⑥）
    "tool_specs_batch107",
    #: ★ 规格 220 · 目标 145/145 —— 装配序列/说明书（★ **直接指向已有的真函数**
    #:   `sw_delivery.collect_assembly_bom`，★ 它的首参就叫 `model` ⇒ 门禁天然满足 ✓）
    #:   ★★ 坐标：★ 官方**没有**「装配序列」成员（只有**序号**类成员 = BOM 行号）⇒
    #:      ★ 本工具给的是**用户心智里的装配说明书**（件表 + 行序），★ 不冒充 ✓
    #:   ★★ 等级如实：★ 尚未真机验证 ⇒ **不提 level**（红线⑥）
    "tool_specs_batch109",
    #: ★ 规格 220 · 目标 145/145 —— 装配/零部件阵列（★ **直接指向已有的真函数**
    #:   `sw_assembly.iter_feature_tree`，★ 它的首参就叫 `model` ⇒ 门禁天然满足 ✓）
    #:   ★★ 如实标注：★ 回的是**整棵装配特征树**的节点清单（★ **含**零部件阵列节点 ✓），
    #:      ★ **不是**"只挑阵列"的专项读数 ✗（★ 官方的 GetPatternComponentCount 是另一条路）
    #:   ★★ 等级如实：★ 尚未真机验证 ⇒ **不提 level**（红线⑥）
    "tool_specs_batch110",
    #: ★ 规格 220 · 目标 145/145 —— 装配/装配体性能分析（★ **换路径**：直接用现成的真函
    #: 数
    #:   `sw_assembly.collect_mate_feature_summary`，★ 首参就叫 `model` ⇒ 门禁天然满足 ✓）
    #:   ★★ 如实标注：★ 官方**搜不到**同名接口 ✗ ⇒ 本工具给的是**真实可核对的计数/摘要**
    #: （★ SolidWorks 自己的 Performance Evaluation 报的正是这类计数 ✓），★ 不冒充官方 A
    #: PI ✓
    #:   ★★ 等级如实：★ 尚未真机验证 ⇒ **不提 level**（红线⑥）
    "tool_specs_batch111",
    #: ★ 规格 220（续）· 目标 145/145 —— 焊件/圆角焊缝（★ **从零真做**：scripts/sw_weld_
    #: bead.py ✓）
    #: ★★ 入口：★ 官方 `InsertFilletBeadFeature2` ✓（★ v1 官方逐字 **Obsolete** ⇒ 只用 v
    #: 2 ✓）
    #: ★★ 前置：★ **预先选中的实体（边）** ✓ —— ★ 官方第 12 行逐字 `pre-selected part bo
    #: dies`
    #:      ⇒ ★ 选边走 `IEntity.Select4`（★ 事实 32）· ★ 且**由函数自己选**（★ 事实 503）✓
    #:   ★★ 判据：★ **特征树回读增量 ≥ 1**（★ 事实 8；★ 返回值 `None` **不代表失败** ✓）
    #:   ★★ 等级如实：★ 尚未真机验证 ⇒ **不提 level**（红线⑥）
    "tool_specs_batch112",
    #: ★ 规格 220 · 目标 145/145 —— PDM 相邻证据读侧（★ 真实现已在 sw_pdm.collect_pdm_ev
    #: idence）✓
    #:   ★★ 等级如实：★ 尚未真机验证 ⇒ **不提 level**（红线⑥）
    "tool_specs_batch108",
    #: ★★ EC00 **T017**（`specs/302-ec00-trustworthy-tool-base/`）—— 草图关系**正式注册*
    #: *。
    #: ★★★ **实测缺口**（2026-10-10）：`scripts/sw_sketch_relations.py` **有实现但 0 个
    #: ToolSpec**
    #:     ⇒ ★ 它**不可被 MCP 调用**（★ 从「用户可发现、可调用」口径看**等于不存在**）。
    #: ★★ 官方依据已逐字核：`AddRelation( object Entities, int RelationType )`（**2 参**
    #: ）+
    #: `## Remarks`「A sketch must be active …」+ `ISketchSegment::GetRelationsCount`（★
    #:  回读判据）。
    #: ★★★ 等级如实：★ 实现由 `tests/test_sw_sketch_relations_safety.py`（**12 例**）在*
    #: *假宿主**上验过
    #: ⇒ ★ **offline**；★★ **真机未在本特性内验证** ⇒ `runtime` = **`not_run`**（红线⑥ ·
    #:  不升级）。
    "tool_specs_batch113",
    #: ★★★ **批 114 —— 弹窗三级分级器上工具面**（★ 业主 2026-10-10 点破的那一件）。
    #:   ★★ 业主原话：「★ **把这个检测的，也注册成一个MCP工具什么的，加入你的工具列表，
    #:     不然每次都不知道主动用**」✓
    #:   ★★★ **实测缺口**：★ 工具面**已有 9 个** `solidworks_gui_*`，★ **但没有任何一个**
    #:     暴露 `classify_dialog` —— ★ 而它才是那套机制的**大脑**（★ 判「能不能自动点」）。
    #:   ★★ **后果（★ 我自己的实例）**：★ 本会话 EC09 我只用了 `--scan`/`--clear`
    #:     ⇒ ★ 看到弹窗却**没读分级理由** ⇒ ★★ 把「求解**失败**（未定义载荷）」
    #:     误读成「求解**很慢**」⇒ ★ **把根因判错了** ✗
    #:   ★ 只做注册（★ 不改 `tools/sw_guard.py` —— ★ 三级分级已由
    #:     `tests/test_sw_guard_dialog_tiers.py` 验过）；★ **纯离线**（`inject=""`）。
    "tool_specs_batch114",
    #: ★★ 规格 329（Q6 L110 逐字）：「**必须同时改 MCP 暴露面**：自主模式的
    #:   `tools/list` **只返回规划入口与必要查询工具**」。
    #:   ★ 实测（2026-10-12）：规格 323 的检索层**有名字、没注册**
    #:     ⇒ ★ **agent 够不到检索层**（★ 判断层 MCP 工具面 0/521）。
    #:   ⇒ ★ 这一批把 `cadstudio_catalog_{domains,retrieve,contract,exposure}`
    #:     **真的接出去**（★ 四个都是**只读、纯 Python、不碰 COM**）。
    "tool_specs_batch115",
    #: ★★ 2026-10-18（业主指令「只做对目标有利的事」）：把 **21 条 verified-零工具**
    #: 的能力接出来（本批之前 140 条能力里 56 条零工具、其中 37 条 verified 却拿不出来用
    #: ）。
    #: ★ 本批**不新增任何 verified 声称** —— 工具只是暴露，不改 capabilities.yaml 的 lev
    #: el。
    #:   ★ 另有 1 条（sw_sketch.get_sketch_slots）**未接**：其首参叫 sketch，而 RESOLVERS
    #:     没有该键，挂上去会在运行期 TypeError（详见 batch116 文件内注释）。
    "tool_specs_batch116",
)


def all_specs() -> list:
    """汇总全部批次的声明（**逐批导入**，缺一个模块就响亮报错）。"""
    specs: list = []
    for mod_name in BATCH_MODULES:
        mod = __import__(mod_name)
        #: ⚠ 实测（2026-10-12，规格 329）：原名从模块名派生
        #:   （`rsplit("batch", 1)[1].upper()`）⇒ ★ **不含 `batch` 的模块名
        #:   直接 `IndexError`** ✗ —— ★ 而"派生失败"看起来像"模块坏了"。
        #:   ⇒ ★ 判据：**先试派生、失败就退回扫描 `SPECS_*`**（★ 那条兜底本来就在）。
        derived = None
        if "batch" in mod_name:
            derived = getattr(
                mod, "SPECS_%s" % mod_name.rsplit("batch", 1)[1].upper(), None
            )
        batch = derived or next(
            (getattr(mod, n) for n in dir(mod) if n.startswith("SPECS_")), None
        )
        if batch is None:
            raise RuntimeError("模块 %s 里找不到任何 SPECS_* 列表" % mod_name)
        specs.extend(batch)
    return specs


def register_capabilities(mcp, base, response_enum, run_locked) -> list[str]:
    """把全部批次注册进 `mcp`，返回注册成功的工具名列表。

    ⚠ **全有或全无**：任一声明过不了门禁 ⇒ `register()` 抛错、**一个都不注册**。
    （由 `tool_registry.register` 保证；这里只是把它接上。）
    """
    specs = all_specs()
    return register(mcp, specs, base, response_enum, run_locked, resolvers=RESOLVERS)
