"""★ 批次 84 的契约测试：第三坡（薄模块）产出的 7 个 —— ★ 含 4 个**真建模能力**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch84.py`（生成物）· `output/bunny3-filtered-report.json`（真新行）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批特有契约：
#         ① ★ **7 个都能解析到真实函数**（生成物必须逐条可调）
#         ② ★ **没有裸坐标**（规则 3）—— ★ 本批含"选草图段/3D 边界框"这类**容易被写成收坐标**的工具，
#            故专门守一条：`select_segment` 走的是**序号**（声明式），不是坐标 ✓
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

KEPT = ("solidworks_gui_get_foreground_window", "solidworks_gui_screen_png",
        "solidworks_revolve_cut", "solidworks_ref_geometry_create_3d_bounding_box",
        "solidworks_sketch_select_segment", "solidworks_surface_cut",
        "solidworks_weldment_iter_features")


def test_batch84_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch84"' in t


def test_seven_tools_present_and_resolve():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    missing = [n for n in KEPT if n not in specs]
    assert not missing, "★ 没挂上: %r" % (missing,)
    for n in KEPT:
        s = specs[n]
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)


def test_no_bare_coordinates_in_this_batch():
    """★ 规则 3：★ 本批有"选草图段 / 3D 边界框"这类**容易被写成收坐标**的工具 ⇒ 专门守一条 ✓"""
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        for p in (getattr(specs[n], "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (n, p.name)


def test_select_segment_is_declarative():
    """★★ `solidworks_sketch_select_segment` 必须走**序号**（声明式），而不是坐标（规则 3 的精神）。"""
    s = next(x for x in rc.all_specs()
             if getattr(x, "name", "") == "solidworks_sketch_select_segment")
    names = [p.name for p in (s.params or [])]
    assert any(k in n.lower() for n in names for k in ("index", "nth", "position")), names
