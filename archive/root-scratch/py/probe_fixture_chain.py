import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_simulation as sim, sw_topology as topo
sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
sw.CommandInProgress = True
title = None
try:
    model = new_document(sw, doc_type="part"); title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"), "CosmosWorks"), "ActiveDoc")
    mgr = get_com_member(doc, "StudyManager")
    n = "FIX_%d" % int(time.time()); get_com_member(mgr, "DeleteStudy", n)
    s = get_com_member(mgr, "CreateNewStudy3", n, 13, 0, out_i4())
    print("  研究 %r" % (s is not None))
    r = topo.set_topology_goal(s, mass_reduce_percent=75.0)
    print("  目标+质量约束 ✓ 复用自带=%r" % r.get("mass_constraint_reused"))
    sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
    fr = sim.apply_fixed_restraint(s, model=model); print("  ✓ 夹具建成 %r" % (fr is not None))
    get_com_member(model, "ClearSelection2", True)
    sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
    fo = sim.apply_normal_force(s, model=model, magnitude=100.0); print("  ✓ 载荷建成 %r" % (fo is not None))
    get_com_member(model, "ClearSelection2", True)
    print("  LoadsAndRestraintsManager.Count = %r" % get_com_member(get_com_member(s, "LoadsAndRestraintsManager"), "Count"))
finally:
    try:
        if title: sw.CloseDoc(title)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成")