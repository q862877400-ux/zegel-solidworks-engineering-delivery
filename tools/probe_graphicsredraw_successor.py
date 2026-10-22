"""★ 真机验证 `GraphicsRedraw2` 的后继路径能不能调（★ 改之前先证）。

★ 官方依据（★ 三源里的 `c:\\swapi`，逐条可复核）：
  · `types/IModelDoc2/GraphicsRedraw2.md` 逐字：
    「**Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].**」
  · `types/IModelView/GraphicsRedraw.md` 签名逐字：
    `void GraphicsRedraw( System.object Rect )` —— ★ **比旧的多一个 `Rect`**
  · 该页 `## Parameters` 逐字：「**Rect**: Array of four integers or longs indicating the boundary
    of the region in the SOLIDWORKS graphics window to redraw;」
  · ★★ 官方例子用法（★ 两种都合法）：
    `modelview.GraphicsRedraw(null)`（c#）· `GraphicsRedraw (Empty)`（VB）·
    `swModelView.GraphicsRedraw(rect)`（传 4 元素数组）
★★ 本探针要验的（★ 判据先写死）：
  ★ **PASS** = 三条都成立：① `model.ActiveView` 拿到非 None · ② `GraphicsRedraw(None)` 不抛 ·
    ③ `GraphicsRedraw([0,0,w,h])` 不抛
  ★ **FAIL** = 任一条抛 ⇒ ★★ **如实记"不可换，保留现状"**（★ 绝不硬改）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_graphicsredraw_successor.py
# 定位:   ★ T1b 的第一条：★ 把 `IModelDoc2.GraphicsRedraw2` 换成 `IModelView.GraphicsR
#           edraw`。
# 官方依据: 见上面 docstring（`IModelDoc2/GraphicsRedraw2.md` · `IModelView/GraphicsRedr
# aw.md` ·
# 官方例子 `Apply_and_Remove_Texture_By_Body_Display_State_Example_CSharp.md` 的 `(null)
# `）
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as p  # noqa: E402

OUT = REPO / "output" / "graphicsredraw-successor-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = c.new_document(sw, "part")
        p.start_sketch(doc, plane_name="Front Plane")
        _g(
            _g(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        p.end_sketch(doc)
        names = [n for n in (p.feature_names(doc) or []) if n.startswith("草图")]
        p.extrude_boss(doc, (names[-1] if names else "草图1"), 15.0)

        #: ★ 基线：旧的 `IModelDoc2.GraphicsRedraw2()`
        try:
            r0 = _g(doc, "GraphicsRedraw2")
            R["old_GraphicsRedraw2"] = "★ 能调（ret=%r）" % (r0,)
            R["old_ok"] = True
        except Exception as exc:  # noqa: BLE001
            R["old_GraphicsRedraw2"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            R["old_ok"] = False

        #: ★ ① `model.ActiveView` 拿到没
        view = None
        try:
            view = _g(doc, "ActiveView")
            R["ActiveView"] = "★ %r" % (view,)
            R["get_view_ok"] = view is not None
        except Exception as exc:  # noqa: BLE001
            R["ActiveView"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            R["get_view_ok"] = False

        #: ★ ② `GraphicsRedraw(None)`（★ 官方例子的 `null` / `Empty` / `Nothing` 用法）
        if view is not None:
            try:
                r1 = _g(view, "GraphicsRedraw", None)
                R["GraphicsRedraw_None"] = "★ 能调（ret=%r）" % (r1,)
                R["none_ok"] = True
            except Exception as exc:  # noqa: BLE001
                R["GraphicsRedraw_None"] = "%s: %s" % (
                    type(exc).__name__,
                    str(exc)[:160],
                )
                R["none_ok"] = False
            #: ★ ③ `GraphicsRedraw([0,0,w,h])`（★ 官方例子的 `rect` 用法）
            try:
                r2 = _g(view, "GraphicsRedraw", [0, 0, 800, 600])
                R["GraphicsRedraw_rect"] = "★ 能调（ret=%r）" % (r2,)
                R["rect_ok"] = True
            except Exception as exc:  # noqa: BLE001
                R["GraphicsRedraw_rect"] = "%s: %s" % (
                    type(exc).__name__,
                    str(exc)[:160],
                )
                R["rect_ok"] = False
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    R["verdict"] = (
        "★ PASS —— `ActiveView.GraphicsRedraw(None)` 与 `(rect)` 都能调 ⇒ **可以换**"
        if R.get("get_view_ok") and R.get("none_ok") and R.get("rect_ok")
        else "★★ FAIL —— 至少一条不通 ⇒ **如实记「不可换，保留现状」**"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
