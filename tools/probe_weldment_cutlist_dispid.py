"""★ 回筛：结构系统的 `InsertWeldmentCutList{,2}` 到底能不能调（`dispid` 路径）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_weldment_cutlist_dispid.py
# 定位:   ★ 2026-10-03（轮 496）★ 用**事实 387 的手法回筛事实 382 的结论**。
#
#   ★★ **为什么要回筛**：
#     · 事实 382 记着「`IFeatureManager.InsertWeldmentCutList2` 在当前后端
#       （**pywin32 迟到绑定**）上**取不到**（权威类型库里有该成员，但 CO…）」
#       —— ★ 而那正是**事实 386/387 那一族的形态** ⚠
#     · 事实 387 定了手法：**见到取不到，不要就定性为「到不了」** ——
# 先走 `_oleobj_.GetIDsOfNames(名)` + `Invoke(dispid, 0, DISPATCH_METHOD, True, 参)` 试
# 一次 ✓
#
#   ★★ **本轮先测到的两件事**（★ 已足以改变说法）：
# · `GetIDsOfNames("InsertWeldmentCutList2")` ⇒ **dispid = 174**（★ **不是 1** ⇒ 路径是
# 对的）
#     · `GetIDsOfNames("InsertWeldmentCutList")`  ⇒ **dispid = 77**
#     · 而 `getattr(fm, "InsertWeldmentCutList2")` ⇒ **`NoneType`**（★ 连 3 元组都不是）
# ⇒ ★ **故「取不到」这个说法要精确化**：★ 名字**是已知的**、★ `getattr` 那条**回 None**
# 。
#
#   ★ 官方签名（`C:\swapi\types\IFeatureManager\`）：
#     `Feature InsertWeldmentCutList2( System.object Bodies )` —— **1 参**
#     `Feature InsertWeldmentCutList()`                      —— **0 参**
#
#   ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 官方依据: 上面两条签名；`kind: method`（两者皆是）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **能不能调通**（`Invoke` 不抛）★ 而**不**把"建出了切割清单"当判据
#   —— ★ 本探针没有焊件前置，建不出来是**应然的**；★ 本探针要回答的是**路径通不通**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import pythoncom                                                      # noqa: E402
from win32com.client import VARIANT                                   # noqa: E402

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u56de\u7b5b\uff1a\u7ed3\u6784\u7cfb\u7edf\u7684 InsertWeldmentCutList{,2} \u80fd\u4e0d\u80fd\u8c03\uff08dispid \u8def\u5f84\uff09",
          "steps": []}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: ★ \u5efa\u4e00\u4e2a\u5b9e\u4f53\uff08\u2605 \u4e0d\u662f\u710a\u4ef6 \u2014\
        #: u2014 \u672c\u63a2\u9488\u53ea\u95ee\u8def\u5f84\u901a\u4e0d\u901a\uff09
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         0.0, 0.0, 0.0, 0.04, 0.02, 0.0)
        P.end_sketch(doc)
        for cand in ("\u8349\u56fe1", "Sketch1"):
            try:
                P.extrude_boss(doc, cand, 0.02)
                break
            except Exception:                                             # noqa: BLE001
                continue
        fm = C.get_com_member(doc, "FeatureManager")
        ole = fm._oleobj_
        before = list(P.feature_names(doc) or [])

        #: \u2605 \u2460 0 \u53c2\u90a3\u6761\uff08dispid 77\uff09
        try:
            r = ole.Invoke(77, 0, pythoncom.DISPATCH_METHOD, True)
            after = list(P.feature_names(doc) or [])
            ev["steps"].append({"tag": "CutList()", "ok": True, "ret": str(r)[:70],
                                "new": [n for n in after if n not in before]})
        except Exception as exc:                                          # noqa: BLE001
            ev["steps"].append({"tag": "CutList()", "ok": False,
                                "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                                "code": getattr(exc, "args", (None,))[0]})

        #: \u2605 \u2461 1 \u53c2\u90a3\u6761\uff08dispid 174\uff09\u2014\u2014 \u4e09\u
        #: 79cd\u5305\u88c5
        bodies = list(C.get_com_member(doc, "GetBodies2", -1, True) or [])
        for tag, mk in (
            ("CutList2(\u7a7a\u6570\u7ec4)", lambda: VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [])),
            ("CutList2(\u4f53\u6570\u7ec4)", lambda: VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, bodies)),
            ("CutList2(None)", lambda: None),
        ):
            try:
                r = ole.Invoke(174, 0, pythoncom.DISPATCH_METHOD, True, mk())
                after = list(P.feature_names(doc) or [])
                ev["steps"].append({"tag": tag, "ok": True, "ret": str(r)[:70],
                                    "new": [n for n in after if n not in before]})
            except Exception as exc:                                      # noqa: BLE001
                ev["steps"].append({"tag": tag, "ok": False,
                                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                                    "code": getattr(exc, "args", (None,))[0]})
    except Exception as exc:                                              # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass

    p = R / "output" / "weldment-cutlist-dispid-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    n_ok = sum(1 for s in ev["steps"] if s.get("ok"))
    print("  \u8c03\u901a\u4e86 **%d / %d**" % (n_ok, len(ev["steps"])))
    for s in ev["steps"]:
        print("  %-20s ok=%-6s %s" % (s.get("tag"), s.get("ok"),
                                      (s.get("ret") or s.get("err") or "")[:100]))
    if ev.get("err"):
        print("  err=%s" % ev["err"][:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
