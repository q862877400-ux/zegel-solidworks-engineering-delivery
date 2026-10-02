"""第九批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch9.py
# 定位:   守 `mcp-server/tool_specs_batch9.py`（轮 98：模具域补暴露）。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 声明是**手抄**的 ⇒ 用 `inspect.signature` 对着真实函数核。
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

SPECS = importlib.import_module("tool_specs_batch9").SPECS_BATCH9

EXPECTED = {
    "solidworks_mold_core_cavity_split": ("sw_mold", "insert_core_cavity_solids"),
    "solidworks_mold_parting_surface": ("sw_mold", "insert_parting_surface"),
    "solidworks_mold_undercut_detect": ("sw_mold", "mold_undercut_detect"),
}


def test_batch9_declares_exactly_the_intended_three():
    """@brief 声明集合与预期**逐条相等**。"""
    assert {s.name for s in SPECS} == set(EXPECTED)


def test_batch9_names_follow_solidworks_prefix():
    """@brief 命名统一（并入规则 1）。"""
    for s in SPECS:
        assert s.name.startswith("solidworks_") and s.name.islower(), s.name


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch9_target_exists(spec):
    """@brief 指向的**真实函数**必须存在。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    assert callable(getattr(mod, spec.function, None)), spec.function


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch9_params_match_signature(spec):
    """@brief 声明的参数名必须真在签名里。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    real = set(inspect.signature(getattr(mod, spec.function)).parameters)
    for p in spec.params:
        target = (spec.param_alias or {}).get(p.name, p.name)
        assert target in real, "%s: %s → %s 不在 %s" % (spec.name, p.name, target, sorted(real))


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch9_injection_matches_signature(spec):
    """@brief 首参 `model` 的必须注入 `model`。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    params = list(inspect.signature(getattr(mod, spec.function)).parameters)
    assert params and params[0] == "model", spec.name
    assert spec.inject == "model", spec.name


def test_batch9_is_not_marked_read_only():
    """@brief 这 3 个**都改几何**（插曲面 / 分型面 / 检测）⇒ **不许**标 `read_only`。

    ⚠ 这是一条**反向**判据：它防的是"为了好看给改几何的操作标只读"。
    """
    for s in SPECS:
        assert s.read_only is False, "%s 会改几何，不能标 read_only" % s.name
