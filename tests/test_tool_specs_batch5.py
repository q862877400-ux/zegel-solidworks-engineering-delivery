"""第五批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch5.py
# 定位:   守 `mcp-server/tool_specs_batch5.py`（轮 90：孤立能力暴露的第一步）。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **本测试的核心价值**：声明里的 `module`/`function`/参数是**手抄**的，手抄会漂移。
#   故用 `inspect.signature` 对着**真实函数**核 —— 对不上就红。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SPECS = importlib.import_module("tool_specs_batch5").SPECS_BATCH5

EXPECTED = {
    "solidworks_current_selection": ("sw_selection_spec", "current_selection"),
    "solidworks_clear_selection": ("sw_selection_spec", "clear_selection"),
    "solidworks_set_standard_view": ("sw_review", "set_standard_view"),
    "solidworks_list_render_materials": ("sw_render_material", "list_render_materials"),
    "solidworks_collect_appearance_evidence": ("sw_render_material", "collect_appearance_evidence"),
}


def test_batch5_declares_exactly_the_intended_five():
    """@brief 声明集合必须与预期**逐条相等**（多了少了都红）。"""
    assert {s.name for s in SPECS} == set(EXPECTED)


def test_batch5_names_follow_solidworks_prefix():
    """@brief 命名统一（并入规则 1）。"""
    for s in SPECS:
        assert s.name.startswith("solidworks_"), s.name
        assert s.name.islower(), s.name


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch5_module_and_function_exist(spec):
    """@brief 声明指向的**真实函数**必须存在（手抄会漂移，这里钉住）。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    fn = getattr(mod, spec.function, None)
    assert fn is not None, "scripts/%s.py 里没有 %s" % (spec.module, spec.function)
    assert callable(fn)


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch5_declared_params_match_the_real_signature(spec):
    """@brief 声明的每个参数名都必须**真的**在函数签名里（否则注册后会 TypeError）。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    sig = inspect.signature(getattr(mod, spec.function))
    real = set(sig.parameters)
    for p in spec.params:
        target = (spec.param_alias or {}).get(p.name, p.name)
        assert target in real, "%s 声明的 %s（→ %s）不在签名 %s 里" % (
            spec.name, p.name, target, sorted(real))


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch5_injects_model_where_the_function_needs_it(spec):
    """@brief 函数第一个参数叫 `model` 时，声明必须 `inject="model"`（否则拿不到文档）。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    sig = inspect.signature(getattr(mod, spec.function))
    first = next(iter(sig.parameters), None)
    if first == "model":
        assert spec.inject == "model", spec.name


def test_batch5_read_only_flags_match_reality():
    """@brief 纯读函数必须标 `read_only=True`（反过来不强制）。"""
    read_only = {"solidworks_current_selection", "solidworks_list_render_materials",
                 "solidworks_collect_appearance_evidence"}
    for s in SPECS:
        if s.name in read_only:
            assert s.read_only is True, s.name
