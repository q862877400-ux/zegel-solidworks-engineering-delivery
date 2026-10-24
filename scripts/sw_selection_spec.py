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
| `__current_selection__` | 用**当前已选中**的东西 | ★ 对 AI 驱动最自然：先用别的工具在界面上选好，再让本工具操作；
也是 `sw_part._ensure_sketch_selected` 已有的约定 |
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
#: ★★ 2026-10-01（轮 328）**加了 `VERTEX`** —— ★ 判据：官方 `IBody2.GetVertices()`（**0
#: 参**，
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
    for i in range(1, count + 1):  # ⚠ 官方 Index **从 1 开始**
        try:
            obj = get_com_member(sm, "GetSelectedObject6", i, int(mark))
        except Exception:  # noqa: BLE001 —— 个别下标取不到就跳过，不编造
            continue
        if obj is not None:
            out.append(obj)
    return out


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）
# 文件:   `IBody2.GetEdges() -> Object`（边数组） / `IBody2.GetFaces() -> Object`（面数
# 组）
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
    bodies = get_com_member(model, "GetBodies2", 0, True)  # 0 = swSolidBody
    if not bodies:
        raise EntitySelectionError("活动文档里没有实体（swSolidBody）—— 先建几何")
    if body_index >= len(bodies):
        raise EntitySelectionError(
            "body_index=%d 越界（共 %d 个体）" % (body_index, len(bodies))
        )
    #: ★★ 2026-10-01（轮 328）：**顶点也走同一条路** —— ★ 官方 `IBody2.GetVertices()`（0
    #:  参）。
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


