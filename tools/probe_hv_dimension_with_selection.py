"""★ 真机：水平/竖直尺寸 —— **选中实体后**再试（★ 事实 421 留的下一步）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_hv_dimension_with_selection.py
# 定位:   ★ 2026-10-03（轮 542）★ 执行**上一轮留在事实 421 里的下一步**：
#
#   > ★ **下一步**：★ 选中**一条边或两个点**后再试那两个方法
#   >   （★ 而**不是**继续读作"会挂"）。
#
#   ★★ **背景（事实 421）**：T501/T502 此前被记作「**会挂**」（`sw_alive: null`）⚠
#     ★ 而**护栏早就落盘了那个弹窗**（`output/dialog-events/2026-10-03T13:4*.json`）——
#     控件树是 `Statics"SLIDER" × 3 · Buttons"THUMB WHEEL" × 3` ⇒
# ★★ **那是 SolidWorks 的「修改」框（数值输入框）**，★ 而 `hung = **false**`（★ **没挂**
# ）⚠
#     ⇒ ★ **故它不是"挂"、而是"缺前置"** ⇒ ★ 典型情形：**没选中合适实体**。
#
#   ★ 本探针照那条下一步做：
#     · 草图画**一条水平直线**（★ 与 X 轴共线，★ 好让"水平尺寸"有意义）
#     · ★ **按对象选那条线段**（★ 草图段没有名字 —— 事实 32 ⇒ 按对象选）
#     · 调 `AddHorizontalDimension2` / `AddVerticalDimension2`
#   ★ 并试三种选法（★ 因为"选什么"正是待定的）：
#     ⓐ 选**一条线段**（★ 一条）
#     ⓑ 选**两个端点**（★ 两个）
#     ⓒ 不选（★ 对照 —— ★ 那正是会弹"修改"框的那种）
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 406/420）：**尺寸计数增加** **或** **树增量** **或** **返回对
# 象**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_sketch_with_line(doc):
    """★ 画一条**水平线段**并**保持草图打开**（★ 尺寸要在草图里建）。"""
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    C.get_com_member(sm, "CreateLine", -0.02, 0.0, 0.0, 0.02, 0.0, 0.0)
    return sm


def _segments_and_points(doc):
    """★ 取当前草图的**段**与**端点**（★ 供按对象选 —— 事实 32）。"""
    segs, pts = [], []
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
    except Exception:                                                     # noqa: BLE001
        sk = None
    if sk is None:
        return segs, pts
    try:
        for s in list(C.get_com_member(sk, "GetSketchSegments") or []):
            segs.append(s)
            for m in ("GetStartPoint2", "GetEndPoint2"):
                try:
                    v = C.get_com_member(s, m)
                    if v is not None:
                        pts.append(v)
                except Exception:                                         # noqa: BLE001
                    pass
    except Exception:                                                     # noqa: BLE001
        pass
    return segs, pts


def _dim_count(doc):
    """★ 数当前草图里的**显示尺寸**（★ 判据）。

    ★★★ 2026-10-03（轮 542）**修**：第一版我用了 `ISketch.GetDisplayDimensions()`
      ⇒ ★ **回 `-1`**（★ 取不到、★ 而判据就废了）⚠
      ⇒ ★★ **改用本仓 B5 探针的手法**（`tools/prove_b5_sketch_dimensions.py` 的 `dim_count`）：
        ★ **在草图特征上走 `IFeature.GetFirstDisplayDimension` + `IAnnotation.GetNext2`** ✓
      ⚠ ★ 这与上一轮（事实 418）那条教训**同一条**：★ **不要手搓、用本仓现成的**。
    """
    try:
        names = [n for n in (FR.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        if not names:
            return -1
        feat = None
        for cand in P._get_sketch_name_candidates(names[-1]):
            try:
                feat = C.get_com_member(doc, "FeatureByName", cand)
                if feat is not None:
                    break
            except Exception:                                             # noqa: BLE001
                continue
        if feat is None:
            return -1
        dd = C.get_com_member(feat, "GetFirstDisplayDimension")
        n = 0
        while dd is not None and n < 200:
            n += 1
            try:
                dd = C.get_com_member(dd, "GetNext2")
            except Exception:                                             # noqa: BLE001
                break
        return n
    except Exception:                                                     # noqa: BLE001
        return -1


def _one(sw, tag, kind):
    row = {"tag": tag, "kind": kind, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_sketch_with_line(doc)
        segs, pts = _segments_and_points(doc)
        row["n_segs"] = len(segs)
        row["n_pts"] = len(pts)
        from sw_part import _select_com_object as _sel
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        picked = 0
        if kind == "seg":
            if segs and _sel(segs[0], append=False, mark=0):
                picked = 1
        elif kind == "two_points":
            for v in pts[:2]:
                if _sel(v, append=(picked > 0), mark=0):
                    picked += 1
        row["picked"] = picked
        before = _dim_count(doc)
        row["dim_before"] = before
        ret = None
        try:
            ret = C.get_com_member(doc, "AddHorizontalDimension2", 0.0, 0.0, 0.0)
            row["h_returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["h_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        after_h = _dim_count(doc)
        row["dim_after_h"] = after_h
        try:
            ret2 = C.get_com_member(doc, "AddVerticalDimension2", 0.0, 0.0, 0.0)
            row["v_returned"] = type(ret2).__name__ if ret2 is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["v_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        row["dim_after_v"] = _dim_count(doc)
        row["ok"] = bool((after_h > before) or (row["dim_after_v"] > before))
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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
          "_": "\u6c34\u5e73/\u7ad6\u76f4\u5c3a\u5bf8\uff1a**\u9009\u4e2d\u5b9e\u4f53\u540e**\u518d\u8bd5\uff08\u2605 \u4e8b\u5b9e 421 \u7684\u4e0b\u4e00\u6b65\uff09",
          "why": "\u4e8b\u5b9e 421\uff1a\u90a3\u5f39\u7684\u662f**\u6570\u503c\u8f93\u5165\u6846**\u3001`hung=false` \u21d2 "
                 "\u5b83\u662f\u201c\u7f3a\u524d\u7f6e\u201d\u3001\u800c\u4e0d\u662f\u201c\u6302\u201d",
          "cases": []}
    for tag, kind in (("\u2605 \u9009**\u4e00\u6761\u7ebf\u6bb5**", "seg"),
                      ("\u2605 \u9009**\u4e24\u4e2a\u7aef\u70b9**", "two_points"),
                      ("\u5bf9\u7167\uff1a**\u4e0d\u9009**", "none")):
        ev["cases"].append(_one(sw, tag, kind))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "hv_dimension_works" if ev["passed"] else "still_no_dimension"
    p = R / "output" / "hv-dimension-with-selection-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-26s ok=%-6s \u6bb5=%s \u70b9=%s picked=%s" % (
            c.get("tag"), c.get("ok"), c.get("n_segs"), c.get("n_pts"), c.get("picked")))
        print("        \u5c3a\u5bf8 %s \u2192 H:%s \u2192 V:%s" % (
            c.get("dim_before"), c.get("dim_after_h"), c.get("dim_after_v")))
        print("        H\u56de=%s V\u56de=%s" % (c.get("h_returned"), c.get("v_returned")))
        for k in ("h_err", "v_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
