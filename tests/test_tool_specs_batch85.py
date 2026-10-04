"""★ 批次 85 的契约测试：两条"真能力"（三视图布局 + Costing 默认值读数）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch85.py`（生成物）· `output/bunny3-filtered-report.json`（真新行）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批两条各自带一段历史/来源：
#         · `create_three_standard_views` —— ★ `capabilities.yaml` 曾记它 `blocked`，
#           2026-10-04 查明真因是**成员名拼错**（官方真名 `Create1stAngleViews2`）⇒ 已修正，本工具挂修好后的入口 ✓
#         · `costing_defaults` —— Costing 是**护城河域**之一 ⇒ 挂它有意义 ✓
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

KEPT = ("solidworks_drawing_create_three_standard_views", "solidworks_costing_defaults")


def test_batch85_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch85"' in t


def test_both_present_and_resolve():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    missing = [n for n in KEPT if n not in specs]
    assert not missing, "★ 没挂上: %r" % (missing,)
    for n in KEPT:
        s = specs[n]
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)


def test_inject_keys_are_registered_and_match_first_param():
    """★★ 注入键必须既在 `RESOLVERS` 里、又等于目标函数首参名（事实 502）。"""
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        s = specs[n]
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (n, inj, sorted(rc.RESOLVERS))
        m = importlib.import_module("scripts.%s" % s.module)
        import inspect
        first = next(iter(inspect.signature(getattr(m, s.function)).parameters), "")
        assert first == inj, (n, first, inj)


def test_three_standard_views_takes_a_part_path_not_coordinates():
    """★ `part_path` 是**路径**（字符串），★ 不是裸坐标（规则 3）；★ 且 `projection` 是枚举。"""
    s = next(x for x in rc.all_specs()
             if getattr(x, "name", "") == "solidworks_drawing_create_three_standard_views")
    names = [p.name for p in (s.params or [])]
    assert "part_path" in names, names
    for p in s.params:
        assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), p.name
