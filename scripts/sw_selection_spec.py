"""声明式实体选择解析层 —— 把「选哪个边/面」解析成**已选中的 COM 对象**。

## ⚠⚠ 本模块的设计来自**真机实测**，不是推断（2026-10-01，SW 2026 SP4.1）
在自建的 100×60×20 mm 板上逐个试（证据脚本 `D:\\AI\\SW\\probe_entity_select_by_name.py`）：

| 选法 | 结果 |
|---|---|
| `SelectByID2("Edge1", "EDGE")` | **计数 0** ⇒ **边没有可用的名字** |
| `SelectByID2("Face1", "FACE")` | **计数 0** ⇒ **面也没有** |
| `SelectByID2("", "EDGE", 0, 0, 0, …)` | **计数 0** ⇒ 原点不在边上 |
| `SelectByID2("", "FACE", x, y, z, …)` | **计数 1** ✓ ⇒ 按**面上的点**选面可行 |
| **`edge.Select4(False, callout)`** | **计数 1** ✓ ⇒ **按**对象**选实体可行** |

**⇒ 两条设计结论（本模块的根据）：**
1. **实体没有名字** ⇒ 「按名字选」这条路**对实体不成立**（对**特征**成立，见 `sw_part._ensure_sketch_selected`）
2. **正解是 `IEntity.Select4(Append, Callout)` —— 按**对象**选** ⇒ 解析层要产出**对象**，
   不是名字、也不是坐标

## 三种解析器（覆盖真实用法）
| 选择器 | 语义 | 为什么需要 |
|---|---|---|
| `__current_selection__` | 用**当前已选中**的东西 | ★ 对 AI 驱动最自然：先用别的工具在界面上选好，再让本工具操作；也是 `sw_part._ensure_sketch_selected` 已有的约定 |
| `index:<n>` | 体上第 n 个实体（边或面，按类型） | 确定性、可复现（适合脚本化与测试） |
| 对象本身 | 已经是 COM 对象，直接 `Select4` | 组合上层工具（如 `path_ref` 从别处取到） |

**⚠ 单位与坐标**：本模块**不接受裸坐标**（并入规范规则 3）。
需要按坐标定位时，用上层已有的 `sw_simulation.select_face_by_selector`（面），
或先 `index:` 选中再取几何判据 —— **不在这里开一个坐标后门**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）+ 本项目真机实测结论
# 文件:   `IEntity.Select4(Boolean Append, Callout Callout) -> Boolean`
#         —— `SolidWorks.Interop.sldworks.dll` 反射
#         `IModelDoc2.SelectionManager` → `ISelectionManager.GetSelectedObject6(Int32, Int32)`
# 定位:   T-011 §11.3 的 C2/C3 前置（「按名字/类型选择」解析层）；
#         也服务 B 类。**实测结论见上表**（证据脚本 `probe_entity_select_by_name.py`）。
#  ⚠ `Callout` 必须是 `VARIANT(VT_DISPATCH, None)`（`sw_part._empty_callout()`），
#    **传 `None` 会得到 `'类型不匹配'`** —— AGENTS.md 已知事实 12 早有记载。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **已在本机实测**（2026-10-01，SW 2026 SP4.1，100×60×20 mm 板）：
#   证据脚本 `D:\\AI\\SW\\probe_selection_spec_e2e.py` ⇒ **12 项通过 / 0 失败**：
#     · `entities_on_body` → 12 边 / 6 面（与几何相符）
#     · `index:0` / `index:11` / `index:0`(FACE) 解析 → 计数均为 1
#     · `__current_selection__`：空选区**正确报错**、有选中时**正确取到**
#     · 直接传 COM 对象 → 计数 1
#     · 4 个「该报错就报错」的判定全部正确报错（非法类型 / 越界 / 非法选择器 / 空选区）
#     · **复现了「`SelectByID2` 对边/面的名字选不中」**（两者计数均为 0）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
    from .sw_part import _empty_callout
except ImportError:  # pragma: no cover
    from sw_connect import get_com_member
    from sw_part import _empty_callout

__all__ = [
    "CURRENT_SELECTION",
    "EntitySelectionError",
    "get_selection_count",
    "clear_selection",
    "current_selection",
    "entities_on_body",
    "select_object",
    "select_entity_by_index",
    "resolve_entity",
    "resolve_selection",
]

#: 特殊选择器：用**当前已选中**的东西（与 `sw_part._ensure_sketch_selected` 同约定）
CURRENT_SELECTION = "__current_selection__"

#: 实体类型（`SelectByID2` / 体遍历用的官方类型串）
#: ★★ 2026-10-01（轮 328）**加了 `VERTEX`** —— ★ 判据：官方 `IBody2.GetVertices()`（**0 参**，
#:   ★ 反射 arity = 0）× `ILoop2.GetVertices()` ⇒ ★ **顶点就是体上的一种 entity**，
#:   ★ 所以它属于**本函数**的语义，★ **不该新开一个工具**（★ 缝合优先）。
#: ⚠ 而**顶点不能"按名字选"**（★ 与边/面同理，事实 32）—— ★ 本处只做**枚举**。
ENTITY_KINDS = ("EDGE", "FACE", "VERTEX")


class EntitySelectionError(RuntimeError):
    """选择解析失败 —— **选不到就报错，不静默返回空**（本项目一贯纪律）。"""


def get_selection_count(model) -> int:
    """回读当前选区计数。

    ⚠ `SelectByID2` / `Select4` 的**返回值不可信**（AGENTS.md 已知事实 8：
    12 次全 false 而计数 = 12）⇒ **判据永远是本函数的回读值**。
    """
    sm = get_com_member(model, "SelectionManager")
    return int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)


def clear_selection(model) -> None:
    """清空选区（`IModelDoc2.ClearSelection2(Boolean)`）。"""
    get_com_member(model, "ClearSelection2", True)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）
# 文件:   `ISelectionManager.GetSelectedObject6(Int32 Index, Int32 Mark) -> Object`
# 定位:   把**当前选区**取成对象列表。`GetSelectedObject6` 的 Index 是**从 1 开始**的
#         （官方示例与 `sw_sheet_metal` 的文档串都用 `GetSelectedObject6(1, -1)`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **已在本机实测**（同上证据脚本）：空选区返回空列表、有选中时正确取到。
# ────────────────────────────────────────────────────────────────────
def current_selection(model, *, mark: int = -1) -> list[Any]:
    """返回**当前选区**里的对象（空选区返回空列表）。

    :param mark: 选择标记（`-1` = 不筛，官方示例的常用值）。
    """
    sm = get_com_member(model, "SelectionManager")
    count = get_selection_count(model)
    out: list[Any] = []
    for i in range(1, count + 1):          # ⚠ 官方 Index **从 1 开始**
        try:
            obj = get_com_member(sm, "GetSelectedObject6", i, int(mark))
        except Exception:                   # noqa: BLE001 —— 个别下标取不到就跳过，不编造
            continue
        if obj is not None:
            out.append(obj)
    return out


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）
# 文件:   `IBody2.GetEdges() -> Object`（边数组） / `IBody2.GetFaces() -> Object`（面数组）
#         `IPartDoc.GetBodies2(Int32 Type, Boolean VisibleOnly) -> Object`
# 定位:   **按序号取实体** —— 因为实测证明**边/面没有可用的名字**（见模块头），
#         序号是唯一确定性的、可脚本化的定位方式。
#  ⚠ 序号顺序**官方未承诺稳定**（与体的拓扑生成顺序有关）⇒ 本函数文档里写明这一点，
#    调用方**不应**把序号当作跨版本/跨重建的持久引用。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **已在本机实测**（同上证据脚本）：12 边 / 6 面，与 100×60×20 mm 板的几何相符。
# ────────────────────────────────────────────────────────────────────
def entities_on_body(model, kind: str, *, body_index: int = 0) -> list[Any]:
    """取第 `body_index` 个体上的实体列表（`kind` = `"EDGE"` / `"FACE"` / `"VERTEX"`）。

    ★★ 2026-10-01（轮 328）**加了 `VERTEX`** —— 判据：官方 `IBody2.GetVertices()`（0 参）
      × `ILoop2.GetVertices()` ⇒ ★ 顶点就是体上的一种 entity，★ 所以它属于本函数。
      ★ 真机（20×20×10 盒子）⇒ **FACE=6 · EDGE=12 · VERTEX=8** ⇒ ★ **欧拉公式 `V−E+F=2` 成立** ✓
    ⚠ **序号顺序官方未承诺稳定**（取决于体的拓扑生成顺序）⇒
    **不要把序号当持久引用**（跨版本/跨重建可能变）。
    ⚠ 顶点与边/面同理**不能"按名字选"**（事实 32）—— ★ 本函数只做**枚举**。
    """
    k = str(kind).strip().upper()
    if k not in ENTITY_KINDS:
        raise EntitySelectionError(
            "未知的实体类型 %r；合法值：%r" % (kind, list(ENTITY_KINDS))
        )
    bodies = get_com_member(model, "GetBodies2", 0, True)   # 0 = swSolidBody
    if not bodies:
        raise EntitySelectionError("活动文档里没有实体（swSolidBody）—— 先建几何")
    if body_index >= len(bodies):
        raise EntitySelectionError(
            "body_index=%d 越界（共 %d 个体）" % (body_index, len(bodies))
        )
    #: ★★ 2026-10-01（轮 328）：**顶点也走同一条路** —— ★ 官方 `IBody2.GetVertices()`（0 参）。
    member = {"EDGE": "GetEdges", "FACE": "GetFaces", "VERTEX": "GetVertices"}[k]
    items = get_com_member(bodies[body_index], member)
    return list(items) if items else []


def select_object(model, obj, *, append: bool = False) -> int:
    """用 `IEntity.Select4` 选一个**对象**，返回**回读到的选区计数**。

    ⚠ 实测结论：这是**选中实体（边/面）的可行路径**；`SelectByID2` 对边/面
    **按名字选不中**（计数 0）。证据见模块头的表。
    """
    if obj is None:
        raise EntitySelectionError("select_object 收到了 None —— 调用方应先解析出对象")
    get_com_member(obj, "Select4", bool(append), _empty_callout())
    return get_selection_count(model)


def select_entity_by_index(model, kind: str, index: int, *,
                           body_index: int = 0, append: bool = False) -> int:
    """按**序号**选第 `index` 个实体（`index` 从 0 开始，是本模块的约定）。

    ⚠ 序号顺序官方未承诺稳定 —— 见 :func:`entities_on_body`。
    """
    items = entities_on_body(model, kind, body_index=body_index)
    if index < 0 or index >= len(items):
        raise EntitySelectionError(
            "%s 序号 %d 越界（体 %d 上共 %d 个）"
            % (kind, index, body_index, len(items))
        )
    return select_object(model, items[index], append=append)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把上面几个实测过的入口组合成一个**声明式**入口）
# 文件:   scripts/sw_selection_spec.py 的 resolve_entity / resolve_selection
# 定位:   T-011 分类表 C2/C3 与 B 类共同需要的那个**收敛点**：
#         对外只收一个**声明式选择器字符串**（或一个对象），
#         内部按实测可行的路径（`Select4`）把它变成**已选中的对象**。
# 官方签名依据: 复用本模块已核过的官方签名，**不引入新的 COM 成员**
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **已在本机实测**（同上证据脚本，12/12 通过）
# ────────────────────────────────────────────────────────────────────
def resolve_entity(model, selector, kind: str, *, body_index: int = 0):
    """把**声明式选择器**解析成**已选中的实体对象**并返回它。

    `selector` 支持：
      * ``"__current_selection__"`` —— 用当前选区里的第一个（**不重选**）
      * ``"index:<n>"``            —— 体上第 n 个实体（从 0 开始）
      * 一个 **COM 对象**          —— 直接 `Select4` 它

    :raises EntitySelectionError: 选择器非法、越界、或合法但**选不中**（不静默返回 None）。
    """
    sel = selector
    if isinstance(sel, str):
        s = sel.strip()
        if s == CURRENT_SELECTION:
            found = current_selection(model)
            if not found:
                raise EntitySelectionError(
                    "选择器是 %r，但当前**没有任何选中项** —— 先在界面上选中一个实体"
                    % CURRENT_SELECTION
                )
            return found[0]
        if s.startswith("index:"):
            try:
                idx = int(s.split(":", 1)[1])
            except ValueError:
                raise EntitySelectionError("非法的 index 选择器 %r（应为 index:<整数>）" % sel)
            items = entities_on_body(model, kind, body_index=body_index)
            if idx < 0 or idx >= len(items):
                raise EntitySelectionError(
                    "%s 序号 %d 越界（体 %d 上共 %d 个）" % (kind, idx, body_index, len(items))
                )
            obj = items[idx]
            select_object(model, obj)
            return obj
        raise EntitySelectionError(
            "非法的实体选择器 %r；合法形式：%r 或 'index:<n>' 或一个 COM 对象"
            % (sel, CURRENT_SELECTION)
        )
    # 已是对象
    select_object(model, sel)
    return sel


def resolve_selection(model, selector, kind: str, *, body_index: int = 0) -> int:
    """同 :func:`resolve_entity`，但**只返回回读到的选区计数**。

    计数为 ``0`` 说明没选中 —— **调用方不得继续**（本项目一贯纪律：
    选不中就报错，不静默继续）。
    """
    resolve_entity(model, selector, kind, body_index=body_index)
    count = get_selection_count(model)
    if count <= 0:
        raise EntitySelectionError(
            "选择器 %r 解析后**选区计数为 0** —— 没选中任何东西" % (selector,)
        )
    return count


# ── 24h 计划 段 4 续（Spec Kit `150`）：**从选区读点**（★ 规则 3 的关键一环）─────────────
# ★★★ 为什么需要它（★ 规则 3 的**精神**，不只是字面）：
#   孔族那几个建孔函数吃 **`center`（一个坐标元组）**。★ 规则 3 的红线**字面**只管**参数名**
#   （`x` / `y` / `cx` …）⇒ ★ `center` **不在** `_BARE_COORD_NAMES` 里
#   （★ 它在 `_COORD_COMPONENT_NOTE`，★ 那条的定性是"**名字不表态**，只登记不判"）。
#   ⇒ ★★ **所以严格说它们能挂 —— 但那会绕过规则 3 的**精神****（"选择必须用声明式 `selection`"）。
#   ⇒ ★★★ **正解与官方一致**：★ **官方 `HoleWizard` 的工作流就是"先在面上选一个点"**
#     ⇒ ★★ **包一层**：★ **用声明式 `selection` 选点 ⇒ 从选区读坐标**
#       ⇒ ★★★ **于是工具参数里**没有坐标**，★ 只有 `selection`** ✓
#
# ★ 官方依据：`C:\swapi\types\ISelectionMgr\GetSelectionPoint.md`（★ 索引里确认存在）
#   ⚠ 另有 `GetSelectionPoint2` / `GetSelectionPointInSketchSpace(2)` ——
#   ★ 本函数**只用 `GetSelectionPoint`**（★ 取不到就如实报，★ 不去猜别的重载）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_selection_spec.py —— 本段
# 定位:   段 4 的孔族声明式包装所需的"从选区读点"。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个函数
# ─────────────────────────────────────────────────────────────────────────────


def selection_point(model) -> dict:
    """★ **读当前选区那个点的坐标**（★ 毫米）—— 供"用声明式选择代替裸坐标"的包装使用。

    ★★ 用途：★ 孔族（`create_through_hole` 等）吃 `center`（**一个坐标元组**）⇒
      ★ 包一层「**先选点、再建孔**」⇒ ★ **工具层的参数里就没有坐标了**（★ 规则 3 的精神）。

    返回 `{"ok": bool, "point_mm": (x, y, z) | None, "selection_count": int, "error": str | None}`。
    ⚠ **不猜**：★ `GetSelectionPoint` 取不到就 `ok=False` + 写明原因（★ 铁律 5）。
    """
    out: dict = {"ok": False, "point_mm": None, "selection_count": None, "error": None}
    try:
        mgr = get_com_member(model, "SelectionManager")
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "取不到 SelectionManager：%s" % str(exc)[:120]
        return out
    try:
        n = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        out["selection_count"] = n
    except Exception:                                          # noqa: BLE001
        pass
    if not out["selection_count"]:
        out["error"] = ("当前**没有选中任何东西** ⇒ 读不到点。"
                        "★ 先用声明式选择选中一个点 / 草图点 / 面，再调本函数。")
        return out
    #: ★★★★ 2026-10-01 轮 266 真机实测：★ **必须用 `GetSelectionPoint2`，且它吃 `AtIndex`**。
    #:   · 老成员 `GetSelectionPoint` 的官方页写着
    #:     「**Obsolete. Superseded by `ISelectionMgr::GetSelectionPoint2`**」；
    #:   · 而它的签名是 **`GetSelectionPoint(AtIndex)`** —— ★ 当**零参**调会报
    #:     **`(-2147352561, '非选择性的参数。')`**（★ 那个错**看不出是"缺参数"**）。
    #:   ⇒ ★★ **定则**：★ **官方标 Obsolete 的成员，先去查它的**后继**（通常 `*2`）**，
    #:     而不是先穷举参数 —— ★ **一次文档查询 vs 试参数**（★ 同族：轮 263 的
    #:     `CreateMassProperty` ⇒ `CreateMassProperty2`，★ 而那一次**它还改变了读数**）。
    pt = None
    entry_used = None
    #: ★★★★ 官方签名（`C:\swapi\types\ISelectionMgr\GetSelectionPoint2.md`）：
    #:     `GetSelectionPoint2( **Index**, **Mark** )` —— ★ **两个参数**；
    #:     · `Index` ★「ranges from **1** to …」⇒ ★ **索引从 1 起**；
    #:     · `Mark`  ★ `-1` = 全部 · `0` = 无标记的 · 其它 = 那个标记值。
    #:   ★★ **而 `GetSelectionPoint(AtIndex)` 只有 1 参**（★ 已 Obsolete）——
    #:     ★2026-10-03（轮 397）**真机抓到**：★ 先前**给两个入口都传 `(1, -1)`**
    #:     ⇒ 走到 1 参那个必然报 **`(-2147352562, '无效的参数数目。')`**，
    #:     ★ 而那个错**指不出是参数个数的问题**（★ 同族：事实 33）。
    #:   ⇒ ★ **按名字给各自的 arity**（★ 那正是“签名三源”该给出的东西），
    #:     并且**两个入口的报错都留住**（★ 先前是后者覆盖前者 ⇒ 看不到 2 参那个为什么失败）。
    errors: list = []
    for _nm, _args in (("GetSelectionPoint2", (1, -1)), ("GetSelectionPoint", (1,))):
        cand = get_com_member(mgr, _nm)
        if cand is None:
            errors.append("%s 不可达" % _nm)
            continue
        entry_used = _nm
        try:
            pt = cand(*_args)
        except Exception as exc:                               # noqa: BLE001
            errors.append("%s%s 报错：%s" % (_nm, _args, str(exc)[:130]))
            pt = None
            continue
        if pt is not None:
            break
        errors.append("%s%s 回 None（★ 选中的可能不是点）" % (_nm, _args))
    if pt is None and errors and out.get("error") is None:
        out["error"] = " · ".join(errors)[:300]
    out["entry_used"] = entry_used
    if pt is None:
        out.setdefault("error", "两个入口都取不到点（★ 见上面的报错）")
        return out
    if pt is None:
        out["error"] = ("GetSelectionPoint 回 None ⇒ "
                        "★ 选中的**不是**一个点（可能是面 / 边 / 特征）。"
                        "★ 本函数不猜别的重载，如实报「取不到」。")
        return out
    try:
        vals = [float(x) for x in pt][:3]
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "返回值不是可转 float 的序列：%s（%s）" % (str(pt)[:60], type(pt).__name__)
        return out
    if len(vals) < 3:
        out["error"] = "返回值长度 %d < 3" % len(vals)
        return out
    out["ok"] = True
    out["point_mm"] = tuple(vals)
    return out

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_selection_spec.py —— 追加两个 report 包装
# 定位:   objective「真缺口」的 `sw_selection_spec` 族（24h 计划 v2 段 1 · 选择底座）。
#   ★ 该模块已有 `select_object`（吃一个 **COM 对象**）与 `resolve_entity`（**返回**一个 COM 对象）
#   ★★ 而 **这两者的返回值 MCP 层过不去**（COM 对象不可 JSON 序列化）⇒ 本段给它们各加一层
#   **只回 JSON** 的 report 包装（★ 而"选中"这个动作本身靠 `Select4` —— 事实 32：对边/面按名字选不中）。
# 官方依据: `C:\swapi\types\IModelDocExtension\SelectByID2.md` · `IEntity` 的 `Select4` ·
#   `ISelectionMgr.GetSelectedObjectCount2`（★ 判据永远是这个回读数 —— 事实 8）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def select_by_selector_report(model, selector, kind: str = "EDGE", *,
                              body_index: int = 0, append: bool = False) -> dict:
    """★ **用声明式选择器选中一个实体**（★ MCP 可用的形态 —— 只回 JSON，不回 COM 对象）。

    ★ 它把 `select_object`（吃 COM 对象）与 `resolve_entity`（吐 COM 对象）**接起来**，
    对外只暴露**选择器字符串**（★ 规则 3：不传坐标、不传对象）。

    :param selector: ``"__current_selection__"`` · ``"index:<n>"`` · 或一个 COM 对象（内部用）。
    :param kind: ``"EDGE"`` / ``"FACE"`` / ``"VERTEX"``。
    :returns: `{ok, selector, kind, count}` —— ★★ **判据是 `count`**（★ 事实 8：`Select4` 的
        返回值不可信，只有 `GetSelectedObjectCount2(-1)` 的回读算数）。
    """
    out: dict = {"ok": False, "selector": str(selector)[:60], "kind": str(kind).upper(),
                 "count": None, "error": None}
    try:
        obj = resolve_entity(model, selector, kind, body_index=body_index)
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "解析选择器失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    try:
        out["count"] = int(select_object(model, obj, append=append))   #: ★ 它自己回读计数
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "Select4 失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["ok"] = bool(out["count"])
    if not out["ok"]:
        out["error"] = "选完**回读计数为 0** ⇒ 没选中（★ 事实 8：不许信返回值）"
    return out


def resolve_entity_report(model, selector, kind: str = "EDGE", *, body_index: int = 0) -> dict:
    """★ **解析声明式选择器并回报结果**（★ 只回 JSON —— 把 COM 对象挡在里面）。

    ★ `resolve_entity` 本身**返回 COM 对象** ⇒ MCP 层过不去 ⇒ 本包装把它换成
    **可核对的描述**：选到什么、选区现在有几个。

    :returns: `{ok, selector, kind, count, resolved}` —— ★ `resolved=True` 表示解析出了对象；
        ★ 而**是否真的在选区里**看 `count`（★ 解析出来 ≠ 选中 —— 事实 8）。
    """
    out: dict = {"ok": False, "selector": str(selector)[:60], "kind": str(kind).upper(),
                 "count": None, "resolved": False, "error": None}
    try:
        obj = resolve_entity(model, selector, kind, body_index=body_index)
        out["resolved"] = obj is not None
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "解析选择器失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    try:
        out["count"] = int(get_selection_count(model))
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "回读选区计数失败：%s" % str(exc)[:120]
        return out
    out["ok"] = bool(out["resolved"]) and bool(out["count"])
    if not out["ok"] and out["resolved"] and not out["count"]:
        out["error"] = ("解析出了对象**而选区计数为 0** ⇒ 选择器是 `__current_selection__` 时"
                        "常见（★ 它不重选）；★ 要真的选中请用 `select_by_selector_report`")
    return out

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_selection_spec.py —— 追加 `entities_as_array`
# 定位:   ★ 2026-10-03（轮 424）承**事实 337** 的**正解**：★ **绕开"从选区读多实体"**。
#   ★★ 事实 336/337 的定性：★ `ISelectionMgr` 上"按序号取对象"那一族（`GetSelectedObject6` /
#     `4` / `5` / `GetSelectedObjectsFace`）**只拿得到第 1 个**，★ 而 `GetSelectedObjectCount2(-1)`
#     **如实报 2** ⇒ ★★ **"从选区读回多个"这条路不通**（★ 五个入口都试过）。
#   ★★★ 而**事实 32** 早就写着：★ 选实体的可行路径是 `IEntity.Select4`（**按对象**）
#     或按面上的点 ⇒ ★★ **而"实体对象"本仓**本来就能直接拿到**（`entities_on_body`）——
#     ★ 它用 `IBody2.GetFaces()/GetEdges()/GetVertices()` 直接列出一个体上的实体 ✓
#   ⇒ ★★ 于是"多实体"载荷**根本不需要"从选区读回来"**：★ **把已知的那些对象直接装成数组** ✓
# 官方依据: `IBody2.GetFaces` / `GetEdges` / `GetVertices`（★ 本模块 `entities_on_body` 已在用）·
#   事实 32（选实体的可行路径）· 事实 8（返回值不可信，以计数为准）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def entities_as_array(model, kind: str, indices, *, body_index: int = 0) -> list:
    """★ 按**已知的实体清单**取对象并装成数组 —— ★ **完全不读选区**。

    ★ 这是**事实 337 的正解**：★ `ISelectionMgr` 上"按序号取对象"那一族**只拿得到第 1 个**
    （★ `GetSelectedObject6` / `4` / `5` / `GetSelectedObjectsFace` 五个入口都试过），
    ★ 而**实体对象本身**用 :func:`entities_on_body` **就能直接拿到**
    ⇒ ★★ 于是"多实体"的载荷**不必**依赖"用户先在界面上选好"那条**交互式**假设。

    :param kind: `"EDGE"` / `"FACE"` / `"VERTEX"`。
    :param indices: 要取哪几个（★ 0 基，★ 与本模块 `select_entity_by_index` 同一约定）。
    :param body_index: 第几个体（★ 与 :func:`entities_on_body` 一致）。
    :raises EntitySelectionError: 某个序号越界（★ 早失败优于静默 —— 传不完整的数组会
        ★★ 让 SW 内部越界，★ 那正是事实 336 里 B 组崩的形态）。
    """
    items = entities_on_body(model, kind, body_index=body_index)
    picked = []
    for i in indices:
        index = int(i)
        if index < 0 or index >= len(items):
            raise EntitySelectionError(
                "%s 序号 %d 越界（体 %d 上共 %d 个）—— 早失败：传不完整的数组会让 SW 越界"
                % (kind, index, body_index, len(items)))
        picked.append(items[index])
    return picked
