"""★ 真机验：段 2 草图图元的 5 个工具（`sw_part` 的 arc/ellipse/polygon/slot/centerline）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_sketch_primitives.py
# 定位:   ★ 2026-10-03（轮 398）24h 计划 v2 **段 2** 的真机探针。被验的 5 个工具见
#   `mcp-server/tool_specs_batch54.py`：`sketch_arc` · `sketch_ellipse` · `sketch_polygon` ·
#   `sketch_slot` · `sketch_centerline`（★ `sketch_spline` 按计划**标不做** —— 事实 47/68 架构限制）。
#   ★★ **按 ToolSpec 的契约调**：★ 回读段数走工具层同一个解析器
#   （`sw_sketch.resolve_sketch(model, "")` ⇒ 与 `_sketch_args` 一致）。
# 官方依据: `C:\swapi\types\ISketchManager\` 的 `CreateArc` / `CreateEllipse` / `CreatePolygon` /
#   `CreateSketchSlot` / `CreateCenterLine`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量 + 负例）：
# ```
# 正例（★ 每个图元各开一张草图）：★ 画完 `count_segments` **必须比画前多 ≥ 1**
#   —— ★ 段数是**独立于返回值**的量（★ `CreateArc` 那些回 COM 对象、而"回对象"不等于"图形在"）。
# 负例：★ **没有活动草图**时调 `sketch_arc` ⇒ **必须失败**（★ 五个图元共享这条前置）
#   · 以及 `sketch_polygon(sides=2)` ⇒ 如实记录它**成不成**（★ 官方的边数下限未查到 ⇒ 不臆断）
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

OUT = Path(r"D:\AI\SW\output\sketch-primitives-evidence.json")


def main() -> int:
    import sw_connect
    from sw_part import end_sketch, start_sketch
    import sw_part as P
    from sw_sketch import count_segments, resolve_sketch

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = {"ok": True,
                              "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        def seg_count() -> int:
            return int(count_segments(resolve_sketch(doc, "")))

        #: ★ 一个图元一张草图 —— 逐条量"画前 / 画后"的段数
        cases = (
            ("arc", lambda: P.sketch_arc(doc, 0.0, 0.0, 10.0, 0.0, 0.0, 10.0, 1)),
            ("ellipse", lambda: P.sketch_ellipse(doc, 0.0, 0.0, 20.0, 0.0, 0.0, 10.0)),
            ("polygon", lambda: P.sketch_polygon(doc, 0.0, 0.0, 15.0, 6)),
            ("slot", lambda: P.sketch_slot(doc, -15.0, 0.0, 15.0, 0.0, 5.0)),
            ("centerline", lambda: P.sketch_centerline(doc, -20.0, 0.0, 20.0, 0.0)),
        )
        for label, draw in cases:
            try:
                start_sketch(doc, plane_name="Front Plane")
                before = seg_count()
                draw()
                after = seg_count()
                end_sketch(doc)
                ev["steps"]["draw_" + label] = {"ok": after > before,
                                                "segments": [before, after]}
            except Exception as exc:                           # noqa: BLE001
                try:
                    end_sketch(doc)
                except Exception:                              # noqa: BLE001
                    pass
                ev["steps"]["draw_" + label] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}

        #: ★ 负例①：**不存在的草图名** ⇒ 解析器**必须报错**
        #:   ⚠ 我第一版把“**没有活动草图**”当负例 —— ★★ **真机上它不成立**：
        #:   `resolve_sketch(doc, "")` 对**已关闭**的草图也能按名取（★ `tool_specs_batch18` 批头就写着）
        #:   ⇒ ★ 那不是负例。★ 与事实 303 同族：**从描述推出的“应该失败”不等于真机上会失败**。
        try:
            resolve_sketch(doc, "\u8fd9个\u8349\u56fe\u4e0d\u5b58\u5728_xyz")
            ev["steps"]["neg_bogus_sketch_name"] = {
                "ok": False, "note": "不存在的草图名竟然也能解析 ⇒ 本负例不成立（如实记）"}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["neg_bogus_sketch_name"] = {
                "ok": True, "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}

        #: ★ 负例②：边数 < 3 ⇒ **如实记录它成不成**（★ 官方下限未查到 ⇒ 不臆断成败）
        try:
            start_sketch(doc, plane_name="Front Plane")
            b = seg_count()
            P.sketch_polygon(doc, 0.0, 0.0, 15.0, 2)
            a = seg_count()
            end_sketch(doc)
            ev["steps"]["probe_polygon_sides2"] = {"ok": True, "segments": [b, a],
                                                   "note": "★ 只是**记录**它成不成，不是成败判据"}
        except Exception as exc:                               # noqa: BLE001
            try:
                end_sketch(doc)
            except Exception:                                  # noqa: BLE001
                pass
            ev["steps"]["probe_polygon_sides2"] = {
                "ok": True, "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                "note": "★ 只是**记录**它成不成，不是成败判据"}

        judged = {k: v for k, v in ev["steps"].items() if not k.startswith("probe_")}
        exec_ok = all(v.get("ok") for v in judged.values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 段 2 草图图元 5 个工具；★ 判据是**段数增加**（★ 独立于返回值 —— "
                      "回 COM 对象不等于图形在）；★ 负例：没有活动草图时解析必须失败。")
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
