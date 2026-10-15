import sys, time, threading, subprocess
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_simulation as sim
RUN_ERR={0:"Successful",19:"MaterialNotDefined",23:"MeshNotFound",24:"AnalysisFailed"}
def mem():
    try:
        v=subprocess.run(['powershell','-NoProfile','-Command',"(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum"],capture_output=True,text=True,timeout=15).stdout.strip()
        return int(int(v)/1048576) if v.isdigit() else 0
    except Exception: return 0
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='MF_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    print("  研究 %r" % (s is not None))
    print("  零件级材料（前）: MaterialIdName=%r" % get_com_member(m,'MaterialIdName'))
    sm = get_com_member(s,'SolidManager')
    try:
        print("  SolidManager.SolidBodyCount = %r" % get_com_member(sm,"SolidBodyCount"))
    except Exception as e:
        print("  SolidBodyCount 读不到: %s" % str(e)[:50])
    # ★ 用「不依赖选中集」的那个入口
    print()
    print("=== SetFavLibraryMaterialToAllBodiesByCompName('solidworks materials','Plain Carbon Steel','') ===")
    try:
        r = get_com_member(sm,'SetFavLibraryMaterialToAllBodiesByCompName','solidworks materials','Plain Carbon Steel','')
        print("    返回 = %r" % (r,))
    except Exception as e:
        print("    ✗ %s" % str(e)[:80])
    print("  零件级材料（后）: MaterialIdName=%r  MaterialUserName=%r"
          % (get_com_member(m,'MaterialIdName'), get_com_member(m,'MaterialUserName')))
    # 回读实体名
    try:
        cnt = get_com_member(sm,'SolidBodyCount')
        print("  实体数 = %r" % (cnt,))
        for i in range(int(cnt or 0)):
            from win32com.client import VARIANT; import pythoncom
            v = VARIANT(pythoncom.VT_BYREF|pythoncom.VT_I4, 0)
            b = get_com_member(sm,'GetSolidBodyAt', i, v)
            if b is not None:
                print("    实体%d 名=%r" % (i, get_com_member(b,'SolidBodyName')))
    except Exception as e:
        print("  枚举实体 ✗ %s" % str(e)[:60])
    # 夹具+载荷+网格+求解
    sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_fixed_restraint(s, model=m); get_com_member(m,'ClearSelection2',True)
    sw_part._select_by_id(m.Extension,'','FACE',append=False,mark=0); sim.apply_normal_force(s, model=m, magnitude=100.0); get_com_member(m,'ClearSelection2',True)
    sz,tl = sim.default_element_size_and_tolerance(s,-1)
    t0=time.time(); mc=get_com_member(s,'CreateMesh',0,float(sz),float(tl))
    print("  CreateMesh=%r 单元数=%r 用时%.0fs" % (mc, get_com_member(get_com_member(s,'Mesh'),'ElementCount'), time.time()-t0))
    t1=time.time(); rc=get_com_member(s,'RunAnalysis')
    print("  ★ RunAnalysis = %r (%s)  用时 %.0f 秒  峰值内存 %d MB" % (rc, RUN_ERR.get(rc,'?'), time.time()-t1, mem()))
    res = get_com_member(s,'Results')
    print("  ★ study.Results 非空 = %r" % (res is not None))
    if res is not None:
        for p in ('GetPlotCount','GetPlotNames'):
            try: print("    %s = %r" % (p, str(get_com_member(res,p))[:130]))
            except Exception as e: print("    %s ✗ %s" % (p, str(e)[:44]))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass