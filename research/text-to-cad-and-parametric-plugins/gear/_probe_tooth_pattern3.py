"""真机：单齿 4 条光滑曲线 → 拉伸 → 圆周阵列 ×z（按 GB/T 齿面组成）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 业主 2026-11-07 澄清 + GB/T 齿面组成：
#   一个轮齿 = 左齿面 + 齿顶面 + 右齿面 + 左右齿根过渡曲面（槽底属齿槽，不属一齿）
#   「能用一段光滑的曲线表达的线，就不要去切分成多条」；圆不许画成多边形。
# 为什么单齿而不是整圈：整圈 80 段样条+圆弧拉伸一律回 None，而
#   **最小对照（2 样条 + 2 圆弧）拉伸成功**（output/_probe_petal.py，体积 355.475）
#   ⇒ 瓶颈是**段数/复杂度**，不是样条或圆弧本身。
# 构造（单齿 4 条，全光滑曲线，零直线）：
#   ① 左齿面 = 1 条样条（真实摆线齿根 rf→rb + 真渐开线 rb→ra）
#   ② 齿顶面 = 1 条真圆弧（ra 上）
#   ③ 右齿面 = 1 条样条（镜像）
#   ④ 槽底   = 1 条真圆弧（rf 上，闭合用）
# 阵列：① 前视基准面 + 右视基准面 → `InsertAxis2` 得 Z 轴
#       ② `FeatureCircularPattern4` ×z
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import json
import math
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


def build_tooth(spec):
    """单齿闭合轮廓：左齿面样条 + 齿顶弧 + 右齿面样条 + 槽底闭合弧。

    ★★★ 2026-11-07 修：原写法直接取 `d["segs"][:4]`，但 k0 的第 4 条齿根弧
    通向**下一齿**的位置 ⇒ 单齿轮廓**没闭合**（首点 ≠ 尾点），真机拉伸必失败。
    正确做法：用一条**绕回自身起点**的槽底圆弧闭合（direction = −1，跨度 2P）。
    """
    d = _v3.build(spec)
    #: 每齿 6 条：①左齿根过渡 ②左齿面 ③齿顶面 ④右齿面 ⑤右齿根过渡 ⑥齿根弧
    #: 单齿取前 5 条（GB/T 的一轮齿组成），再用一条绕回起点的槽底弧闭合。
    segs = list(d["segs"][:5])
    # 左齿根过渡起点 与 右齿根过渡终点（都在 rf 上）
    p_start = segs[0][2][0]
    p_end = segs[4][2][-1]
    segs.append(("root_close", "arc",
                 (0.0, 0.0, p_end[0], p_end[1], p_start[0], p_start[1], -1)))
    # 闭合自检
    def _ends(s):
        if s[1] == "spline":
            return s[2][0], s[2][-1]
        _cx, _cy, x1, y1, x2, y2, _dr = s[2]
        return (x1, y1), (x2, y2)
    worst = 0.0
    for i in range(len(segs)):
        ea = _ends(segs[i])[1]
        sb = _ends(segs[(i + 1) % len(segs)])[0]
        worst = max(worst, math.hypot(ea[0] - sb[0], ea[1] - sb[1]) * 1000)
    d = dict(d)
    d["tooth_gap_um"] = worst
    return segs, d


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    m, z, width = 1.0, 20, 10.0
    for a in sys.argv[1:]:
        if a.startswith("--teeth="):
            z = int(a.split("=", 1)[1])
    spec = g.GearSpec(module_mm=m, teeth=z, face_width_mm=width,
                      pressure_angle_deg=20.0, bore_diameter_mm=0.0)
    segs, d = build_tooth(spec)
    print(f"单齿 {len(segs)} 条曲线  rf={d['rf']:.4f} rb={d['rb']:.4f} "
          f"ra={d['ra']:.4f}")

    sw, _ = c.connect_solidworks(wait_seconds=30)
    doc = None
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": []}
    try:
        doc = c.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        for tag, kind, pl in segs:
            if kind == "spline":
                P.sketch_spline(doc, pl)
            else:
                cx, cy, x1, y1, x2, y2, dr = pl
                P.sketch_arc(doc, cx, cy, x1, y1, x2, y2, dr)
        sk = c.get_com_member(doc, "GetActiveSketch2")
        sk_name = str(c.get_com_member(sk, "Name") or "草图1")
        seg_n = len(list(c.get_com_member(sk, "GetSketchSegments") or []))
        ct_n = len(list(c.get_com_member(sk, "GetSketchContours") or []))
        print(f"草图段数 {seg_n} · 轮廓数 {ct_n}")
        P.end_sketch(doc)

        # 选轮廓
        feat_sk = c.get_com_member(doc, "FeatureByName", sk_name)
        sk_obj = None
        for meth in ("GetSpecificFeature2", "GetSketch"):
            try:
                sk_obj = c.get_com_member(feat_sk, meth)
                if sk_obj is not None:
                    break
            except Exception:  # noqa: BLE001
                continue
        cts = list(c.get_com_member(sk_obj, "GetSketchContours") or [])
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
        target = "__current_selection__" if sel else sk_name
        feat = P.extrude_boss(doc, target, width / 1000.0)
        print(f"选中轮廓 {sel}/{len(cts)} · 齿拉伸 = {feat is not None}")
        rep["tooth_extrude"] = feat is not None
        if feat is None:
            raise RuntimeError("单齿拉伸失败")
        tooth_name = "Tooth"
        try:
            feat.Name = tooth_name
        except Exception:  # noqa: BLE001
            tooth_name = str(c.get_com_member(feat, "Name") or "凸台-拉伸1")

        # ── 建 Z 轴：前视 + 右视 两基准面的交线 ──
        ext_ = c.get_com_member(doc, "Extension")
        ok_axis = False
        for pname in ("Front Plane", "Right Plane"):
            try:
                c.get_com_member(ext_, "SelectByID2", pname, "PLANE",
                                 0.0, 0.0, 0.0, pname != "Front Plane", 0,
                                 None, 0)
            except Exception:  # noqa: BLE001
                pass
        try:
            ok_axis = bool(c.get_com_member(doc, "InsertAxis2", True))
        except Exception as exc:  # noqa: BLE001
            rep["axis_error"] = str(exc)[:120]
        print(f"InsertAxis2 = {ok_axis}")
        axis_name = "基准轴1"

        # ── 圆周阵列 ──
        pat = None
        for an in (axis_name, "Axis1", "基准轴2"):
            try:
                pat = P.circular_pattern(doc, tooth_name, an,
                                         2.0 * math.pi, z, True)
                if pat is not None:
                    break
            except Exception as exc:  # noqa: BLE001
                rep.setdefault("pattern_errors", []).append(
                    "%s: %s" % (an, str(exc)[:60]))
        print(f"圆周阵列 = {pat is not None}")
        rep["pattern"] = pat is not None
        c.get_com_member(doc, "ForceRebuild3", False)

        ext2 = c.get_com_member(doc, "Extension")
        mp = c.get_com_member(ext2, "CreateMassProperty")
        vol = float(c.get_com_member(mp, "Volume")) * 1e9
        print(f"体积 = {vol:.3f} mm³")
        from scripts import sw_review as rv
        env = ((rv.collect_geometry_measurements(doc) or {})
               .get("envelope_mm") or {})
        print(f"包围盒 = {env}")
        rep["volume_mm3"] = vol
        rep["bbox"] = env
        expect_bbox = 2 * d["ra"]
        ok = (pat is not None
              and abs(env.get("length", 0) - expect_bbox) < 0.1
              and abs(env.get("height", 0) - width) < 0.1)
        rep["ok"] = ok
        print(f"判据：阵列 ✓ 且 包围盒≈{expect_bbox:.3f} ⇒ {'✓' if ok else '✗'}")
    except Exception as exc:  # noqa: BLE001
        rep["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:250])
        print("✗", rep["error"])
    finally:
        if doc is not None:
            try:
                t = str(c.get_com_member(doc, "GetTitle") or "")
                if t:
                    c.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    (ROOT / "output" / "_probe_gear_tooth_pattern3.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
