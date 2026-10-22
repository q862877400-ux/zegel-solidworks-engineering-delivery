"""★ 真机验 `pattern_params`（★ 阶段 3 补能力 · 第 3 个 · ★ 换族）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ILinearPatternFeatureDa
# ta\`）
# 文件:   `scripts/sw_feature_readback.py::pattern_params`（★ **刚补的能力**）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **判据（★ 逐个对官方 `## Returns`）**：
#     · ★ 上轮真机构建的阵列是 **`FeatureLinearPattern5(2, 0.02, 1, 0.0, …)`** ⇒
#       ★★ **`D1TotalInstances` 应 = 2** · ★★★ **`D1Spacing` 应 = 0.02**（★ 官方：米）✓
#     · ★ `D2TotalInstances` 应 = 1（★ 没用第二向）· ★ `IsDirection2Specified` 应 = False ✓
#     · ★ `GetSkippedItemCount` 应 = 0 · ★ `GetPatternBodyCount` 应 = 1（★ 实体阵列）✓
#   ★★★ **⚠ 前置（★ 上轮学到的）：★ 阵列要先**选方向 + 选实体**** ——
#     ★ 方向 `mark=1`（★ 按面上的点）· ★ 实体 `IBody2::Select(True, 256)` ✓
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

OUT = REPO / "output" / "pattern-params-capability-recheck.json"


def main() -> int:
    import sw_part as P
    from sw_connect import (
        connect_solidworks,
        create_empty_dispatch_variant,
        get_com_member,
        new_document,
    )
    from sw_feature_readback import pattern_params

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.02, -0.01), (0.02, -0.01)),
            ((0.02, -0.01), (0.02, 0.01)),
            ((0.02, 0.01), (-0.02, 0.01)),
            ((-0.02, 0.01), (-0.02, -0.01)),
        ):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 10.0)
    #: ★★ 前置：★ 方向 `mark=1` · ★ 实体 `mark=256`（★ 官方示例逐字，★ 上轮验过）✓
    ext = get_com_member(model, "Extension")
    get_com_member(model, "ClearSelection2", True)
    d1 = bool(
        get_com_member(
            ext,
            "SelectByID2",
            "",
            "EDGE",
            -0.02,
            0.0,
            0.0,
            True,
            1,
            create_empty_dispatch_variant(),
            0,
        )
    )
    bodies = list(get_com_member(model, "GetBodies2", 0, False) or [])
    d2 = bool(bodies[0].Select(True, 256)) if bodies else None
    #: ★ 官方 22 参：★ 2 个实例、★ 间距 **0.02 米**（= 20mm）、★ 第二向 1 个实例 ✓
    P.linear_pattern(model, "", 1.0, 0.0, 0.0, 20.0, 2)

    r = pattern_params(model)

    def _v(k):
        return r.get(k)

    checks = {
        "★ D1TotalInstances = 2": _v("D1TotalInstances") == 2,
        "★ D1Spacing = 0.02（★ 官方：米）": _v("D1Spacing") == 0.02,
        "★ D2TotalInstances = 1（★ 未用第二向）": _v("D2TotalInstances") == 1,
        "★ IsDirection2Specified = False": _v("IsDirection2Specified") is False,
        "★ GetSkippedItemCount = 0": _v("GetSkippedItemCount") == 0,
        "★ GetPatternBodyCount = 1（★ 实体阵列）": _v("GetPatternBodyCount") == 1,
    }
    R = {
        "★_判据": "★ 逐个成员对官方 `## Returns`（★ 见 `output/_read_pattern_members.py`）",
        "★_前置": {"方向 mark=1": d1, "实体 mark=256": d2},
        "★_单位口径": r.get("★_单位口径"),
        "读取": {k: str(v)[:50] for k, v in r.items()},
        "★_逐条判据": checks,
        "★_全过": all(checks.values()),
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ 前置:", d1, d2)
    print(
        "★ 读取:",
        json.dumps({k: str(v)[:40] for k, v in r.items()}, ensure_ascii=False)[:340],
    )
    for k, v in checks.items():
        print("   %-44s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
