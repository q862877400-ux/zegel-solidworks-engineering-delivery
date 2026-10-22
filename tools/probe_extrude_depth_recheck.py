"""★ 真机验新能力 `extrude_depth`（★ 阶段 3 补能力 · 复查）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_feature_readback.py::extrude_depth`（★ **刚补的能力**）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 本探针调**能力层本体**、
#   ★★ 而**不是**在探针里另写一遍调用 ✓
#   ★★★ **判据**：★ 建 `depth=20`（毫米口径）的凸台 ⇒ `extrude_depth` 回 **20.0** ✓
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

OUT = REPO / "output" / "extrude-depth-capability-recheck.json"


def main() -> int:
    import sw_part as P
    from sw_connect import connect_solidworks, get_com_member, new_document
    from sw_feature_readback import extrude_depth

    app, _ = connect_solidworks(visible=True)
    rows = []
    for depth_mm in (20.0, 5.0):
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            for a, b in (
                ((-0.05, -0.03), (0.05, -0.03)),
                ((0.05, -0.03), (0.05, 0.03)),
                ((0.05, 0.03), (-0.05, 0.03)),
                ((-0.05, 0.03), (-0.05, -0.03)),
            ):
                get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        P.extrude_boss(model, sk, depth_mm)
        r = extrude_depth(model)  #: ★ 按名不给 ⇒ 兜底找第一个
        units = None
        try:
            units = list(get_com_member(model, "GetUnits"))
        except Exception:  # noqa: BLE001
            pass
        rows.append(
            {
                "asked_depth_mm": depth_mm,
                "GetUnits": units,
                "readback": {k: str(v)[:60] for k, v in (r or {}).items()},
            }
        )

    R = {
        "★_判据": "★ 本仓毫米口径下建 depth=N ⇒ `extrude_depth` 应回 **N**（★ 随文档单位）",
        "★_能力": "scripts/sw_feature_readback.py::extrude_depth",
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    for r in rows:
        rb = r["readback"]
        print(
            "★ 建 %-6s mm ⇒ depth=%s · feature=%s · end_condition=%s · err=%s"
            % (
                r["asked_depth_mm"],
                rb.get("depth"),
                rb.get("feature"),
                rb.get("end_condition"),
                (rb.get("error") or "")[:40],
            )
        )
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
