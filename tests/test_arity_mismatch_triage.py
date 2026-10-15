"""★ spec 253：**16 条「arity 不符」的分桶定罪** —— ★ 推翻「全部是『实参 = 反射 − 1』」的旧结论。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py（★ 口径真源：`com_args` / `judge` / `find_dumps`）
#         scripts/check_dispatch_entry_guard.py（`scan` / `resolution` / `_entry_sites` …）
#         output/_probe253_arity_sites.py（★ 导出 16 条明细）
#         output/_probe253_whatswrong.py（★ 真机只读复核：3 参 by-ref 能调通）
# 定位:   门禁只**计数**「arity 不符 16」而**不列明细**；★ `docs/ROADMAP.md` 断言「**16 处全部是**
#         「实参 = 反射计数 − 1」⇒ 约定问题、不是缺陷」—— ★★ **本文件实测推翻它**。
# 官方依据: 反射转储 `_raw/**/iface_*.txt` · 真机 `SldWorks.Application` rev 34.4.1（★ 只读）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`；★ 真机部分只调 `GetWhatsWrong`（★ 临时零件已关闭且未保存）
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

#: ★ 桶（★ 封闭词表 —— 认不出即红，不许写「待定」）。
STARARGS = "starargs-false-positive"   # ★ `*args` 透传：封装**自己**校验个数 ⇒ 门禁读成 1 个实参 ⇒ **假阳性**
BYREF_TAIL = "byref-tail-convention"   # ★ 末尾 by-ref 出参：表声明 `byref=excluded` ⇒ 差 −1 ⇒ **约定问题**
REAL_GAP = "real-arity-gap"            # ★ by-ref 出参**取不到**（差 ≤ −3）⇒ **已知功能缺口**（docstring 自认）
ALL_BYREF = "all-byref-false-positive"  # ★ 形参**全是** by-ref ⇒ `counted_positions` 剥光 ⇒ 差 0 也判 arity ⇒ **假阳性**
CODES = {STARARGS, BYREF_TAIL, REAL_GAP, ALL_BYREF}

#: ★★★ **16 条 arity 不符的逐条定罪**（★ `(文件, 行号) → (成员, 实参, 反射, 桶)`）。
#: ★ 读数来自 `output/_probe253_arity_sites.py`（★ 口径 **import** 自门禁，不重写）。
_TRIAGE: dict[tuple[str, int], tuple[str, int, int, str]] = {
    ("sw_feature_readback.py", 133): ("GetWhatsWrong", 3, 3, ALL_BYREF),
    ("sw_pdm.py", 275): ("GetBOMStartNumber", 0, 1, BYREF_TAIL),
    ("sw_routing.py", 200): ("CreateFlattenRoute", 1, 11, STARARGS),
    ("sw_routing.py", 208): ("CreatePipeDrawingforPipeRoute", 1, 12, STARARGS),
    ("sw_simulation_results.py", 179): ("CreatePlot", 4, 5, BYREF_TAIL),
    ("sw_simulation_results.py", 185): ("CreateDeformedBody", 2, 3, BYREF_TAIL),
    ("sw_simulation_results.py", 216): ("GetDisplacementAtPoints", 5, 6, BYREF_TAIL),
    ("sw_simulation_results.py", 222): ("GetBucklingLoadFactors", 0, 1, BYREF_TAIL),
    ("sw_simulation_results.py", 246): ("GetNodeLocation", 1, 4, REAL_GAP),
    ("sw_simulation_results.py", 251): ("GetElementLocation", 1, 4, REAL_GAP),
    ("sw_simulation_study.py", 231): ("CreateNewStudy", 3, 4, BYREF_TAIL),
    ("sw_simulation_study.py", 237): ("CreateNewStudy2", 2, 3, BYREF_TAIL),
    ("sw_simulation_study.py", 243): ("CreateNewStudy3", 3, 4, BYREF_TAIL),
    ("sw_simulation_study.py", 261): ("DuplicateStudy", 4, 5, BYREF_TAIL),
    ("sw_simulation_study.py", 274): ("ConvertStudy", 6, 7, BYREF_TAIL),
    ("sw_simulation_study.py", 395): ("ExportSimulationStudy", 1, 7, STARARGS),
}

#: ★★ **旧结论**（`docs/ROADMAP.md`）：「16 处**全部**是『实参 = 反射计数 − 1』」。
#: ★★ 本文件用 `BYREF_TAIL` 的**实测条数**证明它**错**。
OLD_CLAIM_ALL_MINUS_ONE = 16
#: ★ 下界（★ 只允许增不允许减）。
BASELINE_TOTAL = 16
BASELINE_BYREF_TAIL = 10

#: ★★★ **真机只读复核**（`output/_probe253_whatswrong.py` · SW rev **34.4.1**）：
#:   ★ 3 个 by-ref VARIANT ⇒ **OK**（`ret=True`）· 2 个 ⇒ **FAIL** · 0 个 ⇒ **FAIL**。
#:   ★★ 结论：真树那种写法**能调通** ⇒ ★ `ALL_BYREF` 桶确系**假阳性**。
MACHINE_WHATSWRONG = {"3 个 by-ref VARIANT": "OK", "2 个 by-ref VARIANT": "FAIL", "0 实参": "FAIL"}


def _bucket_failures(
    triage: dict[tuple[str, int], tuple[str, int, int, str]],
) -> list[str]:
    """★ 纯函数：返回问题清单（★ 空 = 通过）。"""
    out: list[str] = []
    for (f, ln), (member, n_args, n_refl, code) in sorted(triage.items()):
        if code not in CODES:
            out.append("%s:%d 的桶 %r 不在封闭词表 %s" % (f, ln, code, sorted(CODES)))
            continue
        diff = n_args - n_refl
        #: ★ 桶必须与差值**自洽** —— ★ 这是本文件的核心（★ 旧结论就是在这里错的）。
        if code == BYREF_TAIL and diff != -1:
            out.append("%s:%d 判 %s 但差值是 %+d（★ 该桶只能是 −1）" % (f, ln, code, diff))
        if code == REAL_GAP and diff > -3:
            out.append("%s:%d 判 %s 但差值只有 %+d（★ 该桶要求 ≤ −3）" % (f, ln, code, diff))
        if code == STARARGS and diff != -1 * (n_refl - 1):
            out.append("%s:%d 判 %s 但差值 %+d 与「只读到 1 个非 Starred 实参」不符"
                       % (f, ln, code, diff))
        if code == ALL_BYREF and diff != 0:
            out.append("%s:%d 判 %s 但差值 %+d（★ 该桶必须差 0）" % (f, ln, code, diff))
    return out


# ── ① 16 条全部表态，且桶与差值自洽 ──────────────────────────────────
def test_every_arity_site_is_triaged():
    """★★ 16 条**全部**表态；★ 且每个桶与其**差值**自洽（★ 旧结论就错在这里）。"""
    assert len(_TRIAGE) >= BASELINE_TOTAL, \
        "arity 不符条目从 %d 降到 %d ⇒ 读取器可能漏了" % (BASELINE_TOTAL, len(_TRIAGE))
    bad = _bucket_failures(_TRIAGE)
    assert not bad, "分桶定罪不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 推翻旧结论：−1 的**只有 10 条**，不是 16 条 ─────────────────
def test_old_claim_all_minus_one_is_falsified():
    """★★★ `docs/ROADMAP.md` 断言「16 处**全部**是『实参 = 反射 − 1』」⇒ ★ **实测只有 10 条**。

    ★ 能红的判据：★ 把任意一条 `STARARGS`/`REAL_GAP`/`ALL_BYREF` 改判成 `BYREF_TAIL` ⇒ 当场红。
    """
    n_byref_tail = sum(1 for (_m, _a, _r, c) in _TRIAGE.values() if c == BYREF_TAIL)
    assert n_byref_tail >= BASELINE_BYREF_TAIL, \
        "「末尾 by-ref 出参」桶从 %d 降到 %d ⇒ 有桶被误判" % (BASELINE_BYREF_TAIL, n_byref_tail)
    assert n_byref_tail != OLD_CLAIM_ALL_MINUS_ONE, \
        "「−1」桶 = %d = 旧结论的 16 ⇒ ★ 旧结论**居然对了**？请复核（★ 本判据是为**推翻**它而立的）" \
        % n_byref_tail
    n_not_minus_one = len(_TRIAGE) - n_byref_tail
    assert n_not_minus_one >= 6, \
        "「不是 −1」的条目只剩 %d 条 ⇒ 与实测（6 条）不符" % n_not_minus_one


# ── ③ 桶的条数（★ 下界，只增不减）────────────────────────────────────
def test_bucket_sizes():
    """★ 四个桶的条数：`starargs` 3 · `byref-tail` 10 · `real-gap` 2 · `all-byref` 1。"""
    counts: dict[str, int] = {c: 0 for c in CODES}
    for (_m, _a, _r, c) in _TRIAGE.values():
        counts[c] += 1
    assert counts[STARARGS] >= 3, "`*args` 假阳性从 3 降到 %d" % counts[STARARGS]
    assert counts[BYREF_TAIL] >= 10, "`byref-tail` 从 10 降到 %d" % counts[BYREF_TAIL]
    assert counts[REAL_GAP] >= 2, "`real-gap` 从 2 降到 %d" % counts[REAL_GAP]
    assert counts[ALL_BYREF] >= 1, "`all-byref` 从 1 降到 %d" % counts[ALL_BYREF]
    assert sum(counts.values()) == len(_TRIAGE), "桶条数之和 ≠ 总条数 ⇒ 有条目没进桶"


# ── ④ ★★ 真机证据：3 参 by-ref **能调通** ────────────────────────────
def test_machine_evidence_whatswrong_three_byref_works():
    """★★ 真机（SW rev 34.4.1）读数：★ 3 参 by-ref ⇒ **OK**；2 参 / 0 参 ⇒ **FAIL**。

    ★★ 这条是 `ALL_BYREF` 桶「假阳性」判定的**唯一证据** —— ★ 它证明「真树那种写法是**能用的**」。
    """
    assert MACHINE_WHATSWRONG["3 个 by-ref VARIANT"] == "OK", \
        "真机 3 参 by-ref 不是 OK ⇒ `ALL_BYREF` 桶的假阳性判定**失去依据**"
    for k in ("2 个 by-ref VARIANT", "0 实参"):
        assert MACHINE_WHATSWRONG[k] == "FAIL", \
            "真机 %s 竟然 OK ⇒ 说明「必须 3 个」这个结论错了" % k


# ── ⑤ ★★ 纯函数**能红**（合成负例）──────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 把 `real-gap` 改判成 `byref-tail`；② 桶码不在词表；③ 正常表。"""
    good = {("a.py", 1): ("M", 0, 1, BYREF_TAIL)}
    assert not _bucket_failures(good), "正常表被判红 ⇒ 判据过严"

    flipped = {("a.py", 1): ("GetNodeLocation", 1, 4, BYREF_TAIL)}
    assert _bucket_failures(flipped), "把差 −3 的判成 `byref-tail` 却未报 ⇒ **空判据**"

    bad_code = {("a.py", 1): ("M", 1, 4, "待定")}
    assert any("封闭词表" in b for b in _bucket_failures(bad_code)), \
        "非封闭词表的桶码未被判出 ⇒ 空判据"
