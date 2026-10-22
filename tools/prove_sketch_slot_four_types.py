"""★ 真机：**槽口**四种 —— 一条方法 `CreateSketchSlot` + 一个枚举覆盖（官方 + 反射给全了）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_sketch_slot_four_types.py
# 定位:   ★ 2026-10-03（轮 553）★ 照新纪律（**官方文档是第 0 步**）攻台账的**槽口**那
#           几条。
#
#   ★★★★ **官方 `CreateSketchSlot.md` 的签名（14 参）**逐字：
#     ```
#     SketchSlot CreateSketchSlot(int SlotCreationType, int SlotLengthType, double Width,
#                                 double X1, double Y1, double Z1,
#                                 double X2, double Y2, double Z2,
#                                 double X3, double Y3, double Z3,
#                                 int CenterArcDirection, bool AddDimension)
#     ```
#     ★ 而 `CenterArcDirection` 官方给了取值：**-1 = Clockwise · 1 = Counterclockwise** ✓
#
#   ★★★ **两个枚举的值来自**反射**（★ 铁律 4：数值去反射；★ 而 swapi 的 enums 页只给成员名列表）**：
#     ```
#     swSketchSlotCreationType_e :  0 = line · 1 = center_line · 2 = arc · 3 = 3pointarc
#     swSketchSlotLengthType_e   :  0 = CenterCenter · 1 = FullLength
#     ```
#     ⇒ ★★ **故台账那几条**（直槽口 / 中心点直槽口 / 中心点圆弧槽口 / 三点圆弧槽口）
#       ★ **正好对上 0 / 1 / 2 / 3** ⇒ ★ **一次实现 = 4 条能力** ✓
#
#   ★ 本探针**四个值各试一次**（★ 判据：★ 草图里的**段数增加** —— ★ 返回值 `SketchSlot` 只是线索）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：**草图段数比调用前多**（★ 规则 6；★ 槽口是草图图元，没有特征树增量）。

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

#: \u2605 \u53cd\u5c04\u91cc\u7684\u503c\uff08\u2605 \u88c1\u51b3\u8005\uff09
SLOT_TYPE = {
    "line": 0,
    "center_line": 1,
    "arc": 2,
    "3pointarc": 3,
}


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        if sk is None:
            return -1
        return len(list(C.get_com_member(sk, "GetSketchSegments") or []))
    except Exception:                                                     # noqa: BLE001
        return -1


def _one(sw, name, creation_type):
    row = {"tag": "\u69fd\u53e3\u00b7%s\uff08type=%d\uff09" % (name, creation_type),
           "creation_type": creation_type, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        before = _seg_count(doc)
        row["seg_before"] = before
        ret = None
        try:
            sm = C.get_com_member(doc, "SketchManager")
            #: \u2605 \u53c2\u6570\uff1aSlotCreationType \u00b7 SlotLengthType(=0 CenterCenter) \u00b7 Width \u00b7
            #:   P1 \u00b7 P2 \u00b7 P3 \u00b7 CenterArcDirection(=1 CCW) \u00b7 AddDimension(=True)
            ret = C.get_com_member(sm, "CreateSketchSlot", int(creation_type), 0, 0.004,
                                   -0.02, 0.0, 0.0,
                                   0.02, 0.0, 0.0,
                                   0.0, 0.012, 0.0,
                                   1, True)
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
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
          "_": "\u69fd\u53e3\u56db\u79cd\uff1a`ISketchManager.CreateSketchSlot` + `swSketchSlotCreationType_e`",
          "official": "CreateSketchSlot \u7b7e\u540d 14 \u53c2\uff1b\u679a\u4e3e\u503c\u53d6\u81ea**\u53cd\u5c04**"
                      "\uff08line=0 / center_line=1 / arc=2 / 3pointarc=3\uff09",
          "cases": []}
    for name, v in SLOT_TYPE.items():
        ev["cases"].append(_one(sw, name, v))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = ("slot_all_four_work" if ev["passed"] == ev["total"]
                     else ("slot_partial_%d" % ev["passed"]))
    p = R / "output" / "sketch-slot-four-types-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-30s ok=%-6s \u6bb5 %s \u2192 %s\uff08\u589e %s\uff09\u56de=%s" % (
            c.get("tag"), c.get("ok"), c.get("seg_before"), c.get("seg_after"),
            c.get("new_segments"), c.get("returned")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
