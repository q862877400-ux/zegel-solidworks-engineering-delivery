import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\prove_shut_off_surface.py")
t = p.read_text(encoding="utf-8")

#: ★ 在"打孔"与"关断面"之间插入**分型线 + 分型面**两步（★ 轮 391 的假设）
OLD = """        #: ② 关断面（★ 零参）"""
NEW = """        #: ①b ★★ **轮 391 的假设**：`shut_off` 属于**模具流程的一环** ⇒ 先建**分型线 + 分型面**
        #:   （★ 轮 390/391 两次都只打孔、没建它们）。★ 手法照事实 306：mark=1 选方向、mark=4 按**中点**选边。
        ext = get_com_member(doc, "Extension")
        callout = sw_connect.create_empty_dispatch_variant()
        doc.ClearSelection2(True)
        ext.SelectByID2("前视基准面", "PLANE", 0, 0, 0, False, 1, callout, 0)
        ms = []
        for b in (get_com_member(doc, "GetBodies2", -1, True) or []):
            for e in (get_com_member(b, "GetEdges") or []):
                try:
                    a = [float(x) for x in get_com_member(
                        get_com_member(e, "GetStartVertex"), "GetPoint")]
                    c = [float(x) for x in get_com_member(
                        get_com_member(e, "GetEndVertex"), "GetPoint")]
                    ms.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                except Exception:                              # noqa: BLE001
                    continue
        ztop = max(m[2] for m in ms) if ms else None
        for m in ms:
            if ztop is not None and abs(m[2] - ztop) < 1e-9:
                ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, 4, callout, 0)
        try:
            ev["steps"]["pre_parting_line"] = {"ok": True,
                                               "feature": str(M.insert_parting_line(doc))[:40]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["pre_parting_line"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}
        try:
            ev["steps"]["pre_parting_surface"] = {
                "ok": True, "feature": str(M.insert_parting_surface(doc))[:40]}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["pre_parting_surface"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}

        #: ② 关断面（★ 零参）"""

if "pre_parting_line" not in t:
    t = t.replace(OLD, NEW, 1)
    p.write_text(t, encoding="utf-8")
    print("  已插入分型线 + 分型面两步")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
