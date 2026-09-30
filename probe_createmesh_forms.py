import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4
from scripts import sw_part
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='MIN_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    print("  研究 %r" % (s is not None))
    def T(label, fn):
        try:
            r = fn(); print("  %-52s → %r" % (label, r)); return r
        except Exception as e:
            print("  %-52s ✗ %s" % (label, str(e)[:56])); return None
    print("=== CreateMesh 的多种写法（都按毫米给尺寸：size=4.93, tol=0.247）===")
    T("CreateMesh(0, 0.2467, 4.9339)", lambda: get_com_member(s,'CreateMesh',0,0.2467,4.9339))
    T("CreateMesh(0, 0.0, 0.0)", lambda: get_com_member(s,'CreateMesh',0,0.0,0.0))
    T("CreateMesh()（零参）", lambda: get_com_member(s,'CreateMesh'))
    T("MeshAndRun()", lambda: get_com_member(s,'MeshAndRun'))
    print()
    print("=== 直接取属性 / 方法对象看它是什么 ===")
    try:
        raw = getattr(s, 'CreateMesh')
        print("  getattr(s,'CreateMesh') = %r" % (raw,))
    except Exception as e:
        print("  getattr 失败: %s" % str(e)[:70])
    try:
        print("  s.Mesh.ElementCount = %r" % (get_com_member(get_com_member(s,'Mesh'),'ElementCount'),))
    except Exception as e:
        print("  ElementCount 失败: %s" % str(e)[:60])
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass