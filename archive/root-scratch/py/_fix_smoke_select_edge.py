import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''        try:
            sw_sketch_edit.convert_entities(asm)
            chk("★ `convert_entities`（**已有实现**，本轮当部件复用）", True, "ok")
        except Exception as exc:      # noqa: BLE001
            chk("convert_entities", False, "%s: %s" % (type(exc).__name__, str(exc)[:100]))'''
NEW = '''        #: ⚠⚠ **`SketchUseEdge3` 用的是当前选择集** ⇒ 必须先**真的选中一条外部边**，
        #: 否则它返回 ok 而草图里**一个实体都没有**（轮 161 实测到这一步才发现）。
        #: ★ 选边走**按对象**（`IEntity.Select4`，事实 32 认可的可行路径），
        #: 而**不是**按名字（`SelectByID2("Edge1","EDGE")` 计数恒 0）。
        sel_ok = False
        try:
            bodies = asm.GetBodies2(0, False)      #: 0 = swSolidBody
            bodies = list(bodies) if bodies else []
            #: 第二个加的组件是「型材」⇒ 取**最后一个**实体的第一条边
            cand = None
            for b in reversed(bodies):
                eds = b.GetEdges()
                eds = list(eds) if eds else []
                if eds:
                    cand = eds[0]
                    break
            if cand is not None:
                sel_ok = bool(cand.Select4(False, sw_part._empty_callout()))
        except Exception as exc:      # noqa: BLE001
            print("     ⚠ 选边异常: %s" % str(exc)[:80])
        chk("★★ 先**选中一条外部边**（`SketchUseEdge3` 的前置条件）", sel_ok,
            "实体数 %d" % (len(bodies) if 'bodies' in dir() else -1))
        try:
            sw_sketch_edit.convert_entities(asm)
            chk("★ `convert_entities`（**已有实现**，本轮当部件复用）", True, "ok")
        except Exception as exc:      # noqa: BLE001
            chk("convert_entities", False, "%s: %s" % (type(exc).__name__, str(exc)[:100]))'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已补「先选外部边」")
