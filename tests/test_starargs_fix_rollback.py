"""★ spec 267：修 3 条 `starargs` 假阳性的**尝试被棘轮打回** ⇒ 记下**负结论**与**正方向**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py::com_args（★ `*args` 槽的处理，★ 已回滚处）
#         specs/253-arity-mismatch-triage/（★ 3 条 `starargs` 假阳性）· specs/266-counted-positions-impact/
# 定位:   ★ 266 说「3 条 `starargs` 要另想办法」⇒ ★ 本文件记：★ **「`*args` 为空 ⇒ 单列一桶」这个办法**试过、
#         ★★ **被门禁棘轮打回**（★ 丢 187 个已核调用点）⇒ ★ **负结论 + 正方向**。
# 官方依据: 无（★ 这是本仓门禁自身的口径）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 不改任何文件
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **尝试的读数对比**（★ 门禁自己的输出）。
ATTEMPT = {
    "before": {"arity": 16, "judged_entries": 21, "judged_sites": 313, "exit": 0},
    "after": {"arity": 14, "judged_entries": 20, "judged_sites": 124, "exit": 1},
    "reverted": {"arity": 16, "judged_entries": 21, "judged_sites": 313, "exit": 0},
}

#: ★★ **为什么回滚**：★ `_checked(table, "X")` 大多数调用**本来就不传 `*args`**
#:   （★ 对 0 参成员那是**正确**的）⇒ ★ 早返回把**正常调用**也吞了。
WHY = ("`_checked(table, \"X\")` 大多数调用本来就不传 `*args`（对 0 参成员是**正确**的）"
       "⇒ 早返回把**正常调用**也吞了")
#: ★★★ **正方向**。
RIGHT_DIRECTION = "先看**该成员计入了几个形参**，再判「`*args` 为空」算不算不可判"


def _attempt_failures(a: dict) -> list[str]:
    """★ 纯函数：① 尝试**确实**把 arity 降了；② 但**代价**是丢调用点；③ 回滚后恢复。"""
    out: list[str] = []
    if a["after"]["arity"] >= a["before"]["arity"]:
        out.append("尝试后 arity 没降 ⇒ ★ 尝试无效，结论要改")
    if a["after"]["arity"] != 14:
        out.append("尝试后 arity %d ≠ 14 ⇒ 请复核" % a["after"]["arity"])
    #: ★★ 代价：★ 已核调用点**大幅缩水**。
    lost = a["before"]["judged_sites"] - a["after"]["judged_sites"]
    if lost != 189:
        out.append("丢的调用点 %d ≠ 189 ⇒ 请复核" % lost)
    if a["after"]["judged_sites"] >= a["before"]["judged_sites"]:
        out.append("尝试后调用点没少 ⇒ ★ 「代价太大」的结论要改")
    if a["after"]["exit"] == 0:
        out.append("尝试后门禁竟 `exit 0` ⇒ ★ 棘轮没生效，结论要改")
    #: ★ 回滚后**必须完全恢复**。
    if a["reverted"] != a["before"]:
        out.append("回滚后读数没恢复 ⇒ 回滚不彻底")
    return out


# ── ① ★★★ 尝试**被棘轮打回**（★ arity 降了 2，但丢 189 个调用点）────
def test_the_attempt_was_rejected_by_the_ratchet():
    """★★★ 「`*args` 为空 ⇒ 单列一桶」把 `arity` 从 **16 降到 14**，★ **但丢了 189 个已核调用点**
    （**313 → 124**）、★ 且**可核分发口 21 → 20** ⇒ ★ 门禁 **`exit 1`（棘轮打回）**。

    ★★ **为什么这条值钱**：★ 不记 ⇒ ★ 下一个人会**再试一遍同一个办法**；
    ★ 记了 ⇒ ★ **直接跳到正方向**。
    """
    bad = _attempt_failures(ATTEMPT)
    assert not bad, "尝试的结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 源码里**不许**再出现 `starred`（★ 已回滚）──────────────────
def test_the_rollback_is_in_place():
    """★★★ `com_args` 里**不许**再有 `starred` 桶 —— ★ 已回滚，★ 且**回滚理由写在注释里**。

    ★ 能红的判据：★ 谁把那个早返回加回去 ⇒ 当场红。
    """
    src = (SCRIPTS / "check_dispatch_byref_guard.py").read_text(encoding="utf-8")
    assert 'return ("starred", None, None)' not in src, \
        "`starred` 早返回又回来了 ⇒ ★ 会再丢调用点"
    assert "spec 267 **试过、已回滚**" in src, \
        "回滚理由没写在源码注释里 ⇒ ★ 下一个人会重试"


# ── ③ ★★ 负结论与正方向都要留档 ─────────────────────────────────────
def test_negative_result_and_right_direction_are_recorded():
    """★★ 负结论（★ 为什么不行）+ 正方向（★ 该怎么做）**两件都要留档**。"""
    assert "`*args`" in WHY and "吞" in WHY, "负结论不完整"
    assert "计入了几个形参" in RIGHT_DIRECTION, "正方向不完整"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① arity 没降；② 调用点没少；③ 回滚不彻底。"""
    assert not _attempt_failures(ATTEMPT), "正常读数被判红 ⇒ 判据过严"
    assert _attempt_failures(dict(ATTEMPT, after=dict(ATTEMPT["after"], arity=16))), \
        "arity 没降却未判出 ⇒ **空判据**"
    assert _attempt_failures(dict(ATTEMPT, after=dict(ATTEMPT["after"], judged_sites=313))), \
        "调用点没少却未判出 ⇒ **空判据**"
    assert _attempt_failures(dict(ATTEMPT, reverted={"arity": 14})), \
        "回滚不彻底却未判出 ⇒ **空判据**"
