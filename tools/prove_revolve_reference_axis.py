"""★ **参考轴（reference axis）路径的旋转**：照官方示例用 `SelectByID2(Axis1, "AXIS")` + 几何判据。

## 一、为什么要试这一条（★ 轮 360 的遗留）
```
★ 轮 360 发现我们的 `revolve_boss` **选择顺序与官方相反**（官方：先 `AXIS` 后 `SKETCH`）⇒ 已改，
   ★★ 而改序之后**仍不建成**（`feature_created = false`，两次）。
★ 官方示例用的轴是 **`SelectByID2("Axis1", "AXIS", …)`** —— ★ **类型名 `AXIS` = 参考轴**，
   而 objective⑥ 的题述正是「**参考轴 ⇒ mark 16** + `FeatureRevolve2`」那一条。
★ 我们走的是**草图线段**（`GetSketchSegments` + `Select4(mark=4)`）——
   ★★ 两条是**不同的东西** ⇒ 本轮把官方那条**单独试一次**。
```

## 二、★ 判据（★ 沿用轮 360 的几何级硬判据）
```
★ 非对称轮廓 `x∈[10,20] × y∈[0,20]`（★ 完全在轴的一侧）绕**两条不同的参考轴**（x=0 / x=30）各转 360°：
   ★ Pappus：`V = 2π·R̄·A`，`A = 200 mm²`，`R̄ = |15 − axis_x|`
   ⇒ ★ 期望 **18849.6 mm³（x=0）** vs **4712.4 mm³（x=30）** ⇒ ★★ **体积差 4 倍**
   ⇒ ★ **"体积等于哪个"唯一地证明"用的是哪条轴"** ✓
```

## 三、★ 建参考轴的办法（★ 官方 `IModelDoc2.InsertAxis2` 的定义）
```
官方原话：`Inserts a reference axis based on the **currently selected items** with an option to
automatically size the axis.` ⇒ ★★ **要先选中某个项**（一条边 / 一个圆柱面 / 一个基准面）再调它。
★ 本探针用**一条竖直草图线**当那个"选中项"（★ 最可控）。
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（探针）
# 文件:   tools/prove_revolve_reference_axis.py
# 定位:   objective⑥ 的下一半：核**参考轴**这条路径（轮 360 只核到"草图线段"那条不通）。
# 官方依据: `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\
#   Create_360-degree_Revolve_Feature_Example_VBNET.htm`（★ 调用顺序与 `"AXIS"` 类型名）·
# `C:\swapi\types\IModelDoc2\InsertAxis2.md`（★ "based on the currently selected items"
# ）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 新建临时文档并关闭（★ 不保存、不另存 —— 硬约束⑦）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "revolve-reference-axis-evidence.json")


def _callout():
    """★ 空 Dispatch 参数包 —— 事实 33：`SelectByID2` 的 `Callout` 传 `None`
    会得 `类型不匹配`（位置 8），**而那个错误看不出是 Callout 的问题**。"""
    from sw_connect import create_empty_dispatch_variant

    return create_empty_dispatch_variant()


def _vol(sw_connect, model):
    """★ 体积（mm³）—— ★★ **复用本仓库既有的 `sw_mass_property.mass_properties`**，
    ★ **不自己再写一套**（★ `compare_geometry.py` 的注释就写着「三源互证见
    `scripts/sw_mass_property.py`，本模块只读、**不重复换算**」）。

    ★ 该模块回的 `volume` 是**原始单位**（m³）⇒ ★ 本处乘 1e9 得 mm³。
    """
    from sw_mass_property import mass_properties

    try:
        props = mass_properties(model) or {}
    except Exception:                                          # noqa: BLE001
        return None
    v = props.get("volume")
    return float(v) * 1e9 if v else None


def _one_run(sw, sw_connect, axis_x_mm: float) -> dict:
    from sw_connect import get_com_member
    from sw_part import (start_sketch, sketch_corner_rectangle, current_sketch_name,
                         end_sketch, sketch_line)

    doc = sw_connect.new_document(sw, "part")
    out: dict = {"axis_x_mm": axis_x_mm}
    steps: dict = {}
    try:
        #: ① 轮廓（★ 非对称：完全在 x>0 一侧）
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 10.0, 0.0, 20.0, 20.0)
        profile = current_sketch_name(doc)
        end_sketch(doc)
        #: ② 一条竖直线 —— ★ 它将作为"选中项"去建**参考轴**
        start_sketch(doc, plane_name="Front Plane")
        seg = sketch_line(doc, axis_x_mm, -20.0, axis_x_mm, 60.0)
        line_sketch = current_sketch_name(doc)
        end_sketch(doc)
        out.update({"profile_sketch": profile, "line_sketch": line_sketch})

        #: ③ **选中那条线** ⇒ `InsertAxis2(True)` 建**参考轴**
        from sw_part import _select_com_object
        doc.ClearSelection2(True)
        steps["select_line"] = bool(seg is not None and _select_com_object(seg, append=True, mark=0))
        try:
            axis_feat = get_com_member(doc, "InsertAxis2", True)
            steps["insert_axis"] = axis_feat is not None
        except Exception as exc:                               # noqa: BLE001
            axis_feat, steps["insert_axis"] = None, False
            steps["insert_axis_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        #: ④ 找那个参考轴的名字（★ 遍历特征树里 `RefAxis` 类）
        axis_name = "Axis1"
        try:
            feat = get_com_member(doc, "FirstFeature")
            while feat is not None:
                nm = str(get_com_member(feat, "Name") or "")
                tn = str(get_com_member(feat, "GetTypeName2") or "")
                if "Axis" in tn or "轴" in nm:
                    axis_name = nm
                    break
                feat = get_com_member(feat, "GetNextFeature")
        except Exception:                                      # noqa: BLE001
            pass
        out["axis_name"] = axis_name

        #: ⑤ **照官方顺序**：先 `AXIS`、后 `SKETCH`
        doc.ClearSelection2(True)
        ext = get_com_member(doc, "Extension")
        try:
            steps["sel_axis"] = bool(get_com_member(ext, "SelectByID2", axis_name, "AXIS",
                                                    0, 0, 0, False, 0,
                                                    _callout(), 0))
        except Exception as exc:                               # noqa: BLE001
            steps["sel_axis"] = False
            steps["sel_axis_err"] = str(exc)[:100]
        try:
            steps["sel_profile"] = bool(get_com_member(ext, "SelectByID2", profile, "SKETCH",
                                                       0, 0, 0, True, 0,
                                                       _callout(), 0))
        except Exception as exc:                               # noqa: BLE001
            steps["sel_profile"] = False
            steps["sel_profile_err"] = str(exc)[:100]

        #: ⑥ 直接调 `FeatureRevolve2`（★ 绕开我们包装器里"选草图线段"那条路）
        try:
            feat = get_com_member(doc, "FeatureManager")
            fm = get_com_member(feat, "FeatureRevolve2", True, True, False, False, False, False,
                                0, 0, 6.283185307179586, 0, False, False, 0.0, 0.0, 0, 0, 0,
                                True, True, True)
            out["feature_created"] = feat is not None
        except Exception as exc:                               # noqa: BLE001
            out["feature_created"] = False
            out["feature_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        out["volume_mm3"] = _vol(sw_connect, doc)
        out["steps"] = steps
    finally:
        if not _one_run.keep:                                  # type: ignore[attr-defined]
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return out


def _expected(axis_x_mm: float) -> float:
    import math

    return 2.0 * math.pi * abs(15.0 - axis_x_mm) * 200.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()
    _one_run.keep = args.keep                                  # type: ignore[attr-defined]

    import sw_connect

    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    ev: dict = {"steps": {}, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    try:
        for label, ax in (("refaxis_at_x0", 0.0), ("refaxis_at_x30", 30.0)):
            ev["steps"][label] = _one_run(sw, sw_connect, ax)
            e = round(_expected(ax), 1)
            ev["steps"][label]["expected_mm3"] = e
            v = ev["steps"][label].get("volume_mm3")
            ev["steps"][label]["ok"] = bool(v and abs(v - e) / e < 0.05)
        v0 = ev["steps"]["refaxis_at_x0"].get("volume_mm3")
        v1 = ev["steps"]["refaxis_at_x30"].get("volume_mm3")
        if v0 and v1:
            ev["volumes_mm3"] = {"x0": v0, "x30": v1}
            ev["steps"]["volumes_differ"] = {"ok": max(v0, v1) / min(v0, v1) > 1.5,
                                             "ratio": round(max(v0, v1) / min(v0, v1), 3)}
        ev["verdict"] = "pass" if all(
            isinstance(v, dict) and v.get("ok") for v in ev["steps"].values()) else "partial"
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1800])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
