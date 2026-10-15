import sys, time, subprocess
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4, set_com_member
from scripts import sw_part, sw_simulation as sim
RUN_ERR={0:"Successful",19:"MaterialNotDefined",23:"MeshNotFound",24:"AnalysisFailed"}
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    print("  零件 %r ; 材料初值 MaterialIdName=%r" % (t, get_com_member(m,'MaterialIdName')))
    partdoc = m            # IPartDoc 与 IModelDoc2 同对象
    ok = False
    # ── 路径 A：IPartDoc.SetMaterialPropertyName2(config, database, name)
    for cfg in ('', 'Default'):
        if ok: break
        try:
            get_com_member(partdoc,'SetMaterialPropertyName2', cfg, 'solidworks materials', 'Plain Carbon Steel')
            v = get_com_member(m,'MaterialIdName')
            print("  A SetMaterialPropertyName2(cfg=%r) → 回读 MaterialIdName=%r" % (cfg, v))
            if v: ok = True
        except Exception as e:
            print("  A cfg=%r ✗ %s" % (cfg, str(e)[:62]))
    # ── 路径 B：set_MaterialIdName（直接写属性）
    if not ok:
        for prop, val in (('MaterialIdName','Plain Carbon Steel'), ('MaterialUserName','Plain Carbon Steel')):
            try:
                set_com_member(m, prop, val)
                print("  B 写 %s ← %r → 回读 %r" % (prop, val, get_com_member(m,prop)))
                if get_com_member(m,'MaterialIdName'): ok = True
            except Exception as e:
                print("  B %s ✗ %s" % (prop, str(e)[:62]))
    # ── 路径 C：SetMaterialPropertyName（两参的老版本）
    if not ok:
        try:
            get_com_member(partdoc,'SetMaterialPropertyName','solidworks materials','Plain Carbon Steel')
            print("  C SetMaterialPropertyName → 回读 %r" % get_com_member(m,'MaterialIdName'))
            if get_com_member(m,'MaterialIdName'): ok = True
        except Exception as e:
            print("  C ✗ %s" % str(e)[:62])
    print()
    print("  ⇒ 材料是否赋上: %s" % ('✓ 是' if ok else '✗ 否'))
    if not ok:
        print("  ⇒ 材料没赋上 ⇒ 直接结束（不必再跑网格/求解）")
    else:
        d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
        mg = get_com_member(d,'StudyManager'); n='SLV_%d'%int(time.time())
        get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
        sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_fixed_restraint(s, model=m); get_com_member(m,'ClearSelection2',True)
        sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_normal_force(s, model=m, magnitude=100.0); get_com_member(m,'ClearSelection2',True)
        sz,tl = sim.default_element_size_and_tolerance(s,-1)
        t0=time.time(); mc=get_com_member(s,'CreateMesh',0,float(sz),float(tl))
        print("  CreateMesh=%r 单元数=%r 用时%.0fs" % (mc, get_com_member(get_com_member(s,'Mesh'),'ElementCount'), time.time()-t0))
        t1=time.time(); rc=get_com_member(s,'RunAnalysis')
        print("  ★★ RunAnalysis = %r (%s)  用时 %.0f 秒" % (rc, RUN_ERR.get(rc,'?'), time.time()-t1))
        res = get_com_member(s,'Results')
        print("  ★★ study.Results 非空 = %r" % (res is not None))
        if res is not None:
            for p in ('GetPlotCount','GetPlotNames'):
                try: print("     %s = %r" % (p, str(get_com_member(res,p))[:140]))
                except Exception as e: print("     %s ✗ %s" % (p, str(e)[:46]))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass