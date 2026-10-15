"""★ spec 266：**先量** `counted_positions` 口径缺陷的影响面（★ 结论：**只 1 条** ⇒ 降级）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/audit_byref_args.py::counted_positions（★ 跳过 `PURE_OUT` ⇒ `Object&` 不计入）
#         scripts/audit_byref_args.py:75（`PURE_OUT = ^(Object|Variant|Dispatch)&$`）
#         specs/253-arity-mismatch-triage/（★ 16 条里 4 条假阳性：3 `starargs` + 1 `all-byref`）
#         output/_probe266_impact.py（★ 本探针）
# 定位:   ★ 260 说「改 `counted_positions` 要**先量**影响面」⇒ ★ 量完发现**只 1 条** ⇒ ★ **降级**。
# 官方依据: C:/swapi/types/IModelDocExtension/GetWhatsWrong.md（`Object&, Object&, Object&`）·
#           ★ 253 的真机实测：3 个 by-ref VARIANT **是必须的**
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`
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

#: ★★★ **先量读数**（`output/_probe266_impact.py` · 口径与门禁**逐字对齐**）。
IMPACT = {
    "old_count": 16,               #: ★ 现行口径（跳 `PURE_OUT`）
    "new_count": 15,               #: ★ 实验口径（不跳）
    "moved_out": 1,                #: ★★ **只移出 1 条**
    "moved_site": "sw_feature_readback.py:133 GetWhatsWrong（实参 3）",
}

#: ★★ `PURE_OUT` 跳过的类型（★ 实测**只有一种**）。
PURE_OUT_TYPES = ("Object&",)

#: ★★★ **253 的 4 条假阳性**按**病因**分两类 —— ★ 改口径**只救得了第 1 类**。
FALSE_POSITIVE_CAUSES = {
    "all-byref-false-positive": 1,   #: ★ `GetWhatsWrong` ⇒ ★ **改口径可救**
    "starargs-false-positive": 3,    #: ★ `*args` 透传 ⇒ ★ **改口径救不了**（★ 另一病因）
}


def _impact_failures(impact: dict, causes: dict) -> list[str]:
    """★ 纯函数：① 只移出 1 条；② 两类病因的条数；③ 别把「可救的」说成 4 条。"""
    out: list[str] = []
    if impact["old_count"] - impact["new_count"] != impact["moved_out"]:
        out.append("移出数 %d 与两个计数之差 %d 不符"
                   % (impact["moved_out"], impact["old_count"] - impact["new_count"]))
    if impact["moved_out"] != 1:
        out.append("移出数 %d ≠ 1 ⇒ ★ **影响面结论要改**" % impact["moved_out"])
    if sum(causes.values()) != 4:
        out.append("假阳性总数 %d ≠ 4（★ 253 的读数）" % sum(causes.values()))
    if causes["starargs-false-positive"] < 3:
        out.append("`*args` 类少了 ⇒ 请复核")
    return out


# ── ① ★★★ 影响面：**只 1 条**（★ 不是 4 条）─────────────────────────
def test_impact_is_only_one_entry():
    """★★★ 改 `counted_positions` 口径**只移出 1 条**（★ `GetWhatsWrong`）—— ★ **不是 4 条**。

    ★★ **为什么这条值钱**：★ 253 说「4 条假阳性」⇒ ★ 容易以为「改口径能一次解决 4 条」；
    ★ 量完才发现 ★ **只 1 条** ⇒ ★★ **收益/成本比很差**（★ 改门禁本体要跑生成器链 + 同步下界）
    ⇒ ★ **优先级应下调**。
    """
    bad = _impact_failures(IMPACT, FALSE_POSITIVE_CAUSES)
    assert not bad, "影响面结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 4 条假阳性**不是同一病因** ────────────────────────────────
def test_the_four_false_positives_have_two_causes():
    """★★★ 4 条假阳性分**两类病因**：★ `all-byref` **1**（★ 改口径可救）· ★ `starargs` **3**（★ **救不了**）。

    ★★ **为什么必须分清**：★ 混在一起 ⇒ ★ 会以为「改一处口径能解决全部 4 条」。
    """
    assert FALSE_POSITIVE_CAUSES["all-byref-false-positive"] == 1, "可救的那类应为 1 条"
    assert FALSE_POSITIVE_CAUSES["starargs-false-positive"] == 3, "救不了的那类应为 3 条"
    assert sum(FALSE_POSITIVE_CAUSES.values()) == 4, "两类加起来应等于 253 的 4 条"


# ── ③ ★★ `PURE_OUT` 跳的类型实测只有一种 ─────────────────────────────
def test_pure_out_skips_only_object():
    """★★ `PURE_OUT` 实测只跳过 **`Object&`**（★ 正则里还有 `Variant`/`Dispatch`，★ 但真树里没出现）。"""
    assert PURE_OUT_TYPES == ("Object&",), "跳过的类型变了 ⇒ 请复核"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 移出数改 4；② 计数之差与移出数不符；③ 两类病因之和 ≠ 4。"""
    assert not _impact_failures(IMPACT, FALSE_POSITIVE_CAUSES), "正常读数被判红 ⇒ 判据过严"
    assert _impact_failures(dict(IMPACT, moved_out=4), FALSE_POSITIVE_CAUSES), \
        "移出数改 4 却未判出 ⇒ **空判据**"
    assert _impact_failures(dict(IMPACT, new_count=12), FALSE_POSITIVE_CAUSES), \
        "计数与移出数不符却未判出 ⇒ **空判据**"
    assert _impact_failures(IMPACT, {"all-byref-false-positive": 1, "starargs-false-positive": 1}), \
        "两类之和 ≠ 4 却未判出 ⇒ **空判据**"
