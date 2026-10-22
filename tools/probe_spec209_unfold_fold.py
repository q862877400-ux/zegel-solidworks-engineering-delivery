"""★ 真机：unfold（idx 336）+ fold（idx 155）—— ★ 判据全是回读（树增量 / 平展型式 / 逐条 mark）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_unfold_fold.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/`：**B2-1（idx 336 unfold）** + **B4-4（idx
#            155 fold）**。
# ★★ 两条**同一次跑**，因为官方示例 `Insert_and_Access_Fold_Feature_Example_VB.md` **就
# 是同一条链**：
#     先 `InsertSheetMetalUnfold`，**再**拿刚建出来的 `Unfold1` 去 `InsertSheetMetalFold` ✓
#   ★★ 判据（规则 6，全回读）：
#     ```
#     unfold ★ 特征树增量 + 新特征名 + 逐条 mark（[1, 4]）+ 选区计数（== 1 + 折弯条数）
#     fold   ★ 同上，且**前置特征（Unfold1）也要在选区里**（官方示例先选它，mark 0）
#     负例   ★ 不给 mark 4 的对象 ⇒ 必须**判"没建出来"**（不拿"没报错"当成功）
#     ```
# 官方依据: `C:\swapi\types\IModelDoc2\{InsertSheetMetalUnfold,InsertSheetMetalFold}.md`
#            ·
# `C:\swapi\examples\Insert_and_Access_Fold_Feature_Example_VB.md`（★ mark 与调用序的唯
# 一出处）·
#   `C:\swapi\types\ISelectionMgr\{SetSelectedObjectMark,GetSelectedObjectMark}.md` ·
#   `C:\swapi\enums\swSelectionMarkAction_e.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-unfold-fold.json"


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    import sw_part as P
    import sw_sheet_metal as SM

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "规格 209 · B2-1 unfold + B4-4 fold（★ 官方示例就是同一条链）",
        "judge": "回读：特征树增量 + 新特征名 + 平展型式个数 + 逐条 mark",
        "unfold": {},
        "fold": {},
        "negative": {},
    }
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    def _plate():
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with P.sketch(doc, "Front Plane") as sk:
            P.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        #: ★ 真厚度 2 mm（文档单位 = 毫米 —— 见 probe_spec209_hem_units.py 的定案）
        SM.create_base_flange(
            doc, sk, SM.BaseFlangeSpec(thickness=2.0, bend_radius=1.0, depth=50.0)
        )
        return doc

    def _names(doc):
        return [
            str(safe_get_com_member(f, "Name") or "") for f in SM.iter_features(doc)
        ]

    #: ── 正例：unfold → fold ────────────────────────────────────────────────────────
    try:
        doc = _plate()
        ev["base_feature_names"] = _names(doc)
        r1 = SM.create_unfold(doc, ["基体-法兰1"], face_index=0)
        ev["unfold"] = {
            "ok": r1.get("ok"),
            "new_features": r1.get("new_features"),
            "tree": [r1.get("tree_before"), r1.get("tree_after")],
            "selection": r1.get("selection"),
            "flat_pattern_count": [
                r1.get("flat_pattern_count_before"),
                r1.get("flat_pattern_count_after"),
            ],
            "error": r1.get("error"),
            "feature_names_after": _names(doc),
        }
        print(
            "  unfold ok=%s new=%r marks=%r"
            % (
                r1.get("ok"),
                r1.get("new_features"),
                (r1.get("selection") or {}).get("marks_readback"),
            )
        )
        unfolded = (r1.get("new_features") or [None])[0]
        if unfolded:
            r2 = SM.create_fold(
                doc, ["基体-法兰1"], face_index=0, unfold_feature_name=unfolded
            )
            ev["fold"] = {
                "ok": r2.get("ok"),
                "new_features": r2.get("new_features"),
                "tree": [r2.get("tree_before"), r2.get("tree_after")],
                "selection": r2.get("selection"),
                "flat_pattern_count": [
                    r2.get("flat_pattern_count_before"),
                    r2.get("flat_pattern_count_after"),
                ],
                "error": r2.get("error"),
                "feature_names_after": _names(doc),
            }
            print(
                "  fold   ok=%s new=%r marks=%r"
                % (
                    r2.get("ok"),
                    r2.get("new_features"),
                    (r2.get("selection") or {}).get("marks_readback"),
                )
            )
        _close(doc)
    except Exception as exc:  # noqa: BLE001
        ev["unfold"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        print("  unfold/fold FATAL %s" % str(exc)[:140])

    #: ── 负例：**不给 mark 4 的对象** ────────────────────────────────────────────────
    try:
        doc2 = _plate()
        r3 = SM.create_unfold(doc2, [], face_index=0)
        ev["negative"] = {
            "ok": r3.get("ok"),
            "new_features": r3.get("new_features"),
            "tree": [r3.get("tree_before"), r3.get("tree_after")],
            "flat_pattern_count": [
                r3.get("flat_pattern_count_before"),
                r3.get("flat_pattern_count_after"),
            ],
            "selection": r3.get("selection"),
            "error": r3.get("error"),
            "_": "★ 负例判据 = **必须判「没建出来」**（★ 它回 void，只能回读）",
        }
        _close(doc2)
        print("  负例 ok=%s new=%r" % (r3.get("ok"), r3.get("new_features")))
    except Exception as exc:  # noqa: BLE001
        ev["negative"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
        print("  负例 FATAL %s" % str(exc)[:140])

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
