"""★ 真机核：★ `sw_surface_features` 的 `* 0.001` 到底对不对（★ 事实 517 §三的待核项）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_surface_features.py::create_extruded_surface_report`（★ L87 `d * 0
# .001`）
#         `scripts/sw_surface_features.py::thicken_surface_report`（★ L318 `th * 0.001`）
#         `scripts/sw_part.py::get_bounding_box`（★ **量实体** —— 曲面量不了）
# 定位:   ★ `docs/known-facts.md` **事实 517** §三 的**待核项** —— ★ 该模块有 **5 处 `
#           * 0.001`**
#   （★ 都注明「★ 毫米 ⇒ 米」），★ 而**轮 56 的真机定案**说：
# ★★ `FeatureExtrusion3` 的 `D1` 传 `20.0` ⇒ 实体得到 **20 mm** ⇒ ★ **按**文档单位**解释
# ** ✓
#   ★★★ **本探针的判据（★ 一个数就能定案）**：★ 在**毫米文档**里
#     · ★ 建曲面 `depth_mm=**10.0**` ⇒ ★ 曲面应高 **10 mm**
#     · ★★ 加厚 `thickness_mm=**2.0**` ⇒ ★ **量生成的实体厚度**：
#        ★ 厚 **2 mm** ⇒ `*0.001` **错**（★ 值被缩小 1000 倍）
#        ★ 厚 **0.002 mm**（★ 或加厚不出来）⇒ `*0.001` **对**（★ 官方确实吃米）✓
#   ★★ **锚定物**：★ `get_bounding_box` 的 `size`（★ 与参数走**完全不同的 COM 路径**）✓
#   ⚠★ **一次踩到的坑（★ 记下）**：★ 曲面**不是实体** ⇒ `IPartDoc.GetBodies2` 拿不到 ⇒
#     ★ `get_bounding_box` 会抛 `RuntimeError` ⇒ ★★ **所以必须先 `thicken` 成实体再量** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "surface-scale-probe-evidence.json"


def main() -> int:
    import sw_part as P
    import sw_surface_features as S
    from sw_connect import connect_solidworks, get_com_member, new_document

    steps = []
    R = {
        "★_判据": "★ 毫米文档 + 曲面 depth=10.0 + 加厚 thickness=2.0 ⇒ "
        "★ 实体厚 **2 mm** ⇒ `*0.001` 错；★ 厚 **0.002 mm**（或加厚不出）⇒ 对",
        "steps": steps,
    }

    def rec(name, **kw):
        steps.append(dict(name=name, **kw))

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    try:
        R["GetUnits"] = list(get_com_member(model, "GetUnits"))
    except Exception as exc:  # noqa: BLE001
        R["GetUnits"] = "error: %s" % str(exc)[:60]

    P.sketch(model, "Front Plane")
    P.sketch_corner_rectangle(model, -25.0, -15.0, 25.0, 15.0)
    P.end_sketch(model)
    rec("sketch_done", features=P.feature_names(model)[-3:])

    #: ① 建曲面（★ L87 那处 `d * 0.001`）
    #: ★★★★ 2026-10-04（★ 第二轮修正）：★ **把整个返回值原样落盘** ——
    #:   ★ 上一版只记 `ok` / `new_features` / `surface_body_count` ⇒
    #: ★★ 而第一轮跑出 `new_features: []`（★ 调了没建）、★ 第二轮变成 `None`（★ 根本没调
    #: ）
    #:   ⇒ ★★★ **我却看不到 `error` 与 `selection`**（★ 那正是我上一轮刚定的
    #:     「探针必须把**每一次尝试 + 原始返回值**落盘」）✓
    surf = S.create_extruded_surface_report(model, 10.0, "Sketch1")
    rec(
        "create_extruded_surface(depth_mm=10.0)",
        ok=(surf or {}).get("ok"),
        new_features=(surf or {}).get("new_features"),
        surface_bodies=(surf or {}).get("surface_body_count"),
        stage=(surf or {}).get("stage"),
        error=str((surf or {}).get("error"))[:220],
        selection=str((surf or {}).get("selection"))[:280],
        select_returned=(surf or {}).get("select_returned"),
        selection_count=(surf or {}).get("selection_count"),
    )
    R["surface_return_full"] = {k: str(v)[:240] for k, v in (surf or {}).items()}
    R["surface_ok"] = (surf or {}).get("ok")
    R["surface_new_features"] = (surf or {}).get("new_features")

    #: ② 加厚成实体（★ L318 那处 `th * 0.001`）—— ★ 不这样量不到（★ 曲面不是实体）
    th = S.thicken_surface_report(model, 2.0)
    rec(
        "thicken_surface(thickness_mm=2.0)",
        ok=(th or {}).get("ok"),
        new_features=(th or {}).get("new_features"),
        stage=(th or {}).get("stage"),
        error=str((th or {}).get("error"))[:200],
    )
    R["thicken_return_full"] = {k: str(v)[:240] for k, v in (th or {}).items()}
    R["thicken_ok"] = (th or {}).get("ok")

    #: ③ 量实体
    try:
        bb = P.get_bounding_box(model)
        R["bbox_after_thicken"] = bb
        size = bb.get("size") if isinstance(bb, dict) else None
        R["size"] = size
        #: ★ 建草图时 `sketch_corner_rectangle(-25,-15,25,15)` 给的是 50×30 ⇒
        #:   ★★ 若它按毫米 ⇒ 实体应是 **50 × 30 × 2 mm**
        R["★_读法"] = (
            "★ 若 size ≈ [50, 30, **2**] ⇒ 本仓的『毫米』口径**在整条链上一致**；"
            "★ 若第三个分量 ≈ 0.002 或前两维 ≈ 0.05 ⇒ **某处小了 1000 倍**"
        )
    except Exception as exc:  # noqa: BLE001
        R["bbox_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])

    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print(
        json.dumps(
            {k: v for k, v in R.items() if k != "★_判据"},
            ensure_ascii=False,
            indent=1,
            default=str,
        )[:1400]
    )
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
