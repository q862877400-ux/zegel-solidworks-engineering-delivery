"""★ S0 判据：三处执行入口必须能跑通，且不得靠放宽断言换绿。

## 为什么这个文件存在

`specs/348-s0-restore-official-path/` 的 SC-001～SC-003 要求三个入口各自可跑。
那三处修复前，失败原因是**三处不同的实现缺陷**（见
`docs/state/facts/R-engineering-path.md` R-03 / R-14 / R-15）：

- `compiler.py` 调了不存在的 `spec.allows()`
- `housing.py` 的 `FinalDod` 只剩字段，`evaluate()` 消失
- `planner.py` 把编译失败的候选带着**未解析的步骤**混进结果

本文件把「它们现在都能跑」变成**可重跑的断言**，而不是一句结论。

## 判据

① 三个入口各自不抛异常
② 编译失败的候选**不得**带着未解析步骤出现（`tool` 为空即失败）
③ 恢复后的 `FinalDod.evaluate()` 八条判据齐
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering import planner as PL  # noqa: E402
from engineering import registry as R  # noqa: E402
from engineering.compiler import compile_contract  # noqa: E402
from engineering.housing import FinalDod  # noqa: E402
import engineering_contract as ec  # noqa: E402

_SOLVABLE = "做一块100x60x20的安装板，四角四个φ6的孔，孔心距边10mm"


def _frozen(intent: str = "做一个安装板", *, domains=None):
    """★ 造一个**已冻结**的契约（编译器只吃冻结的）。

    ★ 用 `is None` 判 `domains` —— `{}` 是**有效输入**（真空域），不是「没传」。
    """
    c = ec.EngineeringContract(contract_id="S0-1", intent=intent)
    c.classify("intent", ec.InformationClass.KNOWN)
    c.safety_level = "普通"
    c.material = ec.MaterialRef("Q235", "GB/T 700", "2006")
    c.process = ec.ProcessIntent(kind="machined")
    c.datums.append(ec.Datum("安装结合面", semantic_role="mounting_interface"))
    c.load_cases.append(
        ec.LoadCase("面压", "static", ec.normalize_quantity(ec.Quantity(1.0, "N", "force")))
    )
    dom = {"outline": (0.01, 1.0)} if domains is None else domains
    for name, (lo, hi) in dom.items():
        c.parameter_domains[name] = ec.ParameterDomain(
            name, lo, hi, "m", allow_negative=False
        )
    c.obligations.append(
        ec.VerificationObligation("OB-1", "回读尺寸", evidence_kind="readback")
    )
    c.freeze()
    return c


def test_compiler_入口能跑通() -> None:
    """① `compile_contract` 对合法契约不抛 `AttributeError`。

    ★ 修复前：`compiler.py:594` 调 `spec.allows(k)`，而 `MethodSpec` 与其基类
      `ApplicabilityMixin` 都**没有** `allows` ⇒ 必抛 `AttributeError`。
    """
    out = compile_contract(_frozen(), device_class="plate")
    assert out is not None
    assert out.dag.nodes, "★ 编译结果没有 DAG 节点"


def test_越权判定用的是修改域而不是设备适用域() -> None:
    """① 的负例：域不在方法 `modification_domain` 内必须被拒。

    ★ 这条同时钉死「越权该由什么实现」——
      不是 `applies_to`（设备适用域），是 `modification_domain`（参数修改域）。
    """
    #: `plate` 方法的修改域是板的外形与厚度；`surface_finish` 不在其中
    contract = _frozen(domains={"surface_finish": (0.0, 1.0)})
    with pytest.raises(Exception) as ei:
        compile_contract(contract, device_class="plate")
    msg = str(ei.value).upper()
    assert "越权" in str(ei.value) or "OVERREACH" in msg


def test_finaldod_evaluate_八条判据齐() -> None:
    """② 恢复后的 `evaluate()` 必须给出八条判据的结果键。"""
    out = FinalDod().evaluate()
    for key in (
        "cases_ok",
        "obligations_ok",
        "failures_ok",
        "gates_ok",
        "evidence_ok",
        "claims_ok",
        "all_four_ok",
        "takeovers_visible",
    ):
        assert key in out, "★ `evaluate()` 少了判据键 %r" % key
    assert out["ok"] is False, "★ 空案例集必须判不通过，不得默认通过"


def test_空案例集不得判通过() -> None:
    """② 的负例：这是「不许自我认证」的最小形态。"""
    out = FinalDod().evaluate()
    assert out["cases_ok"] is False
    assert out["ok"] is False


def test_编译失败的候选不得带未解析步骤() -> None:
    """③ 规划出口：`tool` 为空的步骤不得出现在任何候选里。

    ★ 修复前：`expand_plan` 抛异常被 `except` 吞掉后，
      `pc.plan` 保持**未解析**状态（所有 `PlanStep.tool` 都是空串），
      而该候选仍被加入 `ps.candidates` ⇒ 下游按「已编译计划」消费会拿到空工具名。
    ★ 修复后：编译失败 ⇒ 保留候选（带 `compile_error`）但**清空步骤**，
      使「有步骤 ⇒ 一定已解析」成为可断言的不变式。
    """
    ps = PL.plan_from_requirement(_SOLVABLE)
    for c in ps.candidates:
        for s in c.plan.steps:
            assert s.tool, (
                "★ 候选 %s 的步骤 %r 没有解析到工具名 —— "
                "编译失败的候选必须清空步骤" % (c.method_id, s.step)
            )


def test_规划出口能跑通且候选都可编译() -> None:
    """③ 正例：四孔需求必须给出 3–5 个**全部可编译**的候选。"""
    ps = PL.plan_from_requirement(_SOLVABLE)
    assert 3 <= len(ps.candidates) <= 5
    assert len(ps.compilable) == len(ps.candidates), [
        (c.method_id, c.compile_error) for c in ps.candidates if not c.compile_ok
    ]
    assert ps.ok is True


def test_建注册表不抛重名异常() -> None:
    """③ 注册表能构建，且每个已准入条目都有 step_name 与 module/function（I3/I4）。"""
    reg = R.build_registry()
    assert reg, "★ 注册表为空"
    for name, d in reg.items():
        if d.admitted:
            assert d.step_name, "★ %s 已准入但没有 step_name（违 I3）" % name
            assert d.module and d.function, "★ %s 已准入但缺 module/function（违 I4）" % name
        else:
            assert d.reject_reason, "★ %s 未准入但没有理由（违 I2）" % name
