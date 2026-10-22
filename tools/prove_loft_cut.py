"""★ 真机：**放样切除** `InsertCutBlend`（★ 12 参 · 未废弃）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_loft_cut.py
# 定位:   ★ 2026-10-03（轮 561）★ 照新纪律（**官方文档是第 0 步**）攻台账「放样切除 /
#           边界切除」。
#
#   ★★★★ **官方签名逐字**（`C:\swapi\types\IFeatureManager\InsertCutBlend.md`）：
#     ```
#     Feature InsertCutBlend(bool Closed, bool KeepTangency, bool ForceNonRational,
#                            double TessToleranceFactor, short StartMatchingType,
#                            short EndMatchingType, bool IsThinBody, double Thickness1,
#                            double Thickness2, short ThinType,
#                            bool UseFeatScope, bool UseAutoSelect)   \u2190 **12 \u53c2**
#     ```
#     ★ 而 md **头**上**未标 `Obsolete`**（★ 对照事实 433 的地图：另外四条都标了）✓
#     ★ 它的 `## Remarks` 与 `InsertProtrusionBlend2` **逐字同一套**：
#       剖面**按顺序**选 · **强烈建议带引导线** · **mark：1 剖面 · 2 引导线 · 4 中心线**。
#
#   ★★ **故本探针的前置照 `create_loft_report` 那一套**（★ 已知能成）：
#     ★ 两个**平行剖面** ⇒ 按顺序选中（mark=1）⇒ `InsertCutBlend`。
#   ★ 判据（★ 与放样同一套）：**树增量** **且** **类型名 = `Blend`**。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 两组：能切（有实体可切）/ 对照。
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
from scripts import sw_loft as l  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _mk_solid_and_profiles(doc):
    """★ 一个**实体**（★ 要有料可切）+ ★ **两个平行剖面**。"""
    #: \u2605 \u5b9e\u4f53
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.05,
        -0.05,
        0.0,
        0.05,
        0.05,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    solid = False
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.03)
            solid = True
            break
        except Exception:  # noqa: BLE001
            continue
    #: \u2605 \u4e24\u4e2a\u5256\u9762\uff08\u2605 \u524d\u89c6\u9762\u4e0a\u7684\u4e24\
    #: u4e2a\u4e0d\u540c\u5927\u5c0f\u7684\u5706\uff09
    made = []
    for i, rad in enumerate((0.015, 0.008)):
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        if i == 0:
            P.start_sketch(doc, plane_name="Front Plane")
        else:
            from sw_connect import get_com_member as _get

            P._select_by_id(
                _get(doc, "Extension"),
                "\u524d\u89c6\u57fa\u51c6\u9762",
                "PLANE",
                append=False,
                mark=0,
            )
            _get(_get(doc, "FeatureManager"), "InsertRefPlane", 8, 0.04, 0, 0, 0, 0)
            try:
                P.start_sketch(doc, plane_name="\u57fa\u51c6\u97621")
            except Exception:  # noqa: BLE001
                P.start_sketch(doc, plane_name="Plane1")
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCircleByRadius",
            0.0,
            0.0,
            0.0,
            rad,
        )
        P.end_sketch(doc)
        nm = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        if nm:
            made.append(nm[-1])
    return solid, made


def _pick(doc, sketches):
    ext = C.get_com_member(doc, "Extension")
    picked = []
    for sk in sketches:
        for cand in P._get_sketch_name_candidates(sk):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=1):
                    picked.append(cand)
                    break
            except Exception:  # noqa: BLE001
                continue
    return picked


def _vol(doc):
    try:
        mp = C.get_com_member(C.get_com_member(doc, "Extension"), "CreateMassProperty")
        v = C.get_com_member(mp, "Volume")
        return float(v) if v is not None else None
    except Exception:  # noqa: BLE001
        return None


def _one(sw, tag, cut):
    row = {"tag": tag, "cut": cut, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        solid, sketches = _mk_solid_and_profiles(doc)
        row["solid"] = solid
        row["sketches"] = sketches
        before = list(fr.feature_names(doc) or [])
        row["vol_before"] = _vol(doc)
        picked = _pick(doc, sketches)
        row["picked"] = picked
        try:
            if cut:
                r = l.create_loft_cut_report(
                    doc, closed=False, use_selected_profiles=True
                )
            else:
                r = l.create_loft_report(doc, closed=False, use_selected_profiles=True)
            row.update(
                {
                    "report_ok": r.get("ok"),
                    "feature_name": r.get("feature_name"),
                    "type_name": r.get("type_name"),
                    "args_count": r.get("args_count"),
                    "mark1": r.get("mark1_selected"),
                    "err": r.get("error"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["vol_after"] = _vol(doc)
        if row["vol_before"] and row["vol_after"]:
            row["vol_ratio"] = round(row["vol_after"] / row["vol_before"], 4)
        #: \u2605 \u5224\u636e\uff1a**\u6811\u589e\u91cf + \u7c7b\u578b\u540d**\uff08\u2
        #: 605 \u5207\u4e0e\u4e0d\u5207**\u7c7b\u578b\u540d\u4e0d\u540c**\uff09
        #: \u2605\u2605 `Blend` = \u653e\u6837**\u51f8\u53f0** \u00b7 `BlendCut` = \u653
        #: e\u6837**\u5207\u9664**\uff08\u2605 \u771f\u673a\u5b9a\u7684\uff09
        named = row.get("type_name") in ("Blend", "BlendCut")
        row["ok"] = bool(row["new"] and named)
        #: \u2605 \u800c\u5207\u9664\u8fd8\u8981**\u4f53\u79ef\u4e0d\u53d8\u5927**
        if cut and row["ok"] and row.get("vol_ratio"):
            row["ok"] = row["vol_ratio"] <= 1.0001
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
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
        "_": "\u653e\u6837\u5207\u9664\uff1a`InsertCutBlend`\uff08\u2605 12 \u53c2 \u00b7 \u672a\u5e9f\u5f03\uff09",
        "official": "InsertCutBlend \u2014\u2014 12 \u53c2\uff1bRemarks \u4e0e InsertProtrusionBlend2 \u9010\u5b57\u540c\u4e00\u5957"
        "\uff08\u5256\u9762\u6309\u987a\u5e8f \u00b7 mark 1/2/4\uff09",
        "cases": [],
    }
    ev["cases"].append(
        _one(sw, "\u2605 \u653e\u6837**\u5207\u9664**\uff08InsertCutBlend\uff09", True)
    )
    ev["cases"].append(
        _one(
            sw,
            "\u5bf9\u7167\uff1a\u653e\u6837**\u51f8\u53f0**\uff08InsertProtrusionBlend2\uff09",
            False,
        )
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "loft_cut_works" if ev["cases"][0].get("ok") else "loft_cut_fails"
    p = R / "output" / "loft-cut-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        print("  %-44s ok=%-6s solid=%s" % (c.get("tag"), c.get("ok"), c.get("solid")))
        print(
            "        \u5256\u9762=%s \u9009\u4e2d=%s mark1=%s"
            % (c.get("sketches"), c.get("picked"), c.get("mark1"))
        )
        print(
            "        \u7279\u5f81=%s \u578b=%s \u53c2\u6570=%s \u65b0\u589e=%s"
            % (
                c.get("feature_name"),
                c.get("type_name"),
                c.get("args_count"),
                c.get("new"),
            )
        )
        print(
            "        \u4f53\u79ef %s\u2192%s\uff08\u6bd4=%s\uff09"
            % (c.get("vol_before"), c.get("vol_after"), c.get("vol_ratio"))
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:150])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
