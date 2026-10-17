"""★ 真机：分辨「两个 mark 桶」还是「同一个桶里的两个」—— 量 `GetSelectedObjectCount2` 按 mark 的取值。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_selection_marks_split.py
# 定位:   ★ 2026-10-03（轮 422）承本轮那条**系统性发现**：
#   ★★ 同一份选区（两个面，`select_face_at` 两次、第二次 `append=True`）：
#     ```
#     GetSelectedObjectCount2(**-1**) ⇒ **2**
#     而「按位置取对象」那**四个入口**（GetSelectedObject4 / 5 / 6(i,-1) / 6(i,0)）
#        ⇒ ★ **都只取得到第 1 个**（★ 第 2 个如实回 `None`，★ 不是异常被吞）
#     ```
#   ★★ 而它**解释**了 B 组为什么崩：★ `_selected_dispatch_array` **只读到第一个**
#     ⇒ ★ 传**不完整的数组**给 `AddRigidConnector(SourceFaces, TargetFaces)`
#     ⇒ ★★ SW 内部越界 ⇒ **RPC 服务器不可用**（`0x800706BA` / `0x800706BE`）。
#   ★★★ **两个候选解释**（★ 本探针就为分辨它们）：
#     ```
#     ① **两个 mark 桶**：★ `Count2(-1)` 把两个桶加起来报 2，★ 而"取对象"那族只认当前桶
#        ⇒ ★ 修法：**两次选择用同一个 mark**
#     ② **同一个桶**：★ 那 `Count2(0)` 也应是 2，★ 而"取对象"那族**自己**只能回第一个
#        ⇒ ★ 修法在**调用方式**（★ 或那条路根本不可用）
#     ```
#     ⇒ ★★ 判据：★ **`Count2(0)` 是几** —— ★ 2 ⇒ 候选②；★ 1 ⇒ 候选① ✓
# 官方依据: `SolidWorks.Interop.sldworks.dll` 的元数据反射 · 事实 8（返回值不可信，以计数为准）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 拿到 `Count2` 在 mark = -1 / 0 / 1 三处的取值，★ 以及第二种选法（mark=1,2）的结果。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "selection-marks-split-evidence.json")


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

        def counts() -> dict:
            return {("mark%s" % m): repr(safe_get_com_member(sm, "GetSelectedObjectCount2", m))
                    for m in (-1, 0, 1, 2)}

        #: ★ 选法 A：两次都默认 mark=0（★ 即 B 组探针的用法）
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        a1 = sim.select_face_at(doc, 0.0, 0.0, 0.0)
        a2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True)
        ev["A_default_mark"] = {"selects": [a1, a2], "counts": counts()}
        ev["A_gso6"] = {"i1_none": safe_get_com_member(sm, "GetSelectedObject6", 1, -1) is None,
                        "i2_none": safe_get_com_member(sm, "GetSelectedObject6", 2, -1) is None}

        #: ★ 选法 B：**两次用不同的 mark**（★ 逐个 mark 桶取）
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        b1 = sim.select_face_at(doc, 0.0, 0.0, 0.0, mark=1)
        b2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True, mark=2)
        ev["B_two_marks"] = {"selects": [b1, b2], "counts": counts()}
        ev["B_gso6"] = {"i1_none": safe_get_com_member(sm, "GetSelectedObject6", 1, -1) is None,
                        "i2_none": safe_get_com_member(sm, "GetSelectedObject6", 2, -1) is None}

        a = (ev["A_default_mark"]["counts"] or {}).get("mark0")
        ev["verdict"] = "pass" if a is not None else "partial"
        ev["note"] = ("★ 分辨「两个 mark 桶」还是「同一个桶里的两个」：★ 看 **`Count2(mark0)`** —— "
                      "★ 2 \u21d2 \u5019\u9009\u2461\uff08\u53d6\u5bf9\u8c61\u90a3\u65cf\u81ea\u5df1\u53ea\u80fd\u56de\u7b2c\u4e00\u4e2a\uff09\uff1b"
                      "★ 1 \u21d2 \u5019\u9009\u2460\uff08\u4e24\u4e2a\u6876\uff0c\u2605 \u4fee\u6cd5\u662f\u4e24\u6b21\u9009\u62e9\u7528\u540c\u4e00\u4e2a mark\uff09\u3002"
                      "★ 选法 B\uff08mark=1,2\uff09\u770b\u201c\u9010\u4e2a mark \u6876\u53d6\u201d\u80fd\u4e0d\u80fd\u62ff\u5230\u4e24\u4e2a\u3002")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  \u4ea7\u7269: %s" % OUT)
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
