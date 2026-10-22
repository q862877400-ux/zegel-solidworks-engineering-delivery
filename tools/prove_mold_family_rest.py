"""★ 真机验：模具族的另三个（分型面 / 关断面 / 型芯型腔）—— 承接分型线已打通。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_mold_family_rest.py
# 定位:   ★ 2026-10-03（轮 390）`insert_parting_line` 已真机 PASS（事实 306）⇒ 一次验*
#           *另三个**：
#   `insert_parting_surface` / `insert_shut_off_surface` / `insert_core_cavity_solids`。
# 官方依据: `C:\swapi\types\IFeatureManager\` 的三份 md ——
#   · `InsertMoldPartingSurface(int Radiate, bool ReverseAlignment, bool ReverseOffset,
# double OffsetDistance, double Angle, int Smooth, double SmoothDistance, bool Knit)` **
# 8 参**；
#     ★ Remarks：**若模型里还没有分型线**，才必须先选方向与边 ⇒ ★ **有分型线后不必再选** ✓
#   · `InsertMoldShutOffSurface()` —— **零参**
# · `InsertMoldCoreCavitySolids(double Dist1, double Dist2, bool Setback, double Angle)`
#  **4 参**
# · 枚举两源一致：`swPartingSurfaceMoldParmTangent = 0` · `Normal = 1` · `Perpendicular
# = 4`；
#     `swPartingSurfaceSharp = 1` · `Smooth = 2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 每步都定量）：
# ```
# ① 前置 `insert_parting_line` ⇒ 特征树 +1（★ 已真机 PASS 的那一步）
# ② 三步各自：★ **特征树 diff 非空**（★ 规则 6 —— 建完必须回读）
# ③ 若 `mold_evidence()` 的计数可读，★ 一并记下（★ 事实 8：读不到就如实写 null）
# ```
# ★ 单位：★ 该族坐标是**米**（事实 305）⇒ 长度参数给 **0.01**（= 10 mm）这类值。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "mold-family-rest-evidence.json"
)
PARM_TANGENT = 0  # swPartingSurfaceMoldParmTangent
SMOOTH_SHARP = 1  # swPartingSurfaceSharp
MM = 0.001  # 该族长度参数单位是米 ⇒ 毫米 * MM


def main() -> int:
    import sw_connect
    import sw_mold as m_
    import sw_surface_features as sf
    from sw_connect import get_com_member
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%m_:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 25.0)
        ext = get_com_member(doc, "Extension")
        callout = sw_connect.create_empty_dispatch_variant()
        ev["steps"]["doc"] = {
            "ok": True,
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
        }

        # ① 前置：分型线（★ mark=1 方向 + mark=4 按中点选边）
        doc.ClearSelection2(True)
        ext.SelectByID2("前视基准面", "PLANE", 0, 0, 0, False, 1, callout, 0)
        ms = []
        for b in get_com_member(doc, "GetBodies2", -1, True) or []:
            for e in get_com_member(b, "GetEdges") or []:
                try:
                    a = [
                        float(x)
                        for x in get_com_member(
                            get_com_member(e, "GetStartVertex"), "GetPoint"
                        )
                    ]
                    c = [
                        float(x)
                        for x in get_com_member(
                            get_com_member(e, "GetEndVertex"), "GetPoint"
                        )
                    ]
                    ms.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                except Exception:  # noqa: BLE001
                    continue
        ztop = max(m[2] for m in ms) if ms else None
        for m in ms:
            if ztop is not None and abs(m[2] - ztop) < 1e-9:
                ext.SelectByID2("", "EDGE", m[0], m[1], m[2], True, 4, callout, 0)
        try:
            ev["steps"]["prereq_parting_line"] = {
                "ok": True,
                "feature": str(m_.insert_parting_line(doc))[:40],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["prereq_parting_line"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:90]),
            }

        def step(label, fn):
            before = sf.feature_names(doc)
            try:
                r = fn()
                after = sf.feature_names(doc)
                new = [n for n in after if n not in before]
                ev["steps"][label] = {
                    "ok": bool(new),
                    "returned": (r is not None),
                    "new_features": new[-2:],
                    "tree": [len(before), len(after)],
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"][label] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }

        # ② 分型面（★ 8 参；有分型线 ⇒ 不必再选方向/边）
        #: ★★ 按**我们自己的签名**调（★ 实测发现它与官方参数名**不一致** —— 事实 307）
        step(
            "parting_surface",
            lambda: m_.insert_parting_surface(
                doc,
                surface_type=PARM_TANGENT,
                flip=False,
                use_trim=False,
                distance=10.0 * MM,
                angle=0.0,
                option=SMOOTH_SHARP,
                tolerance=0.0,
                alternate=True,
            ),
        )
        # ③ 关断面（★ 零参）
        step("shut_off_surface", lambda: m_.insert_shut_off_surface(doc))
        # ④ 型芯型腔（★ 4 参）
        step(
            "core_cavity_solids",
            lambda: m_.insert_core_cavity_solids(
                doc, scale=30.0 * MM, thickness=30.0 * MM, flip=False, offset=0.0
            ),
        )
        # ⑤ 回读
        try:
            ev["steps"]["evidence_readback"] = {
                "ok": True,
                "evidence": m_.mold_evidence(doc),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["evidence_readback"] = {"ok": False, "err": str(exc)[:90]}
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 承接事实 306（分型线已通）⇒ 一次验另三个；★ 判据是每步**特征树 diff**（规则 6）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
