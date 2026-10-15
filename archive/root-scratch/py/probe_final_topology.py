import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_topology as topo
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
    n = "FINAL2_%d" % int(time.time())
    get_com_member(mgr, "DeleteStudy", n)
    s = get_com_member(mgr, "CreateNewStudy3", n, 13, 0, out_i4())
    print("  研究建成: %r  AnalysisType=%r" % (s is not None, get_com_member(s, "AnalysisType")))
    for pct in (75.0, 60.0, 50.0):
        r = topo.set_topology_goal(s, mass_reduce_percent=pct)
        mc = r["mass_constraint"]
        nm = get_com_member(mc, "GetName") if mc is not None else None
        print("  ✓ 减重 %.0f%% → 约束名=%r  复用目标自带的=%r" % (pct, nm, r.get("mass_constraint_reused")))
    print()
    print("  ── 再加 FOS 约束（先清 stress，因两者互斥）──")
    r2 = topo.set_topology_goal(s, mass_reduce_percent=50.0, factor_of_safety=80.0)
    print("  ✓ 质量约束=%r  FOS 约束=%r  removed=%r"
          % (r2["mass_constraint"] is not None, r2["fos_constraint"] is not None, r2["removed"]))
    print()
    print("  ── 列清单（真读到才算数）──")
    lst = topo.list_topology_constraints_and_controls(s)
    for k, v in lst.items():
        if not k.endswith("__error"):
            print("    %-18s %s" % (k, "✓ 有" if v else "○ None"))
finally:
    try:
        if title: sw.CloseDoc(title)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成（文档未保存）")