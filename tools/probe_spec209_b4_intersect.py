"""★ 真机：规格 209 · B4-3（idx 181 intersect）—— ★ 唯一要验的是布尔 SafeArray 的包装。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b4_intersect.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-3**：外部项目 idx **181 `intersect`**。
#   ★★ 裁决书逐字：「真名是**两步** `PreIntersect2` → `PostIntersect`；RegionType 三值表 +
#   示例 mark=0 + 排除数组形状齐备；★ 读侧 `IIntersectFeatureData` 零指针族 ⇒
#   ★ **唯一要实测的只有 `System.object` 布尔 SafeArray 的包装**」✓
#   ★★ 判据（规则 6，全回读）：
#     ```
#     ① PreIntersect2 回的**体数组长度**（★ 它回 System.object）
#     ② 特征树增量 + 新特征名（★ PostIntersect 回的 IFeature **不当判据**）
#     ③ IIntersectFeatureData::GetIntersectionsCount()（零参回 int）
#     ④ 两种 region_type（intersecting / both）+ 一个"排除某个体"的变体
#     ```
# 官方依据: `C:\\swapi\\types\\IFeatureManager\\{PreIntersect2,PostIntersect}.md` ·
#   `C:\\swapi\\types\\IIntersectFeatureData\\*.md` ·
#   ★★ `C:\\swapi\\examples\\Create_Intersect_Feature_Example_VB.md`（**调用序**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-intersect.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_boolean_ops as BO

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "规格 209 · B4-3 intersect（两步 PreIntersect2 → PostIntersect）",
          "judge": "体数组长度 + 特征树增量 + GetIntersectionsCount（★ 不看返回值）",
          "runs": [], "verdict": {}}
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    def _features(doc):
        rows, f, n = [], get_com_member(doc, "FirstFeature"), 0
        while f is not None and n < 4096:
            rows.append((str(safe_get_com_member(f, "Name") or ""),
                         str(safe_get_com_member(f, "GetTypeName2") or "")))
            f = get_com_member(f, "GetNextFeature")
            n += 1
        return rows

    def _box():
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with P.sketch(doc, "Front Plane") as sk:
            P.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        P.end_sketch(doc)
        P.extrude_boss(doc, "草图1", 20.0)
        return doc

    for rt in ("intersecting", "intersecting_and_internal"):
        for excl in ("", "0"):
            row = {"region_type": rt, "exclude": excl}
            try:
                doc = _box()
                feats = _features(doc)
                body_feat = next((n for n, t in feats if "Extru" in t or "拉伸" in n), "")
                plane = next((n for n, t in feats if t == "RefPlane" and n), "")
                row["body_feature"] = body_feat
                row["plane"] = plane
                row["sel_spec"] = "SOLIDBODY:%s,PLANE:%s" % (body_feat, plane)
                r = BO.create_intersect(doc, row["sel_spec"], region_type=rt, exclude=excl)
                row.update({k: r.get(k) for k in
                            ("ok", "selection_count", "pre_bodies", "exclude_array_len",
                             "exclude_flagged", "feature", "feature_type", "tree_before",
                             "tree_after", "new_features", "intersections_count", "error",
                             "note")})
                row["feature_names_after"] = [n for n, _t in _features(doc)][-4:]
                _close(doc)
                print("  rt=%-28s excl=%-2s ok=%-5s pre=%s new=%r inter=%s"
                      % (rt, excl or "-", r.get("ok"), r.get("pre_bodies"),
                         r.get("new_features"), r.get("intersections_count")))
            except Exception as exc:                           # noqa: BLE001
                row["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
                print("  rt=%-28s excl=%-2s FATAL %s" % (rt, excl or "-", str(exc)[:90]))
            ev["runs"].append(row)

    got = [r for r in ev["runs"] if r.get("ok")]
    ev["verdict"] = {
        "any_built": bool(got),
        "array_wrapping_works": any(r.get("pre_bodies") for r in ev["runs"]),
        "intersections_count_read": any(r.get("intersections_count") for r in ev["runs"]),
        "built_runs": [{"region_type": r["region_type"], "exclude": r["exclude"],
                        "feature": r.get("feature"), "new": r.get("new_features")} for r in got],
    }
    print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False)[:300])

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
