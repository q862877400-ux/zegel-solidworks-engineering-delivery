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

#: `swMateType_e`（官方枚举，逐条核过 `C:\swapi\enums\swMateType_e.md`）
MATE_TYPE = {
    0: "COINCIDENT", 1: "CONCENTRIC", 2: "PERPENDICULAR", 3: "PARALLEL",
    4: "TANGENT", 5: "DISTANCE", 6: "ANGLE", 7: "UNKNOWN", 8: "SYMMETRIC",
    9: "CAMFOLLOWER", 10: "GEAR", 11: "WIDTH", 12: "LOCKTOSKETCH",
    13: "RACKPINION", 14: "MAXMATES", 15: "PATH", 16: "LOCK", 17: "SCREW",
    18: "LINEARCOUPLER", 19: "UNIVERSALJOINT", 20: "COORDINATE", 21: "SLOT",
    22: "HINGE", 23: "SLIDER",
}

#: `swMateAlign_e`
MATE_ALIGN = {0: "ALIGNED", 1: "ANTI_ALIGNED", 2: "CLOSEST"}

#: `swConstraintType_e`（草图关系；1 = DISTANCE 即尺寸）
CONSTRAINT = {
    1: "DISTANCE", 2: "ANGLE", 3: "RADIUS", 4: "HORIZONTAL", 5: "VERTICAL",
    6: "PERPENDICULAR", 7: "TANGENT", 8: "CONCENTRIC", 9: "COINCIDENT",
    10: "CONCENTRIC", 11: "SYMMETRIC", 12: "ATMIDDLE", 13: "INTERSECTION",
    14: "SAMELENGTH", 15: "DIAMETER", 17: "FIXED", 25: "HORIZPOINTS",
    26: "VERPOINTS", 27: "COLINEAR", 40: "ATPIERCE", 41: "DOUBLEDISTANCE",
    42: "MERGEPOINTS", 45: "NORMAL", 46: "NORMALPOINTS", 51: "ALONGXPOINTS",
    52: "ALONGYPOINTS", 53: "ALONGZPOINTS",
}

#: `swSketchSegments_e`
SEGMENT_KIND = {0: "直线", 1: "圆弧", 2: "椭圆", 3: "样条", 4: "文字", 5: "抛物线"}

#: `swDocumentTypes_e`
DOC_KIND = {1: "零件", 2: "装配", 3: "图样"}

NA = "读不到"


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
    """调本仓 	ry_call（失败不抛，回 (ok, 值)）。"""
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
                    d["%s_mm" % tag] = [_mm(q[0]), _mm(q[1]), _mm(q[2])]
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
        out["shape"] = SEGMENT_KIND[t]
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

    pts = []
    for sp in list(_g(sk, "GetSketchPoints2") or ()):
        item = {"x_mm": _mm(_g(sp, "X")), "y_mm": _mm(_g(sp, "Y"))}
        t = _int(_g(sp, "Type"))
        if t is not None:
            item["type_int"] = t
        pts.append(item)
    out["points"] = pts

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
            item["type"] = CONSTRAINT.get(rt, str(rt))
            item["entities"] = [describe_entity(e)
                                for e in list(_g(rel, "GetEntities") or ())]
            dd = _g(rel, "GetDisplayDimension")
            if dd is not None:
                dim = _g(dd, "GetDimension2", 0)
                if dim is not None:
                    #: ★ 官方 `GetSystemValue2(ConfigName)` 要传配置名，空串=当前配置
                    v = _g(dim, "GetSystemValue2", "")
                    if v is not None:
                        try:
                            item["value_mm"] = _mm(v)
                        except Exception:  # noqa: BLE001
                            item["value_mm"] = None
            rels.append(item)
    out["relations"] = rels
    return out


# ── 零件 ─────────────────────────────────────────────────────────────
def dump_part(doc) -> dict:
    """零件：特征树 + 每张草图 + 实体统计 + 自定义属性 + 参考几何。"""
    out: dict = {"features": [], "sketches": [], "bodies": []}

    for feat, owner, level in walk_features(doc):
        tp = str(_g(feat, "GetTypeName2") or "")
        out["features"].append({
            "name": str(_g(feat, "Name") or ""), "type": tp,
            "owner": owner or None, "level": level,
        })
        if tp == "ProfileFeature":
            sk = sketch_detail(feat)
            sk["owner"] = owner or None      #: 孔内草图要能看出挂在哪个孔特征下
            out["sketches"].append(sk)

    for body in list(_g(doc, "GetBodies2", 0, False) or ()):
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
        out["_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    return out


# ── 装配 ─────────────────────────────────────────────────────────────
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
            e["entity"] = describe_entity(ent_obj)
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
    return item


# ── 图样 ─────────────────────────────────────────────────────────────
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
            out["views"].append({"name": str(_g(feat, "Name") or ""),
                                  "type": tp, "owner": owner or None})
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
        out.append({"error": "%s: %s" % (type(exc).__name__, str(exc)[:160])})
    return out


def dump_document(doc) -> dict:
    """整份文档的记录（按类型分发）。**只记录，不推断。**"""
    dtype = _int(_g(doc, "GetType"))
    kind = DOC_KIND.get(dtype, "未知(%s)" % (dtype,))
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
