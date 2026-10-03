"""★ 测 `recon/sheetmetal.md` 不再把「**我没查**」写成「**官方没写**」（★ `JUDGE-C_D_E` 🔴 #11 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方文档目录（本机 `C:\swapi\types`）
# 文件:   `specs/202-user-coverage-gaps/recon/sheetmetal.md`
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#11**（★ `C-sm-1 V-5`）逐字：「★ `recon/sheetmetal.md`
#   把**已实现且官方有入口**的斜接/闭合角记成「**官方没写**」⇒ ★★ **会把后来人引到错误结论**」✓
#   ★★ 而原表**五行全是「官方没写」** —— ★ 实测复核后那是**错的**：
#     · ★ `C:\swapi\types` 里**有** `InsertSheetMetalMiterFlange` / `IMiterFlangeFeatureData` ·
#       `InsertSheetMetalClosedCorner` / `IClosedCornerFeatureData` ✓
#     · ★★ 而**本仓也已实现**（`sw_sheet_metal_weld_entry` + `tool_specs_batch74`）✓
#   ★★★ **本条的教训**：★★★ **「官方没写」与「我没查」是两件事、★ 而它们看起来一样** ——
#     ★ 与**事实 518**（★ 「我这张表里没有」≠「它不存在」）**同族** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECON = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "sheetmetal.md"
SWAPI = Path(r"C:\swapi\types")


def _table_rows() -> list[str]:
    """★ 只取**表格数据行**（★ 以 `|` 开头、★ 且不是分隔行）—— ★ 引述块不算 ✓"""
    out = []
    for line in RECON.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("|") and set(s) - set("|-: "):
            out.append(s)
    return out


def test_official_pages_exist_for_miter_and_closed_corner() -> None:
    """★★★ **前提断言**：★ 官方**确实有**那两个入口（★ 判据的锚点）✓"""
    if not SWAPI.is_dir():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    names = {p.name for p in SWAPI.rglob("*.md")}
    assert "InsertSheetMetalMiterFlange.md" in names, "★ 官方没有斜接法兰页了？"
    assert "InsertSheetMetalClosedCorner.md" in names, "★ 官方没有闭合角页了？"


def test_table_does_not_say_official_missing() -> None:
    """★★★ 核心断言：★ **表格行里**不许再出现「官方没写」（★ 那是本条病灶）✓

    ★★ 允许它出现在**引述块**里（★ 更正块要引旧句 —— ★ 「补正而不是删除」）✓
    """
    rows = _table_rows()
    bad = [r for r in rows if "官方没写" in r]
    assert not bad, "★ 表格行里还有「官方没写」：%r" % bad[:2]


def test_miter_and_corner_are_recorded_as_implemented() -> None:
    """★★★ 核心断言：★ 斜接与闭合角必须记成**已实现**（★ 它们确实已实现）✓"""
    rows = [r for r in _table_rows() if "斜接" in r or "闭合角" in r]
    assert len(rows) == 2, "★ 那两行不见了：%r" % rows
    for r in rows:
        assert "已实现" in r, "★ 没记成已实现：%s" % r[:80]
        assert "sw_sheet_metal_weld_entry" in r, "★ 没给可核的模块名"


def test_negative_case_unchacked_is_not_written_as_absent() -> None:
    """★★★ **负例 · 用词**：★ 「**没有**」与「**没查**」必须用**不同的词** ✓

    ★★ 判据：★ 只要某行**没有**可核的实现名，★ 它就必须说「**未查**」——
      ★ **绝不许**说「无」/「没有」（★ 那是**没查过的**、★ 不是**查过的结论**）✓
    """
    for r in _table_rows():
        if r.startswith("|---") or "功能" in r:
            continue
        cols = [c.strip() for c in r.strip("|").split("|")]
        if len(cols) < 5:
            continue
        status = cols[4]
        #: ★ 若那一格既没有模块名、★ 又没有"未查/查不到"，★ 就是过度断言
        if "sw_" not in status and "查不到" not in status:
            assert "未查" in status, (
                "★ 这一格既没给实现名、★ 又没说「未查」⇒ 会被读成「查过了、没有」：%s" % r[:90])
