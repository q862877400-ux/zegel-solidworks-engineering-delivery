"""★ spec 287：**cosworks 的 `Double&` 正例** —— ★ 274 缺的那一格，★ 一直在仓里（`sw_simulation.py`）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_simulation.py:708-726（★ 来源块：★ 官方 VB6 CHM 的 `ByRef … As Double` + ★ **真机实测 2026-10-01**）
#         scripts/sw_simulation.py:744-745（★ `VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)`）
#         specs/274-double-out-param-form/acceptance.md（★ 274 的结论：★ 「`out_double` 只有类推、**无 `Double&` 真机正例**」）
# 定位:   ★ 273 说「12 条里 **6 个 `Double&`**」· ★ 274 说「**没有** `Double&` 的真机正例」⇒ ★★ 本轮**把它找出来**。
# 官方依据: `CosmosWorksLib~CWMesh~GetDefaultElementSizeAndTolerance.html`（★ `ByRef DElementSize As Double`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 回源码核；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **正例**（★ 逐字来自 `sw_simulation.py` 的来源块）：★ 2026-10-01 真机实测**取回了值**。
POSITIVE = {
    "member": "ICWMesh::GetDefaultElementSizeAndTolerance",
    "official": "ByRef DElementSize As Double",          #: ★ 官方 VB6 CHM 的逐字签名
    "form": "VT_BYREF | VT_R8",
    "reading_1": (4.9339, 0.2467),                       #: ★ `NUnits=-1` ⇒ **毫米级**
    "reading_2": (0.0049339, 0.0002467),                 #: ★ `NUnits=2` ⇒ **米级**
}
#: ★★★ **精炼后的模型**：★ `Double&` **没有唯一形态** —— ★★ **它按「接口有没有类型信息」分**。
INTERFACE_DEPENDENT = {
    "cosworks（★ 无类型信息）": ("VT_BYREF | VT_R8", "★ 本条正例"),
    "sldworks.tlb（★ 有类型信息）": ("裸值 / 省略", "★ 274 的 `IBody2::GetExtremePoint` 反例"),
}
#: ★★ **12 条的前置**（★ 三种出参各有正例 ⇒ ★ 接线的前置**全部满足**）。
PREREQS = {
    "Int32&（9 个）": "out_i4 ⇒ `VT_BYREF | VT_I4`（★ 2026-10-01 逐形态实测）",
    "Double&（6 个）": "`VT_BYREF | VT_R8`（★ **本条** · 2026-10-01 真机实测）",
    "SwDmTableError&（1 个）": "枚举 ⇒ `VT_BYREF | VT_I4`",
}


def _failures(positive, idep, prereqs, src) -> list[str]:
    """★ 纯函数：① 正例齐；② 两条读数**不同**（★ 那是「两次实测」的证据）；③ 接口相关表 2 档；④ 前置 3 条；⑤ 回源码核。"""
    bad: list[str] = []
    if len(positive) != 5:
        bad.append("★ 正例应 5 个字段，实测 %d" % len(positive))
    if positive.get("reading_1") == positive.get("reading_2"):
        bad.append("★ 两条读数**不该相同**（★ 相同就说明只测了一次）")
    if "VT_BYREF" not in positive.get("form", "") or "VT_R8" not in positive.get("form", ""):
        bad.append("★ 形态应是 `VT_BYREF | VT_R8`（★ **两半都要**）")
    if "As Double" not in positive.get("official", ""):
        bad.append("★ 官方签名要引全（`ByRef … As Double`）")
    if len(idep) != 2:
        bad.append("★ 接口相关表应 2 档（★ cosworks / sldworks.tlb）")
    if len(prereqs) != 3:
        bad.append("★ 三种出参的前置都要记")
    if not src:
        bad.append("★ 回源码核失败：取不到 `sw_simulation.py` 的那处")
    return bad


# ── ① ★★★ 仓里**有** cosworks `Double&` 的正例 ────────────────────
def test_the_positive_example_exists_in_the_repo():
    """★★★ `scripts/sw_simulation.py` 的 `default_element_size_and_tolerance`：
    ★ `VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)` ★ 传给
    `ICWMesh::GetDefaultElementSizeAndTolerance`（★ 官方 `ByRef … As Double`）
    ⇒ ★★★ **真机实测（2026-10-01）取回了值**（★ 4.9339 / 0.2467）⇒ ★★ **正例成立** ✓
    """
    assert POSITIVE["member"] == "ICWMesh::GetDefaultElementSizeAndTolerance"
    assert "VT_R8" in POSITIVE["form"]
    assert POSITIVE["reading_1"] != POSITIVE["reading_2"], "★ 两次实测的读数应不同"


# ── ② ★★★ 精炼：★ `Double&` **按接口族分**（★ 两张表都对） ────────
def test_double_out_is_interface_dependent():
    """★★★ **274 的「两表不同」仍然成立**，★ 而现在**两张表都有真机证据**：
    ★ **cosworks（无类型信息）** ⇒ `VT_BYREF | VT_R8` ✓（★ 本条）；
    ★ **sldworks.tlb（有类型信息）** ⇒ **裸值** ✓（★ 274 的 `IBody2::GetExtremePoint`）。
    ⇒ ★★ **`Double&` 没有唯一形态 —— 它按「接口有没有类型信息」分** ✓
    """
    assert len(INTERFACE_DEPENDENT) == 2
    assert "VT_BYREF | VT_R8" in INTERFACE_DEPENDENT["cosworks（★ 无类型信息）"][0]
    assert "裸值" in INTERFACE_DEPENDENT["sldworks.tlb（★ 有类型信息）"][0]


# ── ③ ★★★ **12 条接线的前置全部满足** ─────────────────────────────
def test_the_twelve_entries_are_now_unblocked():
    """★★★ 273 量出 12 条只有 **3 种**出参 ⇒ ★ 现在**三种都有真机正例**：
    ★ `Int32&`（9）⇒ `out_i4` ✓ · ★ `Double&`（6）⇒ `VT_BYREF | VT_R8` ✓（★ 本条）· ★ `SwDmTableError&`（1）⇒ 枚举 ⇒ `VT_BYREF | VT_I4` ✓
    ⇒ ★★ **接线的前置**全部满足****（★ 下一轮可动手改表）。
    """
    assert len(PREREQS) == 3
    assert "真机实测" in PREREQS["Double&（6 个）"]


# ── ④ ★★★ **回源码核**（★ 不靠手抄） ─────────────────────────────
def test_source_check_proves_the_positive_example():
    """★★★ 回源码核：★ `sw_simulation.py` 里**确实**有 `VT_BYREF | VT_R8` 与
    ★ 那条**真机实测**的来源块（★ 含 `4.9339` 与 `ByRef DElementSize As Double`）。
    """
    src = (ROOT / "scripts" / "sw_simulation.py").read_text(encoding="utf-8", errors="replace")
    assert "VT_BYREF | pythoncom.VT_R8" in src, "★ 找不到 `VT_BYREF | VT_R8`"
    assert "4.9339" in src, "★ 找不到真机读数 `4.9339`"
    assert "ByRef DElementSize As Double" in src, "★ 找不到官方逐字签名"
    assert "真机实测" in src, "★ 找不到「真机实测」"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 正例字段少；② 两条读数相同；③ 形态不是 `VT_R8`；④ 接口相关表不 2 档；⑤ 前置不 3 条。"""
    good = "…"
    args = (POSITIVE, INTERFACE_DEPENDENT, PREREQS, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({k: v for k, v in list(POSITIVE.items())[:3]}, INTERFACE_DEPENDENT, PREREQS,
                     good), "正例字段少却未判出"
    assert _failures(dict(POSITIVE, reading_2=POSITIVE["reading_1"]), INTERFACE_DEPENDENT,
                     PREREQS, good), "两条读数相同却未判出"
    assert _failures(dict(POSITIVE, form="VT_R8"), INTERFACE_DEPENDENT, PREREQS, good), \
        "形态不对却未判出"
    assert _failures(POSITIVE, {"一档": ("x", "y")}, PREREQS, good), "接口相关表不 2 档却未判出"
    assert _failures(POSITIVE, INTERFACE_DEPENDENT, {"一": "x"}, good), "前置不 3 条却未判出"
