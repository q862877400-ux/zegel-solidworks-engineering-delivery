"""★ 契约测试：`mech-design` 的 17 个标准件数据表（★ 1169 行真实数据）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_standard_parts.py
# 定位:   规格 `specs/333-standard-parts-tables` 的契约测试。
#           ★★ 触发它的是 2026-10-14 全自动挖掘：`mech-design`（★ 业主早装好的）
#             里有 **O 型圈 349 · 底孔 99 · 通孔 90 · 轴承 102** ——
#             ★ 而本仓 `manufacturing_rules.yaml` **只有 5 个规格**。
# 官方依据: `~/.agents/skills/mech-design/知识库/标准件数据表/*.csv`（★ 只读）
# 许可:   本仓库 MIT。★ 外部数据表只读；★ 测试**不复制数据**，只**验形态与查询**。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import standard_parts as S                    # noqa: E402


def test_tables_dir_resolves() -> None:
    """★★★ **表目录必须真的存在**。

    ⚠ 实测（2026-10-14）：表**不在** `mech-design/标准件数据表/`，
      ★ 而在 **`mech-design/知识库/标准件数据表/`** ✗ ——
      ★ 我第一版按索引里的写法猜了路径 ⇒ ★ 报 `no-tables`。
    ⇒ ★ 判据：**列候选路径**（★ 找到第一个存在的）。
    """
    assert S.TABLES_DIR.is_dir(), "★★ 表目录不存在：%s" % S.TABLES_DIR
    assert any(S.TABLES_DIR.glob("*.csv"))


def test_available_lists_tables() -> None:
    """★ 表清单非空，且每张表都有行数与来源。"""
    av = S.available()
    assert len(av) >= 15, "★ 表太少：%d" % len(av)
    for name, v in av.items():
        assert v["rows"] > 0, "★ %s 是空的" % name
        assert v["source"]


def test_total_rows_is_large() -> None:
    """★★ 总行数 **≥ 1000**（★ 这是「业主早就给了」的证据）。"""
    r = S.report()
    assert r["rows_total"] >= 1000, "★ 总行数只有 %d" % r["rows_total"]


def test_oring_table_has_349_rows() -> None:
    """★ O 型圈表 **349** 行（★ 索引里逐字写的数）。"""
    av = S.available()
    assert av["o-ring_parameters"]["rows"] == 349


def test_tap_hole_table_has_99_rows() -> None:
    """★ 底孔表 **99** 行。"""
    assert S.available()["tap_hole_sizes"]["rows"] == 99


def test_clearance_table_has_90_rows() -> None:
    """★ 通孔表 **90** 行。"""
    assert S.available()["clearance_hole_sizes"]["rows"] == 90


#: ══ ★★★ 查询：真值 ═══════════════════════════════════════════════════

def test_m8_tap_drill_is_6_8_soft() -> None:
    """★★★ **M8-1.25 底孔 = 6.8mm（Soft 列）**。

    ★★ 与 `manufacturing_rules.thread_spec('M8')` 的 **6.8 一致** ⇒
      ★ 两份**独立来源互证** ✓
    """
    r = S.tap_drill("M8-1.25")
    assert r["soft_mm"] == "6.8"
    assert r["picked"] == "6.8"


def test_tap_drill_returns_both_columns() -> None:
    """★★★ **表有两列 `Soft`/`Hard`** ⇒ ★ **两列都回**。

    ⚠ ★ 而实测发现「硬材料用小底孔」与列名**相反** ——
      ★ `M8-1.25`：`Soft=6.8` · `Hard=7.2` ⇒ ★ Hard 列的值**更大** ✗
      ⇒ ★ **不替它解释**（★ 铁律 5）—— ★ 由调用方定。
    """
    r = S.tap_drill("M8-1.25")
    assert r["soft_mm"] and r["hard_mm"]
    assert "不替它解释" in r["★"]


def test_m6_clearance_normal_is_6_6() -> None:
    """★★★ **M6 通孔 = 6.6mm（Normal 档）** —— ★ 与 `manufacturing_rules` 一致 ✓"""
    r = S.clearance_hole("M6")
    assert r["normal_mm"] == "6.6"
    assert r["picked"] == "6.6"


def test_clearance_has_three_fits() -> None:
    """★★ **通孔有三档** `Close` / `Normal` / `Loose`（★ 逐字承 `mech-design`）。"""
    r = S.clearance_hole("M6")
    assert r["close_mm"] == "6.4"
    assert r["normal_mm"] == "6.6"
    assert r["loose_mm"] == "7"


def test_clearance_fit_selector_works() -> None:
    """★ 三档可选（★ `fit` 参数）。"""
    assert S.clearance_hole("M6", fit="close")["picked"] == "6.4"
    assert S.clearance_hole("M6", fit="loose")["picked"] == "7"


def test_oring_has_iso3601_fields() -> None:
    """★★ O 型圈按 **ISO 3601** 标准（★ 表里有 `iso3601:id` / `w` / 公差）。"""
    r = S.oring("001")[0]
    assert r["iso3601:id"] == "0.74"
    assert r["iso3601:w"] == "1.02"
    assert r["iso3601:id_tol"] and r["iso3601:w_tol"]


def test_bearing_has_load_ratings() -> None:
    """★★ 轴承表有**额定载荷**（`SKT:C` 基本额定 · `SKT:C0` 静额定）。

    ★★ 判据：★ 这是选型计算**必需**的字段 —— ★ 而本仓此前**没有**。
    """
    r = S.rows("single_row_deep_groove_ball_bearing_parameters")[0]
    assert "SKT:C" in r and "SKT:C0" in r
    assert float(r["SKT:C"]) > 0
    assert "SKT:d" in r and "SKT:D" in r


def test_bearing_has_designation() -> None:
    """★ 轴承有牌号（`SKT:Designation`，★ 如 `623`）。"""
    r = S.rows("single_row_deep_groove_ball_bearing_parameters")[0]
    assert r["SKT:Designation"] == "623"


#: ══ 错误路径 ═════════════════════════════════════════════════════════

def test_unknown_table_raises() -> None:
    """★ 表名不存在 ⇒ **响亮报错**（★ 不静默回空）。"""
    with pytest.raises(S.TableError) as ei:
        S.rows("no_such_table")
    assert ei.value.code == "unknown-table"


def test_unknown_size_raises() -> None:
    """★ 规格不在表里 ⇒ 报错（★ 不猜一个值）。"""
    with pytest.raises(S.TableError):
        S.tap_drill("M999-9.99")


def test_find_is_case_insensitive_on_columns() -> None:
    """★ 列名匹配**大小写不敏感**（★ 容错）。"""
    a = S.find("tap_hole_sizes", size="M8-1.25")
    b = S.find("tap_hole_sizes", SIZE="M8-1.25")
    assert len(a) == len(b) == 1


def test_report_lists_17_tables() -> None:
    """★ 总览列出 **17** 张表。"""
    r = S.report()
    assert r["tables"] == 17, "★ 表数变了：%d" % r["tables"]


def test_harvest_docs_exist() -> None:
    """★ 挖掘文档在（★ 记录「业主早就给了」这件事）。"""
    d = ROOT / "specs" / "332-known-facts-triage"
    assert (d / "batch-15-mech-design.md").is_file()
    assert (d / "batch-15-deep-dive.md").is_file()
    t = (d / "four-tier-trust-hierarchy.md").read_text(encoding="utf-8")
    for k in ("L1", "L2", "L3", "L4", "带方向", "静默失败"):
        assert k in t, "★ 四级信任层级文档缺 `%s`" % k
