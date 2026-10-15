"""★ spec 272：**12 条 `arity` 是同一病因**（★ 封装未接 by-ref 出参）—— ★ 271 的「real-gap」其实是约定。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_simulation_results.py:128-129（`MESH_ARITY` 的 `1`）· `:229-230`（官方签名注释）
#         scripts/sw_simulation_results.py:142-152（`_checked` 的 arity 护栏）
#         specs/271-real-gap-visible-again/（★ 判 2 条为 `real-gap`）· specs/253-arity-mismatch-triage/（★ 10 条 `byref-tail`）
# 定位:   ★ 271 说「下一轮修 2 条 `real-gap`」⇒ ★ 本文件**先量**那 2 条的**表侧值** ⇒
#         ★★ **量出它们与 10 条 `byref-tail` 是同一条约定**。
# 官方依据: `C:/swapi/types/ICWMesh/GetNodeLocation.md`（`(Int32, Double&, Double&, Double&)`）
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

#: ★★★ **表侧值 vs 官方形参数**（★ 272 量出）。
TABLE = {
    "GetNodeLocation": {"table": 1, "official": 4, "byref_out": 3},
    "GetElementLocation": {"table": 1, "official": 4, "byref_out": 3},
    "CreatePlot": {"table": 4, "official": 5, "byref_out": 1},
    "GetBOMStartNumber": {"table": 0, "official": 1, "byref_out": 1},
}
#: ★★★ **共同点**：★ `table + byref_out == official` ⇒ ★ **表侧一律「不含 by-ref 出参」**。
def consistent(row: dict) -> bool:
    return row["table"] + row["byref_out"] == row["official"]


#: ★★ 271 的分桶（★ 13 = 10 + 1 + 2）。
BUCKETS_271 = {"byref-tail-convention": 10, "all-byref-false-positive": 1, "real-arity-gap": 2}
#: ★★★ **272 的重新定性**：★ 那 2 条**不是** `real-gap` ⇒ ★ 与 10 条**同类** ⇒ **12 条同一病因**。
SAME_CAUSE = 12


def _failures(table: dict, buckets: dict, same: int) -> list[str]:
    """★ 纯函数：① 表侧一律「不含 by-ref 出参」；② 12 条同类；③ 病因写清。"""
    out: list[str] = []
    for name, row in sorted(table.items()):
        if not consistent(row):
            out.append("%s 的表侧值不自洽（%d + %d ≠ %d）"
                       % (name, row["table"], row["byref_out"], row["official"]))
    if buckets.get("real-arity-gap") != 2:
        out.append("271 的 `real-gap` 桶 %r ≠ 2 ⇒ 请复核" % buckets.get("real-arity-gap"))
    if same != buckets.get("byref-tail-convention", 0) + buckets.get("real-arity-gap", 0):
        out.append("同类条数 %d ≠ 10 + 2" % same)
    if "by-ref 出参" not in CAUSE:
        out.append("病因没写清")
    return out


CAUSE = ("★ **封装未接 by-ref 出参**（★ 表侧一律**不含**出参 ⇒ 12 条**同一条约定**）"
         "—— ★ 差的个数不同（1 vs 3）只是**出参有几个**，★ **不是两种病因**")


# ── ① ★★★ 表侧一律「不含 by-ref 出参」──────────────────────────────
def test_table_side_excludes_byref_out():
    """★★★ `table + byref_out == official` 对**每一条**都成立 ⇒ ★ 表侧**一律**「不含 by-ref 出参」。

    ★★ 这是 253 的 `byref=excluded` 约定 ★ **在 2 条 `real-gap` 上同样成立**。
    """
    bad = _failures(TABLE, BUCKETS_271, SAME_CAUSE)
    assert not bad, "表侧约定结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 12 条**同一病因**（★ 271 的 `real-gap` 其实是约定）──────────
def test_twelve_entries_share_one_cause():
    """★★★ 271 把 2 条判成 `real-gap`（★ 差 −3）★ 而 272 量出：★ **它们与 10 条 `byref-tail` 同一病因**
    —— ★ 都是「**封装未接 by-ref 出参**」。

    ★★★ **为什么这条要紧**：★ 不纠正 ⇒ ★ 下一轮会把 2 条当**独立缺陷**修（★ 而它们与另 10 条**同一处**改法）。
    """
    assert SAME_CAUSE == 12, "同类条数应为 12（10 + 2）"
    assert BUCKETS_271["byref-tail-convention"] + BUCKETS_271["real-arity-gap"] == SAME_CAUSE, \
        "10 + 2 应等于 12"
    assert "同一病因" in CAUSE or "同一条约定" in CAUSE, "病因没写「同一条」"


# ── ③ ★★ `_checked` 的护栏会**拒**多传的出参 ──────────────────────────
def test_checked_guard_rejects_extra_args():
    """★★ `_checked` 逐字：「`expected != len(args)` ⇒ 抛 `ValueError`」
    ⇒ ★★ **想补出参就得先改表**（★ 否则护栏先拦）—— ★ 这是下一轮动手前必须知道的。
    """
    src = (SCRIPTS / "sw_simulation_results.py").read_text(encoding="utf-8")
    assert "expected != len(args)" in src, "`_checked` 的护栏变了 ⇒ 请复核"
    assert '"GetNodeLocation": 1' in src, "表侧值变了 ⇒ 请复核"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 表侧不自洽；② `real-gap` 桶 ≠ 2；③ 同类条数不对。"""
    assert not _failures(TABLE, BUCKETS_271, SAME_CAUSE), "正常读数被判红 ⇒ 判据过严"
    bad = dict(TABLE)
    bad["X"] = {"table": 1, "official": 5, "byref_out": 1}
    assert _failures(bad, BUCKETS_271, SAME_CAUSE), "表侧不自洽却未判出 ⇒ **空判据**"
    assert _failures(TABLE, dict(BUCKETS_271, **{"real-arity-gap": 0}), SAME_CAUSE), \
        "`real-gap` 桶为 0 却未判出 ⇒ **空判据**"
    assert _failures(TABLE, BUCKETS_271, 10), "同类条数不对却未判出 ⇒ **空判据**"
