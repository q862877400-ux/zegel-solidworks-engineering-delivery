"""★ 规格 213 · B1 的契约与负例：A 类 6 项「实现已有、只差 ToolSpec」（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch100.py`）
# 文件:   tests/test_spec213_batch100_tools.py
# 定位:   ★ 规格 `specs/213-hook-up-tools/` 的 **B1**。★ 起因：★★ `docs/user-feature-coverage.md`
#   只量三列里的**第一列「有入口」**，★ 而它的来源是 `all_specs()` 的**工具名集合** ✓ ⇒
#   ★★★ 规格 211 做成 `verified` 的能力**没有任何 ToolSpec 引用它们** ✗ ⇒
#   ★★ 从「用户可发现、可调用」口径看它们**等于不存在** ✓
# 判据（★ 一正 + 多条负例，★ 事实 62：★ 门禁只靠负例证明 ✓）：
#   ★ **正例①**：★ 6 个 ToolSpec **全部过 `check_spec`** ✓
#   ★ **正例②**：★ 6 个**都进了 `all_specs()`**（★ 那才是"用户能发现" ✓），★ 且**无重名** ✓
#   ★ **正例③**：★ 工具数是 **448 + 6 = 454**（★ 基线 448 是实测的 ✓）
#   ★★ **负例①**：★ `scale_feature` 的**线名不许**是裸 `x`/`y`/`z` ——
#     ★★★ 那正是本批**被门禁教过**的那一处：★ 原名 `x` 被**规则 3** 拦下，
#     逐字「入参 `x` 是**裸坐标** —— 必须改用具名实体 + 声明式 selection」✓
#   ★★ **负例②**：★ 但**函数形参**仍然叫 `x`/`y`/`z` ⇒ ★ **必须靠 `param_alias` 映射回去** ✓
#     （★ `make_tool_function` 逐字：`target = spec.param_alias.get(p.name, p.name)` ✓）
#     本测试**断言那条映射真的在**，★ 否则函数会收到 `x_factor=` 而**炸掉** ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                    # noqa: E402
import tool_registry as R                                             # noqa: E402
import tool_specs_batch100 as B                                       # noqa: E402

#: ★ 本批声明的 6 个工具（★ 与 `tool_specs_batch100.py` 里的名字**逐字对应** ✓）
WANTED = (
    "solidworks_section_properties",
    "solidworks_scale_feature",
    "solidworks_untrim_surface",
    "solidworks_sweep_surface",
    "solidworks_weldment_trim",
    "solidworks_export_flat_pattern_dxf",
)
#: ★★ 基线是**实测**的：★ 本批之前 `len(all_specs()) == 448` ✓
BASE_TOOL_COUNT = 448


#: ── 正例① ───────────────────────────────────────────────────────────────
def test_all_six_pass_check_spec():
    """★ **正例①**：★ 6 个 ToolSpec 全部过 `check_spec`（★ 规则 2 / 2b / 3 都在里面 ✓）。"""
    assert len(B.SPECS_BATCH100) == 6
    for s in B.SPECS_BATCH100:
        R.check_spec(s)                      #: ★ 不过就抛 `GateError` ✓


#: ── 正例② ───────────────────────────────────────────────────────────────
def test_all_six_are_in_all_specs():
    """★ **正例②**：★ 6 个**都进了 `all_specs()`** —— ★★ 那才是"**用户能发现**" ✓。

    ★★★ 这条正是本规格存在的理由：★ 能力做完了却**没进 `all_specs()`** ⇒
    ★★ 覆盖表的第一列**看不见它** ⇒ ★ 从用户口径**等于不存在** ✓
    """
    names = {getattr(s, "name", "") for s in RC.all_specs()}
    missing = [w for w in WANTED if w not in names]
    assert not missing, "★ 这些没进 all_specs：%r" % missing


#: ── 正例③ ───────────────────────────────────────────────────────────────
def test_tool_count_grew_by_exactly_six():
    """★ **正例③**：★ 工具数 = 基线 **448** + **6** = **454** ✓（★ 不许顺手挂了别的 ✓）。"""
    n = len(RC.all_specs())
    assert n == BASE_TOOL_COUNT + 6, "★ 期望 %d、实际 %d" % (BASE_TOOL_COUNT + 6, n)


def test_no_duplicate_tool_names():
    """★ **正例④**：★ 全仓**无重名工具** ✓（★ 重名会让 MCP 注册静默丢一个 ✓）。"""
    names = [getattr(s, "name", "") for s in RC.all_specs()]
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, "★ 重名：%r" % dupes


#: ── 负例① ───────────────────────────────────────────────────────────────
def test_scale_feature_has_no_bare_coordinate_param_names():
    """★★ **负例①**：★ 线名**不许**是裸 `x`/`y`/`z` ✓

    ★★★ 事由（本批**被门禁教过**的那一处）：★ 原名 `x` 被**规则 3** 拦下，逐字 ——
    「规则 3 违反：工具 `solidworks_scale_feature` 的入参 `x` 是**裸坐标**
    —— 必须改用具名实体 + 声明式 selection」✓
    ★★ 而它们**其实是无量纲缩放比例**（★ 不是坐标 ✗）⇒ ★ 改名 `*_factor` ✓
    """
    spec = next(s for s in B.SPECS_BATCH100 if s.name == "solidworks_scale_feature")
    wire = [p.name for p in spec.params]
    bare = [n for n in wire if n in ("x", "y", "z", "point", "coordinate")]
    assert not bare, "★ 线名仍是裸坐标：%r ⇒ 规则 3 会拦" % bare
    #: ★ 而**正确形态**是带 `_factor` 后缀（★ 语义："无量纲比例" ✓）
    assert "x_factor" in wire and "y_factor" in wire and "z_factor" in wire, wire


#: ── 负例② ───────────────────────────────────────────────────────────────
def test_scale_feature_param_alias_maps_back_to_function_kwargs():
    """★★ **负例②**：★ 线名改了 ⇒ ★ **必须靠 `param_alias` 映射回函数形参** ✓

    ★★★ 为什么这条是负例而不是废话：★ 函数（`sw_part.insert_scale`）的形参**仍叫** `x`/`y`/`z` ✓
    ⇒ ★★ 若 `param_alias` **漏了**那三项，★ `make_tool_function` 会传 `x_factor=` 给函数
      ⇒ ★ **函数收到不认识的 kwarg ⇒ 真机调用当场炸** ✗
    ★ `tool_registry.make_tool_function` 逐字实现：`target = spec.param_alias.get(p.name, p.name)` ✓
    """
    spec = next(s for s in B.SPECS_BATCH100 if s.name == "solidworks_scale_feature")
    alias = dict(spec.param_alias or {})
    assert alias.get("x_factor") == "x", alias
    assert alias.get("y_factor") == "y", alias
    assert alias.get("z_factor") == "z", alias
    #: ★★ 而**函数那边确实叫 `x`/`y`/`z`** ⇒ ★ 这条映射是**必需**的、不是装饰 ✓
    import inspect
    import sw_part as P
    fn_params = set(inspect.signature(P.insert_scale).parameters)
    assert {"x", "y", "z"} <= fn_params, fn_params


#: ★ 附：本批的"六项各自对应一个真实存在的被包函数" —— ★ 防"声明了但模块里没有" ✓
@pytest.mark.parametrize("spec", B.SPECS_BATCH100, ids=lambda s: s.name)
def test_declared_target_function_exists(spec):
    import importlib
    mod = importlib.import_module(spec.module)
    assert callable(getattr(mod, spec.function, None)), (
        "★ %s.%s 不存在 —— 声明与实现脱节" % (spec.module, spec.function))
