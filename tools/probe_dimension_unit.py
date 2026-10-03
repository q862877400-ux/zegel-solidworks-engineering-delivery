"""★ 核：「`GetSystemValue3` 的单位随文档单位变」—— ★ 上一轮真机顺带量到的可疑 ①。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 走本仓既有读法）
# 文件:   `scripts/sw_units.py`（`GetUnits()` 读文档单位）·
#         `scripts/sw_document_data.py::_dimension_value_mm`（★ 硬编码 `× 1000`）
# 定位:   ★ 上一轮（轮 55）真机跑 A4 证据时**顺带量到**：★ `before_mm.current` 是 **20000.0**，
#   而那个尺寸的本意是 **20 mm** ⇒ ★★ **可能是 `× 1000` 做错了** ✓
#   ★★★ **本探针的判据（★ 两条独立证据交叉）**：
#     · ★ **A**：★ 同一个尺寸，★ 用 `GetSystemValue3` 读到的**原始值**
#     · ★★ **B**：★ 那份文档的 **`GetUnits()` 单位**
#     ⇒ ★★★ **若 A ≈ 0.02 而单位是米 ⇒ `× 1000` 对**；
#        ★★★ **若 A ≈ 20.0 而单位是毫米 ⇒ `× 1000` 错**（★ 它把毫米又乘了 1000）✓
#   ★★ **对照两份文档**（★ 旧的是上游来源、新的是我建的 —— ★ 单位可能不同）✓
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

OUT = REPO / "output" / "dimension-unit-probe-evidence.json"
OLD_DOC = REPO / "output" / "_probe_drawing_part.SLDPRT"


def _units_of(model):
    """★ 文档单位（★ `IModelDoc2.GetUnits()` ⇒ 5 个 short，★ 第 1 个是 `swLengthUnit_e`）。"""
    try:
        from sw_connect import get_com_member
        raw = get_com_member(model, "GetUnits")
        return list(raw) if raw is not None else None
    except Exception as exc:                                              # noqa: BLE001
        return "error: %s" % str(exc)[:60]


def main() -> int:
    import sw_part as P
    import sw_document_data as D
    from sw_connect import connect_solidworks, new_document, get_com_member

    app, _ = connect_solidworks(visible=True)
    rows = []

    def probe(model, tag):
        names = ["D1@凸台-拉伸1", "D1@Boss-Extrude1"]
        rec = {"tag": tag, "units_GetUnits": _units_of(model), "tries": []}
        for n in names:
            try:
                dim = model.Parameter(n)
            except Exception as exc:                                      # noqa: BLE001
                rec["tries"].append("%s ⇒ Parameter 抛 %s" % (n, type(exc).__name__))
                continue
            if dim is None:
                rec["tries"].append("%s ⇒ Parameter 回 None" % n)
                continue
            raw2 = None
            try:
                raw2 = get_com_member(dim, "GetSystemValue2", "")
            except Exception as exc:                                      # noqa: BLE001
                raw2 = "抛 %s" % type(exc).__name__
            raw3 = None
            try:
                from sw_connect import create_empty_dispatch_variant as _e
                raw3 = get_com_member(dim, "GetSystemValue3", 1, _e())
            except Exception as exc:                                      # noqa: BLE001
                raw3 = "抛 %s" % type(exc).__name__
            rec["tries"].append({
                "name": n,
                "GetSystemValue2_原始": str(raw2)[:60],
                "GetSystemValue3_原始": str(raw3)[:60],
                "★_本仓 _dimension_value_mm 会回": str(D._dimension_value_mm(dim)),
            })
        rows.append(rec)

    #: ① 新建一个 20 mm 拉伸的零件（★ 与上一轮同一工况）
    model = new_document(app, "part")
    P.sketch(model, "Front Plane")
    P.sketch_corner_rectangle(model, -50.0, -30.0, 50.0, 30.0)
    P.end_sketch(model)
    P.extrude_boss(model, "Sketch1", 20.0)
    probe(model, "★ 新建（extrude_boss 20.0 = 20 mm）")

    #: ② 打开那份**旧**文档（★ 上游来源 —— 单位可能是米）
    try:
        old = app.OpenDoc6(str(OLD_DOC), 1, 0, "", 0, 0)
        if old:
            probe(old, "★ 旧文档 _probe_drawing_part.SLDPRT（D1 原本回 0.01）")
    except Exception as exc:                                              # noqa: BLE001
        rows.append({"tag": "★ 旧文档打不开", "error": str(exc)[:120]})

    R = {
        "★_判据": "★ 同一个尺寸：`GetSystemValue3` 的**原始值** vs 文档 **`GetUnits()`** —— "
                  "★ 若原始值≈0.02 且单位是米 ⇒ `×1000` 对；若原始值≈20 且单位是毫米 ⇒ `×1000` 错",
        "★_swLengthUnit_e": {"0": "swMM", "1": "swCM", "2": "swM", "3": "swINCHES",
                             "4": "swFEET", "5": "swFEETINCHES", "6": "swANGSTROM",
                             "7": "swNANOMETER", "8": "swMICRON", "9": "swMIL",
                             "10": "swUINCH"},
        "rows": rows,
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print("★ %s" % r.get("tag"))
        print("     GetUnits:", r.get("units_GetUnits"))
        for t in r.get("tries", []):
            print("     ", t if isinstance(t, str) else json.dumps(t, ensure_ascii=False))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
