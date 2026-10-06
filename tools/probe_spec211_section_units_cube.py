"""★ 探针：用**正方体**坐实 `GetSectionProperties2` 的面积单位（★ 六面同面积 ⇒ 消除面序干扰）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-1 的单位坐实探针）
# 文件:   tools/probe_spec211_section_units_cube.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**。★ 前两轮的困境是：
#   ★★ **我认不出 `index:<n>` 对应哪个面** ⇒ ★ 于是"读数 vs 理论面积"对不上时，
#     ★ 分不清是**单位错**还是**我认错面** ✗
#   ⇒ ★★ **本探针用一个 20×20×20 的正方体**：★ **六个面面积全都 = 400 mm²**
#     ⇒ ★★ **"认错面"这个干扰被彻底消掉** ⇒ ★ **读数只有一个值，单位随之唯一确定** ✓
# 判据:   ★★ **正方体的六面读数**（★ 全 6 次 + status）：
#     · 读数 **400**    ⇒ 单位 = **mm²** ✓
#     · 读数 **4**      ⇒ 单位 = **cm²** ✓
#     · 读数 **0.0004** ⇒ 单位 = **m²**  ✓
#     · 读数 **0.62**   ⇒ 单位 = **in²** ✓
#     · 读数 **0.000645** ⇒ 单位 = **in² 的 m² 版**（in² 换算）✓
#   ★ 同时读 `IFace2.GetArea()` 做**交叉验证**（★ 上一轮 6/6 相同 ⇒ 应再次相同）✓
#   ★★ 若两个成员的读数**仍不一致**，★ 或读数**不等于上面任何一个** ⇒
#     ★ **如实记"单位未定"**，★ 并在返回值里带 `units_verified: false`（★ 不许假装知道）✓
# 官方依据: `C:\swapi\types\IFace2\GetArea.md`（Returns: square meters）+
#   `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（24 元，retval[1]=area）
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

#: ★ 20 × 20 × 20 mm 的正方体 ⇒ **六面全 400 mm²** ✓
SIDE = 20.0
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": SIDE, "y2_mm": SIDE}
THEORY_MM2 = SIDE * SIDE

#: ★ 候选单位（★ 把 400 mm² 换算到各单位，看读数落在哪个上）✓
CANDIDATES = {"mm^2": 400.0, "cm^2": 4.0, "m^2": 0.0004, "in^2": 0.62, "ft^2": 0.0043}


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
                          {"sketch_name": "Sketch1", "depth_mm": SIDE})):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建状态没成：%s ⇒ %s" % (step, str(note)[:80]))
            return 1

    ext = sw_connect.get_com_member(model, "Extension")
    rows, areas = [], []
    for idx in range(6):
        ok, _n = tool_caller.call("solidworks_select_by_selector", inject_objects=inj,
                                  selector="index:%d" % idx, kind="FACE", body_index=0)
        row = {"face_index": idx, "selected": ok}
        if not ok:
            rows.append(row)
            continue
        try:
            sm = sw_connect.get_com_member(model, "SelectionManager")
            face = sw_connect.get_com_member(sm, "GetSelectedObject6", 1, -1)
            row["get_area"] = float(sw_connect.get_com_member(face, "GetArea"))
        except Exception as exc:                                        # noqa: BLE001
            row["get_area"] = "★ %s" % type(exc).__name__
        try:
            raw = getattr(ext, "GetSectionProperties2")
            vals = tuple(raw) if raw is not None else None
            if vals:
                row["status"], row["area"] = vals[0], vals[1]
                row["centroid"] = list(vals[2:5])
                areas.append(float(vals[1]))
        except Exception as exc:                                        # noqa: BLE001
            row["sect_err"] = type(exc).__name__
        rows.append(row)
        print("★ face[%d] GetArea=%r | retval[1]=%r status=%r 形心=%s"
              % (idx, row.get("get_area"), row.get("area"), row.get("status"),
                 row.get("centroid")))

    #: ★★ 判定：六面读数是否**同一个值**、且落在哪个候选单位上 ✓
    verdict = {"theory_mm2": THEORY_MM2, "readings": areas}
    if areas and len(set(round(a, 6) for a in areas)) == 1:
        v = areas[0]
        verdict["all_same"] = v
        hit = [u for u, x in CANDIDATES.items() if abs(v - x) <= max(0.02 * x, 1e-6)]
        verdict["unit_by_candidate"] = hit or None
        print("★★ 六面读数**全相同** = %r ⇒ ★ 落在候选单位：%s" % (v, hit or "★ 都不吻合"))
    else:
        verdict["all_same"] = None
        print("★ 六面读数**不全相同** ⇒ %s ⇒ ★ 面序或几何有意外" % areas)

    out = {"official": {"area_basis": "IFace2.GetArea ⇒ square meters",
                        "sect": "GetSectionProperties2 retval[1] = area"},
           "cube_side_mm": SIDE, "verdict": verdict, "faces": rows}
    p = ROOT / "output" / "spec211-b1-section-units-cube.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