def select_entity_by_index(
    model, kind: str, index: int, *, body_index: int = 0, append: bool = False
) -> int:
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
      * ★ **语义选择器**（2026-10-25 新增）——
        ``"+z"`` / ``"-z"`` / ``"+x"`` / ``"-x"`` / ``"+y"`` / ``"-y"`` /
        ``"top_face"`` / ``"near:<x>,<y>,<z>"``
        ⇒ 见下方「为什么加语义选择器」。

    ## 为什么加语义选择器

    `docs/ENGINEERING-PATH.md` 第四节 E3 要求「跨重建**不依赖选区或下标**」。
    而 `index:<n>` 与 `__current_selection__` **两者都不可跨重建**：

      * `index:<n>` —— `reference_resolver.LIMITATIONS` 逐字：
        「索引不跨编辑保持 …… 改完模型后，之前算出来的 face/edge index 全部作废」
      * `__current_selection__` —— 取决于调用时选了什么，不是模型属性

    ⇒ 语义选择器是**几何事实**（方向 / 语义名 / 几何锚点），改主参数后仍指同一类几何。
      解析在**用时**做（`reference_collect.resolve_semantic`），
      下标只是中间量，**不保存**。

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
        #: ★ 语义选择器分流：先解析成下标，再走 `index:` 那条路
        try:
            from engineering.reference_collect import is_semantic_selector
        except ImportError:  # 顶层载入
            is_semantic_selector = lambda _x: False  # noqa: E731
        if is_semantic_selector(s):
            try:
                from engineering.reference_collect import resolve_semantic
            except ImportError:  # 顶层载入
                from reference_collect import resolve_semantic  # type: ignore
            try:
                got = resolve_semantic(model, s, kind, body_index=body_index)
            except Exception as exc:  # noqa: BLE001
                raise EntitySelectionError(
                    "语义选择器 %r 解析失败：%s: %s"
                    % (s, type(exc).__name__, str(exc)[:140])
                )
            s = "index:%d" % int(got["index"])
        if s.startswith("index:"):
            try:
                idx = int(s.split(":", 1)[1])
            except ValueError:
                raise EntitySelectionError(
                    "非法的 index 选择器 %r（应为 index:<整数>）" % sel
                )
            items = entities_on_body(model, kind, body_index=body_index)
            if idx < 0 or idx >= len(items):
                raise EntitySelectionError(
                    "%s 序号 %d 越界（体 %d 上共 %d 个）"
                    % (kind, idx, body_index, len(items))
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


# ── 24h 计划 段 4 续（Spec Kit `150`）：**从选区读点**（★ 规则 3 的关键一环）──────────
# ───
# ★★★ 为什么需要它（★ 规则 3 的**精神**，不只是字面）：
# 孔族那几个建孔函数吃 **`center`（一个坐标元组）**。★ 规则 3 的红线**字面**只管**参数名
# **
#   （`x` / `y` / `cx` …）⇒ ★ `center` **不在** `_BARE_COORD_NAMES` 里
#   （★ 它在 `_COORD_COMPONENT_NOTE`，★ 那条的定性是"**名字不表态**，只登记不判"）。
# ⇒ ★★ **所以严格说它们能挂 —— 但那会绕过规则 3 的**精神****（"选择必须用声明式 `selecti
# on`"）。
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


def selection_point(model, selection: str = "", selection_kind: str = "FACE") -> dict:
    """★ **读当前选区那个点的坐标**（★ 毫米）—— 供"用声明式选择代替裸坐标"的包装使用。

    ★★ 用途：★ 孔族（`create_through_hole` 等）吃 `center`（**一个坐标元组**）⇒
      ★ 包一层「**先选点、再建孔**」⇒ ★ **工具层的参数里就没有坐标了**（★ 规则 3 的精神）。

    返回 `{"ok": bool, "point_mm": (x, y, z) | None, "selection_count": int, "error": str | None}`。
    ⚠ **不猜**：★ `GetSelectionPoint` 取不到就 `ok=False` + 写明原因（★ 铁律 5）。
    """
    out: dict = {"ok": False, "point_mm": None, "selection_count": None, "error": None}
    #: ★★★ 2026-10-07（接手轮 · 规格 216 T-216-07）先按声明式选择器**重建**选区 ——
    #:   ★ 起因：★ 本函数**读当前选区**、★ 而**注入解析器会清空选区**（**事实 503**）⇒
    #:     ★ 模型**没有任何办法**先把目标选好 ⇒ ★ 经工具层**恒回空** ✗
    #:     （★ 预选族基线把它归在「真危险·诊断型」）✓
    #:   ★★ 与 `measure_selection` **同一条理由**：★ "读哪个"是**调用方的意图**
    #:     ⇒ ★ **绝不能由函数乱造**（★ 造了读到的就不是你要的那个）⇒ ★ 让调用方**声明** ✓
    #: ★ 规则 3 **不许收裸坐标** ⇒ ★ 收 `selection`（`index:<n>` / `__current_selection_
    #: _`）+ 种类 ✓
    #:   ★ 必须在**读选区之前**（★ 下面紧接着就是读计数）✓
    if str(selection or "").strip():
        try:
            resolve_selection(model, str(selection), str(selection_kind or "FACE"))
        except Exception as exc:  # noqa: BLE001
            out["selection_count"] = 0
            out["error"] = (
                "选区未建立：%s: %s（★ 前置未成立、★ 与「取不到点」是两件事）"
                % (type(exc).__name__, str(exc)[:140])
            )
            return out
    try:
        mgr = get_com_member(model, "SelectionManager")
    except Exception as exc:  # noqa: BLE001
        out["error"] = "取不到 SelectionManager：%s" % str(exc)[:120]
        return out
    try:
        n = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        out["selection_count"] = n
    except Exception:  # noqa: BLE001
        pass
    if not out["selection_count"]:
        out["error"] = (
            "当前**没有选中任何东西** ⇒ 读不到点。"
            "★ 先用声明式选择选中一个点 / 草图点 / 面，再调本函数。"
        )
        return out
    #: ★★★★ 2026-10-01 轮 266 真机实测：★ **必须用 `GetSelectionPoint2`，且它吃 `AtIndex
    #: `**。
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
    #: 并且**两个入口的报错都留住**（★ 先前是后者覆盖前者 ⇒ 看不到 2 参那个为什么失败）
    #: 。
    errors: list = []
    for _nm, _args in (("GetSelectionPoint2", (1, -1)), ("GetSelectionPoint", (1,))):
        cand = get_com_member(mgr, _nm)
        if cand is None:
            errors.append("%s 不可达" % _nm)
            continue
        entry_used = _nm
        try:
            pt = cand(*_args)
        except Exception as exc:  # noqa: BLE001
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
        out["error"] = (
            "GetSelectionPoint 回 None ⇒ "
            "★ 选中的**不是**一个点（可能是面 / 边 / 特征）。"
            "★ 本函数不猜别的重载，如实报「取不到」。"
        )
        return out
    try:
        vals = [float(x) for x in pt][:3]
    except Exception:  # noqa: BLE001
        out["error"] = "返回值不是可转 float 的序列：%s（%s）" % (
            str(pt)[:60],
            type(pt).__name__,
        )
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
# ★ 该模块已有 `select_object`（吃一个 **COM 对象**）与 `resolve_entity`（**返回**一个 C
# OM 对象）
#   ★★ 而 **这两者的返回值 MCP 层过不去**（COM 对象不可 JSON 序列化）⇒ 本段给它们各加一层
# **只回 JSON** 的 report 包装（★ 而"选中"这个动作本身靠 `Select4` —— 事实 32：对边/面按
# 名字选不中）。
# 官方依据: `C:\swapi\types\IModelDocExtension\SelectByID2.md` · `IEntity` 的 `Select4`
#           ·
#   `ISelectionMgr.GetSelectedObjectCount2`（★ 判据永远是这个回读数 —— 事实 8）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def select_by_selector_report(
    model, selector, kind: str = "EDGE", *, body_index: int = 0, append: bool = False
) -> dict:
    """★ **用声明式选择器选中一个实体**（★ MCP 可用的形态 —— 只回 JSON，不回 COM 对象）。

    ★ 它把 `select_object`（吃 COM 对象）与 `resolve_entity`（吐 COM 对象）**接起来**，
    对外只暴露**选择器字符串**（★ 规则 3：不传坐标、不传对象）。

    :param selector: ``"__current_selection__"`` · ``"index:<n>"`` · 或一个 COM 对象（内部用）。
    :param kind: ``"EDGE"`` / ``"FACE"`` / ``"VERTEX"``。
    :returns: `{ok, selector, kind, count}` —— ★★ **判据是 `count`**（★ 事实 8：`Select4` 的
        返回值不可信，只有 `GetSelectedObjectCount2(-1)` 的回读算数）。
    """
    out: dict = {
        "ok": False,
        "selector": str(selector)[:60],
        "kind": str(kind).upper(),
        "count": None,
        "error": None,
    }
    try:
        obj = resolve_entity(model, selector, kind, body_index=body_index)
    except Exception as exc:  # noqa: BLE001
        out["error"] = "解析选择器失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    try:
        out["count"] = int(
            select_object(model, obj, append=append)
        )  #: ★ 它自己回读计数
    except Exception as exc:  # noqa: BLE001
        out["error"] = "Select4 失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["ok"] = bool(out["count"])
    if not out["ok"]:
        out["error"] = "选完**回读计数为 0** ⇒ 没选中（★ 事实 8：不许信返回值）"
    return out


