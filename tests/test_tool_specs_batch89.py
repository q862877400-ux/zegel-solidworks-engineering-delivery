"""★ 批次 89 的契约测试：C 类最后两组（Costing 写侧 3 + 运动算例 2）—— ★ 含"解析器消费参数"这条。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch89.py`（手写，逐条带官方依据）·
#         `mcp-server/register_capabilities.py`（同笔加的两个注入键）·
#         `scripts/sw_costing.py` · `scripts/sw_motion.py`
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批四条契约：
#         ① 5 个都能解析到真实函数；② 注入键既在 `RESOLVERS` 里又与首参同名（事实 502）；
#         ③ **没有裸坐标**（规则 3）；★★ ④ 「**由解析器消费的参数**」必须是
#            `param_alias={名字: None}`（★ `tool_registry.py:511-513` 的机制），
#            **不是**把它当普通参数传下去（★ 那样运行期必 `TypeError` —— 本批真踩过）✓
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
import tool_specs_batch89 as b89                              # noqa: E402

#: ★★ 这两个协议：`motion_study_name` **只给解析器读**、**不传给目标函数** ⇒ 必须是 None 别名 ✓
RESOLVER_CONSUMED = {"solidworks_motion_calculate_and_play": "motion_study_name",
                     "solidworks_motion_export_avi": "motion_study_name"}


def test_batch89_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch89"' in t


def test_five_specs_declared_and_resolve():
    assert len(b89.SPECS_BATCH89) == 5, len(b89.SPECS_BATCH89)
    for s in b89.SPECS_BATCH89:
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (s.name, s.module, s.function)
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (s.name, inj, sorted(rc.RESOLVERS))
        first = next(iter(inspect.signature(getattr(m, s.function)).parameters), "")
        assert first == inj, (s.name, first, inj)


def test_new_resolver_keys_are_the_two_this_batch_added():
    assert "cost_part" in rc.RESOLVERS and "motion_study" in rc.RESOLVERS


def test_resolver_consumed_params_are_none_aliases():
    """★★★ 本批真踩过的坑：★ 给解析器读的参数**必须**写成 `param_alias={名字: None}`
    —— 否则注册器会把它当普通参数传给目标函数 ⇒ 运行期 `TypeError`（★ 门禁当场抓到过）✓"""
    for s in b89.SPECS_BATCH89:
        want = RESOLVER_CONSUMED.get(s.name)
        if not want:
            continue
        alias = getattr(s, "param_alias", None) or {}
        assert want in alias and alias[want] is None, (s.name, alias)


def test_no_bare_coordinates():
    for s in b89.SPECS_BATCH89:
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (s.name, p.name)


def test_avi_export_does_not_take_the_com_object():
    """★★ 官方 `SaveToAVI(FileName, AVIParameter)` 的第 2 参是 **COM 对象** ⇒ 过不了 JSON 边界
    ⇒ ★ 本工具**不收它**（函数默认 `None`，时长/帧率走 SolidWorks 默认）✓"""
    s = next(x for x in b89.SPECS_BATCH89 if x.name == "solidworks_motion_export_avi")
    names = [p.name for p in s.params]
    assert "avi_parameter" not in names, names
