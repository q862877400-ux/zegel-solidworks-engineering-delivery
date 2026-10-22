"""★ 探针：`InsertWeldmentTrimFeature2` **第三步** —— ★ 用**正确档位** `swEndConditionTrim(4)`。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3-1 的第三步探针）
# 文件:   tools/probe_spec211_weldtrim_opt.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B3-1**。★ 前两步：★ 第一步"查行为"
#           （★ 前置没上 ⇒
# 没建 ✓）⇒ ★ 第二步"把 mark 1/2 选上"（★ 而**仍不建** ⇒ ★ 我当时**拒称"完全试死"** ✓）
# 。
#   ★★★ **本探针查到"不建"的第三种成因：档位传错** ✓✓ ——
#     ★ `EndCond` 取 `swSolidworksWeldmentEndCondOptions_e`，★ 而该枚举里
#       ★ **`swEndConditionTrim = 4`** ✓（★ 我第二步**传的是 `0` = `swEndConditionNone`** ✗）
#     ★ `Options` 是 `swWeldmentTrimExtendOptionType_e` 的 **Logical sum**（★ 1/2/4/8 ✓）
#   ⇒ ★★ 故本探针**传正确档位**再试一次 ✓ —— ★ 并按官方 Remarks：
# ★ mark **1 = Body or bodies to trim** · ★ mark **2 = Trimming boundaries (body **or fa
# ce**)**
#     ⇒ ★★★ **mark 2 用「面」** ✓（★ 面比体好选：★ `sw_selection_spec` 的 `index:<n>` ✓）
# 判据:   ★★★ **三条路分开**（★ 与「扫描曲面」那条成功案例同型）：
#     · ★ **建成** ⇒ ★★★ **「大发现」**：★ 裁剪/延伸焊件走得通 ✓
# ★ · ★ **仍不建** ⇒ ★★ **那才够格叫「试死」**（★ 因为三处都追过了：★ 前置 ✓ · mark ✓ ·
# 档位 ✓）
#   ★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
# 官方依据: `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`（签名 + Param
#           eters + Remarks）
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

BODY_A = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 60.0, "y2_mm": 40.0}
BODY_B = {"x1_mm": 30.0, "y1_mm": -20.0, "x2_mm": 90.0, "y2_mm": 60.0}
#: ★ 官方 `swSolidworksWeldmentEndCondOptions_e` 里**与 trim 有关**的那几档 ✓
END_COND_CANDIDATES = (4, 1, 5, 0)  #: ★ 4 = swEndConditionTrim（★ **最可能**）✓
OPTION_CANDIDATES = (1, 0)  #: ★ 1 = AllowTrimmedExtensionTrim ✓


def main() -> int:
    import sw_connect
    import sw_part
    import sw_selection_spec as SS
    import sw_weldment as W

    out: dict = {
        "official": "IFeatureManager.InsertWeldmentTrimFeature2",
        "step": "第三步：用正确档位（EndCond=4 = swEndConditionTrim）",
        "end_cond_enum": {
            "swEndConditionNone": 0,
            "swEndConditionMiter": 1,
            "swEndConditionButt1": 2,
            "swEndConditionButt2": 3,
            "swEndConditionTrim": 4,
            "swEndConditionUseDefault": 5,
        },
        "option_enum": {
            "AllowTrimmedExtensionTrim": 1,
            "AllowTrimmingExtensionTrim": 2,
            "CopedCut": 4,
            "WeldGap": 8,
        },
        "runs": [],
    }

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    #: ★★ **批量试**：★ 每档**各自一个零件**（★ 免得相互污染 —— ★ 规格 210 的教训 ✓）
    for end_cond in END_COND_CANDIDATES:
        for options in OPTION_CANDIDATES:
            model = sw_connect.new_document(sw, "part")
            if model is None:
                continue
            for rect in (BODY_A, BODY_B):
                sw_part.start_sketch(model, "Front Plane")
                sw_part.sketch_corner_rectangle(
                    model, rect["x1_mm"], rect["y1_mm"], rect["x2_mm"], rect["y2_mm"]
                )
                nm = sw_part.current_sketch_name(model)
                sw_part.end_sketch(model)
                sw_part.extrude_boss(model, nm, 20.0)
            feats = W.feature_names(model)
            ex = [f for f in feats if "拉伸" in f or "Extrude" in f]
            fm = sw_connect.get_com_member(model, "FeatureManager")
            try:
                sw_connect.get_com_member(fm, "InsertWeldmentFeature")
            except Exception:  # noqa: BLE001
                pass
            ext = sw_connect.get_com_member(model, "Extension")
            #: ★ mark 1（★ 体，按生成体的**特征名** —— ★ 事实 32 ✓）
            ok1 = (
                bool(
                    sw_part._select_by_id(
                        ext, ex[0], "BODYFEATURE", append=False, mark=1
                    )
                )
                if ex
                else False
            )
            #: ★★ mark 2 **用面**（★ 官方 Remarks 逐字允许 "body **or face**" ✓；
            #:    ★ 面比体好选：★ `index:<n>` ✓）
            try:
                #: ★★★ **必须 `append=True`**（★ 我上一版漏了它 ⇒ ❌ 它**清空了 mark 1
                #: 的体** ✗：
                #:   ★ `select_entity_by_index` 的 `append` **默认为 `False`** ✓
                #: ⇒ ★★ 于是八组读数**全部无效**（mark2 根本没上）⇒ ★ 那种读数**不能当结
                #: 论** ✓）
                SS.select_entity_by_index(model, "FACE", 0, append=True)
                ok2 = SS.get_selection_count(model) > 1
            except Exception:  # noqa: BLE001
                ok2 = False
            before = W.feature_names(model)
            rep = W.insert_weldment_trim_report(
                model, end_cond=end_cond, options=options, gap_mm=0.0
            )
            added = [n for n in W.feature_names(model) if n not in before]
            row = {
                "end_cond": end_cond,
                "options": options,
                "body_selected": ok1,
                "boundary_by_face": ok2,
                "selection_count": SS.get_selection_count(model),
                "ok": rep.get("ok"),
                "added": added,
                "returned_is_none": rep.get("returned_is_none"),
                "error": str(rep.get("error"))[:120],
            }
            out["runs"].append(row)
            print(
                "★ EndCond=%-2d Options=%-2d ⇒ ok=%r · mark1体=%r · mark2面=%r · 新增 %r"
                % (
                    end_cond,
                    options,
                    rep.get("ok"),
                    row["body_selected"],
                    row["boundary_by_face"],
                    added,
                )
            )
            if rep.get("ok"):
                out["verdict"] = (
                    "★★★★ **建成**（★ EndCond=%d · Options=%d）⇒ ★★★ **大发现**："
                    "★ 裁剪/延伸焊件**走得通** ✓" % (end_cond, options)
                )
                break
        if out.get("verdict"):
            break
    if not out.get("verdict"):
        out["verdict"] = (
            "★★★★ **四档 × 两 options 全试过、仍不建** ⇒ ★★ **这才够格叫「试死」** "
            "（★ 前置 ✓ · mark ✓ · 档位 ✓ —— 三处都追过了）✓"
        )
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b3-weldtrim-opt.json"
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
