"""★ 测：★ 测试**不许用「切片到文件末尾」取函数体**（★ 事实 51 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tests/_funcbody.py`（★ 新帮手）· `output/_audit_test_funcbody_slicing.py`（★ 只报不动）
# 定位:   ★ **起因（★ 可核）**：★ 轮 113 跑全量基线（★ **25 failed / 1711 passed**）⇒
#   ★★ **其中唯一一条是我引入的**：★ `test_csys_params_capability.py
#     ::test_code_does_not_call_the_no_page_members` ✓
#   ★★★ **真因**：★ 我（★ 轮 107）用 `src[i:].split('\"\"\"')[-1]` 取"函数体" ⇒
#     ★ **那实际是"从那个 `def` 到**文件末尾**"** ⇒ ★★ 而那个文件的末尾**后来**多了
#       `base_flange_params`（★ 轮 109 加的）⇒ ★★★ **判据范围跑出了组织单元** ✓
#     ⇒ ★★★★ **⇒ 那正是**事实 51**：★ **分析范围必须贴合代码的**组织单元**** ✓
#   ★★★★★ **静态扫的影响面**（★ `output/_audit_test_funcbody_slicing.py`）：
#     ★ **3 个测试文件**用了那种脆取法（★ `test_csys_/fillet_/base_flange_params_capability.py`）·
#     ★★ **对照 38 个**用 `ast`（★ 那才是稳的）⇒ ★★★ **⇒ 改那 3 处、★ 抄那 38 个** ✓
#   ★★★★★★ **⚠ 修的过程里**又暴露一层****（★ 值记）：
#     ★ 改成 `func_source` 之后，`test_fillet_params_capability` **红了** ⇒
#     ★★ **真因**：★ 它断言「函数体里**不许出现** `GetRadius` / `GetDistance` /
#       `GetConicRhoOrRadius`」⇒ ★★★ **而那三个名字**就在**注释**里**
#       （★ 那句「★ 本函数**不碰**它们」）⇒ ★★ **"注释里提到"正是**记录**、★ 不是**调用**** ✓
#     ★★★★ **⇒ 判据改成查**调用形态** `get_com_member(fd, "<name>"`** ——
#       ★ 与 `test_csys_params_capability.py` 那条**同一个修法** ✓
#   ★★★★★ **修后读数**：★ 那 8 个能力测试**全部 32 passed** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402
from _codescan import code_only  # noqa: E402


def test_the_helper_takes_exactly_one_function() -> None:
    """★★★ 核心断言：★ `func_source` 取的范围**恰好那一个函数** ✓

    ★★ **判据**：★ 对 `sw_feature_readback.py` 的两个相邻函数分别取 ⇒
      ★★ **各自**都不含对方的名字** ✓
    """
    src = (REPO / "scripts" / "sw_feature_readback.py").read_text(encoding="utf-8",
                                                                  errors="replace")
    a = func_source(src, "csys_params")
    b = func_source(src, "base_flange_params")
    assert "base_flange_params" not in a, "★ `csys_params` 的范围里混进了下一个函数"
    assert "csys_params" not in b, "★ `base_flange_params` 的范围里混进了上一个函数"
    #: ★★ 而**各自的内容**要在 ✓
    assert "页不在" in a, "★ `csys_params` 里那句记录不见了"
    assert "不读" in b, "★ `base_flange_params` 里那句记录不见了"


def test_no_test_slices_to_end_of_file_for_a_function_body() -> None:
    """★★★ 核心断言：★ **没有任何测试**再用「切片到文件末尾」取函数体 ✓

    ★★★★ **⚠ 要先用 `code_only` 剥掉注释与字符串**（★ 本会话第 N 次）：
      ★ 我第一版只看「行首是不是 `#`」⇒ ★★ **而那句判据的说明在**docstring** 里** ⇒
      ★★★ **它把自己的说明当成了"真用"**（★ 假阳性）✓
      ⇒ ★★★★ **⇒ 用 `tests/_codescan.py::code_only`**（★ `tokenize` 剥注释**与**字符串）✓
    """
    bad = []
    for f in sorted(TESTS.glob("test_*.py")):
        code = code_only(f.read_text(encoding="utf-8", errors="replace"))
        for pat in (r"""src\[i:\]""", r"""t\[i:\]""", r"""\.split\(['"]{3}\)\[-1\]"""):
            for m in re.finditer(pat, code):
                bad.append((f.name, code[:m.start()].count("\n") + 1, pat))
    assert not bad, "★ 还有人用「切片到文件末尾」取函数体：%r" % bad[:4]


def test_negative_case_the_three_files_now_use_the_helper() -> None:
    """★★★★ **负例 · 那三处要用上帮手**：★ `func_source` 在**那 3 个文件**里出现 ✓"""
    for fn, target in (("test_csys_params_capability.py", "csys_params"),
                       ("test_fillet_params_capability.py", "fillet_params"),
                       ("test_base_flange_params_capability.py", "base_flange_params")):
        t = (TESTS / fn).read_text(encoding="utf-8", errors="replace")
        assert "func_source" in t, "★ `%s` 还在用切片取法" % fn
        assert 'func_source(src, "%s")' % target in t, (
            "★ `%s` 没按名字取 `%s`" % (fn, target))


def test_negative_case_the_call_shape_criterion_is_kept() -> None:
    """★★★★ **负例 · 判据要用**调用形态****：★ `fillet` 那条不许回到"查名字出现" ✓

    ★★ **为什么**：★ 那三个成员名**就在注释里**（★ 说明"不碰它们"）⇒
      ★★★ **若判据查"名字出现" ⇒ 会把**记录**当成**调用**、★ 从而**永远红**** ✓
      （★ 而**更糟**的是：★ 有人可能为了让它绿而**删掉那句记录**）✓
    """
    t = (TESTS / "test_fillet_params_capability.py").read_text(encoding="utf-8",
                                                               errors="replace")
    assert 'get_com_member(fd, "%s"' in t, (
        "★ 判据退回成「查名字出现」了 ⇒ 会把注释里的记录当成调用")
    #: ★★ 而那句"不碰"的记录**必须还在**（★ 不许为了绿而删）✓
    assert '"不碰" in body' in t, "★ 那条「记录必须还在」的断言被删了"
