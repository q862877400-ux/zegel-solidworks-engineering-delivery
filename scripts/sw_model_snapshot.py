"""示教器的**记录器**：把 SolidWorks 文档的当前状态**原样、完整**地读成结构化数据。

## 职责边界（业主 2026-10-26 明确纠正）

> 它就是一个动作的记录，而且要记录得特别特别全，各种场景都能记录，
> 而提炼这一步就交给使用这个工具的 agent 进行，你千万不要把我们这个示教器越搞越复杂。

⇒ 本模块**只记录**：不推断意图、不提炼规则、不建配方、不下结论。
   输出是**原始事实**，够 agent 用它推出任何东西。

## 记什么

```
零件  features[]（类型）
      sketches[]（点 / 线段含直线·弧·椭圆·样条 / **构造线标记** /
                  关系与尺寸的**参照实体** / 求解状态）
      自定义属性 / 参考几何 / 实体（面数·圆柱面数）
装配  components[]（名称/路径/压缩/变换矩阵）
      mates[]（类型 swMateType_e / 对齐 swMateAlign_e / 参与实体）
图样  views[]
通用  文档类型、路径、配置名
```

★ 每个字段都**独立取**并容错：读不到就写 `"读不到"` 或 `None`，
  **绝不因为一个字段失败而丢掉整份记录**，也绝不编一个看起来合理的值。

## 实体描述器（`describe_entity`）

按**自身特征**判断（不看 `IEntity.GetType()` —— 实测它对本机所有实体都返回 0）：

```
有 X/Y                  ⇒ 草图点（附类型 int）
有 GetStartPoint2/End   ⇒ 草图线段（直线/弧/椭圆/样条 + **是否构造**）
有 GetStartVertex/End   ⇒ 实体边（给两端点坐标）
有 GetEdges             ⇒ 面
有 GetPoint             ⇒ 顶点
都判不出                ⇒ 明确标「未识别」并留下能拿到的标识
```
"""
from __future__ import annotations

from sw_enums import (
    CONSTRAINT_TYPE as _CONSTRAINT_RAW,
)
from sw_enums import (
    CONSTRAINT_TYPE_ZH as _CONSTRAINT_ZH,
)
from sw_enums import (
    DOC_KIND as _DOC_RAW,
)
from sw_enums import (
    DOC_KIND_ZH as _DOC_ZH,
)
from sw_enums import (
    MATE_ALIGN as _MATE_ALIGN_RAW,
)
from sw_enums import (
    MATE_ALIGN_ZH as _MATE_ALIGN_ZH,
)
from sw_enums import (
    MATE_TYPE as _MATE_TYPE_RAW,
)
from sw_enums import (
    MATE_TYPE_ZH as _MATE_TYPE_ZH,
)
from sw_enums import (
    SEGMENT_KIND as _SEG_RAW,
)
from sw_enums import (
    SEGMENT_KIND_ZH as _SEG_ZH,
)
from sw_enums import (
    SKETCH_POINT_TYPE as _SPT_RAW,
)

#: `swMateType_e`（官方枚举，逐条核过 `C:\swapi\enums\swMateType_e.md`）
#: ★★★ 枚举一律来自 scripts/sw_enums.py（由 tools/gen_sw_enums.py 从
#:   C:/swapi/enums/*.md **生成**），这里**不再手抄任何表**。
#:   教训：手抄 swConstraintType_e 把 7/8 抄错 ⇒ 业主的「平行/垂直」被记成
#:   「相切/同心」，是**假事实**。见 AGENTS.md 与事实 592。
from sw_units import dimension_reading


def _strip(d: dict, *prefixes: str) -> dict:
    """把生成表的成员名去掉前缀，只留值名（便于人读）。

    ★ 前缀**不统一**，必须多给几个候选（实测）：
      swConstraintType_PARALLEL → 前缀 swConstraintType
      swMateAlignALIGNED        → 前缀 swMateAlign（**不是** swAlign）
      swSketchLINE              → 前缀 swSketch
      swDocPART                 → 前缀 swDoc
    只给一个前缀会剥不掉，值名原样带着前缀（实测踩过：MATE_ALIGN[0] 成了
    swMateAlignALIGNED）。
    """
    out = {}
    for k, v in d.items():
        name = v
        #: 长的优先，避免 swMate 先命中 swMateAlignXXX
        for cand in sorted(prefixes, key=len, reverse=True):
            if name.startswith(cand):
                name = name[len(cand):]
                break
        out[k] = name.lstrip("_")
    return out


CONSTRAINT = _strip(_CONSTRAINT_RAW, "swConstraintType_", "swConstraintType")
MATE_TYPE = _strip(_MATE_TYPE_RAW, "swMateType_", "swMateType", "swMate")
MATE_ALIGN = _strip(_MATE_ALIGN_RAW, "swMateAlign", "swAlign")
SEGMENT_KIND = _strip(_SEG_RAW, "swSketchSegments_", "swSketch")
DOC_KIND = _strip(_DOC_RAW, "swDoc")
SKETCH_POINT_KIND = _strip(_SPT_RAW, "swSketchPointType_", "swSketchPointType")

#: 中文标签（只给已真机核过的值；缺的不猜）
CONSTRAINT_ZH = dict(_CONSTRAINT_ZH)
MATE_TYPE_ZH = dict(_MATE_TYPE_ZH)
MATE_ALIGN_ZH = dict(_MATE_ALIGN_ZH)
SEGMENT_KIND_ZH = dict(_SEG_ZH)
DOC_KIND_ZH = dict(_DOC_ZH)

