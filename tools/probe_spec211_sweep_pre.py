"""★ 探针：`InsertSweepSurface2` —— ★★ **给它把前置完全对上**：轮廓 mark 1 · 路径 mark 4。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B2-2 的第二步探针）
# 文件:   tools/probe_spec211_sweep_pre.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B2-2**。★ 上一轮（`probe_spec211_s
#           weep.py`）
#   **只到「查了行为」**：★ 空零件、**无选择**下直接调 ⇒ **静默回 `None`** ✗ ——
#   ★★ 而官方 `## Remarks` 明写**必须先按 mark 选**（1=Profile · 4=Sweep path）⇒
#     ★ 那个"静默"**很可能只是因为"前置没上"** ✗
#   ⇒ ★★★ **本探针把前置完全对上**：★ 建**两个互相垂直面上的草图**（★ 轮廓 / 路径），
#     ★ **按官方 mark 表选好**（1 / 4）⇒ ★★ **然后才谈"这条路是死是活"** ✓
# 判据:   ★★★ **两条路分开**（★ 这是本探针存在的全部意义）：
#     · ★ 若**仍静默回 `None`** ⇒ ★★ **那才是真正的「试死」** ✓（★ 那时才可与**事实 392** 并列 ✓）
#     · ★ 若**建成**（特征树 +1）⇒ ★★ **「大发现」** ✓（★ 那条路走得通 ✓）
#   ★ 主判据一律**回读**：★ **特征树多了新特征**（★ 不看返回值 ✓）
#   ★★ **前置必须逐条对上**（★ 否则读数没有判别力）：
#     ★ ① 轮廓草图 mark **1** · ★ ② 路径草图 mark **4** · ★ ③ 两者在**不同的面**上
#     ★（★ 扫描的路径与轮廓**不能共面** —— 共面时那条路本身不成立 ✓）
#     ★ ④ ★ `SelectByID2` 的 Callout **必须传** `VARIANT(VT_DISPATCH, None)`（**事实 33**；
#       ★ 本探针复用 `sw_part._select_by_id` —— ★ 它内部已有 `_empty_callout()` ✓）
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
    import sw_part
    import sw_surface_features as sf

    out: dict = {"official": "IFeatureManager.InsertSweepSurface2",
                 "purpose": "把前置完全对上，把「试死」与「大发现」分开",
                 "marks_used": {"profile": 1, "path": 4}}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    if model is None:
        print("★ 建不了零件")
        return 2

    #: ★ 轮廓草图（★ **前视基准面**）：一个圆 ✓
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_circle(model, 0.0, 0.0, 10.0)
    sk1 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    #: ★ 路径草图（★ **上视基准面** —— ★ 与轮廓**不同的面**，★ 扫描要求 ✓）：一条直线 ✓
    sw_part.start_sketch(model, "Top Plane")
    sw_part.sketch_line(model, 0.0, 0.0, 0.0, 60.0)
    sk2 = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    out["sketches"] = {"profile": sk1, "path": sk2}
    print("★ 草图：★ 轮廓 = %r（前视）· 路径 = %r（上视）" % (sk1, sk2))

    before = sf.feature_names(model)
    out["features_before"] = before
    ext = sw_connect.get_com_member(model, "Extension")
    #: ★★ **按官方 mark 表选**：★ 1 = Profile · 4 = Sweep path ✓
    ok1 = bool(sw_part._select_by_id(ext, sk1, "SKETCH", append=False, mark=1))
    ok2 = bool(sw_part._select_by_id(ext, sk2, "SKETCH", append=True, mark=4))
    out["select_results"] = {"profile_mark1": ok1, "path_mark4": ok2}
    import sw_selection_spec as SS
    out["selection_count"] = SS.get_selection_count(model)
    print("★ 选择：★ mark1(profile)=%r · mark4(path)=%r · 选区计数=%r"
          % (ok1, ok2, out["selection_count"]))

    rep = sf.sweep_surface_report(model, use_auto_select=True)
    out["report"] = rep
    print("★★ 调用后 ⇒ ok=%r · returned_is_none=%r · 特征 %r→%r · 新增 %r"
          % (rep.get("ok"), rep.get("returned_is_none"), rep.get("feature_count_before"),
             rep.get("feature_count_after"), rep.get("new_features")))

    #: ★★★ **两条路分开**（★ 本探针存在的全部意义 ✓）
    if rep.get("ok"):
        verdict = "★★★★ **建成了** ⇒ ★ **「大发现」**：★ 这条路走得通 ✓（★ 事实 392 那条是路 A ✓）"
    elif rep.get("returned_is_none"):
        verdict = ("★★★★ **前置全对上、仍静默回 `None`** ⇒ ★★ **这才是真正的「试死」** ✓ "
                   "⇒ ★★ **从此可与事实 392 并列**（★ 两条路都死 ✓）")
    else:
        verdict = "★ 其它：%s" % str(rep.get("error"))[:120]
    out["verdict"] = verdict
    print("★★★ 判定 ⇒ %s" % verdict)

    p = ROOT / "output" / "spec211-b2-sweep-pre.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
