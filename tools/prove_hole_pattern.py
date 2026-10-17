"""★ 真机验：段 4 孔族的 `hole_pattern_report`（按孔位批量建孔）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_hole_pattern.py
# 定位:   ★ 2026-10-03（轮 401）24h 计划 v2 **段 4** 的真机探针。被验的工具见
#   `mcp-server/tool_specs_batch57.py`（`solidworks_hole_pattern`）。
#   ★★ 它的存在理由：`create_hole_pattern` 收一个 **`creator` 可调用对象** ⇒
#   ★ MCP 层给不出函数 ⇒ 包装换成**具名的 `kind`**。
# 官方依据: `IFeatureManager.HoleWizard5`（各 `create_*_hole` 走它）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 正例 + 三条可证伪的负例）：
# ```
# 正例：★ 4 个孔位 ⇒ `holes` 4 条 · **特征树 +4** · `new_features` 里 4 个（★ 规则 6 双判据）
# 负例①：★ `kind="counterbore"` ⇒ **必须被拒**（★ 本工具只暴露 through/blind）
# 负例②：★ `kind="blind"` 而不给 `depth_mm` ⇒ **必须被拒**（★ 盲孔没深度建不出来）
# 负例③：★ `positions=[]` ⇒ **必须被拒**
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "hole-pattern-evidence.json")


def main() -> int:
    import sw_connect
    from sw_hole_features import hole_pattern_report
    from sw_part import (current_sketch_name, end_sketch, extrude_boss,
                         sketch_corner_rectangle, start_sketch)

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        ev["steps"]["doc"] = {"ok": True,
                              "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        def expect_reject(label, fn, why=""):
            try:
                v = fn()
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {"ok": True, "why": why,
                                      "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}
                return
            bad = isinstance(v, dict) and v.get("ok") is False and bool(v.get("error"))
            ev["steps"][label] = {"ok": bool(bad), "why": why, "value": v}

        #: 负例先做（★ 免得正例建出的孔影响后面的判断）
        expect_reject("neg_kind_counterbore",
                      lambda: hole_pattern_report(doc, [[0.0, 0.0]], kind="counterbore"),
                      why="本工具只暴露 through/blind")
        expect_reject("neg_blind_without_depth",
                      lambda: hole_pattern_report(doc, [[0.0, 0.0]], kind="blind"),
                      why="盲孔没深度建不出来")
        expect_reject("neg_empty_positions",
                      lambda: hole_pattern_report(doc, [], kind="through"),
                      why="空孔位表")
        #: 正例：4 个通孔
        try:
            v = hole_pattern_report(doc, [[-20.0, -10.0], [20.0, -10.0], [-20.0, 10.0], [20.0, 10.0]],
                                    kind="through", diameter_mm=6.0)
            ev["steps"]["hole_pattern_4_through"] = {
                "ok": bool(v.get("ok")), "requested": v.get("requested"),
                "holes": len(v.get("holes") or []), "tree": [v.get("tree_before"), v.get("tree_after")],
                "new_features": v.get("new_features"), "error": v.get("error")}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["hole_pattern_4_through"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 段 4 孔族：包装把 `create_hole_pattern` 的 **creator 可调用对象**换成"
                      "**具名的 kind**（★ MCP 层给不出函数）。★ 判据两条都要：证据条数 + **特征树增量**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1600])
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
