"""★ 真机：`InsertCutSurface` 的 **`Bodies` 传"真的体数组"**（★ 而非空数组）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_cut_surface_real_bodies.py
# 定位:   ★ 2026-10-03（轮 528）★ 试一个**从没动过的变量**。
#
#   ★★ **官方对 `Bodies` 的说法**（`C:\\swapi\\types\\IFeatureManager\\InsertCutSurface.md` 逐字）：
#     · 「Array of specific **bodies** that intersect with the cut」—— ★ 且分两种情况：
#       `UseFeatScope = true` / `UseAutoSelect = false` 时**用传给 `Bodies` 的体**；
#     · 「**Empty array indicating to cut all bodies that intersect with the cut**」
#   ⇒ ★★ **故本仓一直传的 `[]` 是"切所有"那条路** —— ★ 而**从没试过"传真的体数组"** ⚠
#
#   ★ 为什么值得试（★ 有据的推理）：事实 407 说那个特征对象**浮在树外**
#     （递归看不见 · `EditRebuild3` 也不让它进 · 而 `whats_wrong = 0`）。
#     ⇒ ★★ **一个还没排除的解释**：★ **它没"认领到体"** ——
#       ★ 而 `Bodies` 正是"要切哪些体"的那个参数 ⇒ ★ **传真的体 + `UseFeatScope=True`** 值得试 ✓
#     ★ 这也**对得上官方那两条分支**：`UseFeatScope=True` 走"用 `Bodies`"，★ 而我一直是
#       `UseFeatScope=False`（★ 那就落到"自动"那条，★ 而**空数组**又叠了一层模糊）。
#
#   ★ 试的组（★ 只动 `Bodies` 与那两个布尔）：
#     ⓐ `[]` + `use_feat_scope=False` + `use_auto_select=True`（★ 前三轮那组 —— 对照）
#     ⓑ **`[实体体]`** + `use_feat_scope=True` + `use_auto_select=False`
#     ⓒ **`[曲面体, 实体体]`** + `use_feat_scope=True` + `use_auto_select=False`
#     ⓓ `[实体体]` + `use_feat_scope=False` + `use_auto_select=False`
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6）：**特征树多了新特征**；★ 并**同时看返回对象的 `Name`**
#   （★ 事实 405/406：即使树不动，返回对象也可能带着名字）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from win32com.client import VARIANT as _V                            # noqa: E402
import pythoncom                                                      # noqa: E402
from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
from scripts import sw_surface_features as SF                         # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402


def _mk_solid(doc):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.03, -0.03, 0.0, 0.03, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, 0.02)
            return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _mk_surface(doc, plane="Front Plane"):
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name=plane)
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCornerRectangle",
                     -0.02, -0.02, 0.0, 0.02, 0.02, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    for cand in (names[-1] if names else "\u8349\u56fe1", "\u8349\u56fe1", "Sketch1"):
        try:
            if SF.create_extruded_surface_report(doc, 30.0, sketch_name=cand).get("ok"):
                return True
        except Exception:                                                 # noqa: BLE001
            continue
    return False


def _one(sw, tag, bodies_kind, feat_scope, auto_select):
    row = {"tag": tag, "bodies_kind": bodies_kind,
           "use_feat_scope": feat_scope, "use_auto_select": auto_select, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_solid(doc)
        _mk_surface(doc)
        from sw_connect import get_com_member as _get, out_i4 as _oi4
        from sw_part import _select_com_object as _sel
        #: \u2605 \u53ea\u9009\u7b2c\u4e00\u5f20\u66f2\u9762\u9762\uff08\u2605 \u4e8b\u5b9e 405\uff1a\u8fd9\u79cd\u9009\u6cd5\u56de\u5bf9\u8c61\uff09
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        for b in list(_get(doc, "GetBodies2", 1, True) or []):
            faces = list(_get(b, "GetFaces") or [])
            if faces:
                _sel(faces[0], append=True, mark=0)
            break
        #: \u2605 \u53d6\u4f53
        solid_bodies = list(_get(doc, "GetBodies2", 0, True) or [])
        surf_bodies = list(_get(doc, "GetBodies2", 1, True) or [])
        if bodies_kind == "empty":
            bodies = []
        elif bodies_kind == "solid":
            bodies = solid_bodies[:1]
        elif bodies_kind == "both":
            bodies = (surf_bodies[:1] + solid_bodies[:1])
        else:
            bodies = []
        row["n_solid"] = len(solid_bodies)
        row["n_surface"] = len(surf_bodies)
        row["n_bodies_passed"] = len(bodies)
        before = list(FR.feature_names(doc) or [])
        fm = C.get_com_member(doc, "FeatureManager")
        ret = None
        try:
            ret = C.get_com_member(fm, "InsertCutSurface", False, 0, bool(feat_scope),
                                   bool(auto_select), bodies, _oi4())
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                try:
                    row["ret_name"] = str(C.get_com_member(ret, "Name"))
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(FR.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["ok"] = bool(row["new"])
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "InsertCutSurface\uff1a**Bodies \u4f20\u771f\u7684\u4f53\u6570\u7ec4**\uff08\u2605 \u800c\u975e\u7a7a\u6570\u7ec4\uff09",
          "why": "\u5b98\u65b9\uff1a`Bodies` = \u201cArray of specific bodies\u201d\uff1b\u7a7a\u6570\u7ec4 = \u201ccut all bodies\u201d "
                 "\u21d2 \u672c\u4ed3\u4e00\u76f4\u4f20\u7a7a\u6570\u7ec4\uff0c**\u4ece\u6ca1\u8bd5\u8fc7\u4f20\u771f\u7684\u4f53**",
          "cases": []}
    for tag, kind, fs, asel in (("[] \u00b7 scope=F \u00b7 auto=T\uff08\u2605 \u5bf9\u7167\uff09", "empty", False, True),
                                ("[**\u5b9e\u4f53**] \u00b7 scope=T \u00b7 auto=F", "solid", True, False),
                                ("[**\u66f2\u9762+\u5b9e\u4f53**] \u00b7 scope=T \u00b7 auto=F", "both", True, False),
                                ("[\u5b9e\u4f53] \u00b7 scope=F \u00b7 auto=F", "solid", False, False)):
        ev["cases"].append(_one(sw, tag, kind, fs, asel))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["named"] = sum(1 for c in ev["cases"] if c.get("ret_name"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "real_bodies_works" if ev["passed"] else (
        "no_feature_but_object_named" if ev["named"] else "all_fail")
    p = R / "output" / "cut-surface-real-bodies-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u5efa\u6210 %d \u00b7 \u6709\u540d\u5b57 %d / %d\uff09" % (
        ev["verdict"], ev["passed"], ev["named"], ev["total"]))
    for c in ev["cases"]:
        print("  %-36s ok=%-6s \u4f20\u4e86 %s \u4e2a\u4f53 \u00b7 \u56de=%-9s \u540d=%s" % (
            c.get("tag"), c.get("ok"), c.get("n_bodies_passed"), c.get("returned"), c.get("ret_name")))
        print("        new=%s" % (c.get("new"),))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
