"""★ 关掉**我方**打开的文档（★ 一个都不碰别人的；★ 有非我方的就停手交人）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/close_our_docs.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5**（收尾纪律那一半）。★ 起因（真机）：
#   ★★ 探针跑完**留下一个我方未保存的文档** ⇒ ★ 下一次预检就把**它自己**判成"非我方"
#     （★ 因为它在 COM 路上**没有路径**、而标题路认得它）⇒ ★ **门禁把自己人挡在门外** ✗
#   ★ 根因不是门禁错，★ 而是**我没收尾** —— ★ 本仓纪律原话：「**收尾必做** …… **关掉自己开的文档**」✓
# 判据:   ★★ **只关我方的**（按共用正则 `session_verdict.OURS`，★ 一处实现）·
#   ★ **只要有非我方文档就整体停下**（★ 一个都不碰）· ★ **不保存**（★ 关掉即丢弃，★ 只丢我方的临时件）✓
#   ★ 回 `{"closed": [...], "kept": [...], "refused": bool, "why": str}` ✓
# 官方依据: `ISldWorks.CloseDoc(Name)`（已读该页：★ 关指定文档；★ 名字见 Remarks）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def close_our_documents(connect=None) -> dict:
    """★ 关掉**我方**的打开文档 —— ★ 有非我方文档就**整体拒绝**（不碰任何一个）✓"""
    from session_verdict import OURS, title_documents
    snap = title_documents()
    names = [d["title"] for d in snap["documents"]]
    if not names:
        return {"closed": [], "kept": [], "refused": False, "why": "★ 没有打开文档"}
    mine = [n for n in names if OURS.search(n)]
    others = [n for n in names if n not in mine]
    if others:
        #: ★★ 别人的一个都不碰 —— ★ 连我方的也不关（★ 免得在混着的时候动会话）✓
        return {"closed": [], "kept": names, "refused": True,
                "why": "★★ 有**非我方**文档 %s ⇒ 不碰任何文档（★ 交给人处置）" % others}
    if connect is None:
        import sw_connect
        sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    else:
        sw = connect
    if sw is None:
        return {"closed": [], "kept": names, "refused": True, "why": "★ 连不上 ⇒ 不动手"}
    closed = []
    for n in mine:
        for cand in (n, n + ".SLDPRT", n + ".SLDASM", n + ".SLDDRW"):
            try:
                sw.CloseDoc(cand)
            except Exception:                                           # noqa: BLE001
                pass
        closed.append(n)
    return {"closed": closed, "kept": [], "refused": False, "why": ""}


def main() -> int:
    r = close_our_documents()
    print("★ 关掉我方的：%s" % (r["closed"] or "（无）"))
    if r["refused"]:
        print(r["why"])
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
