"""★ 真机重试：段 3 收尾两条（`add_dimension` · `linear_pattern`）—— ★ 这次**选区卫生**是对的。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_dimension_pattern_retry.py
# 定位:   ★ 2026-10-03（轮 405）24h 计划 v2 收敛报告 §五 第 ③ 条的落地。
#   ★★ **为什么是"重试"**：轮 400 我把这两条判成「真机未建成」并按硬约束⑥ 回退了注册。
#     而轮 405 的**边对穷举表**显示 `AddDimension2` 其实**能建**（[0,1] 这种相邻边都成）——
#     ★★ 差别只在**选边前有没有 `ClearSelection2`**。
#   ⇒ ★ 即：★ **上一轮的真因是"我的探针选区不干净"，不是能力坏了**
#     （★ 而 AGENTS.md 正好警告过这一条：「每次失败都像是能力坏了，实际是我调错了」）。
#   ⚠ 本探针因此**每次选之前一律先清空选区**。
# 官方依据: `IModelDoc2.AddDimension2`（3 参 · **米** · 必须先选中实体）·
#   `IFeatureManager.FeatureLinearPattern3`（**10 参** · `Spacing1` 是**米** · `Num1` 含原件）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：正例两条都要 `ok`（★ 尺寸要 `dimension_created`；阵列要**特征树真的长了**）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dimension-pattern-retry-evidence.json")


def main() -> int:
    import sw_connect
    from sw_feature_readback import feature_names
    from sw_part import (add_dimension_report, current_sketch_name, end_sketch, extrude_boss,
                         linear_pattern_report, sketch_corner_rectangle, start_sketch)
    from sw_selection_spec import select_entity_by_index

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
        ev["steps"]["setup"] = {"ok": True, "boss": boss,
                                "tree": len(feature_names(doc)),
                                "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        #: ★ 正例 ①：加尺寸（★ **先清空选区** —— 那是上一轮的真因）
        try:
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            select_entity_by_index(doc, "EDGE", 0)
            select_entity_by_index(doc, "EDGE", 1, append=True)
            r = add_dimension_report(doc, 30.0, 20.0, selector="__current_selection__")
            ev["steps"]["add_dimension"] = {
                "ok": bool(r.get("ok")), "selected": r.get("selected"),
                "dimension_created": r.get("dimension_created"), "error": r.get("error")}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["add_dimension"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}

        #: ★ 正例 ②：线性阵列（★ 同样先清空选区）
        try:
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            r2 = linear_pattern_report(doc, boss or "凸台-拉伸2", 10.0, 3)
            ev["steps"]["linear_pattern"] = {
                "ok": bool(r2.get("ok")), "tree": [r2.get("tree_before"), r2.get("tree_after")],
                "new_features": r2.get("new_features"), "error": r2.get("error")}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["linear_pattern"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:120])}

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 上一轮（400）把这两条判成「未建成」并回退注册；★ 轮 405 的**边对穷举表**"
                      "显示 `AddDimension2` 其实能建 ⇒ ★★ **真因是上一轮探针选区不干净**"
                      "（★ 本探针每次选前一律 `ClearSelection2`）。")
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
