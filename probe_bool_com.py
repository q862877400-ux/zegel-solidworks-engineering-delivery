import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document
from scripts import sw_part, sw_topology as topo
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    study, entry = topo.create_topology_study(sw, "BOOL_%d" % int(time.time()))
    r = topo.set_topology_goal(study, goal_type=topo.TP_GOAL_MAXIMIZE_STIFFNESS, mass_reduce_percent=75.0)
    print("  set_topology_goal 返回的键值：")
    for k, v in r.items():
        print("    %-26s type=%-22s is_not_None=%-5s bool()=%-5s repr=%s"
              % (k, type(v).__name__, v is not None, bool(v), str(v)[:40]))
    print()
    g = r.get('goal'); mc = r.get('mass_constraint')
    print("  ★ 关键对比：")
    print("    bool(goal)                    = %s   ← 我原判据用的就是这个" % bool(g))
    print("    goal is not None              = %s   ← 正确的判据" % (g is not None))
    print("    bool(mass_constraint)         = %s" % bool(mc))
    print("    mass_constraint is not None   = %s" % (mc is not None))
    if g is not None:
        try:
            print("    goal 的成员可用性: GetName=%r" % str(get_com_member(g,'GetName'))[:40])
        except Exception as e:
            print("    goal.GetName ✗ %s" % str(e)[:40])
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass