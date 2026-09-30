import sys, time, threading
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
    mg = get_com_member(d,'StudyManager'); n='NF_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    print("  研究 %r  —— 注意：**以下全程不访问 s.Mesh**" % (s is not None))
    # ★ 顺序猜想：CreateMesh(NUnits, DElementSize, DTolerance)
    #   文档是毫米 ⇒ NUnits 取 Metric(2)；尺寸 4.93 mm = 0.00493 m
    TESTS = [
        ("(2, 0.0049339, 0.0002467)  正确顺序·米制", (2, 0.0049339, 0.0002467)),
        ("(2, 4.9339, 0.2467)        正确顺序·毫米", (2, 4.9339, 0.2467)),
        ("(0, 0.0049339, 0.0002467)  正确顺序·SI",   (0, 0.0049339, 0.0002467)),
    ]
    for label, args in TESTS:
        def run():
            try:
                return get_com_member(s,'CreateMesh',*args)
            except Exception as e:
                return "EXC:%s" % str(e)[:60]
        box={}
        th=threading.Thread(target=lambda: box.update(v=run()), daemon=True); th.start()
        t0=time.time()
        while th.is_alive() and time.time()-t0 < 300:
            time.sleep(3)
        if th.is_alive():
            print("  %-40s → 超 300s 未完成（中止）" % label)
            import subprocess; subprocess.run(['powershell','-NoProfile','-Command','Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue'],capture_output=True)
            break
        print("  %-40s → %r   用时 %.0f 秒" % (label, box.get('v'), time.time()-t0))
        if not isinstance(box.get('v'), int):
            break
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass