import sys, time, threading, subprocess
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part, sw_simulation as sim
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
def mem():
    try:
        v=subprocess.run(['powershell','-NoProfile','-Command',"(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | Measure-Object WorkingSet64 -Sum).Sum"],capture_output=True,text=True,timeout=15).stdout.strip()
        return int(int(v)/1048576) if v.isdigit() else 0
    except Exception: return 0
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='OK_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    print("  研究 %r" % (s is not None))
    # ★ 决定性组合：NUnits=0(SI)、ElementSize=4.93mm=0.0049339 m、Tolerance=0.247mm=0.0002467 m
    args = (0, 0.0049339, 0.0002467)
    print("  ★ CreateMesh(0, 0.0049339 m, 0.0002467 m)  —— 正确顺序 + SI + 米级数值")
    box={}
    th=threading.Thread(target=lambda: box.update(v=(lambda: (get_com_member(s,'CreateMesh',*args)) )()), daemon=True)
    th.start(); t0=time.time()
    while th.is_alive() and time.time()-t0 < 420:
        time.sleep(5); print("     ...%.0fs 网格器=%d MB" % (time.time()-t0, mem()))
    if th.is_alive():
        print("  → 超 420s 未完成"); subprocess.run(['powershell','-NoProfile','-Command','Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue'],capture_output=True)
    else:
        print("  → CreateMesh = %r   用时 %.0f 秒" % (box.get('v'), time.time()-t0))
        mesh = get_com_member(s,'Mesh')
        print("  ★ ElementCount = %r" % get_com_member(mesh,'ElementCount'))
        print("  ★ NodeCount    = %r" % get_com_member(mesh,'NodeCount'))
        print("  MeshState=%r IsMeshFailed2=%r" % (get_com_member(mesh,'MeshState'), get_com_member(mesh,'IsMeshFailed2')))
        t1=time.time(); rc = get_com_member(s,'RunAnalysis')
        print("  RunAnalysis = %r  用时 %.0f 秒" % (rc, time.time()-t1))
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