import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_simulation as sim
RUN_ERR={0:"Successful",19:"MaterialNotDefined",23:"MeshNotFound",24:"AnalysisFailed"}
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    print("  零件 %r" % t)
    print()
    print("=== 试各种「库名 × 材料名」组合，**以 MaterialIdName 回读为准** ===")
    ok=None
    for db in ("SOLIDWORKS Materials","SolidWorks Materials","solidworks materials",
               "SOLIDWORKS Materials.sldmat"):
        for mat in ("Plain Carbon Steel","AISI 1020","Alloy Steel"):
            try:
                get_com_member(m,'SetMaterialPropertyName2','',db,mat)
            except Exception as e:
                print("  db=%-30r mat=%-20r ✗ %s" % (db,mat,str(e)[:40])); continue
            v = get_com_member(m,'MaterialIdName')
            u = get_com_member(m,'MaterialUserName')
            print("  db=%-30r mat=%-20r → IdName=%r UserName=%r" % (db,mat,v,u))
            if v and not ok: ok=(db,mat)
            if ok: break
        if ok: break
    print()
    print("  ⇒ 生效的组合: %r" % (ok,))
    if ok:
        d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
        mg = get_com_member(d,'StudyManager'); n='FIN_%d'%int(time.time())
        get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
        sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_fixed_restraint(s, model=m); get_com_member(m,'ClearSelection2',True)
        sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_normal_force(s, model=m, magnitude=100.0); get_com_member(m,'ClearSelection2',True)
        sz,tl = sim.default_element_size_and_tolerance(s,-1)
        t0=time.time(); mc=get_com_member(s,'CreateMesh',0,float(sz),float(tl))
        print("  CreateMesh=%r 单元数=%r 用时%.0fs" % (mc, get_com_member(get_com_member(s,'Mesh'),'ElementCount'), time.time()-t0))
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