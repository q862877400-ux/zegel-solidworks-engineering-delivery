"""★ EC02 T07 判据 —— **标准版本变化的影响清单** + 证据自动标过期。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/rules.py`（★ `version_impact`）
#         `specs/304-ec02-rules-and-standards/spec.md`（★ FR-007 · US5）
# 定位:   ★ EC02 **T07**（★ 逐字：「★ 标准版本变化形成影响清单；★ 证据自动标过期；
#         ★ **不能只改数据库版本号**」）。
# 官方依据: ★ 标准号样例来自本会话 KS 的**真实读数**（★ `baseline.md` §二）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM · ★ 不调 LLM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import rules as R


def _reg() -> R.RuleRegistry:
    reg = R.RuleRegistry()
    reg.add(R.Rule(id="R-A", statement="边距规则", unit="m",
                   applicable_devices=("plate",),
                   source=R.StandardRef(standard_no="GB/T 1803-2003", clause="1",
                                        effectiveness=R.Effectiveness.EFFECTIVE,
                                        verified_on="2026-10-10"),
                   threshold=0.010, priority=1))
    reg.add(R.Rule(id="R-B", statement="轴强度规则", unit="m",
                   applicable_devices=("shaft",),
                   source=R.StandardRef(standard_no="GB 51022-2015", clause="3.2.4",
                                        effectiveness=R.Effectiveness.EFFECTIVE,
                                        verified_on="2026-10-10"),
                   threshold=0.020, priority=1))
    return reg


def test_t07_version_change_marks_old_verdicts_expired():
    """★★★★★ T07：★ **换版 ⇒ 旧结论自动标 `expired`**（★ 且**不得**继续放行）。

    ★★ 依据（★ 计划 §5 EC02-T07 逐字）：「★ 标准版本变化形成**影响清单**；
      ★ 证据**自动标过期**；★ **不能只改数据库版本号**」。
    """
    reg = _reg()
    d_a = reg.decide("R-A", "plate", value=0.005)       #: ★ pass
    d_b = reg.decide("R-B", "shaft", value=0.005)       #: ★ pass
    assert d_a.verdict == R.Verdict.PASS and d_b.verdict == R.Verdict.PASS
    #: ★★ 只换 **R-A 依据的那个标准**的版本
    out = R.version_impact([d_a, d_b], reg, {"GB/T 1803-2003": ("2003", "2026")})
    assert out["ok"] is True
    assert out["affected_count"] == 1, "★ 影响面不对：%r" % out["affected"]
    item = out["affected"][0]
    assert item["rule_id"] == "R-A", "★ 受影响的是 %r" % item["rule_id"]
    #: ★★★ **自动标过期** + ★ **结论降为 `unknown`**
    assert item["expired"] is True, "★★ 没标过期 ⇒ ★ 旧结论会继续被用"
    assert item["verdict_after"] == R.Verdict.UNKNOWN, (
        "★★ 换版后旧结论仍是 %r ⇒ ★ 违反「不能只改版本号」" % item["verdict_after"])
    #: ★★ 不受影响的**不动**
    assert out["unaffected"] == ["R-B"], "★ 无关规则被牵连：%r" % out["unaffected"]


def test_t07_version_change_requires_rejudgement():
    """★★★ T07：★ **有受影响 ⇒ 必须重判**（★ 不是「改个号就完事」）。"""
    reg = _reg()
    d = reg.decide("R-A", "plate", value=0.005)
    out = R.version_impact([d], reg, {"GB/T 1803-2003": ("2003", "2026")})
    assert out["requires_rejudgement"] is True, (
        "★★ 换版后不要求重判 ⇒ ★ 那就是「只改数据库版本号」")


def test_t07_no_change_means_no_impact():
    """★★ T07：★ **没换版 ⇒ 无影响**（★ 不能瞎报）。"""
    reg = _reg()
    d = reg.decide("R-A", "plate", value=0.005)
    out = R.version_impact([d], reg, {})
    assert out["affected_count"] == 0, "★★ 没换版却报了影响"
    assert out["requires_rejudgement"] is False
    assert out["unaffected"] == ["R-A"]


def test_t07_impact_carries_the_version_pair_and_a_basis():
    """★★ T07：★ 影响项必须带**版本对**与**依据**（★ 可复核）。"""
    reg = _reg()
    d = reg.decide("R-A", "plate", value=0.005)
    out = R.version_impact([d], reg, {"GB/T 1803-2003": ("2003", "2026")})
    item = out["affected"][0]
    assert item["version_change"] == {"from": "2003", "to": "2026"}, (
        "★ 版本对没记全：%r" % item["version_change"])
    assert item["basis"], "★ 影响项没有依据 ⇒ 不可复核"
    #: ★★ 依据里必须**明写**「不能只改版本号」这条
    assert "不能只改版本号" in item["basis"], (
        "★ 依据里没写清「为什么换版要重判」")


def test_t07_expired_evidence_cannot_be_released():
    """★★★ T07：★ **过期证据不得放行**（★ 与 EC00 的 `expired` 同族）。"""
    reg = _reg()
    d = reg.decide("R-A", "plate", value=0.005)
    out = R.version_impact([d], reg, {"GB/T 1803-2003": ("2003", "2026")})
    after = out["affected"][0]["verdict_after"]
    assert after not in R.Verdict.RELEASING, (
        "★★ 过期后的结论仍是放行态 %r" % after)
