"""★ 引号修复器的语义护栏（★ 它改坏过真断言，★ 这轮根治）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/fix_cjk_quotes.py` 的 `fix_text` / `_string_constants`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**（★ 一路踩出来的工具修复）。★ 起因（真机）：
#   ★★ `assert fp["readings"]["display"] == str(("另一个", "默认<按加工>"))` 被改成
#     `str(("另一个「, 」默认<按加工>"))` ✗✗ —— ★ 它把**代码里的两个字符串**
#     当成了"散文里的引号对" ✓
#   ★ 现象有多坑：★ 那个文件**仍能解析**（★ 只是**语义变了**）⇒
#     ★★ 于是**一条一直绿的测试突然红，而报错指向断言的值、不指引号** ✗
# 判据:   ★★ **语义级护栏**（★ 不是形态级）：★ 若**原文能解析**，★ 则**字符串常量集合必须一字不变** ✓
#   ★★ 且**粒度精确到行**：★ 全有全无**太粗** —— ★ 一个文件里既有正当散文、又有会改坏的代码 ⇒
#     ★ 整份拒绝会把**该改的也不改** ✗ ⇒ ★ 只改"改完仍满足不变式"的那些行 ✓
#   ★ **不适用**：★ 原文本来就解析不了（★ 如 `.md`）⇒ ★ 护栏不适用、照改 ✓
# 官方依据: 无 —— ★ 我方工具口径；`ast` 是标准库
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import fix_cjk_quotes as F                                      # noqa: E402


def test_prose_quotes_are_still_fixed():
    """★ 正例：★ 散文里的引号**照旧要改**（★ 护栏不该把正当的也拦掉）✓"""
    out, n = F.fix_text("# ★ 他说\"这是草稿\"，我信了\n")
    assert n == 1 and "「这是草稿」" in out, out


def test_code_strings_are_not_touched_by_the_guard():
    """★★★ **真机坏例的回归**：★ 那次把**代码里的两个字符串**当成了散文引号对 ✗
    ⇒ ★ 现在：★ 断言里的 `("另一个", "默认<按加工>")` **必须原样** ✓"""
    src = ('def f(fp):\n'
           '    assert fp["readings"] == str(("另一个", "默认<按加工>"))\n')
    out, n = F.fix_text(src)
    assert '("另一个", "默认<按加工>")' in out, out
    assert n == 0, n


def test_the_guard_is_per_line_not_all_or_nothing():
    """★★ **粒度判据**：★ 同一文件里既有正当散文、又有会改坏的代码 ⇒
    ★ **散文那行要改到**、★ **代码那行要保住** ✓（★ 全有全无会把该改的也不改 ✗）"""
    src = ('def f(fp):\n'
           '    # ★ 他说"这是草稿"，我信了\n'
           '    assert fp["readings"] == str(("另一个", "默认<按加工>"))\n')
    out, n = F.fix_text(src)
    assert n == 1, n
    assert "「这是草稿」" in out, out
    assert '("另一个", "默认<按加工>")' in out, out


def test_the_guard_does_not_apply_to_non_python_text():
    """★ **不适用**：★ 解析不了的文本（★ 如 `.md`）⇒ ★ 护栏不适用、**照改** ✓"""
    out, n = F.fix_text('★ 他说"这是草稿"，我信了\n')
    assert n == 1 and "「这是草稿」" in out, out


def test_string_constants_extraction_is_recursive_and_sorted():
    got = F._string_constants('x = ("b", ["a", "c"])\n')
    assert got == ["a", "b", "c"], got
    assert F._string_constants("def (:\n") is None        # ★ 解析不了 ⇒ None ✓
