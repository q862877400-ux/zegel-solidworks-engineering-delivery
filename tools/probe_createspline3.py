"""★ 真机验：`CreateSpline3`（★ 现行的那个）**到底能不能调**（★ 阶段 2 · T1 第 ② 步）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISketchManager\CreateSpline3.md`）
# 文件:   `scripts/sw_connect.py::out_dispatch` / `create_empty_dispatch_variant` ·
#         `scripts/sw_part.py::sketch_spline`
# 定位:   ★ `scripts/sw_part.py` 的 docstring 逐字说：
#     「★ `CreateSpline2` 官方已标 **Obsolete**（★ 后继 `CreateSpline3` 末参是 **BYREF `Object&`**、
#      ★ **pywin32 到不了**）⇒ ★ **能用的是这个已废弃的 `CreateSpline2`**」✓
#   ★★ **而本仓**有 `out_dispatch()`** ⇒ ★★★ **那个说法**要验****（★ 逐条流程第 ② 步）✓
#   ★★★ **官方逐字**（★ `CreateSpline3.md`）：
#     `CreateSpline3(object PointData, object Surfs, object Direction, bool SimulateNaturalEnds,
#      out object Status)` ⇒ **5 参** ·
#     ★★ Remarks 逐字：★ 「To create a **2D spline**… ★ **All other parameters with null or Nothing.**」✓
#   ★★★★ **判据（★ 可核）**：★ 建成 ⇒ **草图段数 +1**（★ 而那正是本仓既有的判据）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "createspline3-probe-evidence.json"


def _seg_count(model) -> int:
    """★ 现成的段数读法（★ 与 `sw_part` 同一路）。"""
    try:
        from sw_connect import get_com_member
        sk = get_com_member(model, "SketchManager")
        act = get_com_member(sk, "ActiveSketch")
        if act is None:
            return -1
        raw = get_com_member(act, "GetSketchSegments")
        return len(list(raw)) if raw is not None else 0
    except Exception:                                                     # noqa: BLE001
        return -1


def main() -> int:
    import sw_part as P
    from sw_connect import (connect_solidworks, get_com_member, new_document,
                            out_dispatch, create_empty_dispatch_variant)

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    rows = []

    def case(tag, *, form):
        """★ 每种形态单独建一张草图（★ 免得互相干扰）。"""
        P.sketch(model, "Front Plane")
        before = _seg_count(model)
        sk = get_com_member(model, "SketchManager")
        pts = [0.0, 0.0, 0.0, 0.05, 0.03, 0.0, 0.10, 0.0, 0.0]   #: 三点、单位**米**
        from win32com.client import VARIANT
        import pythoncom
        data = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, pts)
        got = err = None
        try:
            if form == "v3_out_dispatch":
                #: ★ 官方 Remarks：2D 样条 ⇒ **其余参数一律 null/Nothing** ✓
                got = get_com_member(sk, "CreateSpline3", data, None, None, False, out_dispatch())
            elif form == "v3_empty_dispatch":
                got = get_com_member(sk, "CreateSpline3", data, None, None, False,
                                     create_empty_dispatch_variant())
            elif form == "v3_plain_none":
                got = get_com_member(sk, "CreateSpline3", data, None, None, False, None)
            elif form == "v2_baseline":
                got = get_com_member(sk, "CreateSpline2", data, False)
        except Exception as exc:                                          # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(model)
        P.end_sketch(model)
        rows.append({"form": form, "tag": tag, "returned": str(got)[:70],
                     "error": err, "seg_before": before, "seg_after": after,
                     "built": (after > before) if (before >= 0 and after >= 0) else None})

    case("★ CreateSpline3 + out_dispatch()", form="v3_out_dispatch")
    case("★ CreateSpline3 + 空 Dispatch", form="v3_empty_dispatch")
    case("★ CreateSpline3 + None", form="v3_plain_none")
    case("★ 基线：CreateSpline2（旧的）", form="v2_baseline")

    R = {"★_判据": "★ 建成 ⇒ 草图段数 +1（★ 本仓既有的判据）",
         "★_问题": "★ `sw_part.py` 的 docstring 说「后继末参是 BYREF Object&、pywin32 到不了」⇒ 本探针验它",
         "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print("★ %-34s built=%-5s seg %s→%s err=%s" % (
            r["form"], r["built"], r["seg_before"], r["seg_after"], (r["error"] or "")[:80]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
