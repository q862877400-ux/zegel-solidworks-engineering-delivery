"""★ S2：首件需求冻结的判据。

判据来源：`specs/350-first-part-delivery/spec.md` 的 FR-001～FR-003。

★ 核心：**缺项必须提问，不得填默认值**。
「悄悄填一个默认材料/工艺」是本项目历史上的通病，
它的后果是「看起来能跑，但没人确认过」。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import engineering_contract as ec  # noqa: E402
from engineering.acceptance.s2_requirements import (  # noqa: E402
    ADDITIONAL_REQUIRED,
    REQUIRED_CONFIRMATIONS,
    can_freeze,
    freeze,
    missing_confirmations,
    require_sheet,
)


def _blank() -> object:
    """★ 一个**什么都没确认**的契约。"""
    return ec.EngineeringContract(contract_id="S2-1", intent="做一块安装板")


def _full() -> object:
    """★ 五项必填 + 三项附加全部确认的契约。"""
    c = ec.EngineeringContract(contract_id="S2-2", intent="做一块安装板")
    c.material = ec.MaterialRef("Q235", "GB/T 700", "2006")
    c.load_cases.append(
        ec.LoadCase("面压", "static", ec.normalize_quantity(ec.Quantity(1.0, "N", "force")))
    )
    c.safety_level = "普通"
    c.process = ec.ProcessIntent(kind="machined")
    c.datums.append(ec.Datum("安装结合面", semantic_role="mounting_interface"))
    for name in ADDITIONAL_REQUIRED:
        c.clarifications.append({"field": name, "confirmed": True, "value": "已确认"})
    return c


def test_空契约不能冻结() -> None:
    """★ FR-001：五项必填任一为空 ⇒ 不得冻结。"""
    ok, miss = can_freeze(_blank())
    assert ok is False
    assert len(miss) > 0


def test_空契约报出全部五项必填() -> None:
    """★ 缺项清单必须**指名**，不能只说「不完整」。"""
    miss = missing_confirmations(_blank())
    for name in REQUIRED_CONFIRMATIONS:
        assert name in miss, "★ 空契约应报出 %r，实得 %r" % (name, miss)


def test_缺项不给默认值() -> None:
    """★★ 最核心的一条：`missing_confirmations` 只报缺，**不改契约**。

    ★ 如果在报缺的同时把 `material` 填成默认值，就变成
      「程序替工程负责人拍板」——这正是本项目历史上的通病。
    """
    c = _blank()
    before = (
        c.material,
        list(c.load_cases),
        c.safety_level,
        c.process,
        list(c.datums),
    )
    missing_confirmations(c)
    after = (
        c.material,
        list(c.load_cases),
        c.safety_level,
        c.process,
        list(c.datums),
    )
    assert before == after, "★ 报缺项时不得顺手填任何默认值"


def test_冻结时缺项抛错且指名() -> None:
    """★ FR-001：`freeze()` 在缺项时抛错，且错误信息里要点名缺什么。"""
    with pytest.raises(ValueError) as ei:
        freeze(_blank())
    msg = str(ei.value)
    assert "material" in msg or "未确认" in msg, "★ 报错要指认缺什么"


def test_五项齐了才能冻结() -> None:
    """★ 正例：五项 + 三项附加都确认后可以冻结。"""
    c = _full()
    ok, miss = can_freeze(c)
    assert ok is True, "★ 应当可冻结，仍缺：%r" % miss
    freeze(c)
    assert c.state == "frozen"


def test_只缺一项也不能冻结() -> None:
    """★ 逐项剔除，每剔一项都必须拦住 —— 防「少一项也放行」。"""
    for name in REQUIRED_CONFIRMATIONS:
        c = _full()
        if name == "material":
            c.material = None
        elif name == "load_case":
            c.load_cases.clear()
        elif name == "safety_level":
            c.safety_level = ""
        elif name == "process":
            c.process = None
        elif name == "datums":
            c.datums.clear()
        ok, miss = can_freeze(c)
        assert ok is False, "★ 缺 %s 时不该允许冻结" % name
        assert name in miss, "★ 应报出 %r，实得 %r" % (name, miss)


def test_附加三项未确认也不能冻结() -> None:
    """★ 首件额外要求：接口 / 图样范围 / 交付目的。

    ★ 这三项不在 `LEGACY_ALWAYS_MISSING` 里（那是通用契约的），
      是 S2 按 `docs/ENGINEERING-PATH.md` 第五节给首件补的。
    """
    c = _full()
    c.clarifications.clear()
    ok, miss = can_freeze(c)
    assert ok is False
    for name in ADDITIONAL_REQUIRED:
        assert name in miss


def test_承担者表每条都有执行者与验收者() -> None:
    """★ S2 完成标准：「每条硬要求有执行承担者和验收者」。"""
    sheet = require_sheet(_blank())
    assert sheet["ok"] is True, "★ 有不完整的行：%r" % sheet["incomplete"]
    assert sheet["total"] >= 7
    for row in sheet["rows"]:
        assert row["executor"], "★ %s 没有执行者" % row["requirement_id"]
        assert row["acceptor"], "★ %s 没有验收者" % row["requirement_id"]


def test_承担者表覆盖七条判据() -> None:
    """★ 七条 E 判据都要有对应的验收者。"""
    sheet = require_sheet(_blank())
    acceptors = {r["acceptor"] for r in sheet["rows"]}
    for e in ("e2", "e4", "e5", "e6", "e7"):
        assert any(e in a for a in acceptors), "★ 没有 %s 的验收者" % e


def test_材料牌号为空也算缺() -> None:
    """★ `MaterialRef` 存在但牌号为空，仍然算未确认。"""
    c = _full()
    c.material = ec.MaterialRef("", "", "")
    ok, miss = can_freeze(c)
    assert ok is False
    assert "material" in miss


def test_工艺种类为空也算缺() -> None:
    """★ `ProcessIntent` 存在但 `kind` 为空，仍然算未确认。"""
    c = _full()
    c.process = ec.ProcessIntent(kind="")
    ok, miss = can_freeze(c)
    assert ok is False
    assert "process" in miss
