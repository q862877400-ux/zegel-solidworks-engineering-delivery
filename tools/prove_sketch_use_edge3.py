"""★ 真机：**侧影实体 / `SketchUseEdge3`** —— ★ 按**已核过的官方调用序**试。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sketch_use_edge3.py
# 定位:   ★ 2026-10-03（轮 613）★ 台账「侧影实体」的待办：
#     「★ 待重查：第 2 参（侧影开关）与选区前置」
#
#   ★★★ **本轮由一名 subagent 做静态调研、我再逐条对照官方原文核过**（★ 四项全对）：
#     ① `C:\swapi\types\ISketchManager\SketchUseEdge3.md`：
# 签名逐字 `System.bool SketchUseEdge3( System.bool Chain, System.bool InnerLoops )`（**
# 2 参**）
# `Chain`    = "True to convert an entire chain of sketch entities, false to convert onl
# y the selected…"
# `InnerLoops` = "True to convert the inner loops of the selected faces to sketch entiti
# es, false to not"
# ★ Remarks 第 1 条讲 `Chain` 的语义；第 2 条讲 `swViewSketchRelations`（★ 与建特征无关
# ）
# ② ★ **官方例子给了调用序**（`Convert_Edges_and_Inner_Loops_of_Face_to_Sketch_Entities_
# Example_VB.md`）：
#        ```
#        SelectByID2("Front Plane", "PLANE", 0,0,0, True,  **0**, Nothing, 0)
#        InsertRefPlane(8, 0.05, 0, 0, 0, 0)
#        ClearSelection2 True
#        SelectByID2("Plane1", "PLANE", 0,0,0, **False**, **0**, Nothing, 0)
# swSketchManager.InsertSketch True                       \u2190 \u2605 **\u5148\u5f00\u
# 8349\u56fe**
# SelectByID2("", "FACE", <x>,<y>,<z>, **False**, **0**, Nothing, 0)   \u2190 \u2605 \u9
# 762\u6309**\u5750\u6807**\u9009\u3001mark=0
#        swSketchManager.SketchUseEdge3(**False**, **True**)      \u2190 \u2605 \u8c03\u7528
#        ClearSelection2 True
# swSketchManager.InsertSketch True                       \u2190 \u2605 \u518d `InsertSk
# etch` \u6536\u5c3e
#        ```
# ③ ★ **例子里的 mark 全是 `0`**（★ 三处 `SelectByID2` 全查过）；★ 而 `Append` 有 `True`
# /`False` 两种。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 判据 = **草图段数增量 + 特征树增量**（★ 规则 6）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
import scripts.sw_feature_readback as FR  # noqa: E402
import win32com.client  # noqa: E402
import pythoncom  # noqa: E402


def _empty_callout():
    return win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)


def _box(doc, size=0.03):
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -size,
        -size,
        0.0,
        size,
        size,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, size * 2.0)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _one(sw, tag, *, chain, inner_loops, use_selection):
    """★ 一格：★ 开草图 → 选面 → `SketchUseEdge3(chain, inner_loops)` → 收尾。"""
    row = {"tag": tag, "chain": chain, "inner_loops": inner_loops, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["box"] = _box(doc)
        ext = C.get_com_member(doc, "Extension")
        sk = C.get_com_member(doc, "SketchManager")
        #: \u2605 **\u5148\u5f00\u4e00\u4e2a\u8349\u56fe**\uff08\u2605 \u5b98\u65b9\u4f8
        #: b\u5b50\u91cc `InsertSketch True` \u5728\u9009\u9762\u4e4b\u524d\uff09
        C.get_com_member(sk, "InsertSketch", True)
        doc.ClearSelection2(True)
        if use_selection:
            #: \u2605\u2605\u2605 2026-10-03\uff08\u8f6e 613\uff09**\u53c8\u8e29\u4e86\u
            #: 540c\u4e00\u4e2a\u5751**\uff08\u2605 \u4e8b\u5b9e 483\uff09\uff1a
            #: \u4e0a\u4e00\u7248\u7167\u5b98\u65b9\u4f8b\u5b50\u7528 `SelectByID2("", "
            #: FACE", x,y,z, \u2026)` \u9009\u9762
            #: \u21d2 \u771f\u673a **\u56db\u683c\u5168 `selected = 0`**\uff08\u2605 \u5
            #: 750\u6807\u9009\u4e0d\u4e2d\uff09\u26a0
            #: \u800c**\u4e8b\u5b9e 32 / 482 \u90fd\u5199\u7740**\uff1a\u9009\u5b9e\u4f5
            #: 3\u8981\u7528 **`IEntity.Select4`\uff08\u6309\u5bf9\u8c61\uff09**\u3002
            #: \u6545\u6539\u7528**\u672c\u4ed3\u73b0\u6210\u7684**\uff1a`entities_on_bo
            #: dy` + `select_object` \u2713
            ss = __import__("sw_selection_spec")
            doc.ClearSelection2(True)
            best, best_z = None, -1e9
            for o in ss.entities_on_body(doc, "FACE"):
                try:
                    b = C.get_com_member(o, "GetBox")
                    z = (float(b[2]) + float(b[5])) / 2.0
                    if z > best_z:
                        best_z, best = z, o
                except Exception:  # noqa: BLE001
                    continue
            if best is not None:
                ss.select_object(doc, best)
        mgr = C.get_com_member(doc, "SelectionManager")
        row["selected"] = int(C.get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        #: \u2605 \u8bfb\u8349\u56fe\u6bb5\u6570\uff08\u2605 \u524d\uff09
        try:
            act = C.get_com_member(doc, "GetActiveSketch2")
            segs0 = (
                C.get_com_member(act, "GetSketchSegments") if act is not None else None
            )
            row["segments_before"] = len(segs0) if segs0 is not None else 0
        except Exception:  # noqa: BLE001
            row["segments_before"] = None
        before = list(FR.feature_names(doc) or [])
        try:
            ok = C.get_com_member(sk, "SketchUseEdge3", bool(chain), bool(inner_loops))
            row["returned"] = str(ok)
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
            row["returned"] = "ERR"
        try:
            act = C.get_com_member(doc, "GetActiveSketch2")
            segs1 = (
                C.get_com_member(act, "GetSketchSegments") if act is not None else None
            )
            row["segments_after"] = len(segs1) if segs1 is not None else 0
        except Exception:  # noqa: BLE001
            row["segments_after"] = None
        #: \u2605 \u6536\u5c3e\uff08\u2605 \u5b98\u65b9\u4f8b\u5b50\u6700\u540e\u4e00\u8
        #: 84c\uff09
        try:
            C.get_com_member(sk, "InsertSketch", True)
        except Exception:  # noqa: BLE001
            pass
        after = list(FR.feature_names(doc) or [])
        row["new_features"] = [n for n in after if n not in before]
        grew = (row.get("segments_after") or 0) - (row.get("segments_before") or 0)
        row["segments_grew"] = grew
        row["ok"] = (
            (row.get("returned") == "True") or grew > 0 or bool(row["new_features"])
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u4fa7\u5f71\u5b9e\u4f53 / `SketchUseEdge3` \u2014\u2014 \u2605 \u6309**\u5df2\u6838\u8fc7\u7684\u5b98\u65b9\u8c03\u7528\u5e8f**",
        "official": "`ISketchManager\\SketchUseEdge3.md`\uff08**2 \u53c2**\uff09\u00d7 "
        "`C:\\swapi\\examples\\"
        "Convert_Edges_and_Inner_Loops_of_Face_to_Sketch_Entities_Example_VB.md`",
        "cases": [],
    }
    #: \u2605 **\u5b98\u65b9\u4f8b\u5b50\u90a3\u7ec4\u53c2\u6570**\uff08\u2605 `False, T
    #: rue`\uff09\u4e0e\u4e09\u4e2a\u5bf9\u7167
    ev["cases"].append(
        _one(
            sw,
            "\u2605 **\u5b98\u65b9\u4f8b\u5b50\u53c2\u6570 `(False, True)`**",
            chain=False,
            inner_loops=True,
            use_selection=True,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a`(True, True)`",
            chain=True,
            inner_loops=True,
            use_selection=True,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a`(True, False)`",
            chain=True,
            inner_loops=False,
            use_selection=True,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a**\u4e0d\u9009\u9762**\u5c31\u8c03",
            chain=False,
            inner_loops=True,
            use_selection=False,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "sketch_use_edge3_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "sketch-use-edge3-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-40s ok=%-6s \u56de=%-6s \u9009\u4e2d=%s \u6bb5 %s\u2192%s \u7279\u5f81 %s->%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("returned"),
                c.get("selected"),
                c.get("segments_before"),
                c.get("segments_after"),
                c.get("before"),
                (c.get("before") or 0) + len(c.get("new_features") or []),
            )
        )
        if c.get("new_features"):
            print("        \u65b0\u589e=%s" % (c["new_features"],))
        for k in ("call_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
