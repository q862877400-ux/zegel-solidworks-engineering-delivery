"""★ 探针：`InsertSweepSurface2`（★ **那条从没查过的路 B**）—— ★ 最小实验：先看它的"行为"。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B2-2 的真机探针）
# 文件:   tools/probe_spec211_sweep.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-2**「扫描曲面」。
#   ★★★ **本探针存在的理由（★ 一句话）**：★ 官方有**两条**建曲面扫描的入口 ⇒
#     · ★ **路 A** = `CreateDefinition(swFmSweepSurface)` + `CreateFeature` ⇒
#       ★★ **事实 392**：★「**`CreateFeature` 在这条后端上静默回 `None`**」✗（★ **已试死** ✓）
#     · ★ **路 B** = `InsertSweepSurface2`（★ 参数式 + 官方 mark 表）⇒ ★★ **从来没试过** ✓
# （★ 依据**事实 237**：「'不做曲面族'那条结论只覆盖了**半条路** …**而第二条从来没试过**
# 」✓）
#   ⇒ ★★ 故本探针**只做最小实验**：★ **先量它的"行为"**（★ 抛？静默回 `None`？建成？）✓
#     ★ 因为这三者的**下一步完全不同**：
#       · ★ **抛异常** ⇒ ★ 说明这条路**有反应**（★ 与路 A 不同 ✓）⇒ ★ 值得继续建几何 ✓
#       · ★ **静默回 `None`** ⇒ ★ 与**事实 392 同族** ✗ ⇒ ★ 记下来、别硬试 ✓
#       · ★ **建成** ⇒ ★ 那是**大发现**（★ 那条路走得通 ✓）
# 判据:   ★★ **行为三分**（★ 上面那条）+ ★ **特征树变化**（★ 回读，★ 不看返回值 ✓）
#   ★★ **本探针不建复杂几何** —— ★ 那需要"轮廓草图 + 路径草图 + 按 mark 选"一整条链，
#     ★ 而**先看行为**才知道那条链**值不值得建** ✓（★ 事实 53 的精神：★ 别一头扎进去 ✓）
# 官方依据: `C:\swapi\types\IFeatureManager\InsertSweepSurface2.md`（签名 + Remarks 的 m
#           ark 表）
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


def main() -> int:
    import sw_connect
    import sw_surface_features as sf

    out = {"official": "IFeatureManager.InsertSweepSurface2",
           "route": "B", "route_a_status": "已试死（事实 392：CreateFeature 静默回 None）",
           "route_b_status": "从没试过（事实 237）",
           "experiment": "最小实验 —— 空零件上直接调，先看「行为」三分"}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2

    rep = sf.sweep_surface_report(model, use_auto_select=True)
    out["report"] = rep

    #: ★★ **行为三分**（★ 这三者的下一步完全不同 ✓）
    if not rep.get("ok") and rep.get("error", "").startswith(("TypeError", "com_error", "AttributeError")):
        verdict = "★ **抛异常** ⇒ ★ 这条路**有反应**（★ 与路 A 的「静默」不同 ✓）"
    elif not rep.get("ok") and rep.get("returned_is_none"):
        verdict = ("★★ **静默回 `None`** ⇒ ★ 与**事实 392 同族** ✗ ⇒ "
                   "★ 记下来、★ 别硬试（★ 事实 53）")
    elif rep.get("ok"):
        verdict = "★★★ **建成了** ⇒ ★ **这是大发现**（★ 那条路走得通 ✓）"
    else:
        verdict = "★ 其它：★ %s" % str(rep.get("error"))[:100]
    out["behavior_verdict"] = verdict

    print("★ 路 B 读数：★ ok=%r · returned_is_none=%r · 特征 %r→%r · 新增 %r"
          % (rep.get("ok"), rep.get("returned_is_none"), rep.get("feature_count_before"),
             rep.get("feature_count_after"), rep.get("new_features")))
    print("★ 调用前选择计数 = %r" % rep.get("selection_count_before"))
    print("★ error = %s" % str(rep.get("error"))[:170])
    print("★★ **行为三分** ⇒ %s" % verdict)
    print("★ 官方 mark 表（★ 返回值里带） = %r" % rep.get("official_marks"))

    p = ROOT / "output" / "spec211-b2-sweep.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
