"""定位：几何已验证可拉伸（业主手动拉伸出 3092.02 mm³），为何 API 调用失败。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07：「我拉伸成功了啊，哪里不能拉伸了」——
#   真机事实：`零件46` 特征树含 `凸台-拉伸1`，体积 **3092.0205 mm³**
#   = 309.2 mm² × 10，与解析面积 309.292 吻合 0.03% ⇒ **齿形几何正确**。
# 本探针只查一件事：**API 那条路差在哪**。逐步骤打印状态：
#   ① 画完草图、`end_sketch` 之后 → `GetActiveSketch2()` 是否为 None
#   ② 选择集里到底放了什么（草图特征 / 草图对象 / 轮廓）
#   ③ 直接调 `FeatureExtrusion3`（不经 `extrude_boss` 的封装）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
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


def sel_count(doc):
    try:
        return int(c.get_com_member(
            c.get_com_member(doc, "SelectionManager"),
            "GetSelectedObjectCount2", -1))
    except Exception:  # noqa: BLE001
        return -1


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    spec = g.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    d = _v3.build(spec)
    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = c.new_document(sw, "part")
    print("文档 =", c.get_com_member(doc, "GetTitle"))

    P.start_sketch(doc, plane_name="Front Plane")
    for tag, kind, pl in d["segs"]:
        if kind == "spline":
            P.sketch_spline(doc, pl)
        else:
            cx, cy, x1, y1, x2, y2, dr = pl
            P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
    sk = c.get_com_member(doc, "GetActiveSketch2")
    sk_name = str(c.get_com_member(sk, "Name") or "草图1")
    print(f"画完：草图={sk_name} 段数="
          f"{len(list(c.get_com_member(sk, 'GetSketchSegments') or []))} "
          f"轮廓数={len(list(c.get_com_member(sk, 'GetSketchContours') or []))}")
    print(f"     活动草图存在={bool(sk)}  选择集={sel_count(doc)}")

    # ── 退出草图，并**确认真的退出了** ──
    P.end_sketch(doc)
    still = c.get_com_member(doc, "GetActiveSketch2")
    print(f"end_sketch 后：活动草图存在={bool(still)}  选择集={sel_count(doc)}")

    # ── 路线 A：只选草图特征（名字），直接 extrude_boss ──
    doc.ClearSelection2(True)
    ok_feat = P._select_sketch_feature_by_name(doc, sk_name)
    print(f"A 选中草图特征={ok_feat}  选择集={sel_count(doc)}")
    fa = P.extrude_boss(doc, sk_name, 0.010)
    print(f"A extrude_boss(名字) ⇒ {fa is not None}")
    if fa is not None:
        try:
            fa.Name = "Gear_A"
        except Exception:  # noqa: BLE001
            pass
        ext = c.get_com_member(doc, "Extension")
        mp = c.get_com_member(ext, "CreateMassProperty")
        print(f"   体积 = {float(c.get_com_member(mp,'Volume'))*1e9:.3f} mm³")
        return 0

    # ── 路线 B：选草图**对象**（非轮廓），用 __current_selection__ ──
    doc.ClearSelection2(True)
    feat_sk = c.get_com_member(doc, "FeatureByName", sk_name)
    sk_obj = None
    for meth in ("GetSpecificFeature2", "GetSketch"):
        try:
            sk_obj = c.get_com_member(feat_sk, meth)
            if sk_obj is not None:
                break
        except Exception:  # noqa: BLE001
            continue
    okb = bool(P._select_com_object(sk_obj, append=False, mark=0, model=doc))
    print(f"B 选中草图对象={okb}  选择集={sel_count(doc)}")
    fb = P.extrude_boss(doc, "__current_selection__", 0.010)
    print(f"B extrude_boss(当前选择=草图对象) ⇒ {fb is not None}")
    if fb is not None:
        ext = c.get_com_member(doc, "Extension")
        mp = c.get_com_member(ext, "CreateMassProperty")
        print(f"   体积 = {float(c.get_com_member(mp,'Volume'))*1e9:.3f} mm³")
        return 0

    # ── 路线 C：选轮廓（此前用过的那条） ──
    doc.ClearSelection2(True)
    cts = list(c.get_com_member(sk_obj, "GetSketchContours") or [])
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
    print(f"C 选中轮廓={sel}/{len(cts)}  选择集={sel_count(doc)}")
    fc = P.extrude_boss(doc, "__current_selection__", 0.010)
    print(f"C extrude_boss(当前选择=轮廓) ⇒ {fc is not None}")
    if fc is not None:
        ext = c.get_com_member(doc, "Extension")
        mp = c.get_com_member(ext, "CreateMassProperty")
        print(f"   体积 = {float(c.get_com_member(mp,'Volume'))*1e9:.3f} mm³")
        return 0

    print("三条路线都没成 —— 需要看 FeatureExtrusion3 的返回值与错误码")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
