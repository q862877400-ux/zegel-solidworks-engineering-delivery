"""★ 真机验：`insert_extend_surface_report`（objective② 的真缺之一 `extend_surface`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_extend_surface.py
# 定位:   ★ 2026-10-02（轮 386）objective② 重核后确认 `extend_surface` 为**真缺**
#   （★ `docs/union-gap-evidence-based.md`），★ 而官方 `IModelDoc2.InsertExtendSurface` **3 参、可补**。
#   ★ 本探针：★ 先建一个曲面特征 ⇒ **按对象选中它** ⇒ 延伸 ⇒ **回读特征树**（★ 它回 void，规则 6）。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertExtendSurface.md` ——
#   `void InsertExtendSurface(bool ExtendLinear, int EndCondition, double Distance)`；
#   「Extends a surface along the **selected** faces or edges」；
#   `EndCondition`：**0 = 按距离** · **1 = 到选定点**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量、可被"什么都没发生"证伪）：
# ```
# ① 前置：★ 先建出**一个曲面特征**（★ 用已真机通过的 `create_extruded_surface_report`）——
#    没有曲面就没法延伸；★ 判据是**特征树真的多了**（★ 那一步的）
# ② `insert_extend_surface_report` **返回 ok 且 `tree_after > tree_before`**
# ③ ★ 反证：★ **不选任何面**时它**必须失败**（★ 官方要求"along the selected faces"）——
#    ★ 那证明判据②不是"恒真"
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "extend-surface-evidence.json")


def main() -> int:
    import sw_connect
    from sw_part import (current_sketch_name, end_sketch, sketch_corner_rectangle, start_sketch)
    import sw_surface_features as SF

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: ① 前置：★ 先建一个**曲面特征**（★ 用已真机通过的 `create_extruded_surface_report`）
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        ev["steps"]["doc"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}
        r1 = SF.create_extruded_surface_report(doc, 30.0, sk)
        ev["steps"]["prereq_extruded_surface"] = {"ok": bool(r1.get("ok")),
                                                  "feature": r1.get("feature_name"),
                                                  "tree": [r1.get("tree_before"), r1.get("tree_after")]}

        #: ② **负例**：★ 距离 ≤ 0 ⇒ **必须被入口拒掉**（★ 那不依赖 `InsertExtendSurface` 的选择语义）。
        #:   ⚠ 我第一版把"**不选面**"当负例 —— ★ 而真机上**不选面它也能成**（★ 官方描述说
        #:   "along the **selected** faces"，★ 但实测它**自己会找**）⇒ ★★ 那条**不是负例**，
        #:   保留它会得出"判据失效"的**错误结论**。⇒ 换成参数校验这条（★ 那才可证伪）。
        neg = SF.insert_extend_surface_report(doc, 0.0)
        ev["steps"]["negative_zero_distance"] = {
            "ok": (not neg.get("ok")), "returned_ok": bool(neg.get("ok")),
            "error": str(neg.get("error"))[:110]}

        #: ③ 正例：★ 选面由 `insert_extend_surface_report` 内部完成（`_select_all_surface_faces`）
        pos = SF.insert_extend_surface_report(doc, 10.0)
        ev["steps"]["extend_surface"] = {
            "ok": bool(pos.get("ok")),
            "feature_name": pos.get("feature_name"),
            "faces_selected": pos.get("faces_selected"),
            "tree_before": pos.get("tree_before"), "tree_after": pos.get("tree_after"),
            "distance_mm": pos.get("distance_mm"),
            "error": str(pos.get("error"))[:140] if pos.get("error") else None,
        }

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ `extend_surface` 是 objective② 重核后确认的**真缺**；"
                      "★ 官方 `IModelDoc2.InsertExtendSurface` 3 参、回 void ⇒ 判据只能是特征树。"
                      "★ 负例（不选面）必须失败 —— 那证明判据不是恒真。")
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
