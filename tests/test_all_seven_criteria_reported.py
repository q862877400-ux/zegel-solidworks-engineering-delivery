"""★ 七条判据在验收报告里都要有位置（charter A8）。

## 为什么

`docs/PROJECT-CHARTER.md` 的 A8 要求「进度按 S0–S6 报：首件 **E1–E7 逐条**状态」。

第 60 轮之前，报告里 E5/E6/E7 是「⬜ 未检查」——
**没有原因的分类等于没分类**：读者分不出「还没做」和「做了但不适用」。
把它们接成 `unknown` + **明确原因**之后，报告有 10 条检查、覆盖七条判据。

## 三条的真实原因（都不是工具能力问题）

| 判据 | 原因 |
|---|---|
| E5 图样合规 | 首件还没有图；图样范围未冻结（S2 `drawing_scope`） |
| E6 工艺可行 | 工艺路线未冻结（S2 `process`） |
| E7 结论可溯源 | 出处链要等前六项都有结论 |

## 本文件钉什么

① 运行器里 E5/E6/E7 三条都要接（走采集器 → 判定器，不手工塞字符串）
② 汇总时三条都要进 `_checks`
③ 每条都要写明 `blocked_by`（原因不能缺）
④ 台账里三条都要登记（`check_s3_blockers` 双向校验的另一半）
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_RUNNER = REPO / "tools" / "run_s3_acceptance.py"
_LEDGER = REPO / "docs" / "s3-blockers.yaml"


def _runner() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_三条都接了采集器与判定器() -> None:
    src = _runner()
    for name in (
        "collect_drawing",
        "judge_drawing",
        "collect_process",
        "judge_process",
        "collect_provenance",
        "judge_provenance",
    ):
        assert name in src, "★ 运行器没接 `%s`" % name


def test_三条都进汇总() -> None:
    src = _runner()
    i = src.find("_checks.extend(c for c in (res_e5")
    assert i > 0, "★ E5/E6/E7 没进 `_checks` ⇒ 报告里不会出现"


def test_每条都写了原因() -> None:
    """★ 只有状态没有原因 ⇒ 读者分不出「还没做」和「不适用」。"""
    src = _runner()
    for key in ('"blocked_by": "S2 drawing_scope', '"blocked_by": "S2 process',
                '"blocked_by": "待前六项'):
        assert key in src, "★ 缺原因标注：%s" % key


def test_台账登记了三条() -> None:
    t = _LEDGER.read_text(encoding="utf-8")
    for cid in ("E5.drawing", "E6.process", "E7.provenance"):
        assert "check_id: %s" % cid in t, "★ 台账没登记 `%s`" % cid


def test_不手工塞状态字符串() -> None:
    """★★ 必须走采集器 → 判定器；直接塞 `"unknown"` 等于绕过判据层。"""
    src = _runner()
    for cid in ("E5", "E6", "E7"):
        assert "judge_" in src and ("res_%s = judge_" % cid.lower()) in src, (
            "★ `%s` 不是走判定器得出的" % cid
        )
