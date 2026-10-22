"""★ 真机：直纹曲面失败后读 **What's Wrong**（★ 上轮留的"换观测手段"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_ruled_whats_wrong.py
# 定位:   ★ 2026-10-03（轮 507）★ 做上一轮**登记在事实 391 里的那条方法论**：
#
# > ★ **若要继续攻：该换的是观测手段**（★ 如查 SW 的"什么错"面板 / 试 `CreateDefinition`
#  新架构），
#   > ★ **而不是**继续在同一入口上换参数 —— ★ 那已经证明不是参数问题。
#
#   ★★ **本仓早就有那条手段**：`scripts/sw_feature_readback.py` 的
#     **`whats_wrong(model)`** —— ★ 它正是**本仓规则 6** 的落地：
#     「建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，**不静默成功**」✓
# （★ 官方依据：`IModelDoc2.EditRebuild3`（bool）· `IModelDoc2.GetWhatsWrong2`（按 by-re
# f 数组出参））
#
#   ⇒ ★ 故本探针：★ **建实体 → 选一条水平边 → 调直纹曲面 → 读 `whats_wrong`**
#     ★★ 看 SW 到底**报了什么**（★ 而非只看"树没动"）。
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 本探针**不求建成** —— ★ 它要的是**失败后 SW 自己怎么说** ✓

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as FR  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as SF  # noqa: E402


def _horiz_edge_index(doc):
    """★ 找一条**水平边**（★ 两端 Z 相同 ⇒ 与拉伸方向垂直）。"""
    b = list(C.get_com_member(doc, "GetBodies2", 0, True) or [])[0]
    for i, e in enumerate(list(C.get_com_member(b, "GetEdges") or [])):
        try:
            a = [
                float(x)
                for x in (
                    C.get_com_member(C.get_com_member(e, "GetStartVertex"), "GetPoint")
                    or []
                )
            ]
            z = [
                float(x)
                for x in (
                    C.get_com_member(C.get_com_member(e, "GetEndVertex"), "GetPoint")
                    or []
                )
            ]
        except Exception:  # noqa: BLE001
            continue
        if a and z and abs(a[2] - z[2]) < 1e-9:
            return i
    return None


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u76f4\u7eb9\u66f2\u9762\u5931\u8d25\u540e\u8bfb What's Wrong\uff08\u2605 \u6362\u89c2\u6d4b\u624b\u6bb5\uff09",
        "steps": [],
    }
    doc = None
    try:
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
                P.extrude_boss(doc, cand, 0.02)
                break
            except Exception:  # noqa: BLE001
                continue
        ev["ww_before"] = FR.whats_wrong(doc)

        idx = _horiz_edge_index(doc)
        ev["edge_index"] = idx
        b = list(C.get_com_member(doc, "GetBodies2", 0, True) or [])[0]
        edges = list(C.get_com_member(b, "GetEdges") or [])
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        if idx is not None:
            ev["selected"] = bool(P._select_com_object(edges[idx], append=True, mark=0))
            try:
                ev["sel_count"] = int(
                    C.get_com_member(
                        C.get_com_member(doc, "SelectionManager"),
                        "GetSelectedObjectCount2",
                        -1,
                    )
                    or 0
                )
            except Exception:  # noqa: BLE001
                ev["sel_count"] = None

        r = SF.insert_ruled_surface_report(doc, surface_type=1, length_mm=10.0)
        ev["ruled"] = {k: v for k, v in r.items() if k != "\u2605"}
        ev["ww_after"] = FR.whats_wrong(doc)
        ev["rebuild_after"] = bool(C.get_com_member(doc, "EditRebuild3"))
        ev["ww_after_rebuild"] = FR.whats_wrong(doc)
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass

    p = R / "output" / "ruled-whats-wrong-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u8fb9#%s \u9009\u4e2d=%s\uff08\u8ba1\u6570 %s\uff09"
        % (ev.get("edge_index"), ev.get("selected"), ev.get("sel_count"))
    )
    print("  ruled\uff1a%s" % json.dumps(ev.get("ruled"), ensure_ascii=False)[:180])
    print(
        "  ww_before           \uff1a%s"
        % json.dumps(ev.get("ww_before"), ensure_ascii=False)[:220]
    )
    print(
        "  ww_after            \uff1a%s"
        % json.dumps(ev.get("ww_after"), ensure_ascii=False)[:300]
    )
    print(
        "  ww_after_rebuild    \uff1a%s"
        % json.dumps(ev.get("ww_after_rebuild"), ensure_ascii=False)[:300]
    )
    if ev.get("err"):
        print("  err=%s" % ev["err"][:200])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
