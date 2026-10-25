"""★ 采集器空输入 ⇒ `unknown`（不是 pass、也不是 fail）+ E1 接受 `None`。

## 本文件钉两件事

### ① 七个采集器的空输入必须判 `unknown`

第 34 轮审计（探针 `output/` 一次性脚本）实测：七处**全部正确**判 `unknown`。
本文件把那一刻的状态变成回归守卫 —— 以后谁把 `complete` 改宽了，这里就红。

★ 为什么这件事值得单独守：
  `unknown` 与 `fail` 混同 ⇒ 报告失去「没查」与「查出错」的区分能力；
  `unknown` 与 `pass` 混同 ⇒ 没数据也能通过（最糟）。
  第 33 轮就是这样在孔量测与特征树上抓到两处**误判 fail**。

### ② `collect_sketch_constraint` 必须接受 `None`（表达「数值路径没量过」）

它的 docstring 自己写着「真机拿不到那三个数，填 0 就是**先填返回值**」（禁止），
但原形参是 `int`：填 `None` 会崩 `TypeError: '>' not supported between NoneType and int`
⇒ 真机调用方**没有合法表达方式**。第 34 轮修成接受 `None`。

★ 别把 `None` 与 `0` 混为一谈：
  `None` = 没量过；`0` = 量到 0 个。两者对 `complete` 的影响不同。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e1_sketch import (  # noqa: E402
    collect_sketch_constraint,
    judge_sketch_constraint,
)
from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_rebuild,
    collect_reference_stability,
    judge_rebuild,
    judge_reference_stability,
)
from engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly,
    judge_assembly_interference,
)
from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    collect_drawing,
    collect_process,
    judge_drawing,
    judge_process,
)
from engineering.acceptance.e7_provenance import (  # noqa: E402
    collect_provenance,
    judge_provenance,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"


# ── ① 七处空输入 ⇒ unknown ────────────────────────────────────────────


def _empty_cases():
    """★ 每个采集器的「什么都没给」输入。

    ★ 不用 `pytest.mark.parametrize` 传采集器对象，是为了让失败信息直接说人话。
    """
    return [
        (
            "E2.rebuild",
            lambda: judge_rebuild(
                collect_rebuild(
                    target="板1", opened_existing=False, changed_params=(),
                    rebuild_errors=0,
                    drawing_is_current=False,
                ),
                requirement_id=REQ,
            ),
        ),
        (
            "E3.reference_stability",
            lambda: judge_reference_stability(
                collect_reference_stability(target="板1", steps=()),
                requirement_id=REQ,
            ),
        ),
        (
            "E4.dof",
            lambda: judge_assembly(
                collect_assembly(
                    target="装配", components=(), mates=(), target_dof=0,
                    interference_count=0, min_clearance_mm=2.0,
                    clearance_basis="", configuration="",
                ),
                requirement_id=REQ,
            ),
        ),
        (
            "E4.interference",
            lambda: judge_assembly_interference(
                collect_assembly(
                    target="装配", components=(), mates=(), target_dof=0,
                    interference_count=0, min_clearance_mm=2.0,
                    clearance_basis="", configuration="",
                ),
                requirement_id=REQ,
            ),
        ),
        (
            "E5.drawing",
            lambda: judge_drawing(
                collect_drawing(
                    target="图", required_items=(), bound_items=(),
                    model_revision="", drawing_revision="",
                    material_from_requirement=False, template_ok=False,
                ),
                requirement_id=REQ,
            ),
        ),
        (
            "E6.process",
            lambda: judge_process(
                collect_process(
                target="工艺", route="", checks=(), verified_scope=(),
                required_checks=("刀具可达",),
            ),
                requirement_id=REQ,
            ),
        ),
        (
            "E7.provenance",
            lambda: judge_provenance(
                collect_provenance(
                    target="结论", claims=(), citations=(), outputs={},
                    source_kind="", source_ref="",
                ),
                requirement_id=REQ,
            ),
        ),
    ]


@pytest.mark.parametrize(("name", "run"), _empty_cases(), ids=lambda v: str(v)[:24])
def test_空输入必须判unknown(name, run) -> None:
    """★★ 七处全部必须 `unknown` —— 不许 `pass`（没数据通过）、不许 `fail`（误判）。"""
    res = run()
    assert res.status is Status.UNKNOWN, (
        "★ %s 空输入应判 unknown，实得 %s：%s" % (name, res.status.value, res.reason[:90])
    )


def test_七个采集器空输入没有一个判pass() -> None:
    """★ 汇总断言：把七处一次看全，任何一处变成 pass 都红。"""
    passing = [n for n, run in _empty_cases() if run().status is Status.PASS]
    assert passing == [], "★★ 这些在空输入下判了 pass：%r" % (passing,)


# ── ② E1 接受 None ───────────────────────────────────────────────────


def test_E1数值路径全None不崩() -> None:
    """★★ 修之前这里抛 `TypeError: '>' not supported between NoneType and int`。

    ★ 真机形态：只有枚举可取，三个数值字段拿不到。
    """
    obs = collect_sketch_constraint(
        target="板1",
        entities=None,
        relations=None,
        dimensions=None,
        intentional_dof=None,
        solver_state="fully",
        solver_status_int=3,
        driving_dimensions=1,
    )
    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.PASS, "★ 枚举 3 + 驱动尺寸 1 应判 pass，实得 %s" % (
        res.status.value,
    )
    assert obs.values["numeric_measured"] is False, "★ 数值路径没量过要记下来"


def test_E1全None判unknown() -> None:
    obs = collect_sketch_constraint(
        target="板1",
        entities=None,
        relations=None,
        dimensions=None,
        intentional_dof=None,
        solver_state=None,
        solver_status_int=None,
        driving_dimensions=None,
    )
    assert obs.complete is False
    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.UNKNOWN


def test_E1量到0个实体与没量过不同() -> None:
    """★★ `None`（没量过）与 `0`（量到零个）不是一回事。

    ★ 若把两者混同，`complete` 就会在「没量」时也说「量过了」。
    """
    none_obs = collect_sketch_constraint(
        target="板1", entities=None, relations=None, dimensions=None,
        intentional_dof=0, solver_state=None, solver_status_int=None,
        driving_dimensions=None,
    )
    zero_obs = collect_sketch_constraint(
        target="板1", entities=0, relations=(), dimensions=(),
        intentional_dof=0, solver_state=None, solver_status_int=None,
        driving_dimensions=None,
    )
    assert none_obs.values["numeric_measured"] is False
    assert zero_obs.values["numeric_measured"] is True
    #: 两者都没有枚举 ⇒ 都判 unknown（0 个实体也不算「量到证据」）
    for obs in (none_obs, zero_obs):
        assert judge_sketch_constraint(obs, requirement_id=REQ).status is Status.UNKNOWN


# ── ③ 反向：有数据时不许一律 unknown ──────────────────────────────────


def test_真机枚举路径仍能判pass与fail() -> None:
    """★★ 防「一律 unknown」的假修复 —— 有证据时必须给出真结论。"""
    ok = collect_sketch_constraint(
        target="板1", entities=None, relations=None, dimensions=None,
        intentional_dof=None, solver_state="fully", solver_status_int=3,
        driving_dimensions=2,
    )
    assert judge_sketch_constraint(ok, requirement_id=REQ).status is Status.PASS

    fixed = collect_sketch_constraint(
        target="板1", entities=None, relations=None, dimensions=None,
        intentional_dof=None, solver_state="fully", solver_status_int=3,
        driving_dimensions=0,
    )
    assert judge_sketch_constraint(fixed, requirement_id=REQ).status is Status.FAIL, (
        "★ 全固定（状态 3 但零驱动尺寸）必须判 fail"
    )
