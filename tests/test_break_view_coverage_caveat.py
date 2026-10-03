"""★ 测覆盖矩阵里「断裂视图 ✅」的**口径被记档**（★ `JUDGE-C_D_E` 🔴 #12 的那半 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 主仓库之外的生成器 `D:\SW-coverage-tool\gen_user_feature_coverage.py`
# 文件:   `docs/known-facts.md`（记档）· `docs/user-feature-coverage.md`（**生成物、不许手改**）
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#12**（★ `C-dw-1 #1`）的另一半逐字：
#   「★ 覆盖矩阵「断裂视图 ✅」**只由 `InsertBreak3`**（插断裂线）支撑，`BreakView` /
#     `CreateBreakOutSection` **零调用点**」✓
#   ★★★★ **实测复核（★ 我追到了 ✅ 的来源）**：
#     · ★ 生成器 `gen_user_feature_coverage.py` 的 `("工程图", "断裂视图", ("broken_view",))` ✓
#     · ★★ 而 `_hit(names, pats)` 是**子串匹配** ⇒ ★ 命中的是工具名
#       **`solidworks_drawing_create_broken_view`** ✓
#     · ★★★ 而那个工具**实际调的是** `insert_break_lines`（★ 能力层函数名）⇒
#       ★★ **它只「插断裂线」、不「生成断裂视图」** ✓
#     · ★★★★ 而生成器的 `FALSE_POS` 里**没有**这一格（★ 只有缩放/变形 · 钣金展开/折叠 ·
#       焊件角撑板 三格）✓
#   ★★ **为什么不改生成器**：★ 它在 `D:\SW-coverage-tool\`、★ **不是 git 仓库** ⇒
#     ★★ **改了不入库、会丢**；★★ 且 `release_check.py` / `round_chain.ps1` **都没有**检查它
#     ⇒ ★ **它不是门禁的一部分** ⇒ ★★★ **正解是在仓内记档** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FACTS = REPO / "docs" / "known-facts.md"
GENFILE = REPO / "docs" / "user-feature-coverage.md"


def test_generated_file_is_marked_do_not_hand_edit() -> None:
    """★★★ **前提断言**：★ 那个文件**自己**写着「不要手改」（★ 判据的锚点）✓"""
    if not GENFILE.is_file():
        return
    t = GENFILE.read_text(encoding="utf-8", errors="replace")
    assert "不要手改" in t[:600], "★ 生成物没标「不要手改」了 ⇒ 判据要重看"


def test_tool_name_is_what_matches() -> None:
    """★★★ 核心断言：★ 命中来自**工具名** `solidworks_drawing_create_broken_view` ✓"""
    pat = re.compile(r"['\"](solidworks_drawing_create_broken_view)['\"]")
    hits = []
    for f in (REPO / "mcp-server").rglob("*.py"):
        hits += pat.findall(f.read_text(encoding="utf-8", errors="replace"))
    assert hits, "★ 那个工具名没了 ⇒ 覆盖矩阵那一格会变 · 判据要重看"


def test_implementation_is_break_lines_not_break_view() -> None:
    """★★★ 核心断言：★ 底层实现**只插断裂线**（★ 那才是 ✅ 的真实覆盖）✓"""
    src = (REPO / "scripts" / "sw_drawing_create_missing.py").read_text(
        encoding="utf-8", errors="replace")
    assert "insert_break_lines" in src, "★ 底层实现变了"
    #: ★ 而 `BreakView` / `CreateBreakOutSection` **不该**被这段代码调到
    for name in ("BreakView", "CreateBreakOutSection"):
        assert name not in src, "★ 竟然调了 `%s` ⇒ 本测试的判据要重看" % name


def test_negative_case_the_caveat_is_recorded_in_facts() -> None:
    """★★★ **负例 · 记档**：★ 那条「✅ 只覆盖**插断裂线**」**必须**写进 `known-facts.md` ✓

    ★★ 为什么记在事实表而不是改生成物：★ 生成物在**仓外、非 git** ⇒ 改了会丢 ·
      ★★ 且**没有门禁**检查它 ⇒ ★★★ **仓内记档才是能保住的** ✓
    """
    t = FACTS.read_text(encoding="utf-8", errors="replace")
    assert "断裂视图" in t, "★ 事实表里没提这事"
    assert "insert_break_lines" in t or "只插断裂线" in t, "★ 没记「只覆盖插断裂线」"
    assert "create_broken_view" in t, "★ 没记那个工具名（★ 那是 ✅ 的来源）"
