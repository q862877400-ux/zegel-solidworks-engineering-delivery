r"""验证 set_topology_goal 的「先删后建」修复（真机）。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import time
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_topology as topo

sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
sw.CommandInProgress = True
title = None
try:
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"), "CosmosWorks"), "ActiveDoc")
    mgr = get_com_member(doc, "StudyManager")
    n = "FIX_TEST_%d" % int(time.time())
    get_com_member(mgr, "DeleteStudy", n)
    s = get_com_member(mgr, "CreateNewStudy3", n, 13, 0, out_i4())
    print("  研究建成: %r" % (s is not None))
    print()
    print("  第一次 set_topology_goal(减重75) —— 干净研究")
    try:
        r1 = topo.set_topology_goal(s, mass_reduce_percent=75.0)
        print("    ✓ 成功  goal=%r  mass=%r  removed=%r" % (r1["goal"], r1["mass_constraint"] is not None, r1["removed"]))
    except Exception as e:
        print("    ✗ %s" % str(e)[:90])
    print()
    print("  第二次 set_topology_goal(减重60) —— 【同类约束已存在】，看是否先删再建")
    try:
        r2 = topo.set_topology_goal(s, mass_reduce_percent=60.0)
        print("    ✓ 成功  mass=%r  removed=%r  ← removed 非空即证明「先删后建」生效" % (r2["mass_constraint"] is not None, r2["removed"]))
    except Exception as e:
        print("    ✗ %s" % str(e)[:90])
    print()
    print("  list_topology_constraints_and_controls（修复后应能真读到）")
    try:
        lst = topo.list_topology_constraints_and_controls(s)
        for k, v in lst.items():
            if not k.endswith("__error"):
                print("    %-20s %s" % (k, "✓ 有" if v else "○ None"))
    except Exception as e:
        print("    ✗ %s" % str(e)[:90])
finally:
    try:
        if title: sw.CloseDoc(title)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成（文档未保存）")