"""★ 真机：核两条"**做了但没登记**"的 —— 投影分割线 · 侧影实体。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_splitline_and_silhouette.py
# 定位:   ★ 2026-10-03（轮 552）★ 用「**查本仓调过没有**」那条方法论扫了剩下 27 条可攻
#           关，
#     ★ 而★ 扫出**两条已被调用过**（★ 其余 25 条真的没调过）：
# · `特征下拉 · 曲线-分割线` → 本仓 `sw_curve_and_split.py:118` 调了 `InsertSplitLinePro
# ject` ✓
#       · `草图编辑 · 侧影实体`   → 本仓 `sw_sketch_edit.py:210` 调了 `SketchUseEdge3` ✓
# ★★ **而能力条目 `curve_and_split` 的 label 自己写着**：「…（★ **分割线两条未登记**）」
#  ⚠
#     ⇒ ★ **故它们不是"没做"、而是"做了没登记"** ⇒ ★ **本探针真机核一次，再补登记** ✓
#
#   ★ 依据（★ 本仓既有 docstring 已记）：
#     · `IModelDoc2.InsertSplitLineProject(IsDirectional, FlipDir)` —— **2 参**、回 `void`
#       （★ 类型库 arity 已核；★ 判据只能用**树增量**）
#     · `ISketchManager.SketchUseEdge3(Chain, InnerLoops)` —— 三源互证（★ 反射 + swapi）
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**树增量**（★ 两条的返回值都是 `void`/`bool`，判据只能是树）。

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
from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402


def _mk_solid(doc):
    p_.start_sketch(doc, plane_name="Top Plane")
    c_.get_com_member(
        c_.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    p_.end_sketch(doc)
    names = [
        n
        for n in (p_.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            p_.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _case_silhouette(sw):
    """★ **侧影实体**：把实体的侧影边投进草图（★ `SketchUseEdge3`）。"""
    row = {
        "tag": "\u2605 \u4fa7\u5f71\u5b9e\u4f53\uff08SketchUseEdge3\uff09",
        "ok": False,
    }
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        _mk_solid(doc)
        #: \u2605 \u5148\u9009\u4e00\u4e2a\u9762\uff08\u2605 \u4fa7\u5f71\u8981\u6709\u6
        #: 5b9\u5411\uff09
        from sw_connect import get_com_member as _get
        from sw_part import _select_com_object as _sel

        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        for b in list(_get(doc, "GetBodies2", 0, True) or []):
            for f in list(_get(b, "GetFaces") or [])[:1]:
                _sel(f, append=True, mark=0)
            break
        before = list(fr.feature_names(doc) or [])
        try:
            p_.start_sketch(doc, plane_name="Right Plane")
            skm = c_.get_com_member(doc, "SketchManager")
            got = c_.get_com_member(skm, "SketchUseEdge3", False, False)
            row["returned"] = str(got)
            row["segments"] = len(
                list(
                    c_.get_com_member(
                        c_.get_com_member(doc, "GetActiveSketch2"), "GetSketchSegments"
                    )
                    or []
                )
            )
            p_.end_sketch(doc)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        #: \u2605 \u5224\u636e\uff1a**\u8349\u56fe\u91cc\u771f\u7684\u6709\u4e86\u7ebf\u
        #: 6bb5**\uff08\u2605 \u6216\u6811\u589e\u91cf\uff09
        row["ok"] = bool(row.get("segments") or row["new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def _case_splitline(sw):
    """★ **投影分割线**：`IModelDoc2.InsertSplitLineProject(False, False)`（★ 2 参 · 回 void）。"""
    row = {
        "tag": "\u2605 \u6295\u5f71\u5206\u5272\u7ebf\uff08InsertSplitLineProject\uff09",
        "ok": False,
    }
    doc = None
    try:
        doc = c_.new_document(sw, "part")
        _mk_solid(doc)
        #: \u2605 \u524d\u89c6\u9762\u4e0a\u753b\u4e00\u4e2a\u8349\u56fe\uff08\u2605 \u6
        #: 295\u5f71\u5206\u5272\u7ebf\u7684\u8f6e\u5ed3\uff09
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        p_.start_sketch(doc, plane_name="Front Plane")
        c_.get_com_member(
            c_.get_com_member(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.01,
            -0.005,
            0.0,
            0.01,
            0.015,
            0.0,
        )
        p_.end_sketch(doc)
        names = [
            n
            for n in (p_.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        ext = c_.get_com_member(doc, "Extension")
        picked = False
        if names:
            for cand in p_._get_sketch_name_candidates(names[-1]):
                try:
                    if p_._select_by_id(ext, cand, "SKETCH", append=False, mark=0):
                        picked = True
                        break
                except Exception:  # noqa: BLE001
                    continue
        row["picked_sketch"] = picked
        before = list(fr.feature_names(doc) or [])
        try:
            c_.get_com_member(doc, "InsertSplitLineProject", False, False)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(fr.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
    finally:
        if doc is not None:
            try:
                t = str(c_.get_com_member(doc, "GetTitle") or "")
                if t:
                    c_.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u6838\u4e24\u6761\u201c\u505a\u4e86\u4f46\u6ca1\u767b\u8bb0\u201d\u7684\uff1a\u6295\u5f71\u5206\u5272\u7ebf \u00b7 \u4fa7\u5f71\u5b9e\u4f53",
        "why": "\u626b\u5269\u4e0b 27 \u6761\u53ef\u653b\u5173\u65f6\uff0c\u53d1\u73b0\u8fd9\u4e24\u6761\u7684 API **\u672c\u4ed3\u5df2\u7ecf\u8c03\u8fc7**",
        "cases": [],
    }
    ev["cases"].append(_case_silhouette(sw))
    ev["cases"].append(_case_splitline(sw))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "both_confirmed" if ev["passed"] == ev["total"] else "partial"
    p = R / "output" / "splitline-and-silhouette-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09"
        % (ev["verdict"], ev["passed"], ev["total"])
    )
    for c in ev["cases"]:
        print("  %-40s ok=%-6s" % (c.get("tag"), c.get("ok")))
        print(
            "        \u65b0\u589e=%s \u7ebf\u6bb5=%s \u9009\u4e2d=%s \u56de=%s"
            % (
                c.get("new"),
                c.get("segments"),
                c.get("picked_sketch"),
                c.get("returned"),
            )
        )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
