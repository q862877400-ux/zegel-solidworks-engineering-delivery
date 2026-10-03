"""★ 真机：**复合曲线** —— 照官方例子的形态（★ 两个各含一条样条的草图 + SelectByID2 按名选）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_composite_curve_per_example.py
# 定位:   ★ 2026-10-03（轮 573）★ 执行**事实 450 留的下一步**（★ 照**官方例子**的形态）。
#
#   ★★★★★ **官方例子（CHM）逐字**（`Insert_a_Composite_Curve_Example_VBNET.htm`）：
#     > "This example shows how to insert a composite curve **using two sketches of splines**."
#     > "2. Creates a **sketch of a spline**.\n"
#     > "3. Creates **another sketch of a spline**.\n"
#     > "4. Inserts a composite curve **using the sketches** created in steps 2 and 3."
#     ★ 而它的**调用序**：`CreateSpline2` ×2 \u2192 **`SelectByID2` ×2** \u2192 **`InsertCompositeCurve`**
#       \u2192 \u518d\u7528 `SelectionMgr.Feature` \u53d6 `ICompositeCurveFeatureData` \u2192 `GetEntitiesToJoinCount` \u8bfb\u56de\u3002
#
#   ★★ **故与上一轮（失败那轮）的区别**：
#     · \u4e0a\u4e00\u8f6e\u9009\u7684\u662f**\u76f4\u7ebf\u6bb5 / \u4f53\u7684\u8272**\uff08\u2605 \u4e0d\u662f\u4f8b\u5b50\u91cc\u7684\u5f62\u6001\uff09
#     · \u672c\u8f6e\u9009\u7684\u662f**\u6574\u6761**\u6837\u6761\u8349\u56fe****\uff0c\u2605 \u800c\u4e14\u7528
#       **`SelectByID2` \u6309\u540d\u5b57\u9009**\uff08\u2605 \u8349\u56fe\u662f**\u7279\u5f81** \u2014\u2014 \u4e8b\u5b9e 32 \u8bf4\u7279\u5f81**\u6709\u540d\u5b57**\uff09
#
#   ★ 判据（★ 规则 6）：**特征树增量** **或** **创建对象** **或** **`GetEntitiesToJoinCount` 读回 > 0**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组：样条草图（照例子）/ 对照（直线草图）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import pythoncom
import win32com.client
from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _sketch_with_spline(doc, plane, pts):
    """★ 一个**只含一条样条**的草图（★ 例子里的形态）。

    ⚠ 2026-10-03（轮 575）★ **本函数原来用 `CreateSpline(pts)` —— 那是建不出来的形态**：
      ★ 事实 452 证明**三个条件缺一不可**：
        · 成员名 = **`CreateSpline2`**（`CreateSpline` 在迟到绑定下**取不到**）
        · 数组形态 = **`VARIANT(VT_ARRAY|VT_R8, 扁平 list)`**
        · 第二参 = **`False`**（`SimulateNaturalEnds`）
      ⇒ ★★ **故上一轮那一组"卡在造样条上"是我这边的错**（★ 而事实 451 已如实记成"未跑到那一步"）✓
    """
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    sm = C.get_com_member(doc, "SketchManager")
    data = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(pts))
    C.get_com_member(sm, "CreateSpline2", data, False)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    return names[-1] if names else None


def _sketch_with_line(doc, plane):
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                     -0.02, 0.0, 0.0, 0.02, 0.0, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    return names[-1] if names else None


def _one(sw, tag, use_spline):
    row = {"tag": tag, "use_spline": use_spline, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        if use_spline:
            s1 = _sketch_with_spline(doc, "Front Plane",
                                     [-0.02, -0.01, 0.0, 0.0, 0.02, 0.0, 0.02, -0.01, 0.0])
            s2 = _sketch_with_spline(doc, "Top Plane",
                                     [-0.02, 0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.0, 0.0])
        else:
            s1 = _sketch_with_line(doc, "Front Plane")
            s2 = _sketch_with_line(doc, "Top Plane")
        row["sketches"] = [s1, s2]
        #: \u2605 \u7167\u4f8b\u5b50\uff1a**`SelectByID2` \u00d72**\uff08\u2605 \u6309\u540d\u5b57\u9009\u8349\u56fe\uff09
        ext = C.get_com_member(doc, "Extension")
        picked = []
        for sk in (s1, s2):
            for cand in (P._get_sketch_name_candidates(sk) if sk else []):
                try:
                    if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=1):
                        picked.append(cand)
                        break
                except Exception:                                         # noqa: BLE001
                    continue
        row["picked"] = picked
        try:
            row["sel"] = int(C.get_com_member(
                C.get_com_member(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            row["sel"] = -1
        before = list(FR.feature_names(doc) or [])
        r = P.insert_composite_curve_report(doc, "")
        row["report"] = dict(r or {})
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        #: \u2605 \u7167\u4f8b\u5b50\u7684\u8bfb\u56de\uff1a`SelectionMgr.Feature` \u2192 `ICompositeCurveFeatureData`
        if row["new"]:
            try:
                from sw_connect import get_com_member as _g
                fobj = _g(doc, "FeatureByName", row["new"][-1])
                data = _g(fobj, "GetDefinition")
                row["data_type"] = type(data).__name__ if data is not None else "None"
                if data is not None:
                    row["entities_to_join"] = int(_g(data, "GetEntitiesToJoinCount") or 0)
            except Exception as exc:                                      # noqa: BLE001
                row["readback_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
        row["ok"] = bool(row["new"] or (r or {}).get("present")
                         or (row.get("entities_to_join") or 0) > 0)
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u590d\u5408\u66f2\u7ebf\uff1a\u7167**\u5b98\u65b9\u4f8b\u5b50**\u7684\u5f62\u6001"
               "\uff08**\u4e24\u4e2a\u5404\u542b\u4e00\u6761\u6837\u6761\u7684\u8349\u56fe** + `SelectByID2` \u6309\u540d\u9009\uff09",
          "official": "Insert_a_Composite_Curve_Example_VBNET.htm\uff1a"
                      "\"using **two sketches of splines**\"\uff1b\u5e8f = CreateSpline2 \u00d72 \u2192 "
                      "SelectByID2 \u00d72 \u2192 InsertCompositeCurve",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u4e24\u4e2a**\u6837\u6761**\u8349\u56fe\uff08\u7167\u4f8b\u5b50\uff09", True))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u4e24\u4e2a**\u76f4\u7ebf**\u8349\u56fe", False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "composite_per_example_works" if ev["cases"][0].get("ok") else "composite_per_example_fails"
    p = R / "output" / "composite-curve-per-example-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-40s ok=%-6s sel=%s" % (c.get("tag"), c.get("ok"), c.get("sel")))
        print("        \u8349\u56fe=%s \u9009\u4e2d=%s" % (c.get("sketches"), c.get("picked")))
        rep = c.get("report") or {}
        rb = rep.get("readback") if isinstance(rep.get("readback"), dict) else {}
        print("        report.ok=%s present=%s" % (rep.get("ok"), (rb or {}).get("present")))
        if rep.get("error"):
            print("        error=%s" % str(rep["error"])[:120])
        print("        \u65b0\u589e=%s data=%s \u5b9e\u4f53\u6570=%s" % (
            c.get("new"), c.get("data_type"), c.get("entities_to_join")))
        for k in ("err", "readback_err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:130]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
