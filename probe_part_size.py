import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork"); sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.sw_connect import connect_solidworks, get_com_member, new_document
from scripts import sw_part
sw,_m,_x = connect_solidworks(wait_seconds=20, return_metadata=True)
sw.CommandInProgress = True
t=None
try:
    m = new_document(sw, doc_type='part'); t = get_com_member(m,'GetTitle')
    sk = sw_part.sketch(m,'Front Plane'); sw_part.sketch_corner_rectangle(m,-0.05,-0.03,0.05,0.03); sw_part.extrude_boss(m,sk,0.02)
    # ① 文档单位制
    print("  文档长度单位（swUserPreferenceIntegerValue 第 46 项 = swUnitsLinear）:")
    try:
        print("    = %r" % get_com_member(sw, "GetUserPreferenceIntegerValue", 46))
    except Exception as e:
        print("    ✗ %s" % str(e)[:60])
    # ② 零件包围盒（GetBodyBox 返回米制）
    bodies = get_com_member(m, "GetBodies2", 0, True)
    print("  实体数: %d" % len(bodies or []))
    if bodies:
        try:
            bb = get_com_member(bodies[0], "GetBodyBox")
            if bb:
                xs = bb[0::3]; ys = bb[1::3]; zs = bb[2::3]
                print("  包围盒（API 原始值）: X[%.6g, %.6g] Y[%.6g, %.6g] Z[%.6g, %.6g]"
                      % (bb[0],bb[3],bb[1],bb[4],bb[2],bb[5]))
                print("  ⇒ 尺寸 = %.6g × %.6g × %.6g （API 单位）" % (bb[3]-bb[0], bb[4]-bb[1], bb[5]-bb[2]))
                print("  ⇒ 若 API 单位是米: %.2f × %.2f × %.2f mm" % ((bb[3]-bb[0])*1000, (bb[4]-bb[1])*1000, (bb[5]-bb[2])*1000))
        except Exception as e:
            print("  GetBodyBox ✗ %s" % str(e)[:60])
    # ③ 质量属性（体积）
    try:
        ext = get_com_member(m, "Extension")
        mp = get_com_member(ext, "GetMassProperties2", 1, 0, False)
        if mp: print("  GetMassProperties2: 体积=%.6g 表面积=%.6g 质量=%.6g" % (mp[3], mp[4], mp[5]))
    except Exception as e:
        print("  GetMassProperties2 ✗ %s" % str(e)[:60])
finally:
    try:
        if t: sw.CloseDoc(t)
    except Exception: pass
    try: sw.CommandInProgress = False
    except Exception: pass