#: ★★★ 角度类关系 —— **量纲不同**：GetSystemValue2 对它们回**弧度**，不是米。
#:   ⚠ 只收**已真机实测**的：2 = ANGLE（实测 0.785398 ⇒ 45°，事实 587/592）。
#:   ARCANG* / ANGLE3P 等虽然名字里有 ANGLE，但**未实测其 GetSystemValue2 的量纲**
#:   ⇒ 不放进本集合，改用 ANGLE_TYPES_UNVERIFIED 标出来，取到值时同时标「单位未验证」。
ANGLE_TYPES = {2}
ANGLE_TYPES_UNVERIFIED = {k for k, v in CONSTRAINT.items()
                          if "ANGLE" in v and k not in ANGLE_TYPES}
#: 长度类（GetSystemValue2 回**米**）—— 只收已实测的三种
LENGTH_TYPES = {1, 3, 15}     #: DISTANCE / RADIUS / DIAMETER

#: 「读不到」的统一写法 —— **不许**用空值/0 冒充「读到了」。
NA = "读不到"
#: 长度换算：**米 → 毫米**（只用于长度；角度走 sw_units.rad_to_deg）

#: ★ 文档类型中文（人读版要用中文；生成表给的是英文成员名）
DOC_KIND = {1: "零件", 2: "装配", 3: "图样"}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 · 全场景记录器）
# 文件:   scripts/sw_model_snapshot.py
# 定位:   把 SolidWorks 文档（零件/装配/图样）的当前状态**原样完整**读成结构化数据。
#          只记录不推断 —— 提炼规则是使用工具的 agent 的事（业主 2026-10-26 纠正）。
# 官方依据: IModelDoc2.FirstFeature/GetNextFeature/GetType/GetPathName ·
#          IFeature.GetTypeName2/GetSpecificFeature2 ·
#          ISketch.GetConstrainedStatus/GetSketchPoints2/GetSketchSegments ·
#          ISketchSegment.ConstructionGeometry · ISketchPoint.X/Y/Z/Type ·
#          ISketchRelation.GetRelationType/GetEntities/GetDisplayDimension ·
#          IDisplayDimension.GetDimension2 · IDimension.GetSystemValue2(配置名) ·
#          IAssemblyDoc.GetComponents · IComponent2.Name2/GetPathName/Transform2 ·
#          IMate2.Type/MateEntity/Alignment（配合须经「Mate 特征 → 取 IMate2」；
#          官方**没有** IAssemblyDoc.GetMates，已核实）·
#          IEdge.GetStartVertex/GetEndVertex · IVertex.GetPoint · IFace2.GetEdges ·
#          ISurface.IsCylinder（**属性**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


#: dispatch-guard: exempt internal-helper
def _g(obj, name, *args):
    """取 COM 成员：有实参就调用；取不到返回 None（不抛）。"""
    if obj is None:
        return None
    try:
        from sw_connect import get_com_member

        return get_com_member(obj, name, *args)
    except Exception:  # noqa: BLE001
        return None


def _tc(*args, **kwargs):
    """调本仓 try_call（失败不抛，回 (ok, 值)）。"""
    from sw_connect import try_call

    return try_call(*args, **kwargs)


def _mm(v) -> float:
    """米 → 毫米（COM 长度一律米）。"""
    return round(float(v) * 1000.0, 3)


def _int(v):
    return int(v) if isinstance(v, int) else None


# ── 实体描述（核心：把「你选了什么」记清楚）─────────────────────────
def describe_entity(ent) -> dict:
    """实体描述：类型 / 坐标或端点 / 构造标记 / 曲线信息。**判不出就如实说**。"""
    d: dict = {"kind": "未识别"}

    #: ① 草图点（有 X/Y）
    x = _g(ent, "X")
    y = _g(ent, "Y")
    if x is not None and y is not None:
        d["kind"] = "草图点"
        z = _g(ent, "Z")
        d["point_mm"] = [_mm(x), _mm(y), _mm(z) if z is not None else None]
        t = _g(ent, "Type")
        if isinstance(t, int):
            d["point_type_int"] = t
        return d

    #: ② 草图线段（有 GetStartPoint2 / GetEndPoint2）
    sp = _g(ent, "GetStartPoint2")
    ep = _g(ent, "GetEndPoint2")
    if sp is not None and ep is not None:
        d["kind"] = "草图线段"
        d["endpoints_mm"] = [
            [_mm(_g(sp, "X")), _mm(_g(sp, "Y"))],
            [_mm(_g(ep, "X")), _mm(_g(ep, "Y"))],
        ]
        cg = _g(ent, "ConstructionGeometry")
        if cg is not None:
            d["construction"] = bool(cg)
        d.update(_segment_shape(ent))
        return d

    #: ③ 实体边（有 GetStartVertex / GetEndVertex）
    vs = _g(ent, "GetStartVertex")
    ve = _g(ent, "GetEndVertex")
    if vs is not None or ve is not None:
        d["kind"] = "实体边"
        for tag, vtx in (("start", vs), ("end", ve)):
            if vtx is None:
                continue
            p = _g(vtx, "GetPoint")
            if p is not None:
                q = list(p)
                if len(q) >= 3:
                    d[f"{tag}_mm"] = [_mm(q[0]), _mm(q[1]), _mm(q[2])]
        return d

    #: ④ 面（有 GetEdges）
    if _g(ent, "GetEdges") is not None:
        d["kind"] = "面"
        return d

    #: ⑤ 顶点（有 GetPoint）
    p = _g(ent, "GetPoint")
    if p is not None:
        q = list(p)
        if len(q) >= 3:
            d["kind"] = "顶点"
            d["point_mm"] = [_mm(q[0]), _mm(q[1]), _mm(q[2])]
            return d

    #: ⑥ 兜底：留下能拿到的标识，便于 agent 事后判断（不编类型）
    for name in ("GetTypeName2", "GetClassName"):
        #: dispatch-fwd: probe 试名探测：这两个都不是万能成员，能取到哪个算哪个
        v = _g(ent, name)
        if v:
            d[name] = str(v)[:120]
    return d


def _segment_shape(seg) -> dict:
    """线段再细分：直线 / 圆弧 / 椭圆 / 样条（按可用成员判断，不猜）。"""
    out: dict = {}
    t = _g(seg, "GetType")
    if isinstance(t, int) and t in SEGMENT_KIND:
        #: 官方成员名（LINE/ARC…）+ 中文标签都给，人读用中文、机器用英文
        out["shape"] = SEGMENT_KIND_ZH.get(t) or SEGMENT_KIND[t]
        out["shape_official"] = SEGMENT_KIND[t]
    c = _g(seg, "GetCenterPoint2")
    if c is not None:
        out["center_mm"] = [_mm(_g(c, "X")), _mm(_g(c, "Y"))]
        r = _g(seg, "Radius")
        if r is not None:
            out["radius_mm"] = _mm(r)
        out.setdefault("shape", "圆弧/椭圆")
    n = _g(seg, "GetPointCount")
    if isinstance(n, int):
        out["spline_point_count"] = n
        out.setdefault("shape", "样条")
    out.setdefault("shape", "直线")
    return out


# ── 草图 ─────────────────────────────────────────────────────────────
def sketch_detail(sketch_feature) -> dict:
    """一张草图的**全部内容**：点、线段（含构造标记）、关系与尺寸（含参照实体）。"""
    out: dict = {"name": str(_g(sketch_feature, "Name") or "")}
    sk = _g(sketch_feature, "GetSpecificFeature2")
    if sk is None:
        out["error"] = "草图对象取不到"
        return out

    st = _int(_g(sk, "GetConstrainedStatus"))
    out["constrained"] = st
    out["constrained_meaning"] = {2: "欠定义", 3: "完全定义"}.get(st, "其它/未知")

    #: ★★★ 根因 F：**「草图点」有两种，不能混**
    #:   · GetUserPoints2()  ⇒ **用户显式画的点**（真正的「点」实体）
    #:   · GetSketchPoints2() ⇒ **全部点**，含每条线段的端点（内部点）
    #:   实测业主那张草图：GetSketchPoints2 回 6 个（其中 5 个 Internal=线段端点），
    #:   GetUserPoints2 只回 1 个 ⇒ 说「6 个点」是错的，
    #: ⚠ GetUserPoints2 **不返回点对象**，它返回 **doubles 数组**，
    #:   每 7 个一组（官方 Remarks 逐字）：
    #:   [Color, Line Font, Line Width, Layer ID, Layer Override, ptLoc[3]]
    #:   ⇒ 坐标从每组第 6~8 个取。第一版当它是点对象，直接崩了。
    raw_pts = list(_g(sk, "GetUserPoints2") or ())
    user_pts = []
    step = 7
    for i in range(0, len(raw_pts) - step + 1, step):
        xyz = raw_pts[i + 5:i + 8]
        try:
            user_pts.append({"x_mm": _mm(float(xyz[0])),
                             "y_mm": _mm(float(xyz[1])),
                             "z_mm": _mm(float(xyz[2])) if len(xyz) > 2 else None})
        except (TypeError, ValueError, IndexError):
            continue
    out["user_point_count"] = len(user_pts)
    out["user_points"] = user_pts

    pts = []
    for sp in list(_g(sk, "GetSketchPoints2") or ()):
        item = {"x_mm": _mm(_g(sp, "X")), "y_mm": _mm(_g(sp, "Y"))}
        t = _int(_g(sp, "Type"))
        if t is not None:
            item["type_int"] = t
            #: ★★★ 根因 F：**区分系统元素与用户元素**，不让下游去猜。
            #:   `ISketchPoint.Type` 回 `swSketchPointType_e`（由生成表提供）：
            #:   1 = User（用户）· 8 = Origin（原点）· 10 = External（外部）
            #:   ⇒ 业主那张草图有 6 个点，其中 1 个是**原点**，只有 5 个是他自己画的。
            #:     不标出来，下游会把点数数错（实测踩过）。
            item["kind"] = SKETCH_POINT_KIND.get(t, f"未登记({t})")
            item["is_user"] = t == 1
            item["is_origin"] = t == 8
            item["is_external"] = t == 10
        pts.append(item)
    out["points"] = pts
    out["all_point_count"] = len(pts)
    out["points_note"] = (
        "points = GetSketchPoints2 的**全部点**（含线段端点）；"
        "user_points = GetUserPoints2 的**用户画点**。别把两者混算。")
    out["has_origin"] = any(p.get("is_origin") for p in pts)

    segs = []
    for seg in list(_g(sk, "GetSketchSegments") or ()):
        item = _segment_shape(seg)
        cg = _g(seg, "ConstructionGeometry")
        item["construction"] = bool(cg) if cg is not None else None
        a = _g(seg, "GetStartPoint2")
        b = _g(seg, "GetEndPoint2")
        if a is not None and b is not None:
            item["endpoints_mm"] = [
                [_mm(_g(a, "X")), _mm(_g(a, "Y"))],
                [_mm(_g(b, "X")), _mm(_g(b, "Y"))],
            ]
        segs.append(item)
    out["segments"] = segs

    rels = []
    rm = _g(sk, "RelationManager")
    if rm is not None:
        out["relation_count"] = _int(_g(rm, "GetRelationsCount", 0))
        for rel in list(_g(rm, "GetRelations", 0) or ()):
            item: dict = {}
            rt = _int(_g(rel, "GetRelationType"))
            item["type_int"] = rt
            item["type"] = CONSTRAINT.get(rt, f"未登记({rt})")
            item["entities"] = [describe_entity(e)
                                for e in list(_g(rel, "GetEntities") or ())]
            dd = _g(rel, "GetDisplayDimension")
            if dd is not None:
                dim = _g(dd, "GetDimension2", 0)
                if dim is not None:
                    #: ★★★ 数值一律走 sw_units.dimension_reading —— 它**按关系类型
                    #:   决定量纲**（长度 → value_mm；角度 → value_rad/value_deg；
                    #:   未实测 → unit_unverified）。本文件**不允许**自己写
                    #:   GetSystemValue2 + 乘 1000：那正是「角度被当长度」那个
                    #:   假数值事故的根因（事实 592）。
                    item.update(dimension_reading(dim, item.get("type_int")))
            rels.append(item)
    out["relations"] = rels
    #: ★ 草图级「外部/投影引用」计数：关系类型 32 = USEEDGE（转换实体）
    use_edge = [r for r in rels if r.get("type_int") == 32]
    out["use_edge_count"] = len(use_edge)
    if use_edge:
        out["use_edge_entities"] = [
            [e.get("kind") for e in (r.get("entities") or [])] for r in use_edge
        ]
    return out


