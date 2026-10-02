"""第六批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch6.py
# 定位:   守 `mcp-server/tool_specs_batch6.py`（轮 93：孤立能力暴露的第二步）。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **核心价值**：声明是**手抄**的，手抄会漂移 ⇒ 用 `inspect.signature` 对着**真实函数**核。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT / "mcp-server", REPO_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

SPECS = importlib.import_module("tool_specs_batch6").SPECS_BATCH6

EXPECTED = {
    "solidworks_available_point_selectors": ("sw_geometry_selectors", "available_point_selectors"),
    "solidworks_available_direction_selectors": ("sw_geometry_selectors", "available_direction_selectors"),
    "solidworks_collect_assembly_bom": ("sw_delivery", "collect_assembly_bom"),
}


def test_batch6_declares_exactly_the_intended_three():
    """@brief 声明集合与预期**逐条相等**。"""
    assert {s.name for s in SPECS} == set(EXPECTED)


def test_batch6_names_follow_solidworks_prefix():
    """@brief 命名统一（并入规则 1）。"""
    for s in SPECS:
        assert s.name.startswith("solidworks_") and s.name.islower(), s.name


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch6_target_exists(spec):
    """@brief 指向的**真实函数**必须存在。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    assert callable(getattr(mod, spec.function, None)), spec.function


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch6_params_match_signature(spec):
    """@brief 声明的参数名必须真在签名里。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    real = set(inspect.signature(getattr(mod, spec.function)).parameters)
    for p in spec.params:
        target = (spec.param_alias or {}).get(p.name, p.name)
        assert target in real, "%s: %s → %s 不在 %s" % (spec.name, p.name, target, sorted(real))


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch6_injection_matches_signature(spec):
    """@brief **无参函数不许注入**；首参叫 `model` 的必须注入 `model`。

    ⚠ 这条是本批特有的：`available_*_selectors()` **不收文档**，
    错标 `inject="model"` 会让它在无文档时**无谓失败**。
    """
    mod = importlib.import_module("scripts.%s" % spec.module)
    params = list(inspect.signature(getattr(mod, spec.function)).parameters)
    if not params:
        assert not spec.inject, "%s 无参，不该注入 %r" % (spec.name, spec.inject)
        assert spec.needs_model is False, "%s 无参，不该 needs_model" % spec.name
    elif params[0] == "model":
        assert spec.inject == "model", spec.name


def test_batch6_all_read_only():
    """@brief 本批 3 个全是**纯读**（声明必须标出来）。"""
    for s in SPECS:
        assert s.read_only is True, s.name
