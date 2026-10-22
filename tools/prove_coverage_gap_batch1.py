"""★ 真机：覆盖面缺口批 1 —— 旋转曲面 / 孔向导 / 完全定义检查（★ 只测**能测的**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）· 规格 `specs/202-user-coverage-gaps`（T201 / T401）
# 文件:   tools/prove_coverage_gap_batch1.py
# 定位:   ★ 2026-10-03（接手轮）★ 为「提升覆盖面」测**最便宜的三项**：
#   ★★ 判据：`docs/user-feature-coverage.md` §八 的缺口项里，**本仓已经有真实现**的那些
#     （★ 用 `tools/audit_gap_implementations.py` 以 **AST** 量出来的 —— 不用 grep，
#      因为来源块里大量引用官方成员名，grep 会把注释算成"有实现"）。
#
#   ★★★ **而 AST 只说"有代码"，不说"能用"** —— ★ 本轮就撞到一个反例：
# · **样条曲线**：AST 报"有实现"（`sw_part.sketch_spline`），★ 而**读那个函数的文档串**
# 才发现
#       它**2026-10-01 轮 141 已真机实测不达**：`CreateSpline2` 回 `None`，
# 后继 `CreateSpline3` 末参是 **BYREF `Object&`** ⇒ pywin32 迟到绑定到不了（事实 47/68）
# 。
#       ⇒ ★★ **故本探针不测样条** —— 它属「带依据的到不了」，★ 不假装做到。
#     ⇒ ★ 教训：★ **"有实现" ≠ "能用"**，中间必须过"读它自己的文档串 + 真机"两关。
#
#   ★ 三格：
#     | 格 | 能力 | 入口 | 判据 |
#     |---|---|---|---|
# | B1 | 旋转曲面 | `sw_surface_ref_ops.insert_revolved_ref_surface`（`InsertRevolvedRef
# Surface`） | 树增量 + **曲面体数**增量 |
# | B2 | 孔向导 | `sw_hole_features.create_hole_wizard_at_selection_report`（`HoleWizard
# 5`） | 树增量 + 回读报告 |
# | B3 | 完全定义检查 | `ISketch.GetConstrainedStatus()`（★ 新实现） | 调得动且回 **int*
# *；★ 并试"改到完全定义后值是否变" |
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每格新开文档；★ 收尾关掉自己开的文档。
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

import scripts.sw_feature_readback as fr  # noqa: E402
import scripts.sw_hole_features as hf  # noqa: E402
import scripts.sw_surface_ref_ops as sro  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def _get(o, name, *a):
    return C.get_com_member(o, name, *a)


def _tree(doc):
    return list(fr.feature_names(doc) or [])


def _surface_body_count(doc):
    """★ 曲面体计数（`GetBodies2(1, True)` —— 1 = `swSurfaceBody`）。"""
    try:
        return len(list(_get(doc, "GetBodies2", 1, True) or []))
    except Exception:  # noqa: BLE001
        return None


def _solid_body_count(doc):
    try:
        return len(list(_get(doc, "GetBodies2", 0, True) or []))
    except Exception:  # noqa: BLE001
        return None


def _close(sw, doc):
    try:
        t = str(_get(doc, "GetTitle") or "")
        if t:
            _get(sw, "CloseDoc", t)
    except Exception:  # noqa: BLE001
        pass


def case_revolved(sw):
    """★ B1 旋转曲面：★ 轮廓 = 一条中心线 + 一个偏心的闭合矩形（★ 不碰轴）。"""
    row = {"tag": "★ B1 旋转曲面（InsertRevolvedRefSurface）", "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = _get(doc, "SketchManager")
        _get(sm, "CreateCenterLine", 0.0, -0.03, 0.0, 0.0, 0.03, 0.0)  #: 轴线
        _get(sm, "CreateCornerRectangle", 0.01, -0.02, 0.0, 0.03, 0.02, 0.0)
        P.end_sketch(doc)
        sk = [
            n
            for n in _tree(doc)
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        row["sketch"] = sk[-1] if sk else None
        ext = _get(doc, "Extension")
        doc.ClearSelection2(True)
        selected = []
        for cand in (row["sketch"],):
            if cand and P._select_by_id(ext, cand, "SKETCH", append=False, mark=0):
                selected.append(cand)
        row["selected"] = selected
        row["sel_count"] = int(
            _get(_get(doc, "SelectionManager"), "GetSelectedObjectCount2", -1) or 0
        )
        before_tree, before_surf = _tree(doc), _surface_body_count(doc)
        res = sro.insert_revolved_ref_surface(doc, 360.0, 0, False, 0.0)
        row["returned"] = {
            k: res.get(k)
            for k in ("ok", "returned_is_none", "new_features", "selection_mark")
        }
        row["tree_new"] = [n for n in _tree(doc) if n not in before_tree]
        row["surface_bodies"] = [before_surf, _surface_body_count(doc)]
        row["ok"] = bool(row["tree_new"]) and (row["surface_bodies"][1] or 0) > (
            before_surf or 0
        )
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            _close(sw, doc)
    return row


def case_hole_wizard(sw):
    """★ B2 孔向导：先拉一块板，再用声明式面选择器（`+z`）打高级孔。"""
    row = {"tag": "★ B2 孔向导（HoleWizard5）", "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _get(
            _get(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        P.end_sketch(doc)
        for cand in (
            [n for n in _tree(doc) if n.startswith("\u8349\u56fe")] or ["\u8349\u56fe1"]
        )[::-1]:
            try:
                P.extrude_boss(doc, cand, 0.02)
                break
            except Exception:  # noqa: BLE001
                continue
        before_tree = _tree(doc)
        try:
            rep = hf.create_hole_wizard_at_selection_report(doc, "+z", "M8")
            row["report"] = {k: rep.get(k) for k in list(rep)[:8]}
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        row["tree_new"] = [n for n in _tree(doc) if n not in before_tree]
        row["ok"] = bool(row["tree_new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            _close(sw, doc)
    return row


def case_fully_defined(sw):
    """★ B3 完全定义检查：`ISketch.GetConstrainedStatus()`（★ 只读，官方 `System.int`）。

    ★ 判据：**调得动且回 int**。★ 并**额外试**"加完全定义后值是否变"——
      ★ 若变了 ⇒ 这个读数**有区分度**；★ 若不变 ⇒ **如实写"区分度未证"**（不假装）。
    """
    row = {"tag": "★ B3 完全定义检查（GetConstrainedStatus）", "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _get(
            _get(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.01,
            0.0,
            0.02,
            0.01,
            0.0,
        )
        sk = _get(doc, "GetActiveSketch2")
        if sk is None:
            sk = _get(_get(doc, "SketchManager"), "ActiveSketch")
        row["sketch_obj"] = sk is not None
        if sk is None:
            row["err"] = "取不到活动草图对象（GetActiveSketch2 / ActiveSketch 都 None）"
            return row
        row["status_under_defined"] = int(_get(sk, "GetConstrainedStatus"))
        #: ★ 额外：把矩形钉死（对整张草图加 FIXED 关系）后再读一次
        try:
            segs = list(_get(sk, "GetSketchSegments") or [])
            row["segments"] = len(segs)
            doc.ClearSelection2(True)
            n_sel = 0
            for s in segs:
                try:
                    if P._select_com_object(s, append=True, mark=0):
                        n_sel += 1
                except Exception:  # noqa: BLE001
                    pass
            row["segments_selected"] = n_sel
            if n_sel:
                P.add_sketch_relation(doc, "sgFIXED")
            row["status_after_fixed"] = int(_get(sk, "GetConstrainedStatus"))
            row["status_changed"] = (
                row["status_after_fixed"] != row["status_under_defined"]
            )
        except Exception as exc:  # noqa: BLE001
            row["extra_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        P.end_sketch(doc)
        row["ok"] = isinstance(row.get("status_under_defined"), int)
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            _close(sw, doc)
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u8986\u76d6\u9762\u7f3a\u53e3\u6279 1\uff1a\u65cb\u8f6c\u66f2\u9762 / \u5b54\u5411\u5bfc"
        " / \u5b8c\u5168\u5b9a\u4e49\u68c0\u67e5\uff08\u2605 \u6837\u6761\u66f2\u7ebf**\u4e0d\u6d4b**"
        "\uff1a\u5df2\u6709\u4e0d\u8fbe\u7ed3\u8bba\uff0c\u4e8b\u5b9e 47/68\uff09",
        "spec": "specs/202-user-coverage-gaps",
        "cases": [],
    }
    for fn in (case_revolved, case_hole_wizard, case_fully_defined):
        try:
            ev["cases"].append(fn(sw))
        except Exception as exc:  # noqa: BLE001
            ev["cases"].append(
                {
                    "tag": fn.__name__,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                    "ok": False,
                }
            )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "coverage-gap-batch1-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a\u6210 %d / %d" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-46s ok=%s" % (c.get("tag"), c.get("ok")))
        for k in (
            "tree_new",
            "surface_bodies",
            "status_under_defined",
            "status_after_fixed",
            "status_changed",
            "segments_selected",
        ):
            if k in c:
                print("        %-22s %s" % (k, c[k]))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:160])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
