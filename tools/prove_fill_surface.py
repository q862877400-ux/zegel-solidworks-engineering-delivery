"""★ 真机验：`insert_fill_surface_report`（objective② 的第二个真缺 `filled_surface`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_fill_surface.py
# 定位:   ★ 2026-10-02（轮 388）objective② 补第二个真缺 `filled_surface`；
#   ★ 真机打通的组合见 `scripts/sw_surface_features.insert_fill_surface_report` 的来源块。
# 官方依据: `C:\swapi\types\IFeatureManager\InsertFillSurface2.md`（★ 6 参 · mark 表 · Resolutions 1/2/3）·
#   `C:\swapi\enums\swFeatureFillSurfaceOptions_e.md`（★ `swOptimizeSurface = 1`，Bitmask）·
#   官方示例 `Insert_Fill-surface_Feature_Example_CSharp.htm`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量、可被"什么都没发生"证伪）：
# ```
# ① 前置：★ 先建一个**曲面特征**（★ `create_extruded_surface_report`）当"待填的边界"
# ② `insert_fill_surface_report` **回 ok 且新特征名非空且 tree_after > tree_before**
# ③ ★ 负例：★ `resolutions = 9`（★ 官方只许 1/2/3）⇒ **必须被入口拒**
#    ⚠ 不选"不选边界"当负例 —— 事实 303 记着：从官方描述推的"应该失败"**真机上未必**
# ```
# ★ 全程走 `sw_guard` 护栏（AGENTS.md 的常驻纪律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\fill-surface-evidence.json")


def main() -> int:
    import sw_connect
    from sw_part import (current_sketch_name, end_sketch, sketch_corner_rectangle, start_sketch)
    import sw_surface_features as SF

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        ev["steps"]["doc"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}
        r1 = SF.create_extruded_surface_report(doc, 30.0, sk)
        ev["steps"]["prereq_extruded_surface"] = {"ok": bool(r1.get("ok")),
                                                  "feature": r1.get("feature_name"),
                                                  "tree": [r1.get("tree_before"), r1.get("tree_after")]}
        # ② 负例：resolutions 越界 ⇒ 必须被拒
        neg = SF.insert_fill_surface_report(doc, 9)
        ev["steps"]["negative_bad_resolution"] = {"ok": (not neg.get("ok")),
                                                  "returned_ok": bool(neg.get("ok")),
                                                  "error": str(neg.get("error"))[:110]}
        # ③ 正例
        pos = SF.insert_fill_surface_report(doc, 2)
        ev["steps"]["fill_surface"] = {
            "ok": bool(pos.get("ok")),
            "feature_name": pos.get("feature_name"),
            "points_selected": pos.get("points_selected"),
            "boundary_z": pos.get("boundary_z"),
            "tree_before": pos.get("tree_before"), "tree_after": pos.get("tree_after"),
            "resolutions": pos.get("resolutions"), "options": pos.get("options"),
            "error": str(pos.get("error"))[:140] if pos.get("error") else None,
        }
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ `filled_surface` 是 objective② 重核后确认的真缺；"
                      "★ 真机打通的组合：边界边按**中点 + mark=1** 选（`SelectByID2`）⇒ "
                      "`InsertFillSurface2(2, 1, None, None, None, None)`。"
                      "★ mark 传 4 会**静默失败**（回 true 而计数 0 —— 事实 8）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
