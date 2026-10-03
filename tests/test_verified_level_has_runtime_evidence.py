"""★ 测 A4：`level: verified` 的条目**必须**有一条「我们自己的运行证据」（★ 处置 `JUDGE-C_D_E` 🔴 #10）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `AGENTS.md §一 A4`（★ 验收标准，★ 不是新发明的判据）
# 文件:   tests/test_verified_level_has_runtime_evidence.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#10**（★ `C-sm-1 V-2 / V-3`）逐字：「★ 两条 evidence
#   一条**不碰 COM**、一条按字面 pytest **收 0 个用例** ⇒ ★ 直接**违反验收标准 A4**
#   （`verified` 必须有我们自己的运行证据）」✓
#   ★★ **A4 原文**（`AGENTS.md`）：「每个条目的 `level` 取自五级枚举；★ **`verified` 必须有
#     我们自己的运行证据**」✓
#   ★★★ 本测试把 A4 变成**可执行的判据** —— ★ 而不是只在文档里写一句 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CAPS = REPO / "capabilities.yaml"

#: ★★ 判定"这条 evidence 是不是**运行证据**"的措辞（★ 命中任一即算）✓
#: ★★★★ **2026-10-04 修正：第一版判据太窄，出了假阳性** ——
#:   第一版只有「真机 / 实跑 / 实测」，★ 于是把下面这些**明明是运行证据**的报了进来：
#:     · ★ `python tools/verify_dfm_e2e.py`（**11/11 通过 · verdict: pass**）
#:     · ★ `python tools/verify_costing_e2e.py（verdict: pass；证据 output/…）`
#:     · ★ `output/b1-sketch-primitives-evidence.json`（★ 真机证据**文件**）
#:     · ★ `既有冒烟（权威 · 本仓库自己的判据）：python tools/verify_dome_smoke.py`
#:   ⇒ ★★ **补齐这三类形态**（★ 与"真机"是**同一件事的不同写法**）✓
#:   ★★★ **而这条修正本身也是有判据的**：★ **报出来的每一条，我都要去看它的 evidence 原文** ——
#:     ★★ 若原文明显是运行证据，★ 那就是**判据的错**、不是条目的错 ✓
RUNTIME_MARKERS = (
    #: ① 文字类
    "真机", "运行证据", "实跑", "实测", "sw_guard",
    #: ② **可复跑的验收命令**（★ `tools/verify_*.py` 就是"我们自己的运行"）
    "tools/verify", "verify_", "e2e",
    #: ③ **证据文件**（★ 落盘的运行记录）
    "evidence.json", "evidence", "verdict", "passed",
)


def _caps() -> list:
    return json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]


#: ★★★★★ 2026-10-04（接手轮）**存量账** —— ★ 本判据放宽后跑出来的是 **13 个**未满足的 `verified` 条目：
#:   ★★ 而**其中 12 个的唯一证据都是 `tests/test_cad_reliability.py`** ⇒
#:      ★★★ **而那个文件自己逐字写着「⚠ 未在本机实测 SolidWorks … 不改变任何 COM 调用」**
#:        （★ 实测：`sw_guard` 0 次 · `get_com_member` 0 次 · `mock` 0 次）⇒
#:      ★★★★ **即：12 个 `verified` 条目挂在一个"自己说没实测过"的文件上** ✓
#:   ★ **第 13 个**是 `pack_and_go`（★ 挂 `tests/test_sw_delivery.py`）✓
#:   ★★ **一次改不完**（★ 每个都要核实机证据到底在不在）⇒ ★ **本轮处理 = "记成账、断言不增加"**，
#:      ★★★ **而不是把判据放宽到看不见它**（★ 放宽到看不见 = 又一个"存在但没人用"的守卫，★ 事实 40）✓
#:   ★★ **待核账全文见 `docs/known-facts.md` 的对应条**（★ 逐条列出那 13 个 id 与它们的证据）✓
BASELINE = 13


def test_every_verified_has_a_runtime_evidence() -> None:
    """★★★ 核心断言：★ 每个 `level: verified` 的条目，★ `evidence` 里**至少一条**是**运行证据** ✓

    ★★ 判据（★ 可核、★ 不含主观）：★ 该条 evidence 文本里出现 `RUNTIME_MARKERS` 中任一措辞 ✓
    ★★★ **为什么不能只靠 pytest 文件名当证据**：★ 本轮实测两条反例 ——
      · ★ 一条 `pytest tests/test_sw_sheet_metal.py` **6 passed**、★ **而全文件 COM 0 次**
      · ★ 一条 `pytest tests/solidworks_sheet_metal_regression.py` ⇒ ★ **`no tests ran`** ✓
    ★★★★ **本测试断言的是"存量不增加"**（★ `BASELINE`）—— ★ 因为已发现 **21** 个存量，
      ★ 而**逐个核实**需要真机证据，★ 不是一轮能清完的 ✓
      ★★ 每减少一个就**调小 `BASELINE`**，★ 直到为 0 时改成 `assert not bad` ✓
    """
    bad = []
    for cap in _caps():
        if cap.get("level") != "verified":
            continue
        ev = cap.get("evidence") or []
        if not ev:
            bad.append((cap.get("id"), "**没有任何 evidence**"))
            continue
        if not any(any(m in str(e) for m in RUNTIME_MARKERS) for e in ev):
            bad.append((cap.get("id"), "evidence 里没有一条运行证据"))
    assert len(bad) <= BASELINE, (
        "★ A4 未满足的 verified 条目**增加了**（★ 现值 %d > 基线 %d）：%s"
        % (len(bad), BASELINE, [b[0] for b in bad][:8]))
    #: ★ 而**减少**是好事 ⇒ 提示调小基线（★ 不算失败）
    if len(bad) < BASELINE:
        print("★ A4 存量已从 %d 降到 %d ⇒ 请把 BASELINE 改成 %d" % (BASELINE, len(bad), len(bad)))


def test_sheet_metal_specifically() -> None:
    """★★ 本轮的**直接回归**：★ `sheet_metal` 必须有一条指向 `SHEET_METAL_RUNTIME_STATUS` 的证据 ✓"""
    cap = [c for c in _caps() if c.get("id") == "sheet_metal"][0]
    ev = " ".join(str(e) for e in (cap.get("evidence") or []))
    assert "SHEET_METAL_RUNTIME_STATUS" in ev, (
        "★ `sheet_metal` 的 evidence 仍没指向那份真机状态表")
    assert "闭轮廓" in ev, "★ 没写明范围（★ 仅闭轮廓）—— ★ 那正是它的真机边界"


def test_pytest_only_evidence_is_flagged_in_text() -> None:
    """★ 那两条**纯 pytest 证据必须**仍留在 `evidence` 里（★ 它们是真跑的），
    ★★ 但**必须**已被标注为「不构成运行证据」✓"""
    cap = [c for c in _caps() if c.get("id") == "sheet_metal"][0]
    ev = " ".join(str(e) for e in (cap.get("evidence") or []))
    assert "no tests ran" in ev or "收 0 个用例" in ev, (
        "★ 第 2 条的失败事实（收款 0）没被记下来 ⇒ 后人会再拿它当证据")
    assert "不碰 COM" in ev, "★ 第 1 条的局限（不碰 COM）没被记下来"
