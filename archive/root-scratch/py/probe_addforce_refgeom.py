import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4, create_empty_dispatch_variant
from scripts import sw_part, sw_simulation as sim
sw,_m,_x = connect_solidworks(wait_seconds=15, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    d = get_com_member(get_com_member(sw.GetAddInObject('SldWorks.Simulation'),'CosmosWorks'),'ActiveDoc')
    mg = get_com_member(d,'StudyManager'); n='F_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    lrm = get_com_member(s,'LoadsAndRestraintsManager')
    # 先选中一个面，再取参考几何候选
    sw_part._select_by_id(m.Extension,'','FACE')
    disp = sim._selected_dispatch_array(m)
    print("  DispArray 实体数: %d" % len(disp))
    def T(label, fn):
        try:
            r = fn(); print("  %-56s %s %r" % (label, "✓" if r is not None else "○ None", repr(r)[:22])); return r
        except Exception as e:
            print("  %-56s ✗ %s" % (label, str(e)[:44])); return None
    print("=== AddForce 第 3 参的各种形态 ===")
    T("A 空 Dispatch", lambda: get_com_member(lrm,'AddForce',0,disp,create_empty_dispatch_variant(),out_i4()))
    T("B None", lambda: get_com_member(lrm,'AddForce',0,disp,None,out_i4()))
    # C: 用选中的面本身当参考几何
    T("C 用选中的面对象当参考", lambda: get_com_member(lrm,'AddForce',0,disp,disp[0],out_i4()))
    # D: 用基准面当参考（先选中它）
    sw_part._select_by_id(m.Extension,'Front Plane','PLANE')
    planes = sim._selected_dispatch_array(m)
    T("D 用基准面对象当参考", lambda: get_com_member(lrm,'AddForce',0,disp,planes[0] if planes else None,out_i4()))
    # E: 力类型换几个试
    for ft in (0,1,2,3):
        T("E 力类型 %d + 空 Dispatch" % ft, lambda ft=ft: get_com_member(lrm,'AddForce',ft,disp,create_empty_dispatch_variant(),out_i4()))
    print("  Count = %r" % get_com_member(lrm,'Count'))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成")