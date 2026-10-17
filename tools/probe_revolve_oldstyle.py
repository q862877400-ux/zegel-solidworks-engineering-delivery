"""★ 真机：**旋转曲面**走 `IModelDoc2`（**旧式** 4 参）—— 本仓此前只试过 `IFeatureManager` 那个。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_revolve_oldstyle.py
# 定位:   ★ 2026-10-03（轮 529）★ 回到 **B6/T601（旋转曲面）** —— ★ 而这次**用上刚学到的三条教训**。
#
#   ★★ **为什么值得回来**：
#     · 本仓 `scripts/sw_surface_ref_ops.py::insert_revolved_ref_surface` 走的是
#       **`IFeatureManager.InsertRevolvedRefSurface`（4 参）** —— ★ **新架构**那侧；
#     · 而**类型库**显示 **`IModelDoc2` 上也有一个**同名的
#       `InsertRevolvedRefSurface(Angle, ReverseDir, Angle2, RevType)`（4 参）——
#       ★★ **而本仓**从没试过它** ⚠
#     · 而入库以来「**旧式那一侧成、新架构那侧不成**」已**反复出现**
#       （等距 · 平面区域 · 替换面 · 延伸 · 填充 · 缝合 都走旧式且成）⇒ ★ 值得试 ✓
#
#   ★★ **本轮用上的三条教训**（★ 都是这两轮刚挣来的）：
#     ① ★ **前置要看官方原话的每个名词** —— 官方对旋转曲面逐字是
#        「Creates a **revolved reference surface** by revolving a profile around a **centerline**」
#        ⇒ ★★ **除了轮廓，还要有**中心线**（★ 而本仓旧实现只声明"要选好轮廓"）⚠
#     ② ★ **arity 按类型库数**（★ 含中间 out、不含末尾 `Retval`）—— 事实 397/403
#     ③ ★ **判据不能只看树** —— ★ 事实 406：返回对象可能带名字而树不动
#        ⇒ ★ 故本轮**同时读返回对象的 `Name` / `GetTypeName2`** ✓
#
#   ★ 试的组：
#     ⓐ `IModelDoc2`（旧式）· 轮廓+中心线（★ 带中心线）
#     ⓑ `IModelDoc2`（旧式）· 只有轮廓（★ 对照：看中心线是不是关键）
#     ⓒ `IFeatureManager`（新架构 · 本仓现路）· 轮廓+中心线（★ 对照）
#
#   ⚠ 全程走 `tools/sw_guard.py`；★ 每组**新开一个文档**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 规则 6 + 事实 406）：**树增量** **或** **返回对象带类型名**。

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402
import scripts.sw_feature_readback as FR                              # noqa: E402
import scripts.sw_weldment as W                                       # noqa: E402


def _mk_profile_with_centerline(doc, with_centerline=True):
    """★ 前视面上画**轮廓** + **中心线**（★ 官方原话要 centerline）。"""
    P.start_sketch(doc, plane_name="Front Plane")
    sm = C.get_com_member(doc, "SketchManager")
    #: \u2605 \u4e2d\u5fc3\u7ebf\uff08\u2605 \u6cbf Y \u8f74\uff09
    if with_centerline:
        C.get_com_member(sm, "CreateCenterLine", 0.0, -0.03, 0.0, 0.0, 0.03, 0.0)
    #: \u2605 \u8f6e\u5ed3\uff08\u77e9\u5f62\uff0c\u2605 \u4e0d\u8de8\u4e2d\u5fc3\u7ebf\uff09
    C.get_com_member(sm, "CreateCornerRectangle", 0.005, -0.02, 0.0, 0.02, 0.02, 0.0)
    P.end_sketch(doc)


def _pick_sketch(doc, name, mark, append=False):
    ext = C.get_com_member(doc, "Extension")
    picked = None
    for cand in P._get_sketch_name_candidates(name):
        try:
            if P._select_by_id(ext, cand, "SKETCH", append=append, mark=mark):
                picked = cand
                break
        except Exception:                                                 # noqa: BLE001
            continue
    return picked


def _tree(model):
    """★ 树（顶层 + 递归），★ 事实 406：两套都看。"""
    top = list(FR.feature_names(model) or [])
    types = []
    try:
        for f in W.iter_features_recursive(model):
            try:
                types.append(str(C.get_com_member(f, "GetTypeName2") or ""))
            except Exception:                                             # noqa: BLE001
                pass
    except Exception:                                                     # noqa: BLE001
        pass
    return {"names": top, "types": types}


def _one(sw, tag, entry, with_centerline):
    row = {"tag": tag, "entry": entry, "with_centerline": with_centerline, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_profile_with_centerline(doc, with_centerline)
        names = [n for n in (FR.feature_names(doc) or [])
                 if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
        sk = names[-1] if names else "\u8349\u56fe1"
        try:
            doc.ClearSelection2(True)
        except Exception:                                                 # noqa: BLE001
            pass
        row["picked"] = _pick_sketch(doc, sk, 0)
        try:
            row["sel"] = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                              "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            row["sel"] = -1
        before = _tree(doc)
        try:
            if entry == "modeldoc":
                ret = C.get_com_member(doc, "InsertRevolvedRefSurface",
                                       math.radians(360.0), False, 0.0, 0)
            else:
                fm = C.get_com_member(doc, "FeatureManager")
                ret = C.get_com_member(fm, "InsertRevolvedRefSurface",
                                       math.radians(360.0), False, 0.0, 0)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(C.get_com_member(ret, m))
                    except Exception:                                     # noqa: BLE001
                        pass
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _tree(doc)
        row["new"] = [n for n in (after.get("names") or []) if n not in (before.get("names") or [])]
        row["new_types"] = [t for t in (after.get("types") or []) if t not in (before.get("types") or [])]
        #: \u2605\u2605 \u5224\u636e\uff08\u4e8b\u5b9e 406\uff09\uff1a\u6811**\u6216**\u8fd4\u56de\u5bf9\u8c61\u5e26\u7c7b\u578b\u540d
        row["ok"] = bool(row["new"] or row["new_types"] or row.get("ret_type"))
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
          "_": "\u65cb\u8f6c\u66f2\u9762\uff1a`IModelDoc2`\uff08**\u65e7\u5f0f**\uff09vs `IFeatureManager`\uff08\u65b0\u67b6\u6784\uff09",
          "why": "\u5b98\u65b9\u539f\u8bdd\u8981 **centerline**\uff1b\u800c\u672c\u4ed3\u65e7\u5b9e\u73b0\u53ea\u58f0\u660e\u201c\u8981\u9009\u597d\u8f6e\u5ed3\u201d",
          "cases": []}
    for tag, entry, cl in (("\u2605 IModelDoc2\uff08\u65e7\u5f0f\uff09+ \u4e2d\u5fc3\u7ebf", "modeldoc", True),
                           ("IModelDoc2\uff08\u65e7\u5f0f\uff09\u00b7 \u65e0\u4e2d\u5fc3\u7ebf", "modeldoc", False),
                           ("\u5bf9\u7167\uff1aIFeatureManager\uff08\u65b0\u67b6\u6784\uff09+ \u4e2d\u5fc3\u7ebf",
                            "featuremanager", True)):
        ev["cases"].append(_one(sw, tag, entry, cl))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "revolve_oldstyle_works" if ev["passed"] else "all_revolve_fail"
    p = R / "output" / "revolve-oldstyle-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-38s ok=%-6s \u9009\u4e2d=%-3s \u56de=%-9s \u540d=%s \u578b=%s" % (
            c.get("tag"), c.get("ok"), c.get("sel"), c.get("returned"),
            c.get("ret_name"), c.get("ret_type")))
        print("        new=%s new_types=%s" % (c.get("new"), c.get("new_types")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
