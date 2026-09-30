import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts.sw_part import _empty_callout
from scripts import sw_part, sw_simulation as sim
RUN_ERR={0:"Successful",19:"MaterialNotDefined",23:"MeshNotFound",24:"AnalysisFailed"}
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
def sel_face(ext, x, y, z, mark=0):
    """用**面上的点**选面。"""
    return ext.SelectByID2("", "FACE", x, y, z, False, mark, _empty_callout(), 0)
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    ext = m.Extension
    # ① 材料：库名大写 + AISI 1020
    get_com_member(m,'SetMaterialPropertyName2','','SOLIDWORKS Materials','AISI 1020')
    print("  材料回读 = %r" % get_com_member(m,'MaterialIdName'))
    # ② 研究
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='ENDF_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    # ③ ★ 用坐标选面（底面 z=-0.02 固定；顶面 z=0 加载）
    print()
    print("=== 用面上坐标选面 ===")
    for label,(x,y,z) in (("底面 z=-0.02",(0.0,0.0,-0.02)), ("顶面 z=0",(0.0,0.0,0.0))):
        r = sel_face(ext, x, y, z)
        cnt = get_com_member(get_com_member(m,'SelectionManager'),'GetSelectedObjectCount2',-1)
        print("  %-14s SelectByID2=%r  选区计数=%r" % (label, r, cnt))
        got = get_com_member(get_com_member(m,'SelectionManager'),'GetSelectedObject6',1,-1)
        print("     第 1 个选中对象 = %r" % (got is not None,))
        get_com_member(m,'ClearSelection2',True)
    # ④ 真选：底面固定
    print()
    print("=== 施夹与载荷 ===")
    r1 = sel_face(ext,0.0,0.0,-0.02)
    c1 = get_com_member(get_com_member(m,'SelectionManager'),'GetSelectedObjectCount2',-1)
    rst = sim.apply_fixed_restraint(s, model=m)
    print("  夹具: 选中=%r 计数=%r → 对象=%r" % (r1,c1,rst is not None))
    get_com_member(m,'ClearSelection2',True)
    r2 = sel_face(ext,0.0,0.0,0.0)
    c2 = get_com_member(get_com_member(m,'SelectionManager'),'GetSelectedObjectCount2',-1)
    frc = sim.apply_normal_force(s, model=m, magnitude=100.0)
    print("  载荷: 选中=%r 计数=%r → 对象=%r" % (r2,c2,frc is not None))
    get_com_member(m,'ClearSelection2',True)
    # ⑤ 回读研究的载荷/夹具数（判证据）
    try:
        lm = get_com_member(s,'LoadsAndRestraintsManager')
        print("  LoadsAndRestraintsManager 非空=%r" % (lm is not None))
        for p in ('GetRestraintCount','GetLoadCount','Count'):
            try: print("     %s = %r" % (p, get_com_member(lm,p)))
            except Exception: pass
    except Exception as e: print("  ✗ %s" % str(e)[:50])
    # ⑥ 网格 + 求解
    sz,tl = sim.default_element_size_and_tolerance(s,-1)
    t0=time.time(); mc=get_com_member(s,'CreateMesh',0,float(sz),float(tl))
    print("  CreateMesh=%r 单元=%r %.0fs" % (mc, get_com_member(get_com_member(s,'Mesh'),'ElementCount'), time.time()-t0))
    t1=time.time(); rc=get_com_member(s,'RunAnalysis')
    print("  ★★★ RunAnalysis = %r (%s)  用时 %.0f 秒" % (rc, RUN_ERR.get(rc,'?'), time.time()-t1))
    res = get_com_member(s,'Results')
    print("  ★★★ study.Results 非空 = %r" % (res is not None))
    if res is not None:
        for p in ('GetPlotCount','GetPlotNames'):
            try: print("      %s = %r" % (p, str(get_com_member(res,p))[:150]))
            except Exception as e: print("      %s ✗ %s" % (p, str(e)[:46]))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass