"""★ 阻塞台账门禁的负例自证：三种伪造台账都要抓得到。

## 为什么必须有这一组

`AGENTS.md` 第十八节与 `docs/union-conventions.md` 的同一条纪律：
**判据必须能证明它抓得到坏输入** —— 否则「PASS」只证明它没在看。

本文件对 `scripts/check_s3_blockers.py` 的三种失效形态各造一个负例：

| 负例 | 形态 | 门禁应当 |
|---|---|---|
| ① | 报告里有不合格项，台账**少登记**一条 | fail，并点名那一条 |
| ② | 台账**多登记**一条（问题已解决却没删） | fail，并指出陈旧 |
| ③ | 台账的 `evidence` 路径**不存在** | fail，并指出哪条路径 |

★ 另测两个**不该误伤**的方向：
  ④ 台账与报告完全一致 ⇒ pass
  ⑤ 报告里某一段注释性标题缺失（该段本来就没有条目）⇒ 仍 pass
     —— 否则「没有 unknown 项」会被误判成「格式变了」。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

import check_s3_blockers as G  # noqa: E402

#: 一份最小可解析的报告（两段标题 + 各一条）
_REPORT = """# 验收报告

## 逐条状态

| E2 | 参数化可重建 | ❌ fail |

## 不合格的项

- `E2.rebuild`：孔位不随板宽联动

## 未测到的项（不等于合格）

- `E2.hole_readback`：孔型没测到

## 未检查的判据

- E4、E5
"""


def _ledger(cids, *, evidence="docs/PLAN.md"):
    lines = ["blockers:"]
    for cid in cids:
        lines += [
            "  - check_id: %s" % cid,
            "    cause: toolchain",
            "    owner: agent",
            "    summary: 测试用",
            "    evidence:",
            "      - %s" % evidence,
        ]
    return "\n".join(lines) + "\n"


def test_一致时通过() -> None:
    ok, problems = G.check(_REPORT, _ledger(["E2.rebuild", "E2.hole_readback"]))
    assert ok is True, "★ 一致时应通过，实得问题：%r" % (problems,)


def test_少登记一条必须红() -> None:
    """★★ 负例①：有不合格项没登记 ⇒ 读者会当成「没跑」。"""
    ok, problems = G.check(_REPORT, _ledger(["E2.rebuild"]))
    assert ok is False
    assert any("E2.hole_readback" in p and "没登记" in p for p in problems), (
        "★ 应点名未登记的那一条，实得：%r" % (problems,)
    )


def test_多登记一条必须红() -> None:
    """★★ 负例②：陈旧阻塞 —— 问题解决了却没删。"""
    ok, problems = G.check(_REPORT, _ledger(["E2.rebuild", "E3.tree"]))
    assert ok is False
    assert any("E3.tree" in p and "陈旧" in p for p in problems), (
        "★ 应指出陈旧，实得：%r" % (problems,)
    )


def test_证据路径不存在必须红() -> None:
    """★★ 负例③：证据断了。"""
    ok, problems = G.check(
        _REPORT, _ledger(["E2.rebuild", "E2.hole_readback"],
                         evidence="docs/不存在这个文件.md")
    )
    assert ok is False
    assert any("证据文件不存在" in p for p in problems), (
        "★ 应指出断掉的证据，实得：%r" % (problems,)
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [("cause", "因为工具"), ("owner", "老板")],
)
def test_分类自造必须红(field: str, value: str) -> None:
    """★ `cause` / `owner` 是封闭词表，自造值不算表态。"""
    text = _ledger(["E2.rebuild", "E2.hole_readback"]).replace(
        "%s: %s" % (field, "toolchain" if field == "cause" else "agent"),
        "%s: %s" % (field, value),
    )
    ok, problems = G.check(_REPORT, text)
    assert ok is False
    assert any("封闭词表" in p for p in problems), (
        "★ 应指出自造值，实得：%r" % (problems,)
    )


def test_报告为空必须红() -> None:
    ok, problems = G.check("", _ledger([]))
    assert ok is False
    assert any("报告是空的" in p for p in problems)


def test_两段标题都找不到必须红() -> None:
    """★★ 渲染格式变了 ⇒ 宁可红，不静默空转。"""
    ok, problems = G.check("# 一份没有那两段的报告\n", _ledger([]))
    assert ok is False
    assert any("渲染格式变了" in p for p in problems), (
        "★ 应报格式变化，实得：%r" % (problems,)
    )


def test_某一段没有条目不算格式变化() -> None:
    """★ 不该误伤：只有「不合格」段、没有「未测到」段 ⇒ 仍应能判。"""
    report = _REPORT.split("## 未测到的项（不等于合格）")[0]
    ok, problems = G.check(report, _ledger(["E2.rebuild"]))
    assert ok is True, "★ 缺一段但有条目一致，不该误伤：%r" % (problems,)


def test_报告里两段的check_id都抽得到() -> None:
    ids, detail = G.failing_check_ids(_REPORT)
    assert ids == {"E2.rebuild", "E2.hole_readback"}
    assert dict(detail)["## 不合格的项"] == 1
    assert dict(detail)["## 未测到的项（不等于合格）"] == 1


def test_真仓库的台账与报告一致() -> None:
    """★ 端到端：真实文件必须一致（这条红说明有人改了报告没更新台账，或反之）。"""
    report = (REPO / "specs" / "350-first-part-delivery" / "s3-acceptance.md")
    ledger = REPO / "docs" / "s3-blockers.yaml"
    if not report.is_file():
        pytest.skip("验收报告未生成（需先跑 tools/run_s3_acceptance.py）")
    ok, problems = G.check(
        report.read_text(encoding="utf-8"), ledger.read_text(encoding="utf-8")
    )
    assert ok is True, "★ 真仓库的台账与报告不一致：%r" % (problems,)