# ── 零件 ─────────────────────────────────────────────────────────────
def feature_params(doc, feature) -> dict:
    """特征的**关键参数**（拉伸深度 / 孔规格 / 阵列间距 / 圆角半径…）。

    ★ 复用本仓既有 typed readers（sw_feature_readback 里的
      xtrude_params/hole_params/pattern_params/
illet_params），不重造；
      读不到就返回空 dict（**不编数值**）。
    """
    name = str(_g(feature, "Name") or "")
    tp = str(_g(feature, "GetTypeName2") or "")
    try:
        from sw_feature_readback import (
            extrude_params,
            fillet_params,
            hole_params,
            pattern_params,
        )
    except Exception:  # noqa: BLE001
        return {}
    reader = None
    if tp in ("Extrusion", "ExtrusionThin", "BossThin", "Cut", "CutThin"):
        reader = extrude_params
    elif tp == "HoleWzd":
        reader = hole_params
    elif "Pattern" in tp:
        reader = pattern_params
    elif tp in ("Fillet", "Chamfer"):
        reader = fillet_params
    if reader is None:
        return {}
    try:
        raw = reader(doc, name) or {}
    except Exception:  # noqa: BLE001
        return {}
    #: ★★★ 根因 G：**「口径说明」不许混进数据里**。
    #:   原来我把上游返回的东西整个塞进来，其中既有**值**（GetDepth: 0.025）又有
    #:   **手写的口径字符串**（★_单位口径: 'document（真机：20mm ⇒ 20.0）'）——
    #:   两者不同步就成了**假标注**：值是 0.025 米，口径却说「20mm ⇒ 20.0」。
    #:   现在：① 所有 ★* / _* 内部说明键一律丢掉（口径写进本函数 docstring）；
    #:        ② 长度类数值**按官方口径换算后改名带单位**。
    out = {}
    for k, v in raw.items():
        key = str(k)
        if key.startswith(("_", "★")):
            continue
        if key in ("definition", "feature"):
            continue
        if v in (None, "", [], {}):
            continue
        out.update(_param_with_unit(key, v))
    return out


#: 上游返回的**长度类**键名（值单位是米，官方口径）→ 换成带 _mm 后缀的键名
_LENGTH_KEYS = {
    "GetDepth": "depth_mm",
    "GetDraftAngle": "draft_angle_deg",
}


def _param_with_unit(key: str, value):
    """把一个上游参数**按量纲改名并换算**，回 {新键: 值}。

    ★ 只管**已知道量纲**的键（见 _LENGTH_KEYS，其口径来自
      IExtrudeFeatureData2.GetDepth 的官方 Remarks：**米**）。
      不认识的键**原样保留、不加单位后缀**，因为不知道量纲时加后缀就等于猜。

    ★ 嵌套 dict 要**递归**：实测上游把拉伸参数装成
      `forward = {"GetDepth": 0.025, "GetDraftAngle": 0.0, ...}`；
      第一版只处理顶层，嵌套里的 `GetDepth` 依旧以米出现 —— 等于没修。
    """
    if isinstance(value, dict):
        nested = {}
        for kk, vv in value.items():
            nested.update(_param_with_unit(kk, vv))
        return {key: nested}
    target = _LENGTH_KEYS.get(key)
    if target is None:
        return {key: value if isinstance(value, (int, float, bool, str))
                else str(value)[:120]}
    if not isinstance(value, (int, float)):
        return {target: str(value)[:120]}
    if target.endswith("_mm"):
        try:
            return {target: round(float(value) * 1000.0, 4)}
        except (TypeError, ValueError):
            return {target: None}
    if target.endswith("_deg"):
        try:
            import math as _math

            return {target: round(_math.degrees(float(value)), 4)}
        except (TypeError, ValueError):
            return {target: None}
    return {target: value}


def _sketch_key(sk: dict) -> tuple:
    """草图的**内容指纹**（用于识别「同一张草图在特征树里出现两次」）。"""
    return (str(sk.get("name")),
            sk.get("constrained"),
            len(sk.get("points") or []),
            len(sk.get("segments") or []),
            len(sk.get("relations") or []))


