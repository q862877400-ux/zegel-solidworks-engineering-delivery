"""★ 规格 213 · B2/B3（前半）的契约与负例：`weld_symbol` + `forming_tool`（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_weldment.py` · `scripts/sw_sheet_metal.py` ·
#         `mcp-server/tool_specs_batch101.py`）
# 文件:   tests/test_spec213_batch101_tools.py
# 定位:   ★ 规格 `specs/213-hook-up-tools/` 的 **B2 + B3 前半**。★ B 类的两步：
#   ★★ **第一步（B2）**：★ 把探针里**已证实**的调用序**缝进 `scripts/` 模块**（铁律 3 + 铁律 1）✓
#   ★★ **第二步（B3）**：★ 把模块函数**挂成 ToolSpec** ✓
# 判据（★ 一正多负，★ 事实 62：★ 门禁只靠负例证明）：
#   ★ **正例①**：★ 2 个 ToolSpec 过 `check_spec` ✓
#   ★ **正例②**：★ 2 个都进了 `all_specs()` ✓ · ★ 工具数 = **454 + 2 = 456** ✓ · ★ 无重名 ✓
#   ★★ **正例③（★ B 类的**特有**契约）**：★ 声明的**目标函数真的存在**、★ 且**签名对得上**
#     —— ★★ 因为 B 类的模块函数是**本批新写的**（★ A 类的实现早就在、B 类的不是 ✓）
#   ★★ **负例①**：★ `forming_tool` 的角度参数**必须**以 `_deg` 结尾（★ 规则 2）✓
#   ★★ **负例②**：★ `weld_symbol` 的符号名参数**不许**带单位后缀
#     （★ 规则 2b：★ 字符串/枚举 ⇒ 无量纲 ⇒ ★ 名字不许带单位后缀 ✓）
#   ★★ **负例③**：★ 两项都**不许**声明 `read_only=True`（★ 它们**都会新建特征** ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                    # noqa: E402
import tool_registry as R                                             # noqa: E402
import tool_specs_batch101 as B                                       # noqa: E402

WANTED = ("solidworks_insert_weld_symbol", "solidworks_insert_form_tool")
#: ★★ 基线是**实测**的：★ `batch100` 挂完后 `len(all_specs()) == 454` ✓
BASE_TOOL_COUNT = 454

#: ★ 单位后缀表（★ 机械判据、★ 不许靠 LLM 判 —— 规格 212 的核心纪律 ✓）
UNIT_SUFFIXES = ("_mm", "_mm2", "_mm3", "_deg", "_px", "_s", "_kg", "_m2", "_rad")


def _spec(name: str):
    return next(s for s in B.SPECS_BATCH101 if s.name == name)


#: ── 正例① ───────────────────────────────────────────────────────────────
def test_both_pass_check_spec():
    """★ **正例①**：★ 2 个 ToolSpec 过 `check_spec`（★ 规则 2 / 2b / 3 都在里面 ✓）。"""
    assert len(B.SPECS_BATCH101) == 2
    for s in B.SPECS_BATCH101:
        R.check_spec(s)


#: ── 正例② ───────────────────────────────────────────────────────────────
def test_both_are_in_all_specs_and_count_grew():
    """★ **正例②**：★ 2 个都进 `all_specs()` ✓ · ★ 工具数**不少于** 454 + 2 ✓ · ★ 无重名 ✓。

    ★★★ **钉关系、不钉数字**（★ 本批在 batch100 那里栽过一次 ✗）：★ 写死"454 + 2 = 456"的话，
    ★★ 下一批再挂工具就会让这条变红 ✗ ⇒ ★ 只断言"**不少于**" + ★"这两个**在**里面" ✓
    """
    names = [getattr(s, "name", "") for s in RC.all_specs()]
    assert len(names) >= BASE_TOOL_COUNT + 2, "★ 期望 ≥ %d、实际 %d" % (BASE_TOOL_COUNT + 2, len(names))
    missing = [w for w in WANTED if w not in names]
    assert not missing, "★ 没进 all_specs：%r" % missing
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, "★ 重名：%r" % dupes


#: ── 正例③（★ B 类特有）────────────────────────────────────────────────
@pytest.mark.parametrize("name", WANTED)
def test_declared_module_function_exists(name):
    """★★ **正例③（B 类特有）**：★ 声明的**模块函数真的存在** ✓

    ★★ 为什么这条对 B 类**尤其要紧**：★ A 类的实现**早就在** `scripts/` 里（★ 只差声明 ✓）；
    ★★ 而 B 类的模块函数是**本批新写的**（★ B2 从探针缝合 ✓）⇒
    ★ 声明与模块**脱节的风险高得多** ✓
    """
    spec = _spec(name)
    import importlib
    mod = importlib.import_module(spec.module)
    fn = getattr(mod, spec.function, None)
    assert callable(fn), "★ %s.%s 不存在或不可调 —— 声明与实现脱节" % (spec.module, spec.function)


def test_weld_symbol_function_signature_matches_the_official_arity():
    """★★ **正例④**：★ `insert_weld_symbol_report` 的参数**对得上官方 6 参 `SetText`** ✓。

    ★ 官方 `IWeldSymbol::SetText` 逐字：
    `SetText( Top, Left, Symbol, Right, Stagger, Contour )` ⇒ ★ **6 参** ✓
    ★★ 而 `InsertWeldSymbol3()` 本身是**零参**（★ 那正是"真入口是另一条 API"的要点 ✓）
    """
    import sw_weldment as W
    got = set(inspect.signature(W.insert_weld_symbol_report).parameters)
    assert {"top", "left", "symbol", "right", "stagger", "contour"} <= got, got


def test_form_tool_function_signature_matches_the_official_arity():
    """★★ **正例⑤**：★ `insert_form_tool_report` 的参数**对得上官方 9 参** ✓。

    ★ 官方 `InsertFormToolFeature` 逐字 9 参：`Path · Flip · RotAngle · Config · OverrideDoc ·
    ShowPunch · ShowProfile · ShowCenter · LinkToPart` ✓
    """
    import sw_sheet_metal as M
    got = set(inspect.signature(M.insert_form_tool_report).parameters)
    want = {"tool_path", "flip", "rot_angle_deg", "config", "override_doc",
            "show_punch", "show_profile", "show_center", "link_to_part"}
    assert want <= got, "★ 缺 %r" % (want - got)


#: ── 负例① ───────────────────────────────────────────────────────────────
def test_form_tool_angle_param_ends_with_deg():
    """★★ **负例①**：★ 角度参数**必须**以 `_deg` 结尾（★ 规则 2）✓

    ★★ 反例（★ 什么算违规）：★ 若它被写成 `rot_angle` / `angle` ⇒ ★ 用户无从知道是度还是弧度 ✗
    """
    spec = _spec("solidworks_insert_form_tool")
    wire = [p.name for p in spec.params]
    ang = [n for n in wire if "angle" in n or "rot" in n]
    assert ang, "★ 本该有角度参数，一个都没找到 ⇒ 声明漏了"
    for n in ang:
        assert n.endswith("_deg"), "★ 角度参数 %r 没有 `_deg` 后缀 ⇒ 规则 2 会拦" % n
    #: ★ 而**模块函数**那一侧也必须是同一个名字（★ 声明与实现同名 ⇒ 无 `param_alias` 需求 ✓）
    import sw_sheet_metal as M
    fn = set(inspect.signature(M.insert_form_tool_report).parameters)
    assert "rot_angle_deg" in fn, fn


#: ── 负例② ───────────────────────────────────────────────────────────────
def test_weld_symbol_string_params_carry_no_unit_suffix():
    """★★ **负例②**：★ 字符串/枚举类参数**不许**带单位后缀（★ 规则 2b）✓

    ★★★ 事由：★ 规则 2b 的两半 —— ★ 「名字带单位后缀 ⇒ 描述必须有单位词」**且**
    ★ 「无量纲 / 枚举 / 布尔 ⇒ **名字不许带单位后缀**」✗
    ★★ `left` / `symbol` / `right` / `stagger` 都是**字符串**（★ 内容其实是标注文字的**占位符** ✓），
    `contour` 是**枚举** ⇒ ★ 一个都不该带单位后缀 ✓
    """
    spec = _spec("solidworks_insert_weld_symbol")
    for p in spec.params:
        if p.kind is str or p.name == "contour":
            bad = [s for s in UNIT_SUFFIXES if p.name.endswith(s)]
            assert not bad, "★ %r 是字符串/枚举却带了单位后缀 %r ⇒ 规则 2b 会拦" % (p.name, bad)


#: ── 负例③ ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("name", WANTED)
def test_both_are_not_declared_read_only(name):
    """★★ **负例③**：★ 两项都**不许**声明 `read_only=True` —— ★ 它们**都会新建特征** ✗。

    ★★ 为什么这条值得单列：★ 声明成只读会让**效应规则**（★ 规格 210 的产物）判错 ——
    ★ 而"多声明了一次写"只是啰嗦、★ **漏声明一次写会让并发调用撞车** ✓
    """
    spec = _spec(name)
    assert not R.effective_read_only(spec), (
        "★ %s 被声明成只读，★ 而它真的会改模型（新建特征）✗" % name)
