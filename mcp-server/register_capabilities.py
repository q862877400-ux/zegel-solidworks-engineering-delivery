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
    #: ★★★★★ 2026-10-01（轮 346）**修一处一行之差** —— 真因（挖 `simulation_solver_options` 时发现）：
    #:   `iter_studies(sw_app)` 是 **`yield index, study`**（★ **二元组**），
    #:   而原先写的是 `next(iter(iter_studies(sw)), None)` —— ★★ **没有解包** ⇒
    #:   把 `(0, <study>)` **元组**当成 study 传下去 ⇒ 下游 `study.StaticStudyOptions` 报
    #:   `取 options 失败（family=ICWStaticStudyOptions）：SldWorks.Application.StaticStudyOptions`
    #:   （★ 那个对象名是**元组外面**的东西，★ 所以错误信息**看不出是元组问题**）。
    #:   ★★ 而这条**正好是"空名"那条路** ⇒ ★ **凡是没声明 `study_name` 的工具全部中招**
    #:     （★ 那 5 个求解器配置工具就没声明）⇒ ★ 那是一整片工具**一直没跑通**的原因。
    #:   ⇒ ★ 修法：★ **取出来再解包**（★ 并用 `(None, None)` 兜底，★ 不与"None 当元组"混淆）。
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
    ⚠ 取不到时**抛错**（★ 不静默返回 None —— 否则会挂成一个"永远失败"的工具）。
    """
    from scripts.sw_simulation import _loads_and_restraints_manager

    return _loads_and_restraints_manager(resolve_study(params))


#: ★★ 2026-10-03（接手轮）· **修一批「注入键 ≠ 函数首参名」的工具（共 11 条）** ——
#:   ★ 规范（本表的设计意图，逐字见下面 `manager` 那条注释）是：**`inject` 必须等于目标函数的首参名**。
#:   ★ 依据（逐字核过源码）：`tool_registry.py:507` 是 `kwargs[inject_as or inj] = resolver(params)`，
#:     而 `register()`（同文件 `:559`）**不往下传 `inject_as`** ⇒ ★ **注入键字面上等于 `inject` 的值**。
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


#: ★★★★★ 2026-10-04（接手轮 · 规格 205「解锁 C 类」）：**三个"从 study 取子对象"的解析器**。
#:
#: 为什么（★ 机械预筛给的判据）：★ **A/B 类（首参是标量或已有注入键）已被前三坡吃干** ——
#: 要到 SC-001 的 400 就必须解锁 **C 类（351 个，首参像 COM 对象）**；
#: ★ 而 C 类里 **~90 个**只需要几个**语义无歧义**的解析器，其中这三个最干净：
#:   · `results` ⇒ `ICWStudy.Results`（研究的**结果**对象）
#:   · `mesh`    ⇒ `ICWStudy.Mesh`（研究的**网格**对象）
#:   · `options` ⇒ 研究**选项**对象（★ 读参数里的 `study_name` 与 `family`）
#: ★ 与 `resolve_study` 同手法（都按 `study_name` 定位），只是**多走一步**取子对象 ✓
#: ⚠ **与"危险旋钮"的区别**：★ 这三个只**取对象**、不替调用方改设置 ⇒ 安全；
#:   ★ 批 82 删掉的 `configure_mesh_settings` / `mesh_safety_apply` 是**会改设置**的原始旋钮
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
    except Exception as exc:                                        # noqa: BLE001
        raise RuntimeError("研究上取不到 `Results`（%s: %s）—— ★ 先跑一次求解再读结果"
                           % (type(exc).__name__, str(exc)[:120]))
    if res is None:
        raise RuntimeError("研究上 `Results` 为 None —— ★ 该研究**还没算出结果**"
                           "（先 `solidworks_simulation_run_analysis`）")
    return res


def resolve_mesh(params: Any):
    """注入**研究的 `Mesh` 对象**（`ICWStudy.Mesh`）—— ★ 供首参名叫 `mesh` 的那批函数。"""
    from scripts.sw_connect import get_com_member
    study = resolve_study(params)
    try:
        mesh = get_com_member(study, "Mesh")
    except Exception as exc:                                        # noqa: BLE001
        raise RuntimeError("研究上取不到 `Mesh`（%s: %s）—— ★ 先建网格"
                           % (type(exc).__name__, str(exc)[:120]))
    if mesh is None:
        raise RuntimeError("研究上 `Mesh` 为 None —— ★ 该研究**还没建网格**"
                           "（用 `solidworks_simulation_create_mesh_safely`）")
    return mesh


def resolve_view(params: Any):
    """注入**活动文档的活动视图**（`IModelView`）—— ★ 供首参名叫 `view` 的 `sw_view` 族函数。

    :raises RuntimeError: 活动视图取不到（★ 不返回 None 让下游崩在别处）
    """
    from scripts.sw_view import get_active_view
    return get_active_view(resolve_model(params))


def resolve_study_options(params: Any):
    """注入**研究选项对象** —— ★ 供首参名叫 `options` 的那批函数。

    ★ 读两个参数：`study_name`（定位研究，空名取第一个）与 `family`
      （选项族，缺省 `ICWStaticStudyOptions`）—— ★ 与 `resolve_study` 同手法 ✓
    """
    from scripts.sw_simulation_study_options import study_options_of
    family = (getattr(params, "family", "") or "ICWStaticStudyOptions").strip()
    study = resolve_study(params)
    opts = study_options_of(study, family)
    if opts is None:
        raise RuntimeError("取不到研究选项族 %r —— ★ 该研究可能不属于这一族" % family)
    return opts


RESOLVERS: dict[str, Any] = {
    "model": resolve_model,
    "sw_app": resolve_sw_app,
    "study": resolve_study,
    #: ★ 轮 237（砌墙 W6 / Spec Kit `139`）：**注入名只能是这张表的键**（见 known-facts 169）
    #: —— 而 `scripts/sw_assembly.py` 里有一批函数的首参叫 **`asm_model`**（不是 `model`）。
    #: ★ 装配文档**同样是 `IModelDoc2`** ⇒ 复用同一个解析器；★ 不动 `tool_registry`（它明确
    #:   「不硬编码宿主 API，全从这里供给」）⇒ **加一行正是这张表的设计用途**。
    "asm_model": resolve_model,
    #: ★ 24h 计划 段 2.1（Spec Kit `143`）：`sw_simulation_loads` 那批函数首参是 `manager`
    #:   ⇒ 加一行即可挂（★ 这条表**就是**为"注入名各不相同"而设计的，见 known-facts 169）。
    "manager": resolve_manager,
    #: ★ 2026-10-03（接手轮）：**工程图 subskill 里的函数首参叫 `drawing_model`**
    #:   —— 实现文件 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`，
    #:   经 `scripts/sw_drawing.py`（`spec_from_file_location` 按路径加载后再逐个导出公开名）可达。
    #:   ★ 依据（逐字核过源码）：`tool_registry.py:507` 是 `kwargs[inject_as or inj] = resolver(params)`，
    #:     而 `register()`（同文件 `:559`）**不往下传 `inject_as`** ⇒ **注入键字面上等于 `inject` 的值**；
    #:     ★ 而那个文件的父目录名 `solidworks-engineering-drawing` **带连字符**（非合法标识符）
    #:     ⇒ 无法写进 `module=`（`tool_registry.py:524` 是 `__import__("scripts.%s" % spec.module, …)`）。
    #:   ⇒ ★ 不在这里加这一行，任何挂它的工具都会在运行期
    #:     **`TypeError: unexpected keyword argument 'model'`**。
    #:   ★ 工程图文档同样是 `IModelDoc2` ⇒ **复用 `resolve_model`**，与 `asm_model` 同一手法。
    #:   ★ 本条由 space-bunny 的 L3 档实测发现、Lead 逐条核源码确认
    #:     （见 `specs/202-user-coverage-gaps/recon/bunny-L3-toolspec-draft.py.txt`）。
    "drawing_model": resolve_model,
    #: ★★ 2026-10-03（接手轮）：修「注入键 ≠ 函数首参名」那 11 条 —— 见上面两个新函数前的长注释。
    #:   `sw`：`batch10` 的 3 条（孔标准/紧固件类型/紧固件表类型）函数首参叫 **`sw`**；
    #:   `cost_manager`：`batch38` 的 8 条 Costing 工具首参叫 **`cost_manager`**
    #:     （★ 它们原先声明 `inject="manager"` —— 而那是 **Simulation** 的解析器）。
    "sw": resolve_sw,
    "cost_manager": resolve_cost_manager,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 204 的批 79）：**`doc`** ——
    #:   ★ 那一批是**装配爆炸视图 9 个**（`scripts/sw_assembly_doc.py` 里新增的包装）——
    #:   ★★ **它们的首参叫 `doc`**（该模块**既有**的 `add_mate(doc)` / `hide_component(doc, …)`
    #:     一律用 `doc`），★ 而 `RESOLVERS` 里**只有 `model` / `asm_model`，没有 `doc`** ⇒
    #:   ★★★ 我第一版写 `inject="asm_model"` ⇒ `check_param_binding` **当场报**：
    #:     「`inject='asm_model'` **不在函数的形参表里**（形参：['doc']）—— ★ `register()` 不传
    #:      `inject_as` ⇒ **注入键字面上等于 inject 的值** ⇒ 调用时必
    #:      `TypeError: unexpected keyword argument 'asm_model'`」（★ 事实 502/169 的同一回事）✓
    #:   ⇒ ★ 按那张表**自己的设计意图**加这一行（"注入名各不相同 ⇒ 加一行正是它的用途"），
    #:     ★ **而不是去改包装的形参名**（那会让 `sw_assembly_doc.py` 内部风格分裂）✓
    #:   ★ 装配/零件文档都是 `IModelDoc2` ⇒ **复用 `resolve_model`**，与上面 `asm_model` 同一手法 ✓
    "doc": resolve_model,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205 的批 80）：**`sldworks`** ——
    #:   ★ `scripts/sw_automation_knowledge.py` 那 6 个函数（命令锁 / 首选项开关 / 自弹提示）
    #:     的**首参叫 `sldworks`**（★ 它们是 `ISldWorks` 上的操作）⇒ 白名单里既没有 `sldworks`
    #:     也没有它等价的键名 ⇒ ★ 事实 502（注入键**字面当关键字**传入）下必 `TypeError` ✓
    #:   ★ 复用 `resolve_sw`（= `resolve_sw_app`，回 `ISldWorks`）——
    #:     ★ 与该表既有的 `sw` 键**同一手法**（`sw` 也是为此加的，见上方 `"sw"` 那条）✓
    "sldworks": resolve_sw,
    #: ★★★★★ 2026-10-04（接手轮 · 规格 205 的"解锁 C 类"）：**`results` / `mesh` / `options`** ——
    #:   ★★ 为什么要加（★ 机械预筛给的判据）：★ A/B 类（首参是标量或已有注入键）**已被前三坡吃干**，
    #:     要到 400 必须解锁 **C 类（351 个，首参像 COM 对象）**；
    #:   ★ 而 C 类里 **~90 个**只需几个"**从 study 取**"的解析器 —— ★ **语义无歧义**：
    #:     · `results` ⇒ `ICWStudy.Results`（研究的**结果**对象）
    #:     · `mesh`    ⇒ `ICWStudy.Mesh`（研究的**网格**对象）
    #:     · `options` ⇒ 研究**选项**对象（★ 与 `resolve_study` 同手法：**读参数**里的 `study_name`
    #:       与 `family`，缺省取第一个研究 / `ICWStaticStudyOptions`）✓
    #:   ★ 它们与 `resolve_study` 是**同一种**解析器（都按 `study_name` 定位），只是**多走一步**
    #:     从 study 上取子对象 ⇒ ★ 与事实 169 那张表的设计意图一致 ✓
    #:   ⚠ **与"危险旋钮"的区别**：★ 这三个只**取对象**、不替调用方改设置 ⇒ 安全；
    #:     ★ 而批 82 删掉的 `configure_mesh_settings` / `mesh_safety_apply` 是**会改研究设置**的
    #:     原始旋钮（事实 526 的 40 GB 事故）⇒ ★ 那条禁令不受本次影响 ✓
    "results": resolve_results,
    "mesh": resolve_mesh,
    "options": resolve_study_options,
    #: ★★★★★ **`view`** —— ★ 解锁 `sw_view.py` 的 **26 个**候选（它们的首参都叫 `view`，是
    #:   **`IModelView`**，而"活动文档的活动视图"**语义唯一**）⇒ ★ 仓里已有 `sw_view.get_active_view` ✓
    #: ⚠⚠ **禁忌（可执行）**：★ `sw_drawing_view.py` 里那些首参**也叫 `view`**，但它们是
    #:   **`IView`（图纸视图）**、**不是** `IModelView` ⇒ ★ 用本键注给它们会**注错对象**
    #:   （★ 事实 36 那一族：接口/对象错了表现为"什么都没反应"，最难看）
    #:   ⇒ ★ 由 `tools/check_bunny_toolspec_rows.py` 的 **⑪** 挡住：
    #:     `module == "sw_drawing_view"` ∧ `inject == "view"` ⇒ **判废** ✓
    #:   ★ 要挂 `sw_drawing_view` 那族，得**另加**一个按名字取 `IView` 的解析器（本轮未加）✓
    "view": resolve_view,
}

#: 全部批次（**按注册顺序**）。新增批次只在这里加一行。
BATCH_MODULES = (
    "tool_specs_batch1",
    "tool_specs_batch2",
    "tool_specs_batch3",
    "tool_specs_batch4",
    "tool_specs_batch5",   # 轮 90：孤立能力暴露的第一步（只读/视图/选择）
    "tool_specs_batch6",   # 轮 93：孤立能力暴露的第二步（无参选择器 / BOM）
    "tool_specs_batch7",   # 轮 96：孤立能力暴露的第三步（预览准备 / 场景刷新）
    "tool_specs_batch8",   # 轮 97：**换池子** —— 从未暴露且「只被测试调用」的那批取
    "tool_specs_batch9",   # 轮 98：模具域「已实现 + 有测试 + 未暴露」的 3 个
    "tool_specs_batch10",  # 轮 128：把轮 123~127 **查证并真机跑过**的 4 个高层入口接出去
    #: 轮 204（Spec Kit `123`）：★ **候选先变成"可复现的全量清单"再选** ——
    #: `probe_unexposed_functions.py` 此前只印前 30（302 里 87% 看不见）⇒ 本轮先给它加结构化输出，
    #: 再从"首参可注入"的 51 个里取**拓扑的目标/约束/控制**这一族 4 个。
    "tool_specs_batch11",
    #: 轮 205（Spec Kit `124`）：★ **先把枚举核清再挂** —— 上批因"枚举值未核"留批的三个
    #: （脱模方向 / 应力比较器 / 对称类型），取值来自出厂反射转储 + 官方 VBA 示例。
    "tool_specs_batch12",
    #: 轮 206（Spec Kit `125`）：仿真研究的报告 / 按控制划网格 / 建议网格尺寸 3 个；
    #: ★ 并把一处"两源冲突"（units=-1 到底行不行）**原样写进参数描述**，不合并成一种说法。
    "tool_specs_batch13",
    #: 轮 207（Spec Kit `126`）：视图读取 + 体上实体枚举 2 个；
    #: ★ 队列原本列了 4 个，实测另 2 个（activate_view / add_perspective）首参是 `view`
    #:   ⇒ 既有注入器没有它 ⇒ **不硬挂**，记进 A10（先定行为再做包装层）。
    "tool_specs_batch14",
    #: 轮 208（Spec Kit `127`）：结构化审查报告 1 个；
    #: ★ 队列原本列 2 个 —— 另一个 activate_plot 首参是 `results`/ICWResults，不在注入点里
    #:   ⇒ **不硬挂**（记进 A10）；本批也**不暴露** views/expected_outputs（**list 型无先例**）。
    "tool_specs_batch15",
    #: 轮 209（Spec Kit `128`）：草图几何关系 + 镜像特征 2 个；
    #: ★ 队列 A5 原写 add_sketch_relation/add_dimension —— 实测 add_dimension **碰规则 3**（裸坐标）⇒ 留批；
    #:   而"干净"里的 insert_composite_curve **本来就坏**（事实 121/124）⇒ **不挂**。
    "tool_specs_batch16",
    #: 轮 211（Spec Kit `130`）：圆形阵列 + 旋转凸台 2 个；
    #: ★ 并**落定规则 2 的角度换算边界** —— `_consumed(angle_deg)` + `derived_args` 用
    #:   `sw_connect.deg()` 换算一次（**改名不换算会把"度"当"弧度"静默传进去**）。
    "tool_specs_batch17",
    #: 轮 222（砌墙 W1 / Spec Kit `131`）：草图只读查询 4 个；
    #: ★ 取草图对象**只能按名取**（真机探针：GetActiveSketch2/ActiveSketch 在草图关闭后均 None）；
    #: ★ 挂的是"只回读数"的薄函数（get_lines 返回数值数组，AI 没法从 36 个 float 判断几条线）。
    "tool_specs_batch18",
    #: 轮 224（砌墙 W2 / Spec Kit `132`）：当前活动工程图的轻量只读读数 3 个；
    #: ★ 与 `solidworks_inspect_drawing` 的分工是"**不**要路径、**不**开件、**不**出预览"；
    #: ★ 两点真机坑已处理：宽高是**米**（已换算成 mm）· 图纸本身会被当成假视图（已过滤）。
    "tool_specs_batch19",
    #: 轮 227（砌墙 W3 / Spec Kit `133`）：**读文件自定义属性** 2 个；
    #: ★ 补的是真空白 —— 本仓库能"写"属性（上游工具）却**读不回来验**；
    #: ★ 两个真机坑：`Extension.CustomPropertyManager` **必须当方法调用**；
    #:   读值只能用 `Get(name)`（`Get2..Get6` 的 by-ref out 在 pywin32 下报类型不匹配）。
    "tool_specs_batch20",
    #: 轮 229（砌墙 W4 / Spec Kit `135`）：**建草图 + 画几何** 5 个；
    #: ★ 本批补的是**最底层的短板** —— 此前 MCP 里连草图都建不了，
    #:   以致已挂的 revolve_boss / create_hole_feature / 钣金 base_flange **全都用不了**；
    #: ★ 画几何必须给平面内坐标 ⇒ 参数用**语义名 + _mm**（规则 2 合规 + 规则 3 的豁免路径）。
    "tool_specs_batch21",
    #: 轮 230（砌墙 W4 续 / Spec Kit `136`）：**拉伸族** 3 个；
    #: ★ **第一批能建出实体**的工具 —— 与 batch21（建草图）合起来才是完整建模闭环；
    #: ★ `depth`/`total_depth` 用 param_alias 改成 `_mm`（能力层一行未改）；★ 不做换算（毫米）；
    #: ★ chamfer/fillet 不在本批 —— 它们要**选择**（selection 包装层），单独一批做。
    "tool_specs_batch22",
    #: 轮 231（砌墙 W4 续 / Spec Kit `137`）：**倒角 / 圆角** 2 个；
    #: ★ **第一次用规则 3 的声明式 `selection` 驱动"建特征"工具** ——
    #:   能力层两个函数**都没有 edges 参数** ⇒ 它们作用在**当前选择**上 ⇒
    #:   对外的 selection 由 `pre_call` 解析成真实选区（复用 batch4 的既有机制）。
    "tool_specs_batch23",
    #: 轮 234（砌墙 W5 / Spec Kit `138`）：**读质量属性** 1 个；
    #: ★ 又一个"能写不能读"的真空白（有 set_mass_property_override 却读不出实际值）；
    #: ★ 单位是**毫米系**（实测，非 SI 米）⇒ 不做换算；
    #: ⚠⚠ **`mass` 的物理单位未确证**（volume×density 量纲不成立）⇒ 说明里明写，不猜。
    "tool_specs_batch24",
    #: 轮 237（砌墙 W6 / Spec Kit `139`）：**装配只读** 3 个；
    #: ★ 本批第一次用 `inject="asm_model"` —— 为此给 RESOLVERS **加了一行**；
    #: ★★ 干涉检查那个函数**修过三处成员名却从没验过**（其注释自述"此前静默降级"）
    #:   ⇒ 本批的真机验证是它的**第一次验证**，且设计成**一正一反两个场景**。
    "tool_specs_batch25",
    #: 轮 238（砌墙 W7 / Spec Kit `140`）：**仿真载荷包装层** 2 个 —— ★★ **护城河**。
    #: ★ 核实过：四家合计只有 4 个仿真工具，且**全是"建研究/跑"**，**没有一个挂载荷/约束**。
    #: ★ 而能力层**早已包装好**（`apply_fixed_restraint(study, …)` / `apply_normal_force(study, …)`）
    #:   ⇒ 本批即目标里那句「**有就直接挂**」。
    #: ★ 包装形状是**三种机制的组合**：`inject="study"` + `pre_call`（先选面）+ `derived_args`（补 model）。
    "tool_specs_batch26",
    #: 轮 239（24h 计划 段 1.1 / Spec Kit `141`）：**仿真研究族** 3 个（建/取/列）——
    #: ★★ **补 W7 的硬前置**（此前 `study_name` 只能引用已存在的研究）。
    #: ★ 3 个薄函数包既有四个：`create_static_study` 回**三元组**（含 COM 对象 + `entry_name`）、
    #:   `iter_studies` yield **`(index, study)` 元组**、`get_study_by_name` 回**对象或 None**
    #:   ⇒ ★ 都不可直接挂（MCP 回不了对象）⇒ 各包一层只回可 JSON 化的东西。
    "tool_specs_batch27",
    #: ⚠⚠⚠ **轮 240：`tool_specs_batch28.py`（网格/求解/读数 4 个）**已注册但**未真机验证**** ——
    #:   ★ 真机验证**三次都触发 Simulation 的模态框**「未定义载荷或规定的位移」
    #:   （框内原文：「**固定-刚性零件上的载荷将不处于活动状态**」）⇒ **COM 挂起、救不回来**；
    #:   加了两道前置门（材料回读非空 + `LoadsAndRestraintsManager.Count >= 2`）**仍然弹**。
    #:   ⇒ ★ 按 `AGENTS.md` 硬约束③：**明确标注「未真机验证」**（★ 不谎称验证过），
    #:     能力条目等级 = **`stitched`**（不是 `verified`）。
    #:   ★ 查清的正路 = **对照实验逐个分离变量**（事实 165 第 12 条）—— 见 known-facts 174。
    #:   ★★★★★ **2026-10-04（接手轮）本条已被查清并推翻 —— 留此仅为可追溯**（★ 事实 528）：
    #:     ★ 真根因**不是**"前置门不够"，而是**力的面选不中** —— 配方用 `select_face_at(0,0,0)`
    #:       而**原点在实体内部** ⇒ `SelectByID2("","FACE",0,0,0,…)` 回**选区计数 0**
    #:       （★ 这条真机对比**就写在本仓 `sw_simulation.select_face_at` 的注释里**）
    #:       ⇒ 空 `DispArray` ⇒ **载荷建成也无效** ⇒ 那个框 + `Results` 为空 ✓
    #:     ★★ 处置：两个 apply 新增 **`face_selector`**（声明式、零坐标）⇒ **选不中就拒绝**；
    #:       探针/配方改用 `-z`/`+z` ⇒ ★ **一跑成功**：网格 6541 单元 / 求解 **2.6 s** ·
    #:       **`results_present=True` · `plot_count=4`** ✓
    #:     ★ 所以 `analysis_run_readback` 已由 `stitched` **升为 `verified`**；★ 本批 4 个工具
    #:       **不必再挂着"未真机验证"** —— ★ 而**推荐入口**见 `tool_specs_batch78`（安全链）✓
    "tool_specs_batch28",
    #: ★ 24h 段 2.1（Spec Kit `143`）：载荷族广度 4 个（压力/力矩/重力/离心力）
    #:   —— ★ 首参是 `manager` ⇒ 靠上面新加的 `"manager"` 解析键注入。
    "tool_specs_batch29",
    #: ★ 24h 段 2.2（Spec Kit `144`）：拓扑读数与参数 6 个
    #:   —— ★ 只读数/设参数，**不跑求解** ⇒ 无挂起风险。
    "tool_specs_batch30",
    #: ★ 24h 段 5「修地基」（Spec Kit `145`）：建网格前的**地基闸门** 1 个
    #:   —— ★ 把"跑求解必挂"掐断在网格之前（与 `sw_isolate` 互补：一个防发生、一个防外溢）。
    "tool_specs_batch31",
    #: ★ 24h 段 3（Spec Kit `146`）：建模闭环补全 4 个
    #:   —— ★ 四个都**不吃裸坐标**（规则 3），且**统一回读确认**（规则 6）。
    "tool_specs_batch32",
    #: ★ 24h 段 4（Spec Kit `147`）：**配置族 6 + 导出族 6**
    #:   —— ★ 两族**全无裸坐标**（规则 3）· 配置族能力层回 dict ⇒ 直挂；
    #:     导出族按铁律包成"**文件存在且非空**"的回读报告。
    "tool_specs_batch33",
    #: ★ 24h 段 4 续（Spec Kit `151`）：**声明式建孔 5 个** —— ★ 规则 3 合规版
    #:   （★ 上游那个 `solidworks_create_hole_feature` 吃裸坐标 `center_x_mm/center_y_mm`）。
    "tool_specs_batch34",
    #: ★ 24h 段 4 续（Spec Kit `152`）：**焊件读数与切割清单 6 个**
    #:   —— ★ 10 个未挂里按"入参能不能表达"筛出的 6 个（★ 全无裸坐标）。
    "tool_specs_batch35",
    #: ★ 24h 段 4/5 续（Spec Kit `153`）：**读数与纯数据 11 个**
    #:   —— ★ 薄模块里按"入参能不能表达"筛出（★ 全无裸坐标）。
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
    #:   —— ★ 填三条空条目（external_spur_gear_geometry / standard_parts_toolbox / sketch_chamfer）。
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
    #:     **仍然不做**（事实 40）；★★ `FeatureExtruRefSurface3`（建曲面**特征**）**真机通过**。
    "tool_specs_batch45",
    #: ★ 24h 段 6 续（Spec Kit `167`）：**几何量测**
    #:   —— ★ 补「四家有我们没有」的真缺：★ 全仓 grep `measure`/`area`/`distance` **均为 0**。
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
    "tool_specs_batch53",   # 轮 397：选择底座（真缺口批量挂柜台·段 1）
    "tool_specs_batch54",   # 轮 398：草图图元（段 2）
    "tool_specs_batch55",   # 轮 399：零件读/自动标注（段 3）
    "tool_specs_batch57",   # 轮 401：孔族（段 4）
    "tool_specs_batch58",   # 轮 402：仿真简单载荷 6 条（段 5）
    "tool_specs_batch59",   # 轮 403：导出（图片 + 钣金展开 DXF）（段 6）
    "tool_specs_batch56",   # 轮 405：恢复 add_dimension（穷举表证实能建）
    "tool_specs_batch60",   # 轮 414：A 组收尾（分布质量 + 力）
    "tool_specs_batch61",   # 轮 425：B 组第一条（刚性连接件）
    "tool_specs_batch62",   # 轮 428：焊件族第一条（结构构件）
    "tool_specs_batch63",   # 轮 452：按声明式选择器选面
    "tool_specs_batch64",   # 轮 459：连接件族第三条（link · 两个顶点）
    "tool_specs_batch65",   # 轮 464：B1 批草图图元（3点矩形/平行四边形/切线弧/3点圆弧/部分椭圆/抛物线/圆锥/周边圆）
    "tool_specs_batch66",   # 轮 465：B3 批草图编辑 6 个（剪裁/延伸/等距/圆角/线性阵列/圆周阵列）
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
    #:   ★ 旋转曲面前置试了 4 种未成（★ 最后量到 `轴选中数=5`）⇒ 按 A4 不进 `verified`、**不登记成工具**。
    "tool_specs_batch69",
    #: ★ 2026-10-03（轮 479）：B8 参考几何体 —— **只登记真机建成的 3 条**
    #:   （质心 / 边界框 / 坐标系）。
    #:   ★ 基准面与点**前置未成**（★ 官方要求先按 mark 选参考实体，而 mark 表未给）⇒ 不登记。
    "tool_specs_batch70",
    #: ★ 2026-10-03（轮 481）：B7 特征下拉 —— **只登记契约能表达的那一条**（通过参考点的曲线）。
    #:   ★ 配合参考实现层**已真机建成**，★ 而它第 2 个形参是 **`IEntity` 对象**，
    #:     `Param` 表达不了 ⇒ 留待接声明式选择器（★ 不假装）。
    "tool_specs_batch71",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 T201/T401：
    #:   把 `docs/user-feature-coverage.md` §八 缺口项里**真有实现**的接成工具 ——
    #:   旋转曲面 · 孔向导 · 完全定义检查（★ 三个都带真机证据：`output/coverage-gap-batch1-evidence.json`）。
    #:   ⚠ 判据来自 `tools/audit_gap_implementations.py`（**AST**，★ 不用 grep ——
    #:     grep 会把来源块里引用的官方成员名算成"有实现"）。
    "tool_specs_batch72",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 R2：**工程图真缺口** 4 个 ——
    #:   断裂视图 · 辅助视图 · 表面粗糙度符号 · 基准符号。
    #:   ★★ 与 batch72 **性质不同**：batch72 接的是"AST 量出**已有实现**"的，
    #:     ★ 而这 4 项**本仓一个都没有** ⇒ ★ 先写能力层 `scripts/sw_drawing_create_missing.py`，
    #:     ★ 再在这里声明成工具（`module="sw_drawing_create_missing"`、`inject="model"`）。
    #:   ★ 第 5 项「气泡序号」**故意不在这里**：它的形参是 `AutoBalloonOptions` **COM 对象**，
    #:     `Param` 表达不了 ⇒ ★ 能力层已实现、待将来走 `extra_op`。
    #:   ★★ **真机前置已逐条写进能力层**（`InsertBreak3` 非废弃那一代 / 辅助视图要**先选一条边** /
    #:     粗糙度"位置参数**仅当** leaderType != swNO_LEADER" / 基准符号 `InsertDatumTag2` **零参**）。
    "tool_specs_batch73",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 **R1**：**工程图「已实现却没挂」的 8 项** ——
    #:   投影视图 · 剖面视图 · 局部视图 · 图纸格式/模板 · 注释/文字 · 孔表 · 修订表 · 中心符号线。
    #:   ★★ **本批一行实现逻辑都不新写**（"缝合优先不发明"）—— 依据
    #:     `recon/drawing-existing-coverage.md`：那 13 项里**已实现 8 项、挂出的只有 4 项**
    #:     （且全靠同一个 `solidworks_drawing`）⇒ ★ 本批只做**转接 + 单位边界**。
    #:   ★ 转接层 `scripts/sw_drawing_expose.py`：对外收**毫米**（规则 2 的换算**只在那里发生一次**），
    #:     并把**前置回读**带回来（事实 496：前置与能力必须分开记）。
    #:   ★★ `inject="drawing_model"` —— 该键已在 `RESOLVERS` 里（事实 491）。
    #:   ⚠ 其中「中心符号线」那条走**批量**入口，★ **尚未单独真机验证**（单点入口已实测为阴性）。
    "tool_specs_batch75",
    #: ★ 2026-10-03（接手轮）· 规格 `specs/202-user-coverage-gaps` 的 **R3**：**钣金/焊件 4 条** ——
    #:   斜接法兰 · 闭合角 · 顶端盖 · 角撑板（焊件）。
    #:   ★★ **本批的三条废弃链查证（队友逐条核官方页）**：
    #:     ① `IModelDoc2.InsertSheetMetalMiterFlange`（**11 参**·回 `void`）**废弃**
    #:        → **`IFeatureManager.InsertSheetMetalMiterFlange`（14 参·回 `Feature`）**
    #:        ⇒ ★ **同名两份、参数个数不同** —— 用错**不只是"没反应"，而是个数对不上**；
    #:     ② `InsertEndCapFeature` → `…3`，★ 而 **`InsertEndCapFeature2` 不在链上**（其官方页**无 Obsolete 句**）
    #:        ⇒ ★ **不是 1→2→3 线性**；
    #:     ③ `InsertGussetFeature` → **`…3`**，★ 而 `…2` 的官方页**无 Obsolete 句** ⇒ ★ **中间代状态官方没写**。
    #:   ★ 第 5 项「中面」**不在这里**：`insert_mid_surface(model, **body**, **part_doc**, …)` 的
    #:     第 2/3 个形参是 **`Body2`/`ModelDoc2` 对象** ⇒ `Param` 表达不了 ⇒ ★ 能力层有、**工具层不建**。
    #:   ⚠⚠ **本批的 4 条工具尚未真机验证**（★ 与 batch72/73 一样，★ 注册 ≠ 能跑）——
    #:     ★ 待下一轮用工具层 e2e 探针补读数，★ **在那之前不许把它们的 level 写成 verified**。
    "tool_specs_batch74",
    #: ★ 2026-10-03（接手轮）· **R6+**：把「**已真机证明、代码却只在 `tools/prove_*.py` 里**」的直入法挂成工具。
    #:   ★ 判据逐字来自 `recon/scan-S2b-ledger-vs-tools.md` 的 **A 表**（台账有、`mcp_tools` 无挂 —— 41 条），
    #:     ★ 而它的 `limitations` **自己写着**「⚠ 本包装未接进 MCP 工具层」⇒ ★ 挂出来就是**台账写明的下一步**。
    #:   ★★ **不发明**：`scripts/sw_feature_entry_ops.py` 的调用序**照抄那次建成的真机探针**。
    #:   本批 1 条：**特征/螺纹**（`InsertCosmeticThread3`，7 参 · 未废弃）。
    #:   ⚠ **尚未经工具层端到端验证**（★ 真机证据目前只在**探针**那一级）——
    #:     ★ 在 e2e 读数出来之前，★ **不许**写成「经工具层已验证」。
    "tool_specs_batch76",
    #: ★★★★★★ 轮 103：★ **补我自己造成的一个缺口** ——
    #:   ★ 任务书阶段 5 逐字「建能力 → **挂 ToolSpec** → 真机验证」⇒
    #:   ★★ 我在轮 95–102 补了 6 个**回读能力**、★ 做了建能力与真机验证、
    #:     ★★★ **却没挂 ToolSpec** ⇒ 真机查（★ `output/_check_readback_toolspecs.py`）：
    #:       ★ **6 个全部「没有」** · ★★ **与 `feature_readback` 相关的 ToolSpec 一个都没有** ✓
    #:   ★★★★ **⇒ 那 6 个能力**只在 Python 层可用、★ MCP 层调不到**** ✓
    #:   ★★★★★ **判据**：★★★ **「建成了能力」与「能力能被调」是两件事** ——
    #:     ★ 前者看**函数存在 + 真机读数**、★ 后者看**ToolSpec 清单里有没有它** ✓
    "tool_specs_batch77",
    #: ★★★★★★ 轮 104：★ **把"安全链"从探针搬进工具层** ——
    #:   ★ 业主原话：★「修好，而且要**站在未来别的人使用我们项目的时候也能生效**的角度**根因修复**」✓
    #:   ★★ 事实 526/528 把"网格爆内存"与"求解不出结果"修在了**能力层与探针**里，
    #:     ★★ **而工具层（别人真正会调的那一层）拿到的仍是裸的 `create_mesh_report`**：
    #:       · 不设安全档 ⇒ 曲率自适应 + `MinElementSize=0` ⇒ **网格规模不受控**；
    #:       · 无求解前内存闸 ⇒ **超预算也照跑**；· 不过忙检 ⇒ **SW 忙时照样下发调用**（卡死路径）✓
    #:   ⇒ ★ 本批 2 个：`..._create_mesh_safely`（量闸 → 安全档 → 建网格 → 真读数 → 内存闸 → **还原**）
    #:     + `..._solver_type`（★ 让调用方**看得见求解器**，免得把 FFEPlus 的内存换算过度外推 —— 事实 529）✓
    "tool_specs_batch78",
    #: ★★★★★★ 轮 105：**规格 204 的批 79 —— FR-008 的两半**（`specs/204-tool-ramp/`）：
    #:   ★ 规格 202 的 FR-008 逐字要求「装配**爆炸视图**与**宏/VBA 执行** MUST 可用」，
    #:     ★★ 而实测 `capabilities.yaml` 搜 `Explode`/`RunMacro` = **0 命中** ⇒ 两块**完全空白** ✓
    #:   · ① **爆炸视图 9 个**：`sw_assembly_doc` 里**新增** 9 个包装（成员名与 arity 取自该模块
    #:     机械生成的登记表 → `call_assembly_doc` 会**在调用前**核实参个数）·
    #:   · ② **宏 8 个**：新建 `scripts/sw_macro.py`（`ISldWorks.RunMacro2`，★ 官方签名 **4 入 + 1 out**）
    #:     + `sw_macro_guard` 的 7 个**纯文本**函数（生成/抽取/校验/选模板/落盘；它们此前一个都没挂）✓
    #:   ★ 本批 **17 个** ⇒ 工具数 296 → **313**（规格 204 的 SC-001 第一段）✓
    #:   ★ 与既有工具**零重叠**（SC-004）：既有 296 个里没有爆炸视图、也没有宏**执行**工具 ✓
    "tool_specs_batch79",
    #: ★★★★★★ 轮 106：**规格 205 的批 80 —— 自动化诊断知识 + 会话忙闲检测**（12 个）：
    #:   · `sw_automation_knowledge` 6 个（HRESULT 释义 / 命令锁 3 / 首选项开关 2）——
    #:     ★ 它们的首参叫 **`sldworks`** ⇒ ★ 本批**新加了一个注入键** `"sldworks": resolve_sw`
    #:     （★ 与既有的 `"sw"` 键同一手法 —— 事实 169 那张表的设计用途）✓
    #:   · `sw_com_traps` 2 个**纯函数**（`deprecated_successor` / `find_real_implementations`）——
    #:     ★ 同一批里另 7 个**明确不做**（弹框的 `send_message` · 重复的 `explain` ·
    #:       无独立价值的 `is_type_mismatch` · 内部管道 `byref_*` · 收可调用的 `adaptive_arity` ·
    #:       收字节的 `is_swp_macro` · generator 的 `iter_real_sources`）⇒ ★ 原因逐条写在批次文件头 ✓
    #:   · `sw_busy` 4 个（忙闲 / 卡死 / 求解器进程 / 等空闲）—— ★ 本会话新建的模块，
    #:     ★★ 它的判据正是事实 526 的教训（忙碌要**归属家族进程**，否则孤儿窗口假阳性）✓
    #:   ★ 本批 **12 个** ⇒ 工具数 313 → **325** ✓
    #:   ★ 选域依据：机械预筛（`output/prescreen-deduped.json`）—— ★ 不再按"候选数"排序，
    #:     而按"**去重后可挂数**"排序（★ 这是 v3 批序的由来，见规格 §8.2）✓
    "tool_specs_batch80",
    #: ★★★★★★ 轮 107：**规格 205 的批 81 —— 由 Bunny 扇出产出、经机器门禁过滤**（18 个）：
    #:   ★ 这是**第一次**用"60 路 Bunny 扇出 → 门禁逐行核 → 转换器生成批次文件"这条路做的批次 ✓
    #:   · 域：`sw_review`（10）· `sw_feature_readback`（3）· `sw_import_mesh_reference`（2）·
    #:     `sw_preflight` / `sw_sketch_dimensions` / `sw_misumi` / `sw_automation_knowledge` /
    #:     `sw_com_traps`（各 1）✓
    #:   ★★ 门禁挡下的与**主线明确不做**的都不进来：
    #:     · `solidworks_dialog_send_message`（弹模态框）· `solidworks_com_is_type_mismatch`
    #:       （无独立价值）—— ★ 由 `tools/build_toolspec_batch_from_rows.py` 生成后**主线再删** ✓
    #:   ★ 本批文件**由 `tools/build_toolspec_batch_from_rows.py` 生成**（★ 只收过门禁且
    #:     `exposable=True` 的行，并按构造保证规则 2 —— 长度缺 `_mm` 就自动改名 + 补 `param_alias`）✓
    "tool_specs_batch81",
    #: ★★★★★★ 轮 108：**规格 205 的批 82 —— 第二坡扇出（仿真/装配/导出域）**（13 个）：
    #:   ★ 生成器产出 **19** 个 ⇒ ★ 主线按 **FR-006 语义去重**删掉 **6** 个：
    #:     · `export_pdf` / `export_flat_pattern_dxf` / `…_report` —— ★ `export_active` 已含 PDF、
    #:       `export_dxf` **就是**钣金展开导出（其 doc 逐字这么写）⇒ **真重复** ✓
    #:     · `assembly_add_distance_mate_by_name` —— `add_distance_mate` 已覆盖 ✓
    #:     · ★★ **`simulation_configure_mesh_settings` / `simulation_mesh_safety_apply`** ——
    #:       ★ 它们是**未护栏的原始网格旋钮**：★ 事实 526 的 **40 GB 事故**正是**盲设它们**造成的；
    #:       批 78 已定「安全入口 = `create_mesh_safely`」（自动设安全档 + 事后还原）
    #:       ⇒ ★ **不单独发旋钮**（D-1 宁缺毋滥）—— ★ 这是**安全**判断，不是数量判断 ✓
    #:   ★ 留下的 13 个覆盖：装配（含 5 种配合/抑制/替换/平行）· 导出 · 外观渲染材质删除 ·
    #:     仿真（加载项 / 研究管理器 / 按类型建研究 / 内存预算 / 网格设置报表 / 校验）✓
    "tool_specs_batch82",
    #: ★★★★★ 轮 109：**规格 205 的批 83 —— 第二坡的"真新"残余**（4 个）：
    #:   ★ 第二坡 92 行里，**33 条是"已建过"**（★ 门禁的 ⑧ 分支把"已建"与"真撞名"分开之后
    #:   才读得出来）、6 条是主线按 FR-006/安全判掉的 ⇒ ★ **真正新的只有这 4 个** ✓
    #:   · `solidworks_simulation_get_loads_manager` / `get_results` —— ★ 仿真**读数**入口
    #:     （★ 与批 78 的"安全建网格"配套：建完要能读结果）✓
    #:   · `solidworks_simulation_solve_memory_preflight` —— ★ **只读**内存预算前置闸
    #:     （★ 与危险旋钮不同：**它只算不设**，故单独发它是安全的 —— 对比批 82 删掉的那两个）✓
    #:   · `solidworks_simulation_get_edge_weld_connector` —— 边焊缝连接件读数 ✓
    "tool_specs_batch83",
    #: ★★★★★ 轮 110：**规格 205 的批 84 —— 第三坡（残余 40 模块）产出**（7 个）：
    #:   ★ 第三坡是**薄模块**（`sw_part` / `sw_hole_features` / `sw_costing` / `sw_sketch` /
    #:     `sw_surface_features` / `sw_weldment` / `sw_ref_geometry` / `sw_gui_*` …）——
    #:     ★★ 实测**可暴露率偏低**（45 行里只有 9 行 exposable）⇒ ★ 真正新的 7 个 ✓
    #:   · ★ 真建模能力：`solidworks_revolve_cut`（旋转切除）· `solidworks_surface_cut`（曲面切除）·
    #:     `solidworks_ref_geometry_create_3d_bounding_box`（3D 边界框）·
    #:     `solidworks_sketch_select_segment`（按序号选草图段 —— ★ 声明式，不收坐标）✓
    #:   · 诊断/取证：`solidworks_gui_get_foreground_window` · `solidworks_gui_screen_png` ·
    #:     `solidworks_weldment_iter_features`（焊件特征树遍历）✓
    "tool_specs_batch84",
)

def all_specs() -> list:
    """汇总全部批次的声明（**逐批导入**，缺一个模块就响亮报错）。"""
    specs: list = []
    for mod_name in BATCH_MODULES:
        mod = __import__(mod_name)
        batch = getattr(mod, "SPECS_%s" % mod_name.rsplit("batch", 1)[1].upper(), None) \
            or next((getattr(mod, n) for n in dir(mod) if n.startswith("SPECS_")), None)
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
    return register(mcp, specs, base, response_enum, run_locked,
                    resolvers=RESOLVERS)
