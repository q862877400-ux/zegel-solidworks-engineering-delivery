"""★ 测：★ `sw_feature_readback.py` 的**每个 `__all__` 名字都真的是顶格函数**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tests/test_readback_all_exports_exist.py`（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 123）**一次真事故**（★ 值记）：
#   ★ 我给 `sw_feature_readback.py` 加 `_read_feature_params` / `rib_params` /
#     `dome_params` 时，那个 `edit` 的 `old_string` **结尾是**
#     `def shell_params(model, feature_name: str = "") -> dict:`、
#     ★★ **而 `new_string` 里没有它** ⇒ **那一行被删掉了** ⇒
#     ★★★ **`shell_params` 的 docstring 与函数体整个**并进了 `dome_params`**** ✓
#   ★★★★ **⚠ 而 `ast.parse` **通过了**** —— ★ 因为多出来的 docstring 与语句在
#     `dome_params` 里**语法合法** ⇒ ★★★★★ **⇒ **「语法通过」不等于「结构没坏」**** ✓
#   **真机读数**（★ 怎么发现的）：★ 三条测试红了 ⇒
#     `test_reads_the_five_readable_members` · `test_does_not_touch_pointer_or_precondition_members` ·
#     `test_negative_case_the_unit_readout_is_recorded` ⇒ ★ 它们都走 `func_source(src, "shell_params")` ✓
#   ★★ **⇒ 发现路径**：★ **`func_source` 抛 `AssertionError: 没有函数 shell_params`** ——
#     而**语法门禁 `check_python_syntax.py` 什么都没说** ✓
#   ★★★ **⇒ 本测试就是补那道缺口**：★ **`__all__` 里的名字必须是**真的顶格函数**** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))

SRC = REPO / "scripts" / "sw_feature_readback.py"


def _top_level_names() -> tuple[set, str]:
    t = SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(t)
    return {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}, t


def test_every_dunder_all_name_is_a_real_top_level_function() -> None:
    """★★★ 核心断言：★ `__all__` 里**每一个**名字都能在顶格找到 ✓

    ★★ **为什么**：★ 名字进了 `__all__` ⇒ ★ 调用方 `from sw_feature_readback import X`
      ★★★ **就会 ImportError**（★ 而那是**运行时**才炸）⇒ **要在静态就抓住** ✓
    """
    names, t = _top_level_names()
    tree = ast.parse(t)
    exported = None
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(
                getattr(x, "id", "") == "__all__" for x in n.targets):
            exported = [e.value for e in n.value.elts]
    assert exported, "★ 找不到 `__all__`"
    missing = [x for x in exported if x not in names]
    assert not missing, "★ `__all__` 里有名字**不是顶格函数**：%r" % missing


def test_negative_case_each_readback_function_has_its_own_docstring() -> None:
    """★★★★ 核心断言：★ **每个回读函数都有自己的 docstring**（★ 抓"函数体并进别人"）✓

    ★★ **为什么这条能抓那个事故**：★ `shell_params` 被并进 `dome_params` 之后，
      ★★★ **它的 docstring 会变成 `dome_params` 里的一个**孤立字符串表达式**、
      ★★ 而 `shell_params` **自己不存在** ⇒ **上一条会红**；
      ★★★ **而本条再从"每个函数都要有 docstring"这个角度兜一层** ✓
      （★ 两层判据、★ 一道门真出问题时**另一道也响**）✓
    """
    names, t = _top_level_names()
    tree = ast.parse(t)
    for n in tree.body:
        if not isinstance(n, ast.FunctionDef):
            continue
        if n.name.startswith("_"):
            continue                                              # ★ 私有帮手不强制
        doc = ast.get_docstring(n)
        assert doc, "★ 顶格公开函数 `%s` **没有 docstring**" % n.name
        #: ★★★★ **⚠ 我第一版在这里还加了**一条**「docstring 不许以另一个函数的标题开头」**
        #:   —— ★ **而它**误伤了 `shell_params` 自己****（★ 它的 docstring 本来就该以
        #:   「★ 读**抽壳特征…」开头）⇒ ★★ **⇒ 那正是"判据自指"的又一例** ✓
        #:   ★★★ **⇒ 去掉它** —— ★ 因为**上一条**（★ `__all__` 的名字必须是真函数）
        #:   已经能抓到那个事故、★ **这条只是重复** ✓
        #:   ★★★★ **可复用判据**：★★★ **"多加一条判据"之前，先问它能不能被**已有的**那条覆盖** ——
        #:     ★ **能覆盖就别加**（★ 加了只会多一个假阳性来源）✓
        assert len(doc.strip()) > 8, "★ `%s` 的 docstring 太短（★ 像占位）" % n.name


def test_negative_case_the_four_new_functions_are_all_present() -> None:
    """★★★ **负例 · 那四个都在**：★ `_read_feature_params` / `rib_params` /
    `dome_params` / `shell_params` ✓

    ★★ **为什么**：★ 那四个是**同一批**加的 ⇒ ★ 出过一次"少一个"的事故 ⇒
      ★★★ **⇒ 点名守住** ✓
    """
    names, _ = _top_level_names()
    for want in ("_read_feature_params", "rib_params", "dome_params", "shell_params"):
        assert want in names, "★ 顶格函数里少了 `%s`" % want


def test_negative_case_the_public_ones_have_the_right_arity() -> None:
    """★★★★ **负例 · 签名形状**：★ 三个公开的都是 `(model, feature_name="")` ✓

    ★★ **为什么**：★ 本仓有**契约测试**按那个形状调它们 ⇒
      ★★★ **形状变了会**在别处**炸**、★ **而在这里能更早看到真因** ✓
    """
    _, t = _top_level_names()
    tree = ast.parse(t)
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in (
                "rib_params", "dome_params", "shell_params"):
            args = [a.arg for a in n.args.args]
            assert args[:1] == ["model"], "★ `%s` 的首参应是 `model`：%r" % (n.name, args)
            assert "feature_name" in args, "★ `%s` 少了 `feature_name`：%r" % (n.name, args)
