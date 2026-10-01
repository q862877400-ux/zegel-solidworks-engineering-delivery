import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_spline_redraw.py")
t = P.read_text(encoding="utf-8")

OLD = '''        redrawn = "—"
        try:
            mv = sw_connect.safe_get_com_member(sw, "ActiveView")
            for meth in ("GraphicsRedraw2", "GraphicsRedraw"):
                f = getattr(mv, meth, None)
                if f is None:
                    continue
                f()
                redrawn = meth
                break
        except Exception as exc:      # noqa: BLE001
            redrawn = "EXC:%s" % str(exc)[:40]'''
NEW = '''        redrawn = "—"
        try:
            #: ⚠ `ActiveView` 是**属性**（不是方法）—— 上一版当方法调，报
            #: `EXC:SldWorks.Application.ActiveView` ⇒ **那次重绘没发生**，
            #: 所以"官方说必须重绘"这条解释**当时并未被排除**。
            mv = sw.ActiveView
            for meth in ("GraphicsRedraw2", "GraphicsRedraw"):
                f = getattr(mv, meth, None)
                if f is None:
                    continue
                f()
                redrawn = meth
                break
            if redrawn == "—":
                redrawn = "（两个重绘方法都没有）"
        except Exception as exc:      # noqa: BLE001
            redrawn = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:60])'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)

#: `CreateSpline` 那条要分清"成员不在"与"调用失败"
OLD2 = '''        try:
            r1 = skm.CreateSpline(arr)
            t1 = type(r1).__name__
        except Exception as exc:      # noqa: BLE001
            t1 = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:70])'''
NEW2 = '''        f1 = getattr(skm, "CreateSpline", None)
        if f1 is None:
            t1 = "**迟到绑定里没有这个成员**"
        else:
            try:
                r1 = f1(arr)
                t1 = type(r1).__name__
            except Exception as exc:      # noqa: BLE001
                t1 = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:70])'''
assert OLD2 in t, "第二处锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已修（ActiveView 用属性 + CreateSpline 分清成员在不在）")