def resolve_entity_report(
    model, selector, kind: str = "EDGE", *, body_index: int = 0
) -> dict:
    """★ **解析声明式选择器并回报结果**（★ 只回 JSON —— 把 COM 对象挡在里面）。

    ★ `resolve_entity` 本身**返回 COM 对象** ⇒ MCP 层过不去 ⇒ 本包装把它换成
    **可核对的描述**：选到什么、选区现在有几个。

    :returns: `{ok, selector, kind, count, resolved}` —— ★ `resolved=True` 表示解析出了对象；
        ★ 而**是否真的在选区里**看 `count`（★ 解析出来 ≠ 选中 —— 事实 8）。
    """
    out: dict = {
        "ok": False,
        "selector": str(selector)[:60],
        "kind": str(kind).upper(),
        "count": None,
        "resolved": False,
        "error": None,
    }
    try:
        obj = resolve_entity(model, selector, kind, body_index=body_index)
        out["resolved"] = obj is not None
    except Exception as exc:  # noqa: BLE001
        out["error"] = "解析选择器失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    try:
        out["count"] = int(get_selection_count(model))
    except Exception as exc:  # noqa: BLE001
        out["error"] = "回读选区计数失败：%s" % str(exc)[:120]
        return out
    out["ok"] = bool(out["resolved"]) and bool(out["count"])
    if not out["ok"] and out["resolved"] and not out["count"]:
        out["error"] = (
            "解析出了对象**而选区计数为 0** ⇒ 选择器是 `__current_selection__` 时"
            "常见（★ 它不重选）；★ 要真的选中请用 `select_by_selector_report`"
        )
    return out


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_selection_spec.py —— 追加 `entities_as_array`
# 定位:   ★ 2026-10-03（轮 424）承**事实 337** 的**正解**：★ **绕开"从选区读多实体"**。
# ★★ 事实 336/337 的定性：★ `ISelectionMgr` 上"按序号取对象"那一族（`GetSelectedObject6`
#  /
# `4` / `5` / `GetSelectedObjectsFace`）**只拿得到第 1 个**，★ 而 `GetSelectedObjectCoun
# t2(-1)`
#     **如实报 2** ⇒ ★★ **"从选区读回多个"这条路不通**（★ 五个入口都试过）。
#   ★★★ 而**事实 32** 早就写着：★ 选实体的可行路径是 `IEntity.Select4`（**按对象**）
#     或按面上的点 ⇒ ★★ **而"实体对象"本仓**本来就能直接拿到**（`entities_on_body`）——
#     ★ 它用 `IBody2.GetFaces()/GetEdges()/GetVertices()` 直接列出一个体上的实体 ✓
# ⇒ ★★ 于是"多实体"载荷**根本不需要"从选区读回来"**：★ **把已知的那些对象直接装成数组**
# ✓
# 官方依据: `IBody2.GetFaces` / `GetEdges` / `GetVertices`（★ 本模块 `entities_on_body`
#           已在用）·
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
                % (kind, index, body_index, len(items))
            )
        picked.append(items[index])
    return picked


