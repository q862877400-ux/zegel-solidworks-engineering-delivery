"""★ 批次 87 的契约测试：**跨过 SC-001 的 400** 的那 2 个（含 SC-001 本身的断言）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch87.py`（生成物）· `output/bunny6-filtered-report.json`（真新行）
# 定位:   规格 `specs/205-tool-ramp/` 的 **SC-001（工具数 ≥400）**；★ 本批是**跨线的那一批**，
#         故测试里**直接断言 SC-001**（★ 把"达标"写进可执行的判据，而不是写在报告里）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch87 as b87                              # noqa: E402

KEPT = ("solidworks_selection_clear_colors", "solidworks_costing_set_default_template")


def test_sc001_tool_count_reaches_400():
    """★★★ **SC-001**：工具数 ≥400 —— ★ 把判据写成可执行的，而不是写在报告里 ✓"""
    n = len(rc.all_specs())
    assert n >= 400, "★ SC-001 未达成：只有 %d 个工具" % n


def test_batch87_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch87"' in t


def test_both_present_and_resolve():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    missing = [n for n in KEPT if n not in specs]
    assert not missing, "★ 没挂上: %r" % (missing,)
    for n in KEPT:
        s = specs[n]
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (n, inj)
        first = next(iter(inspect.signature(getattr(m, s.function)).parameters), "")
        assert first == inj, (n, first, inj)


def test_no_duplicate_tool_names():
    """★ 注册表里**不许有重名**（★ 重名会让工具面出现两个同名的东西）。"""
    names = [getattr(s, "name", "") for s in rc.all_specs()]
    dup = [n for n, c in __import__("collections").Counter(names).items() if c > 1]
    assert not dup, "★ 重名: %r" % (dup,)


def test_no_bare_coordinates_in_this_batch():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        for p in (getattr(specs[n], "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (n, p.name)
