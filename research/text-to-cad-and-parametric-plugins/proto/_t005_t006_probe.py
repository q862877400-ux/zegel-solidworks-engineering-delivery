"""T005 + T006 合并探针（省一次 COM 调用）。

T005: ForceRebuild3(False) 是否必须？
      —— 建件后：① 不 rebuild 直接读 bbox/volume；② rebuild 再读。比对。
T006: save_review_previews 出 BMP 还是 PNG？
      —— 调一次，看 output 目录里的扩展名。

同时复核 T004 的结论：volume 单位是 m^3（1e-6 对应 1000 mm^3）。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\Agent-Studio\Deepseek-Harness\DSH-Data\workspace\SW")
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

import sw_connect  # noqa: E402
from sw_mass_property import mass_properties  # noqa: E402
from sw_part import extrude_boss, sketch, sketch_line  # noqa: E402
from sw_feature_readback import solid_body_extent_mm  # noqa: E402
from sw_review import save_review_previews  # noqa: E402

TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot"
OUT = ROOT / "output" / "t005t006"


def build_cube(sw, size_mm: float, depth_mm: float):
    model = sw.NewDocument(TEMPLATE, 0, 0, 0)
    pts = [(0.0, 0.0), (size_mm, 0.0), (size_mm, size_mm), (0.0, size_mm)]
    with sketch(model, "Front Plane") as sk:
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            sketch_line(model, x1, y1, x2, y2)
    feat = extrude_boss(model, sk, sw_connect.mm(depth_mm))
    return model, feat


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sw, _ = sw_connect.connect_solidworks(visible=True)

    # ── T005 ─────────────────────────────────────────────────────
    print("=" * 60)
    print("T005: ForceRebuild3 是否必须")
    print("=" * 60)
    model, feat = build_cube(sw, 20.0, 5.0)
    if feat is None:
        print("VERDICT: 建件失败")
        return 1

    before = solid_body_extent_mm(model)
    before_v = mass_properties(model)["volume"]
    print(f"  rebuild 前: bbox={ {k: before.get(k) for k in ('x_mm','y_mm','z_mm')} }  volume={before_v}")

    model.ForceRebuild3(False)

    after = solid_body_extent_mm(model)
    after_v = mass_properties(model)["volume"]
    print(f"  rebuild 后: bbox={ {k: after.get(k) for k in ('x_mm','y_mm','z_mm')} }  volume={after_v}")

    same = (
        abs((before.get("x_mm") or 0) - (after.get("x_mm") or 0)) < 1e-9
        and abs((before.get("z_mm") or 0) - (after.get("z_mm") or 0)) < 1e-9
        and abs((before_v or 0) - (after_v or 0)) < 1e-15
    )
    print(f"  ⇒ 结论: {'rebuild 不改变读数，非必须（但保留更稳）' if same else 'rebuild 改变了读数 ⇒ 必须调'}")
    print(f"  期望 20x20x5 = 2000 mm^3 = 2.0e-06 m^3")

    # ── T004 复核 ────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("T004 复核：volume 单位")
    print("=" * 60)
    print(f"  20x20x5 读回 volume = {after_v}")
    print(f"  ×1e9 = {(after_v or 0) * 1e9:.3f} mm^3（期望 2000）")
    if after_v and abs(after_v * 1e9 - 2000.0) < 1.0:
        print("  ⇒ 确认：volume 原始单位是 m^3，×1e9 得 mm^3")
    else:
        print("  ⇒ 单位关系与预期不符，需再查")

    # ── T006 ─────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("T006: save_review_previews 输出格式")
    print("=" * 60)
    try:
        paths = save_review_previews(model, OUT, basename="cube20x20x5")
        print(f"  返回 {len(paths)} 个路径:")
        for p in paths:
            pp = Path(str(p))
            print(f"    {pp.name}  exists={pp.exists()}  size={pp.stat().st_size if pp.exists() else 0}")
        exts = {Path(str(p)).suffix.lower() for p in paths}
        print(f"  ⇒ 扩展名: {exts}")
    except Exception as e:  # noqa: BLE001
        print(f"  save_review_previews 失败: {type(e).__name__}: {e}")

    # 落盘结论
    (OUT / "t005_t006_result.txt").write_text(
        f"before_bbox={before}\nbefore_volume={before_v}\n"
        f"after_bbox={after}\nafter_volume={after_v}\n"
        f"rebuild_required={not same}\n"
        f"volume_unit_m3_confirmed={bool(after_v and abs(after_v*1e9-2000.0) < 1.0)}\n",
        encoding="utf-8")
    print()
    print(f"结论已落盘: {OUT / 't005_t006_result.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
