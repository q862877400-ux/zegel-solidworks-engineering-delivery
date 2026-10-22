"""★ 真机：加厚曲面（`IFeatureManager.FeatureBossThicken`）—— B6/T610。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_thicken_surface.py
# 定位:   ★ 2026-10-03（轮 502）★ 给 `sw_surface_features.thicken_surface_report` 留真
#           机证据。
#   ★ 对应 `specs/201-toolbar-gaps` 的 **T610**（★ 而 T605-T610 这六条一直空着）。
#
# 官方三源（★ 铁律 4）：
#   · `C:\swapi\types\IFeatureManager\FeatureBossThicken.md`：
#     `Feature FeatureBossThicken(double Thickness, int Direction, int FaceIndex, bool FillVolume,
#      bool Merge, bool UseFeatScope, bool UseAutoSelect)`
#     ★★ 参数表逐字：**`FaceIndex` ⇒「Not used」** ✓（★ 故本包装不收面索引）
#   · `C:\swapi\types\IModelDoc2\FeatureBossThicken.md` ⇒ **Obsolete**（★ 继任者是 `IFeatureManager` 那个）
#
# ★ 前置（★ 与 `knit_surfaces_report` 同款）：★ **文件里要有一个曲面体**
#   ⇒ 本探针先用本仓**已验过**的 `create_extruded_surface_report` 建一张曲面 ✓
#
# ⚠ 全程走 `tools/sw_guard.py`（★ 超时 + 弹窗处置 + `sw_alive` 复查）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：★ **特征树多了新特征**；★ 并记账**实体数 / 曲面体数**的变化
#   （★ 加厚的语义就是"曲面 ⇒ 实体"）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_part as P                                       # noqa: E402
from scripts import sw_surface_features as SF                          # noqa: E402


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "\u52a0\u539a\u66f2\u9762\uff1aIFeatureManager.FeatureBossThicken\uff08B6/T610\uff09",
          "judge": "\u7279\u5f81\u6811\u589e\u91cf\uff08\u89c4\u5219 6\uff09+ \u5b9e\u4f53\u6570/\u66f2\u9762\u4f53\u6570\u7684\u53d8\u5316",
          "steps": []}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u2605 \u2460 \u5148\u5efa**\u4e00\u5f20\u66f2\u9762**\uff08\u2605 \u7528\u672c\u4ed3\u5df2\u9a8c\u8fc7\u7684\u62d3\u5c55\u66f2\u9762\uff09
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                         -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
        ev["steps"].append({"step": "sketch", "tree": P.feature_names(doc)})
        ex = None
        for cand in ("\u8349\u56fe1", "Sketch1"):
            try:
                ex = SF.create_extruded_surface_report(doc, 20.0, sketch_name=cand)
                break
            except Exception as exc:                                      # noqa: BLE001
                ev["steps"].append({"step": "extruded_surface", "sketch": cand,
                                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])})
        ev["steps"].append({"step": "extruded_surface_ok",
                            "ok": bool(ex and ex.get("ok")), "detail": str(ex)[:130]})
        ev["before"] = {"tree": len(P.feature_names(doc) or []),
                        "solid": SF._solid_body_count(doc),
                        "surface": SF._surface_body_count(doc)}
        #: \u2605 \u2461 \u52a0\u539a
        try:
            r = SF.thicken_surface_report(doc, 3.0, fill_volume=True, merge=True)
            ev["thicken"] = r
        except Exception as exc:                                          # noqa: BLE001
            ev["thicken"] = {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        ev["after"] = {"tree": len(P.feature_names(doc) or []),
                       "solid": SF._solid_body_count(doc),
                       "surface": SF._surface_body_count(doc),
                       "names": list(P.feature_names(doc) or [])}
        ev["verdict"] = "pass" if (ev["thicken"] or {}).get("ok") else "fail"
    except Exception as exc:                                              # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ev["verdict"] = "fail"
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass

    p = R / "output" / "thicken-surface-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u636e\uff1a**%s**" % ev.get("verdict"))
    for s in ev["steps"]:
        print("  %-22s %s" % (s.get("step"), json.dumps({k: v for k, v in s.items() if k != "step"},
                                                        ensure_ascii=False)[:140]))
    print("  \u524d\uff1a%s" % ev.get("before"))
    print("  \u540e\uff1a%s" % json.dumps({k: v for k, v in (ev.get("after") or {}).items() if k != "names"},
                                        ensure_ascii=False)[:130])
    print("  thicken\uff1a%s" % json.dumps(ev.get("thicken"), ensure_ascii=False)[:230])
    if ev.get("err"):
        print("  err=%s" % ev["err"][:170])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
