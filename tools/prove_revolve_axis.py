"""★ **旋转轴的几何级判据**：用「非对称轮廓绕不同轴 ⇒ 体积不同」证明**轴真的生效**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（探针）
# 文件:   tools/prove_revolve_axis.py
# 定位:   objective⑥ 的**硬判据**：从"建成"升级到"轴真的生效"。
#   ★ 触发它的是 `output/revolve-axis-evidence.json` 里看出来的问题：
#     四条用例里 `SKETCHSEGMENT_m4` 的 `sel_axis = 0`、`EXTSKETCHSEGMENT_noSk` 的
#     `sel_sketch = 0`，**而两条都 `ok=True`（新出现了「旋转1」）** ⇒
#     ★★ **"建成"证明不了轴选对了**（SolidWorks 会自己推断轴）—— 与事实 62 同族。
# 官方依据: 不适用（★ 用本项目 `scripts/sw_part.py` 的 `revolve_boss` + 质量属性回读）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 会**新建临时文档并关闭**（★ 不保存、不另存 —— 硬约束⑦）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "revolve-axis-geometric-evidence.json"
)


def _volume_mm3(model) -> float | None:
    """★ 回读体积（mm³）—— 规则 6：改完特征要回读。"""
    from sw_connect import get_com_member

    try:
        ext = get_com_member(model, "Extension")
    except Exception:  # noqa: BLE001
        return None
    if ext is None:
        return None
    try:
        mp = get_com_member(ext, "CreateMassProperty")
    except Exception:  # noqa: BLE001
        return None
    if mp is None:
        return None
    try:
        v = get_com_member(mp, "Volume")
    except Exception:  # noqa: BLE001
        return None
    return float(v) * 1e9 if v else None


def _one_run(sw, sw_connect, axis_x_mm: float) -> dict:
    """★ **一次独立运行**：新文档 → 非对称矩形轮廓 → 一条竖直线当轴 → 旋转 360° → 回读体积。"""
    from sw_part import (
        start_sketch,
        sketch_corner_rectangle,
        current_sketch_name,
        end_sketch,
        sketch_line,
        revolve_boss,
    )

    doc = sw_connect.new_document(sw, "part")
    out: dict = {"axis_x_mm": axis_x_mm}
    try:
        #: ① 轮廓：x 从 10 到 20、y 从 0 到 20 ⇒ ★ **完全在轴的一侧**（★ 非对称）
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 10.0, 0.0, 20.0, 20.0)
        profile = current_sketch_name(doc)
        end_sketch(doc)
        #: ② 轴：一条竖直线（★ x = axis_x_mm）
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, axis_x_mm, -20.0, axis_x_mm, 60.0)
        axis = current_sketch_name(doc)
        end_sketch(doc)
        out.update({"profile_sketch": profile, "axis_sketch": axis})
        #: ③ 旋转 360°
        feat = revolve_boss(doc, profile, 6.283185307179586, axis)
        out["feature_created"] = feat is not None
        #: ④ 回读体积（★ 那才是"轴生效"的证据）
        out["volume_mm3"] = _volume_mm3(doc)
        #: ⑤ 再回读特征类型名（★ 只是辅助，★ 不作主判据）
        try:
            from sw_connect import get_com_member

            tree = get_com_member(doc, "FirstFeature")
            names = []
            while tree is not None and len(names) < 12:
                names.append(str(get_com_member(tree, "Name") or ""))
                tree = get_com_member(tree, "GetNextFeature")
            out["feature_names"] = names
        except Exception:  # noqa: BLE001
            out["feature_names"] = []
    finally:
        if not _one_run.keep:  # type: ignore[attr-defined]
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return out


def _expected_volume(axis_x_mm: float) -> float:
    """★ 解析期望值：矩形绕竖直线转 360° ⇒ 圆环（Pappus）：
    `V = 2π·R̄·A`，`A = 10×20 = 200 mm²`，`R̄ = 质心到轴的距离`（质心 x = 15）。"""
    import math

    area = 10.0 * 20.0
    r_bar = abs(15.0 - axis_x_mm)
    return 2.0 * math.pi * r_bar * area


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    _one_run.keep = args.keep  # type: ignore[attr-defined]

    import sw_connect

    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    ev: dict = {"steps": {}, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        for label, axis_x in (("axis_at_x0", 0.0), ("axis_at_x30", 30.0)):
            ev["steps"][label] = _one_run(sw, sw_connect, axis_x)
            ev["steps"][label]["expected_mm3"] = round(_expected_volume(axis_x), 1)
            exp = ev["steps"][label]["expected_mm3"]
            got = ev["steps"][label].get("volume_mm3")
            ev["steps"][label]["ok"] = bool(got and abs(got - exp) / exp < 0.05)

        v0 = ev["steps"]["axis_at_x0"].get("volume_mm3")
        v1 = ev["steps"]["axis_at_x30"].get("volume_mm3")
        if v0 and v1:
            ratio = max(v0, v1) / min(v0, v1)
            ev["volumes_mm3"] = {"axis_at_x0": v0, "axis_at_x30": v1}
            ev["steps"]["volumes_differ"] = {
                "ok": ratio > 1.5,
                "ratio": round(ratio, 3),
                "note": "★ 绕不同轴 ⇒ 体积必须显著不同；★ 若基本相同 ⇒ 轴没生效（被自动推断覆盖）",
            }
        ev["verdict"] = (
            "pass"
            if all(isinstance(v, dict) and v.get("ok") for v in ev["steps"].values())
            else "partial"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print("  产物: %s  ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
