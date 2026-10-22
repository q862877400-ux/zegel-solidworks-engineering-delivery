"""★ 真机：线性阵列按**官方 Remarks 的 mark 表**给方向 —— mark=1 是方向、mark=4 是要阵列的特征。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_pattern_direction_marks.py
# 定位:   ★ 2026-10-03（轮 406）24h 计划 v2 收敛报告 §五 第 ③ 条的**后半**（`linear_pa
#           ttern`）。
#   ★★ **假设从官方 Remarks 读出**（★ 不是猜）：`IFeatureManager.FeatureLinearPattern3` 的
#     Remarks 给了 mark 表 ——
#     ```
#     - **1 and 2 to mark the directions**
#     - 4 to mark the features to pattern
#     ```
#     ⇒ ★★ 即：**方向是靠"选区里的 mark"给的**，★ 而轮 400/405 我**只传了 `DName1=""`、
#       根本没选方向实体** ⇒ ★ 那很可能就是"不报错而特征树不变"的真因。
#   ★ 与 `AddDimension2` 的「**必须先选中实体**」**同族前置**（★ 那一条本轮刚学到）。
# 官方依据: `IFeatureManager.FeatureLinearPattern3` 的 Remarks（mark 表，见上）·
#   `IModelDocExtension.SelectByID2`（**9 参**，第 7 个是 `Mark`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **特征树真的长了**（★ 规则 6）—— ★ 不看返回值。

from __future__ import annotations

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
    / "pattern-direction-marks-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_feature_readback import feature_names
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        linear_pattern_report,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 15.0, -2.0, 19.0, 2.0)
        sk2 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk2, 20.0)
        boss = None
        for nm in ("凸台-拉伸2", "Boss-Extrude2"):
            if sw_connect.safe_get_com_member(doc, "FeatureByName", nm) is not None:
                boss = nm
                break
        ev["steps"]["setup"] = {
            "ok": True,
            "boss": boss,
            "tree": len(feature_names(doc)),
        }

        ext = get_com_member(doc, "Extension")
        empty = sw_connect.create_empty_dispatch_variant()

        def sel(name, kind, x, y, z, mark):
            """★ `SelectByID2(Name, Type, X, Y, Z, Append, Mark, Callout, Option)` —— **9 参**。"""
            return get_com_member(
                ext,
                "SelectByID2",
                str(name),
                str(kind),
                float(x),
                float(y),
                float(z),
                False,
                int(mark),
                empty,
                0,
            )

        #: ★ 方向 1：选一条边（mark=1）—— ★ 边长方向就是阵列方向。
        #: ★ 坐标单位是**米**（`SelectByID2` 的 X/Y/Z）。
        try:
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            ok_dir = sel("", "EDGE", 0.0, -0.015, 0.0, 1)
            len(
                sw_connect.safe_get_com_member(
                    get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                or []
            )
            ev["steps"]["select_direction_edge"] = {
                "ok": bool(ok_dir),
                "returned": bool(ok_dir),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["select_direction_edge"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
            }
        #: ★ 要阵列的特征：mark=4
        try:
            ok_feat = sel(boss or "凸台-拉伸2", "BODYFEATURE", 0.0, 0.0, 0.0, 4)
            ev["steps"]["select_feature_mark4"] = {"ok": bool(ok_feat)}
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["select_feature_mark4"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
            }
        #: ★ 阵列（★ 判据是特征树）
        try:
            r = linear_pattern_report(doc, boss or "凸台-拉伸2", 10.0, 3)
            ev["steps"]["linear_pattern_with_marks"] = {
                "ok": bool(r.get("ok")),
                "tree": [r.get("tree_before"), r.get("tree_after")],
                "new_features": r.get("new_features"),
                "error": r.get("error"),
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["linear_pattern_with_marks"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
            }

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 验证官方 Remarks 的 mark 表（**1/2 标方向 · 4 标要阵列的特征**）—— "
            "★ 与轮 400/405 的差别是**这次先按 mark 选了方向实体**。"
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
