"""★ 真机验：段 6 导出（图片导出做正例；展开 DXF 在非钣金件上做表征）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_export_two.py
# 定位:   ★ 2026-10-03（轮 403）24h 计划 v2 **段 6** 的真机探针（见
#   `mcp-server/tool_specs_batch59.py`）。
#   ★★ 判据**复用本模块既有的 `_export_report`** —— 它回读文件（存在且 size > 0）
#   ★ 并记 `size_before` / `grew_or_created`（★ 能区分"这次真导出了"与"旧文件本来就在"）。
# 官方依据: `IModelDocExtension.SaveAs3` · `IModelDoc2.ExportToDWG2(..., swExportToDWG_e)`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 正例 + 负例 + 一条**表征**）：
# ```
# 正例：`export_image_report` 落一张 PNG ⇒ `ok` 且 `exists` 且 `size_bytes > 0`
# 负例：★ **非法输出目录** ⇒ `ok=False` 且带 `error`（★ 判据是文件 ⇒ 写不出去就必须红）
# 表征：`export_flat_pattern_dxf_report` 在**非钣金件**上 ⇒ ★ 只**记录**它成不成，
#   ★ 不当成败判据（★ 它的前置是钣金件，而造钣金件要另一条链 ⇒ 留后批）
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\export-two-evidence.json")


def main() -> int:
    import sw_connect
    from sw_export import export_flat_pattern_dxf_report, export_image_report
    from sw_part import (current_sketch_name, end_sketch, extrude_boss,
                         sketch_corner_rectangle, start_sketch)

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    stamp = time.strftime("%H%M%S")
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -25.0, -15.0, 25.0, 15.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 12.0)
        ev["steps"]["doc"] = {"ok": True,
                              "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        def expect_reject(label, fn, why=""):
            try:
                v = fn()
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {"ok": True, "why": why,
                                      "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
                return
            bad = isinstance(v, dict) and v.get("ok") is False and bool(v.get("error"))
            ev["steps"][label] = {"ok": bool(bad), "why": why,
                                  "value": {k: v.get(k) for k in ("ok", "exists", "size_bytes", "error")}
                                  if isinstance(v, dict) else str(v)[:80]}

        #: 正例：图片导出
        img = Path(r"D:\AI\SW\output") / ("export-image-%s.png" % stamp)
        try:
            r = export_image_report(doc, str(img))
            ev["steps"]["export_image"] = {"ok": bool(r.get("ok")), "values":
                                           {k: r.get(k) for k in
                                            ("format", "exists", "size_bytes", "grew_or_created",
                                             "returned", "error")}}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["export_image"] = {"ok": False,
                                           "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}
        #: 负例：非法输出目录
        expect_reject("neg_export_bad_path",
                      lambda: export_image_report(doc, r"Z:\no-such-dir-xyz\a.png"),
                      why="写不出去就必须红（判据是文件）")
        #: 表征：非钣金件上导展开 DXF（★ 只记录）
        try:
            dxf = Path(r"D:\AI\SW\output") / ("flat-pattern-%s.dxf" % stamp)
            rr = export_flat_pattern_dxf_report(doc, str(dxf))
            ev["steps"]["probe_flat_pattern_on_solid_part"] = {
                "ok": True, "note": "★ 只**记录**（前置是钣金件）",
                "value": {k: rr.get(k) for k in ("ok", "exists", "size_bytes", "error")}}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["probe_flat_pattern_on_solid_part"] = {
                "ok": True, "note": "★ 只**记录**（前置是钣金件）",
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}

        judged = {k: v for k, v in ev["steps"].items() if not k.startswith("probe_")}
        exec_ok = all(v.get("ok") for v in judged.values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 段 6 导出：判据**复用 `_export_report`**（回读文件：存在且 size > 0，"
                      "★ 并记 size_before / grew_or_created）。"
                      "★ 展开 DXF 的正例需要钣金件（前置链另一条）⇒ 本批只在非钣金件上**表征**。")
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
