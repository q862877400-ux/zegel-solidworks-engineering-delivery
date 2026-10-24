"""★ 用现有样件生成一份真实报告 —— 证明报告链路能跑通。

★ 为什么要有这个脚本（而不是只在测试里拼 CheckResult）：

测试里拼的是**人工构造**的 `CheckResult`，只能证明汇总逻辑对。
本脚本把 `samples.py` 的样件**真的**跑过十对采集器/判定器，
再用 `build_report()` 汇总 —— 证明「采集 → 判定 → 汇总 → 渲染」整条链路通。

★ 只读：不连 SolidWorks、不写仓库文件（除非 `--out` 指定）。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_acceptance_report.py
# 定位:   证明「采集 → 判定 → 汇总 → 渲染」整条链路能跑通。
#           ★ 测试里拼的是人工构造的 CheckResult，只证明汇总逻辑对；
#             本探针把 samples.py 的样件**真的**跑过十对采集器/判定器，
#             再用 build_report() 汇总 —— 证明链路本身通。
#           ★ 两组样例：全绿组（应 10/10 pass）· 混合组（三种状态都出现）。
# 官方依据: 不适用（纯离线，不连 SolidWorks、不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from engineering.acceptance import samples as smp  # noqa: E402
from engineering.acceptance.e1_sketch import judge_sketch_constraint  # noqa: E402
from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_hole_readback,
    collect_reference_stability,
    judge_feature_tree,
    judge_hole_readback,
    judge_rebuild,
    judge_reference_stability,
)
from engineering.acceptance.e4_assembly import (  # noqa: E402
    judge_assembly,
    judge_assembly_interference,
)
from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    judge_drawing,
    judge_process,
)
from engineering.acceptance.e7_provenance import judge_provenance  # noqa: E402
from engineering.acceptance.report import build_report, render_markdown  # noqa: E402

REQ = "R-report-demo"

#: ★ 一组「好样件」——应给出七条全绿（reference_stability 用语义选择器）
_GOOD_STEPS = (
    {"step": "sketch_start", "params": {"plane_name": "Front Plane"}},
    {
        "step": "chamfer",
        "params": {"selection": "+z", "distance_mm": 2.0},
    },
)

_HOLE_REQ = tuple(
    {
        "id": "h%d" % (i + 1),
        "kind": "through",
        "diameter_mm": 6.0,
        "position_mm": [10.0 + i * 20.0, 10.0, 0.0],
    }
    for i in range(4)
)
_HOLE_MEAS = {
    "holes": [
        {
            "diameter_mm": 6.0,
            "position_mm": [10.0 + i * 20.0, 10.0, 0.0],
            "axis": [0.0, 0.0, 1.0],
            "kind": "through",
        }
        for i in range(4)
    ]
}


def good_checks() -> list:
    """★ 七条判据全绿的一组检查。"""
    return [
        judge_sketch_constraint(smp.good_e1(), requirement_id=REQ),
        judge_rebuild(smp.good_e2(), requirement_id=REQ),
        judge_hole_readback(
            collect_hole_readback(
                target="plate", requested=_HOLE_REQ, measured=_HOLE_MEAS
            ),
            requirement_id=REQ,
        ),
        judge_feature_tree(smp.good_e3(), requirement_id=REQ),
        judge_reference_stability(
            collect_reference_stability(target="plan", steps=_GOOD_STEPS),
            requirement_id=REQ,
        ),
        judge_assembly(smp.good_e4(), requirement_id=REQ),
        judge_assembly_interference(smp.good_e4(), requirement_id=REQ),
        judge_drawing(smp.good_e5(), requirement_id=REQ),
        judge_process(smp.good_e6(), requirement_id=REQ),
        judge_provenance(smp.good_e7(), requirement_id=REQ),
    ]


def mixed_checks() -> list:
    """★ 混合：有绿、有不合格、有未测到 —— 报告的三种状态都出现。"""
    return [
        judge_sketch_constraint(smp.good_e1(), requirement_id=REQ),
        judge_rebuild(smp.bad_e2_new_document(), requirement_id=REQ),
        judge_hole_readback(
            collect_hole_readback(
                target="plate",
                requested=_HOLE_REQ,
                #: ★ 不给 kind ⇒ 孔型那项必然 unknown
                measured={
                    "holes": [
                        {
                            "diameter_mm": 6.0,
                            "position_mm": [10.0 + i * 20.0, 10.0, 0.0],
                            "axis": [0.0, 0.0, 1.0],
                        }
                        for i in range(4)
                    ]
                },
            ),
            requirement_id=REQ,
        ),
        judge_feature_tree(smp.good_e3(), requirement_id=REQ),
        judge_reference_stability(
            collect_reference_stability(
                target="plan",
                steps=(
                    {
                        "step": "chamfer",
                        "params": {"selection": "index:0", "distance_mm": 2.0},
                    },
                ),
            ),
            requirement_id=REQ,
        ),
        judge_drawing(smp.bad_e5_empty_evidence(), requirement_id=REQ),
    ]


def main() -> int:
    print("=" * 68)
    print("① 全绿组（语义选择器 + 孔型齐全）")
    print("=" * 68)
    rep = build_report(good_checks())
    print(
        "overall=%s · 十项=%d · pass=%d fail=%d unknown=%d"
        % (
            rep["overall"],
            rep["counts"]["checks"],
            rep["counts"]["pass"],
            rep["counts"]["fail"],
            rep["counts"]["unknown"],
        )
    )
    bad = [c for c in rep["criteria"] if rep["criteria"][c]["status"] != "pass"]
    print("未全绿的判据：%s" % (bad or "无"))
    print()
    print(render_markdown(rep, title="E1–E7 验收报告 · 全绿组"))

    print()
    print("=" * 68)
    print("② 混合组（有不合格、有未测到、有未检查）")
    print("=" * 68)
    rep2 = build_report(mixed_checks())
    print("overall=%s" % rep2["overall"])
    print()
    print(render_markdown(rep2, title="E1–E7 验收报告 · 混合组"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
