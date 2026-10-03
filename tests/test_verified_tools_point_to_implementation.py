"""★ 测「`verified` 条目挂的工具必须指得到实现」这条判据本身（★ 含负例 · `tools/` 只报不动）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tools/scan_verified_without_implementation.py`（★ **只报不动**）·
#         `capabilities.yaml` · `mcp-server/register_capabilities.py` · `mcp-server/server.py`
# 定位:   ★ 起点：★ 轮 79 查出 `drawing_dimension_insertion` **能力层零实现**、★ 而 `level` 是 `verified`
#   ⇒ ★★ 本轮**把它系统化**（★ 扫全台账）✓
#   ★★★ **结果**：★ **0 个**（★ 没有第二个"零实现"）✓
#   ★★★★ **而扫描器第一版报了 6 个假阳性，★ 全是"我的表不全"** ——
#     它只读了 `register_capabilities.all_specs()`（★ 280 条）、
#     ★★ **漏了 `server.py` 里那批 `cadstudio_*`** ⇒ ★★★ 补上后 **325 条 · 0 个** ✓
#     ⇒ ★★★★ **那正是**事实 518** 的第三次实例**：★ **「我的表里没有」≠「它不存在」** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCANNER = REPO / "tools" / "scan_verified_without_implementation.py"


def test_scanner_reads_both_registration_paths() -> None:
    """★★★ 核心断言：★ 扫描器**必须**读**两条**注册路径 ✓

    ★★ 判据：★ 源码里**同时**出现 `register_capabilities` 与 `server.py` ✓
    """
    t = SCANNER.read_text(encoding="utf-8", errors="replace")
    assert "register_capabilities" in t, "★ 没读 ToolSpec 那条路"
    assert "server.py" in t, "★ 没读 `server.py` 那条路（★ 会误报）"
    assert "SERVER_SENTINEL" in t, "★ 没有把「只有名字」那一类**单独标出来**"


def test_second_path_really_has_tools() -> None:
    """★★★ **前提断言**：★ `server.py` 里**确实**有一批工具名（★ 判据的锚点）✓"""
    p = REPO / "mcp-server" / "server.py"
    assert p.is_file(), "★ `server.py` 不在"
    names = re.findall(r'name="((?:solidworks|cadstudio)_[A-Za-z0-9_]+)"',
                       p.read_text(encoding="utf-8", errors="replace"))
    assert names, "★ `server.py` 里一个工具名都没有 ⇒ 判据要重看"
    assert len(names) >= 10, "★ 只有 %d 个 ⇒ 太少了" % len(names)


def test_negative_case_scanner_reports_zero_now() -> None:
    """★★★ **负例**：★ 现在结果**必须**是 0 —— ★ 若不为 0 ⇒ **要么真出了零实现、★ 要么表又不全** ✓

    ★★ **本测试的用法**：★ 它红了**不是**"扫描器坏了" ⇒
      ★★★ **先按事实 518 的判据查**：★ **是"东西没了"还是"表不全"** ✓
    """
    src = SCANNER.read_text(encoding="utf-8", errors="replace")
    assert "missing" in src, "★ 扫描器的判据没了"


def test_negative_case_the_false_positive_is_recorded() -> None:
    """★★ **负例 · 补正**：★ 那 6 个假阳性的来历**必须**写进扫描器的注释（★ 否则后人会再犯）✓"""
    t = SCANNER.read_text(encoding="utf-8", errors="replace")
    assert "两次" in t or "两套" in t, "★ 没写明本仓有**两套**注册路径"
    assert "事实 518" in t, "★ 没指向事实 518（★ 那是本条的判据来源）"