# ── 规格 209 · B3（idx 115 `edges` + idx 145 `faces`，★ 裁决书强制**合并成一条工具**）─
# ─────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_selection_spec.py —— 追加 `entity_geometry` / `entities_report`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B3-1** · 外部项目 idx **115 `edges`**
#   + idx **145 `faces`**。★★ 裁决书的硬约束（§一/§三.1/§六）逐字：
#   「★ 不新建平行工具 ⇒ **扩已有的 `solidworks_entities_on_body`**」·
# 「与 #115 的 `GetEdges` **是同一件活的两种 kind** ⇒ ★ **一条工具**（FACE/EDGE/VERTEX）
# ，
#     **不许开两条**」✓
#   ★★ 它点名的**真风险**：「本条真风险**不是后端到不了**，而是『**读属性读不到**』
#     （事实 3x）⇒ 先单独做一条**小验证**再落」✓
#   ★★ **而本条落地的真正缺口是另一件事（我自己读代码时发现的）**：既有工具指向的
#     `entities_on_body` **返回 COM 对象** ⇒ ★ **过不了 MCP 的 JSON 边界** ——
#     ★ 也就是说那条工具**经工具层拿不到任何可用的东西**（"能枚举"≠"能把结果交出去"）✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
# · `C:\swapi\types\IBody2\{GetEdges,GetFaces,GetVertices}.md` —— 三个都是**零参**、回 `
# System.object`
# · `C:\swapi\types\IEdge\{GetStartVertex,GetEndVertex}.md` —— 回 `System.object`（顶点
# ）
#   · `C:\swapi\types\IVertex\GetPoint.md` —— `System.object GetPoint()`
#   · `C:\swapi\types\IFace2\GetArea.md` —— `System.double GetArea()`
# · ★★ **`IEdge` 上没有任何「长度」成员** —— 官方成员表逐条列过（`GetCurve` / `GetCurveP
# arams` /
#     `GetStartVertex` / `GetEndVertex` …）⇒ ★ 边长**只能自己算**（两个顶点求距离）✓
# ⚠ 这一条是 2026-10-06 真机踩出来的：我按印象读 `IEdge.GetLength` ⇒ **12 条边全部抛异常
# **
#     （★ 铁律 5：**名字缺席 = 官方没有这个成员**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **单位**：`IVertex::GetPoint` 的读数与文档长度单位一致（本机 **毫米**）——
# ★ 判据是**边长**：60×40×2 的板算出 `{0.002, 40.0, 60.0}`、厚 2 的算出 `{2.0, 40.0, 60.
# 0}`
#   （见 `output/spec209-hem-units.json`）⇒ ★ 本模块如实标 `_mm` / `_mm2` ✓


