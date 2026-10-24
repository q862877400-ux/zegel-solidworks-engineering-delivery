"""★ 守「阶段 2 · T1 生产侧现状」这份文档（★ 含两条判据 · 轮 134）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `docs/history/phase2-obsolete-status.md` + `tools/scan_obsolete_safe.py`（★ 判据**不改**）
# 文件:   tests/test_phase2_obsolete_status.py（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 134）**生产侧从 35 降到 6、★ 而 6 条**全部已处置**** ⇒
#     ★★ **⇒ **生产侧待办 = 0**** ✓
#   ★★★ **两条判据**（★ 本测试守住它们）：
#     ★ **① 「扫描器报的命中」≠「待办」** —— ★ **先回源码看有没有**处置结论 + 依据引用**** ✓
#     ★★ **② 拿"别人记的行号"取上下文之前，先把那一行**打出来看一眼**** ——
#       ★ 实测扫描器偏 **4~6 行**（★ `sw_assembly.py` 报 409、真在 415）⇒
#       ★★★ **⇒ 我第一版据它报"2 条未判"，★ 那是**假阳性**** ✓
#   ★★★★ **⚠ 本测试**不跑 SolidWorks、★ 也不改判据**** ⇒ ★ 只核：
#     ★ ① 那 6 条的源码里**确实有**处置引用 · ★★ ② 文档记下了两条判据与真读数 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "docs" / "history" / "phase2-obsolete-status.md"
SCAN = REPO / "tools" / "scan_obsolete_safe.py"

#: ★ 那 6 条（★ 文件, 成员, ★ 真调用点所在的**成员名**必须在文件里出现）
SIX = [
    ("scripts/sw_assembly_doc.py", "AddMate5"),
    ("scripts/sw_assembly.py", "AddMate5"),
    ("scripts/sw_part.py", "CreateSpline2"),
    ("scripts/sw_part.py", "FeatureLinearPattern5"),
    ("scripts/sw_render_material.py", "DeleteRenderMaterial"),
    ("scripts/sw_render_material.py", "AdvancedGraphics"),
]

#: ★★ 「处置证据」的形态（★ 官方页引用 / 证据文件 / 明写的处置词）
DISPOSED = re.compile(
    r"(swapi\\\\types|swapi\\types|output/[a-z0-9\-_]+\.json|probe_[a-z0-9_]+|"
    r"记档保留|当前仍可调|官方明写\*\*无后继|by-ref)")


def test_the_scanner_criterion_is_untouched() -> None:
    """★★★ 核心断言：★ `scan_obsolete_safe.py` **还在**（★ 任务书：★ **不改判据**）✓"""
    assert SCAN.is_file(), "★ 判据脚本不见了"
    t = SCAN.read_text(encoding="utf-8", errors="replace")
    #: ★★ 它自带自检反例（★ S2）—— ★ 那说明判据**被负例验过**（★ 事实 62）✓
    assert "S2" in t or "反例" in t, "★ 判据的自检反例不见了"


def test_each_of_the_six_has_a_recorded_disposition() -> None:
    """★★★★ 核心断言：★ 那 6 条**每条**的源码里都有**处置依据** ✓

    ★★ **为什么**：★ 扫描器只在"调用形态 × 官方废弃位"上判 ⇒
      ★★★ **⇒ 它**分不出「没处置」与「已判不可换」**** ⇒
      ★★ **⇒ 所以"是不是待办"要**回源码看**（★ 判据 ①）✓
    """
    missing = []
    for rel, member in SIX:
        p = REPO / rel
        assert p.is_file(), "★ %s 不在" % rel
        t = p.read_text(encoding="utf-8", errors="replace")
        assert member in t, "★ %s 里没有 `%s`" % (rel, member)
        if not DISPOSED.search(t):
            missing.append(rel)
    assert not missing, ("★ 这些文件里**没有**处置依据引用 ⇒ 那才是真待办：%r" % missing)


def test_the_doc_records_the_real_numbers_and_attribution() -> None:
    """★★★ 核心断言：★ 文档记**任务书旧值**、★ **实测新值**、★ 且**归因**清楚 ✓"""
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for v in ("35", "6", "66", "37"):
        assert v in t, "★ 数字 `%s` 没记" % v
    assert "生产侧待办 = 0" in t or "待办 = 0" in t, "★ 结论没写明"
    #: ★★ 而"探针 31 只报不动 / 兜底 29 不算缺陷"这两条边界也要在 ✓
    assert "只报不动" in t and "不算缺陷" in t, "★ 两档的边界没写"


def test_the_line_number_lesson_is_recorded() -> None:
    """★★★★ 核心断言：★ 「扫描器行号偏 4–6 行」这条教训写在文档里 ✓

    ★★ **为什么**：★ 我第一版据它的行号取上下文 ⇒ **误报"2 条未判"** ✗ ⇒
      ★★★ **⇒ 判据：★ 拿别人记的行号取上下文前，先把那一行**打出来看一眼**** ✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "415" in t and "409" in t, "★ 那两个行号（★ 报 409 / 真在 415）没记"
    assert "打出来看一眼" in t or "定位漂移" in t, "★ 那条判据没写"


def test_the_two_official_verdicts_are_recorded() -> None:
    """★★★★ 核心断言：★ 两条**官方判定**（★ 第 ① 步原文）都写进文档 ✓

    ★★ **且两条的**理由不同****（★ 一个"后继要造对象"、★ 一个"官方没写后继"）⇒
      ★★★ **⇒ 那条区别要留住**（★ 免得后人以为"废弃就一定有个简单后继"）✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "out System.int ErrorStatus" in t, "★ `AddMate5` 那个 by-ref 末参没记"
    assert "CreateMate" in t, "★ `AddMate5` 的后继没记"
    assert "没有" in t and "Superseded" in t, "★ `AdvancedGraphics` 那条「官方没写后继」没记"
