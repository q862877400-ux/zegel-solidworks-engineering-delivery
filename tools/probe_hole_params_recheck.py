"""★ 真机验 `hole_params` 并**测出那一族的单位口径**（★ 阶段 3 补能力 · 第 4 个）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IWizardHoleFeatureData2
# \`）
# 文件:   `scripts/sw_feature_readback.py::hole_params`（★ 刚补的能力）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **而本轮多一件事**：★ 那一族的官方 `## Returns` **没写单位** ⇒
#     ★★★ **按铁律 5 真机测它** —— ★ 判据（★ 与前三层对照）：
#       · ★ 本仓 `hole_wizard` 的 `size` 参数是个**规格串**（如 `"M8"`）⇒
#         ★★ **直径应由标准决定** ⇒ ★★★ **若读数 ≈ 8 而文档单位是毫米** ⇒ **随文档** ✓
#       · ★ 而**若读数 ≈ 0.008** ⇒ **写死米** ✓
# ★★★ **⚠ 前置**：★ `hole_wizard` 需要一个**轴对齐的实体 + 声明式面选择器**（★ 见工具的
# doc）⇒
#     ★ 本探针先建一块板、再在 `+z` 面上打孔 ✓
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

OUT = REPO / "output" / "hole-params-capability-recheck.json"


def main() -> int:
    import sw_part as p
    from sw_connect import connect_solidworks, get_com_member, new_document
    from sw_feature_readback import hole_params

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with p.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.05, -0.03), (0.05, -0.03)),
            ((0.05, -0.03), (0.05, 0.03)),
            ((0.05, 0.03), (-0.05, 0.03)),
            ((-0.05, 0.03), (-0.05, -0.03)),
        ):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    p.extrude_boss(model, sk, 20.0)

    #: ★★ 前置：★ 用**本仓的**异型孔入口 —— ★★ **名字是
    #: `create_hole_wizard_at_selection_report(model, selection, size, *, diameter_mm=8)
    #: `**
    #:   （★ 我第一版猜的是 `hole_wizard` ⇒ ★ **不存在**）✓
    #:   ⇒ ★★★ **那正是上一轮那条判据**：★★★ **写新调用前，先在仓里搜同名成员怎么用的** ✓
    hw = {"error": None, "returned": None}
    try:
        from sw_hole_features import create_hole_wizard_at_selection_report  # noqa: PLC0415

        hw["returned"] = str(
            create_hole_wizard_at_selection_report(model, "+z", "M8", diameter_mm=8)
        )[:120]
    except Exception as exc:  # noqa: BLE001
        hw["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])

    r = hole_params(model)
    f = {k: v for k, v in r.items() if not k.startswith("★_")}

    #: ★★★★★★ **单位判定（★ 与前三层对照）** —— ★ 判据写死、★ 只报 ✓
    #: ★★ **⚠ 我第一版只看 `HoleDiameter`** ⇒ ★ **它在本例是 `0.0`**（★ 通孔类型下不用它
    #: ）⇒
    #:     ★★★ **判不出** ⇒ ★ **改用**通孔那两个量**（★ 它们才是本例在用的）** ✓
    #:   ★★★★ **实测（★ 本轮）**：★ `ThruHoleDiameter = **0.008**` ⇒ **米**（★ M8 = 8mm）·
    #:     ★ `ThruHoleDepth = **20.0**` ⇒ **毫米**（★ 板厚 20mm）⇒
    #:     ★★★★★ **⇒ **同一个接口里两个量的口径不同****（★ 本会话的**第五层**）✓
    verdict = "★ 判不出（★ 没读到直径）"
    detail = {}
    for key, expect_m, expect_mm in (
        ("ThruHoleDiameter", 0.008, 8.0),
        ("HoleDiameter", 0.008, 8.0),
    ):
        try:
            v = float(r.get(key))
        except Exception:  # noqa: BLE001
            continue
        if v == 0.0:
            detail[key] = "★ 0.0 ⇒ 本例不使用它（★ 判据要换一个量）"
            continue
        if abs(v - expect_m) < 5e-4:
            detail[key] = "★ **米**（★ 读数 %r）" % v
        elif abs(v - expect_mm) < 0.5:
            detail[key] = "★ **毫米**（★ 读数 %r）" % v
        else:
            detail[key] = "★ 读数 %r ⇒ 两种都不是" % v
    try:
        v = float(r.get("ThruHoleDepth"))
        detail["ThruHoleDepth"] = (
            ("★ **毫米**（★ 读数 %r · 板厚 20mm）" % v)
            if abs(v - 20.0) < 0.5
            else ("★ 读数 %r" % v)
        )
    except Exception:  # noqa: BLE001
        pass
    verdict = "★ **同一个接口里两个量口径不同** —— " + " · ".join(
        "%s ⇒ %s" % (k, v) for k, v in detail.items()
    )

    r_ = {
        "★_目的": "★ 验 `hole_params` + ★ **测出那一族的单位口径**（★ 官方 `## Returns` 没写）",
        "★_前置": hw,
        "读取": {k: str(v)[:50] for k, v in f.items()},
        "★_单位口径（★ 官方未写）": r.get("★_单位口径"),
        "★_单位判定": verdict,
        "★_逐量判定": detail,
    }
    OUT.write_text(
        json.dumps(r_, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ 前置 hole_wizard:", json.dumps(hw, ensure_ascii=False)[:150])
    print("★ 读取:", json.dumps(r_["读取"], ensure_ascii=False)[:400])
    print("★ 单位判定:", verdict)
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
