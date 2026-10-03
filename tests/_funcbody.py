"""★ 测试共用帮手：★ **按 `ast` 取一个函数的源码**（★ 事实 51：范围要贴合组织单元）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/_funcbody.py（★ 新）
# 定位:   ★ 轮 113 跑全量基线 ⇒ ★★ **25 failed / 1711 passed** ⇒
#   ★★★ **其中唯一一条是我引入的**：★ `test_csys_params_capability.py
#     ::test_code_does_not_call_the_no_page_members` ✓
#   ★★★★ **真因**：★ 我用 `src[i:].split('\"\"\"')[-1]` 取"函数体" ⇒
#     ★ **那实际是"从那个 `def` 到**文件末尾**"** ⇒ ★★ 而那个文件的末尾**后来**多了
#       `base_flange_params`（★ 轮 109 加的）⇒ ★★★ **判据范围跑出了组织单元** ✓
#     ⇒ ★★★★ **⇒ 那正是**事实 51**：★ **分析范围必须贴合代码的**组织单元**** ✓
#   ★★★★★ **影响面（★ 静态扫的）**：★ `output/_audit_test_funcbody_slicing.py` ⇒
#     ★ **3 个测试文件**用了那种脆取法（★ **全是我在轮 102/107/109 写的**）·
#     ★★ **对照 38 个**用 `ast`（★ 那才是稳的）✓
#   ★★★★★★ **⇒ 本帮手把那 3 处的取法统一成 `ast`** —— ★ 写法**抄那 38 个** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast


def func_source(src: str, name: str) -> str:
    """★ 取 `src` 里**名为 `name` 的那个函数**的源码（★ **按 `ast` 的起止行**）✓

    ★★★★ **为什么不用字符串切片**（★ 本会话第 N 次踩这个坑）：
      ★ `src[i:].split('\"\"\"')[-1]` **看着像"取函数体"**、
      ★★ **而它实际是"从那个 `def` 到**文件末尾**"** ⇒
      ★★★ **一旦有人在文件末尾**再加一个函数**，范围就**悄悄变宽**、
        判据会**误报**（★ 本轮就是这样红的）✓
      ⚠ **它静默变宽、★ 不报错** —— ★ 那正是最坏的一类。
    ★★★★★ **⇒ 本函数用 `ast` 的 `lineno` / `end_lineno`**（★ Python 3.8+ 有 `end_lineno`）⇒
      ★ **范围**恰好那一个函数**** ✓
    """
    tree = ast.parse(src)
    lines = src.splitlines()
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            end = getattr(n, "end_lineno", None)
            if end is None:                                    # pragma: no cover
                #: ★ 兜底：★ 没 `end_lineno` 就算到"下一个顶层 def 之前"
                end = len(lines)
            return "\n".join(lines[n.lineno - 1:end])
    raise AssertionError("★ `%s` 里没有函数 `%s`" % ("<src>", name))
