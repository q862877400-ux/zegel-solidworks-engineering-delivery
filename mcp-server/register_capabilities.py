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
