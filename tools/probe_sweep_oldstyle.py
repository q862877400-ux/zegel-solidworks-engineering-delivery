"""★ 真机：`IModelDoc2.InsertSweepRefSurface2`（**旧式扫描曲面**）—— 能否推翻「到不了」。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_sweep_oldstyle.py
# 定位:   ★ 2026-10-03（轮 518）★ 沿**已验证的方向**（「旧式方法那侧是成的」—— 事实 39
#           5/398）继续。
#
#   ★★ **本轮从类型库 dump 里发现的事**（★ 而它直接挑战一条既有结论）：
#     `IModelDoc2` 上有一整族**旧式曲面入口** ——
#     ```
#     InsertSweepRefSurface2    arity=6  (Propagate, TwistCtrlOption, KeepTangency, ForceNonRational,
#                                          StartMatchingType, EndMatchingType)   ← ★ T602 扫描曲面
#     InsertRevolvedRefSurface  arity=4  (Angle, ReverseDir, Angle2, RevType)    ← ★ T601 旋转曲面
#     PreTrimSurface            arity=1  (BMutualTrimIn)                         ← ★ T607 剪裁（两段式）
#     PostTrimSurface           arity=1  (BSewSurfaceIn)
#     InsertRadiateSurface      arity=3  (Distance, FlipDir, TangentPropagate)   ← 辐射曲面
#     ```
#
#   ★★ **为什么要试**：本仓此前对**扫描曲面**下过「到不了」的结论 ——
#     依据是**新架构**那条路（`CreateDefinition(swFmRefSurface = 62)` → `CreateFeature`）
#     在真机上**静默回 `None`**（★ 事实 391/393/396 那一串否证）。
#     ⚠ 而**从没试过 `IModelDoc2` 上的旧式入口** —— ★ 而旧式那一侧**已经成了 3 条**
#     （等距 `InsertOffsetSurface` · 平面区域 `InsertPlanarRefSurface` · 替换面 `InsertFeatureReplaceFace`）。
#   ⇒ ★★★ **故本探针要问**：★ **扫描曲面的旧式入口成不成？**
#     · ★ 若**成** ⇒ ★★ **「扫描曲面到不了」这条结论要按事实 53 的口径修正**（★ 那是**推翻**）
#     · ★ 若**不成** ⇒ ★ 那 6 条否证之上再添一条**更强的**（★ 旧式侧也不成）
#
#   官方：`IModelDoc2.InsertSweepRefSurface2` 标 **Obsolete. Superseded by
#     `IFeatureManager::InsertProtrusionSwept3`** ⇒ ★ 而★ 本仓已有多处「废弃入口反而更顺」的反例。
#   ★ 前置：★ 与实体扫描同款 —— **轮廓 mark=1 · 路径 mark=4**（★ 事实 384 的正解：`SelectByID2` 带 mark）。
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 事实 242）：**特征树多了新特征**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                    # noqa: E402
from scripts import sw_part as P                                       # noqa: E402


def _mk_profile_path(doc):
    """★ 轮廓（上视面圆）+ 路径（前视面直线，★ 起点在 Z=0 上 —— ★ 方向 1 的硬约束）。"""
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                     0.0, 0.0, 0.0, 5.0 / 1000.0)
    P.end_sketch(doc)
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    P.start_sketch(doc, plane_name="Front Plane")
    C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                     0.0, 0.0, 0.0, 40.0 / 1000.0, 0.0, 0.0)
    P.end_sketch(doc)


def _pick(doc, marks=(1, 4)):
    """★ 轮廓 mark=1 · 路径 mark=4（★ 事实 384：`SelectByID2` 带 mark 是正解）。"""
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    ext = C.get_com_member(doc, "Extension")
    picked = {}
    try:
        doc.ClearSelection2(True)
    except Exception:                                                     # noqa: BLE001
        pass
    for i, (label, mark) in enumerate((("profile", marks[0]), ("path", marks[1]))):
        if i >= len(names):
            continue
        for cand in P._get_sketch_name_candidates(names[i]):
            try:
                if P._select_by_id(ext, cand, "SKETCH", append=bool(picked), mark=mark):
                    picked[label] = (cand, mark)
                    break
            except Exception:                                             # noqa: BLE001
                pass
    per = {}
    for m in marks:
        try:
            per[str(m)] = int(C.get_com_member(C.get_com_member(doc, "SelectionManager"),
                                               "GetSelectedObjectCount2", m))
        except Exception:                                                 # noqa: BLE001
            per[str(m)] = -1
    return picked, per


def _one(sw, tag, call):
    """★ `call(doc)` 里做实际调用；★ 先准备好轮廓+路径与选区。"""
    row = {"tag": tag, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        _mk_profile_path(doc)
        picked, per = _pick(doc)
        row["picked"] = picked
        row["sel_by_mark"] = per
        before = list(P.feature_names(doc) or [])
        try:
            ret = call(doc)
            row["returned"] = type(ret).__name__ if ret is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
            row["code"] = getattr(exc, "args", (None,))[0]
        after = list(P.feature_names(doc) or [])
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
          "_": "\u65e7\u5f0f\u626b\u63cf\u66f2\u9762\uff1a`IModelDoc2.InsertSweepRefSurface2`",
          "why": "\u65b0\u67b6\u6784\u90a3\u6761\u8def\uff0862\uff09\u9759\u9ed8\u56de None\uff1b\u800c\u65e7\u5f0f\u4fa7\u5df2\u6210 3 \u6761 "
                 "\u21d2 \u95ee\uff1a\u626b\u63cf\u66f2\u9762\u7684**\u65e7\u5f0f**\u5165\u53e3\u6210\u4e0d\u6210\uff1f",
          "cases": []}
    #: \u2605 \u2460 \u5168\u90e8\u9ed8\u8ba4\u53c2\uff08\u2605 \u6700\u5c0f\u5e72\u9884\uff09
    ev["cases"].append(_one(sw, "InsertSweepRefSurface2 \u9ed8\u8ba4\u53c2",
                            lambda d: C.get_com_member(d, "InsertSweepRefSurface2",
                                                       True, 0, True, False, 0, 0)))
    #: \u2605 \u2461 \u53ea\u4f20 4 \u53c2\uff08\u2605 \u65e7\u4ee3\u7b7e\u540d\u7684\u5f62\u72b6\uff09
    ev["cases"].append(_one(sw, "InsertSweepRefSurface\uff084 \u53c2\uff09",
                            lambda d: C.get_com_member(d, "InsertSweepRefSurface",
                                                       True, 0, True, False)))
    #: \u2605 \u2462 \u65b0\u67b6\u6784\u5bf9\u7167\uff0862\uff09
    def _newarch(d):
        fm = C.get_com_member(d, "FeatureManager")
        data = C.get_com_member(fm, "CreateDefinition", 62)
        return C.get_com_member(fm, "CreateFeature", data) if data is not None else None
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u65b0\u67b6\u6784 62", _newarch))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "oldstyle_sweep_works" if ev["passed"] else "oldstyle_sweep_also_fails"
    p = R / "output" / "sweep-oldstyle-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-34s ok=%-6s sel=%s \u56de=%s new=%s" % (c.get("tag"), c.get("ok"),
                                                          c.get("sel_by_mark"), c.get("returned"), c.get("new")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
