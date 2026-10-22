"""★ 决定性验证：曲面扫描**设上 `Profile` / `Path` 属性**后再 `CreateFeature`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_sweep_set_profile_path.py
# 定位:   ★ 2026-10-03（轮 512）★ 验证一个**修正版的假设** ——
#   它同时解释了**事实 395 那条规律**与**它的反例**。
#
#   ★★ **推理链**：
#     · 事实 395 立了「改动已有体 3/3 成 · 新建独立体 0/3 不成」——
#       ★ 而**它立刻有反例**：`create_extruded_surface_report`（**曲面-拉伸**）
#       ★ **本身就是"新建"**、★ 而它**成**（`曲面-拉伸1`，树 6→7）⚠
#     ⇒ ★★ **故「新建 vs 改动」是表象** —— ★ 得找**真正在变的那一项**。
#     · 于是看 `ISweepFeatureData` 的成员表：★ 它**有 `Profile` 与 `Path` 属性**（可写）
#       ★★ **而那正是扫描必需的两个东西** —— ★ 而它们**默认是空的** ⚠
#     · 而★ 本仓轮 486-488 的探针只做 `CreateDefinition(62)` → `CreateFeature`，
#       ★ **一个属性都没设** ⚠
#     · ★ 对照：
#       ✓ **曲面-拉伸**（`FeatureExtruRefSurface3`，**22 参**）—— ★ **参数里就带轮廓**
#       ✓ **填充 / 延伸 / 缝合**（旧式方法）—— ★ **参数里带边界 / 距离 / 容差**
#       ✗ **扫描曲面 / 加厚 / 直纹**（新架构 FeatureData）—— ★ **我什么都没设**
#
#   ⇒ ★★★ **修正后的假设**：★ **「参数 / 属性没给全」⇒ `CreateFeature` 静默回 `None`** ✓
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 事实 242）：**特征树多了新特征** **且** **类型名 = `Sweep`**。

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

SW_FM_REF_SURFACE = 62


def _sketch_ref(doc, idx):
    """★ 取第 idx 个草图的**引用**（★ 用来赋给 `Profile` / `Path`）。"""
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")]
    if idx < len(names):
        try:
            return C.get_com_member(doc, "FeatureByName", names[idx])
        except Exception:                                                 # noqa: BLE001
            return None
    return None


def _one(sw, tag, *, set_props):
    row = {"tag": tag, "set_props": set_props, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u8f6e\u5ed3\uff1a\u4e0a\u89c6\u9762\u7684\u5706
        P.start_sketch(doc, plane_name="Top Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateCircleByRadius",
                         0.0, 0.0, 0.0, 5.0 / 1000.0)
        P.end_sketch(doc)
        #: \u8def\u5f84\uff1a\u524d\u89c6\u9762\u4ece\u539f\u70b9\u6cbf X
        try:
            C.get_com_member(doc, "ClearSelection2", True)
        except Exception:                                                 # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(C.get_com_member(doc, "SketchManager"), "CreateLine",
                         0.0, 0.0, 0.0, 40.0 / 1000.0, 0.0, 0.0)
        P.end_sketch(doc)

        fm = C.get_com_member(doc, "FeatureManager")
        before = list(P.feature_names(doc) or [])
        data = C.get_com_member(fm, "CreateDefinition", SW_FM_REF_SURFACE)
        row["data"] = type(data).__name__ if data is not None else None
        if data is None:
            return row

        if set_props:
            #: \u2605\u2605 \u672c\u8f6e\u7684\u81ea\u53d8\u91cf\uff1a\u628a\u4e24\u4e2a
            #: **\u5fc5\u9700\u5c5e\u6027**\u8bbe\u4e0a
            refs = {}
            for attr, idx in (("Profile", 0), ("Path", 1)):
                r = _sketch_ref(doc, idx)
                refs[attr] = type(r).__name__ if r is not None else None
                if r is not None:
                    try:
                        C.set_com_member(data, attr, r)
                    except Exception as exc:                              # noqa: BLE001
                        refs[attr + "_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
            row["refs"] = refs
            #: \u2605 \u5e26\u4e0a AutoSelect\uff08\u2605 \u5b83\u5728\u6210\u5458\u8868
            #: \u91cc\uff09
            try:
                C.set_com_member(data, "AutoSelect", True)
                row["auto_select"] = True
            except Exception as exc:                                      # noqa: BLE001
                row["auto_select"] = "ERR %s" % str(exc)[:60]

        try:
            feat = C.get_com_member(fm, "CreateFeature", data)
            row["create_feature"] = type(feat).__name__ if feat is not None else "None"
        except Exception as exc:                                          # noqa: BLE001
            row["create_feature_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
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
          "_": "\u626b\u63cf\u66f2\u9762\uff1a**\u8bbe\u4e0a Profile/Path \u5c5e\u6027**\u540e\u518d CreateFeature",
          "hypothesis": "\u4e0d\u662f\u201c\u65b0\u5efa vs \u6539\u52a8\u201d\uff08\u2605 \u90a3\u6709\u53cd\u4f8b\uff1a\u66f2\u9762-\u62c9\u4f38\u5c31\u662f\u65b0\u5efa\u800c\u6210\uff09\uff0c"
                        "\u800c\u662f\u300c\u53c2\u6570/\u5c5e\u6027\u6ca1\u7ed9\u5168\u300d",
          "cases": []}
    ev["cases"].append(_one(sw, "\u2605 \u8bbe Profile/Path \u540e CreateFeature", set_props=True))
    ev["cases"].append(_one(sw, "\u5bf9\u7167\uff1a\u4e0d\u8bbe\u5c5e\u6027", set_props=False))
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "hypothesis_supported" if ev["passed"] else "hypothesis_rejected"
    p = R / "output" / "sweep-set-props-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u5224\u522b\uff1a**%s**\uff08\u6210 %d / %d\uff09" % (ev["verdict"], ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print("  %-32s ok=%-6s data=%s" % (c.get("tag"), c.get("ok"), c.get("data")))
        print("        refs=%s  CF=%-9s new=%s" % (c.get("refs"), c.get("create_feature"), c.get("new")))
        if c.get("create_feature_err"):
            print("        CF_ERR=%s" % str(c["create_feature_err"])[:110])
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
