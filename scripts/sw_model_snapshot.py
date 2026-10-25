"""把零件的**语义状态**取成结构化数据：特征 / 草图 / 点 / 关系 / 尺寸（含参照实体）。

## 为什么需要它（业主 2026-10-26）

> 你能够读得到我标了 4 个尺寸，但是你不知道我标的是哪里。

截图只能看像素，录屏只能看画面 —— 而「这条尺寸量的是**点(10,10) 到左边线**」
这种语义，**只能从模型里读**。本模块就是那一层的采集器。

## 关键 API

```
ISketch.RelationManager                 → 关系/尺寸的宿主
ISketchRelationManager.GetRelations(0)  → 每条 ISketchRelation
ISketchRelation.GetRelationType()       → swConstraintType_e（1=DISTANCE 就是尺寸）
ISketchRelation.GetEntities()           → 参照的实体数组
ISketchRelation.GetDisplayDimension()   → 尺寸对象
IDisplayDimension.GetDimension2(0)      → IDimension
IDimension.GetSystemValue2(配置名)       → **米**（要传配置名，空串=当前）
```

★ 实体类型**不看 `GetEntitiesType()`**（实测映射对不上，会把点报成 FACE）——
  改用**按对象自身特征判断**：有 `X/Y` 就是草图点；有 `GetStartPoint2` 就是线段。

## 输出形状

```python
{
  "document": "零件1", "path": "...",
  "features": [{"name": "凸台-拉伸1", "type": "Extrusion"}, ...],
  "holes":    [{"name": "M6 间隙孔1", "standard": "GB", "fastener": "螺钉间隙",
                "size": "M6", "sketches": [...]}],
  "sketches": [{"name": "草图2", "constrained": 3,
                "points": [[10.0, -10.0], ...],
                "relations": [{"type": "DISTANCE", "value_mm": 10.0,
                               "refs": ["点(10.0,-10.0)", "线[(0,0)→(0,-60)]"]}]}]
}
```
"""
from __future__ import annotations

