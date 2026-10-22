"""★ 真机复验：★ 换代后**生产函数 `linear_pattern`** 还能不能建成（★ 阶段 2 · T1 · 改完必验）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_part.py::linear_pattern`（★ 生产 · ★ 刚换成 `FeatureLinearPattern5
# `）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 本探针调**生产函数本体**、
#   ★★ 而**不是**我在探针里另写一遍调用（★ 否则验的是探针、★ 不是代码）✓
#   ★★★ **判据（★ 本仓原有）**：★ `feature_names` 增量 ⇒ 新特征名 ✓
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

OUT = REPO / "output" / "linear-pattern-production-recheck.json"


def main() -> int:
    import sw_part as P
    from sw_connect import (
        connect_solidworks,
        create_empty_dispatch_variant,
        get_com_member,
        new_document,
    )
    from sw_feature_readback import feature_names

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk1:
        sm = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.05, -0.03), (0.05, -0.03)),
            ((0.05, -0.03), (0.05, 0.03)),
            ((0.05, 0.03), (-0.05, 0.03)),
            ((-0.05, 0.03), (-0.05, -0.03)),
        ):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk1, 10.0)

    #: ★★ 官方示例的调用序（★ 方向 mark=1 · ★ 实体 mark=256）——
    #:   ★ 而**选实体用 `IBody2::Select`**（★ 不是 `Select4`）✓
    ext = get_com_member(model, "Extension")
    get_com_member(model, "ClearSelection2", True)
    d1 = bool(
        get_com_member(
            ext,
            "SelectByID2",
            "",
            "EDGE",
            -0.05,
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

    before = feature_names(model)
    #: ★★ 签名逐字：★ `(model, feature_name, d1_x, d1_y, d1_z, d1_spacing, d1_count, …)`
    #:  ✓
    result = P.linear_pattern(
        model, str(before[-1]) if before else "", 1.0, 0.0, 0.0, 20.0, 2
    )
    after = feature_names(model)
    new = [x for x in after if x not in before]

    R = {
        "★_目的": "★ 复验**生产函数**（★ 刚换成 `FeatureLinearPattern5`）能不能建成",
        "★_选中": {"方向 mark=1": d1, "实体 mark=256": d2},
        "★_生产函数返回": {k: str(v)[:120] for k, v in (result or {}).items()}
        if isinstance(result, dict)
        else str(result)[:200],
        "new_features": new[:6],
        "built": bool(new),
        "tree": {"before": len(before), "after": len(after)},
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ 方向选中:", d1, "· 实体选中:", d2)
    print("★ 生产函数返回:", json.dumps(R["★_生产函数返回"], ensure_ascii=False)[:220])
    print("★ 新特征:", new[:4], "· built =", bool(new))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
