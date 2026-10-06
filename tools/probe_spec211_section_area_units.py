"""★ 探针：`GetSectionProperties2` 的**面积单位**（★ 用 `Face.GetArea()` 做基准回读）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-1 的单位判定探针）
# 文件:   tools/probe_spec211_section_area_units.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**。★ 上一轮实测：
#   ★ `GetSectionProperties2` **可用**（★ 当属性取 + 用当前选择集），`retval[0]=0`（status=success）、
#   ★ 形心 `(0.0, 29.9999, -0.0)` ⇒ **长度是 mm** ✓；★ **而 `retval[1]`（面积）= `1.2`**
#   ⇒ ★★ 与几何算出来的面积**差得离谱** ✗ ⇒ **单位必须查明**（★ 记忆里也记着"单位未确证"）✓
# 判据:   ★★ **用已知基准做回读**：★ `IFace2.GetArea()` 的官方 `## Returns` 写着
#   「**Face area in square meters**」⇒ ★ 它就是**权威基准** ✓
#   ⇒ ★ 对**同一个面**同时读两者 ⇒ **比值 = 单位系数** ✓
#   ★ 6 个面全量一遍（★ 一块 100×60×20 的板 ⇒ 面积应为 6000/6000/2000/2000/1200/1200 mm²）
#   ⇒ ★★ 既得单位系数，★ 又**顺便验证面序**（`index:<n>` 到底选了哪个面）✓
#   ★★ 判据：★ **线性性**（比值恒定）**且** 比值是一个"像单位换算"的整数/幂次 ✓
# 官方依据: `C:\swapi\types\IFace2\GetArea.md`（Returns: square meters）+
#   `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（24 元格式，retval[1]=area）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 几何：100 × 60 × 20 mm ⇒ 六个面的**理论面积（mm²）** = 6000×2 · 2000×2 · 1200×2 ✓
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}
DEPTH = 20.0
THEORY_MM2 = sorted([100 * 60, 100 * 60, 100 * DEPTH, 100 * DEPTH,
                     60 * DEPTH, 60 * DEPTH], reverse=True)


def main() -> int:
    import sw_connect
    import tool_caller

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (("solidworks_sketch_start", {}),
                         ("solidworks_sketch_add_rectangle", RECT),
                         ("solidworks_extrude_boss",
                          {"sketch_name": "Sketch1", "depth_mm": DEPTH})):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建状态没成：%s ⇒ %s" % (step, str(note)[:80]))
            return 1

    ext = sw_connect.get_com_member(model, "Extension")
    rows = []
    for idx in range(6):
        ok, note = tool_caller.call("solidworks_select_by_selector", inject_objects=inj,
                                    selector="index:%d" % idx, kind="FACE", body_index=0)
        row = {"face_index": idx, "selected": ok}
        if not ok:
            row["note"] = str(note)[:70]
            rows.append(row)
            continue
        #: ★ 基准：官方说 `IFace2.GetArea()` 回 **square meters** ✓
        try:
            sm = sw_connect.get_com_member(model, "SelectionManager")
            face = sw_connect.get_com_member(sm, "GetSelectedObject6", 1, -1)
            row["get_area_m2"] = float(sw_connect.get_com_member(face, "GetArea"))
        except Exception as exc:                                        # noqa: BLE001
            row["get_area_m2"] = "★ %s" % type(exc).__name__
        #: ★★ 被测：当属性取（★ 上一轮查明它是"无参属性"形态）✓
        try:
            raw = getattr(ext, "GetSectionProperties2")
            vals = tuple(raw) if raw is not None else None
            if vals:
                row["status"] = vals[0]
                row["area_raw"] = vals[1]
                row["centroid"] = list(vals[2:5])
        except Exception as exc:                                        # noqa: BLE001
            row["sect_err"] = type(exc).__name__
        #: ★ 比值（★ 判据：线性 ⇒ 比值恒定）✓
        try:
            a_m2 = float(row["get_area_m2"])
            r_raw = float(row["area_raw"])
            row["ratio_raw_over_m2"] = round(r_raw / a_m2, 6) if a_m2 else None
            row["ratio_raw_over_mm2"] = round(r_raw / (a_m2 * 1e6), 9) if a_m2 else None
        except Exception:                                               # noqa: BLE001
            pass
        rows.append(row)
        print("★ face[%d] GetArea=%.9f m² (%.1f mm²) | retval[1]=%r status=%r 形心=%s"
              % (idx, row.get("get_area_m2") if isinstance(row.get("get_area_m2"), float) else -1,
                 (row.get("get_area_m2") or 0) * 1e6 if isinstance(row.get("get_area_m2"), float) else -1,
                 row.get("area_raw"), row.get("status"), row.get("centroid")))

    out = {"official": {"area_basis": "IFace2.GetArea ⇒ square meters",
                        "sect": "GetSectionProperties2 retval[1] = area"},
           "theory_mm2_sorted": THEORY_MM2, "faces": rows}
    p = ROOT / "output" / "spec211-b1-section-area-units.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
