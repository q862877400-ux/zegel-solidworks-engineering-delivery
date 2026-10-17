"""★ 真机：**自由样式**（`InsertFreeform2`）—— ★ 按官方 Remarks 的五步链走一遍。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_freeform.py
# 定位:   ★ 2026-10-03（轮 606）★ 攻台账里**唯一一条已知有活路的**可攻关项。
#
#   ★★★ **为什么它有活路**（★ 事实 477）：★ 整条链**四个成员全在、且全未标废弃**
#     —— ★ 而★ 那与四个阵列（全带 `AccessSelections`）**形成鲜明对比** ✓
#
#   ★★ **官方依据**：`C:\swapi\types\IFeatureManager\InsertFreeform2.md` 的 **`## Remarks`**
#     （★ **签名与参数都给不出那条链，★ 只有 Remarks 给得出**）——
#     ★ 逐字给出**五步**：
#     ```
#     1. **Select the face to form.**        \u2605 \u800c\u4e14\u524d\u7f6e\u91cc\u5199\u7740
#                                            "**The face must have four sides**"
#     2. Add curves on the selected face.    \u21d2 `SetFreeformCurveData`\uff08 **8 \u53c2**\uff09
#     3. Add points on the curves.           \u21d2 `SetFreeformPointData`\uff08 **6 \u53c2**\uff09
#     4. Specify boundary continuity.        \u21d2 `SetFreeformBoundaryContinuity`\uff08**2 \u53c2**\uff09
#     5. Insert the Freeform feature.        \u21d2 `InsertFreeform2(Nsided, Symmetric0, Symmetric1, Angle)`
#     ```
#   ★ 参数语义（★ 从同一页的 `## Parameters` 抄，★ 不猜）：
#     · `Direction` = **0 或 1** · `CurveParameter` = 面上**何处**加曲线 · `ParameterOnCurve` = 曲线上何处加点
#     · `XOffset`/`YOffset` **典型为 0**（★ "point was not modified"）
#     · `BoundaryIndex` = **0 基** · `Continuity` = **−1 Movable / 0 Contact / …**
#     · `Nsided` = True 用新算法（★ **三边或超过四边的面必须 True**）· `Angle` 单位**弧度**
#   ⚠ 全程走 `tools/sw_guard.py`；★ 判据 = **特征树增量 + 特征名**（★ 规则 6）。
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
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402

SW_SEL_FACES = 2


def _box(doc, size=0.03):
    """★ 造一个立方体（★ **每个面都是四边** —— ★ 满足前置 "The face must have four sides"）。"""
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -size, -size, 0.0, size, size, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, size * 2.0)
            return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _side(doc):
    """★ 第 1 步：★ **选中要造型的那个面**（★ 用射线打法选到 +Z 面，★ 它四边）。

    ★★★ 2026-10-03（轮 607）**修了一个真因**（★ 事实 479）：
      ★ 上一版**没清选区**就发射线 ⇒ 选区里留下**一个残留对象**
        （★ 真机：`counts=**2,1,1,1**` —— ★ 不清就选得 **2**（`type=22` + `FACE`），
        ★ 而**先清再选得 1**）⚠
      ★ 而官方第 1 步写的是“Select the **face**”（★ **单数**）
        ⇒ ★ 故**清一次**是前置。
    """
    try:
        doc.ClearSelection2(True)          #: ★ 前置：选区里只能有那一个面
    except Exception:                                                 # noqa: BLE001
        pass
    ext = C.get_com_member(doc, "Extension")
    ok = C.get_com_member(ext, "SelectByRay", 0.0, 0.0, 0.2,
                          0.0, 0.0, -1.0, 1e-4, SW_SEL_FACES, False, 0, 0)
    n = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                             "GetSelectedObjectCount2", -1) or 0)
    return bool(ok), n


def _one(sw, tag, *, n_curves=1, n_points=1):
    row = {"tag": tag, "ok": False, "steps": {}}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["box"] = _box(doc)
        ok_ray, sel_n = _side(doc)
        row["steps"]["1_select_face"] = {"ray": ok_ray, "selected": sel_n}
        fm = C.get_com_member(doc, "FeatureManager")
        #: \u2605 \u7b2c 2 \u6b65\uff1a\u52a0**\u66f2\u7ebf**\uff08\u2605 8 \u53c2\uff09
        for i in range(n_curves):
            C.get_com_member(fm, "SetFreeformCurveData",
                             0, 0.25 + 0.25 * i,
                             0.0, 1.0, 0.0,      #: \u2605 \u4e00\u7aef\u5207\u5411
                             0.0, 1.0, 0.0)      #: \u2605 \u53e6\u4e00\u7aef\u5207\u5411
        row["steps"]["2_curves"] = n_curves
        #: \u2605 \u7b2c 3 \u6b65\uff1a\u5728\u66f2\u7ebf\u4e0a\u52a0**\u70b9**\uff08\u2605 6 \u53c2\uff0c\u2605 \u504f\u79fb\u5178\u578b\u4e3a 0\uff09
        for j in range(n_points):
            C.get_com_member(fm, "SetFreeformPointData",
                             0, 0.25, 0.5 + 0.3 * j, 0.0, 0.0, 0.0)
        row["steps"]["3_points"] = n_points
        #: \u2605 \u7b2c 4 \u6b65\uff1a\u8fb9\u754c\u8fde\u7eed\u6027\uff08\u2605 2 \u53c2\uff1b\u2605 `-1 = Movable`\uff09
        C.get_com_member(fm, "SetFreeformBoundaryContinuity", 0, -1)
        row["steps"]["4_continuity"] = "-1 (Movable)"
        before = list(FR.feature_names(doc) or [])
        row["before"] = len(before)
        #: \u2605 \u7b2c 5 \u6b65\uff1a\u63d2\u5165\uff08\u2605 4 \u53c2\uff1b\u2605 `Nsided=True` \u7528\u65b0\u7b97\u6cd5\uff09
        feat = C.get_com_member(fm, "InsertFreeform2", True, False, False, 0.0)
        row["returned"] = type(feat).__name__ if feat is not None else "None"
        after = list(FR.feature_names(doc) or [])
        row["new_features"] = [n for n in after if n not in before]
        row["ok"] = feat is not None and bool(row["new_features"])
        if not row["ok"] and feat is None:
            row["err"] = "InsertFreeform2 \u56de None\uff08\u2605 \u800c\u524d\u56db\u6b65\u90fd\u6ca1\u62a5\u9519\uff09"
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
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
          "_": "\u81ea\u7531\u6837\u5f0f\uff08`InsertFreeform2`\uff09\u2014\u2014 \u2605 \u6309\u5b98\u65b9 `## Remarks` \u7684**\u4e94\u6b65\u94fe**\u8d70",
          "official": "`C:\\swapi\\types\\IFeatureManager\\InsertFreeform2.md` \u7684 `## Remarks`"
                      "\uff08\u2605 \u4e94\u6b65\uff1a\u9009\u9762 \u2192 \u52a0\u66f2\u7ebf \u2192 \u52a0\u70b9 \u2192 \u8fb9\u754c\u8fde\u7eed\u6027 \u2192 \u63d2\u5165\uff09",
          "arity": {"InsertFreeform2": 4, "SetFreeformCurveData": 8,
                    "SetFreeformPointData": 6, "SetFreeformBoundaryContinuity": 2},
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u4e94\u6b65\u9f50\u5168\uff08\u2605 1 \u66f2\u7ebf + 1 \u70b9\uff09"))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a**\u4e0d\u9009\u9762**\u5c31\u63d2\u5165", n_curves=0, n_points=0))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "freeform_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "freeform-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print("  %-40s ok=%-6s \u7279\u5f81 %s -> %s" % (
            c.get("tag"), c.get("ok"), c.get("before"),
            (c.get("before") or 0) + len(c.get("new_features") or [])))
        print("        \u6b65\u9aa4=%s" % (c.get("steps"),))
        print("        \u56de=%s \u65b0\u589e=%s" % (c.get("returned"), c.get("new_features")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