def _merge_sketch_duplicate(acc: list, sk: dict) -> None:
    """★ SolidWorks 会把**同一张草图**同时作为顶层特征和某个特征的子特征暴露出来
    （实测：草图1 顶层一次 + 凸台-拉伸1 下再一次，内容完全相同）。

    这不是数据错，但下游会误当成两张草图 ⇒ 这里合并：
    保留**顶层那份**（owner 为空），把另一处的 owner 记进 lso_owned_by。
    """
    key = _sketch_key(sk)
    for i, prev in enumerate(acc):
        if prev is sk or _sketch_key(prev) != key:
            continue
        #: 同一张：优先保留 owner 为空的（顶层）
        keep, drop = (prev, sk) if not prev.get("owner") else (sk, prev)
        others = list(keep.get("also_owned_by") or [])
        if drop.get("owner") and drop["owner"] not in others:
            others.append(drop["owner"])
        keep["also_owned_by"] = others or None
        acc[acc.index(drop)] = keep
        if drop is sk:
            acc.pop()
        return


def _bodies_of(doc, component=None) -> tuple:
    """回 (实体列表, 取数来源说明)。

    ★ 顺序即优先级：
      ① 传了组件 ⇒ IComponent2.GetBodies2(BodyType)（**1 参**）；
      ② 否则 IPartDoc.GetBodies2(BodyType, BVisibleOnly)（**2 参**）；
      ③ 再退 IBody2 单实体入口 GetBody()。
    两次都失败时**如实写来源=读不到**，不写空数组冒充「没有实体」。
    """
    if component is not None:
        got = _g(component, "GetBodies2", 0)
        if got is not None:
            return list(got), "IComponent2.GetBodies2(1 参)"
    try:
        got = doc.GetBodies2(0, False)
        if got is not None:
            return list(got), "IPartDoc.GetBodies2(2 参)"
    except Exception:  # noqa: BLE001
        pass
    one = _g(doc, "GetBody")
    if one is not None:
        return [one], "GetBody() 单实体兜底"
    return [], "读不到（该上下文下 GetBodies2 不可用且无 GetBody）"


def dump_part(doc, component=None) -> dict:
    """零件：特征树 + 每张草图 + 实体统计 + 自定义属性 + 参考几何。

    :param component: 若这份零件是**装配里的组件**，传 IComponent2 进来。

    ★★★ 为什么需要它（根因 E：几何取数要区分上下文）
      在装配体里，组件内零件文档的 IPartDoc.GetBodies2(0, False) 会**抛异常**
      （实测 com_error），于是 odies 记成空数组 —— 下游看到「没有实体」，
      而实际有实体。同一份几何只能从**组件**问：
      IComponent2.GetBodies2(BodyType)（注意：**1 个参数**，与 IPartDoc 的 2 个不同）。
    """
    out: dict = {"features": [], "sketches": [], "bodies": []}

    for feat, owner, level in walk_features(doc):
        tp = str(_g(feat, "GetTypeName2") or "")
        item = {
            "name": str(_g(feat, "Name") or ""), "type": tp,
            "owner": owner or None, "level": level,
        }
        params = feature_params(doc, feat)
        if params:
            item["params"] = params
        out["features"].append(item)
        if tp == "ProfileFeature":
            sk = sketch_detail(feat)
            sk["owner"] = owner or None      #: 孔内草图要能看出挂在哪个孔特征下
            out["sketches"].append(sk)
            _merge_sketch_duplicate(out["sketches"], sk)

    bodies, bodies_source = _bodies_of(doc, component)
    out["bodies_source"] = bodies_source
    for body in bodies:
        faces = list(_g(body, "GetFaces") or ())
        cyl = 0
        for face in faces:
            surf = _g(face, "GetSurface")
            if surf is None:
                continue
            try:
                cyl += 1 if bool(surf.IsCylinder) else 0
            except Exception:  # noqa: BLE001
                pass
        out["bodies"].append({"face_count": len(faces), "cylinder_faces": cyl})

    out["custom_properties"] = _custom_properties(doc)
    out["reference_geometry"] = [
        {"name": x["name"], "type": x["type"]} for x in out["features"]
        if x["type"] in ("RefPlane", "RefAxis", "OriginProfileFeature", "RefPoint")
    ]
    return out


def walk_features(doc) -> list:
    """**递归**遍历全部特征（含子特征），回 [(feature, owner_name, depth)]。

    ★ 必须递归：孔特征的定位/轮廓草图是**子特征**；装配里的配合在 MateGroup 里。
      第一版只走顶层，于是「孔内草图」「配合」全被漏掉 —— 这与「记录得全」直接冲突。
    """
    out: list = []

    def _walk(first, owner: str, level: int, is_sub: bool) -> None:
        #: ★ 形参叫 level 不叫 depth：单位命名门禁把 depth 当**长度量纲**，
        #:   而这里其实是特征树层级，与实际尺寸无关。
        cur = first
        while cur is not None:
            name = str(_g(cur, "Name") or "")
            out.append((cur, owner, level))
            sub = _g(cur, "GetFirstSubFeature")
            if sub is not None:
                _walk(sub, name, level + 1, True)
            #: ★ 顶层走 GetNextFeature，**子特征走 GetNextSubFeature** ——
            #:   第一版子层也用了 GetNextFeature ⇒ 同一条链被反复走（草图记 3 遍）。
            cur = _g(cur, "GetNextSubFeature") if is_sub else _g(cur, "GetNextFeature")

    _walk(_g(doc, "FirstFeature"), "", 0, False)
    return out


