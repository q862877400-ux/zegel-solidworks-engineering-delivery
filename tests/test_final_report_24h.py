"""★ 守「24h 收口报告」这份文档 —— ★ 核心是**数字不许手写**（★ 轮 137）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `docs/history/final-report-24h.md` + `output/final-report-facts.json`
# 文件:   tests/test_final_report_24h.py（★ 新）
# 定位:   ★★★★ 任务书**阶段 6**：★「写收口报告（★ 做成了什么 / 没做成什么 / 为什么 / 下一步）」⇒
#     ★★ **⇒ 报告的四节都要在** ⇒ ★★ **而本测试把它变成可核的** ✓
#   ★★★★★ **⚠ 而本报告**为什么提前就有**（★ 风险处置）**：★ 本轮前 **DSH 崩过一次** ⇒
#     ★ **⇒ 先落盘、★ 之后每轮刷新** ⇒ ★★ **⇒ 所以有一条判据**：
#       ★ **报告里的数字必须与 `output/final-report-facts.json` **一致**** ✓
#       （★ 而那份 JSON 由脚本**现场算出** ⇒ ★ **数字不能手写**）✓
#   ★★★ **还有两条**（★ 都是本报告期的真教训）：
#     ★ **① 归因要诚实** —— ★ 阶段 3 的 ①② 是**轮 99** 消解的、★ **不许算进本段** ✓
#     ★★ **② 「没做成」那一节不能省** —— ★ 任务书逐字要求它、★ 而**纪律②**要求如实记 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC = REPO / "docs" / "history" / "final-report-24h.md"
FACTS = REPO / "output" / "final-report-facts.json"
COLLECT = REPO / "output" / "_collect_final_report_facts.py"


def test_the_facts_file_exists_and_is_generated_by_script() -> None:
    """★★★★ 核心断言：★ 那份事实 JSON **由脚本算出**、★ 而报告引用它 ✓

    ★★ **为什么**：★ 手写数字会**漂**（★ 本会话已多次）⇒ ★★ **⇒ 数字必须有一个**可重跑的来源**** ✓
    """
    assert COLLECT.is_file(), "★ 收集事实的脚本不在"
    assert FACTS.is_file(), "★ 事实 JSON 不在（★ 跑一次 `_collect_final_report_facts.py`）"
    d = json.loads(FACTS.read_text(encoding="utf-8"))
    for k in ("tool_specs", "capabilities_total", "capabilities_by_level",
              "test_files", "read_capabilities"):
        assert k in d, "★ 事实 JSON 少了 `%s`" % k


def test_the_doc_numbers_match_the_facts_file() -> None:
    """★★★★★ 核心断言：★ **报告里的两个关键数与事实 JSON **一致**** ✓"""
    d = json.loads(FACTS.read_text(encoding="utf-8"))
    t = DOC.read_text(encoding="utf-8", errors="replace")
    #: ★ ToolSpec 总数 —— ★ 那是本报告期最常被引用的数 ✓
    assert str(d["tool_specs"]) in t, (
        "★ 报告里的 ToolSpec 数与事实文件不一致：★ 事实是 **%s**" % d["tool_specs"])
    #: ★★ 能力清单条数 ✓
    assert str(d["capabilities_total"]) in t, (
        "★ 报告里的能力条数与事实不一致：★ 事实是 **%s**" % d["capabilities_total"])
    #: ★★★ `verified` 条数 ✓
    assert str(d["capabilities_by_level"]["verified"]) in t, (
        "★ 报告里的 `verified` 条数与事实不一致")


def test_all_four_required_sections_are_present() -> None:
    """★★★★ 核心断言：★ 任务书要求的**四节都在**（★ 做成了 / 没做成 / 为什么 / 下一步）✓"""
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for need in ("做成了什么", "没做成什么", "为什么", "下一步"):
        assert need in t, "★ 少了任务书要求的那一节：`%s`" % need
    #: ★★ 而**「没做成」那一节不许空**（★ 那意味着在粉饰）✓
    #: ★★★★ **⚠ 而边界要按**节标题**取**（★ 值记）：★ 我第一版找的是「下一个 `为什么`」⇒
    #:   ★★ **而那一节表格的**列头**就叫 `为什么`** ⇒ 于是量出的"那一节"只有 **49 字符** ⇒
    #:   ★★★ **⇒ 假阳性（★ 而那**不是**内容缺失）** ⇒
    #:   ★★ **⇒ 正解：★ 按 `## 三` 这种**节标题**切** ✓
    #:   ★★★★★ **可复用判据**：★★★ **量"某一段有多长"时，边界要用**结构标记**
    #:     （标题 / 空行 / 分隔线）、★ 不要用**内容里的词** —— ★ 内容里的词会**在该段内部再现** ✓
    i = t.find("## 二 · ")
    j = t.find("## 三 · ")
    assert i != -1 and j > i, "★ 找不到「没做成」那一节的边界"
    body = t[i:j]
    assert len(body) > 500, "★ 「没做成」那一节太短 ⇒ 像在粉饰（★ 现 %d 字符）" % len(body)


def test_the_attribution_credits_the_right_round() -> None:
    """★★★★ 核心断言：★ 阶段 3 的 ①② **归给轮 99**、★ 不领功 ✓

    ★★ **为什么**：★ 那两个数（★ 7.85% / 19.33%）本报告期**只读数** ⇒
      ★★★ **⇒ 写成自己的功就是虚报**（★ 与纪律②同族）✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "轮 99" in t, "★ 没把 ①② 的改善归给轮 99"
    assert "不领功" in t or "只读数" in t, "★ 没写明本报告期只读数"


def test_the_open_items_are_listed_with_reasons() -> None:
    """★★★★ 核心断言：★ 三条**已知未定案**都列着、★ 且各有原因 ✓

    ★★ **三条**：★ ① `rib` 建不成（★ 事实 53 结题）· ★★ ② `GetWallThickness`（旋转族）口径未定案 ·
      ★★★ ③ 阶段 4 两域没做完 ✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for need in ("rib", "GetWallThickness", "api-pre"):
        assert need in t, "★ 未定案清单里少了 `%s`" % need
    assert "事实 53" in t, "★ 没写明 `rib` 是按**事实 53** 结题的"
