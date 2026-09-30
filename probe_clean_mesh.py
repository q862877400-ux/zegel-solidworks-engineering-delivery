import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_simulation as sim
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='CLEAN_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    print("  研究 %r" % (s is not None))
    mesh = get_com_member(s,'Mesh')
    print("  网格前 ElementCount = %r" % get_com_member(mesh,'ElementCount'))
    # 官方建议值（毫米）
    from win32com.client import VARIANT
    import pythoncom
    vs = VARIANT(pythoncom.VT_BYREF|pythoncom.VT_R8, 0.0); vt = VARIANT(pythoncom.VT_BYREF|pythoncom.VT_R8, 0.0)
    get_com_member(mesh,'GetDefaultElementSizeAndTolerance',0,vs,vt)
    print("  官方建议 size=%.4f tol=%.4f" % (vs.value, vt.value))
    t0=time.time()
    code = get_com_member(s,'CreateMesh',0,float(vt.value),float(vs.value))
    print("  CreateMesh(0,%.4f,%.4f) → %r   用时 %.0f 秒" % (vt.value, vs.value, code, time.time()-t0))
    print("  ★ 网格后 ElementCount = %r" % get_com_member(mesh,'ElementCount'))
    print("  ★ 网格后 NodeCount    = %r" % get_com_member(mesh,'NodeCount'))
    print("  MeshState = %r  IsMeshFailed2 = %r" % (get_com_member(mesh,'MeshState'), get_com_member(mesh,'IsMeshFailed2')))
    t1=time.time()
    rc = get_com_member(s,'RunAnalysis')
    print("  RunAnalysis → %r   用时 %.0f 秒" % (rc, time.time()-t1))
    res = get_com_member(s,'Results')
    print("  ★ study.Results 非空 = %r" % (res is not None))
    if res is not None:
        print("    GetPlotCount = %r" % get_com_member(res,'GetPlotCount'))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass