"""★ 批次 90 的契约测试：Costing 写侧收尾 3 个（★ 含"解析器消费参数"再次钉住）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch90.py` · `mcp-server/register_capabilities.py`（同笔两个新键）·
#         `scripts/sw_costing.py`
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004/SC-009；★ 本批三条契约：
#         ① 3 个都能解析到真实函数、注入键既在 `RESOLVERS` 里又与首参同名（事实 502）；
#         ② ★ **没有裸坐标**（规则 3）；③ ★★ 「**由解析器消费的参数**」必须写成
#            `param_alias={名字: None}`（★ `tool_registry.py:511-513` 的机制；本会话踩过两次）✓
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
import tool_specs_batch90 as b90                              # noqa: E402

CONSUMED = {"solidworks_costing_assign_custom_cost": "body_name"}
#: ★ 只读侧**早已挂过**的两个 ⇒ 本批不许重复（FR-006）
ALREADY = ("solidworks_costing_read_analysis", "solidworks_costing_read_body")


def test_batch90_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch90"' in t


def test_three_specs_declared_and_resolve():
    assert len(b90.SPECS_BATCH90) == 3, len(b90.SPECS_BATCH90)
    for s in b90.SPECS_BATCH90:
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (s.name, s.module, s.function)
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (s.name, inj, sorted(rc.RESOLVERS))
        first = next(iter(inspect.signature(getattr(m, s.function)).parameters), "")
        assert first == inj, (s.name, first, inj)


def test_two_new_keys_exist():
    assert "cost_analysis" in rc.RESOLVERS and "cost_body" in rc.RESOLVERS


def test_resolver_consumed_param_is_none_alias():
    for s in b90.SPECS_BATCH90:
        want = CONSUMED.get(s.name)
        if want:
            alias = getattr(s, "param_alias", None) or {}
            assert alias.get(want, "缺失") is None, (s.name, alias)


def test_no_bare_coordinates():
    for s in b90.SPECS_BATCH90:
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (s.name, p.name)


def test_read_side_tools_not_duplicated():
    """★ 只读侧那两个**早已挂过** ⇒ 本批只取写侧 3 个（FR-006）✓"""
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    for n in ALREADY:
        assert n in names, "★ 只读侧那个不见了（否则本批的取舍要重新审）: %s" % n
    assert not any(s.name in ALREADY for s in b90.SPECS_BATCH90)
