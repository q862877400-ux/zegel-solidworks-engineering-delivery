"""★ 真机：**样条曲线** —— 用**前人已证的第三种形态**（`VARIANT(VT_ARRAY|VT_R8)`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_spline_with_variant.py
# 定位:   ★ 2026-10-03（轮 574）★ 执行**事实 451 留的那一步**（★ 先把样条造对）。
#
#   ★★★★★ **而答案本仓早就有了** —— ★ 本轮按「**先扫已走死的路**」（AGENTS.md 那节）查了
#     `tools/probe_spline_forms.py` 与它的证据 `output/spline-forms.json`：
#     ```\n
#     \u2460 \u6241\u5e73 list                     \u21d2 ret=None  \u00b7 \u6bb5 0 \u2192 0   \u2717
#     \u2461 \u6241\u5e73 tuple                    \u21d2 ret=None  \u00b7 \u6bb5 0 \u2192 0   \u2717
#     \u2462 **`VARIANT(VT_ARRAY|VT_R8)`**    \u21d2 ret=**`CDispatch`** \u00b7 **\u6bb5 0 \u2192 1** \u2713
#     \u2463 list of tuples\uff08\u5bf9\u7167\uff09         \u21d2 ret=None             \u2717
#     ```\n
#     \u21d2 \u2605\u2605 **\u6545\u6b63\u786e\u5f62\u6001 = \u7b2c \u2462 \u79cd**\uff1b
#       \u2605 \u800c**\u6211\u4e0a\u4e00\u8f6e\u4f20\u7684\u5c31\u662f\u7b2c \u2460 \u79cd\uff08\u6241\u5e73 list\uff09\u2014\u2014 \u5df2\u77e5\u4e0d\u6210\u7684\u90a3\u4e2a** \u26a0
#
#   ★ 官方依据（`C:\swapi\types\ISketchManager\CreateSpline.md` 的 Remarks）：
#     · `PointData` = **扁平的 X,Y,Z 序列**（★ 至少两个）
#     · **2D 草图里 Z 被忽略**
#     · ★ 它**不配合** `AddToDB` / `DisplayWhenAdded`
#
#   ★ 判据（★ 规则 6 + 事实 436）：**草图段数增加**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 三格：第 ③ 种 / 第 ① 种（对照）/ 第 ④ 种（对照）。
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

import pythoncom                                                     # noqa: E402
import win32com.client                                               # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402

#: \u2605 \u6241\u5e73\u7684 X,Y,Z \u5e8f\u5217\uff08\u2605 \u5b98\u65b9\u8bf4\u81f3\u5c11\u4e24\u4e2a\uff09
PTS = [-0.02, -0.01, 0.0,
       0.0, 0.02, 0.0,
       0.02, -0.01, 0.0]


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _one(sw, tag, form):
    row = {"tag": tag, "form": form, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        before = _seg_count(doc)
        row["seg_before"] = before
        sm = C.get_com_member(doc, "SketchManager")
        ret = None
        try:
            if form == "variant_r8":
                #: \u2605\u2605 \u7b2c \u2462 \u79cd\uff08\u2605 \u524d\u4eba\u5df2\u8bc1\uff09
                data = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(PTS))
                ret = C.call_com_member(sm, "CreateSpline", data)
            elif form == "spline2":
                #: ★★ **前人探针原样**：`CreateSpline2(data, False)`
                #:   （`tools/probe_spline_forms.py` L99 逐字）
                data = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(PTS))
                ret = C.get_com_member(sm, "CreateSpline2", data, False)
            elif form == "flat_list":
                ret = C.call_com_member(sm, "CreateSpline", list(PTS))
            else:
                tuples = [(PTS[i], PTS[i + 1], PTS[i + 2]) for i in range(0, len(PTS), 3)]
                ret = C.call_com_member(sm, "CreateSpline", tuples)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg_after"] = after
        row["new_segments"] = (after - before) if (after >= 0 and before >= 0) else None
        row["ok"] = bool(row["new_segments"] and row["new_segments"] > 0)
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
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
          "_": "\u6837\u6761\u66f2\u7ebf\uff1a\u7528**\u524d\u4eba\u5df2\u8bc1\u7684\u7b2c\u4e09\u79cd\u5f62\u6001**"
               "\uff08`VARIANT(VT_ARRAY|VT_R8)`\uff09",
          "prior": "\u672c\u4ed3 `tools/probe_spline_forms.py` \u4e0e `output/spline-forms.json` **\u5df2\u7ecf\u8bd5\u8fc7\u56db\u79cd**\uff0c"
                   "\u2605 \u7b54\u6848\u662f\u7b2c\u4e09\u79cd\uff08\u6bb5 0\u21921\uff09",
          "official": "CreateSpline \u7684 Remarks\uff1aPointData = **\u6241\u5e73\u7684 X,Y,Z \u5e8f\u5217**\uff08\u81f3\u5c11\u4e24\u4e2a\uff09\uff1b"
                      "2D \u8349\u56fe\u91cc Z \u88ab\u5ffd\u7565",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605\u2605 **\u524d\u4eba\u539f\u6837**\uff1a`CreateSpline2(data, False)`", "spline2"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a`CreateSpline(data)`\uff08\u4e0d\u5e26 2\uff09", "variant_r8"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u7b2c\u2460\u79cd\u6241\u5e73 list\uff08\u2605 \u6211\u4e0a\u4e00\u8f6e\u7528\u7684\uff09", "flat_list"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u7b2c\u2463\u79cd list of tuples", "tuples"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "spline_variant_works" if ev["cases"][0].get("ok") else "spline_variant_fails"
    p = R / "output" / "spline-with-variant-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-48s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("seg_before"), c.get("seg_after"),
            c.get("new_segments"), c.get("returned")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
