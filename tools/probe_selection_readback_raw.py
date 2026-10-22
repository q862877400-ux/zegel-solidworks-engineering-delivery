"""★ 真机：直接按序号读选区对象 —— ★ 看第 2 个到底抛了什么（`safe_get_com_member` 会吞异常）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_selection_readback_raw.py
# 定位:   ★ 2026-10-03（轮 422）承本轮的**决定性发现**：
#   ★★ 同一份选区（两个面），★ **两条读法给出的数不一样**：
#     ```
# SelectionManager.GetSelectedObjectCount2(-1)          ⇒ **2**   （select_face_at 用的
# ）
# SelectionManager.GetSelectedObject6(1..2, -1) 逐个数  ⇒ **1**   （_selected_dispatch_a
# rray 用的）
#     ```
#     ⇒ ★ 而**传一个不完整的数组**给 `AddRigidConnector(SourceFaces, TargetFaces)`
#       ⇒ ★★ SW 内部越界 ⇒ **RPC 服务器不可用**（★ 那正是 B 组四次"崩"的真因嫌疑）。
#   ★★ **官方签名已查**（`C:\swapi\types\ISelectionMgr\GetSelectedObject6.md`）：
#     `GetSelectedObject6(Index, Mark)`，★ `Index` **从 1 到 `GetSelectedObjectCount2`**，
#     ★ `Mark = -1` = **All selections regardless of marks** ⇒ ★ **我们的调用形态是对的**。
#   ⇒ ★★★ **那为什么只读到 1 个？** ★ 本探针**直接读、把异常打出来** ——
#     ★ 因为 `_selected_dispatch_array` 用的是 `safe_get_com_member`，
#       ★★ **它会吞异常并回 `None`** ⇒ ★ **一次异常就被当成"没有更多了"**，★ 循环提前 break ⚠
# 官方依据: `C:\swapi\types\ISelectionMgr\GetSelectedObject6.md`（★ 上面那段逐字）·
#   `GetSelectedObjectCount2`（事实 8：返回值可信的那一个）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 拿到**每个序号的原始取值或原始异常** ⇒ ★ 才能判"是读不到，还是抛了异常"。

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
    / "selection-readback-raw-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

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

        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        c1 = sim.select_face_at(doc, 0.0, 0.0, 0.0)
        c2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True)
        ev["selection"] = {"count_via_count2": [c1, c2]}
        sm = get_com_member(doc, "SelectionManager")
        ev["count2_readback"] = repr(
            safe_get_com_member(sm, "GetSelectedObjectCount2", -1)
        )

        #: ★ **直接读**（★ 带异常的原文），★ 两种 mark 都试
        per_mark = {}
        for mark in (-1, 0):
            rows = []
            for i in range(1, 5):
                try:
                    obj = get_com_member(sm, "GetSelectedObject6", int(i), int(mark))
                    rows.append(
                        {"index": i, "raw": repr(obj)[:70], "is_none": obj is None}
                    )
                except Exception as exc:  # noqa: BLE001
                    rows.append(
                        {
                            "index": i,
                            "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                        }
                    )
            per_mark["mark=%d" % mark] = rows
        ev["per_index"] = per_mark
        #: ★ 也读一下 `safe_get_com_member` 那条（★ 复现 `_selected_dispatch_array` 的行
        #: 为）
        safe_rows = []
        for i in range(1, 5):
            obj = safe_get_com_member(sm, "GetSelectedObject6", int(i), -1)
            safe_rows.append({"index": i, "is_none": obj is None})
        ev["via_safe_helper"] = safe_rows
        ev["note"] = (
            "★ 直接按序号读，★ 把**原始值或原始异常**都记下来 —— ★ 才能分清"
            "「读不到」与「抛了异常被吞掉」。★ 两种 mark（-1 与 0）都试。"
        )
        ev["verdict"] = "pass" if ev.get("per_index") else "partial"
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1800])
        print("  产物: %s" % OUT)
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
