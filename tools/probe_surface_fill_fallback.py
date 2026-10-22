"""★ 真机验证 `surface_fill` 的回退：**给了 `selection`** 时该回退并**建成**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps`。
# 文件:   tools/probe_surface_fill_fallback.py
# 定位:   ★★★ 事实 503 说「调用方预选」经工具层不可能成立；★ 而 `surface_fill` 的**声
#           明式分支**
#   恰恰只回读选区 ⇒ ★ 上一版**只要传 `selection` 就必失败**。
#   ★ 本轮把它改成「拿不到就**回退**到自动路」，★ 本探针验的就是这条回退。
#   官方依据: `C:\\swapi\\types\\IFeatureManager\\InsertFillSurface2.md`（边界边用 **mark 1**）
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

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "surface-fill-fallback-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _plate_with_hole(doc):
    """★ 造一块**中间有圆孔**的板 —— ★ 填充要的就是那一圈孔边。"""
    P.start_sketch(doc, plane_name="Front Plane")
    sm = _g(doc, "SketchManager")
    _g(sm, "CreateCornerRectangle", -0.05, -0.03, 0.0, 0.05, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
    P.extrude_boss(doc, (names[-1] if names else "草图1"), 10.0)
    P.start_sketch(doc, plane_name="Front Plane")
    _g(_g(doc, "SketchManager"), "CreateCircleByRadius", 0.0, 0.0, 0.0, 0.02)
    P.end_sketch(doc)
    names2 = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
    P.extrude_cut(doc, (names2[-1] if names2 else "草图2"), 0.0)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    #: ★★★ 第三例的关键：**先显式清掉选区**再调 —— ★ 这才**复现了工具层的条件**。
    #:   ★★ 为什么必须这样：`RESOLVERS["model"]` 经 `connect_solidworks()` **会清空选区**
    #:     （事实 503，证据 `output/selection-lifetime-evidence.json`）。
    #:   ★ 而本探针**直接调能力层**、绕过了那个解析器 ⇒ 造零件留下的**残余选择**会骗过
    #:     `_selected_readback`（★ 实测：第二例回读 > 0 ⇒ 回退不触发 ⇒ 拿到一圈**错的**边界）。
    #:   ⇒ ★ **清掉再调**，才是经工具层时真正会发生的样子。
    for label, sel, do_clear in (("selection 为空（自动路）", "", False),
                                 ("selection 非空 + 残余选择未清（对照）", "index:0", False),
                                 ("★ selection 非空 + 先清选区（= 工具层条件）", "index:0", True)):
        doc = None
        row: dict = {"case": label, "selection": sel}
        try:
            doc = C.new_document(sw, "part")
            _plate_with_hole(doc)
            row["features_before"] = len(list(P.feature_names(doc) or []))
            if do_clear:
                _g(doc, "ClearSelection2", True)
                row["cleared_before_call"] = True
                row["sel_readback_after_clear"] = int(
                    _g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0)
            from scripts.sw_surface_features import insert_fill_surface_report
            ret = insert_fill_surface_report(doc, 2, options=1, selection=sel)
            row["ok"] = bool(isinstance(ret, dict) and ret.get("ok"))
            if isinstance(ret, dict):
                for k in ("stage", "points_selected", "new_features",
                          "fallback_from_declarative", "tree_before", "tree_after",
                          "error", "stage"):
                    if k in ret:
                        row[k] = ret[k]
        except Exception as exc:                                          # noqa: BLE001
            row["ok"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:                                             # noqa: BLE001
                pass
        R["cases"].append(row)
    R["passed"] = sum(1 for r in R["cases"] if r.get("ok"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
