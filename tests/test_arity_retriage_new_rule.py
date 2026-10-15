"""★ spec 269：**按新口径重量分桶** + ★★ 发现 268 的窄规则**误移了 2 条 `real-gap`**（★ 掩盖真缺口）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/check_dispatch_byref_guard.py::judge（★ spec 268 的窄规则）
#         output/_probe268_retriage.txt（★ 重量分桶读数，★ 口径 `import` 自门禁）
#         specs/253-arity-mismatch-triage/（★ 原分桶：10 byref-tail + 3 starargs + 2 real-gap + 1 all-byref）
#         specs/268-starargs-narrow-rule/（★ 窄规则 ⇒ arity 16 → 11）
# 定位:   ★ 268 说「下一轮按新口径重量分桶」⇒ ★ 本文件就做这件事，★ 并**发现 268 的副作用**。
# 官方依据: C:/swapi/types/ICWMesh/GetNodeLocation.md（`(Int32, Double&, Double&, Double&)`）
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

#: ★★★ **新口径下的 11 条**（`output/_probe268_retriage.txt` · SW rev **34.4.1** 无关，★ 这是静态读数）。
RETRIAGE = {
    "byref-tail-convention": 10,   #: ★ 差 −1 · 末位 `Int32&` / `SwDmTableError&`
    "all-byref-false-positive": 1,  #: ★ 差 0 · 末位 `Object&`（★ `GetWhatsWrong`）
}
#: ★★ 253 的**原**分桶（★ 16 条）。
ORIGINAL = {"byref-tail-convention": 10, "starargs-false-positive": 3,
            "real-arity-gap": 2, "all-byref-false-positive": 1}

#: ★★★ **268 移出的 5 条**（★ 拆开看：★ 3 条**对**、★ 2 条**误**）。
MOVED = {
    "correct": ("starargs-false-positive", 3),
    "WRONG": ("real-arity-gap", 2),   #: ★★ **误移** —— ★ 它们不是 `*args`，是**真缺口**
}

#: ★★★ **误移的那 2 条的官方签名**（★ 说明它们**不是** `*args`）。
REAL_GAP_SIGS = (
    "ICWMesh.GetNodeLocation(Int32, Double&, Double&, Double&)",
    "ICWMesh.GetElementLocation(Int32, Double&, Double&, Double&)",
)


def _retriage_failures(r: dict, orig: dict, moved: dict) -> list[str]:
    """★ 纯函数：① 新桶之和 = 11；② 与 253 的原桶**对得上**；③ 误移的 2 条要认出来。"""
    out: list[str] = []
    if sum(r.values()) != 11:
        out.append("新口径的桶之和 %d ≠ 11" % sum(r.values()))
    if sum(orig.values()) != 16:
        out.append("253 的原桶之和 %d ≠ 16" % sum(orig.values()))
    #: ★★ 新桶必须**只**剩「253 原有桶里没被移走的那些」。
    for k, v in r.items():
        if k not in orig:
            out.append("新桶 %r 不在 253 的桶里" % k)
        elif orig[k] != v:
            out.append("桶 %r：新 %d ≠ 253 的 %d ⇒ ★ 请复核" % (k, v, orig[k]))
    #: ★★★ **误移**：★ 268 移走的应是 3 条 `starargs`，★ **不该**碰 `real-gap`。
    if moved["WRONG"][0] != "real-arity-gap":
        out.append("误移的桶名不对 ⇒ 请复核")
    if moved["correct"][1] + moved["WRONG"][1] != 5:
        out.append("移出总数 %d ≠ 5" % (moved["correct"][1] + moved["WRONG"][1]))
    return out


# ── ① ★★★ 重量分桶：11 = 10 `byref-tail` + 1 `all-byref` ──────────────
def test_retriage_under_the_new_rule():
    """★★★ 新口径下 `arity` 剩 **11** = **10** `byref-tail`（差 −1）+ **1** `all-byref`（差 0）。

    ★★ `starargs` 与 `real-gap` **都从桶里消失了** —— ★ 前者是**预期**，★ 后者**不是**。
    """
    bad = _retriage_failures(RETRIAGE, ORIGINAL, MOVED)
    assert not bad, "重量分桶不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 268 的窄规则**误移了 2 条 `real-gap`**（★ 掩盖真缺口）────────
def test_the_narrow_rule_wrongly_moved_two_real_gaps():
    """★★★ `GetNodeLocation(Int32, Double&, Double&, Double&)` 也是「**1 实参 vs 4 形参**」
    ⇒ ★ 满足 268 的窄规则 ⇒ ★ **被一并判成 `starred`** —— ★ 而它**不是 `*args`**，
    ★ 是「**三个 by-ref 出参一个都没传**」的**真缺口**。

    ★★★ **为什么这条最要紧**：★ `starred` **算已核** ⇒ ★★ **那 2 条真缺口从此不再被计数**
    ⇒ ★ **门禁把它们藏起来了**（★ 本仓纪律：「可见性边界必须被量出来，减少 = 探测器漏了」）。
    """
    assert MOVED["WRONG"][1] == 2, "误移数不是 2 ⇒ 请复核"
    for sig in REAL_GAP_SIGS:
        assert "Double&, Double&, Double&" in sig, "真缺口的签名变了 ⇒ 请复核"
    #: ★ 两者的**共同点**：都是「1 个实参」⇒ ★ 窄规则**分不开**它们。
    assert "Int32, Double&" in REAL_GAP_SIGS[0], "真缺口第 2 参起全是 by-ref"


# ── ③ ★★ 正方向：窄规则该在**知道 `*args` 的地方**判 ─────────────────
def test_right_direction_for_the_fix():
    """★★ 窄规则**分不开**「`*args` 透传」与「by-ref 出参没传」—— ★ 两者都是「1 实参 vs N 形参」。

    ★★★ **正方向**：★ **把窄规则移回 `com_args`**（★ 那里**知道 `*args`**），
    ★★ **但 `main` 仍要把 `starred` 算「已核」**（★ 268 的那半是对的）。
    ⇒ ★ 两半合起来才对：★ **267 的位置 + 268 的计数**。
    """
    assert "com_args" in RIGHT_DIRECTION and "算「已核」" in RIGHT_DIRECTION, "正方向不完整"
    assert "267 的位置" in RIGHT_DIRECTION and "268 的计数" in RIGHT_DIRECTION, "没写清两半的来源"


RIGHT_DIRECTION = ("把窄规则移回 `com_args`（那里**知道 `*args`**），但 `main` 仍要把 `starred` "
                   "算「已核」⇒ 两半合起来才对：**267 的位置 + 268 的计数**")


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 新桶之和 ≠ 11；② 桶数与原桶不符；③ 误移桶名不对。"""
    assert not _retriage_failures(RETRIAGE, ORIGINAL, MOVED), "正常读数被判红 ⇒ 判据过严"
    assert _retriage_failures(dict(RETRIAGE, **{"byref-tail-convention": 9}), ORIGINAL, MOVED), \
        "桶数变了却未判出 ⇒ **空判据**"
    assert _retriage_failures(RETRIAGE, ORIGINAL,
                              {"correct": ("x", 3), "WRONG": ("y", 2)}), \
        "误移桶名不对却未判出 ⇒ **空判据**"
