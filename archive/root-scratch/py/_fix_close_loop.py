"""★ 一次性：让 close_our_documents 循环清到没有为止（★ 一次枚举可能只看到一个）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\close_our_docs.py")
s = p.read_text(encoding="utf-8")

OLD = """    closed = []
    for n in mine:
        for cand in (n, n + ".SLDPRT", n + ".SLDASM", n + ".SLDDRW"):
            try:
                sw.CloseDoc(cand)
            except Exception:                                           # noqa: BLE001
                pass
        closed.append(n)
    return {"closed": closed, "kept": [], "refused": False, "why": ""}"""

NEW = """    #: ★★★ **循环清到没有为止**（★ 真机踩过：★ 一次枚举**可能只看到一个** ⇒
    #:   只关一个就走 ⇒ ★★ 下一次预检读到一堆"非我方" ⇒ **门禁拒绝一切** ✗）
    #:   ⇒ ★ 每轮**重新枚举**，★ 最多 `MAX_ROUNDS` 轮；★ 任一轮见到**非我方**就立刻停手 ✓
    closed, rounds = [], 0
    mine_seen = list(mine)
    while rounds < 8:
        rounds += 1
        for n in (mine or []):
            for cand in (n, n + ".SLDPRT", n + ".SLDASM", n + ".SLDDRW"):
                try:
                    sw.CloseDoc(cand)
                except Exception:                                       # noqa: BLE001
                    pass
        #: ★ 关完一个**退出草图**再试一次（★ 停在编辑态时按名字关不掉）✓
        try:
            m = sw.ActiveDoc
            if m is not None:
                try:
                    m.SketchManager.InsertSketch(True)
                except Exception:                                       # noqa: BLE001
                    pass
                for cand in (str(getattr(m, "GetTitle", lambda: "")() or ""),
                             str(getattr(m, "GetPathName", lambda: "")() or "")):
                    if cand:
                        try:
                            sw.CloseDoc(cand)
                        except Exception:                               # noqa: BLE001
                            pass
        except Exception:                                               # noqa: BLE001
            pass
        closed += [n for n in (mine or []) if n not in closed]
        docs = _all_open_documents(sw)
        names = [d["title"] or d["path"] for d in docs]
        if not names:
            break
        mine = [n for n, d in zip(names, docs) if _is_ours(d)]
        others = [n for n, d in zip(names, docs) if not _is_ours(d)]
        if others:
            return {"closed": closed, "kept": names, "refused": True, "rounds": rounds,
                    "why": "★★ 关的过程中见到**非我方**文档 %s ⇒ 停手（★ 一个都不碰）" % others}
        if not mine:
            break
    return {"closed": closed, "kept": [], "refused": False, "rounds": rounds,
            "why": "", "first_seen": mine_seen}"""

assert OLD in s, "收尾关闭块没匹配上"
s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("收尾已改成循环清到没有为止")
