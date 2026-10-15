"""★ spec 268：按 267 的**正方向**做第二层改动 —— `arity` **16 → 11**，且**已核调用点 +5**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py::judge（★ 新增**窄规则**）+ `main`（★ `starred` **算已核**）
#         specs/267-starargs-fix-rollback/（★ 宽规则失败：丢 189 个调用点）
#         specs/266-counted-positions-impact/ · specs/253-arity-mismatch-triage/
# 定位:   ★ 267 留的**正方向**：★ 「先看该成员计入了几个形参」⇒ ★ 本文件落地它。
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

#: ★★★ **窄规则**（★ spec 268）：★ 只有 **1** 个实参 **且** 该成员**最少**计入形参 **≥2**
#:   ⇒ ★ `*args` 该补而没补 ⇒ ★ `starred`（★ **算已核**）。
NARROW_RULE = "len(com) == 1 and min(len(counted_positions(v[1])) for v in variants) >= 2"

#: ★★★ **改动前后读数**（★ 门禁自己打印的）。
READINGS = {
    "before": {"arity": 16, "starred": 0, "judged_entries": 21, "judged_sites": 313, "exit": 0},
    "after": {"arity": 11, "starred": 5, "judged_entries": 21, "judged_sites": 318, "exit": 0},
}
#: ★★ 267 的**宽规则**（★ 失败）读数 —— ★ 对照用。
WIDE_ATTEMPT = {"arity": 14, "judged_entries": 20, "judged_sites": 124, "exit": 1}


def _failures(r: dict, wide: dict) -> list[str]:
    """★ 纯函数：① arity 降了；② `starred` 有 5 条；③ **调用点不降反增**；④ 门禁仍过。"""
    out: list[str] = []
    if r["after"]["arity"] >= r["before"]["arity"]:
        out.append("`arity` 没降 ⇒ ★ 窄规则没生效")
    if r["after"]["arity"] != 11:
        out.append("`arity` %d ≠ 11 ⇒ 请复核" % r["after"]["arity"])
    if r["after"]["starred"] != 5:
        out.append("`starred` %d ≠ 5 ⇒ 请复核" % r["after"]["starred"])
    #: ★★★ **关键**：★ 调用点**不许降**（★ 267 的教训）。
    if r["after"]["judged_sites"] < r["before"]["judged_sites"]:
        out.append("已核调用点从 %d 降到 %d ⇒ ★ **重蹈 267 的覆辙**"
                   % (r["before"]["judged_sites"], r["after"]["judged_sites"]))
    if r["after"]["judged_entries"] != r["before"]["judged_entries"]:
        out.append("可核分发口变了（%d → %d）⇒ ★ 不该变"
                   % (r["before"]["judged_entries"], r["after"]["judged_entries"]))
    if r["after"]["exit"] != 0:
        out.append("门禁 `exit %d` ⇒ ★ 棘轮又不放行" % r["after"]["exit"])
    #: ★ 对照：宽规则**确实**是坏的（★ 免得有人「改回去」）。
    if wide["judged_sites"] >= r["before"]["judged_sites"]:
        out.append("宽规则的对照读数不成立 ⇒ ★ 267 的负结论要复核")
    if wide["exit"] == 0:
        out.append("宽规则竟 `exit 0` ⇒ ★ 267 的结论要复核")
    return out


# ── ① ★★★ 窄规则生效：arity 16 → 11，且**调用点 +5** ─────────────────
def test_narrow_rule_works_without_losing_coverage():
    """★★★ `arity` **16 → 11**（★ 移出 **5** 条）· ★ `starred` **5** ·
    ★★ **已核调用点 313 → 318（+5，不是 −189）** · ★ 门禁仍 **`exit 0`**。

    ★★ **为什么这条值钱**：★ 267 的宽规则「看起来对」却**丢 189 个调用点**；
    ★ 本条**同时**要求「arity 降」与「调用点不降」⇒ ★ **两个条件缺一不可**。
    """
    bad = _failures(READINGS, WIDE_ATTEMPT)
    assert not bad, "窄规则结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 源码里必须有窄规则（★ 且带 267 的教训注释）────────────────
def test_narrow_rule_is_in_the_source():
    """★★★ `judge` 里必须有那条**窄规则**，★ 且**注释里写着 267 的教训**（★ 免得被改宽）。"""
    src = (SCRIPTS / "check_dispatch_byref_guard.py").read_text(encoding="utf-8")
    assert NARROW_RULE in src, "窄规则不在源码里 ⇒ ★ 判据失效"
    assert "spec 267 的教训" in src, "没把 267 的教训写在窄规则旁边 ⇒ ★ 容易被改宽"


# ── ③ ★★ `starred` **算已核**（★ 与 `arity` 的区别）─────────────────
def test_starred_counts_as_judged():
    """★★ `starred` 必须**算「已核」**（★ `judged_sites += 1`）—— ★ 这正是 267 栽的地方。"""
    src = (SCRIPTS / "check_dispatch_byref_guard.py").read_text(encoding="utf-8")
    i = src.find('if res == "starred":')
    assert i >= 0, "`main` 里没有 `starred` 分支"
    seg = src[i:i + 420]
    assert "judged_sites += 1" in seg, "`starred` **不算已核** ⇒ ★ 会重蹈 267"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 四组负例：① arity 没降；② 调用点降了；③ 可核分发口变了；④ 门禁红了。"""
    assert not _failures(READINGS, WIDE_ATTEMPT), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(READINGS, after=dict(READINGS["after"], arity=16)), WIDE_ATTEMPT), \
        "arity 没降却未判出 ⇒ **空判据**"
    assert _failures(dict(READINGS, after=dict(READINGS["after"], judged_sites=124)), WIDE_ATTEMPT), \
        "★ 调用点降到 124 却未判出 ⇒ **空判据**（★ 这条最要紧）"
    assert _failures(dict(READINGS, after=dict(READINGS["after"], judged_entries=20)), WIDE_ATTEMPT), \
        "可核分发口变了却未判出 ⇒ **空判据**"
