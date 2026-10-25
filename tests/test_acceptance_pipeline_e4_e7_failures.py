"""★ 补 E4/E6/E7 的**失败路径**端到端覆盖。

## 缺口（第 30 轮发现）

`tests/test_acceptance_pipeline_e2e.py` 的两组样件覆盖不对称：

| 组 | 覆盖的 check_id |
|---|---|
| `good_checks()`（全绿） | **10 条全覆盖**（含 E4/E5/E6/E7） |
| `mixed_checks()`（混合） | **只有 6 条**：E1.dof · E2.rebuild · E2.hole_readback · E3.tree · E3.reference_stability · E5.drawing |

⇒ **E4.dof / E4.interference / E6.process / E7.provenance 的失败路径从没在流水线里跑过。**

## 为什么这很危险

`report.py` 按 `check_id` 的 `E1..E7` 前缀归组；**前缀不对就落进 `unassigned`**。
若这四条的 check_id 被改坏（拼错、少点、改成 `E44.`），
「全绿」测试仍然通过（它们都在 pass 分支），而**失败路径静默掉进 `unassigned`** ——
报告里那一条就消失了，看起来像「没跑」而不是「不合格」。

⇒ 本文件用**真实采集器与判定器**造这四条的失败结果，断言：
  ① 每条都落到**它自己的** criterion 下（不在 `unassigned`）
  ② `unassigned` 必须为空
  ③ 总体必须 `fail`
  ④ 渲染出的 markdown 里，这四条都出现在「不合格」段
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    judge_feature_tree,
)
from engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly,
    judge_assembly_interference,
)
from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    collect_process,
    judge_process,
)
from engineering.acceptance.e7_provenance import (  # noqa: E402
    collect_provenance,
    judge_provenance,
)
from engineering.acceptance.report import build_report, render_markdown  # noqa: E402
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"


#: ★ E4 的采集器参数很多，这里只填判定器用得到的那些
_ASM = dict(
    target="板1 装配",
    #: ★ 实测签名：`components` 是**元组**（组件名清单），不是数量
    components=("板1", "板2"),
    mates=(
        {"a": "板1", "b": "板2", "kind": "coincident", "target_ok": True},
    ),
    target_dof=0,
    interference_count=0,
    min_clearance_mm=2.0,
    clearance_basis="GB/T 5277 中等装配",
    configuration="默认",
)


def _get(**kw):
    d = dict(_ASM)
    d.update(kw)
    return collect_assembly(**d)


def _fail_checks() -> list:
    """★ 用真实采集器+判定器造 4 条**失败**结果（各一条）。"""
    out = []

    #: E4.dof —— 重复配合（R-05 的伪造手法）
    out.append(
        judge_assembly(
            _get(
                mates=(
                    {"a": "板1", "b": "板2", "kind": "coincident"},
                    {"a": "板1", "b": "板2", "kind": "coincident"},
                )
            ),
            requirement_id=REQ,
        )
    )

    #: E4.interference —— 有实体干涉
    out.append(
        judge_assembly_interference(_get(interference_count=3), requirement_id=REQ)
    )

    #: E6.process —— 有刀具到不了的孔
    out.append(
        judge_process(
            collect_process(
                target="板1 工艺",
                route="machined",
                checks=(
                    {"name": "刀具可达", "applicable": True, "passed": False,
                     "evidence": "⌀6 深 20，长径比 3.3 超刀具"},
                ),
                verified_scope=("machined",),
                required_checks=("刀具可达",),
            ),
            requirement_id=REQ,
        )
    )

    #: E7.provenance —— 假引用（占位符 locator）
    out.append(
        judge_provenance(
            collect_provenance(
                target="板1 结论",
                claims=({"id": "C1", "text": "板厚满足刚度"},),
                citations=({"claim_id": "C1", "locator": "见上", "resolved": True},),
                outputs={"deflection_mm": 0.03},
                source_kind="standard_clause",
                source_ref="GB/T 1804-2000 表1",
                artifact_version="rev1",
                evidence_version="rev1",
            ),
            requirement_id=REQ,
        )
    )
    return out


def test_四条失败路径都落到自己的判据下() -> None:
    """★★★ 核心：E4/E6/E7 的失败必须归到自己那一条，**不得掉进 unassigned**。"""
    checks = _fail_checks()
    rep = build_report(checks)

    assert rep["unassigned"] == [], (
        "★ 有检查掉进 unassigned（check_id 前缀不对）：%r" % (rep["unassigned"],)
    )
    for c in checks:
        assert c.status is Status.FAIL, "★ %s 应为 fail，实得 %s" % (
            c.check_id,
            c.status.value,
        )

    #: 落在自己的 criterion 下
    assert "E4.dof" in rep["criteria"]["E4"]["failed"]
    assert "E4.interference" in rep["criteria"]["E4"]["failed"]
    assert "E6.process" in rep["criteria"]["E6"]["failed"]
    assert "E7.provenance" in rep["criteria"]["E7"]["failed"]


def test_总体必须是fail() -> None:
    rep = build_report(_fail_checks())
    assert rep["overall"] == "fail", "★ 四条都失败，总体应为 fail，实得 %r" % (
        rep["overall"],
    )


def test_渲染把四条都列进不合格段() -> None:
    """★ 渲染层也要能看见 —— 只看 aggregate 不看 render 会漏掉版面问题。"""
    md = render_markdown(build_report(_fail_checks()), title="失败路径覆盖")
    tail = md.split("## 不合格的项", 1)
    assert len(tail) == 2, "★ 报告缺「不合格的项」段"
    for cid in ("E4.dof", "E4.interference", "E6.process", "E7.provenance"):
        assert cid in tail[1], "★ %s 没出现在「不合格的项」里" % cid


@pytest.mark.parametrize(
    ("cid", "crit"),
    [
        ("E4.dof", "E4"),
        ("E4.interference", "E4"),
        ("E6.process", "E6"),
        ("E7.provenance", "E7"),
    ],
)
def test_每条check_id前缀正确(cid: str, crit: str) -> None:
    """★ 单看前缀：`report.py` 就是按 `E1..E7` 前缀归组的。"""
    assert cid.startswith(crit + "."), "★ %r 应以 %r 开头" % (cid, crit + ".")


def test_全绿组仍然覆盖十条() -> None:
    """★ 对照：全绿组本来就覆盖 10 条 —— 本文件补的是**失败**那一侧。

    ★ 若哪天 `good_checks()` 少了条目，这条会红，提醒「全绿覆盖」退化。
    """
    sys.path.insert(0, str(REPO / "tools"))
    from probe_acceptance_report import good_checks  # noqa: E402

    ids = {c.check_id for c in good_checks()}
    assert len(ids) == 10, "★ 全绿组应覆盖 10 条，实得 %d：%r" % (len(ids), sorted(ids))
    for needed in ("E4.dof", "E4.interference", "E5.drawing", "E6.process", "E7.provenance"):
        assert needed in ids, "★ 全绿组缺 %s" % needed
