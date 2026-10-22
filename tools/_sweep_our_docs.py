"""★ 一次性清场：关掉**我方**遗留文档（★ 处理「停在草图编辑态」这种拼接标题）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/_sweep_our_docs.py
# 定位:   一次性清场：关掉**我方**遗留文档（★ 处理「停在草图编辑态」这种拼接标题）。
# 官方依据: 不适用（本仓一次性清场工具：只关**我方**打开的文档，不调官方 API 做建模）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main() -> int:
    import sw_connect
    from session_verdict import OURS
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    #: ★ 用 COM 枚举（★ 这一步现在是能用的）✓
    try:
        from sw_session import open_documents
        snap = open_documents(sw)
        docs = [{"title": d.get("title") or "", "path": d.get("path") or ""}
                for d in (snap.get("documents") or [])]
    except Exception as exc:                                            # noqa: BLE001
        print("★ COM 枚举失败：%s" % type(exc).__name__)
        docs = []
    print("★ COM 枚举到 %d 个：" % len(docs))
    for d in docs:
        print("     title=%r path=%r" % (d["title"], d["path"]))

    #: ★★ 标题可能是拼接的（如 `草图1 ← 零件3`）⇒ ★ **从 `←` 后面取零件名** ✓
    def candidates(d):
        t = str(d.get("title") or "")
        out = [t]
        if "\u2190" in t:
            out.append(t.split("\u2190")[-1].strip())
        if t:
            out += [t + ".SLDPRT", t + ".SLDASM"]
        p = str(d.get("path") or "")
        if p:
            out.append(Path(p).name)
            out.append(Path(p).stem)
        return [c for c in out if c]

    others = [d for d in docs if not OURS.search(str(d.get("title") or ""))]
    if others:
        print("★★ 有**非我方**文档 %s ⇒ 一个都不碰，交给人" % [d["title"] for d in others])
        return 3

    closed = []
    for d in docs:
        for name in candidates(d):
            try:
                sw.CloseDoc(name)
            except Exception:                                           # noqa: BLE001
                pass
        #: ★ 关完一个就**退出草图**再试一次（★ 停在编辑态时按名字关不掉）✓
        try:
            m = sw.ActiveDoc
            if m is not None:
                try:
                    m.SketchManager.InsertSketch(True)   # ★ 退出草图
                except Exception:                                   # noqa: BLE001
                    pass
                sw.CloseDoc(str(getattr(m, "GetTitle", lambda: "")() or ""))
        except Exception:                                               # noqa: BLE001
            pass
        closed.append(d["title"] or d["path"])
    print("★ 已请求关闭：%s" % closed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
