"""★ `shape_problems`：只验「能不能作为依据」，**不验值对不对、不给默认值**。

## 它与 `missing_confirmations` 的分工（必须一起测）

| 函数 | 判什么 | 全空契约应报什么 |
|---|---|---|
| `missing_confirmations` | **有没有填** | 报 material/load_case/… 五项 + 附加项 |
| `shape_problems` | 填的**能不能用** | **报 0 项**（空不是形状问题） |

★ 合并成一个「缺 N 项」会丢失信息：读者分不清「还没填」与「填了但不可用」。

## 右侧（不该报的）同样重要

`shape_problems` 加严之后，**合法填法不能被误伤** —— 否则工程负责人会不敢填。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

import engineering_contract as ec  # noqa: E402
from engineering.acceptance import s2_requirements as s  # noqa: E402


def _mk(**kw):
    kw.setdefault("contract_id", "T")
    kw.setdefault("intent", "x")
    return ec.EngineeringContract(**kw)


def _fields(contract) -> list:
    return [x["field"] for x in s.shape_problems(contract)]


# ── 左侧：该报的 ──────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "name",
    ["钢", "45 钢", "普通碳钢", "Q235"],
)
def test_材料没有标准号要报(name: str) -> None:
    """★★ 只写牌号、追不到标准 ⇒ 无法核对（`Q235` 没有标准号也报）。"""
    assert "material" in _fields(_mk(material=ec.MaterialRef(name=name)))


def test_材料标准号写进_standard_字段也算() -> None:
    """★ 标准号写在哪一边都行 —— 判据看的是「能不能追到标准」。"""
    got = _fields(
        _mk(material=ec.MaterialRef(name="碳素结构钢", standard="GB/T 700-2006"))
    )
    assert "material" not in got


@pytest.mark.parametrize("mag", ["500", "大", "按经验", ""])
def test_载荷没有数值加量纲要报(mag: str) -> None:
    got = _fields(_mk(load_cases=[ec.LoadCase(name="c", kind="k", magnitude=mag)]))
    assert "load_case" in got, "★ magnitude=%r 应被报出" % mag


def test_基准没有语义角色要报() -> None:
    got = _fields(_mk(datums=[ec.Datum(name="A", semantic_role="")]))
    assert "datums" in got


def test_每个问题都带_hint() -> None:
    """★ 只报问题不给人怎么填，等于把活退回去。"""
    for prob in s.shape_problems(_mk(material=ec.MaterialRef(name="钢"))):
        assert prob.get("hint"), "★ %s 的问题缺 hint" % prob.get("field")


# ── 右侧：不该报的（防误伤） ──────────────────────────────────────────

@pytest.mark.parametrize(
    "mag",
    ["500 N", "12.5 kN", "2 MPa", "0.03 mm", "1200 rpm", "15%"],
)
def test_合法载荷单位不误伤(mag: str) -> None:
    got = _fields(_mk(load_cases=[ec.LoadCase(name="c", kind="k", magnitude=mag)]))
    assert "load_case" not in got, "★ magnitude=%r 是合法形态，被误伤" % mag


@pytest.mark.parametrize(
    "std",
    ["GB/T 700-2006", "GB 30871-2022", "ASTM A36", "ISO 2768", "JB/T 1234-2010"],
)
def test_合法标准号不误伤(std: str) -> None:
    got = _fields(_mk(material=ec.MaterialRef(name="结构钢", standard=std)))
    assert "material" not in got, "★ 标准号 %r 被误伤" % std


def test_基准有角色不误伤() -> None:
    got = _fields(_mk(datums=[ec.Datum(name="A", semantic_role="主基准")]))
    assert "datums" not in got


# ── 两者的分工边界 ────────────────────────────────────────────────────

def test_全空契约形状问题为零() -> None:
    """★★ 关键边界：**空不是形状问题** —— 空由 `missing_confirmations` 负责。

    ★ 若这里也报，读者就分不清「还没填」与「填了但不可用」。
    """
    assert s.shape_problems(_mk()) == []


def test_全空契约缺项不为零() -> None:
    """★ 对照：全空契约由缺项检查负责，应报出五项以上。"""
    missing = s.missing_confirmations(_mk())
    assert "material" in missing
    assert "load_case" in missing
    assert "datums" in missing


def test_填了但不合格时缺项检查仍说缺() -> None:
    """★ 两者**不互相顶替**：形状不合格 ⇒ 缺项检查仍报缺（因为它只看非空？）——

    ⚠ 这里如实记录现状：`missing_confirmations` 只看非空，
      所以「材料=钢」它**不报**，只有 `shape_problems` 报。
      ⇒ 冻结前必须**两个都跑**，任一有输出就不得冻结。
    """
    c = _mk(material=ec.MaterialRef(name="钢"))
    assert "material" not in s.missing_confirmations(c), (
        "★ 现状：非空即不算缺 —— 所以必须同时跑 shape_problems"
    )
    assert "material" in _fields(c)
