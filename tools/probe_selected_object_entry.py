"""★ 真机：**按位置取选区对象**的正确入口 —— `GetSelectedObject5` / `4` vs `GetSelectedObject6`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_selected_object_entry.py
# 定位:   ★ 2026-10-03（轮 422）承本轮的**两条决定性发现**：
#   ★★ ① 同一份选区（两个面），**两条读法给出不同的数**：
#     ```
#     SelectionManager.GetSelectedObjectCount2(-1)     ⇒ **2**
#     SelectionManager.GetSelectedObject6(1..2, -1)    ⇒ **1**（★ 第 2 个如实回 `None`，★ 不是异常被吞）
#     ```
#     ⇒ ★ 而**传不完整的数组**给 `AddRigidConnector(SourceFaces, TargetFaces)` ⇒ SW 内部越界
#       ⇒ **RPC 服务器不可用**（★ 那正是 B 组四次"崩"的真因嫌疑）。
#   ★★ ② 而**出厂类型库**（铁律 4 的裁决者）给出**另一代入口**：
#     ```
#     GetSelectedObject6(Index:Int32, **Mark**:Int32) -> Object
#     GetSelectedObject5(**AtIndex**:Int32)           -> Object   ← ★ 只有一个参数、**没有 Mark**
#     GetSelectedObject4(**AtIndex**:Int32)           -> Object
#     ```
#     ⇒ ★★★ **推断**：`GetSelectedObject6` 的 `Index` 是「**该 mark 的那个列表里**」的序号
#       ⇒ ★ 所以 `(2, -1)` 越界 ⇒ 回 `None` ✓
#     ⇒ ★★ 而 `GetSelectedObject5` **按位置取、不按 mark 分** ⇒ ★ 它才是"枚举整个选区"的入口。
#   ★ 本探针**逐个试**（★ 而每个都是**官方存在的方法**，★ 不是猜参数）。
# 官方依据: `SolidWorks.Interop.sldworks.dll` 的元数据反射（★ 四个方法的形参名与类型逐字）·
#   `C:\swapi\types\ISelectionMgr\GetSelectedObject6.md` · 事实 8（返回值不可信，以计数为准）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 有**某一个入口**能按位置取到**两个**对象（★ 与 `Count2` 的 2 一致）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\selected-object-entry-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)

    ev: dict = {"entries": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
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
        sm = get_com_member(doc, "SelectionManager")
        ev["count2"] = [c1, c2]
        ev["count2_readback"] = repr(safe_get_com_member(sm, "GetSelectedObjectCount2", -1))

        def try_entry(label, member, kind):
            rows = []
            for i in (1, 2, 3):
                try:
                    #: ★ 参数顺序**按官方签名**：`GetSelectedObject6(Index, Mark)` ⇒ `(i, mark)`
                    argmap = {"5": (int(i),), "4": (int(i),),
                              "6m-1": (int(i), -1), "6m0": (int(i), 0)}
                    obj = get_com_member(sm, member, *argmap[kind])
                    rows.append({"i": i, "got": obj is not None})
                except Exception as exc:                       # noqa: BLE001
                    rows.append({"i": i, "err": "%s: %s" % (type(exc).__name__, str(exc)[:90])})
            ev["entries"][label] = rows
            return sum(1 for r in rows if r.get("got"))

        got = {}
        got["GetSelectedObject5(i)"] = try_entry("GetSelectedObject5(i)", "GetSelectedObject5", "5")
        got["GetSelectedObject4(i)"] = try_entry("GetSelectedObject4(i)", "GetSelectedObject4", "4")
        got["GetSelectedObject6(i,-1)"] = try_entry("GetSelectedObject6(i,-1)", "GetSelectedObject6", "6m-1")
        got["GetSelectedObject6(i,0)"] = try_entry("GetSelectedObject6(i,0)", "GetSelectedObject6", "6m0")
        ev["got_counts"] = got
        winners = [k for k, v in got.items() if v >= 2]
        ev["entries_that_see_both"] = winners
        ev["verdict"] = "pass" if winners else "partial"
        ev["note"] = ("★ 找一个**能按位置取到两个对象**的入口（★ 与 `Count2` 的 2 一致）—— "
                      "★ 四个候选都是**官方存在的方法**，★ 逐个试，★ 不猜参数。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        for k, v in got.items():
            print("  %-26s \u53d6\u5230 %d/3" % (k, v))
        print("  \u80fd\u770b\u5230\u4e24\u4e2a\u7684\u5165\u53e3\uff1a%s" % winners)
        print("  产物: %s \u21d2 %s" % (OUT, str(ev["verdict"]).upper()))
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
