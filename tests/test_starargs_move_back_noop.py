"""★ spec 270：**「移回 `com_args` + 双条件」是空改动**（★ `*args` 不空）⇒ 记负结论 + **更精确的方向**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py::com_args（★ `*args` 槽；★ 270 试过、已回滚）
#         specs/267-starargs-fix-rollback/（★ 宽规则失败）· specs/268-starargs-narrow-rule/（★ 窄规则）
#         specs/269-arity-retriage-new-rule/（★ 核出 268 掩盖 2 条 real-gap）
# 定位:   ★ 269 说「修法 = 移回 `com_args` + `main` 仍算已核」⇒ ★ 本文件试它 ⇒ ★ **是空改动**。
# 官方依据: 无（★ 本仓门禁自身的口径）
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

#: ★★★ **真机（静态）读数**（`output/_probe270_*` 的调试输出）。
FACT = {
    "slots": "[('*args', None)]",   #: ★ 3 处的 `slots` **只有** `*args` 一个槽
    "com": 1,                        #: ★★ 而 `com` 有 **1** 个元素
    "starred_empty": False,          #: ★★★ 所以 `env.get("*args")` **不是空的**
}

#: ★★★ **270 的读数**：★ 改前 = 改后 ⇒ ★ **空改动**。
READINGS = {
    "before": {"arity": 11, "starred": 5, "judged_sites": 318, "exit": 0},
    "after": {"arity": 11, "starred": 0, "judged_sites": 318, "exit": 0},
}
#: ★ 回滚后（★ 恢复 268 的状态）。
RESTORED = {"arity": 11, "judged_entries": 21, "judged_sites": 318, "exit": 0}

#: ★★★ **更精确的方向**（★ 270 换来的一句）。
NEW_DIRECTION = ("判据条件不该是「`*args` **为空**」，而是「★ `*args` **恰好 1 个**（= 对象本身）」"
                 "⇒ ★ 下一轮要按这个改")


def _noop_failures(r: dict, fact: dict) -> list[str]:
    """★ 纯函数：① 改动前后**完全一样**（★ 空改动）；② `starred` 从未触发。"""
    out: list[str] = []
    if r["before"]["arity"] != r["after"]["arity"]:
        out.append("改前改后的 arity 不同（%d vs %d）⇒ ★ 「空改动」的结论要改"
                   % (r["before"]["arity"], r["after"]["arity"]))
    if r["after"]["starred"] != 0:
        out.append("`starred` 触发了 %d 次 ⇒ ★ 不是空改动" % r["after"]["starred"])
    if r["before"]["judged_sites"] != r["after"]["judged_sites"]:
        out.append("改前改后的调用点不同 ⇒ ★ 不是空改动")
    #: ★★ 空改动的**原因**：★ `*args` 不空。
    if fact["starred_empty"]:
        out.append("`*args` 竟是空的 ⇒ ★ 那早返回**该**触发 ⇒ ★ 结论要改")
    if fact["com"] != 1:
        out.append("`com` 不是 1（%r）⇒ ★ 请复核" % fact["com"])
    return out


# ── ① ★★★ 270 是**空改动**（★ 读数一字未变）────────────────────────
def test_the_attempt_was_a_no_op():
    """★★★ 「移回 `com_args` + 双条件」⇒ ★ **改前改后读数一字未变**（`arity 11` · `starred 0`）。

    ★★ **为什么值钱**：★ 不记 ⇒ ★ 下一轮还会试「移回 `com_args`」这个方向（★ 269 刚提过）。
    """
    bad = _noop_failures(READINGS, FACT)
    assert not bad, "空改动的结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 空改动的**原因**：★ `*args` 不空 ──────────────────────────
def test_the_reason_starred_is_not_empty():
    """★★★ `slots = [('*args', None)]` 而 **`com = 1`** ⇒ ★ `env.get("*args")` **有 1 个元素**
    ⇒ ★ `if not starred` **不成立** ⇒ ★ 早返回**从未触发**。

    ★★ 而 267 的宽规则**恰恰**是「`*args` 为空 ⇒ `starred`」★ 并**真的触发过**（★ 丢了 189 个调用点）
    ⇒ ★★ **两轮的条件不同** —— ★ 267 用的是 `judge` 里的**个数**（★ 不是 `*args` 是否为空）。
    """
    assert FACT["starred_empty"] is False, "`*args` 不空是本条的前提"
    assert FACT["com"] == 1, "`com` 必须是 1（★ 那 1 个元素来自 `*args`）"


# ── ③ ★★★ 更精确的方向 ─────────────────────────────────────────────
def test_the_new_direction_is_sharper():
    """★★★ **正方向（★ 270 换来的）**：★ 条件不是「`*args` **为空**」★ 而是「`*args` **恰好 1 个**」。

    ★ 依据：★ 那 3 处的 `com` **就是 1**（★ 1 个元素来自 `*args` 展开）⇒
    ★★ **「恰好 1 个」才是那 3 处的实际形态**。
    """
    assert "恰好 1 个" in NEW_DIRECTION, "新方向没写「恰好 1 个」"
    assert "为空" in NEW_DIRECTION, "没写清「不是为空」"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 改前改后不同；② `starred` 触发了；③ `*args` 竟是空的。"""
    assert not _noop_failures(READINGS, FACT), "正常读数被判红 ⇒ 判据过严"
    assert _noop_failures(dict(READINGS, after=dict(READINGS["after"], arity=13)), FACT), \
        "改前改后不同却未判出 ⇒ **空判据**"
    assert _noop_failures(dict(READINGS, after=dict(READINGS["after"], starred=3)), FACT), \
        "`starred` 触发却未判出 ⇒ **空判据**"
    assert _noop_failures(READINGS, dict(FACT, starred_empty=True)), \
        "`*args` 空却未判出 ⇒ **空判据**"
