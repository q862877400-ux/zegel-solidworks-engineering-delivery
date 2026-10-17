"""★ 真机：用**本仓的包装** `add_link_connector` 走**已验场景**（★ 两个体各一个顶点）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_link_wrapper_twobody.py
# 定位:   ★ 2026-10-03（轮 459）—— ★ 承**事实 373**（★ `AddLinkConnector` 真机建成 · `Count 0→1`）
#   与**事实 374 的发现**（★ `_check` **已统一补** `out_i4()` —— ★ 故那个包装**可能本来就是对的**）。
#   ★★★ **故本探针的问法是**：★ **不手调 COM，★ 而调本仓的包装** ——
#     ★★ 若它**在已验场景上也成** ⇒ ★ **包装本来就是对的** ⇒ ★ **可以直接挂** ✓
#     ★ 而★ 若它**不成** ⇒ ★ **那才是包装的问题**（★ 而★ 那时该改它）✓
#   ⚠ **判据（★ 与事实 373 同一口径）**：★ **`Count` +1** · ★ 而★ **不拿返回值当判据**（★ 事实 8）。
#   ⚠ **前置**：★ **两个不相连的凸台**（★ 而★ 那就是上一轮验成的场景）✓
# 官方依据: `scripts/sw_simulation_loads.add_link_connector`（★ 走 `_check(..., 2, …)` ⇒ **自动补 out_i4()**）·
#   `ICWLoadsAndRestraintsManager.AddLinkConnector`（★ arity 3）· 事实 338 / 373
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "link-wrapper-twobody-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_simulation import create_static_study, get_study_manager
    from scripts.sw_simulation_loads import add_link_connector

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        for x1, x2 in ((-40.0, -10.0), (10.0, 40.0)):
            start_sketch(doc, plane_name="Front Plane")
            sketch_corner_rectangle(doc, x1, -10.0, x2, 10.0)
            sk = current_sketch_name(doc, "")
            end_sketch(doc)
            extrude_boss(doc, sk, 10.0)
        bs = list(get_com_member(doc, "GetBodies2", -1, True) or [])
        ev["bodies"] = len(bs)
        verts = []
        for b in bs[:2]:
            vs = list(get_com_member(b, "GetVertices") or [])
            if vs:
                verts.append(vs[0])
        ev["verts"] = len(verts)

        try:
            create_static_study(sw, "LinkWrapper")
        except Exception as exc:                               # noqa: BLE001
            ev["study_err"] = str(exc)[:110]
        mgr = get_study_manager(sw)
        study = get_com_member(mgr, "GetStudy", 0)
        ev["study_none"] = study is None
        if study is None:
            ev["verdict"] = "fail"
        else:
            lm = get_com_member(study, "LoadsAndRestraintsManager")

            def cnt() -> int:
                try:
                    return int(get_com_member(lm, "Count") or 0)
                except Exception:                              # noqa: BLE001
                    return -1

            ev["count_before"] = cnt()
            try:
                r = add_link_connector(lm, verts[0], verts[1])
                ev["raw_type"] = type(r).__name__
                ev["raw_is_none"] = r is None
            except Exception as exc:                           # noqa: BLE001
                ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            ev["count_after"] = cnt()
            built = ev["count_after"] > ev["count_before"]
            ev["verdict"] = "pass" if built else "fail"
            ev["note"] = ("★ **调本仓的包装**（★ 而不手调 COM）★ 走**已验场景**（★ 两个体各一个顶点）。"
                          "★ `_check` 已统一补 `out_i4()` ⇒ ★ 若它成 ⇒ ★ 包装本来就是对的 ⇒ 可直接挂。"
                          "★ 判据：★ `Count` **+1**。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1200])
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
