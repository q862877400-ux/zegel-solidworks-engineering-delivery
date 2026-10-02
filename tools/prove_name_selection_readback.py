"""★ 真机：按**名字**选草图线段，★ 看 `GetSelectedObject6(i, 0)` 读不读得到**多实体**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_name_selection_readback.py
# 定位:   ★ 2026-10-03（轮 444）承**事实 358** —— ★ 官方结构系统示例里那句
#   ```
#   Set segments(0) = swSelMgr.GetSelectedObject6(1, 0)     ' ★ 而它一次读**6**个
#   ```
#   ★★ 而**事实 337** 记的是：★ `GetSelectedObject6(2, -1)` 回 `None` 而计数为 2 ⇒
#     ★ 当时我判「**读多实体那条路不通**」，★ 改用 `entities_as_array`。
#   ★★★ **而两者的差别在**选择的方式****：
#     ```
#     ★ 官方示例：★ `SelectByID2("Line3@3DSketch1", "EXTSKETCHSEGMENT", 0,0,0, True, 0, Nothing, 0)`
#        ⇒ ★ **按名字选** —— ★ 而草图线段**有**名字（★ 事实 32 说的是**边/面**没名字）⚠
#     ★ 我实测的：★ 按点（`SelectByID2("", "EDGE", x,y,z, …)`）或按对象（`Select4`）
#     ```
#   ⇒ ★★ **本探针的判据**：★ **按名字选 2 条线段，然后看 `GetSelectedObject6(i, 0)` 回不回对象** ✓
# ★ 判据（★ 两条都要）：
#     ① `GetSelectedObjectCount2(-1)` == 2（★ 命中几条）
#     ② `GetSelectedObject6(2, 0)` **非 None**（★ 而那就是"读得到多实体"）
# 官方依据: `IModelDocExtension.SelectByID2`（★ 9 参）· `ISelectionMgr.GetSelectedObject6`
#   （★ 官方示例用法见事实 358）· 事实 8（bool 不可信，要回读计数）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（① 计数 ② 第二个对象非 None）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\name-selection-readback-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import _empty_callout, current_sketch_name, end_sketch, sketch_line, start_sketch

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, -40.0, 0.0, 40.0, 0.0)
        sketch_line(doc, -40.0, 20.0, 40.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        ext = get_com_member(doc, "Extension")
        sm = get_com_member(doc, "SelectionManager")
        ev["sketch"] = sk

        #: ★ 两种选法各试一轮（★ 而**每轮前先清选区**）
        for label, use_name in (("by_name", True), ("by_point", False)):
            rec: dict = {"trial": label}
            try:
                safe_get_com_member(doc, "ClearSelection2", True)
                if use_name:
                    #: ★ 按**名字**选（★ 官方示例的写法）
                    for i in (1, 2):
                        st = ext.SelectByID2("Line%d@%s" % (i, sk), "EXTSKETCHSEGMENT",
                                             0.0, 0.0, 0.0, True, 0, _empty_callout(), 0)
                        rec["stat_L%d" % i] = bool(st)
                else:
                    #: ★ 按**点**选（★ 我事实 337 那一族）
                    for y in (0.0, 0.02):
                        st = ext.SelectByID2("", "EDGE", 0.0, y, 0.0, True, 0, _empty_callout(), 0)
                        rec.setdefault("stat_pt", []).append(bool(st))
                rec["count2_minus1"] = int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)
                rec["count2_0"] = int(get_com_member(sm, "GetSelectedObjectCount2", 0) or 0)
                #: ★★ 核心：★ 第 2 个对象读不读得到
                for idx in (1, 2):
                    got = get_com_member(sm, "GetSelectedObject6", idx, 0)
                    rec["obj%d_is_none" % idx] = got is None
                    if got is not None:
                        try:
                            rec["obj%d_type" % idx] = str(get_com_member(got, "GetType") or "")
                        except Exception:                      # noqa: BLE001
                            rec["obj%d_type" % idx] = "?"
            except Exception as exc:                           # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            ev["trials"].append(rec)

        byname = next((t for t in ev["trials"] if t["trial"] == "by_name"), {})
        ev["by_name_reads_second"] = (byname.get("count2_minus1") == 2
                                      and byname.get("obj2_is_none") is False)
        ev["by_name_counts_two"] = byname.get("count2_minus1") == 2
        ev["verdict"] = "pass" if ev["by_name_reads_second"] else (
            "partial" if ev["by_name_counts_two"] else "fail")
        ev["note"] = ("★ 验事实 358 提的那个假设：★ **按名字选草图线段**（EXTSKETCHSEGMENT）后，"
                      "`GetSelectedObject6(2, 0)` 读不读得到**第二个**对象。"
                      "★ 判据：① 计数 == 2；★ ② 第 2 个对象非 None。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1400])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
