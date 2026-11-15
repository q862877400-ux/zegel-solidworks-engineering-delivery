"""直调 FeatureExtrusion3：改三个关键参数看能否建成（业主手动已成功）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 真机事实：业主在 `零件46` 手动拉伸**成功**（特征树 `凸台-拉伸1`，
#   体积 3092.02 mm³ = 309.2 mm² × 10，与解析面积 309.292 吻合 0.03%）。
#   ⇒ 几何正确，失败在 API 调用路径。
# 本探针只改 `FeatureExtrusion3` 的三处选择/范围参数，其余与 `sw_part.extrude_boss` 一致：
#   变体 1：UseFeatScope=True,  UseAutoSelect=False  （用我给的选择集）
#   变体 2：UseFeatScope=False, UseAutoSelect=False
#   变体 3：UseFeatScope=True,  UseAutoSelect=True
# 官方签名（IFeatureManager::FeatureExtrusion3，23 参）见
#   `C:\\swapi\\types\\IFeatureManager\\FeatureExtrusion3.md`
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import gear_geometry as g  # noqa: E402
from scripts import sw_connect as c  # noqa: E402
from scripts import sw_part as P  # noqa: E402

_sp = importlib.util.spec_from_file_location(
    "_v3", ROOT / "output" / "_gear_v3_curves.py")
_v3 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(_v3)


def extrude3(doc, depth_m, feat_scope, auto_select):
    """直调 FeatureExtrusion3（参数顺序照 sw_part.extrude_boss）。"""
    return c.get_com_member(
        c.get_com_member(doc, "FeatureManager"), "FeatureExtrusion3",
        True,                # Sd 单向
        False,               # Flip
        False,               # Dir
        0,                   # T1 盲孔
        0,                   # T2
        depth_m,             # D1 深度（米）
        0.0,                 # D2
        False,               # Dchk1
        False,               # Dchk2
        False,               # Ddir1
        False,               # Ddir2
        0.0,                 # Dang1
        0.0,                 # Dang2
        False,               # OffsetReverse1
        False,               # OffsetReverse2
        False,               # TranslateSurface1
        False,               # TranslateSurface2
        True,                # Merge
        feat_scope,          # UseFeatScope
        auto_select,         # UseAutoSelect
        0,                   # T0
        0.0,                 # StartOffset
        False,               # FlipStartOffset
    )


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    spec = g.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    d = _v3.build(spec)
    sw, _ = c.connect_solidworks(wait_seconds=30)

    variants = [
        ("V1 scope=T auto=F", True, False, True),
        ("V2 scope=F auto=F", False, False, True),
        ("V3 scope=T auto=T", True, True, True),
        #: ★★★ V4：**不退出草图**（业主手动拉伸时草图就在编辑中）。
        #:   此前所有尝试都先 `end_sketch` —— 这是与手动操作唯一的实质差异。
        ("V4 草图仍活动 scope=T auto=F", True, False, False),
        ("V5 草图仍活动 scope=F auto=T", False, True, False),
    ]
    for label, fs, auto, do_end in variants:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        for tag, kind, pl in d["segs"]:
            if kind == "spline":
                P.sketch_spline(doc, pl)
            else:
                cx, cy, x1, y1, x2, y2, dr = pl
                P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
        sk = c.get_com_member(doc, "GetActiveSketch2")
        sk_name = str(c.get_com_member(sk, "Name") or "草图1")
        if do_end:
            P.end_sketch(doc)

        fs_ = c.get_com_member(doc, "FeatureByName", sk_name)
        so = None
        for meth in ("GetSpecificFeature2", "GetSketch"):
            try:
                so = c.get_com_member(fs_, meth)
                if so is not None:
                    break
            except Exception:  # noqa: BLE001
                continue
        cts = list(c.get_com_member(so, "GetSketchContours") or [])
        doc.ClearSelection2(True)
        sm = c.get_com_member(doc, "SelectionManager")
        sd = c.get_com_member(sm, "CreateSelectData")
        if sd is not None:
            c.set_com_member(sd, "Mark", 0)
        sel = 0
        for ct in cts:
            try:
                if bool(c.get_com_member(ct, "Select2", True, sd)):
                    sel += 1
            except Exception:  # noqa: BLE001
                pass
        r = extrude3(doc, 0.010, fs, auto)
        vol = 0.0
        try:
            c.get_com_member(doc, "ForceRebuild3", False)
            ext = c.get_com_member(doc, "Extension")
            mp = c.get_com_member(ext, "CreateMassProperty")
            vol = float(c.get_com_member(mp, "Volume")) * 1e9
        except Exception:  # noqa: BLE001
            pass
        title = str(c.get_com_member(doc, "GetTitle") or "?")
        print(f"{label}  选中轮廓 {sel}/{len(cts)}  返回 "
              f"{'Feature' if r is not None else 'None'}  体积 {vol:.3f}  "
              f"文档 {title}")
        if r is not None and vol > 1:
            print("  ⇒ 建成！留在窗口给你看")
            try:
                c.get_com_member(doc, "ViewZoomtofit2")
            except Exception:  # noqa: BLE001
                pass
            return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