#: `swConstraintType_e` 常用值（官方枚举；未列出的给数字）
CONSTRAINT = {
    1: "DISTANCE", 2: "ANGLE", 3: "RADIUS", 10: "CONCENTRIC",
    11: "SYMMETRIC", 12: "ATMIDDLE", 15: "DIAMETER", 17: "FIXED",
    25: "HORIZPOINTS", 26: "VERPOINTS", 27: "COLINEAR", 40: "ATPIERCE",
    41: "DOUBLEDISTANCE", 51: "ALONGXPOINTS", 52: "ALONGYPOINTS",
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（采集器 · 模型语义快照）
# 文件:   scripts/sw_model_snapshot.py
# 定位:   把零件语义取成 dict：特征树 / 每张草图的点坐标 / 关系与尺寸（含参照实体）。
#          供 tools/demo_capture.py 在「示范捕获（试教）」时落盘，补截图看不到的语义。
# 官方依据: IModelDoc2.FirstFeature/GetNextFeature · IFeature.GetTypeName2/GetDefinition ·
#          IFeature.GetSpecificFeature2 · IFeature.GetFirstSubFeature ·
#          ISketch.GetConstrainedStatus/GetSketchPoints2/RelationManager ·
#          ISketchRelationManager.GetRelationsCount/GetRelations ·
#          ISketchRelation.GetRelationType/GetEntities/GetDisplayDimension ·
#          ISketchPoint.X/Y · ISketchSegment.GetStartPoint2/GetEndPoint2 ·
#          IDisplayDimension.GetDimension2 · IDimension.GetSystemValue2
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


#: dispatch-guard: exempt internal-helper
def _g(obj, name, *args):
    """取 COM 成员：**有实参就调用**（`IsCylinder` 这类属性不能带实参）。

    ★ 本地 def 而不是导入别名：`check_dispatch_byref_guard` 靠**本地 def** 认出
      「分发口调用点」并逐条核验成员名，改成别名会让它认不出（基线里有同款判例）。
    """
    from sw_connect import get_com_member

    return get_com_member(obj, name, *args)


def _tc(*args, **kwargs):
    from sw_connect import try_call

    return try_call(*args, **kwargs)


def describe_entity(ent) -> str:
    """实体 → 可读描述。★ 按对象自身特征判断，**不用** `GetEntitiesType()`。"""
    try:
        x = float(_g(ent, "X")) * 1000.0
        y = float(_g(ent, "Y")) * 1000.0
        return "点(%.2f,%.2f)" % (x, y)
    except Exception:  # noqa: BLE001
        pass
    try:
        sp = _g(ent, "GetStartPoint2")
        ep = _g(ent, "GetEndPoint2")
        x1 = float(_g(sp, "X")) * 1000.0
        y1 = float(_g(sp, "Y")) * 1000.0
        x2 = float(_g(ep, "X")) * 1000.0
        y2 = float(_g(ep, "Y")) * 1000.0
        return "线[(%.1f,%.1f)→(%.1f,%.1f)]" % (x1, y1, x2, y2)
    except Exception:  # noqa: BLE001
        pass
    try:
        return "边#%s" % (_g(ent, "GetID"),)
    except Exception:  # noqa: BLE001
        return "未知实体"


def sketch_snapshot(feature) -> dict:
    """一张草图的点 / 关系 / 尺寸（含参照实体）。"""
    ok, sk = _tc(_g, feature, "GetSpecificFeature2")
    if not ok or sk is None:
        return {"error": "草图对象取不到", "name": str(_g(feature, "Name") or "")}

    out: dict = {"name": str(_g(feature, "Name") or "")}
    okc, st = _tc(lambda: int(sk.GetConstrainedStatus))
    out["constrained"] = st if okc else None

    pts = []
    okp, arr = _tc(_g, sk, "GetSketchPoints2")
    for sp in list(arr or ()):
        try:
            pts.append([round(float(_g(sp, "X")) * 1000.0, 3),
                        round(float(_g(sp, "Y")) * 1000.0, 3)])
        except Exception:  # noqa: BLE001
            continue
    out["points"] = pts

    rels: list = []
    okm, rm = _tc(_g, sk, "RelationManager")
    if okm and rm is not None:
        okn, cnt = _tc(_g, rm, "GetRelationsCount", 0)
        if okn and isinstance(cnt, int) and cnt > 0:
            okr, arr2 = _tc(_g, rm, "GetRelations", 0)
            for rel in list(arr2 or ()):
                rels.append(_relation_item(rel))
    out["relations"] = rels
    return out


def _relation_item(rel) -> dict:
    """一条关系/尺寸 → dict（类型 / 参照实体 / 数值）。"""
    item: dict = {}
    okt, rt = _tc(_g, rel, "GetRelationType")
    item["type"] = CONSTRAINT.get(int(rt), str(rt)) if okt else "?"
    oke, ents = _tc(_g, rel, "GetEntities")
    item["refs"] = [describe_entity(e) for e in list(ents or ())]

    okt2, dd = _tc(_g, rel, "GetDisplayDimension")
    if not okt2 or dd is None:
        return item
    okd, dim = _tc(_g, dd, "GetDimension2", 0)
    if not okd or dim is None:
        return item
    #: ★ `GetSystemValue2(ConfigName)` 要传配置名；空串 = 当前配置。
    #:   不传会抛 DISP_E_PARAMNOTOPTIONAL（非选择性参数）。
    try:
        val = _g(dim, "GetSystemValue2", "")
        item["value_mm"] = round(float(val) * 1000.0, 3)
    except Exception:  # noqa: BLE001
        pass
    return item


def hole_snapshot(feature) -> dict:
    """孔特征：标准 / 类型 / 规格 + 它的子草图快照。"""
    out: dict = {"name": str(_g(feature, "Name") or "")}
    d = _g(feature, "GetDefinition")
    for key, member in (("standard", "Standard"), ("fastener", "FastenerType"),
                        ("size", "FastenerSize")):
        try:
            out[key] = str(_g(d, member))
        except Exception:  # noqa: BLE001
            out[key] = None
    subs = []
    sub = _g(feature, "GetFirstSubFeature")
    while sub is not None:
        if str(_g(sub, "GetTypeName2") or "") == "ProfileFeature":
            subs.append(sketch_snapshot(sub))
        sub = _g(sub, "GetNextSubFeature")
    out["sketches"] = subs
    return out


def dump_model(doc) -> dict:
    """整份零件的语义快照。"""
    out: dict = {
        "document": str(_g(doc, "GetTitle") or ""),
        "path": str(_g(doc, "GetPathName") or ""),
        "features": [],
        "sketches": [],
        "holes": [],
    }
    f = _g(doc, "FirstFeature")
    while f is not None:
        nm = str(_g(f, "Name") or "")
        tp = str(_g(f, "GetTypeName2") or "")
        out["features"].append({"name": nm, "type": tp})
        if tp == "ProfileFeature":
            out["sketches"].append(sketch_snapshot(f))
        elif tp == "HoleWzd":
            out["holes"].append(hole_snapshot(f))
        f = _g(f, "GetNextFeature")
    return out
