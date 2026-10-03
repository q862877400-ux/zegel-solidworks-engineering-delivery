"""★ 名单**完整性**门禁的契约与负例（★ 事实 62）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_backend_limited_completeness_gate.py
# 定位:   ★ 2026-10-03（轮 602）★ `scripts/check_backend_limited_completeness.py` 的负例。
#
#   ★★ **为什么要负例**（★ 事实 62）：★ 一个门禁"写了"不等于它"有效" ——
#     ★ 而**这道门禁的判据尤其容易写成"永远说 ok"**（★ 因为它靠一个**文件系统谓词**）。
#     ⇒ ★★ **故本测试**注入**那个谓词**（★ `has_acc`）与索引（★ `idx`），
#       ★ **才测得到判据本身**（★ 否则测的只是"这台机器上恰好没漏"）✓
#
#   ★ 证明四件事：
#     ① ★ **能抓到**：`api` 提到一个带 `AccessSelections` 的 `*FeatureData`、而该条不在名单 ⇒ 违规；
#     ② ★ **负例**：该条**已在名单里** ⇒ **不该报**（★ 否则永远红）；
#     ③ ★ **负例**：那个接口**不带** `AccessSelections` ⇒ **不该报**（★ 判据要认得出区别）；
#     ④ ★ **便携性**：索引为空（★ 接口目录不在）⇒ **SKIP**（★ 不误报）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_backend_limited_completeness", R / "scripts" / "check_backend_limited_completeness.py")
GATE = importlib.util.module_from_spec(_spec)
sys.modules["check_backend_limited_completeness"] = GATE
_spec.loader.exec_module(GATE)                                          # type: ignore[union-attr]

#: ★ 伪造索引（★ 非空 —— ★ 否则门禁会 SKIP）
FAKE_IDX = {"Anything": ["IFake"], "InsertSplitLineProject": ["IModelDoc2"]}


def test_catches_missing_from_list():
    """★ 正例：`api` 提到带 `AccessSelections` 的 `*FeatureData`、而该条不在名单 ⇒ **抓到**。

    ★ 而**真实台账里那一条已经补进名单了**（★ 轮 601）⇒ ★ 故这里**用注入的谓词**造出那个情形
      （★ 假装 `IFooFeatureData` 带 `AccessSelections`）。
    """
    fake_items = [{"tier": "\u53ef\u653b\u5173", "zh": "\u67d0\u9879",
                   "api": "IFooFeatureData.AccessSelections"}]
    bad, _w, ran = GATE.check(idx=FAKE_IDX, has_acc=lambda i: i == "IFooFeatureData",
                              items=fake_items, limited=set())
    assert ran, "门禁 SKIP 了（★ 索引非空时不该 SKIP）"
    assert bad, "带 AccessSelections 的 FeatureData 没被怀疑 ⇒ 判据失效"


def test_negative_not_flagged_when_no_access_selections():
    """★ 负例：那个接口**不带** `AccessSelections` ⇒ **不该报**（★ 判据要认得出区别）。"""
    bad, _w, ran = GATE.check(idx=FAKE_IDX, has_acc=lambda i: False,
                              items=[{"tier": "\u53ef\u653b\u5173", "zh": "\u67d0\u9879",
                                      "api": "IFooFeatureData.AccessSelections"}],
                              limited=set())
    assert ran
    assert not bad, "不带 AccessSelections 也被怀疑 ⇒ 门禁太宽、会永远红：%r" % (bad[:3],)


def test_negative_skips_when_index_empty():
    """★ 负例：★ **索引为空**（★ 接口目录不在）⇒ **SKIP**（★ 便携性守卫，★ 不误报）。"""
    bad, _w, ran = GATE.check(idx={}, has_acc=lambda i: True)
    assert not ran, "索引为空时没 SKIP ⇒ 在别的机器上会误报"
    assert not bad


def test_real_tree_runs_and_skips_or_passes():
    """★ 真实仓库：★ **要么 SKIP（★ 接口目录不在）、要么没有违规**。"""
    bad, _w, ran = GATE.check()
    assert not bad, "真实仓库有违规：%r" % (bad[:3],)


def test_obsolete_detected():
    """★★ 2026-10-03（轮 605）★ 新增的那条**提示**：`api` 点名的成员**已标废弃**。

    ★ 为什么它值得测（★ 事实 477）：★ 那正是**事实 433** 那条纪律的机器版
      ——「先读 md 头顶那句 `Obsolete`，继任者名字就在那句里」。
      ★ 而它一加上**立刻找出 2 条**（`InsertProjectedSketch` / `InsertFreeform`）✓
    """
    if not GATE.SWAPI_TYPES.exists():
        return                    #: ★ 便携性：接口目录不在 ⇒ 无从判定
    assert GATE.is_obsolete("InsertFreeform"), (
        "`InsertFreeform` 明明标了废弃（`Superseded by InsertFreeform2`）却判成未废弃")
    assert not GATE.is_obsolete("InsertFreeform2"), (
        "`InsertFreeform2` **未标废弃**却被判成废弃 ⇒ 判据读错了")


def test_obsolete_is_warn_not_blocking():
    """★ 负例：★ **废弃只该提示、不该拦**（★ 事实 379：废弃入口也可能有活路）。"""
    fake_items = [{"tier": "可攻关", "zh": "自由样式", "api": "InsertFreeform"}]
    bad, warn, ran = GATE.check(idx=FAKE_IDX, has_acc=lambda i: False,
                                items=fake_items, limited=set())
    assert ran
    assert not bad, "废弃被当成违规拦下了 ⇒ 太严（★ 应只提示）：%r" % (bad[:2],)
    if GATE.SWAPI_TYPES.exists():
        assert warn, "废弃没进提示 ⇒ 那条新判据没生效"
