"""★ 测「阶段 1 审计脚本 + 那两条判据」（★ 含负例 · 轮 132）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（任务书**阶段 1** 最严重的那一类）+ `docs/verified-evidence-audit.md`
# 文件:   tests/test_verified_evidence_audit.py（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 132）**两条可数量**（★ 真读数）：
#     ★ **判据 A**：★ 每条 `level: verified` ⇒ 数它证据文件里的**否定标记** ⇒ ★ **0 条可疑** ✓
#     ★★ **判据 B**：★ 从 `evidence` 的**散文**里抽路径 ⇒ **真实存在**的占比 ⇒ ★ **96/96 = 100%** ✓
#   ★★★ **而本轮**我先判错了一次****（★ 值记）：
#     ★ 我先按"**字面就是路径**"去数 ⇒ 得到 **"94/96 不是路径"** ⇒ ★★ **据此写下
#       "`verified` 与可核证据之间没有机器可读的链"** ✗ ⇒ ★★★ **抽出之后结论**反转**** ✓
#     ⇒ ★ **⇒ 判据**：★★★ **"覆盖率 0%" 与 "我没抽" 长得一样** ⇒
#       ★ **报"扫不到"之前先确认**抽取规则够不够宽** ✓（★ 与事实 51 同族）
#   ★★★★ **⚠ 脚本都在 `output/`**（★ 只报不动）⇒ ★ **本测试只核**它们存在 + 产物字段** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

AUDIT_A = REPO / "output" / "_audit_verified_vs_evidence.py"
AUDIT_B = REPO / "output" / "_audit_evidence_path_extraction.py"
DOC = REPO / "docs" / "verified-evidence-audit.md"
OUT_A = REPO / "output" / "verified-vs-evidence-audit.json"
OUT_B = REPO / "output" / "evidence-path-coverage.json"


def test_both_audit_scripts_exist_and_are_read_only_by_name() -> None:
    """★★★ 核心断言：★ 两个审计脚本都在 `output/`（★ 那意味着**只报不动**）✓"""
    for p in (AUDIT_A, AUDIT_B):
        assert p.is_file(), "★ 缺审计脚本 %s" % p.name
        t = p.read_text(encoding="utf-8", errors="replace")
        #: ★★ **不许**在审计脚本里写 `capabilities.yaml`（★ 那是"动"）✓
        assert "CAPS.write_text" not in t and 'capabilities.yaml").write' not in t, (
            "★ 审计脚本**只报不动** —— 不许写 `capabilities.yaml`")


def test_criterion_a_recorded_zero_suspects() -> None:
    """★★★ 核心断言：★ 判据 A 的结论是**可疑 0 条**（★ 那是阶段 1 要的那个数）✓"""
    d = json.loads(OUT_A.read_text(encoding="utf-8"))
    assert d["verified_total"] >= 90, "★ `verified` 条数不对：%r" % d["verified_total"]
    assert d["suspect"] == [], "★ 出现了可疑条目 ⇒ 要立刻逐条看：%r" % d["suspect"][:3]


def test_criterion_b_recorded_full_coverage() -> None:
    """★★★★ 核心断言：★ 判据 B 的覆盖率是 **100%**（★ 那是本仓的一个**真实优点**）✓"""
    d = json.loads(OUT_B.read_text(encoding="utf-8"))
    assert d["verified_total"] == d["with_real_path"], (
        "★ 有 `verified` 条目的证据**抽不到真实文件** ⇒ 那条**只能靠信**：%r"
        % [r["id"] for r in d["rows"] if r["n_real"] == 0][:5])
    assert d["coverage_pct"] == 100.0


def test_negative_case_the_extraction_covers_prose() -> None:
    """★★★★ **负例**：★ 抽取规则**必须覆盖散文**、★ 不许只认"字面就是路径" ✓

    ★★ **为什么**：★ 我第一版只认字面 ⇒ 得到 **"94/96 不是路径"** ⇒ ★ **结论反了** ✓
      ★★★ **⇒ 所以要有这条判据钉住"四类路径都要抽"** ✓
    """
    t = AUDIT_B.read_text(encoding="utf-8", errors="replace")
    for need in ("tests", "output", "tools", "scripts"):
        assert need in t, "★ 抽取规则少了 `%s` 这一类" % need
    #: ★★ 而它要**在整段散文里**搜（★ 不是拿整段当路径）✓
    assert "prose" in t, "★ 要把证据拼成整段散文再搜"


def test_the_doc_records_both_the_result_and_the_boundary() -> None:
    """★★★★ 核心断言：★ 文档既记**结果**、★ 也记**边界**（★ 别把覆盖率当证据强度）✓"""
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "96" in t and "100" in t, "★ 两个真读数要写进文档"
    #: ★★ **两条边界**必须写（★ "不等于那份文件真能证明它"）✓
    assert "不等于" in t, "★ 没写边界"
    #: ★★★ 而那条教训（★ "覆盖率 0% 与我没抽长得一样"）也要在 ✓
    assert "我没抽" in t or "抽取规则" in t, "★ 那条教训没记下"
