"""★ 属性形门禁的**负例**（★ 事实 62：没有负例的判据不算数）。

★ 正例原文取自 `git show d15723d~1:subskills/…/drawing_workflow.py`
（★ 即**修复前**的那一版）—— ★★ 这比手写一个「像 bug 的样本」硬得多。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁的负例测试）+ SolidWorks 出厂反射（判据的真源）
# 文件:   `scripts/check_property_form_members.py`（★ 被测门禁）
# 定位:   ★★★ 为什么必须写它：★ 事实 62 ——「**一个门禁"写了"不等于它"有效"**，
#   ★★ 而**负例测试是唯一的证明**。★ 本测试做两件事：
#     ① ★ **正例**：★ 拿**修复前**的原文（`git show d15723d~1:…/drawing_workflow.py`
#        里逐字是 `get_com_member(model, "GetModelViewManager")`）喂给门禁的判据
#        ⇒ ★★ **必须命中**（★ 否则门禁抓不到它真正要抓的东西）；
#     ② ★ **反例**：★ 修复后的写法（`get_com_member(model, "ModelViewManager")`）
#        与几个**长得很像但合法**的形态 ⇒ ★ **不许命中**（★ 否则它会天天误伤）。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_property_form_members as gate  # noqa: E402

#: ★ 正例：**修复前**那一行的逐字形态（★ 来自 `git show d15723d~1:…`）
OLD_SOURCE = '''
def get_model_view_manager(model):
    """取 IModelViewManager（属性，不是方法）。"""
    manager = get_com_member(model, "GetModelViewManager")
    if manager is None:
        raise RuntimeError("IModelDoc2.GetModelViewManager() 返回 None")
    return manager
'''

#: ★ 反例：修好之后的写法 + 四个**像但合法**的形态
NEW_SOURCE = '''
def get_model_view_manager(model):
    """取 IModelViewManager（属性，不是方法）。"""
    manager = get_com_member(model, "ModelViewManager")
    return manager


def other(model):
    a = getattr(model, "GetTitle")          # 官方**有**裸名 GetTitle ⇒ 合法
    b = get_com_member(model, "GetPathName")  # 官方**有**裸名 GetPathName ⇒ 合法
    c = getattr(model, "GetModelViewManagerX")  # ★ `X` 不是官方成员 ⇒ 不属本判据（另一道闸管）
    d = model.GetModelViewManager()             # ★ 不是**字面量**实参 ⇒ 本判据不管（另一形态）
    return a, b, c, d
'''


def _hits(src: str) -> list[tuple[int, str, str]]:
    cls = gate.classify()
    pages = gate.official_pages()
    tree = ast.parse(src)
    out = []
    for lineno, fn, lit in gate._string_args(tree):
        if gate.is_property_form(lit, cls, pages):
            out.append((lineno, fn, lit))
    return out


def test_gate_is_armed_the_official_source_is_readable() -> None:
    """★ 判据的**两个**真源都必须在（★ 读不到就该 SKIP，而不是假装绿）。"""
    assert any(r.is_file() for r in gate.REFLECTIONS), (
        "★ 本机读不到出厂反射 ⇒ 这条门禁判不了（★ 门禁自己会报 SKIP）")
    pages = gate.official_pages()
    assert pages, "★ 本机读不到官方 md 镜像 ⇒ 收敛器不在（★ 门禁自己会报 SKIP）"
    assert "property" in pages.get("ModelViewManager", set()), (
        "★ 官方 `IModelDoc2.ModelViewManager` 是 `kind: property` ⇒ 它必须被认出来")
    #: ★★★ 收敛器的**负例**：这些是**官方方法**（★ 各有自己的页）⇒ ★ **不许**被当成属性形
    for legal in ("GetCurrentSheet", "GetBodies2", "GetAnnotationCount", "SetViewPosition"):
        assert legal in pages, "★ %s 官方**有页** ⇒ 它是合法方法" % legal
        assert not gate.is_property_form(legal, gate.classify(), pages), (
            "★ 误伤：%s 是官方方法（有页），却被判成属性形" % legal)


def test_positive_the_pre_fix_line_is_caught() -> None:
    """★★★ 核心：**修复前**那一行必须被抓住（★ 否则门禁是摆设）。"""
    hits = _hits(OLD_SOURCE)
    assert hits, "★ 修复前的 `get_com_member(model, \"GetModelViewManager\")` **没被抓住**"
    assert hits[0][2] == "GetModelViewManager", hits


def test_negative_the_fixed_line_is_not_caught() -> None:
    """★ 修好之后 + 四个像但合法的形态 ⇒ 一处都不许命中（★ 门禁不许天天误伤）。"""
    hits = _hits(NEW_SOURCE)
    assert not hits, "★ 误伤：%r" % (hits,)


def test_current_tree_is_clean() -> None:
    """★ 全仓现状（★ 门禁的实际输出）—— ★ 扫到的每一处都是真命中，不是样例。"""
    hits, seen = gate.scan()
    assert seen > 300, "★ 只扫了 %d 个文件 ⇒ 扫描根可能挂错了" % seen
    assert not hits, "★ 全仓命中 %d 处：%r" % (len(hits), hits[:3])


# ── 直接运行 ──────────────────────────────────────────────────────────────

def _main() -> int:
    fails = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  [ok] %s" % name)
            except AssertionError as exc:
                fails.append(name)
                print("  [FAIL] %s: %s" % (name, exc))
    print("★ %d 条失败" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_main())
