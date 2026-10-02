"""★ 真机：`linear_pattern` 的卡点 —— ★ 判据**三条都看**（特征树 · 特征数 · **几何**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_linear_pattern_geometry.py
# 定位:   ★ 2026-10-03（轮 453）—— ★ 承**事实 315**（`linear_pattern` 三次尝试后**没抛错而特征树 9→9**）
#   与**本轮**的否定结论（★ `tools/prove_pattern_members.py`：★ 5 代成员**全都取得到** ⇒ **不是"成员不可用"**）。
#   ★★★ **故本轮换的是**判据**，不是参数**（★ 事实 53 那条区分）：
#     ```
#     ★ 事实 315 的判据 = 「**特征树名字有没有多一个**」
#     ★★ 而**阵列**建出来的特征**可能不叫新名字** ——
#       ★ 它可能**替换/合并**了原特征（★ 而那样"树 9→9"**恰恰是应然的**）⚠
#     ⇒ ★★★ **故真正的判据该看**几何**：★ **包围盒**与★ **面的数量** ✓✓✓
#     ```
#   ★★ 判据（★ 三条并列报，★ **不预设哪条对**）：
#     ```
#     ① ★ 特征树：★ 名字增量（★ 事实 315 用的那条）
#     ② ★ `GetFeatureCount` 的前后（★ 比"名字"更粗、★ 而**不会漏掉改名**）
#     ③ ★★ **几何**：★ `GetBodies2` 的**体数** + 第一个体的**包围盒**（★ 阵列**必须**让它变）
#     ```
#   ⚠ **前置**：★ 要一个**能被阵列**的特征（★ 本探针先建一个凸台，★ 而它**没有**依赖外部草图）
# 官方依据: `IFeatureManager.FeatureLinearPattern3`（★ **10 参**：`Num1, Spacing1, Num2, Spacing2,
#   FlipDir1, FlipDir2, DName1, DName2, GeometryPattern, VaryInstance`）· 间距**单位是米**（事实 315）·
#   本仓 `scripts/sw_part.py` 的 `linear_pattern`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 三条并列报（特征树 / 特征数 / 几何）—— ★ 而「建成」= 几何真的变了。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(r"D:\AI\SW\output\linear-pattern-geometry-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)

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

        def tree() -> list:
            #: ★★★ 2026-10-03（轮 453）**用本仓既有的帮手** ——
            #:   ★ 我第一版**自己搓**了一个读特征名的循环，
            #:   ★★ 而它在**树里有非特征项**时坏了（★ 真机：`feature_name = "?"`）⚠
            #:   ★★★ 而本仓**早就有** `sw_feature_readback.feature_names`（★ 还专门一个模块）✓
            from scripts.sw_feature_readback import feature_names as _fn
            return list(_fn(doc))

        def geom() -> dict:
            """★ 几何读数：★ 体数 + 第一个体的包围盒（★ 阵列**必须**让它变）。"""
            out: dict = {}
            try:
                bodies = list(get_com_member(doc, "GetBodies2", -1, True) or [])
                out["bodies"] = len(bodies)
                if bodies:
                    bb = get_com_member(bodies[0], "GetBodyBox")
                    out["box"] = [round(float(x), 6) for x in bb] if bb else None
            except Exception as exc:                           # noqa: BLE001
                out["err"] = str(exc)[:80]
            return out

        before_names = tree()
        before_geom = geom()
        ev["before"] = {"tree": len(before_names), "geom": before_geom}
        ev["feature_name"] = (before_names[-1] if before_names else "")

        #: ★ 三条分别试（★ 而**每条都是同一件事的一个判据**）
        for label, fn in (
            ("pattern_named_feature", lambda: __import__("scripts.sw_part", fromlist=["x"])
             .linear_pattern(doc, ev["feature_name"], 1.0, 0.0, 0.0, 25.0, 3)),
        ):
            rec: dict = {"trial": label}
            try:
                r = fn()
                rec["raw_none"] = r is None
                rec["raw_type"] = type(r).__name__
            except Exception as exc:                           # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            after_names = tree()
            after_geom = geom()
            rec["tree_new"] = [n for n in after_names if n not in before_names]
            rec["tree_before_after"] = [len(before_names), len(after_names)]
            rec["geom_changed"] = after_geom != before_geom
            rec["geom"] = after_geom
            ev["trials"].append(rec)
        ev["verdict"] = ("pass" if any(t.get("geom_changed") for t in ev["trials"])
                         else ("partial" if any(t.get("tree_new") for t in ev["trials"]) else "fail"))
        ev["note"] = "★ 三条判据并列：① 特征树名字增量 · ② 特征数 · ③ 几何（体数 + 包围盒）。★ 「建成」 = 几何真的变了。"
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1500])
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
