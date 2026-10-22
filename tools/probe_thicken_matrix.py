"""★ 真机：`FeatureBossThicken` 的**参数矩阵**（★ 上一轮单组参数回了 `None`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools\probe_thicken_matrix.py
# 定位:   ★ 2026-10-03（轮 503）★ 上一轮（轮 502）建好 `thicken_surface_report` 后：
#     · 前置**完美**（`tree=7 · solid=0 · **surface=1**`）；
#     · 而单组参数（`direction=0 · fill_volume=True · merge=True ·
#       use_feat_scope=False · use_auto_select=True`）⇒ ★ **返回 `None`**、树不动 ⚠
#   ⇒ ★ 本探针按**官方参数表**逐个变到，看哪一组能成。
#
#   ★★ **官方三源给的线索**（★ `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`）：
#     `Feature FeatureBossThicken(double Thickness, int Direction, int FaceIndex,
#      bool FillVolume, bool Merge, bool UseFeatScope, bool UseAutoSelect)`
#     · `FaceIndex` ⇒ ★ 「**Not used**」
#     · `FillVolume` ⇒ "True if you want to make a **solid** from the knitted surface"
#     · `UseFeatScope` ⇒ "True if the feature **only affects selected bodies**"
#     · `UseAutoSelect` ⇒ "True to **automatically select all bodies** and have the feature
#       affect those bodies"
#     ⇒ ★★ **关键推论**：`UseFeatScope=False` 时"影响所有体" ⇒ ★ 而 `UseAutoSelect=True`
#       却是"自动选所有体" ⇒ ★ 两者**语义有重叠** ⚠
#     ★ 故本矩阵里 **`use_feat_scope=True` + 先选中曲面体** 是重点组合 ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`。★ 每组**新开一个文档**（★ 免互相污染）。
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
from scripts import sw_surface_features as SF  # noqa: E402


def _build_surface(sw):
    """★ 建一个**只有一张曲面**的零件（★ 与轮 502 同款前置）。"""
    doc = C.new_document(sw, "part")
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.02,
        -0.02,
        0.0,
        0.02,
        0.02,
        0.0,
    )
    P.end_sketch(doc)
    for cand in ("\u8349\u56fe1", "Sketch1"):
        try:
            r = SF.create_extruded_surface_report(doc, 20.0, sketch_name=cand)
            if r.get("ok"):
                break
        except Exception:  # noqa: BLE001
            continue
    return doc


def _select_surface_bodies(doc, mark=0):
    """★ **按对象选中曲面体**（★ 给 `UseFeatScope=True` 那种组合用）。"""
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    n = 0
    for b in list(C.get_com_member(doc, "GetBodies2", 1, True) or []):
        if P._select_com_object(b, append=True, mark=mark):
            n += 1
    return n


def _one(
    sw,
    tag,
    *,
    direction=0,
    fill_volume=True,
    merge=True,
    use_feat_scope=False,
    use_auto_select=True,
    select_bodies=False,
):
    row = {
        "tag": tag,
        "direction": direction,
        "fill_volume": fill_volume,
        "use_feat_scope": use_feat_scope,
        "use_auto_select": use_auto_select,
        "select_bodies": select_bodies,
    }
    doc = None
    try:
        doc = _build_surface(sw)
        row["pre"] = {
            "solid": SF._solid_body_count(doc),
            "surface": SF._surface_body_count(doc),
        }
        row["sel"] = _select_surface_bodies(doc) if select_bodies else 0
        before = list(P.feature_names(doc) or [])
        fm = C.get_com_member(doc, "FeatureManager")
        try:
            feat = C.get_com_member(
                fm,
                "FeatureBossThicken",
                3.0 * 0.001,
                int(direction),
                0,
                bool(fill_volume),
                bool(merge),
                bool(use_feat_scope),
                bool(use_auto_select),
            )
            row["returned"] = type(feat).__name__ if feat is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
            row["code"] = getattr(exc, "args", (None,))[0]
        after = list(P.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["post"] = {
            "solid": SF._solid_body_count(doc),
            "surface": SF._surface_body_count(doc),
        }
        row["ok"] = bool(row["new"])
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
        "_": "FeatureBossThicken \u53c2\u6570\u77e9\u9635\uff08\u2605 \u4e0a\u4e00\u8f6e\u5355\u7ec4\u56de None\uff09",
        "cases": [],
    }
    cases = [
        ("\u57fa\u51c6\uff08\u8f6e 502 \u90a3\u7ec4\uff09", {}),
        ("scope=True + \u9009\u4f53", {"use_feat_scope": True, "select_bodies": True}),
        ("auto=False", {"use_auto_select": False}),
        (
            "scope=True + auto=False + \u9009\u4f53",
            {"use_feat_scope": True, "use_auto_select": False, "select_bodies": True},
        ),
        ("fill=False", {"fill_volume": False}),
        ("direction=1", {"direction": 1}),
        ("scope=True + auto=False", {"use_feat_scope": True, "use_auto_select": False}),
    ]
    for tag, kw in cases:
        ev["cases"].append(_one(sw, tag, **kw))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "thicken-matrix-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-28s ok=%-6s returned=%-9s new=%s %s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("returned"),
                c.get("new"),
                (c.get("err") or "")[:70],
            )
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
