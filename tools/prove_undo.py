"""★ 真机验：`undo_report`（objective② 的真缺 `undo`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_undo.py
# 定位:   ★ 2026-10-03（轮 395）objective② 补真缺 `undo`：官方 `IModelDoc2.EditUndo2(i
#           nt Steps)`
#   （★ 1 参 · 回 `void`）⇒ 判据只能是**特征树退回了**。
#   ★ 本探针：★ 先建一个特征（树 +1）⇒ 调 `undo_report(model, 1)` ⇒ **树应退回**（★ 定量）。
# 官方依据: `C:\swapi\types\IModelDoc2\EditUndo2.md`（★ `void EditUndo2(int Steps)`；
#   「Undoes the specified number of actions in the active SOLIDWORKS Design session」）·
#   `EditUndo`（★ **Obsolete**）· `SketchUndo()`（★ 零参，撤最后一条草图画线）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量、可被"什么都没发生"证伪）：
# ```
# ① 前置：★ 建一个**拉伸体** ⇒ 特征树 **+1**（★ 用 `create_basic_part` 那条太粗 ⇒ 直接用 sw_part）
# ② `undo_report(model, 1)` ⇒ **`tree_after < tree_before`** 且 `undone = True`
# ③ ★ 负例：★ `steps = 0` ⇒ **必须被入口拒**（★ 官方要求 ≥ 1 个动作）
# ```
# ★ 全程走 `sw_guard` 护栏（AGENTS.md 的常驻纪律）。
# ⚠ **调用纪律**：★ `EditUndo2` 撤的是**会话里的动作**、★ 不区分是不是我们做的 ⇒ ★ 本探针只在
#   **自己刚建完特征之后**调用它 ✓

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "undo-evidence.json")


def main() -> int:
    import sw_connect
    from sw_part import (current_sketch_name, end_sketch, extrude_boss,
                         sketch_corner_rectangle, start_sketch)
    import sw_session as S

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}
        #: ① 前置：★ 建一个拉伸体（★ 树 +1）
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        r = extrude_boss(doc, sk, 10.0)
        from sw_feature_readback import feature_names
        tree_after_build = len(feature_names(doc))
        ev["steps"]["prereq_extrude"] = {"ok": tree_after_build > 0, "tree": tree_after_build,
                                         "returned": str(r)[:60]}
        #: ② 负例：steps = 0 ⇒ 必须被拒
        neg = S.undo_report(doc, 0)
        ev["steps"]["negative_zero_steps"] = {"ok": (not neg.get("ok")),
                                              "returned_ok": bool(neg.get("ok")),
                                              "error": str(neg.get("error"))[:110]}
        #: ③ 正例：steps = 1 ⇒ 树应退回
        pos = S.undo_report(doc, 1)
        ev["steps"]["undo"] = {"ok": bool(pos.get("ok")), "steps": pos.get("steps"),
                               "tree_before": pos.get("tree_before"),
                               "tree_after": pos.get("tree_after"),
                               "undone": pos.get("undone"),
                               "removed_features": pos.get("removed_features"),
                               "error": str(pos.get("error"))[:120] if pos.get("error") else None}
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ `undo` 是 objective② 三层证据判定的**真缺**；★ 官方 `EditUndo2(int Steps)` 回 void ⇒ "
                      "判据是**特征树退回**。★ ⚠ 它撤的是**会话里的动作**、不区分来源 ⇒ "
                      "**只在我们自己的改动之后调用**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1300])
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
