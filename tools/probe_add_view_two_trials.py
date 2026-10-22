"""★ 真机：`add_view` 的两个独立试验 —— ★「模型先打开 vs 只给路径」（事实 324：每格独立）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_add_view_two_trials.py
# 定位:   ★ 2026-10-03（轮 413）承**事实 327**。
#   ★ 事实 327 给的两个候选：① 图纸没有图框；② **模型需要先被打开**。
#   ★★ 本轮已把 ① 排掉：★ `setup_current_sheet_as_a3` 回 **`status: pass`**（A3 国标框上好了），
#     ★ 而 `add_view` **仍回 `None`** ⇒ ★ 图框不是卡点。
#   ⇒ ★ 本探针测 ②，★ 而且**做成两个独立试验**（★ **事实 324**：穷举表的每一格必须独立）：
#     · 格 A：★ 只给路径（★ 不预先打开模型）—— ★ 复现上一版；
#     · 格 B：★ **先用 `open_document` 打开该零件**，再 `add_view`。
#     ★ 两格**各自新建一张工程图**（★ 这样一格不会污染另一格）。
# 官方依据: `IDrawingDoc.CreateDrawViewFromModelView3(ModelName, ViewName, LocX, LocY, Z
#           )`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ `add_view` **回一个非空视图对象**（★ 那是后续 `GetDatumTagCount` 回读的前提）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "subskills" / "solidworks-engineering-drawing" / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "add-view-two-trials-evidence.json")
PART = Path(r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples"
            r"\tutorial\api\squarepad_blue.sldprt")
A3_GB = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\Chinese-Simplified"
             r"\sheetformat\a3 - gb.slddrt")


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    import drawing_workflow as DW

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    docs = []
    try:
        for label, pre_open in (("A_path_only", False), ("B_model_preopened", True)):
            cell: dict = {"trial": label, "pre_open": pre_open}
            doc = None
            try:
                if pre_open:
                    #: ★ 格 B：★ 先把零件打开（★ 只读方式，★ 不修改它）
                    m = sw_connect.open_document(sw, str(PART), read_only=True)
                    docs.append(m)
                    cell["model_opened"] = m is not None
                doc = sw_connect.new_document(sw, "drawing")
                docs.append(doc)
                try:
                    DW.setup_current_sheet_as_a3(doc, [str(A3_GB)])
                    cell["a3"] = True
                except Exception as exc:                       # noqa: BLE001
                    cell["a3"] = False
                    cell["a3_err"] = str(exc)[:80]
                view = DW.add_view(doc, str(PART), "*Front", 0.15, 0.15)
                cell["view"] = view is not None
                if view is not None:
                    cell["datum_count"] = safe_get_com_member(view, "GetDatumTagCount")
                cell["ok"] = view is not None
            except Exception as exc:                           # noqa: BLE001
                cell["ok"] = False
                cell["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
            ev["trials"].append(cell)
        wins = [c["trial"] for c in ev["trials"] if c.get("ok")]
        ev["verdict"] = "pass" if wins else "partial"
        ev["successes"] = wins
        ev["note"] = ("★ 两个**独立**试验（★ 事实 324）：★ 格 A 只给路径、★ 格 B 先打开模型。"
                      "★ 判据是 `add_view` **回一个非空视图对象**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        for d in reversed(docs):
            try:
                t = str(safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
