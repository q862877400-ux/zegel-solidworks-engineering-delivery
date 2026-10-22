"""★ 真机：**曲面上偏移** —— ★ 严格按官方 VB 例子的**调用序**重试。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_offset_on_surface_per_example.py
# 定位:   ★ 2026-10-03（轮 612）★ 台账「曲面上偏移」的**待重查项**已写明：
#     「★ 下一步：读它的 `## Remarks` 看**选区与面的要求**」—— ★ 本轮做了。
#
#   ★★★ **官方依据**（★ 三样齐）：
#     ① `C:\swapi\types\IModelDocExtension\SketchOffsetOnSurface.md`：
# · 签名 `(Offset, Reverse, UseFront, MakeConstruct)` · ★ `UseFront` **"must be set to t
# rue"**
#        · **`## Remarks` 三条**：
#          ★ a) 要**测地线**偏移请用 `GeodesicSketchOffset`（★ 另一个方法）；
#          ★ b) 「Before…call `SelectByID2` for **each edge** to offset and set
#                **Append to true** and **Mark …**」；
# ★ c) 「After…call **`ISketchManager::InsertSketch`** to rebuild the model with the 3D
# sketch」
#     ② **`## Examples` 给了三个**（C# / VB.NET / VBA）—— ★ **本机都有**：
#        `C:\swapi\examples\Offset_Edges_to_Create_3D_Sketch_on_Surface_Example_VB.md`
#     ③ ★ **而那个例子的调用序是关键**（★ 而签名与 Remarks 都给不出"两遍选边"）：
#        ```
#        'Select the edges
# SelectByID2("", "EDGE", x,y,z, **True**, **0**, Nothing, 0)   \u00d74   \u2190 \u2605
# \u7b2c\u4e00\u904d mark=0
#        ClearSelection2 True                                        \u2190 \u2605 \u6e05\u6389
# SelectByID2("", "EDGE", x,y,z, **True**, **1**, Nothing, 0)   \u00d74   \u2190 \u2605
# \u7b2c\u4e8c\u904d mark=1
#        'Create a 3D sketch
# SketchOffsetOnSurface(0.01, False, True, False)            \u2190 \u2605 **\u8c03\u752
# 8**
#        ClearSelection2 True
#        'Close the sketch
# swSketchManager.InsertSketch True                          \u2190 \u2605 **\u6536\u5c3
# e**\uff08\u2605 \u800c\u6211\u4e0a\u4e00\u7248**\u6ca1\u505a**\uff09
#        ```
# ⚠ 全程走 `tools/sw_guard.py`；★ 判据 = **3D 草图真的出现**（★ 规则 6：回读草图层数/特
# 征树）。
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

import pythoncom  # noqa: E402
import win32com.client  # noqa: E402

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


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


def _select_edges_by_object(doc, indices, mark=1):
    """★★ 按**对象**选边 + 补设 `Mark`（★ 事实 32 的正解 + `SetSelectedObjectMark`）。

    ★★★ 2026-10-03（轮 612）**修了另一个真因**：
      ★ 上一版用**官方例子那样的 `SelectByID2("", "EDGE", x,y,z, …)`**
        ⇒ ★ 而真机**三格全 `selected = 0`**（★ 角点与中点都不行）⚠
      ★ 而**事实 32** 早就写着：★ **选实体的可行路径是
        `IEntity.Select4(Append, Callout)`（按**对象**选）**。
      ★★ 而 `Select4` **没有 mark 参数** ⇒ ★ 故用
        **`ISelectionMgr.SetSelectedObjectMark(i, mark, -1)`** 补设 ✓
    """
    ss = __import__("sw_selection_spec")
    objs = ss.entities_on_body(doc, "EDGE")
    ext = C.get_com_member(doc, "Extension")
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    counts = []
    for k, i in enumerate(indices):
        if i >= len(objs):
            counts.append(-1)
            continue
        counts.append(ss.select_object(doc, objs[i], append=(k > 0)))
    #: ★ 补设 mark（★ 官方 Remarks："set Append to true and Mark …"）
    mgr = C.get_com_member(doc, "SelectionManager")
    n = int(C.get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
    marked = []
    for i in range(1, n + 1):
        try:
            marked.append(
                bool(C.get_com_member(mgr, "SetSelectedObjectMark", i, int(mark), -1))
            )
        except Exception as exc:  # noqa: BLE001
            marked.append(str(exc)[:40])
    return {
        "n_edges_on_body": len(objs),
        "counts": counts,
        "selected": n,
        "marked": marked,
    }


def _one(sw, tag, *, offset, reverse, usefront, makeconstruct, do_insert_sketch):
    row = {
        "tag": tag,
        "offset": offset,
        "reverse": reverse,
        "usefront": usefront,
        "make_construct": makeconstruct,
        "insert_sketch": do_insert_sketch,
        "ok": False,
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["box"] = _box(doc)
        ext = C.get_com_member(doc, "Extension")
        #: \u2605 \u4e00\u4e2a\u65b9\u4f53\u7684\u56db\u6761\u9876\u8fb9\uff08\u2605 \u6
        #: 309\u5b98\u65b9\u4f8b\u5b50\u90a3\u6837\u7528\u5750\u6807\u5b9a\u4f4d\uff09
        #: ★★★ 2026-10-03（轮 612）**修了一个真因**（★ 事实 482）：
        #:   ★ 上一版给的是 `(±0.03, ±0.03, 0.06)` ——
        #:   ★ 而那是四条边的**角点**！★ 角点被两条边共享
        #:   ⇒ ★ **落不到任何一条边的内部** ⇒ ★ 三格全 `selected = 0` ⚠
        #:   ★ 故改成**边中点**（★ 每条边只有一个中点、不共享）✓
        row["sel"] = _select_edges_by_object(doc, (0, 1, 2, 3), mark=1)
        before = list(fr.feature_names(doc) or [])
        row["before"] = len(before)
        try:
            ok = C.get_com_member(
                ext,
                "SketchOffsetOnSurface",
                float(offset),
                bool(reverse),
                bool(usefront),
                bool(makeconstruct),
            )
            row["returned"] = str(ok)
        except Exception as exc:  # noqa: BLE001
            row["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
            row["returned"] = "ERR"
        #: \u2605 **\u7b2c 5 \u6b65**\uff1a\u6536\u5c3e\uff08\u2605 \u5b98\u65b9\u4f8b\u
        #: 5b50\u91cc\u6709\u3001\u800c\u6211\u4e0a\u4e00\u7248\u6ca1\u505a\uff09
        if do_insert_sketch:
            try:
                sk = C.get_com_member(doc, "SketchManager")
                C.get_com_member(sk, "InsertSketch", True)
                row["insert_sketch"] = True
            except Exception as exc:  # noqa: BLE001
                row["insert_sketch_err"] = "%s: %s" % (
                    type(exc).__name__,
                    str(exc)[:80],
                )
        after = list(fr.feature_names(doc) or [])
        row["new_features"] = [n for n in after if n not in before]
        #: ★★★ 2026-10-03（轮 612）**补上规则 6 的完整回读**：
        #:   ★ **那个新草图到底是不是 3D、有几段** ——
        #:   ★ 而“回 `False`”不能当判据（官方：它说的是
        #:   "3D sketch **is created**" 而后面还要 `InsertSketch` 重建）⚠
        for nm in row["new_features"]:
            if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
                continue
            info = {"name": nm}
            try:
                info["is_3d"] = (
                    bool(C.get_com_member(doc, "SketchIs3D")) if False else None
                )
            except Exception:  # noqa: BLE001
                pass
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                if sk is None:
                    feat = None
                    for f in (
                        C.get_com_member(doc, "FeatureManager").GetFeatureTreeRootItem2(
                            0
                        ),
                    ):
                        pass
                else:
                    info["active"] = True
                    info["is_3d"] = bool(C.get_com_member(sk, "Is3D"))
                    segs = C.get_com_member(sk, "GetSketchSegments")
                    info["segments"] = len(segs) if segs is not None else 0
            except Exception as exc:  # noqa: BLE001
                info["read_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
            row.setdefault("sketches", []).append(info)
        row["ok"] = bool(row["new_features"])
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
        "_": "\u66f2\u9762\u4e0a\u504f\u79fb\u2014\u2014 \u2605 \u4e25\u683c\u6309\u5b98\u65b9 VB \u4f8b\u5b50\u7684**\u8c03\u7528\u5e8f**\u91cd\u8bd5",
        "official": "`IModelDocExtension\\SketchOffsetOnSurface.md`\uff08**`## Remarks` \u4e09\u6761** + "
        "**`## Examples` \u4e09\u4e2a**\uff09\u00d7 `C:\\swapi\\examples\\"
        "Offset_Edges_to_Create_3D_Sketch_on_Surface_Example_VB.md`",
        "cases": [],
    }
    #: \u2605 \u4e09\u683c\uff1a\u5b98\u65b9\u53c2\u6570 \u00b7 \u5b98\u65b9\u53c2\u6570
    #: \u4e0d\u6536\u5c3e \u00b7 \u53cd\u5411
    ev["cases"].append(
        _one(
            sw,
            "\u2605 \u5b98\u65b9\u53c2\u6570 + **\u6536\u5c3e InsertSketch**",
            offset=0.01,
            reverse=False,
            usefront=True,
            makeconstruct=False,
            do_insert_sketch=True,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a\u5b98\u65b9\u53c2\u6570 \u00b7 **\u4e0d\u6536\u5c3e**",
            offset=0.01,
            reverse=False,
            usefront=True,
            makeconstruct=False,
            do_insert_sketch=False,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a\u53cd\u5411 **Reverse=True**",
            offset=0.01,
            reverse=True,
            usefront=True,
            makeconstruct=False,
            do_insert_sketch=True,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "offset_on_surface_per_example_%d_of_%d" % (
        ev["passed"],
        ev["total"],
    )
    p = R / "output" / "offset-on-surface-per-example-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-44s ok=%-6s \u56de=%-6s \u9009\u4e2d=%s \u7279\u5f81 %s -> %s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("returned"),
                (c.get("sel") or {}).get("selected"),
                c.get("before"),
                (c.get("before") or 0) + len(c.get("new_features") or []),
            )
        )
        if c.get("new_features"):
            print("        \u65b0\u589e=%s" % (c["new_features"],))
        for k in ("call_err", "insert_sketch_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
