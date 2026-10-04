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

#: ★★★★ 2026-10-04（真机探针的后裁决）：这 4 个**必须不在**本批里 ——
#:   · 两个 `sw_sketch` 的：★ **机测证明返回裸 COM 对象**（`CDispatch`）⇒ 过不了 JSON 边界；
#:   · 两个 `sw_assembly` 的：★ **没验成**（建立不起该成员认得的组件选择）⇒ 未实测不发货 ✓
#:   ★ 证据：`output/batch88-return-types-evidence.json`（`tools/probe_batch88_return_types.py`）
#:   ★ 原因逐条写在 `tools/bunny_toolspec_pipeline.py` 的 `REFUSED` 里 ✓
RETRACTED = ("solidworks_sketch_relation_manager",
             "solidworks_sketch_model_to_sketch_transform",
             "solidworks_assembly_get_component_feature",
             "solidworks_assembly_get_feature_entity")


def test_batch88_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch88"' in t


def test_thirteen_specs_declared():
    """★ 原 17 个，**真机探针后撤下 4 个** ⇒ **13** ✓"""
    assert len(b88.SPECS_BATCH88) == 13, len(b88.SPECS_BATCH88)


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


def test_the_four_retracted_tools_are_absent():
    """★★★ 撤回的那 4 个**不许在注册表里** —— ★ 未实测不发货，撤了就要真的撤 ✓"""
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    leaked = [n for n in RETRACTED if n in names]
    assert not leaked, "★ 又把撤回的挂回来了: %r" % (leaked,)