def entity_geometry(model, kind: str, index: int, *, body_index: int = 0) -> dict:
    """★ 取**第 index 个实体**的**可 JSON 化的几何读数**（★ 把 COM 对象挡在函数里面）。

    :param kind: `"EDGE"` / `"FACE"` / `"VERTEX"`。
    :returns: ★ 按 kind 给不同的读数（★ **都来自官方成员，一个不编**）：
      ```
      VERTEX ★ {"point_mm": [x, y, z]}                    ← IVertex::GetPoint()
      EDGE   ★ {"start_mm": [...], "end_mm": [...],
                "length_mm": L}                            ← GetStartVertex/GetEndVertex 自己算
                                                             ★★ 官方 IEdge **没有** Length 成员
      FACE   ★ {"area_mm2": A}                             ← IFace2::GetArea()
      ```
    ⚠ **读不到就如实报**（`None` + `error`）—— ★ 这正是裁决书点名的那个风险
      （「读属性读不到」）：★ 本函数**把"读不到"与"读到 0"分开** ✓
    """
    info: dict = {"index": int(index), "kind": str(kind).upper(), "error": None}
    try:
        items = entities_on_body(model, kind, body_index=body_index)
        if index < 0 or index >= len(items):
            raise EntitySelectionError(
                "%s 序号 %d 越界（体 %d 上共 %d 个）"
                % (kind, index, body_index, len(items))
            )
        ent = items[index]
    except Exception as exc:  # noqa: BLE001
        info["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        return info
    k = info["kind"]
    if k == "VERTEX":
        try:
            pt = get_com_member(ent, "GetPoint")
            info["point_mm"] = [round(float(v), 6) for v in list(pt)[:3]]
        except Exception as exc:  # noqa: BLE001
            info["error"] = "IVertex.GetPoint 读不到：%s" % str(exc)[:120]
    elif k == "EDGE":
        pts = []
        for member in ("GetStartVertex", "GetEndVertex"):
            try:
                v = get_com_member(ent, member)
                p = get_com_member(v, "GetPoint") if v is not None else None
                pts.append(
                    None if p is None else [round(float(x), 6) for x in list(p)[:3]]
                )
            except Exception as exc:  # noqa: BLE001
                info["error"] = "IEdge.%s→GetPoint 读不到：%s" % (
                    member,
                    str(exc)[:100],
                )
                pts.append(None)
        info["start_mm"], info["end_mm"] = pts[0], pts[1]
        if pts[0] and pts[1]:
            info["length_mm"] = round(
                sum((pts[1][i] - pts[0][i]) ** 2 for i in range(3)) ** 0.5, 6
            )
    elif k == "FACE":
        try:
            info["area_mm2"] = round(float(get_com_member(ent, "GetArea") or 0.0), 6)
        except Exception as exc:  # noqa: BLE001
            info["error"] = "IFace2.GetArea 读不到：%s" % str(exc)[:120]
    return info


def entities_report(model, kind: str, *, body_index: int = 0) -> dict:
    """★ **列出体上的实体（带几何读数）**—— ★ **MCP 可用的形态**（只回 JSON，不回 COM 对象）。

    ★★ 为什么需要它：既有的 `entities_on_body` **返回 COM 对象** ⇒ ★ **过不了 MCP 的 JSON 边界**
      ⇒ 那条工具**经工具层其实拿不到东西**（★「能枚举」与「能交出去」是两件事）✓
    ★★ **判据（规则 6）**：① **计数**；② ★ **欧拉公式 `V − E + F = 2`**（★ 本仓既有的判据，
      20×20×10 盒子真机 `FACE=6 · EDGE=12 · VERTEX=8`）—— ★ 它**不需要任何新 API** ✓
    :returns: `{ok, kind, body_index, count, entities, euler, error}`
      ★ `euler` 三个计数**各自独立回读**（★ 不是从别的字段推的）；
      ★ ★ **读不到某一类就回 `None`**（★ 不拿 0 冒充）✓
    """
    out: dict = {
        "ok": False,
        "kind": str(kind).upper(),
        "body_index": int(body_index),
        "count": None,
        "entities": [],
        "euler": None,
        "error": None,
        "★": "判据 = **计数** + **欧拉公式 V−E+F=2**（★ 本仓既有判据，不需要新 API）；"
        "★ 每类的计数**各自回读**，读不到就 `None`（不拿 0 冒充）",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    try:
        items = entities_on_body(model, kind, body_index=body_index)
    except Exception as exc:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["count"] = len(items)
    rows = []
    for i in range(len(items)):
        rows.append(entity_geometry(model, kind, i, body_index=body_index))
    out["entities"] = rows
    #: ★★ 欧拉校验：三类计数**各自独立回读**（★ 读不到 → None，★ 不拿 0 冒充）
    counts: dict = {}
    for k in ENTITY_KINDS:
        try:
            counts[k] = len(entities_on_body(model, k, body_index=body_index))
        except Exception:  # noqa: BLE001
            counts[k] = None
    v, e, f = counts.get("VERTEX"), counts.get("EDGE"), counts.get("FACE")
    euler = {"vertex": v, "edge": e, "face": f}
    if None not in (v, e, f):
        euler["v_minus_e_plus_f"] = v - e + f
        euler["holds"] = (v - e + f) == 2
    else:
        euler["v_minus_e_plus_f"] = None
        euler["holds"] = None
        euler["note"] = "★ 有一类实体**读不到** ⇒ 欧拉式**判不了**（★ 不拿 0 冒充）"
    out["euler"] = euler
    out["ok"] = out["count"] is not None
    unreadable = [r["index"] for r in rows if r.get("error")]
    if unreadable:
        out["error"] = (
            "**%d 个实体的几何读不到**（★ 这正是裁决书点名的"
            "「读属性读不到」风险）：序号 %r —— ★ 计数仍然有效，几何字段如实为空"
            % (len(unreadable), unreadable[:8])
        )
    return out
