'''★ 规格 220 · PDM 相邻证据工具的契约与负例（★ 不连真机）。'''
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（mcp-server/tool_specs_batch108.py）
# 文件:   tests/test_spec220_pdm_tool.py
# 定位:   ★ 规格 220（目标 145/145）的 **其他/PDM** 一格。
# 判据（★ 事实 62：门禁只靠负例证明）：
#   ★ 正例① 过 check_spec · 在 all_specs() 且无重名
#   ★ 正例② 工具数 >= 474 + 1 = 475（★ 单调下界）
#   ★ 正例③ 被某个台账条目认领（三件套第 2 件）
#   ★★ 负例① ★ **不许收坐标**（规则 3）
#   ★★ 负例② ★ **不许把 stitched 写成 verified** —— 本工具**尚未真机验证** ⇒
#      台账 document_dependencies 的 level 不许被抬（红线⑥）✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / 'mcp-server'), str(ROOT / 'scripts')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC

NEW = ('solidworks_pdm_evidence_report',)
BASE = 474


def _specs():
    return {s.name: s for s in RC.all_specs()}


def test_spec_ok_and_registered():
    '''★ 正例①'''
    from tool_registry import check_spec
    specs = _specs()
    for n in NEW:
        assert n in specs, n
        check_spec(specs[n])
    names = [s.name for s in RC.all_specs()]
    for n in NEW:
        assert names.count(n) == 1


def test_tool_count_lower_bound():
    '''★ 正例②'''
    assert len(RC.all_specs()) >= BASE + len(NEW)


def test_claimed_by_ledger():
    '''★ 正例③'''
    import yaml
    doc = yaml.safe_load((ROOT / 'capabilities.yaml').read_text(encoding='utf-8'))
    claimed = set()
    for c in doc['capabilities']:
        claimed.update(str(t) for t in (c.get('mcp_tools') or []))
    for n in NEW:
        assert n in claimed, n


def test_no_bare_coords():
    '''★ 负例①'''
    bare = {'x', 'y', 'z', 'x_mm', 'y_mm', 'z_mm'}
    for n in NEW:
        for p in _specs()[n].params:
            assert p.name.lower() not in bare


def test_level_not_raised():
    '''★ 负例② 红线六'''
    import yaml
    doc = yaml.safe_load((ROOT / 'capabilities.yaml').read_text(encoding='utf-8'))
    got = {c.get('id'): c.get('level') for c in doc['capabilities']}
    assert got.get('pdm') == 'not_implemented', got.get('pdm')
