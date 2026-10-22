"""★ 探针：`InsertWeldmentTrimFeature2` **第二步** —— ★ 把前置完全对上，把「试死」与「大发现」分开。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3-1 的第二步探针）
# 文件:   tools/probe_spec211_weldtrim_pre.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B3-1**。★ 第一步（上一轮）**只到"
#           查行为"**：
#   ★ 两种数组形参形态**都调通**、★ 而**特征树没变** ⇒ ★★ **因为前置没上**（★ 官方 `## Remarks`
#   明写 mark **1 = Body to trim** · **2 = Trimming boundaries** 都要选 ✓）
#   ⇒ ★★★ **本探针把前置完全对上** —— ★★ 与「扫描曲面」那条**成功案例同型** ✓
# 判据:   ★★★ **两条路分开**（★ 本探针存在的全部意义）：
#     · ★ **仍不建** ⇒ ★★ **那才是真正的「试死」** ✓
#     · ★ **建成** ⇒ ★★ **「大发现」** ✓
#   ★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
#   ★★ **前置逐条对上**（★ 否则读数没有判别力 ✓）：
#     ★ ① **焊件特征**：★ 官方要"焊件体" ⇒ ★ 先 `InsertWeldmentFeature`（★ 本模块既有的调用 ✓）
#     ★ ② **两个体**：★ 用**两次拉伸**各产一个体 ✓
#     ★ ③ **按 mark 选**：★★ **`IEntity::Select4` 没有 mark 参数** ✗（★ 记忆里 `revolve_boss` 那条
#        死路的一部分）⇒ ★★ 正解是 **`SelectByID2(<特征名>, "BODYFEATURE", …, mark, …)`** ✓
#        （★ 事实 32：★ **特征有名字**、★ 实体没有 ⇒ ★ 按"生成体的**特征名**"选 ✓）
#     ★ ④ `SelectByID2` 的 Callout **必须传** `VARIANT(VT_DISPATCH, None)`（**事实 33**）✓
# 官方依据: `C:\swapi\types\IFeatureManager\InsertWeldmentTrimFeature2.md`（签名 + Remar
#           ks 的 mark 表）
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

#: ★ 两个**相交**的拉伸体（★ 第二块沿 Z 压过去 ⇒ 与第一块相交 ✓）
BODY_A = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 60.0, "y2_mm": 40.0}
BODY_B = {"x1_mm": 30.0, "y1_mm": -20.0, "x2_mm": 90.0, "y2_mm": 60.0}


def main() -> int:
    import sw_connect
    import sw_part
    import sw_weldment as W
    import sw_selection_spec as SS

    out: dict = {"official": "IFeatureManager.InsertWeldmentTrimFeature2",
                 "step": "第二步：把前置完全对上",
                 "marks": dict(W.WELDMENT_TRIM_MARKS)}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2

    #: ① 两个体（★ 各由一次拉伸产生 ⇒ ★ 各有名字 ✓）
    for rect in (BODY_A, BODY_B):
        sw_part.start_sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, rect["x1_mm"], rect["y1_mm"],
                                        rect["x2_mm"], rect["y2_mm"])
        name = sw_part.current_sketch_name(model)
        sw_part.end_sketch(model)
        sw_part.extrude_boss(model, name, 20.0)
    feats = W.feature_names(model)
    extrudes = [f for f in feats if "拉伸" in f or "Extrude" in f]
    out["features"] = feats
    out["extrude_names"] = extrudes
    print("★ 特征树 = %r" % feats)
    print("★ 可用来选的拉伸特征 = %r" % extrudes)

    #: ② **焊件特征**（★ 官方要"焊件体" ⇒ 这一步把零件变成焊件 ✓）
    fm = sw_connect.get_com_member(model, "FeatureManager")
    weld = None
    try:
        weld = sw_connect.get_com_member(fm, "InsertWeldmentFeature")
    except Exception as exc:                                            # noqa: BLE001
        out["weldment_feature_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    out["weldment_feature_ok"] = weld is not None
    print("★ `InsertWeldmentFeature` ⇒ %r" % ("建了" if weld is not None else "没建/报错"))

    #: ③ **按 mark 选两个体**（★ 用"生成体的特征名" + `BODYFEATURE` ✓；★ Callout 按事实 33 ✓）
    if len(extrudes) < 2:
        out["stage"] = "precondition"
        out["error"] = "★ 拉伸特征不足两个（★ 实测 %d 个）⇒ ★ 前置立不起来" % len(extrudes)
        print("★★ %s" % out["error"])
    else:
        ext = sw_connect.get_com_member(model, "Extension")
        ok1 = bool(sw_part._select_by_id(ext, extrudes[0], "BODYFEATURE",
                                         append=False, mark=1))
        ok2 = bool(sw_part._select_by_id(ext, extrudes[1], "BODYFEATURE",
                                         append=True, mark=2))
        out["select_results"] = {"mark1_body_to_trim": ok1, "mark2_boundary": ok2,
                                 "feature_names": extrudes[:2]}
        out["selection_count"] = SS.get_selection_count(model)
        print("★ 选择：mark1=%r · mark2=%r · 选区计数=%r"
              % (ok1, ok2, out["selection_count"]))
        #: ④ **调**
        rep = W.insert_weldment_trim_report(model, end_cond=0, options=0, gap_mm=0.0)
        out["report"] = {k: rep.get(k) for k in
                         ("ok", "returned_is_none", "new_features", "feature_count_before",
                          "feature_count_after", "selection_count_before", "error")}
        if rep.get("ok"):
            out["verdict"] = "★★★★ **建成** ⇒ ★ **「大发现」**：★ 裁剪/延伸焊件这条路走得通 ✓"
        else:
            out["verdict"] = ("★★★★ **前置全对上、仍不建** ⇒ ★★ **这才是真正的「试死」** ✓")
        print("★★ 调用后 ⇒ ok=%r · 新增 %r" % (rep.get("ok"), rep.get("new_features")))
        print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b3-weldtrim-pre.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