def _custom_properties(doc) -> dict:
    """自定义属性（名称 → [解析值, 类型, 是否链接]）。

    ★★★ 实测三个坑（本机 2026-10-26）：
      ① CustomPropertyManager 是可调用的延迟属性，必须 ("") 调用；
         且返回的 CDispatch 本身也可能 callable ⇒ **不能用 callable() 判空**。
      ② GetAll3 有 **5 个 out 参数**（含 **PropLink**）；
         只传 4 个会报 非选择性的参数（DISP_E_PARAMNOTOPTIONAL）。
      ③ Get/Get2/Get3/Get4/Get5/Get6 在本机全部报错
         （参数个数或类型不匹配）⇒ **只有 GetAll3 能用**，GetNames 可单独用。
    """
    out: dict = {}
    ext = _g(doc, "Extension")
    if ext is None:
        return out
    cpm = _g(ext, "CustomPropertyManager", "")
    if cpm is None:
        return out
    try:
        import pythoncom
        from win32com.client import VARIANT

        def _byref():
            return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)

        names, types, values, resolved, link = (
            _byref(), _byref(), _byref(), _byref(), _byref())
        ok, ret = _tc(lambda: cpm.GetAll3(names, types, values, resolved, link))
        if not ok:
            out["_error"] = str(ret)[:200]
            return out
        nl = list(getattr(names, "value", None) or ())
        tl = list(getattr(types, "value", None) or ())
        vl = list(getattr(values, "value", None) or ())
        rl = list(getattr(resolved, "value", None) or ())
        ll = list(getattr(link, "value", None) or ())
        for i, nm in enumerate(nl):
            out[str(nm)] = [
                str(vl[i]) if i < len(vl) else None,
                str(tl[i]) if i < len(tl) else None,
                bool(ll[i]) if i < len(ll) else None,
            ]
        out["_count"] = int(ret) if isinstance(ret, int) else len(nl)
        out["_resolved"] = [str(x) for x in rl]
    except Exception as exc:  # noqa: BLE001
        out["_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    return out


# ── 装配 ─────────────────────────────────────────────────────────────
def _same_doc(a, b) -> bool:
    """两个 COM 文档对象是否同一份（比标题 + 路径，避免拿到同一个对象却判不出）。"""
    try:
        ta, tb = str(_g(a, "GetTitle") or ""), str(_g(b, "GetTitle") or "")
        pa, pb = str(_g(a, "GetPathName") or ""), str(_g(b, "GetPathName") or "")
        return ta == tb and pa == pb
    except Exception:  # noqa: BLE001
        return False


def dump_assembly(doc) -> dict:
    """装配：组件（位置/朝向/压缩/路径）+ 配合（类型/对齐/参与实体）。"""
    out: dict = {"components": [], "mates": []}

    comps = list(_g(doc, "GetComponents", False) or ())
    out["component_count"] = len(comps)
    for cp in comps:
        item: dict = {
            "name": str(_g(cp, "Name2") or ""),
            "path": str(_g(cp, "GetPathName") or ""),
        }
        sup = _g(cp, "IsSuppressed")
        if isinstance(sup, bool):
            item["suppressed"] = sup
        tr = _g(cp, "Transform2")
        if tr is not None:
            arr = _g(tr, "ArrayData")
            if arr is not None:
                try:
                    item["transform"] = [round(float(v), 6) for v in list(arr)]
                except Exception:  # noqa: BLE001
                    item["transform"] = NA
        #: ★★★ 组件的**内部内容**也要记 —— 实测踩过：业主在装配体里对「在位零件」
        #:   建草图并标了 3 个尺寸，而 dump_assembly 只记组件名与变换 ⇒ 快照里
        #:   sketches: 0，那 3 个尺寸全丢了。装配记录不递归进组件 = 记录不全。
        sub = _g(cp, "GetModelDoc2")
        if sub is not None and not _same_doc(sub, doc):
            try:
                inner = dump_part(sub, component=cp)
                item["model"] = {
                    "document": str(_g(sub, "GetTitle") or ""),
                    "path": str(_g(sub, "GetPathName") or ""),
                    "features": inner.get("features"),
                    "sketches": inner.get("sketches"),
                    "bodies": inner.get("bodies"),
                    "bodies_source": inner.get("bodies_source"),
                    "custom_properties": inner.get("custom_properties"),
                }
            except Exception as exc:  # noqa: BLE001
                item["model"] = {"error": f"{type(exc).__name__}: {str(exc)[:120]}"}
        out["components"].append(item)

    #: 特征树（配合也在里面）—— ★ 第一版这里**没填 features**，于是配合永远找不到。
    out["features"] = []
    #: 配合：官方**没有** GetMates（已核实）⇒ 走「Mate 特征 → GetSpecificFeature2」；
    #:   ★ 且配合通常挂在 MateGroup 文件夹下 ⇒ 必须**递归**才找得到。
    for feat, owner, level in walk_features(doc):
        tp = str(_g(feat, "GetTypeName2") or "")
        out["features"].append({
            "name": str(_g(feat, "Name") or ""), "type": tp,
            "owner": owner or None, "level": level,
        })
        #: ★★★ 配合特征的 GetTypeName2() **不是** "Mate"，而是按配合种类命名 ——
        #:   实测本轮加的距离配合是 **MateDistanceDim**（同族还有 MateCoincident 等）。
        #:   第一版只认 "Mate" ⇒ 配合永远记成 0。改为「以 Mate 开头且 != MateGroup」。
        if tp.startswith("Mate") and tp != "MateGroup":
            m = _mate_detail(feat)
            m["feature_type"] = tp
            m["owner"] = owner or None
            out["mates"].append(m)
    return out


def _mate_detail(feature) -> dict:
    """一个配合：名字 + 类型 + 对齐 + 参与实体。"""
    item: dict = {"name": str(_g(feature, "Name") or "")}
    mate = _g(feature, "GetSpecificFeature2")
    if mate is None:
        item["error"] = "IMate2 取不到"
        return item
    t = _int(_g(mate, "Type"))
    if t is not None:
        item["type_int"] = t
        item["type"] = MATE_TYPE.get(t, "未知(%d)" % t)
    a = _int(_g(mate, "Alignment"))
    if a is not None:
        item["align"] = MATE_ALIGN.get(a, str(a))

    ents = []
    i = 0
    while i < 12:  #: 官方没有 MateEntityCount ⇒ 逐个试到空
        #: ★ 实测 MateEntity 是 **0 基**（0 与 1 都有值、2 起为 None）；
        #:   第一版从 1 开始 ⇒ 距离配合只记到 1 个实体（应为 2）。
        me = _g(mate, "MateEntity", i)
        if me is None:
            break
        e: dict = {}
        #: ★★ IMateEntity2 取实体用 **Reference**，不是 Entity
        #:   （第一版写了 Entity ⇒ 参与实体永远是空）。
        ent_obj = _g(me, "Reference")
        if ent_obj is not None:
            desc = describe_entity(ent_obj)
            #: ★ 在位配合（MateInPlace）的 Reference 常常不是几何实体，
            #:   而是**组件/特征** ⇒ 几何描述判不出时，退回记「它到底是什么对象」。
            if desc.get("kind") == "未识别":
                for attr, tag in (("Name2", "component"), ("Name", "feature")):
                    nm = _g(ent_obj, attr)
                    if nm:
                        desc = {"kind": tag, "name": str(nm)[:120]}
                        break
            e["entity"] = desc
        comp = _g(me, "ReferenceComponent")
        if comp is not None:
            e["reference_component"] = str(_g(comp, "Name2") or "")
        for attr in ("ReferenceType", "ReferenceType2"):
            rt = _int(_g(me, attr))
            if rt is not None:
                e[attr.lower()] = rt
        n = _int(_g(me, "GetEntityParamsSize"))
        if n is not None:
            e["entity_params_size"] = n
        if not e:
            e["描述"] = NA
        ents.append(e)
        i += 1
    item["entities"] = ents
    item["entity_count"] = len(ents)
    #: ★ 在位配合（MateInPlace）实测 MateEntity(i).Reference 与 ReferenceComponent
    #:   都回 None ⇒ 如实标「实体读不到」，而不是让下游以为「这个配合没有实体」。
    if ents and all(not e.get("entity") for e in ents):
        item["entities_unreadable"] = True

    #: ★ 配合的数值参数（距离/角度）在配合特征的**显示尺寸**上：
    #:   IFeature.GetFirstDisplayDimension() → IDisplayDimension.GetDimension2(0)。
    #: ★ 量纲按**配合类型**分派，不能一律当长度：MATE_TYPE_RAW[6] = swMateANGLE
    #:   ⇒ 角度配合的 GetSystemValue2 回**弧度**（与草图 ANGLE 同理，事实 592）。
    okd, dd = _tc(_g, feature, "GetFirstDisplayDimension")
    if okd and dd is not None:
        okr, dim = _tc(_g, dd, "GetDimension2", 0)
        if okr and dim is not None:
            #: 用 `t`（配合类型整数，上面 `_int(_g(mate, "Type"))` 得到的）
            item.update(_mate_reading(dim, t))
    return item


def _mate_reading(dim, mate_type_int) -> dict:
    """配合的数值：**按配合类型决定量纲**（距离 → mm；角度 → rad/deg）。"""
    if dim is None:
        return {}
    v = _g(dim, "GetSystemValue2", "")
    if v is None:
        return {}
    try:
        raw = float(v)
    except (TypeError, ValueError):
        return {}
    if mate_type_int == 6:            #: swMateANGLE
        from sw_units import rad_to_deg

        return {"value_rad": round(raw, 6), "value_deg": rad_to_deg(raw)}
    if mate_type_int == 5:            #: swMateDISTANCE
        from sw_units import m_to_mm

        return {"value_mm": m_to_mm(raw)}
    return {"raw_system_value": round(raw, 6), "unit_unverified": True}


# ── 图样 ─────────────────────────────────────────────────────────────
def _view_detail(feature, base: dict) -> dict:
    """图样视图的**标注信息**：尺寸个数与数值、注释个数。

    ★ 实测入口（IView）：GetDisplayDimensionCount() / GetDisplayDimensions() /
      GetAnnotationCount() / GetAnnotations()。
    """
    view = _g(feature, "GetSpecificFeature2")
    if view is None:
        return base
    n_dim = _int(_g(view, "GetDisplayDimensionCount"))
    if n_dim is not None:
        base["dimension_count"] = n_dim
    n_ann = _int(_g(view, "GetAnnotationCount"))
    if n_ann is not None:
        base["annotation_count"] = n_ann
    #: ★ 图样视图里的尺寸**量纲不能一概当成长度**（可能是角度标注）。
    #:   判据：IDisplayDimension.Type2 回 swDimensionType_e；
    #:   ★ 但本机**未实测**该枚举在各标注类型上的取值 ⇒ 不猜：
    #:   能判出量纲才写 value_mm / value_deg，判不出就标 unit_unverified。
    #:   图样尺寸的**真实数值**留给下游按标注类型解读，本记录器只如实交原始值。
    raw_vals = []
    for dd in list(_g(view, "GetDisplayDimensions") or ()):
        dim = _g(dd, "GetDimension2", 0)
        if dim is None:
            continue
        v = _g(dim, "GetSystemValue2", "")
        if v is None:
            continue
        try:
            raw_vals.append(round(float(v), 6))
        except (TypeError, ValueError):
            continue
    if raw_vals:
        base["dimension_values_raw"] = raw_vals
        base["dimension_unit_note"] = (
            "图样标注未实测量纲，不代换算")
    return base


def dump_drawing(doc) -> dict:
    """图样：特征树 + 视图 + 各视图里的草图（图样几何）。

    ★ 实测（output/stage2/drawing_板1_rev-1/板1_rev-1.SLDDRW）：
      视图特征的类型名是 **AbsoluteView**（不是 DrawingView），
      图纸是 DrSheet；视图里还挂着 ProfileFeature（图样几何草图）。
      第一版只认 DrawingView/DrSheet ⇒ 只记到 1 个图纸、0 个视图、0 条特征。
    """
    out: dict = {"features": [], "views": [], "sketches": []}

    #: 视图类特征的类型名（实测 + 常见同族；命中即记为视图）
    view_types = (
        "DrSheet", "AbsoluteView", "DrawingView", "SectionView", "DetailView",
        "ProjectedView", "AuxiliaryView", "StandardView", "NamedView",
        "ModelView", "UnfoldedView", "RelativeView",
    )

    for feat, owner, level in walk_features(doc):
        tp = str(_g(feat, "GetTypeName2") or "")
        out["features"].append({
            "name": str(_g(feat, "Name") or ""), "type": tp,
            "owner": owner or None, "level": level,
        })
        if tp in view_types:
            v = {"name": str(_g(feat, "Name") or ""), "type": tp,
                 "owner": owner or None}
            out["views"].append(_view_detail(feat, v))
        elif tp == "ProfileFeature":
            sk = sketch_detail(feat)
            sk["owner"] = owner or None      #: 图样里草图挂在某个视图下
            out["sketches"].append(sk)
    return out


# ── 入口 ─────────────────────────────────────────────────────────────
def external_references(doc) -> list:
    """**外部引用**：本文件里哪些特征引用了别的文档/别的零件的实体。

    ### 为什么单独做（业主 2026-10-26 点名要求）

    > 我在画图的时候，可能引用这个基准面上已有的一个实体的某个边或者某个点；
    > 或者是在装配体中编辑零件的时候，可能还会选择或者引用别的零件的这个边或者点。

    ### 官方路（实测）

    `
    IModelDocExtension.ListExternalFileReferencesCount()        # 0 参
    IModelDocExtension.ListExternalFileReferences2(9 个 out)     # 见下
    `
    ★ 别用 IModelDoc2.ListExternalFileReferences2（**已废弃**），也别用
      IModelDoc2.ListExternalFileReferencesCount(UseSearchRules) —— 实测它在
      有 3 条外部引用的装配上仍回 **0**；只有 ...Count2() / 扩展版是对的。

    9 个 out 数组：ModelPathName / ComponentPathName / Feature / DataType /
    Status / RefEntity / FeatCom / ConfigOptions / ConfigNames。
    其中 DataType 会写清「转换的边或面」这类具体来源，RefEntity 是被引用的实际对象，
    FeatCom 是它所在**哪个组件**（装配内引用别的零件时才有）。
    """
    out: list = []
    ext = _g(doc, "Extension")
    if ext is None:
        return out
    cnt = _g(ext, "ListExternalFileReferencesCount")
    if not isinstance(cnt, int) or cnt <= 0:
        return out
    try:
        import pythoncom
        from win32com.client import VARIANT

        def _byref():
            return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)

        holders = [_byref() for _ in range(9)]
        ok, _ = _tc(lambda: ext.ListExternalFileReferences2(*holders))
        if not ok:
            return [{"error": "ListExternalFileReferences2 调用失败"}]
        arrs = [list(getattr(h, "value", None) or ()) for h in holders]
        keys = ("model_path", "component_path", "feature", "data_type", "status",
                "ref_entity", "ref_component", "config_options", "config_names")
        for i in range(cnt):
            item = {}
            for k, arr in zip(keys, arrs):
                if i < len(arr) and arr[i] not in (None, ""):
                    item[k] = str(arr[i])[:200]
            if item:
                out.append(item)
    except Exception as exc:  # noqa: BLE001
        out.append({"error": f"{type(exc).__name__}: {str(exc)[:160]}"})
    return out


def dump_document(doc) -> dict:
    """整份文档的记录（按类型分发）。**只记录，不推断。**"""
    dtype = _int(_g(doc, "GetType"))
    kind = DOC_KIND.get(dtype, f"未知({dtype})")
    out: dict = {
        "document": str(_g(doc, "GetTitle") or ""),
        "path": str(_g(doc, "GetPathName") or ""),
        "doc_type": kind,
        "doc_type_int": dtype,
    }
    #: 外部引用：任何文档类型都可能存在（零件引用别的零件 / 装配内 in-context）
    out["external_references"] = external_references(doc)
    if kind == "零件":
        out.update(dump_part(doc))
    elif kind == "装配":
        out.update(dump_assembly(doc))
    elif kind == "图样":
        out.update(dump_drawing(doc))
    return out


#: 兼容旧调用名（`demo_capture` / `teach.py` 用的是 `dump_model`）
dump_model = dump_document
