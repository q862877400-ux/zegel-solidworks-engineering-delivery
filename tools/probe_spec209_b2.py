"""★ 真机：规格 209 · B4-2（idx 173 hem）+ B2-1（idx 336 unfold）—— 判据全是回读。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b2.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-2（hem）** 与 **B2-1（unfold）**
#           真机探针。
# ★★ 为什么这两条**同一次跑**：unfold 的**前置是"带折弯的钣金件"**，而本机磁盘上**没有**
# 这种模型
#     （全盘扫过 `.SLDPRT`：只有刀柄/螺母/垫圈/壳体那几个，**零个钣金件**），
# 且 `create_edge_flange` / `create_one_bend` 属**事实 47 那一族**（`AccessSelections`
# 到不了，
#     20+ 形态已穷尽 ⇒ **不许再试**）⇒ ★★ **hem 是唯一可达的"造出折弯"的路**
#     （它是**直接 16 参调用**，不经过 `AccessSelections`）✓
# 官方依据: 见 `scripts/sw_sheet_metal.py` 本轮追加段的来源块（两页 + 五个枚举 + 两份官
#           方示例）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
#
# ★★ **判据（规则 6 —— 一律回读，不用返回值）**：
#   ```
#   T1 造前置    ★ 基体法兰（闭轮廓）建成 + `IsSheetMetal` 为真
# T2 hem       ★ 特征树 **+1** 且（**面数变化** 或 **包围盒变化**）；★ 并回读 `IHemFeatu
# reData.Type`
#   T3 unfold    ★ 特征树增量 + **平展型式个数**；★ 且**记下"折弯特征"到底叫什么**
#   T4 负例      ★ 在**没有折弯**的基体法兰上调 unfold ⇒ **如实报**（不拿"没报错"当成功）
#   ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-b2-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sheet_metal as SM
    import sw_selection_spec as SS

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "规格 209 · B4-2 hem + B2-1 unfold（★ 一次跑：hem 是 unfold 的前置）",
        "judge": "回读（特征树增量 / 面数 / 包围盒 / 平展型式个数）+ IHemFeatureData.Type",
        "T1_base_flange": {},
        "T2_hem": {},
        "T3_unfold": {},
        "T4_unfold_no_bends": {},
    }
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    def _make_sheet_metal(tag=""):
        """★ 闭轮廓基体法兰 ⇒ 真机已验证可成的钣金件（特征树：钣金 / 基体-法兰 / 平展型式）✓"""
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with P.sketch(doc, "Front Plane") as sk:
            P.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        spec = SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.001, depth=0.05)
        SM.create_base_flange(doc, sk, spec)
        return doc

    def _feature_names(doc):
        return [
            str(safe_get_com_member(f, "Name") or "") for f in SM.iter_features(doc)
        ]

    def _faces(doc):
        try:
            return len(SS.entities_on_body(doc, "FACE"))
        except Exception:  # noqa: BLE001
            return None

    #: ── T1 · 造前置（基体法兰）──────────────────────────────────────────────────────
    doc = None
    try:
        doc = _make_sheet_metal()
        sm_ev = SM.sheet_metal_evidence(doc)
        ev["T1_base_flange"] = {
            "feature_names": _feature_names(doc),
            "feature_types": sm_ev.get("feature_types"),
            "has_base_flange": sm_ev.get("has_base_flange"),
            "has_sheet_metal_feature": sm_ev.get("has_sheet_metal_feature"),
            "all_solid_bodies_are_sheet_metal": sm_ev.get(
                "all_solid_bodies_are_sheet_metal"
            ),
            "base_parameters": sm_ev.get("base_flange_parameters"),
            "face_count": _faces(doc),
            "verdict": "前置建成" if sm_ev.get("has_base_flange") else "★ 前置没建出来",
        }
        print(
            "  T1 基体法兰 %s | faces=%s"
            % (ev["T1_base_flange"]["verdict"], ev["T1_base_flange"]["face_count"])
        )
    except Exception as exc:  # noqa: BLE001
        ev["T1_base_flange"] = {
            "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])
        }
        print("  T1 FATAL %s" % str(exc)[:140])

    #: ── T2 · hem（idx 173）★ 官方四步前置 + 16 参 ────────────────────────────────────
    hem_feature = None
    if doc is not None and ev["T1_base_flange"].get("verdict") == "前置建成":
        try:
            r = SM.create_hem(doc, "index:0")
            hem_feature = r.get("feature") or None
            ev["T2_hem"] = {
                "ok": r.get("ok"),
                "feature": r.get("feature"),
                "feature_type": r.get("feature_type"),
                "hem_type_readback": r.get("hem_type_readback"),
                "tree": [r.get("tree_before"), r.get("tree_after")],
                "face_count": [r.get("face_count_before"), r.get("face_count_after")],
                "bbox_before": r.get("bbox_before"),
                "bbox_after": r.get("bbox_after"),
                "bbox_changed": r.get("bbox_changed"),
                "bbox_comparable": r.get("bbox_comparable"),
                "api_args": r.get("api_args"),
                "error": r.get("error"),
                "note": r.get("note"),
                "feature_names_after": _feature_names(doc),
            }
            print(
                "  T2 hem ok=%s feature=%r type=%r 面 %s→%s"
                % (
                    r.get("ok"),
                    r.get("feature"),
                    r.get("feature_type"),
                    r.get("face_count_before"),
                    r.get("face_count_after"),
                )
            )
        except Exception as exc:  # noqa: BLE001
            ev["T2_hem"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
            print("  T2 FATAL %s" % str(exc)[:140])

    #: ── T3 · unfold（idx 336）★ 用 hem 造出来的那个特征当"折弯"（★★ 这一格就是裁决书要
    #: 的
    #: "**必须先真机定出可建对象**"）───────────────────────────────────────────────────
    #: ─
    if doc is not None and hem_feature:
        try:
            r = SM.create_unfold(doc, [hem_feature], face_index=0)
            ev["T3_unfold"] = {
                "ok": r.get("ok"),
                "bend_feature_used": hem_feature,
                "selection": r.get("selection"),
                "returned": str(r.get("returned"))[:40],
                "tree": [r.get("tree_before"), r.get("tree_after")],
                "new_features": r.get("new_features"),
                "flat_pattern_count": [
                    r.get("flat_pattern_count_before"),
                    r.get("flat_pattern_count_after"),
                ],
                "bbox_comparable": r.get("bbox_comparable"),
                "bbox_before": r.get("bbox_before"),
                "bbox_after": r.get("bbox_after"),
                "error": r.get("error"),
                "feature_names_after": _feature_names(doc),
            }
            print(
                "  T3 unfold ok=%s new=%r 平展型式 %s→%s"
                % (
                    r.get("ok"),
                    r.get("new_features"),
                    r.get("flat_pattern_count_before"),
                    r.get("flat_pattern_count_after"),
                )
            )
        except Exception as exc:  # noqa: BLE001
            ev["T3_unfold"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
            print("  T3 FATAL %s" % str(exc)[:140])
    else:
        ev["T3_unfold"] = {
            "skipped": "★ 前置不存在（没有 hem 特征可当折弯）—— 如实记，不伪造"
        }

    #: ── T4 · 负例：**没有折弯**的基体法兰上调 unfold ─────────────────────────────────
    #: ────
    try:
        doc2 = _make_sheet_metal()
        names2 = _feature_names(doc2)
        r2 = SM.create_unfold(doc2, [], face_index=0)
        ev["T4_unfold_no_bends"] = {
            "ok": r2.get("ok"),
            "bend_feature_used": [],
            "selection": r2.get("selection"),
            "tree": [r2.get("tree_before"), r2.get("tree_after")],
            "new_features": r2.get("new_features"),
            "flat_pattern_count": [
                r2.get("flat_pattern_count_before"),
                r2.get("flat_pattern_count_after"),
            ],
            "error": r2.get("error"),
            "feature_names_before": names2,
            "_": "★ 负例：**没有折弯可展**时它应当**建不出特征**（★ 而「没报错」不算成功）",
        }
        _close(doc2)
        print("  T4 负例 ok=%s new=%r" % (r2.get("ok"), r2.get("new_features")))
    except Exception as exc:  # noqa: BLE001
        ev["T4_unfold_no_bends"] = {
            "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])
        }
        print("  T4 FATAL %s" % str(exc)[:140])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
