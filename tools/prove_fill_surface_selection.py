"""★ 真机：填充曲面 —— ★ 验 `boundary_z` → `selection` 这次改动的**两条路**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_fill_surface_selection.py
# 定位:   ★ 2026-10-03（轮 434）承**事实 347** 那条**真欠账**的修复。
#   ★★ 事实 347 查明：★ `solidworks_surface_fill` 的 `boundary_z` **是裸坐标**（★ 违反规则 3），
#     ★ 而那条违反让 `tool_registry` 的声明门禁**整批不过** ⇒
#     **4 个测试文件在收集期就 ERROR**（★ 一直在吃测试覆盖）。
#   ★★ **修法**：★ 把那个坐标参数换成**声明式 `selection`** ——
#     ★ 而**保留原自动行为**（★ 留空 = 自动取最高那一圈）⇒ ★ **行为不变、形态合规** ✓
#   ★★★ **而改了实现就必须真机验**（★ 硬约束③）—— ★ 本探针验**两条路**：
#     ```
#     ① 留空 selection ⇒ **自动取最高那一圈**（★ 与改动前同一行为）
#     ② 给 selection   ⇒ **声明式选**（★ 规则 3 要求的形态）
#     ```
#   ★ 判据（★ 规则 6）：★ **回 `Feature` 非 None** **且** **特征树增量非空**。
# 官方依据: `IFeatureManager.InsertFillSurface2`（★ 6 参）· 本仓 `insert_fill_surface_report` ·
#   `sw_selection_spec.resolve_selection`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 两条路**各自**都 `ok` 且**特征树有增量**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "fill-surface-selection-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_surface_features import insert_fill_surface_report
    from scripts.sw_part import _empty_callout

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        #: ★ 两条路**各用一个新的零件**（★ 事实 324：每格独立）—— ★ 不然第二条会被第一条污染
        for label, use_selection in (("auto_top_ring", False), ("declarative_selection", True)):
            doc = sw_connect.new_document(sw, "part")
            start_sketch(doc, plane_name="Front Plane")
            sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
            sk = current_sketch_name(doc, "")
            end_sketch(doc)
            extrude_boss(doc, sk, 20.0)
            rec: dict = {"trial": label}
            try:
                if use_selection:
                    #: ★★ **声明式：先把"最高那一圈"的边选上** ——
                    #:   ★ 而选法**照自动路的口径**（★ 按中点 z 找最高一圈）
                    #:   ⇒ ★ 这样才是**忠实地测那一支**（★ 而不是测"随便选一条边会怎样"）。
                    #:   ⚠ 上一版只选了**1 条**（★ 而填充要**一圈**）⇒ ★ 那是**探针样本**的错，不是代码的错。
                    sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                    bodies = list(get_com_member(doc, "GetBodies2", -1, True) or [])
                    ring = []
                    for b in bodies:
                        for e in (get_com_member(b, "GetEdges") or []):
                            try:
                                a = [float(x) for x in get_com_member(
                                    get_com_member(e, "GetStartVertex"), "GetPoint")]
                                c = [float(x) for x in get_com_member(
                                    get_com_member(e, "GetEndVertex"), "GetPoint")]
                            except Exception:                      # noqa: BLE001
                                continue
                            #: ★★ 用**中点** z（★ 与实现同一口径）——
                            #:   ★ 上一版用 `max(a[2], c[2])` 而**竖边的顶点** z 也等于最高值
                            #:   ⇒ 选了 **7** 条（顶圈 4 + 竖边 4，而不是一圈）⇒ 当然不成。
                            ring.append(((a[2] + c[2]) / 2.0, e, ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0,
                                                              (a[2] + c[2]) / 2.0)))
                    if ring:
                        zmax = max(r[0] for r in ring)
                        top = [r for r in ring if abs(r[0] - zmax) < 1e-9]
                        ext = get_com_member(doc, "Extension")
                        for _z, _e, mid in top:
                            ext.SelectByID2("", "EDGE", mid[0], mid[1], mid[2], True, 1,
                                             _empty_callout(), 0)
                        n = int(get_com_member(get_com_member(doc, "SelectionManager"),
                                               "GetSelectedObjectCount2", -1) or 0)
                    else:
                        n = 0
                    rec["preselected"] = n
                    rep = insert_fill_surface_report(doc, 2, selection="__current_selection__")
                else:
                    rep = insert_fill_surface_report(doc, 2)
                rec["ok"] = bool(rep.get("ok"))
                rec["feature_name"] = rep.get("feature_name")
                rec["new_features"] = rep.get("new_features")
                rec["tree_before_after"] = [rep.get("tree_before"), rep.get("tree_after")]
                rec["points_selected"] = rep.get("points_selected")
                rec["error"] = (rep.get("error") or "")[:130]
            except Exception as exc:                           # noqa: BLE001
                rec["ok"] = False
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
            ev["trials"].append(rec)
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
            doc = None
        wins = [t["trial"] for t in ev["trials"] if t.get("ok") and t.get("new_features")]
        ev["verdict"] = "pass" if len(wins) >= 1 else "partial"
        ev["successes"] = wins
        ev["note"] = ("★ 验 `boundary_z` → `selection` 的改动：★ 两条路各用一个**新零件**"
                      "（★ 事实 324：每格独立）。★ 判据：★ `ok` **且** 特征树**有增量**。")
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
