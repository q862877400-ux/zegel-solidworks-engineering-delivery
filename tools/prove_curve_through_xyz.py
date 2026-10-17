"""★ 真机：**通过 XYZ 点的曲线** —— `IModelDoc2.InsertCurveFileBegin/Point/End`（三步式）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_curve_through_xyz.py
# 定位:   ★ 2026-10-03（轮 582）★ 照新纪律（**官方文档是第 0 步**）攻台账「曲线-通过XYZ点的曲线」。
#
#   ★★ **官方四页（`C:\swapi\types\IModelDoc2\`，★ 四者全**未标废弃****）**：
#     ```
#     void InsertCurveFileBegin()
#        Remarks \u9010\u5b57\uff1a"This method: - **is the first method called that create a curve**. "
#        "This method **must precede** all calls to `InsertCurveFilePoint`; "
#        "\u2605 **and `InsertCurveFileEnd` must enclose all of the calls to `InsertCurveFilePoint`**."
#     bool InsertCurveFilePoint(double X, double Y, double Z)
#        Remarks\uff1a"sets a point for a curve\uff1b\u2605 **called multiple times** after Begin and before End"
#     bool InsertCurveFileEnd()
#        Remarks\uff1a"**is the last method called to create a curve**"
#     bool InsertCurveFile(string FileName)
#        Remarks\uff1a"The curve goes through the points in the specified **file**."
#     ```
#
#   ★★★ **故判据不能看返回值**：★ `Begin` 官方回 **void** ⇒
#     按**事实 436**（0 参 + 回 void 的成员，判据取**几何量/特征树的增量**）⇒
#     ★ 本探针判 **`feature_names()` 的增量**（★ 应出现一个「曲线」特征）✓
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两格：**三步式（内联点）** / **从文件**。
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

from scripts import sw_connect as C                                   # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402

#: \u2605 \u8981\u7a7f\u8fc7\u7684\u70b9\uff08\u2605 **\u6beb\u7c73**\uff0c\u2605 \u672c\u4ed3\u7ea6\u5b9a\uff1a\u8fb9\u754c\u6362\u7b97\u4e00\u6b21\uff09
PTS_MM = [(0.0, 0.0, 0.0), (20.0, 10.0, 0.0), (40.0, 0.0, 10.0), (60.0, 10.0, 10.0)]


def _one(sw, tag, mode):
    row = {"tag": tag, "mode": mode, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        before = list(FR.feature_names(doc) or [])
        row["before"] = len(before)
        if mode == "steps":
            #: \u2605 **\u4e09\u6b65\u5f0f**\uff1aBegin \u2192 Point\u00d7N \u2192 End\uff08\u2605 \u800c\u5b98\u65b9\u8bf4 Begin/End \u5fc5\u987b**\u5939\u4f4f**\u6240\u6709 Point\uff09
            steps = {}
            try:
                C.get_com_member(doc, "InsertCurveFileBegin")
                steps["Begin"] = "ok"
            except Exception as exc:                                      # noqa: BLE001
                steps["Begin"] = "%s: %s" % (type(exc).__name__, str(exc)[:60])
            pts = []
            for (x, y, z) in PTS_MM:
                try:
                    ok = C.get_com_member(doc, "InsertCurveFilePoint",
                                          x / 1000.0, y / 1000.0, z / 1000.0)
                    pts.append(bool(ok))
                except Exception as exc:                                  # noqa: BLE001
                    pts.append("%s: %s" % (type(exc).__name__, str(exc)[:50]))
            steps["Point"] = pts
            try:
                steps["End"] = bool(C.get_com_member(doc, "InsertCurveFileEnd"))
            except Exception as exc:                                      # noqa: BLE001
                steps["End"] = "%s: %s" % (type(exc).__name__, str(exc)[:60])
            row["steps"] = steps
        else:
            #: \u2605 **\u4ece\u6587\u4ef6**\uff08\u2605 \u5b98\u65b9\uff1a"The curve goes through the points in the specified file"\uff09
            f = R / "output" / "_xyz_points.txt"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("\n".join("%.6f %.6f %.6f" % (x / 1000.0, y / 1000.0, z / 1000.0)
                                   for (x, y, z) in PTS_MM) + "\n", encoding="utf-8")
            row["file"] = str(f)
            try:
                row["returned"] = str(C.get_com_member(doc, "InsertCurveFile", str(f)))
            except Exception as exc:                                      # noqa: BLE001
                row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"])
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
          "_": "\u901a\u8fc7 XYZ \u70b9\u7684\u66f2\u7ebf\uff1a`InsertCurveFileBegin/Point/End`\uff08\u4e09\u6b65\u5f0f\uff09\u00b7 `InsertCurveFile`",
          "official": "Begin/Point/End \u56db\u9875\u5747**\u672a\u6807\u5e9f\u5f03**\uff1b"
                      "\u2605 Begin \u56de **void** \u21d2 \u6309\u4e8b\u5b9e 436\uff0c\u5224\u636e\u53d6**\u7279\u5f81\u6811\u589e\u91cf**",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 **\u4e09\u6b65\u5f0f**\uff08Begin \u2192 Point\u00d74 \u2192 End\uff09", "steps"))
    ev["cases"].append(_one(sw, "\u2605 **\u4ece\u6587\u4ef6**\uff08`InsertCurveFile`\uff09", "file"))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "xyz_curve_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "curve-through-xyz-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-44s ok=%-6s \u7279\u5f81 %s \u2192 %s" % (
            c.get("tag"), c.get("ok"), c.get("before"), (c.get("before") or 0) + len(c.get("new") or [])))
        print("        \u65b0\u589e=%s" % (c.get("new"),))
        if c.get("steps"):
            for k, v in c["steps"].items():
                print("        step %-8s %s" % (k, str(v)[:96]))
        if c.get("returned"):
            print("        \u56de=%s" % c.get("returned"))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
