"""★ 真机：**递归遍历**（含子特征）找 `SurfCut` —— 上一轮留的下一步。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_surfcut_recursive.py
# 定位:   ★ 2026-10-03（轮 526）★ 执行**上一轮留在事实 406 里的那条下一步**：
#
# > ★ **下一步**：用 `iter_features_recursive` 重读一次，看 `SurfCut` 在**子特征**里或不
# 在。
#
#   ★★ **要回答的问题**（★ 事实 406 立的）：
#     · 已知：`InsertCutSurface` 的返回值**确实是一个特征**（`Name` = 「使用曲面切除1」·
#       `GetTypeName2` = `SurfCut`）；
# · 而已知：`FirstFeature` + `GetNextFeature` 那条链**调用前后都是 22 节点**、`SurfCut`
# 不在上面；
#     ⇒ ★ **故本轮问**：★ **它在不在 `GetFirstSubFeature` 那些**子链**里？**
#
#   ★ 两种结果都是信息：
# ⓐ ★ **在子链里** ⇒ ★★ **那是一条**全仓级**的判据修正**（本仓 `feature_names` 不走子特
# 征、
#        而大量「特征树增量」判据都建在它上面）⚠
#     ⓑ ★ **哪儿都没有** ⇒ ★ 那说明它是个**未提交/预览**态的特征（★ 需再确认一次才进树）
#
#   ★ 本探针同时 dump **顶层链**与**递归链**，★ 并对每个节点报**它有没有子特征**。
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 本探针**不求建成** —— ★ 它要的是**递归链上到底有什么**。

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
import scripts.sw_weldment as W  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_surface_features as SF  # noqa: E402


def _mk_solid(doc):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.03,
        -0.03,
        0.0,
        0.03,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _mk_surface(doc, plane="Front Plane"):
    try:
        doc.ClearSelection2(True)
    except Exception:  # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
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
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _recurse(model):
    """★ **递归**遍历（★ 走 `iter_features_recursive`）—— 报每个节点的 名字/类型/层级。"""
    rows = []
    try:
        for feat in W.iter_features_recursive(model):
            row = {}
            for k, m in (("name", "Name"), ("type", "GetTypeName2")):
                try:
                    row[k] = str(C.get_com_member(feat, m) or "")
                except Exception as exc:  # noqa: BLE001
                    row[k] = "ERR %s" % str(exc)[:40]
            try:
                row["has_sub"] = (
                    C.get_com_member(feat, "GetFirstSubFeature") is not None
                )
            except Exception:  # noqa: BLE001
                row["has_sub"] = None
            rows.append(row)
    except Exception as exc:  # noqa: BLE001
        rows.append({"err": "%s: %s" % (type(exc).__name__, str(exc)[:100])})
    return rows


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "**\u9012\u5f52**\u904d\u5386\u627e SurfCut\uff08\u2605 \u4e0a\u4e00\u8f6e\u7559\u7684\u4e0b\u4e00\u6b65\uff09",
        "why": "\u4e8b\u5b9e 406\uff1a\u7279\u5f81\u5bf9\u8c61\u5b58\u5728\u3001\u800c FirstFeature \u94fe\u770b\u4e0d\u89c1",
        "steps": [],
    }
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_solid(doc)
        _mk_surface(doc)
        ev["recurse_before"] = _recurse(doc)
        ev["names_before"] = list(FR.feature_names(doc) or [])
        #: \u2605 \u53ea\u9009\u7b2c\u4e00\u5f20\u66f2\u9762\u9762 + 6 \u53c2
        try:
            doc.ClearSelection2(True)
        except Exception:  # noqa: BLE001
            pass
        from sw_connect import get_com_member as _get
        from sw_connect import out_i4 as _oi4
        from sw_part import _select_com_object as _sel

        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            faces = list(_get(b, "GetFaces") or [])
            if faces:
                _sel(faces[0], append=True, mark=0)
            break
        fm = C.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            ret = C.get_com_member(
                fm, "InsertCutSurface", False, 0, False, True, [], _oi4()
            )
        except Exception as exc:  # noqa: BLE001
            ev["call_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        ev["returned_name"] = None
        ev["returned_type"] = None
        if ret is not None:
            for k, m in (("returned_name", "Name"), ("returned_type", "GetTypeName2")):
                try:
                    ev[k] = str(C.get_com_member(ret, m))
                except Exception as exc:  # noqa: BLE001
                    ev[k] = "ERR %s" % str(exc)[:60]
        ev["recurse_after"] = _recurse(doc)
        ev["names_after"] = list(FR.feature_names(doc) or [])
        #: \u2605 **\u5173\u952e\u5224\u65ad**\uff1a\u9012\u5f52\u94fe\u4e0a\u6709\u6ca1
        #: \u6709 `SurfCut`
        ev["surfcut_in_recurse"] = any(
            str(r.get("type")) == "SurfCut" for r in (ev["recurse_after"] or [])
        )
        ev["surfcut_in_names"] = any(
            "SurfCut" in str(n) for n in (ev["names_after"] or [])
        )
        ev["ok"] = bool(ev["returned_name"])
    except Exception as exc:  # noqa: BLE001
        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    p = R / "output" / "surfcut-recursive-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u8fd4\u56de\uff1a%s / %s"
        % (ev.get("returned_name"), ev.get("returned_type"))
    )
    print(
        "  \u9012\u5f52\u94fe \u524d=%d \u8282\u70b9 \u00b7 \u540e=%d \u8282\u70b9"
        % (len(ev.get("recurse_before") or []), len(ev.get("recurse_after") or []))
    )
    print(
        "  \u2605\u2605 **SurfCut \u5728\u9012\u5f52\u94fe\u91cc\uff1a%s**  \uff08\u5728 feature_names \u91cc\uff1a%s\uff09"
        % (ev.get("surfcut_in_recurse"), ev.get("surfcut_in_names"))
    )
    print("  \u9012\u5f52\u94fe\uff08\u6700\u540e 6 \u4e2a\uff09\uff1a")
    for r in (ev.get("recurse_after") or [])[-6:]:
        print(
            "     %-30s %-18s has_sub=%s"
            % (str(r.get("name"))[:30], str(r.get("type"))[:18], r.get("has_sub"))
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
