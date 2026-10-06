"""★ 关掉**我方**打开的文档（★ 一个都不碰别人的；★ 有非我方的就停手交人）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/close_our_docs.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5**（收尾纪律那一半）。★ 起因（真机）：
#   ★★ 探针跑完**留下我方文档** ⇒ ★ 下一次预检把它判成「非我方」 ⇒
#     ★★ **门禁把自己人挡在门外** ✗ —— ★ 根因不是门禁错，★ 是**我没收尾** ✓
#   ★★★ 两处真机踩过的坑（都写在这里，★ 免得重犯）：
#     ① ★ 我一开始按**窗口标题**取名字 ⇒ ★★ SolidWorks 标题栏**只显示一个文档** ⇒
#        ★ 收尾**只关得掉活动的那一个** ⇒ 下次预检读到一堆「非我方」 ⇒ 门禁拒绝一切 ✗
#        ⇒ ★ 正解：★ **用 COM 枚举**（`sw_session.open_documents`）✓
#     ② ★ 即便用了 COM，★ **一次枚举也可能只看到一个** ⇒ ★ 所以要**循环清到没有为止** ✓
# 判据:   ★★ **只关我方的**（★ 按共用正则 `session_verdict.OURS`，★ 一处实现；
#     ★ 路径在沙盒里**也算我方**）· ★ **只要有非我方文档就整体停下**（★ 一个都不碰）·
#   ★ **不保存**（★ 关掉即丢弃，★ 只丢我方的临时件）· ★ 每轮**重新枚举**、最多 `MAX_ROUNDS` 轮 ✓
#   ★ 回 `{"closed", "kept", "refused", "rounds", "why"}` ✓
# 官方依据: `ISldWorks.CloseDoc(Name)`（已读该页：★ 关指定文档；★ 名字见 Remarks）✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 最多清几轮（★ 防病态循环；★ 正常一两轮就空了）✓
MAX_ROUNDS = 8


def _is_ours(doc) -> bool:
    """★ 是不是**我方**的文档 —— ★ 名字命中约定，★ 或**路径在沙盒里**（★ 我们只在沙盒里开）✓"""
    from session_verdict import OURS
    if OURS.search(str((doc or {}).get("title") or "")):
        return True
    path = str((doc or {}).get("path") or "")
    return bool(path) and "sandbox" in path.lower()


def _all_open_documents(sw) -> list:
    """★★ 枚举**全部**已打开文档（★ 优先 COM，退回标题路）—— ★ 返回 `[{"title","path"}]` ✓

    ★★ 为什么必须优先 COM：★ 标题栏**只显示一个文档**，★ 而且**会给出拼接名**
      （★ 文档停在草图编辑态时形如 `草图1 ← 零件3`）⇒ ★ 按名字**关不掉** ✓
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
    if connect is None:
        import sw_connect
        sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    else:
        sw = connect
    if sw is None:
        return {"closed": [], "kept": [], "refused": True, "rounds": 0, "why": "★ 连不上 ⇒ 不动手"}

    docs = _all_open_documents(sw)
    if not docs:
        return {"closed": [], "kept": [], "refused": False, "rounds": 0, "why": "★ 没有打开文档"}
    others = [d["title"] or d["path"] for d in docs if not _is_ours(d)]
    if others:
        #: ★★ 别人的一个都不碰 —— ★ 连我方的也不关（★ 免得在混着的时候动会话）✓
        return {"closed": [], "kept": [d["title"] or d["path"] for d in docs],
                "refused": True, "rounds": 0,
                "why": "★★ 有**非我方**文档 %s ⇒ 不碰任何文档（★ 交给人处置）" % others}

    closed, rounds = [], 0
    while rounds < MAX_ROUNDS:
        rounds += 1
        current = _all_open_documents(sw)
        mine = [d for d in current if _is_ours(d)]
        if [d for d in current if not _is_ours(d)]:
            return {"closed": sorted(set(closed)),
                    "kept": [d["title"] or d["path"] for d in current if not _is_ours(d)],
                    "refused": True, "rounds": rounds,
                    "why": "★★ 关的过程中见到**非我方**文档 ⇒ 停手（★ 一个都不碰）"}
        if not mine:
            break
        for d in mine:
            title = str(d.get("title") or "")
            path = str(d.get("path") or "")
            name = title or (Path(path).name if path else "")
            cands = [c for c in (name, title, Path(path).name if path else "",
                                 Path(path).stem if path else "") if c]
            for cand in cands:
                for suffix in ("", ".SLDPRT", ".SLDASM", ".SLDDRW"):
                    try:
                        sw.CloseDoc(cand + suffix)
                    except Exception:                                   # noqa: BLE001
                        pass
            if name:
                closed.append(name)
        #: ★ 关完一个**退出草图**再试一次（★ 停在编辑态时按名字关不掉）✓
        try:
            m = sw.ActiveDoc
            if m is not None:
                try:
                    m.SketchManager.InsertSketch(True)
                except Exception:                                       # noqa: BLE001
                    pass
                t = str(getattr(m, "GetTitle", lambda: "")() or "")
                if t:
                    try:
                        sw.CloseDoc(t)
                    except Exception:                                   # noqa: BLE001
                        pass
        except Exception:                                               # noqa: BLE001
            pass
    return {"closed": sorted(set(closed)), "kept": [], "refused": False,
            "rounds": rounds, "why": ""}


def main() -> int:
    r = close_our_documents()
    print("★ 关掉我方的：%s（★ %d 轮）" % (r["closed"] or "（无）", r.get("rounds", 0)))
    if r["refused"]:
        print(r["why"])
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
