"""★ spec 273：**改表前先量** —— 12 处的 by-ref 出参**只有 3 种类型** ⇒ VARIANT 写法只需 3 种。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe271_retriage.txt（★ 13 条的反射签名）· specs/272-twelve-share-one-cause/（★ 12 条同一病因）
#         scripts/sw_simulation_results.py:142-152（★ `_checked` 会先拦）
# 定位:   ★ 272 说「下一轮改表 + 接出参」⇒ ★ 本文件**先量出参的类型**（★ 272 的教训：动手前先量）。
# 官方依据: 各成员的反射签名（★ `_raw/**/iface_*.txt`）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改任何文件
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

#: ★★★ **出参类型分布**（★ 273 量出 · 口径 `import` 自门禁）。
OUT_PARAMS = {
    "Int32&": 9,
    "Double&": 6,
    "SwDmTableError&": 1,
}
#: ★★ **只有 3 种** ⇒ ★ **VARIANT 写法只需 3 种**。
VARIANTS = {
    "Int32&": "VT_BYREF | VT_I4",
    "Double&": "VT_BYREF | VT_R8",
    "SwDmTableError&": "VT_BYREF | VT_I4",   #: ★ 枚举 ⇒ 整数
}

#: ★★ **逐成员的出参**（★ 273 量出）。
PER_MEMBER = {
    "GetBOMStartNumber": ("SwDmTableError&",),
    "CreatePlot": ("Int32&",),
    "CreateDeformedBody": ("Int32&",),
    "GetDisplacementAtPoints": ("Int32&",),
    "GetBucklingLoadFactors": ("Int32&",),
    "GetNodeLocation": ("Double&", "Double&", "Double&"),
    "GetElementLocation": ("Double&", "Double&", "Double&"),
    "CreateNewStudy": ("Int32&",),
    "CreateNewStudy2": ("Int32&",),
    "CreateNewStudy3": ("Int32&",),
    "DuplicateStudy": ("Int32&",),
    "ConvertStudy": ("Int32&",),
}
#: ★ `GetWhatsWrong` 出参**为空**（★ 差 0）⇒ ★ 它是 `all-byref` 桶，★ **不在 12 条里**。
ALL_BYREF = "GetWhatsWrong"


def _failures(out: dict, variants: dict, per: dict) -> list[str]:
    """★ 纯函数：① 类型只有 3 种；② 每种都有 VARIANT 写法；③ 逐成员总数对得上；④ 12 条齐。"""
    bad: list[str] = []
    if set(out) != set(variants):
        bad.append("类型集合与 VARIANT 表不符：%s vs %s" % (sorted(out), sorted(variants)))
    if len(out) != 3:
        bad.append("出参类型 %d 种 ≠ 3" % len(out))
    total = 0
    for name, outs in sorted(per.items()):
        for o in outs:
            if o not in out:
                bad.append("%s 的出参 %r 不在类型表里" % (name, o))
        total += len(outs)
    if total != sum(out.values()):
        bad.append("逐成员出参总数 %d ≠ 分布之和 %d" % (total, sum(out.values())))
    if len(per) != 12:
        bad.append("成员数 %d ≠ 12" % len(per))
    if ALL_BYREF in per:
        bad.append("`GetWhatsWrong` 不该在 12 条里（★ 它差 0）")
    return bad


# ── ① ★★★ 出参**只有 3 种类型** ─────────────────────────────────────
def test_only_three_out_param_types():
    """★★★ 12 处的 by-ref 出参**只有 3 种**：`Int32&`（9）· `Double&`（6）· `SwDmTableError&`（1）。

    ★★ **为什么这条值钱**：★ 改表 + 接出参要写 **VARIANT** ⇒ ★ 类型数**决定要写几种**；
    ★ 量出只有 3 种 ⇒ ★★ **VARIANT 写法只需 3 种**（★ 不是 12 种）。
    """
    bad = _failures(OUT_PARAMS, VARIANTS, PER_MEMBER)
    assert not bad, "出参类型结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 每种类型都有 VARIANT 写法 ──────────────────────────────────
def test_every_type_has_a_variant_form():
    """★★ 3 种类型**各有**对应的 `VT_BYREF` 组合 ⇒ ★ 改表时**照着抄**即可。"""
    assert VARIANTS["Int32&"] == "VT_BYREF | VT_I4", "`Int32&` 的写法变了"
    assert VARIANTS["Double&"] == "VT_BYREF | VT_R8", "`Double&` 的写法变了"
    assert VARIANTS["SwDmTableError&"] == "VT_BYREF | VT_I4", "枚举出参的写法变了"


# ── ③ ★★ `GetWhatsWrong` **不在** 12 条里（★ 差 0）───────────────────
def test_all_byref_is_not_in_the_twelve():
    """★★ `GetWhatsWrong` 的出参**为空**（★ `com = 3` = 形参 3）⇒ ★ 它是 `all-byref` 桶 ⇒ ★ **不在 12 条里**。

    ★★ 混进来 ⇒ ★ 改表时会**多改一处**（★ 而它差 0、★ 本来就不该动）。
    """
    assert ALL_BYREF not in PER_MEMBER, "`GetWhatsWrong` 混进 12 条了"
    assert sum(len(v) for v in PER_MEMBER.values()) == 16, "12 条的出参总数应为 16"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 类型多了一种；② 逐成员总数不符；③ 混进 `GetWhatsWrong`。"""
    assert not _failures(OUT_PARAMS, VARIANTS, PER_MEMBER), "正常读数被判红 ⇒ 判据过严"
    bad = dict(OUT_PARAMS)
    bad["String&"] = 1
    assert _failures(bad, VARIANTS, PER_MEMBER), "多了一种类型却未判出 ⇒ **空判据**"
    assert _failures(OUT_PARAMS, VARIANTS, dict(PER_MEMBER, CreatePlot=("Int32&", "Int32&"))), \
        "逐成员总数不符却未判出 ⇒ **空判据**"
    assert _failures(OUT_PARAMS, VARIANTS, dict(PER_MEMBER, **{ALL_BYREF: ()})), \
        "混进 `GetWhatsWrong` 却未判出 ⇒ **空判据**"
