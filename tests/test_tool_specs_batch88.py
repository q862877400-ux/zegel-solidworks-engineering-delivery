"""★ 批次 88 的契约测试：第六坡（`sketch`/`selection` 两组 C 类）产出的 17 个。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch88.py`（生成物）· `output/bunny6-filtered-report.json`（真新行）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批三条契约：
#         ① ★ **17 个都要能解析到真实函数**、注入键既在 `RESOLVERS` 里又与首参同名（事实 502）
#         ② ★ **没有裸坐标**（规则 3）
#         ③ ★★ **如实记下静态查不到的风险**：有几个函数的**返回可能是 COM 对象**
#            （★ 门禁只看入参，故这条**查不到** ⇒ 测试里把它**显式列为待复核**，不假装没问题）✓
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
import tool_specs_batch88 as b88                              # noqa: E402

#: ★★ 静态查不到"返回是不是 COM 对象" ⇒ ★ 这 4 个**显式列为待真机复核**（★ 不假装没问题）
RETURN_RISK = ("solidworks_assembly_get_component_feature",
               "solidworks_assembly_get_feature_entity",
               "solidworks_sketch_relation_manager",
               "solidworks_sketch_model_to_sketch_transform")


def test_batch88_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch88"' in t


def test_seventeen_specs_declared():
    assert len(b88.SPECS_BATCH88) == 17, len(b88.SPECS_BATCH88)


def test_every_spec_resolves_and_inject_matches_first_param():
    for s in b88.SPECS_BATCH88:
        m = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(m, s.function, None)
        assert callable(fn), "%s → %s.%s" % (s.name, s.module, s.function)
        inj = getattr(s, "inject", "")
        assert inj in rc.RESOLVERS, (s.name, inj, sorted(rc.RESOLVERS))
        first = next(iter(inspect.signature(fn).parameters), "")
        assert first == inj, (s.name, first, inj)


def test_no_bare_coordinates():
    for s in b88.SPECS_BATCH88:
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (s.name, p.name)


def test_return_risk_tools_are_still_declared():
    """★★ 把"返回可能是 COM 对象"的那几个**显式钉住** —— ★ 它们仍在本批里，
    但**名字记在这里** ⇒ 若将来改法（报告式包装），这条测试会提醒要同步改 ✓"""
    names = {s.name for s in b88.SPECS_BATCH88}
    missing = [n for n in RETURN_RISK if n not in names]
    assert not missing, "★ 待复核的那几个不在本批里了（改了实现就要同步改这条测试）: %r" % (missing,)
