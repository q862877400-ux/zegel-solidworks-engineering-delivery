"""★ 真机：自由样式 —— ★ **参数矩阵**（★ 官方材料已穷尽后的"最后手段"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_freeform_matrix.py
# 定位:   ★ 2026-10-03（轮 609）★ 承**事实 480**（官方材料已穷尽 ⇒ 只剩逐参数试）。
#
#   ★★ **矩阵的设计依据**（★ 每一条都从官方 md 的原文推出来，★ 不凭空铺）：
#     · `InsertFreeform2(Nsided, Symmetric0, Symmetric1, Angle)`：
# ★ `Nsided` 官方逐字「**True to use the new Freeform algorithm, false to use the old on
# e**」
#         ⇒ ★ **故它有两个值可试**（★ 而"新算法"未必在本机可用）⚠
#     · `SetFreeformBoundaryContinuity(BoundaryIndex, Continuity)`：
#       ★ 官方给了取值表：`-1 = Movaeable`（★ 原文拼写）· `0 = Contact` · ★ 而上轮只试了 `-1`
#         ⇒ ★ **故把取值表全试一遍** ✓
#     · `SetFreeformCurveData` 的 `Direction`：★ 官方「valid values are either **0 or 1**」
#       ⇒ ★ **故 0 与 1 各试一次** ✓
#   ★ 判据 = **特征树增量**（★ 规则 6）。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每格新开文档。
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

import scripts.sw_feature_readback as fr  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


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


def _one(sw, tag, *, nsided, continuity, direction, n_curves=1, n_points=1, angle=0.0):
    row = {
        "tag": tag,
        "nsided": nsided,
        "continuity": continuity,
        "direction": direction,
        "n_curves": n_curves,
        "ok": False,
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        row["box"] = _box(doc)
        doc.ClearSelection2(True)  #: ★ 事实 479：发射线前先清选区
        ext = C.get_com_member(doc, "Extension")
        C.get_com_member(
            ext, "SelectByRay", 0.0, 0.0, 0.2, 0.0, 0.0, -1.0, 1e-4, 2, False, 0, 0
        )
        mgr = C.get_com_member(doc, "SelectionManager")
        row["selected"] = int(C.get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        fm = C.get_com_member(doc, "FeatureManager")
        for i in range(n_curves):
            C.get_com_member(
                fm,
                "SetFreeformCurveData",
                int(direction),
                0.3 + 0.3 * i,
                0.0,
                1.0,
                0.0,
                0.0,
                1.0,
                0.0,
            )
        for j in range(n_points):
            C.get_com_member(
                fm,
                "SetFreeformPointData",
                int(direction),
                0.3,
                0.4 + 0.3 * j,
                0.0,
                0.0,
                0.0,
            )
        C.get_com_member(fm, "SetFreeformBoundaryContinuity", 0, int(continuity))
        before = list(fr.feature_names(doc) or [])
        row["before"] = len(before)
        try:
            feat = C.get_com_member(
                fm, "InsertFreeform2", bool(nsided), False, False, float(angle)
            )
            row["returned"] = type(feat).__name__ if feat is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["insert_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
            row["returned"] = "ERR"
        after = list(fr.feature_names(doc) or [])
        row["new_features"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new_features"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
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
        "_": "\u81ea\u7531\u6837\u5f0f\u53c2\u6570\u77e9\u9635\uff08\u2605 \u5b98\u65b9\u6750\u6599\u5df2\u7a77\u5c3d\u540e\u7684\u201c\u6700\u540e\u624b\u6bb5\u201d\uff09",
        "basis": "\u2605 \u6bcf\u4e00\u683c\u90fd\u4ece\u5b98\u65b9 md \u539f\u6587\u63a8\u51fa\uff1a"
        "`Nsided` \u6709\u4e24\u4e2a\u503c\uff08\u65b0/\u65e7\u7b97\u6cd5\uff09\u00b7 "
        "`Direction` \u53d6 0 \u6216 1 \u00b7 `Continuity` \u53d6\u503c\u8868 -1/0/1/2",
        "cases": [],
    }
    #: \u2605 \u77e9\u9635\uff1a`Nsided` \u00d7 `Continuity`\uff08\u2605 \u800c `Directi
    #: on` \u53d6 0\uff09
    for nsided in (True, False):
        for cont in (-1, 0, 1, 2):
            ev["cases"].append(
                _one(
                    sw,
                    "\u2605 Nsided=%-5s \u00b7 Continuity=%s" % (nsided, cont),
                    nsided=nsided,
                    continuity=cont,
                    direction=0,
                )
            )
    #: \u2605 \u800c `Direction=1` \u4e0e\u201c\u591a\u6761\u66f2\u7ebf\u201d\u5404\u4e0
    #: 0\u683c
    ev["cases"].append(
        _one(
            sw,
            "\u2605 Nsided=True \u00b7 Continuity=-1 \u00b7 **Direction=1**",
            nsided=True,
            continuity=-1,
            direction=1,
        )
    )
    ev["cases"].append(
        _one(
            sw,
            "\u2605 Nsided=True \u00b7 Continuity=-1 \u00b7 **2 \u66f2\u7ebf 2 \u70b9**",
            nsided=True,
            continuity=-1,
            direction=0,
            n_curves=2,
            n_points=2,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "freeform_matrix_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "freeform-matrix-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-48s ok=%-6s sel=%s \u7279\u5f81 %s -> %s \u56de=%s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("selected"),
                c.get("before"),
                (c.get("before") or 0) + len(c.get("new_features") or []),
                c.get("returned"),
            )
        )
        if c.get("new_features"):
            print("        \u65b0\u589e=%s" % (c["new_features"],))
        for k in ("insert_err", "err"):
            if c.get(k):
                print("        %s=%s" % (k, str(c[k])[:120]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
