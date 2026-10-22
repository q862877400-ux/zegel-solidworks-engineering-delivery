"""★ 草图几何关系**专属工具**：一次把该加的关系加全（★ 与画圆/画线同级）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/sw_sketch_relations.py
# 定位:   ★ 目标 goal-d2098c24 —— ★★ 用户 2026-10-08 逐字：「**你把给草图加定义做成一
#           个专门的工具，
# 相当于它和画圆、画圈工具是同级别的，它专门就是用来加定义的。那它这个定义是：哪几条线互
# 相平行，
# 哪条是垂直的，哪两个是同心圆，这些东西，你每一轮都要把所有这些几何关系该加的都加上。**
# 」✓
# 官方依据: ★★ **三样都读过**（★ 铁律 4）：
# · ★ 官方例 `C:\swapi\examples\Constrain_Sketch_Example_CSharp.md`（**99 行** ✓）逐字调
# 用序：
# ★ `SelectByID2(段, "SKETCHSEGMENT", …, mark)` ⇒ ★ `SketchAddConstraints("sgCOLINEAR")`
#  ⇒
#     ★ `ClearSelection2(true)` ⇒ ★ 重复 —— ★ 官方**也是逐条加** ✓（★ 共 6 条 ✓）
# · ★ 官方例 `Fully_Define_Underdefined_Sketch_Example_CSharp.md`（**73 行** ✓）：★ 正解
# 是
#     ★ **给基准点打 mark（`lMarkHorizontal | lMarkVertical`）+ `InsertSketch` 进出草图** ✓
#     ★ **不是靠堆关系** ✗（★ 这正是用户批评的"过定义" ✗）
# · ★ `ISketchSegment` 成员表：★ **`GetRelationsCount`** ✓（★ 真判据 ✓）· ★ `GetConstrai
# nedStatus` ✓
# ★★ 外部 MIT 项目证据（★ 铁律 1 的合法来源 ✓）：
# · ★ **Slacker-LLC** `CONTRIBUTING.md:56` 逐字：★「★ **`SketchAddConstraints` silently
# ignores a
# string it does…**」✓ ⇒ ★ 它**不校验**、失败也照回 `True` ✗（★ 我第 10 轮实测 13/13 全
# True ✓）
# · ★ **Slacker-LLC** `README.md:227` 逐字：★「★ **`ISketchRelationManager.AddRelation`
# and verifies
#     via the relation count**」✓ ⇒ ★ **正解入口 + 判据** ✓
# 许可:   本仓库 MIT。★ 引用的四家均为 MIT（★ 仅作对照，未抄代码 ✓）。
# 覆盖:   全文件
# ★★ 判据：★★ 每条关系 ⇒ **`GetRelationsCount` 真的 +1** ✓（★ 不看返回码 ✗ —— 本仓事实 8
#  ✓）
#   ★★ 负例 ①：★ 非法关系名 ⇒ `applied: False` ✗ ★ 负例 ②：★ 已完全定义 ⇒ **拒加** ✗
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举（三处离线源逐项比对一致，86/86）
# 文件:   C:/swapi/enums/swConstraintType_e.md
#         AI Solidworks/官方文档/SWhelp/swconst/…swConstraintType_e.html
#         _raw/enum_values_sldworks.txt（`## swConstraintType_e` 段）
# 定位:   RELATION_TYPES 的数值 = 官方 `swConstraintType_e` 逐项照录。
# 覆盖:   只收录**二维草图常用**的官方成员；未收录的即「本表未支持」。
# ★★ 2026-10-08（spec 222）**整表按官方重写**：原表 11 键里 **9 键数值与官方不符**
#   （COINCIDENT 写 0 而官方 9 · PARALLEL 写 8 而官方 7 · PERPENDICULAR 写 9 而官方 8 ·
#    TANGENT 写 10 而官方 6 · CONCENTRIC 写 11 而官方 10 · SYMMETRIC 写 13 而官方 11 ·
#    HORIZONTAL 写 15 而官方 4 · VERTICAL 写 16 而官方 5 · FIXED 写 19 而官方 17），
#   另 2 键（`EQUAL` / `MIDPOINT`）**在官方枚举里根本不存在** ⇒ 改为反别名（见下）。
#   ⇒ ★ 后果：旧表会「**安全地派发一个错误的数值**」—— 加关系后回读计数可能变，
#     但加的不是想要的那个关系。★ 判据见 tests/test_relation_enum_alignment.py。
# ⚠ 本表经**三源静态比对**确认，**未**在本机真机复验（AGENTS.md 铁律 2）。
# ─────────────────────────────────────────────────────────────────────
#: enum-gate: enum swConstraintType_e
#: ★★ 2026-10-12（★ 业主定「先做 A」的第 ② 步）：**补到官方全表**。
#:   ⚠ 改前 **11** 个 ⇒ ★ 缺的**恰恰是把圆弧/距离/角度/椭圆定死用的**
#:     （`DISTANCE` / `ANGLE` / `RADIUS` / `DIAMETER` / `ARCANG*` /
#:      `ELLIPSEANG*` / `COLINEAR` / `CORADIAL` / `ATPIERCE` …）
#:   ★★ 后果：★ 生成器**生成不出**「把圆弧定死」那类关系
#:     ⇒ ★ 而「生成不出来」看起来像「不需要」✓
#:   ★★★ 两处官方源的分工（★ 本轮实测）：
#:     · **官方 VB 示例**只列 **24** 个（★ 是「常用子集」、**不是全表**）
#:     · **枚举页** `C:\swapi\enums\swConstraintType_e.md` 列 **86** 个 ✓
#:     ⇒ ★ 判据：**以枚举页为准**。
#:   ★ 本表由 `output/_fill_all_relation_types.py` 从枚举页**现读生成**。
RELATION_TYPES: dict[str, int] = {
    "ALONGX": 48,
    "ALONGX3D": 64,
    "ALONGXPOINTS": 51,
    "ALONGXPOINTS3D": 66,
    "ALONGY": 49,
    "ALONGY3D": 65,
    "ALONGYPOINTS": 52,
    "ALONGYPOINTS3D": 67,
    "ALONGZ": 50,
    "ALONGZPOINTS": 53,
    "ANGLE": 2,
    "ANGLE3P": 43,
    "ARCANG180": 19,
    "ARCANG270": 20,
    "ARCANG90": 18,
    "ARCANGBOTTOM": 22,
    "ARCANGLEFT": 23,
    "ARCANGRIGHT": 24,
    "ARCANGTOP": 21,
    "ARCLENGTH": 44,
    "ATINTERSECT": 13,
    "ATMIDDLE": 12,
    "ATPIERCE": 40,
    "BELTTRACTION": 69,
    "BLOCKFIXEDLOCK": 70,
    "BLOCKNORMALLOCK": 71,
    "BLOCKROTATELOCK": 72,
    "C3TOUCH": 83,
    "CIRCULARPATTCNT": 77,
    "COINCIDENT": 9,
    "COLINEAR": 27,
    "CONCENTRIC": 10,
    "CONICRHO": 82,
    "CORADIAL": 28,
    "DIAMETER": 15,
    "DISTANCE": 1,
    "DOUBLEANGLE": 84,
    "DOUBLEDISTANCE": 41,
    "ELLIPSEANG180": 34,
    "ELLIPSEANG270": 35,
    "ELLIPSEANG90": 33,
    "ELLIPSEANGBOTTOM": 37,
    "ELLIPSEANGLEFT": 38,
    "ELLIPSEANGRIGHT": 39,
    "ELLIPSEANGTOP": 36,
    "EQUALCURV3DALIGN": 80,
    "EQUALCURVATURE": 61,
    "EQUALTANGENT": 62,
    "FAKESLOTCONSTRAINT": 73,
    "FITSPLINE": 60,
    "FIXED": 17,
    "FIXEDSLOT": 74,
    "FLANGEFACEDIST": 81,
    "HORIZONTAL": 4,
    "HORIZPOINTS": 25,
    "INTERSECTION": 56,
    "INVALIDCTYPE": 0,
    "ISOBYPOINT": 58,
    "LINEARPATTCNT": 76,
    "MERGEPOINTS": 42,
    "NORMAL": 45,
    "NORMALPOINTS": 46,
    "OFFSETEDGE": 16,
    "PARALLEL": 7,
    "PARALLELYZ": 54,
    "PARALLELZX": 55,
    "PATTERNED": 57,
    "PERPENDICULAR": 8,
    "PLANAROFFSET": 79,
    "RADIALOFFSET": 78,
    "RADIUS": 3,
    "SAMECURVELENGTH": 85,
    "SAMEISOPARAM": 59,
    "SAMELENGTH": 14,
    "SAMESLOTS": 75,
    "SKETCHOFFSET": 47,
    "SNAPANGLE": 31,
    "SNAPGRID": 29,
    "SNAPLENGTH": 30,
    "SYMMETRIC": 11,
    "TANGENT": 6,
    "TANGENTFACE": 63,
    "TRACTION": 68,
    "USEEDGE": 32,
    "VERTICAL": 5,
    "VERTPOINTS": 26,
}

#: ★ 旧名 → 官方名。★ **方向单向**：旧名归一为官方名，官方名不会被改写成旧名。
#: ★ 为什么保留旧名：`EQUAL` / `MIDPOINT` 是用户与旧提示词里**已经写下**的词；
#:   直接删掉会把「静默无效」变成「突然报错」，方向虽对但代价高 ⇒ 归一 + 给出官方名。
#: ⚠ 旧名**不得**作为键混进 RELATION_TYPES —— 否则又会被原样派发（测试已钉住）。
LEGACY_ALIASES: dict[str, str] = {
    "EQUAL": "SAMELENGTH",
    "MIDPOINT": "ATMIDDLE",
}

#: ★ 完全定义的状态码（★ 官方 `GetConstrainedStatus` 取值表未公布 ✗ ⇒ ★ 本仓真机两状态读
#: 数 2/3 ✓）
FULLY_DEFINED = 3


def _norm_type(name: Any) -> str | None:
    """★ 归一关系名：★ 大小写无关 · ★ `sg` 前缀可省 ✓；★ 非法回 `None` ✓

    ★ 顺序：① 先查官方成员表 ⇒ ② 再查旧名反别名（**结果仍是官方名**）✓
    ⇒ ★ 调用方拿到的永远是官方成员名，不会把 `EQUAL` 这种官方不存在的名字送进 COM ✓
    """
    raw = str(name or "").strip()
    if not raw:
        return None
    body = raw[2:] if raw.lower().startswith("sg") else raw
    for key in RELATION_TYPES:
        if key.lower() == body.lower():
            return key
    alias = LEGACY_ALIASES.get(body.upper())
    if alias is not None and alias in RELATION_TYPES:
        return alias
    return None


def _val(obj, *names):
    """★ 取 COM 属性/方法 —— ★★ **必须先走 `get_com_member`** ✓（★ 本仓事实：迟到绑定下裸 `getattr`
    取不到成员，而 `sw_part.get_com_member` 专治这个 ✓）；★ 兜底才裸 `getattr` ✓。

    ★★ 这条正是我第 20/25/33 轮取不到 `ISketch.RelationManager` 的**根因** ✗ ——
      ★ 官方成员页逐字：`SketchRelationManager RelationManager {get;}` ✓（★ 一个**属性** ✓），
      ★ 而我用裸 `getattr(sk, "RelationManager")` ✗ ⇒ ★ 永远 `None` ⇒ ★ 只好走 `SketchAddConstraints` 兜底 ✓
    """
    try:
        from sw_part import get_com_member as _gcm
    except Exception:  # noqa: BLE001
        _gcm = None
    for nm in names:
        for getter in (
            (lambda n: _gcm(obj, n)) if _gcm else None,
            (lambda n: getattr(obj, n)),
        ):
            if getter is None:
                continue
            try:
                v = getter(nm)
                return v() if callable(v) else v
            except Exception:  # noqa: BLE001
                continue
    return None


def _seg_count(model) -> int:
    """★ 草图段数（★ 取不到回 -1 ✓）"""
    from sw_sketch import active_sketch as _active

    try:
        sk = _active(model)
    except Exception:  # noqa: BLE001
        sk = None
    if sk is None:
        return -1
    try:
        return len(list(sk.GetSketchSegments or []))
    except Exception:  # noqa: BLE001
        return -1


def _rel_count(model, seg) -> int | None:
    """★ 单段的关系数（★ 官方 `ISketchSegment::GetRelationsCount` ✓ —— **真判据** ✓）"""
    v = _val(seg, "GetRelationsCount", "IGetRelationsCount")
    return int(v) if isinstance(v, (int, float)) else None


def _status(model) -> int | None:
    """★ 草图完全定义状态（★ `ISketch::GetConstrainedStatus` ✓；★ 3 = 完全定义 ✓）"""
    from sw_sketch import active_sketch as _active

    try:
        sk = _active(model)
    except Exception:  # noqa: BLE001
        sk = None
    if sk is None:
        return None
    v = _val(sk, "GetConstrainedStatus", "GetConstrainedStatus2")
    return int(v) if isinstance(v, (int, float)) else None


def _parse_relation(item: Any) -> tuple[str | None, list[int]]:
    """★ 解析一条关系：★ `{"type":…, "targets":["index:2",…]}` 或 ★ `"PARALLEL:2,4"` ✓"""
    if isinstance(item, dict):
        kind = _norm_type(item.get("type") or item.get("relation") or item.get("kind"))
        tgt = item.get("targets") or item.get("indices") or []
        idx = []
        for t in tgt:
            s = str(t)
            s = s.split(":", 1)[1] if s.lower().startswith("index:") else s
            try:
                idx.append(int(s))
            except ValueError:
                return kind, []
        return kind, idx
    if isinstance(item, str):
        if ":" in item:
            head, tail = item.split(":", 1)
            kind = _norm_type(head)
            idx = []
            for s in tail.split(","):
                try:
                    idx.append(int(s.strip()))
                except ValueError:
                    return kind, []
            return kind, idx
    return _norm_type(item), []


def apply_sketch_relations(model, *, relations, verify: bool = True) -> dict[str, Any]:
    """★ 把一整张几何关系清单**一次加全**（★ 本工具专管"加定义" ✓）。

    ★★ 与画圆/画线**同级**：★ 画完一段就调它，★ 一次把该加的关系加全 ✓
    ★★ 判据（★ 不看返回码 ✗）：★ 每条关系 ⇒ **该段 `GetRelationsCount` 真的 +1** ✓
    ★★ 防过定义：★ 若草图**已完全定义** ⇒ **整批拒加** ✗（★ 用户 2026-10-08 的批评 ✓）
    ★ 选段：★ **`index:N`**（★ 声明式 ✓ · ★ 规则 3）+ ★ **`IEntity.Select4`** ✓（★ 事实 32 ✓）
    """
    import sw_part as _sp
    from sw_sketch import active_sketch as _active

    #: ★ 归一清单
    plan: list[dict[str, Any]] = []
    for item in relations or []:
        kind, idx = _parse_relation(item)
        plan.append({"raw": item, "type": kind, "indices": idx})

    #: ★ 前置：★ 要有活动草图 ✓
    try:
        sk = _active(model)
    except Exception:  # noqa: BLE001
        sk = None
    if sk is None:
        return {
            "ok": False,
            "error": "没有活动草图 ⇒ 先 `sketch_start` ✓",
            "applied": 0,
            "total": len(plan),
            "results": [],
        }

    segs = []
    try:
        segs = list(sk.GetSketchSegments or [])
    except Exception:  # noqa: BLE001
        pass

    #: ★★ 防过定义：★ 已完全定义就不再加 ✓
    #: ★★★ 2026-10-08 闸门修正（★ 用户 2026-10-08 截图指出"关系加得根本不对"✗）
    #:   ★★ 官方取值表 **逐字**（`C:\swapi\enums\swConstrainedStatus_e.md` ✓，7 个成员）：
    #:     ★ 1 `swUnknownConstraint` · ★ **2 `swUnderConstrained`（欠定义）** ✓ ·
    #: ★ **3 `swFullyConstrained`（完全定义）** ✓ · ★ **4 `swOverConstrained`（过定义）*
    #: * ✗ ·
    #: ★ 5 `swNoSolution`（无解）✗ · ★ 6 `swInvalidSolution`（无效）✗ · ★ 7 `swAutosolve
    #: Off` ✓
    #:   ★★ 现场铁证：★ 我真机读到的正是 **`status = 4`** ✗，★ 而截图上出现
    #:     **红「项目无法解出」+ 黄「项目冲突」** ✗ ⇒ ★ 我先前**只拦 `== 3`** ✗ ⇒
    #:     ★★ **在已经过定义（4）的草图上还继续加** ✗ ⇒ **越加越坏** ✓
    #: ★★★ 正确规则：★★ **只有 `status == 2`（欠定义）才允许加关系** ✓ —— ★ 其余全部**拒
    #: 加并说明** ✗
    _status_name = {
        1: "swUnknownConstraint",
        2: "swUnderConstrained",
        3: "swFullyConstrained",
        4: "swOverConstrained",
        5: "swNoSolution",
        6: "swInvalidSolution",
        7: "swAutosolveOff",
    }
    addable_status_ = 2  #: ★★ **唯一允许加关系的状态** ✓
    # State validation is mandatory even when optional post-verification is disabled.
    st0 = _status(model)
    if st0 != addable_status_:
        why = {
            3: "★ 已**完全定义** ⇒ 再加必过定义 ✗",
            4: "★ 已**过定义**（`swOverConstrained`）⇒ **不能再加**，★ 必须先撤销多余关系 ✗",
            5: "★ 草图**无解**（`swNoSolution`）⇒ 先修草图 ✗",
            6: "★ 草图**解无效**（`swInvalidSolution`）⇒ 先修草图 ✗",
        }.get(st0, "★ 非欠定义状态 ⇒ 不擅自加 ✗")
        return {
            "ok": False,
            "refused": _status_name.get(st0, "status=%r" % (st0,)),
            "status_before": st0,
            "addable_status": addable_status_,
            "error": "草图状态为 **%s（%r）**：%s —— ★ **只有 `status == 2`（欠定义）才允许加关系** ✓"
            % (_status_name.get(st0, "未知"), st0, why),
            "applied": 0,
            "total": len(plan),
            "results": [],
        }

    #: ★ 关系管理器（★ 正解入口 ✓ —— Slacker-LLC 逐字：★ `ISketchRelationManager.AddRela
    #: tion` ✓）
    #: ★ 关系管理器（★ 正解入口 ✓）—— ★★ 官方成员页**逐字**（`C:\swapi\types\ISketch\Rel
    #: ationManager.md` ✓）：
    #:   ★ `**Signature**: SketchRelationManager RelationManager {get;}` ✓
    #: ⇒ ★★ **它是 `ISketch` 上的一个属性，★ 名字就叫 `RelationManager`** ✓
    #:   ★★ 官方例 `Get_Sketch_Relations_Example_CSharp.md` 第 51 行逐字：
    #:     ★ `swSkRelMgr = swSketch.RelationManager;` ✓
    #:   ★★ 我第 20/25 轮试的是 `GetSketchRelationManager` ✗ 与 `SketchRelationManager` ✗
    #:     ⇒ ★ **一个不存在、一个差前缀** ✗ ⇒ ★ **永远取不到，只好走兜底** ✓；★ 本行修正 ✓
    mgr = None
    _probe = {}
    for path in (
        "RelationManager",
        "GetSketchRelationManager",
        "SketchRelationManager",
    ):
        try:
            from sw_part import get_com_member as _gcm

            _g = _gcm(sk, path)
        except Exception as exc:  # noqa: BLE001
            _g = None
            _probe[path] = "gcm✗%s: %s" % (type(exc).__name__, str(exc)[:70])
        else:
            _probe[path] = "gcm=%r" % (type(_g),)
        try:
            _a = getattr(sk, path)
        except Exception as exc:  # noqa: BLE001
            _a = None
            _probe[path] = _probe.get(path, "") + " | attr✗%s" % type(exc).__name__
        mgr = _g if _g is not None else _a
        if mgr is not None:
            _probe["★ 命中"] = path
            break
    #: ★★★ 第 43 轮：★ 把取值过程**打在工具里面** ✗ —— 第 38 轮的旁路诊断说"取得到" ✓，
    #:   而第 42 轮证明工具里 `mgr is None` ✗ ⇒ ★ 两边差别只能靠**工具自己开口**才看得见 ✓
    print("★ [诊断] type(sk)=%r · mgr=%r · 过程=%r" % (type(sk), type(mgr), _probe))

    # Select the route before dispatch. Never probe a mutating member with no args.
    # get_com_member_raw in sw_connect has the same get-only contract.
    add_relation = None
    if mgr is not None:
        try:
            candidate = getattr(mgr, "AddRelation")
        except Exception:  # Member resolution happened before any mutation.
            candidate = None
        if callable(candidate):
            add_relation = candidate

    results: list[dict[str, Any]] = []
    applied = 0
    uncertain = False
    for rec in plan:
        kind, idx = rec["type"], rec["indices"]
        entry: dict[str, Any] = {
            "raw": rec["raw"],
            "type": kind,
            "indices": idx,
            "applied": False,
        }
        if uncertain:
            entry.update(
                execution_state="not_started",
                effect_status="unknown",
                error="A previous relation has uncertain execution; batch stopped.",
            )
            results.append(entry)
            continue
        if kind is None:
            _alias_hint = ""
            _raw_body = str(rec["raw"] or "").strip()
            _raw_body = (
                _raw_body[2:] if _raw_body.lower().startswith("sg") else _raw_body
            )
            _suggest = LEGACY_ALIASES.get(_raw_body.upper())
            if _suggest:
                _alias_hint = " ★ 官方对应名为 **%s**（官方枚举里**没有** %s）✓" % (
                    _suggest,
                    _raw_body,
                )
            entry["error"] = (
                "非法关系名 %r ⇒ ★ 官方 `SketchAddConstraints` 会**静默回 True** 而"
                "不加任何关系 ✗；★ 合法值：%s%s"
                % (rec["raw"], sorted(RELATION_TYPES), _alias_hint)
            )
            results.append(entry)
            continue
        if len(idx) < 2 or any(i < 0 or i >= len(segs) for i in idx):
            entry["error"] = "段序号非法：%r（共 %d 段）" % (idx, len(segs))
            results.append(entry)
            continue

        #: ★ 选段（★ index:N + Select4 ✓）
        try:
            model.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        grabbed = 0
        for k, i in enumerate(idx):
            try:
                if segs[i].Select4(bool(k > 0), _sp._empty_callout()):
                    grabbed += 1
            except Exception:  # noqa: BLE001
                pass
        entry["selected"] = grabbed
        if grabbed != len(idx):
            entry.update(
                execution_state="rejected",
                effect_status="unknown",
                error="Incomplete entity selection; no relation was dispatched.",
            )
            results.append(entry)
            continue

        # A trustworthy pre-state is required before any non-idempotent dispatch.
        before = _rel_count(model, segs[idx[0]])
        if before is None:
            entry.update(
                execution_state="rejected",
                effect_status="unknown",
                error="Pre-dispatch relation count unavailable; no mutation attempted.",
            )
            results.append(entry)
            continue

        #: ★ 入口 ①（正解）：★ `ISketchRelationManager::AddRelation` ✓
        #: ★★ 官方签名**逐字**（`C:\swapi\types\ISketchRelationManager\AddRelation.md` ✓
        #: ）：
        #: ★ `SketchRelation AddRelation( System.object Entities, System.int RelationTyp
        #: e )`
        #:   ⇒ ★★ **两个形参**：★ `Entities` = **"Array of entities"**（★ 实体数组 ✓）
        #:     + ★ `RelationType` = `swConstraintType_e` 数值 ✓
        #:   ★★ 我第 20 轮只传了**一个**参数 ✗ ⇒ 取不到 ⇒ 自动走兜底 ✓；★ 本轮补齐 ✓
        # Source: specs/081 and sketch_relations._dispatch_array, repository MIT.
        # AddRelation(Object, Int32) differs from IAddRelation(Int32, Object&, Int32).
        # 0x80010105 is RPC_E_SERVERFAULT, not RPC_E_SERVERCALL_RETRYLATER.
        # An exception does not prove that a non-idempotent mutation did not happen.
        if add_relation is not None:
            try:
                from sketch_relations import _dispatch_array

                payload = _dispatch_array([segs[i] for i in idx])
            except Exception as exc:
                entry.update(
                    execution_state="rejected",
                    effect_status="unknown",
                    error="Entity array preparation failed before dispatch: %s"
                    % str(exc)[:110],
                )
                results.append(entry)
                continue
            via = "ISketchRelationManager::AddRelation"
            dispatch = lambda: add_relation(payload, RELATION_TYPES[kind])
        else:
            # Fallback is chosen BEFORE dispatch, never after an ambiguous call.
            via = "SketchAddConstraints"
            dispatch = lambda: model.SketchAddConstraints("sg" + kind)

        dispatch_error = None
        try:
            dispatch()
        except Exception as exc:
            dispatch_error = str(exc)[:130]
            entry["error"] = dispatch_error
            if add_relation is not None:
                entry["mgr_error"] = dispatch_error
        after = _rel_count(model, segs[idx[0]])
        uncertain = dispatch_error is not None or after is None
        entry["via"] = via
        entry["relations_count"] = [before, after if verify else None]
        entry["execution_state"] = "uncertain" if uncertain else "returned"
        # A count increase is only count evidence, not complete geometric proof.
        count_increased = isinstance(after, int) and after > before
        entry["relation_count_status"] = (
            "unknown"
            if uncertain or not verify
            else ("pass" if count_increased else "fail")
        )
        # Type, entities, geometry and persistence are not independently inspected.
        entry["effect_status"] = (
            "fail" if verify and not uncertain and not count_increased else "unknown"
        )
        entry["applied"] = bool(verify and count_increased and not uncertain)
        if not entry["applied"] and "error" not in entry:
            entry["error"] = (
                "Relation effect unavailable or not confirmed (%r -> %r); no replay."
                % (before, after)
            )
        if entry["applied"]:
            applied += 1
        results.append(entry)
        try:
            model.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass

    st1 = _status(model) if verify else None
    return {
        "ok": applied == len(plan) and len(plan) > 0,
        "execution_state": "uncertain" if uncertain else "returned",
        "applied": applied,
        "total": len(plan),
        "status_before": st0,
        "status_after": st1,
        "over_defined_guard": "★ 已完全定义时**拒加** ✓",
        "criterion": "★★ 每条 ⇒ `ISketchSegment::GetRelationsCount` **+1** ✓（不看返回码 ✗）",
        "sources": (
            "★ 官方 Constrain_Sketch 例（逐条加 ✓）· ★ Slacker-LLC："
            "`AddRelation` + 关系数回读 ✓"
        ),
        "results": results,
    }
