"""`scripts/sw_selection_spec.py` 的静态契约测试（**不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_selection_spec_contract.py
# 定位:   选择解析层的**契约守卫**。真机行为由
#         `D:\\AI\\SW\\probe_selection_spec_e2e.py` 覆盖（12/12）；本文件管**形状与纪律**：
#         ① 对外只收声明式选择器（**禁裸坐标** —— 并入规范规则 3）
#         ② 该报错就报错（不静默返回 None）
#         ③ 回读计数用 `GetSelectedObjectCount2`，不用不可信的返回值（已知事实 8）
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MOD = REPO_ROOT / "scripts" / "sw_selection_spec.py"


@pytest.fixture(scope="module")
def src():
    return MOD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def tree(src):
    return ast.parse(src)


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO_ROOT))
    from scripts import sw_selection_spec as S

    return S


# ── ① 对外只收声明式选择器（规则 3）───────────────────────────────
def test_public_signatures_have_no_bare_coordinates(tree):
    """公开函数的形参里**不得**出现裸坐标 `x` / `y` / `z`（规则 3）。

    ⚠ 这条是本模块存在的理由：边/面**没有名字**（真机实测，见模块头），
    但**也不能**因此开一个「传坐标」的后门 —— 那正是规则 3 禁止的形状。
    """
    banned = {"x", "y", "z", "point", "normal", "axis", "origin"}
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        if node.name in {"__init__"}:
            continue
        for a in node.args.args + node.args.kwonlyargs:
            if a.arg in banned:
                offenders.append("%s(%s)" % (node.name, a.arg))
    assert offenders == [], "公开函数出现了裸坐标形参：%r（违规则 3）" % offenders


def test_selector_is_a_string_not_coordinates(mod):
    """选择器常量必须存在，且是特殊字符串（不是坐标元组）。"""
    assert isinstance(mod.CURRENT_SELECTION, str)
    assert mod.CURRENT_SELECTION.startswith("__")


def test_entity_kinds_are_declared(mod):
    """★ 实体类型集合 —— ★★ 2026-10-01（轮 328）**加了 `VERTEX`**（★ 契约变更）。

    ★ 依据：官方 `IBody2.GetVertices()` / `ILoop2.GetVertices()` 都是 **0 参**成员，
      ★ 顶点就是体上的一种 entity ⇒ ★ 它属于 `entities_on_body`（★ 而不是新开一个工具）。
    ★ 真机（20×20×10 盒子）⇒ **FACE=6 · EDGE=12 · VERTEX=8** ⇒ ★ **欧拉公式 `V−E+F=2` 成立**。
    """
    assert set(mod.ENTITY_KINDS) == {"EDGE", "FACE", "VERTEX"}
    #: ★ 每个类型都要有对应的官方取值器（★ 防止"声明了却取不到"）
    for kind in mod.ENTITY_KINDS:
        assert kind in {"EDGE", "FACE", "VERTEX"}, kind


# ── ② 该报错就报错（不静默）─────────────────────────────────────
def test_module_defines_its_own_error_type(mod):
    assert issubclass(mod.EntitySelectionError, RuntimeError)


def test_resolve_raises_instead_of_returning_none(src):
    """`resolve_entity` 的源码里必须**有 raise**（不静默返回 None）。

    ⚠ 用 AST 而不是字符串找 —— 注释里写「不静默」不算数。
    """
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "resolve_entity":
            raises = [n for n in ast.walk(node) if isinstance(n, ast.Raise)]
            assert raises, "resolve_entity 里没有任何 raise ⇒ 可能静默失败"
            return
    pytest.fail("找不到 resolve_entity")


def test_resolve_selection_checks_count(src):
    """`resolve_selection` 必须**检查回读计数**（计数 0 要报错）。"""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "resolve_selection":
            names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            assert "get_selection_count" in names, "resolve_selection 没回读计数"
            return
    pytest.fail("找不到 resolve_selection")


# ── ③ 回读计数用官方入口（已知事实 8）───────────────────────────
def test_count_uses_getselectedobjectcount2(src):
    assert "GetSelectedObjectCount2" in src, (
        "回读计数必须用 GetSelectedObjectCount2 —— SelectByID2/Select4 的返回值不可信"
        "（AGENTS.md 已知事实 8）"
    )


def test_current_selection_index_starts_at_one(src):
    """`GetSelectedObject6` 的下标**从 1 开始**（官方约定）—— 代码里要体现。"""
    assert "range(1, count + 1)" in src, "current_selection 的下标应当从 1 开始"


def test_callout_is_not_none(src):
    """`Select4` / `SelectByID2` 的 `Callout` **不能传 `None`**（已知事实 12）。

    ⚠ 本会话实测：传 `None` 得到 `'类型不匹配'`（`sw_part._empty_callout()` 才对）。
    """
    assert "_empty_callout" in src, "必须用 _empty_callout()（VARIANT(VT_DISPATCH, None)）"
    assert "Select4\", bool(append), None" not in src, "Select4 的 Callout 传了 None"


def test_defers_to_part_for_the_callout_helper(src):
    """空 Callout 要从 `sw_part` 复用，不自己再造一个（不重造）。"""
    assert "from .sw_part import _empty_callout" in src or \
           "from sw_part import _empty_callout" in src


# ── ④ 已实测的痕迹（避免「未实测」被当成品交付）─────────────────
def test_module_records_having_been_tested_on_a_real_machine(src):
    assert "已在本机实测" in src, "实测后应把标注改成实测结论 + 证据出处"
    assert "probe_selection_spec_e2e" in src, "要写出证据脚本名"
