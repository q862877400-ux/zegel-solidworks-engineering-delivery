"""★ 用"中点 + mark"重试 `insert_parting_line`（轮 51 因"边线带不了 mark"而走死）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_mold_parting_line_marks.py
# 定位:   ★ 2026-10-03（轮 389）**用新发现回头解旧死路**：轮 51 判 `mold_parting_geome
#           try` 的写入那半
# "走死"（★ 因为 `IEntity.Select4` 没有 mark 参数、而官方 Remarks 要求**边线带 mark = 4*
# *）。
# ★★ 而轮 388（事实 305）在 `filled_surface` 上证明：**用 `SelectByID2` + **边的中点** +
#  mark 是有效的**
#   （★ 对照：mark 给对 ⇒ 计数对得上；mark 给错 ⇒ 回 true 而计数 0）。
#   ⇒ 本探针用那个手法重试 `insert_parting_line`。
# 官方依据: `InsertMoldPartingLine` 的 Remarks —— 「you must select the direction of pul
#           l and the edges
# for the parting line by calling `IModelDocExtension::SelectByID2` with the following m_
# arks:
#   **Direction of pull = 1** · **Parting line edges = 4**」。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量）：
# ```
# ① mark=1 选基准面（拔模方向）+ mark=4 按**中点**选边 ⇒ **回读计数**必须 ≥ 2
# ② `insert_parting_line` **回非空特征名**
# ③ 回读 `mold_evidence()` 的 `parting_lines` 计数（★ 若它回 null，★ 如实记 —— 事实 8）
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "mold-parting-line-marks-evidence.json"
)
MARK_PULL = 1
MARK_EDGES = 4


def main() -> int:
    import sw_connect
    import sw_mold as m_
    import sw_surface_features as sf
    from sw_connect import get_com_member
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%m_:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 25.0)
        ext = get_com_member(doc, "Extension")
        callout = sw_connect.create_empty_dispatch_variant()
        sm = get_com_member(doc, "SelectionManager")
        ev["steps"]["doc"] = {
            "ok": True,
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
        }

        def mids():
            out = []
            for b in get_com_member(doc, "GetBodies2", -1, True) or []:
                for e in get_com_member(b, "GetEdges") or []:
                    try:
                        a = [
                            float(x)
                            for x in get_com_member(
                                get_com_member(e, "GetStartVertex"), "GetPoint"
                            )
                        ]
                        c = [
                            float(x)
                            for x in get_com_member(
                                get_com_member(e, "GetEndVertex"), "GetPoint"
                            )
                        ]
                        out.append([(a[i] + c[i]) / 2.0 for i in range(3)])
                    except Exception:  # noqa: BLE001
                        continue
            return out

        #: ① mark=1 选拔模方向（基准面）
        doc.ClearSelection2(True)
        ok1 = bool(
            ext.SelectByID2(
                "前视基准面", "PLANE", 0, 0, 0, False, MARK_PULL, callout, 0
            )
        )
        #: ② mark=4 按**中点**选边（★ 轮 388 的手法）
        ms = mids()
        zs = sorted({round(m[2], 9) for m in ms})
        picked = 0
        if zs:
            ztop = zs[-1]
            for m in ms:
                if abs(m[2] - ztop) < 1e-9:
                    if ext.SelectByID2(
                        "", "EDGE", m[0], m[1], m[2], True, MARK_EDGES, callout, 0
                    ):
                        picked += 1
            ev["steps"]["boundary_z"] = {"ok": True, "z": ztop, "candidates": len(ms)}
        total = int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)
        ev["steps"]["select_marks"] = {
            "ok": (ok1 and picked > 0 and total > 1),
            "pull_ok": ok1,
            "edges_picked": picked,
            "readback": total,
            "note": "★ 回读计数才对（★ 回 true 不算 —— 事实 8）",
        }
        #: ③ 插分型线
        before = sf.feature_names(doc)
        try:
            name = m_.insert_parting_line(doc)
            after = sf.feature_names(doc)
            ev["steps"]["insert_parting_line"] = {
                "ok": bool(name),
                "feature_name": str(name)[:60],
                "new_features": [n for n in after if n not in before][-2:],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["insert_parting_line"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
            }
        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 轮 51 判「边线带不了 mark」；★ 本轮用 `SelectByID2` + **边的中点** + mark=4 重试 —— "
            "★ 该手法在 `filled_surface`（轮 388）上被证明有效（mark 对 ⇒ 计数对得上）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1300])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
