"""第十批工具声明的守卫测试（**不依赖 `mcp` 库、不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_tool_specs_batch10.py
# 定位:   守 `mcp-server/tool_specs_batch10.py`（轮 128：把轮 123~127 查证并
#         **真机跑过**的 4 个高层入口接出去）。
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

SPECS = importlib.import_module("tool_specs_batch10").SPECS_BATCH10

#: 工具名 → (模块, 函数, 注入, 首参名)
#: ★★★ **2026-10-03（接手轮）修正**：这三条的注入名从 **`"sw_app"`** 改成 **`"sw"`**。
#:   ★ **本条测试原先断言 `spec.inject == "sw_app"`，而它同一行也断言真实首参 `== "sw"`**
#:     ⇒ ★★ **它把"注入名与真实首参不符"这个 bug 固化成了"期望行为"**，
#:     ★ 依据是那句「`tool_registry` 的 `inject` **本来就支持 `sw_app`**」——
#:     ★ **而那句话是错的**：`register()`（`tool_registry.py:559`）**不传 `inject_as`**
#:     ⇒ **注入键字面上等于 `inject` 的值** ⇒ ★ 真机报
#:     **`TypeError: list_hole_standards() got an unexpected keyword argument 'sw_app'`**
#:     （证据 `output/inject-key-evidence.json`，2026-10-03）。
#:   ⇒ ★ **修法**：注入名改用真实首参名 `sw`（并在 `RESOLVERS` 里加一行 `"sw"`）。
#:   ★ **教训**：★ **一条只做静态断言的测试，会把一个错误信念"洗"成"已验证"** ——
#:     ★ 这条测试与真机之间**隔着一次没人跑的调用**。
EXPECTED = {
    "solidworks_part_bounding_box": ("sw_part", "get_bounding_box", "model", "model"),
    "solidworks_hole_standards": ("sw_hole_features", "list_hole_standards", "sw", "sw"),
    "solidworks_fastener_types": ("sw_hole_features", "list_fastener_types", "sw", "sw"),
    "solidworks_fastener_table_types":
        ("sw_hole_features", "list_fastener_table_types", "sw", "sw"),
}


def test_batch10_declares_exactly_the_intended_four():
    """@brief 声明集合与预期**逐条相等**。"""
    assert {s.name for s in SPECS} == set(EXPECTED)


def test_batch10_names_follow_solidworks_prefix():
    """@brief 命名统一（并入规则 1）。"""
    for s in SPECS:
        assert s.name.startswith("solidworks_") and s.name.islower(), s.name


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch10_target_exists(spec):
    """@brief 指向的**真实函数**必须存在。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    assert callable(getattr(mod, spec.function, None)), spec.function


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch10_params_match_signature(spec):
    """@brief 声明的参数名必须真在签名里。"""
    mod = importlib.import_module("scripts.%s" % spec.module)
    real = set(inspect.signature(getattr(mod, spec.function)).parameters)
    for p in spec.params:
        target = (spec.param_alias or {}).get(p.name, p.name)
        assert target in real, "%s: %s → %s 不在 %s" % (spec.name, p.name, target, sorted(real))


@pytest.mark.parametrize("spec", SPECS, ids=[s.name for s in SPECS])
def test_batch10_injection_matches_the_real_first_parameter(spec):
    """@brief ★ 注入名必须与**真实首参**对得上。

    ⚠ 本批**两种注入混用**：`get_bounding_box` 首参是 `model`（活动文档）；
    `list_*` 三个首参是 **`sw`（`ISldWorks`）**。

    ★★★ **2026-10-03（接手轮）本条被改过** —— 原先的 docstring 写的是
      「⇒ 必须注入 **`sw_app`**」，并断言 `spec.inject == "sw_app"`。
      ★★ **那是错的**：`register()`（`tool_registry.py:559`）**不往下传 `inject_as`**
      ⇒ **注入键字面上等于 `inject` 的值** ⇒ ★ 注入名**必须等于真实首参名**。
      ★ 真机证据：`TypeError: list_hole_standards() got an unexpected keyword argument 'sw_app'`
      （`output/inject-key-evidence.json`）。
      ⇒ ★ 现改为断言注入名 **== 真实首参名**（★ 即本条测试的名字所声称的那件事 ——
        ★ 它原先**名不副实**：名字说"matches the real first parameter"，断言却在要求二者**不同**）。
    """
    _mod, _fn, want_inject, want_first = EXPECTED[spec.name]
    mod = importlib.import_module("scripts.%s" % spec.module)
    params = list(inspect.signature(getattr(mod, spec.function)).parameters)
    assert params and params[0] == want_first, "%s 首参是 %r" % (spec.name, params[:1])
    assert spec.inject == want_inject, "%s 应注入 %r" % (spec.name, want_inject)
    #: ★★ **本条的真正判据**：注入名与真实首参**一致**（★ 事实 502）
    assert spec.inject == params[0], (
        "%s 的 inject=%r 与真实首参 %r **不一致** ⇒ 经工具层必 "
        "`TypeError: unexpected keyword argument`（★ 事实 502）"
        % (spec.name, spec.inject, params[0]))


def test_batch10_tools_are_all_read_only():
    """@brief ★ 这 4 个**都是查询**（不改几何、不改文档）⇒ 必须标 `read_only`。

    ⚠ 与 batch9 相反（那 3 个都改几何）—— 标错会让调用方以为"读一下就改了东西"。
    """
    for s in SPECS:
        assert s.read_only is True, "%s 应当标 read_only" % s.name


def test_batch10_docs_carry_the_measured_warnings():
    """@brief ★★ 每条声明都要把**实测出来的警告**带给调用方。

    没有这段，调用方就不知道：
    * `bbox` 的官方 approximate 声明 与 **单位是毫米**；
    * 紧固件名**随 UI 语言**（中文 UI ⇒ 中文名）；
    * `fastener_id` 是 **Int32 的 ID**，不是尺寸名。
    """
    by_name = {s.name: s for s in SPECS}
    bbox = by_name["solidworks_part_bounding_box"].doc
    assert "APPROXIMATE" in bbox.upper(), "bbox 要带官方 approximate 警告"
    assert "MILLIMETRES" in bbox.upper(), "bbox 要写明单位是毫米（实测）"

    ft = by_name["solidworks_fastener_types"].doc
    assert "UI language" in ft, "要写明名字随 UI 语言"

    ftt = by_name["solidworks_fastener_table_types"].doc
    assert "FASTENER ID" in ftt.upper(), "要写明第二参是紧固件 ID"
    assert "size name" in ftt, "要写明传尺寸名会报错"
