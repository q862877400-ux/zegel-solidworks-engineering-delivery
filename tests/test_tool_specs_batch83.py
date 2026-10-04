"""★ 批次 83 的契约测试：第二坡"真新"残余 4 个（★ 含一处**安全对照**：只读闸 vs 危险旋钮）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch83.py`（生成物）· `output/bunny2-filtered-report.json`（真新行）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★★ 本批特有的一条**安全对照**：
#         ★ `solve_memory_preflight` **只算不设** ⇒ 发它安全；
#         ★ 而批 82 删掉的 `configure_mesh_settings` / `mesh_safety_apply` **会改研究设置**
#           （事实 526 的 40 GB 事故正是盲设它们造成的）⇒ ★ 那两个**不许**出现 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402

KEPT = ("solidworks_simulation_get_loads_manager", "solidworks_simulation_get_results",
        "solidworks_simulation_solve_memory_preflight",
        "solidworks_simulation_get_edge_weld_connector")
#: ★ 危险旋钮（批 82 删的）—— ★ 本批**同样不许**把它们带回来
DANGEROUS = ("solidworks_simulation_configure_mesh_settings",
             "solidworks_simulation_mesh_safety_apply")


def test_batch83_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch83"' in t


def test_four_tools_present_and_resolve():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    missing = [n for n in KEPT if n not in specs]
    assert not missing, "★ 没挂上: %r" % (missing,)
    for n in KEPT:
        s = specs[n]
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)


def test_dangerous_knobs_still_absent():
    """★★ **安全对照**：只读的 `solve_memory_preflight` 可以发；**会改设置的旋钮不行**（事实 526）。"""
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    leaked = [n for n in DANGEROUS if n in specs]
    assert not leaked, "★ 又把危险旋钮带回来了: %r" % (leaked,)


def test_read_results_tools_expose_no_bare_coordinates():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        for p in (getattr(specs[n], "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (n, p.name)
