import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_composite_curve_edges.py")
t = P.read_text(encoding="utf-8")

#: ⚠ 第一版用 `IEntity.Select4` —— 它**没有 mark 参数**，而官方 Remarks 要求 **mark = 1**
#: ⇒ 那一条**前提可能没满足**。★ 补上「按点选 + mark=1」（事实 32 的另一条可行路径）。
OLD = '''        #: ③ 调它
        if cnt2 >= 2:'''
NEW = '''        #: ②b ★ 按**面上的点**选边，并且 **mark = 1**（官方 Remarks 明确要求）
        #: ⚠ `IEntity.Select4` **没有 mark 参数** ⇒ 上面那次选**可能不算数**
        #: ⇒ 这一条才是「按官方要求」的形态（事实 32：按点选边是可行路径）
        pts = [(0.025, 0.0, 0.0), (0.05, 0.025, 0.0),   #: 底面两条相邻棱的中点
               (0.0, 0.025, 0.0), (0.025, 0.05, 0.0)]
        doc.ClearSelection2(True)
        picked = 0
        for (x, y, z) in pts[:2]:
            try:
                if doc.Extension.SelectByID2("", "EDGE", x, y, z, True, 1, callout, 0):
                    picked += 1
            except Exception as exc:      # noqa: BLE001
                print("     ⚠ 按点选边异常: %s" % str(exc)[:60])
        cnt3 = 0
        try:
            cnt3 = int(doc.SelectionManager.GetSelectedObjectCount2(1))   #: ★ mark = 1
        except Exception:      # noqa: BLE001
            pass
        print("  ②b **按点 + mark=1** 选 2 条棱 ⇒ 命中 %d · **mark=1 的计数** %d"
              % (picked, cnt3))
        ev["by_point_mark1_selected"] = picked
        ev["mark1_count"] = cnt3
        cnt2 = max(cnt2, cnt3)

        #: ③ 调它
        if cnt2 >= 2:'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已补「按点 + mark=1」那条路径")
