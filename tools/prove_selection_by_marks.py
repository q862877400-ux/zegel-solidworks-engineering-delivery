"""★ 真机：验「**分桶取数**」这条修法 —— 两次选择用不同 mark，逐个桶各取一个对象。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_selection_by_marks.py
# 定位:   ★ 2026-10-03（轮 423）承**事实 336** 的具体下一步。
#   ★★ 事实 336 的定性：★ `GetSelectedObjectCount2(0)` **如实报 2**，
#     ★ 而「按位置取对象」那一族（`GetSelectedObject4/5/6`）**只回得到第 1 个**
#     ⇒ ★ `sw_simulation._selected_dispatch_array` **只拿到 1 个**
#     ⇒ ★★ **传不完整的数组**给"两组实体"的载荷 ⇒ SW 内部越界 ⇒ **RPC 不可用**
#       （★ 那正是 B 组四次"崩"的真因）。
#   ★★ 而**对照实验**给出了修法候选：★ **两次选择用不同 mark** 时，
#     `Count2` = `{-1: 2, 0: 0, 1: 1, 2: 1}` ⇒ ★ **分桶确实成立** ✓
#   ★★★ 而本探针**照本轮纪律"先验再改"**：★ 修 `_selected_dispatch_array` **之前**，
#     先在**已知可用**的场景上证明「**逐个桶各取 1 个**」**能稳定拿到该拿的个数**。
#      ★ 依据：上一轮五次事故全是"没验就改"（★ 事实 320/323/329/330/332/335）。
#   ⚠ **改它影响面大**（★ 所有多实体载荷都过 `_selected_dispatch_array`）
#     ⇒ ★ 故本探针**只验**、**不改**；改了要跑全量 pytest。
# 官方依据: `C:\swapi\types\ISelectionMgr\GetSelectedObject6.md`（★ `Mark` 的三种取值语
#           义）·
#   `SolidWorks.Interop.sldworks.dll` 的元数据反射 · 事实 8（以计数为准）· 事实 336
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 「逐个 mark 桶各取 1 个」能拿到 **2 个不同的对象** ⇒ 修法可用。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "selection-by-marks-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sm = get_com_member(doc, "SelectionManager")

        #: ★ **两次选择用不同 mark**（★ 那就是修法的核心）
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        c1 = sim.select_face_at(doc, 0.0, 0.0, 0.0, mark=1)
        c2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True, mark=2)
        ev["selects"] = [c1, c2]
        ev["count2"] = {("mark%s" % m): repr(safe_get_com_member(sm, "GetSelectedObjectCount2", m))
                        for m in (-1, 0, 1, 2)}
        #: ★ **逐个桶各取 1 个**
        per = {}
        for mark in (1, 2):
            try:
                obj = get_com_member(sm, "GetSelectedObject6", 1, int(mark))
                per["mark%d" % mark] = {"got": obj is not None,
                                        "id": id(obj) if obj is not None else None}
            except Exception as exc:                           # noqa: BLE001
                per["mark%d" % mark] = {"got": False,
                                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])}
        ev["per_mark"] = per
        both = all(v.get("got") for v in per.values())
        distinct = len({v.get("id") for v in per.values() if v.get("id") is not None}) == 2
        ev["judge_by_marks_usable"] = bool(both and distinct)
        ev["verdict"] = "pass" if ev["judge_by_marks_usable"] else "partial"
        ev["note"] = ("★ 验「**分桶取数**」这条修法：★ 两次选择用不同 mark（1 与 2），"
                      "★ 而**逐个桶各取 1 个**（`GetSelectedObject6(1, mark)`）—— "
                      "★ 判据：**拿到两个不同的对象**。★ 验过了才准改共享助手。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1200])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
