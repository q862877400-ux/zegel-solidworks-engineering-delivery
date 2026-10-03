"""★ 测 `sw_hole_features.py` 的**判据层** —— ★ 处置 `JUDGE-C_D_E` 🔴 #1 · E5-2（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_hole_feature_judgement.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#1 · E5-2** 逐字：「★ batch72 孔向导 —— ★ 仓内 doc：
#   `★ 判据 = **特征树增量**` · ★ 而目标：`return { "ok": True,` ⇒ ★★ **无任何 before/after 取样**」✓
#   ★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_hole_features as H                                              # noqa: E402

REPORTS = [
    "create_through_hole_at_selection_report",
    "create_blind_hole_at_selection_report",
    "create_counterbore_hole_at_selection_report",
    "create_countersink_hole_at_selection_report",
    "create_semicircular_slot_at_selection_report",
    "create_hole_wizard_at_selection_report",
]


def test_no_report_hardcodes_ok_true() -> None:
    """★★★ 核心断言：★ **6 个 report 里一个都不许**再写死 `"ok": True`**（★ 那正是病灶）。"""
    bad = [fn for fn in REPORTS
           if re.search(r'"ok"\s*:\s*True', inspect.getsource(getattr(H, fn)))]
    assert not bad, "★ 仍有 report 写死 ok:True ⇒ 「特征没建成也报成功」：%s" % bad


def test_five_reports_use_shared_tree_judgement() -> None:
    """★ 那 5 个（★ 全委托给底层 `create_xxx` 的）**必须**走共享的树判据助手。"""
    miss = [fn for fn in REPORTS[:5]
            if "_with_tree_judgement" not in inspect.getsource(getattr(H, fn))]
    assert not miss, "★ 这些 report 没走树判据助手：%s" % miss


def test_wizard_declares_tree_delta() -> None:
    """★ 孔向导那条（★ 它自己不委托）也**必须**有 doc 承诺的「特征树增量」。"""
    src = inspect.getsource(H.create_hole_wizard_at_selection_report)
    assert "_before_wizard" in src and "tree_before" in src, (
        "★ 孔向导没做 doc 承诺的『特征树增量』判据")


def test_helper_returns_ok_false_when_nothing_added() -> None:
    """★★ **负例**：★ 若底层**什么都没建**（★ 树不变）⇒ `ok` **必须** `False`。

    ★ 用一个**假的底层函数**（★ 不建任何特征）喂给助手 ⇒ ★ 助手应当回 `ok=False` ✓
    """
    class _FakeModel:
        pass

    def _noop(*_a, **_k) -> dict:
        return {"feature_names": ()}          # ★ 底层回证据、★ 但没建任何东西

    out = H._with_tree_judgement(_FakeModel(), _noop)
    assert out["ok"] is False, "★★ 树没变却报了成功 ⇒ 静默成功（违反规则 6）：%r" % out
    assert out["new_features"] == []
    assert "verified_by" in out


def test_docstring_promise_is_still_there() -> None:
    """★ doc 里那句「判据 = 特征树增量」**必须**保留 —— ★ 它才是本次修复的目标契约。"""
    assert "特征树增量" in (H.__doc__ or "") or "特征树增量" in inspect.getsource(H), (
        "★ 找不到『特征树增量』这个承诺 ⇒ 修复的目标契约丢了")
