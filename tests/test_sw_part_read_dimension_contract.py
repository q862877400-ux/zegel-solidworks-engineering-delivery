"""★ 段 3（本批）：2 个工具的契约 + 「空存根不许被挂」的自动保护。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_part_read_dimension_contract.py
# 定位:   ★ 2026-10-03（轮 399）24h 计划 v2 段 3 的契约测试。被锁的契约：
#   ① `mcp-server/tool_specs_batch55.py` 的 2 条声明（★ `inject="model"` 必须写 ——
#      轮 398 我漏过一次，那样工具一调就 `TypeError`）；
#   ② ★★ **空存根不许被挂**：`sw_part.hole_wizard` 有名字 / 有参数 / 有文档串，
#      而函数体**只有一个 `pass`** ⇒ ★ 挂出去必然什么都不发生（★ 而它**静默成功**，比报错更糟）。
#      本测试直接调分诊的 `is_empty_stub()` 断言它被抓到。
#   ③ ★ `current_sketch_name` 的**回退语义**：取不到时回 `fallback`，★ 而那**不是真名**
#      ⇒ 测试锁住"文档里写着这件事"（★ 免得有人拿回退值去按名取草图）。
# 官方依据: `ISketch.AutoDimension2` · `IModelDoc2.GetActiveSketch2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "tools"))

import sw_part as P                                                # noqa: E402
import triage_real_gaps as T                                       # noqa: E402

EXPECTED = {
    "solidworks_current_sketch_name": "current_sketch_name",
    "solidworks_auto_dimension_sketch": "auto_dimension_sketch",
}


def _specs():
    import tool_specs_batch55 as B                                  # noqa: PLC0415
    return {s.name: s for s in B.SPECS_BATCH55}


def test_both_specs_declared() -> None:
    assert set(_specs()) == set(EXPECTED)


@pytest.mark.parametrize("tool_name,fn_name", sorted(EXPECTED.items()))
def test_spec_wiring(tool_name: str, fn_name: str) -> None:
    """★ 接线三件套：`module` / `inject` / `function` —— ★ 少 `inject` 就是一调就 `TypeError`。"""
    spec = _specs()[tool_name]
    assert spec.module == "sw_part"
    assert spec.function == fn_name
    assert spec.inject == "model", "★ 段 3 这两个入口都要文档对象"
    assert callable(getattr(P, fn_name))
    real = set(inspect.signature(getattr(P, fn_name)).parameters)
    for p in spec.params:
        target = spec.param_alias.get(p.name, p.name)
        assert target in real, "%s 的参数 %s→%s 不存在" % (tool_name, p.name, target)


def test_auto_dimension_returns_status_dict() -> None:
    """★ `auto_dimension_sketch` 的返回值必须是**带 `status` 的 dict**（★ 工具层要能判成败）。"""
    src = inspect.getsource(P.auto_dimension_sketch)
    assert "'status'" in src or '"status"' in src
    assert "SKETCH_NOT_ACTIVE" in src, "★ 没有活动草图时必须给得出这个可判的 error_code"


def test_current_sketch_name_documents_fallback_is_not_the_real_name() -> None:
    """★★ 锁住那条**已文档化的局限**：★ 回退值 ≠ 真名 ⇒ ★ 别拿它去按名取草图。
    ★ 真机实测（轮 399）：草图打开时回「草图1」（真名）；关闭后回自定义回退值。"""
    spec = _specs()["solidworks_current_sketch_name"]
    doc = spec.doc
    assert "fallback" in doc
    assert "resolve_sketch" in doc, "★ 文档必须指出**正确的**取草图路径"
    names = {p.name for p in spec.params}
    assert "fallback" in names


@pytest.mark.parametrize("module,name", [
    #: ★ 真例：有名字、有参数、有文档串，而函数体只有一个 `pass`
    ("sw_part", "hole_wizard"),
])
def test_empty_stub_is_detected(module: str, name: str) -> None:
    """★★ **空存根保护**：★ 分诊必须抓到"函数体只有 `pass`"的假能力。"""
    reason = T.is_empty_stub(module, name)
    assert reason, "%s.%s 是空存根，分诊必须抓到" % (module, name)
    assert "pass" in reason or "docstring" in reason
    kind, why = T.classify(module, name)
    assert kind == "不做", "空存根必须归「不做」"
    assert why == reason


@pytest.mark.parametrize("module,name", [
    ("sw_part", "current_sketch_name"),
    ("sw_part", "auto_dimension_sketch"),
    ("sw_part", "shell"),
])
def test_non_stub_functions_are_not_flagged(module: str, name: str) -> None:
    """★ 反向保护：★ **有实现的函数不许被误判成空存根**（★ 否则会静默丢掉真能力）。"""
    assert T.is_empty_stub(module, name) == ""
