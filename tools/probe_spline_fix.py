"""★ 真机验证：修好后的 `sw_part.sketch_spline` + 新工具 `solidworks_sketch_spline` 能否建成。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。规格 `specs/202-user-coverage-gaps` 的 **R6+**。
# 文件:   tools/probe_spline_fix.py
# 定位:   ★ `scripts/sw_part.sketch_spline` 本轮被修（数组包装 `VARIANT(VT_ARRAY|VT_R8)`）⇒
#   ★ **不能只靠旧探针的读数就宣布修好** —— 本探针**按工具层的契约**调一次修好后的实现，
#   并把判据（草图段数增量）与返回对象的类型如实记下来。
#   官方依据: `C:\swapi\types\ISketchManager\CreateSpline.md`（`PointData` = **扁平 X,Y,Z 序列**，
#     至少两组；2D 草图里 Z 被忽略）
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

OUT = REPO / "output" / "spline-fix-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _segs(doc):
    """★ 段数用**仓内既有助手**读（★ 我第一版写 `SketchManager.GetSketchSegments` —— 那个成员不存在）。"""
    from scripts import sw_sketch as S
    sk = _g(doc, "GetActiveSketch2") or _g(doc, "SketchManager")
    try:
        return len(S.get_sketch_segments(sk) or [])
    except Exception:                                                     # noqa: BLE001
        return len(S.get_sketch_segments(doc) or [])


def main() -> int:
    started = time.time()
    row: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "form": "VARIANT(VT_ARRAY|VT_R8) —— 本轮修进 sw_part.sketch_spline"}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        before = _segs(doc)
        row["seg_before"] = before
        #: ★ 按**工具层的契约**给：`points` = [[x_mm, y_mm], …]（★ 至少两组）
        pts = [[0.0, 0.0], [20.0, 15.0], [40.0, -5.0]]
        row["points_mm"] = pts
        ret = P.sketch_spline(doc, pts)
        row["returned"] = type(ret).__name__ if ret is not None else "None"
        after = _segs(doc)
        row["seg_after"] = after
        row["seg_delta"] = after - before
        row["ok"] = bool(after > before)
        P.end_sketch(doc)
        row["feature_names"] = list(P.feature_names(doc) or [])
    except Exception as exc:                                              # noqa: BLE001
        row["ok"] = False
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    row["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
