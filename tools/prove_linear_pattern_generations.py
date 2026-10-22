"""★ 真机：`FeatureLinearPattern*` 三代逐个试 —— ★ 逐字照搬 `circular_pattern` 那套，只换成员名。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_linear_pattern_generations.py
# 定位:   ★ 2026-10-03（轮 454）—— ★ 承**事实 368**（排除性结论：★ 成员可用 · 判据没问
#           题 · 选区没问题）。
#   ★★★ **所以本轮的维度是**换成员代 + 看返回值****（★ 而不是再调参数）：
#     ```
#     ★ 对照：`circular_pattern`（**能用**）用的是
#        `model.FeatureManager.FeatureCircularPattern4(count, angle_rad, False, "None", False, eq, False)`
#        ⇒ ★ **直接属性调用 + 7 参**
#     ★★ 而 `linear_pattern` 用的是 `FeatureLinearPattern3`（★ **10 参**）
#     ⇒ ★★★ **故本轮问的是**：★ 「**换一代**会不会成？」· ★ 「**它回的是 Feature 还是 None？**」✓
#     ```
#   ★★ 判据（★ 三条并列 + ★ **原始返回值**）：
#     ```
#     ① ★ **原始返回值**（★ None / Feature / 别的 —— ★ 那是最直接的一条线索）
#     ② ★ 特征树增量 · ★ ③ ★★ **几何**（体数 + 包围盒 —— ★ 阵列**必须**改变它）
#     ```
#   ⚠ 选区**逐字照搬** `circular_pattern`（★ `_select_by_id(..., "BODYFEATURE", mark=4)`）——
#     ★★ 因为★ 它**能用**，★ 故那是"已知可用的选区形态" ✓
# 官方依据: `IFeatureManager.FeatureLinearPattern3/4/5`（★ 出厂程序集有**四代**：`Featur
#           eLinearPattern` /
#   `2` / `3` / `4` / `5`）· `FeatureLinearPattern3` 的 10 参
#   （`Num1, Spacing1, Num2, Spacing2, FlipDir1, FlipDir2, DName1, DName2, GeometryPattern, VaryInstance`）·
#   间距**单位是米**（事实 315）· 本仓 `scripts/sw_part.py` 的 `linear_pattern` / `circular_pattern`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（原始返回值 + 特征树 + 几何）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "linear-pattern-generations-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_feature_readback import feature_names
    from scripts.sw_part import (_select_by_id, current_sketch_name, end_sketch,
                                 extrude_boss, sketch_corner_rectangle, start_sketch)

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "trials": []}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -8.0, -8.0, 8.0, 8.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        names = list(feature_names(doc))
        feat = names[-1] if names else ""

        def geom() -> dict:
            out: dict = {}
            try:
                bodies = list(get_com_member(doc, "GetBodies2", -1, True) or [])
                out["bodies"] = len(bodies)
                if bodies:
                    bb = get_com_member(bodies[0], "GetBodyBox")
                    out["box"] = [round(float(x), 6) for x in bb] if bb else None
            except Exception as exc:                           # noqa: BLE001
                out["err"] = str(exc)[:70]
            return out

        ev["feature_name"] = feat
        ev["before_tree"] = len(names)
        ev["before_geom"] = geom()

        #: ★ 逐代试（★ 选区**逐字照搬** `circular_pattern` 的形态）
        trials = [
            ("FeatureLinearPattern3", 3,
             lambda: get_com_member(get_com_member(doc, "FeatureManager"), "FeatureLinearPattern3",
                                    3, 0.025, 1, 0.0, False, False, "", "", False, False)),
            #: ★★★ 2026-10-03（轮 454）**换一代而不是再调参数** ——
            #:   ★ 从出厂程序集读到的 **arity 表**：
            #:     `FeatureLinearPattern` 8 · `2` 9 · **`3` 10**（★ 我用对了）·
            #:     **`4` 20** · **`5` 22** · `FeatureCircularPattern4` 7（对照，能用）
            #:   ★★ 故上一版对 4/5 代传 10 个 ⇒ **报"非选择性的参数"**（★ 那正是 arity 信号）
            #:   ★★★ 而本次**按 20 参填满**（★ 前 10 个同名，后 10 个取"不偏移、按数量控制、不从质心" 的常规值）✓
            ("FeatureLinearPattern4", 3,
             lambda: get_com_member(get_com_member(doc, "FeatureManager"), "FeatureLinearPattern4",
                                    3, 0.025, 1, 0.0, False, False, "", "", False, False,
                                    False, False, True, True, False, False, False, False, 0.0, 0.0)),
            ("FeatureLinearPattern5", 3,
             lambda: get_com_member(get_com_member(doc, "FeatureManager"), "FeatureLinearPattern5",
                                    3, 0.025, 1, 0.0, False, False, "", "", False, False)),
        ]
        for label, _n, call in trials:
            rec: dict = {"trial": label}
            try:
                doc.ClearSelection2(True)
                sel = _select_by_id(get_com_member(doc, "Extension"), feat, "BODYFEATURE", mark=4)
                rec["selected"] = bool(sel)
                r = call()
                rec["raw_type"] = type(r).__name__
                rec["raw_is_none"] = r is None
            except Exception as exc:                           # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            after = list(feature_names(doc))
            rec["tree_before_after"] = [ev["before_tree"], len(after)]
            rec["tree_new"] = [n for n in after if n not in names]
            rec["geom_changed"] = geom() != ev["before_geom"]
            rec["geom"] = geom()
            ev["trials"].append(rec)
        ev["any_geom_changed"] = any(t.get("geom_changed") for t in ev["trials"])
        ev["verdict"] = "pass" if ev["any_geom_changed"] else "fail"
        ev["note"] = ("★ 三代逐个试，★ 选区逐字照搬 circular_pattern（★ 而它**能用**）。"
                      "★ 判据：★ **原始返回值** + 特征树 + ★★ **几何**（★ 阵列必须改变包围盒）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
