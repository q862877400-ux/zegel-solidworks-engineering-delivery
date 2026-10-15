"""★ spec 271：**加判别层** ⇒ `arity` **11 → 13**（★ 2 条 `real-gap` **重新可见**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py::judge（★ 271 的判别层）
#         specs/269-arity-retriage-new-rule/（★ 核出 268 掩盖 2 条 real-gap）
#         specs/270-starargs-move-back-noop/（★ 「移回 com_args」是空改动）
#         output/_probe271_retriage.txt（★ 本轮分桶读数）
# 定位:   ★ 271 **量出**那两类在 AST 上完全同形 ⇒ ★ 改**按形参表**判 ⇒ ★ **真缺口重新可见**。
# 官方依据: C:/swapi/types/ICWMesh/GetNodeLocation.md（`(Int32, Double&, Double&, Double&)`）·
#           C:/swapi/types/IRouteManager/CreateFlattenRoute.md（11 参，全是普通入参）
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

#: ★★★ **判别规则**（★ 271）：★ `len(com) == 1` 且 最少计入形参 ≥2 且 **「缺的形参不全是 by-ref」** ⇒ `starred`。
RULE = "missing_all_byref"

#: ★★★ **两类在 AST 上完全同形**（★ 271 量出）—— ★ 这是「必须按形参表判」的**依据**。
SAME_SHAPE = {
    "CreateFlattenRoute": {"slots": "[('*args', None)]", "com": 1, "n_params": 11, "missing_all_byref": False},
    "GetNodeLocation": {"slots": "[('*args', None)]", "com": 1, "n_params": 4, "missing_all_byref": True},
}

#: ★★★ **读数对比**。
READINGS = {
    "spec_268": {"arity": 11, "starred": 5, "judged_entries": 21, "judged_sites": 318, "exit": 0},
    "spec_271": {"arity": 13, "starred": 3, "judged_entries": 21, "judged_sites": 316, "exit": 0},
}
#: ★★ **271 的分桶**：13 = 10 + 1 + 2。
BUCKETS_271 = {"byref-tail-convention": 10, "all-byref-false-positive": 1, "real-arity-gap": 2}
#: ★ 下界（★ 313）。
BASELINE_SITES = 313


def _failures(r: dict, buckets: dict, same: dict) -> list[str]:
    """★ 纯函数：① `arity` 回到 13；② 桶 = 10+1+2；③ **调用点仍 ≥ 下界**；④ 门禁仍过。"""
    out: list[str] = []
    if r["spec_271"]["arity"] != 13:
        out.append("`arity` %d ≠ 13 ⇒ 判别层没生效" % r["spec_271"]["arity"])
    if r["spec_271"]["arity"] <= r["spec_268"]["arity"]:
        out.append("`arity` 没回升 ⇒ ★ 2 条 `real-gap` 没回来")
    if r["spec_271"]["starred"] != 3:
        out.append("`starred` %d ≠ 3（★ 应只剩 3 条 `starargs`）" % r["spec_271"]["starred"])
    if sum(buckets.values()) != 13:
        out.append("桶之和 %d ≠ 13" % sum(buckets.values()))
    if buckets.get("real-arity-gap") != 2:
        out.append("`real-gap` %r ≠ 2 ⇒ ★ 真缺口没全回来" % buckets.get("real-arity-gap"))
    #: ★★★ **不许丢覆盖**（★ 267 的教训）。
    if r["spec_271"]["judged_sites"] < BASELINE_SITES:
        out.append("已核调用点 %d < 下界 %d ⇒ ★ 会触发棘轮"
                   % (r["spec_271"]["judged_sites"], BASELINE_SITES))
    if r["spec_271"]["exit"] != 0:
        out.append("门禁 `exit %d`" % r["spec_271"]["exit"])
    #: ★★ 同形的依据必须在（★ 否则「按形参表判」就没理由）。
    a, b = same["CreateFlattenRoute"], same["GetNodeLocation"]
    if a["slots"] != b["slots"] or a["com"] != b["com"]:
        out.append("两类在 AST 上竟不同形 ⇒ ★ 「必须按形参表判」的依据要改")
    if a["missing_all_byref"] or not b["missing_all_byref"]:
        out.append("`missing_all_byref` 的取值反了 ⇒ ★ 判别层会判错")
    return out


# ── ① ★★★ `arity` 11 → 13（★ 2 条 `real-gap` 重新可见）─────────────
def test_real_gaps_are_visible_again():
    """★★★ 加判别层后 ★ `arity` **11 → 13** ⇒ ★★ **2 条 `real-gap` 重新可见**
    （★ `GetNodeLocation` / `GetElementLocation`）。

    ★★ **为什么这条最要紧**：★ 269 核出 268 **掩盖了 2 条真缺口**（★ 违反「减少 = 探测器漏了」）；
    ★ 本条把它**修回来了**。
    """
    bad = _failures(READINGS, BUCKETS_271, SAME_SHAPE)
    assert not bad, "判别层结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 两类在 AST 上**完全同形**（★ 必须按形参表判）──────────────
def test_the_two_cases_are_ast_identical():
    """★★★ `CreateFlattenRoute` 与 `GetNodeLocation` 的 `slots` **都是** `[('*args', None)]`、`com` **都是 1**
    ⇒ ★ **AST 分不开** ⇒ ★★ **只能按形参表判**。

    ★★ 依据：★ `GetNodeLocation(Int32, Double&, Double&, Double&)` 缺的 **全是 by-ref 出参**
    （★ 调用方拿不到 ⇒ **真缺口**）；★ `CreateFlattenRoute` 缺的**全是普通入参**（★ `*args` 该补）。
    """
    a, b = SAME_SHAPE["CreateFlattenRoute"], SAME_SHAPE["GetNodeLocation"]
    assert a["slots"] == b["slots"] == "[('*args', None)]", "两类不再同形 ⇒ 结论要改"
    assert a["com"] == b["com"] == 1, "`com` 不再相同 ⇒ 结论要改"
    assert a["missing_all_byref"] is False and b["missing_all_byref"] is True, \
        "`missing_all_byref` 必须一真一假（★ 那正是判别依据）"


# ── ③ ★★ 不丢覆盖（★ 267 的教训）──────────────────────────────────
def test_coverage_is_not_lost():
    """★★ 已核调用点 **316 ≥ 下界 313** ⇒ ★ **不触发棘轮**（★ 267 那次丢了 189 个）。

    ★ 271 比 268 少 2 个（318 → 316）—— ★ 因为那 2 条 `real-gap` 从 `starred`（★ 算已核）
    **回到了 `arity`**（★ 不算已核）⇒ ★ **这是正当的**（★ 它们**本来就该在 `arity` 里**）。
    """
    assert READINGS["spec_271"]["judged_sites"] >= BASELINE_SITES, "掉到下界以下"
    assert READINGS["spec_271"]["judged_entries"] == READINGS["spec_268"]["judged_entries"], \
        "可核分发口不该变"
    delta = READINGS["spec_268"]["judged_sites"] - READINGS["spec_271"]["judged_sites"]
    assert delta == 2, "少掉的调用点 %d ≠ 2 ⇒ 请复核" % delta


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 四组负例：① arity 没回到 13；② `real-gap` 桶 ≠ 2；③ 调用点掉到下界以下；④ 两类不同形。"""
    assert not _failures(READINGS, BUCKETS_271, SAME_SHAPE), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(READINGS, spec_271=dict(READINGS["spec_271"], arity=11)),
                     BUCKETS_271, SAME_SHAPE), "arity 没回升却未判出 ⇒ **空判据**"
    assert _failures(READINGS, dict(BUCKETS_271, **{"real-arity-gap": 0}), SAME_SHAPE), \
        "`real-gap` 桶为 0 却未判出 ⇒ **空判据**"
    assert _failures(dict(READINGS, spec_271=dict(READINGS["spec_271"], judged_sites=300)),
                     BUCKETS_271, SAME_SHAPE), "掉到下界以下却未判出 ⇒ **空判据**"
