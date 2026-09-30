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
    mg = get_com_member(d,'StudyManager'); n='S_%d'%int(time.time())
    get_com_member(mg,'DeleteStudy',n); s = get_com_member(mg,'CreateNewStudy3',n,0,0,out_i4())
    lrm = get_com_member(s,'LoadsAndRestraintsManager')
    sw_part._select_by_id(m.Extension,'','FACE')
    disp = sim._selected_dispatch_array(m)
    f = get_com_member(lrm,'AddForce',1,disp,create_empty_dispatch_variant(),out_i4())
    print("  AddForce(type=1) → %r" % (f is not None))
    get_com_member(f,'ForceBeginEdit'); print("  ForceBeginEdit ✓")
    def T(label, fn):
        try:
            fn(); print("  %-40s ✓" % label)
        except Exception as e:
            print("  %-40s ✗ %s" % (label, str(e)[:56]))
    print("=== setter 形态 ===")
    T("get_com_member(f,'set_ForceType',1)", lambda: get_com_member(f,'set_ForceType',1))
    T("get_com_member(f,'put_ForceType',1)", lambda: get_com_member(f,'put_ForceType',1))
    T("f.ForceType = 1（属性赋值）", lambda: setattr(f,'ForceType',1))
    T("get_com_member(f,'set_Unit',0)", lambda: get_com_member(f,'set_Unit',0))
    T("setattr(f,'Unit',0)", lambda: setattr(f,'Unit',0))
    T("get_com_member(f,'set_NormalForceOrTorqueValue',100.0)", lambda: get_com_member(f,'set_NormalForceOrTorqueValue',100.0))
    T("setattr(f,'NormalForceOrTorqueValue',100.0)", lambda: setattr(f,'NormalForceOrTorqueValue',100.0))
    print("=== 回读 ===")
    for rd in ('ForceType','Unit','NormalForceOrTorqueValue','get_ForceType'):
        try: print("  %-28s = %r" % (rd, get_com_member(f, rd)))
        except Exception as e: print("  %-28s ✗ %s" % (rd, str(e)[:40]))
    print("  ForceEndEdit = %r" % (get_com_member(f,'ForceEndEdit'),))
    print("  Count = %r" % get_com_member(lrm,'Count'))
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass
    print("  收尾完成")