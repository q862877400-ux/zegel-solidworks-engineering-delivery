import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path[:0] = [r"C:\swprojects\sw-skill-fork", r"C:\swprojects\sw-skill-fork\scripts"]

import sw_connect
from sw_connect import get_com_member
from scripts import sw_part as P
from scripts import sw_surface_features as SF

MARK_BOUNDARY = 1          # 官方 Remarks：Boundary curves = 1
sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
ev = {}
doc = None
try:
    doc = sw_connect.new_document(sw, "part")
    P.start_sketch(doc, plane_name="Front Plane")
    P.sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
    sk = P.current_sketch_name(doc)
    P.end_sketch(doc)
    SF.create_extruded_surface_report(doc, 30.0, sk)
    edges = []
    for b in (get_com_member(doc, "GetBodies2", -1, True) or []):
        edges.extend(get_com_member(b, "GetEdges") or [])
    ext = get_com_member(doc, "Extension")
    callout = sw_connect.create_empty_dispatch_variant()
    sm = get_com_member(doc, "SelectionManager")

    def mid(e):
        try:
            a = [float(x) for x in get_com_member(get_com_member(e, "GetStartVertex"), "GetPoint")]
            b = [float(x) for x in get_com_member(get_com_member(e, "GetEndVertex"), "GetPoint")]
            return [(a[i] + b[i]) / 2.0 for i in range(3)]
        except Exception:
            return None

    valid = [(mid(e), e) for e in edges]
    valid = [(m, e) for m, e in valid if m]
    top = max(m[2] for m, _ in valid)
    top_edges = [(m, e) for m, e in valid if abs(m[2] - top) < 1e-9]
    ev["top_z"] = top
    ev["top_edges"] = len(top_edges)
    before = SF.feature_names(doc)
    fm = get_com_member(doc, "FeatureManager")

    # A. SelectByID2 按中点 + mark=1（官方 Remarks 要的那个）
    doc.ClearSelection2(True)
    nA = 0
    for m, _e in top_edges:
        if ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, MARK_BOUNDARY, callout, 0):
            nA += 1
    ev["A_selectbyid_mark1"] = {
        "returned_true": nA,
        "readback": int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0),
    }
    # B. 在该选中基础上填充（Options=1 / 0）
    for label, opts in (("mark1_opt1", 1), ("mark1_opt0", 0)):
        try:
            f = get_com_member(fm, "InsertFillSurface2", 2, opts, None, None, None, None)
            after = SF.feature_names(doc)
            ev["fill_" + label] = {"returned": (f is not None),
                                   "new": [x for x in after if x not in before][-2:]}
        except Exception as ex:
            ev["fill_" + label] = {"err": "%s: %s" % (type(ex).__name__, str(ex)[:90])}
    # C. 再试 Select4 选中 + list payload（组合）
    doc.ClearSelection2(True)
    for _m, e in top_edges:
        try:
            e.Select4(True, callout)
        except Exception:
            pass
    try:
        f = get_com_member(fm, "InsertFillSurface2", 2, 1, [e for _m, e in top_edges], None, None, None)
        after = SF.feature_names(doc)
        ev["fill_select4_list"] = {"returned": (f is not None),
                                   "new": [x for x in after if x not in before][-2:]}
    except Exception as ex:
        ev["fill_select4_list"] = {"err": "%s: %s" % (type(ex).__name__, str(ex)[:90])}
    print(json.dumps(ev, ensure_ascii=False, indent=1)[:1300])
    t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
finally:
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
