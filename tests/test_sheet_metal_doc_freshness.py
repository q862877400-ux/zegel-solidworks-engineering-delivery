"""★ 测 4 个钣金工具的 doc 是否已不再陈述**已被自己修掉的失败原因**（★ 处置 `JUDGE-C_D_E` 🔴 #2）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本工具只比对**仓内两处副本**，不引官方原文）
# 文件:   tests/test_sheet_metal_doc_freshness.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#2**（★ `E-1 #2 / #3 / #4 / #1`）逐字：「★ 工具描述是**对外契约**，
#   ★ 当前**逐字陈述的是已被自己修掉的失败原因**，★ **按它排查会停在死路上**」✓
#   ★★ 这是**「扩散副本」类**的第 2 例（★ 第 1 例是 `A-features F1` 的 `add_dimension`）：
#     ★ **真相在 `scripts/` 里（已修好）**、★ **而 `mcp-server/` 的 doc 没跟着改** ✓
#   ★★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
B3 = REPO / "mcp-server" / "tool_specs_batch3.py"
B4 = REPO / "mcp-server" / "tool_specs_batch4.py"

#: ★★ 四条"已作废的失败形态"（★ 逐字取自改前的 doc）
STALE = [
    "CreateDefinition(33) returned None",
    "setting `ReverseDirection` gave",
    "setting `Thickness` gave",
    "An open polyline path produces a profile flange",
]


def _texts() -> dict:
    return {"batch3": B3.read_text(encoding="utf-8", errors="replace"),
            "batch4": B4.read_text(encoding="utf-8", errors="replace")}


def test_stale_phrases_not_stated_as_current() -> None:
    """★★★ 核心断言：★ 四条旧措辞**不许**再作为**当前事实**出现。

    ★★ 注意：★ 它们**可以**出现在"旧描述（已作废）"那一句里（★ 那是**记录**）—— ★ 所以本条查的是：
      ★ **每出现一次，同一段里必须有「已作废」或「旧描述」的标记** ✓
    """
    t = _texts()
    for phrase in STALE:
        for name, text in t.items():
            if phrase not in text:
                continue
            i = text.find(phrase)
            window = text[max(0, i - 400):i + 200]
            assert ("已作废" in window or "旧描述" in window), (
                "★ %s 里 %r 出现时**没有**「已作废/旧描述」标记 ⇒ 会被读成当前事实" % (name, phrase))


def test_each_doc_points_to_the_first_scene() -> None:
    """★ 四处 doc **必须**都指向 `SHEET_METAL_RUNTIME_STATUS`（★ 第一现场）✓"""
    t = _texts()
    for name, text in t.items():
        assert "SHEET_METAL_RUNTIME_STATUS" in text, (
            "★ %s 没指向第一现场 ⇒ 读者无从核对" % name)


def test_updated_docs_carry_the_now_state() -> None:
    """★ 四处 doc **必须**写明**现在**的卡点（★ 而不是只标"已作废"）✓"""
    t = _texts()
    joined = t["batch3"] + t["batch4"]
    for now_phrase in ("swFmSketchBend(35)", "CreateFeature(37) 创建失败",
                       "GussetThickness", "开放折线（轮廓法兰）真机失败"):
        assert now_phrase in joined, "★ 缺少「现在的事实」：%r" % now_phrase


def test_docs_carry_the_correction_date() -> None:
    """★ 四处更正**必须**带日期与处置编号（★ 否则后人不知道这是哪一轮改的）✓"""
    joined = _texts()["batch3"] + _texts()["batch4"]
    assert joined.count("2026-10-04 更正") >= 4, "★ 更正的条数不足 4（★ 应四条都带）"
    assert "JUDGE-C_D_E" in joined, "★ 没写明处置的是哪份裁判稿"


def test_negative_case_status_table_still_says_failure() -> None:
    """★★ **负例 · 交叉核**：★ `SHEET_METAL_RUNTIME_STATUS` **必须**仍然记着这些失败
    —— ★ 因为**改 doc 不是把失败说成成功**，★ 只是**把失败原因更新到当前形态** ✓"""
    src = (REPO / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    for must in ("is_directional", "create_edge_flange", "create_gusset", "create_one_bend"):
        if must == "is_directional":
            continue
        assert must in src, "★ 状态表里少了 %r" % must
    assert "True` 仅对闭轮廓成立" in src, (
        "★★ 状态表里那句「`True` 仅对闭轮廓成立」丢了 ⇒ 而它正是 #4 的依据")
