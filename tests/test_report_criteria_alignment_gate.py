"""守「自评表编号一致性」门禁 —— **重点是负例**（轮 100）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_report_criteria_alignment_gate.py
# 定位:   守 `scripts/check_report_criteria_alignment.py`（轮 82 建 · 轮 100 推广）。
# 官方签名依据: 不适用（纯静态门禁测试，不连 SolidWorks）
# 许可:   本仓库 MIT。无第三方代码引入。
#
# ⚠⚠ **为什么这个测试是必要的（已知事实 62）**：
#   轮 82 写了这个门禁，但它**只扫 `harvest-report.md`**；
#   轮 100 发现 `docs/history/final-audit.md` **也**是另一套 A 编号，**门禁扫不到它**
#   ⇒ **「一个门禁写了 ≠ 它有效」**。
#   下面第 3、4 个测试就是**用负例把作用范围钉住**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "scripts" / "check_report_criteria_alignment.py"


def _gate():
    """把门禁当模块加载（它不是包，故用 spec_from_file_location）。"""
    spec = importlib.util.spec_from_file_location("_criteria_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


AGENTS_SAMPLE = """# 假 AGENTS

## 一、验收标准

| # | 判据 |
|---|---|
| A1 | 甲 |
| A2 | 乙 |
| A3 | 丙 |
| A4 | 丁 |

## 二、别的
"""


def test_gate_script_exists():
    """@brief 门禁脚本在。"""
    assert GATE.is_file()


def test_criteria_ids_reads_only_section_one():
    """@brief 权威编号**只从 §一 抽**（§二 里的 A 编号不算）。"""
    m = _gate()
    ids = m._criteria_ids(AGENTS_SAMPLE)
    assert ids == {"A1", "A2", "A3", "A4"}, ids


def test_tables_detects_a_table_and_ignores_the_header_row():
    """@brief ★ **负例**：表头 `| # |` **不得**被当成"混入的非 A 编号行"。

    ⚠ 这是轮 100 当场抓到的**假阳性**：第一版没排除表头 ⇒ 报 `['#']`。
    """
    m = _gate()
    doc = ("| # | 判据 | 判定 |\n"
           "|---|---|---|\n"
           "| **A1** | 甲 | 达成 |\n"
           "| **A2** | 乙 | 达成 |\n"
           "| **A3** | 丙 | 达成 |\n")
    tables = m._tables(doc)
    assert len(tables) == 1, tables
    ids, odd, _start = tables[0]
    assert ids == {"A1", "A2", "A3"}
    assert odd == [], "表头不该被当成混入行：%r" % odd


def test_tables_requires_at_least_three_rows():
    """@brief ★ **作用范围**：只有 2 个 A 行的表格**不算**逐条自评表（避免误报）。"""
    m = _gate()
    doc = ("| **A1** | 甲 |\n"
           "| **A2** | 乙 |\n")
    assert m._tables(doc) == []


def test_tables_finds_every_table_in_one_document():
    """@brief ★ **负例（本轮的教训）**：一份文档里**多张**表都要被发现。

    ⚠ 轮 82 的门禁只认「`## 四、` 那一节」，而 `final-audit.md` 的表在 `## 逐条判定` 下
    ⇒ **扫不到**。这条测试把"要扫全篇"钉住。
    """
    m = _gate()
    doc = ("## 逐条判定\n\n"
           "| # | 判据 |\n|---|---|\n"
           "| **A1** | 甲 |\n| **A2** | 乙 |\n| **A3** | 丙 |\n"
           "\n## 另一节\n\n"
           "| # | 判据 |\n|---|---|\n"
           "| **A1** | 甲 |\n| **A2** | 乙 |\n| **A3** | 丙 |\n| **A9** | 壬 |\n")
    tables = m._tables(doc)
    assert len(tables) == 2, "两张表都该被扫到，实得 %d" % len(tables)
    assert tables[0][0] == {"A1", "A2", "A3"}
    assert tables[1][0] == {"A1", "A2", "A3", "A9"}, "第二张表的 A9 必须被看见"


def test_gate_covers_the_two_known_self_assessment_documents():
    """@brief ★ 两份已知的自评表**都在扫描范围内**（这是本轮推广的直接断言）。"""
    m = _gate()
    names = {p.name for p in m._targets()}
    assert "final-audit.md" in names, sorted(names)[:8]
    assert "harvest-report.md" in names


def test_skips_cleanly_when_agents_missing(monkeypatch, tmp_path):
    """@brief 拿不到 `AGENTS.md` 时 **SKIP 并 exit 0**（便携性守卫）。"""
    m = _gate()
    monkeypatch.setattr(m, "AGENTS", tmp_path / "nope.md")
    assert m.main() == 0
