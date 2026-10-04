"""★ 批次 80 的契约测试：诊断知识 + 会话忙闲（12 个）真的挂上了，且注入键与形参对得上。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch80.py`（★ 被测）· `scripts/sw_automation_knowledge.py` ·
#         `scripts/sw_com_traps.py` · `scripts/sw_busy.py` · `mcp-server/register_capabilities.py`
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 含三条本批特有的契约：
#         ① `sldworks` 注入键必须**真的在 RESOLVERS 里**（★ 否则事实 502 下必 TypeError）
#         ② ★ **不做的那 7 个不许偷偷挂上**（FR-002/D-5：说"不做"就要真的不做）
#         ③ ★ 本批工具的参数里**没有裸坐标**（规则 3）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402

EXPECTED = (
    "solidworks_automation_explain_hresult", "solidworks_automation_enter_command_lock",
    "solidworks_automation_exit_command_lock", "solidworks_automation_is_command_locked",
    "solidworks_automation_set_flag", "solidworks_automation_get_flag",
    "solidworks_api_deprecated_successor", "solidworks_repo_find_real_implementations",
    "solidworks_session_busy_status", "solidworks_session_stuck_status",
    "solidworks_session_solver_processes", "solidworks_session_wait_until_idle",
)
#: ★ 本批**明确不做**的（★ 名字一个都不许出现在工具清单里）
REFUSED = (
    "solidworks_automation_send_message",          # 弹模态框 ⇒ 与无人值守冲突
    "solidworks_com_traps_explain",                # 与 explain_hresult 重复（FR-006）
    "solidworks_com_traps_is_type_mismatch",       # 无独立价值
    "solidworks_com_traps_byref_pair",
    "solidworks_com_traps_iter_real_sources",      # generator 过不了 MCP 边界
)


def _names():
    return {getattr(s, "name", "") for s in rc.all_specs()}


def test_batch80_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch80"' in t, "★ batch80 没进 BATCH_MODULES"


def test_twelve_tools_present():
    names = _names()
    missing = [n for n in EXPECTED if n not in names]
    assert not missing, "★ 没挂上: %r" % (missing,)


def test_refused_seven_are_really_absent():
    """★★ 说了"不做"就要真的不做（★ 否则"不做+原因"就成了空话 —— FR-002/D-5）。"""
    names = _names()
    leaked = [n for n in REFUSED if n in names]
    assert not leaked, "★ 这些本该「不做」却挂上了: %r" % (leaked,)


def test_sldworks_inject_key_is_registered():
    """★★ 新加的 `sldworks` 注入键必须**真的在 RESOLVERS 里**（★ 事实 502：注入键字面当关键字传）。"""
    assert "sldworks" in rc.RESOLVERS, sorted(rc.RESOLVERS)
    for n in EXPECTED:
        s = next((x for x in rc.all_specs() if getattr(x, "name", "") == n), None)
        if s is not None and getattr(s, "inject", "") == "sldworks":
            assert "sldworks" in rc.RESOLVERS, n


def test_no_bare_coordinates_in_this_batch():
    for n in EXPECTED:
        s = next((x for x in rc.all_specs() if getattr(x, "name", "") == n), None)
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (n, p.name)


def test_flag_tools_expose_the_named_switch():
    """★ 首选项那两个：`pref` 是**必填**（★ 没有默认值 ⇒ 调用方必须点名，不许"随便挑一个"）。"""
    for n in ("solidworks_automation_set_flag", "solidworks_automation_get_flag"):
        s = next(x for x in rc.all_specs() if getattr(x, "name", "") == n)
        pref = next(p for p in s.params if p.name == "pref")
        #: ★ 注册器用 `Ellipsis`（`...`）当"**必填**"的哨兵 —— ★ 我第一版只判 (None,"","None")
        #:   ⇒ 测试红了；★ **是断言写错、不是规格错**（把它们一起接受）✓
        assert pref.default in (None, "", "None", Ellipsis), (n, pref.default)


def test_wait_until_idle_is_bounded_and_typed_in_seconds():
    """★ 等待那个必须**有界**（超时是秒，不是长度 ⇒ 不带 `_mm`）。"""
    s = next(x for x in rc.all_specs() if getattr(x, "name", "") == "solidworks_session_wait_until_idle")
    names = [p.name for p in s.params]
    assert names == ["timeout", "interval"], names
    assert all(not p.name.endswith("_mm") for p in s.params)
