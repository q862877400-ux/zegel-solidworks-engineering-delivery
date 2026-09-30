import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4, create_empty_dispatch_variant
from scripts import sw_part, sw_simulation as sim, sw_topology as topo
sw,_m,_x = connect_solidworks(wait_seconds=15, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='MSH_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,13,0,out_i4())
    topo.set_topology_goal(s, mass_reduce_percent=75.0)
    sw_part._select_by_id(m.Extension,'','FACE'); sim.apply_fixed_restraint(s, model=m)
    get_com_member(m,'ClearSelection2',True)
    sw_part._select_by_id(m.Extension,'','FACE'); sim.apply_normal_force(s, model=m, magnitude=100.0)
    get_com_member(m,'ClearSelection2',True)
    print("  Count=%r" % get_com_member(get_com_member(s,'LoadsAndRestraintsManager'),'Count'))
    print()
    print("=== ActiveStudy（官方示例在建研究前就设了）===")
    cnt = get_com_member(mg,'StudyCount'); print("  StudyCount = %r" % cnt)
    try:
        setattr(mg, 'ActiveStudy', int(cnt)); print("  mg.ActiveStudy = %d  ✓" % cnt)
    except Exception as e:
        print("  mg.ActiveStudy 赋值 ✗ %s" % str(e)[:60])
    print("  回读 ActiveStudy = %r" % get_com_member(mg,'ActiveStudy'))
    print()
    def T(label, fn):
        try:
            r = fn(); print("  %-46s %r" % (label, r)); return r
        except Exception as e:
            print("  %-46s ✗ %s" % (label, str(e)[:52])); return None
    print("=== 网格 / 求解 ===")
    T("CreateMesh(0, 0.0, 0.0)", lambda: get_com_member(s,'CreateMesh',0,0.0,0.0))
    T("  get_MeshState", lambda: get_com_member(s,'get_MeshState'))
    T("  get_IsMeshFailed2", lambda: get_com_member(s,'get_IsMeshFailed2'))
    T("RunAnalysis()", lambda: get_com_member(s,'RunAnalysis'))
    T("  get_AnalysisType", lambda: get_com_member(s,'get_AnalysisType'))
    T("Results", lambda: get_com_member(s,'Results'))
    T("MeshAndRun()（对照）", lambda: get_com_member(s,'MeshAndRun'))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成")