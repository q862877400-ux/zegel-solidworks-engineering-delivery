"""★ 一次性：收尾改用 COM 枚举（★ 标题栏只显示一个文档 ⇒ 只关得掉一个）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\close_our_docs.py")
s = p.read_text(encoding="utf-8")

OLD = '''def close_our_documents(connect=None) -> dict:
    """★ 关掉**我方**的打开文档 —— ★ 有非我方文档就**整体拒绝**（不碰任何一个）✓"""
    from session_verdict import OURS, title_documents
    snap = title_documents()
    names = [d["title"] for d in snap["documents"]]
    if not names:
        return {"closed": [], "kept": [], "refused": False, "why": "★ 没有打开文档"}
    mine = [n for n in names if OURS.search(n)]
    others = [n for n in names if n not in mine]'''

NEW = '''def _all_open_documents(sw) -> list:
    """★★ 枚举**全部**已打开文档（★ 优先 COM，退回标题路）—— ★ 返回 `[{"title","path"}]` ✓

    ★★★ 2026-10-06 **真机暴露的缺陷**：★ 我原来用 `title_documents()` 取名字 ——
      ★★ 而 **SolidWorks 的标题栏只显示一个文档** ⇒ ★ 收尾**只关得掉活动的那一个** ✗
      ★ 现场：★ 标定跑建了 `零件1..零件10` ⇒ ★ 收尾只关了 `零件10` ⇒
      ★★ 下一次预检读到 **9 个非我方文档** ⇒ **门禁拒绝一切**（★ 门禁没错，★ 是我没关干净）✓
    ⇒ ★ 正解：★ 用**现在已能工作的 COM 枚举**（`sw_session.open_documents`）✓
    """
    try:
        try:
            from sw_session import open_documents
        except ImportError:
            from scripts.sw_session import open_documents
        snap = open_documents(sw)
        docs = [{"title": d.get("title") or "", "path": d.get("path") or ""}
                for d in (snap.get("documents") or [])]
        if docs:
            return docs
    except Exception:                                                   # noqa: BLE001
        pass
    from session_verdict import title_documents
    return [{"title": d["title"], "path": ""} for d in title_documents()["documents"]]


def close_our_documents(connect=None) -> dict:
    """★ 关掉**我方**的打开文档 —— ★ 有非我方文档就**整体拒绝**（不碰任何一个）✓"""
    from session_verdict import OURS
    if connect is None:
        import sw_connect
        sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    else:
        sw = connect
    if sw is None:
        return {"closed": [], "kept": [], "refused": True, "why": "★ 连不上 ⇒ 不动手"}
    docs = _all_open_documents(sw)
    names = [d["title"] or d["path"] for d in docs]
    if not names:
        return {"closed": [], "kept": [], "refused": False, "why": "★ 没有打开文档"}

    def _is_ours(d):
        #: ★ 名字命中约定 ⇒ 我方；★ 否则若**路径**命中沙盒 ⇒ 也算我方（★ 我们只在沙盒里开）✓
        if OURS.search(str(d.get("title") or "")):
            return True
        path = str(d.get("path") or "")
        return bool(path) and "sandbox" in path.lower()

    mine = [n for n, d in zip(names, docs) if _is_ours(d)]
    others = [n for n, d in zip(names, docs) if not _is_ours(d)]'''

assert OLD in s, "close_our_documents 的头没匹配上"
s = s.replace(OLD, NEW)

#: ★ 后面那段"连一次"要拿掉（前面已经连过）
OLD2 = """    if connect is None:
        import sw_connect
        sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    else:
        sw = connect
    if sw is None:
        return {"closed": [], "kept": names, "refused": True, "why": "★ 连不上 ⇒ 不动手"}
    closed = []"""
NEW2 = """    closed = []"""
assert OLD2 in s, "后面的连接块没匹配上"
s = s.replace(OLD2, NEW2)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("收尾已改用 COM 枚举（★ 并加了"路径在沙盒里也算我方"的兜底）".replace('"', "「", 1).replace('"', "」", 1))
