"""★ 探针：`InsertUntrimSurface2`（取消剪裁）—— ★ 三条**必然失败**的负例 + 官方前置的实证。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B2-1 的真机探针）
# 文件:   tools/probe_spec211_untrim.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-1**「剪裁曲面 · 取消剪裁」。
#   ★★ 先说清**边界**（★ 如实，不夸大）：
#     · ★ **"剪裁曲面"本身仓里已有**（★ `trim_surface_report` + `cut_surface_report`，
#       ★ 走 `PreTrimSurface` + `PostTrimSurface` 两段式）✓ —— ★ **本批补的是"取消剪裁"** ✓
#     · ★★ **正例（曲面零件上真的取消剪裁）本轮**未做** ✗ —— ★ 理由：★ 它需要
#       「**先建出被剪裁的曲面**」那一条链（★ 曲面 → 相交 → 剪裁），★ 而那**不是本批的范围** ✓
#       ★ 故本探针**只做负例** + ★ **把官方两条前置实证掉** ✓
# 判据:   ★★ 三条负例（★ 全部"必然失败"，★ 且**都不需要复杂前置** ✓）：
# ★ ① **枚举越界**（`face_untrim_type=9`）⇒ ★ 不在官方 `swFaceUntrimType_e` ⇒ **必然非法
# ** ✓
#     ★ ② **枚举越界**（`edge_untrim_type=9`）⇒ ★ 同上（★ `swEdgeUntrimType_e`）✓
#     ★ ③ ★★★ **普通零件上"能选到面"却调** ⇒ ★ 官方 `## Remarks` 逐字「**is valid only for
#       surface parts**」⇒ ★★ **特征树不该有新特征** ✓ —— ★ 这是**官方那条前置的实证** ✓
# ★ 另记：★ `BTrimOppositeSide` **只在 `BMerge=False` 时有意义**（★ 官方逐字）⇒ ★ 报告里
# 如实标 ✓
# 官方依据: `C:\swapi\types\IFeatureManager\InsertUntrimSurface2.md`（签名 + Parameters
#           + Remarks 两条）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}


def main() -> int:
    import sw_connect
    import tool_caller
    import sw_surface_features as sf

    out = {
        "official": "IFeatureManager.InsertUntrimSurface2",
        "scope_note": (
            "★ 本批补的是「取消剪裁」；「剪裁曲面」本身仓里已有"
            "（trim_surface_report + cut_surface_report）✓"
        ),
        "positive_case_note": (
            "★ 正例（曲面零件上真的取消剪裁）**本轮未做** —— 它需要"
            "「先建出被剪裁的曲面」那一条链，★ 不在本批范围 ✓"
        ),
    }

    #: ── ① / ② 枚举越界（★ 纯 Python ⇒ 必然失败 ✓）───────────────────────
    neg = {}
    r = sf.untrim_surface_report(object(), face_untrim_type=9)
    neg["face_type_9"] = (
        "✓ 拒：%s" % str(r.get("error"))[:80] if not r["ok"] else "★★ 没拒"
    )
    r = sf.untrim_surface_report(object(), edge_untrim_type=9)
    neg["edge_type_9"] = (
        "✓ 拒：%s" % str(r.get("error"))[:80] if not r["ok"] else "★★ 没拒"
    )
    out["negatives"] = neg
    for k, v in neg.items():
        print("★ 负例 %-14s %s" % (k, v))

    #: ── ③ 真机：普通零件上有面可选 ⇒ 调 ⇒ ★ **特征树不该变**（★ 官方前置的实证）──
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (
        ("solidworks_sketch_start", {}),
        ("solidworks_sketch_add_rectangle", RECT),
        ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 20.0}),
    ):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建状态没成：%s" % step)
            return 1
    rep = sf.untrim_surface_report(model, distance_mm=0.0)
    out["solid_part_call"] = {
        k: rep.get(k)
        for k in (
            "ok",
            "doc_type",
            "faces_selected",
            "stage",
            "feature_count_before",
            "feature_count_after",
            "new_features",
            "error",
            "trim_opposite_side_valid",
        )
    }
    print(
        "★★ 普通零件上（★ 能选到面）⇒ ok=%r · 特征 %r→%r · 新增 %r"
        % (
            rep.get("ok"),
            rep.get("feature_count_before"),
            rep.get("feature_count_after"),
            rep.get("new_features"),
        )
    )
    print(
        "★★ `BTrimOppositeSide` 在 `merge=True` 时是否有效 = %r（★ 官方：只在 BMerge=false 时）"
        % rep.get("trim_opposite_side_valid")
    )

    #: ── ④ ★ 负例：★ 没预选（★ 官方 "requires preselection"）─────────────
    sw_connect.new_document(sw, "part")
    m2 = sw_connect.get_com_member(sw, "ActiveDoc")
    rep2 = sf.untrim_surface_report(m2, distance_mm=0.0)
    out["no_preselection"] = {
        k: rep2.get(k) for k in ("ok", "faces_selected", "stage", "error")
    }
    print(
        "★★ 没预选 ⇒ ok=%r · stage=%r · faces_selected=%r"
        % (rep2.get("ok"), rep2.get("stage"), rep2.get("faces_selected"))
    )

    p = ROOT / "output" / "spec211-b2-untrim.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
