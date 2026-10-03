"""★ 测「断言不许钉死**取决于环境**的值」—— ★ 修掉"单独绿、全量红"（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tests/test_sw_sketch_edit_contract.py`（★ 改的就是它）· `output/_full_baseline_failures.txt`
# 定位:   ★ 轮 119 跑全量：★ **3 failed / 1741 passed**（★ 真基线 **25 → 3**）⇒
#   ★★ **其中唯一一条是我的**：★ `test_sw_sketch_edit_contract
#     ::test_mirror_calls_the_official_zero_arg_member` ✓
#   ★★★ **症状**：★ **单独跑 16 passed** · ★★ **与前一个文件一起跑 ⇒ 1 failed** ⇒
#     **那正是"单独绿、全量红"** ✓
#   ★★★★ **真因（★ 两次对照，可核）**：
#     · ★ **单跑**：★ `ok = None` · ★ `segments_before/after = None`（★ 取不到计数）✓
#     · ★ **与 `tests/test_extended_modules_contract.py` 一起跑**：★ `ok = False` ·
#       ★ `segments_before/after = **0**`（★ **拿到了数字 0**）✓
#     ★★ **⇒ 那个文件往 `sys.modules` 里装了 `sw_connect` 的**桩**（★ 它的 `_load` 里有
#       `sys.modules.setdefault("sw_connect", module)`、★ 桩的
#       `safe_get_com_member = lambda obj, name, *a, **k: None`）⇒
#       ★★★ **⇒ 计数的**形态**跟着变 ⇒ `ok` 在 `None` 与 `False` 之间变** ✓
#   ★★★★★ **⇒ 我轮 118 写的 `assert r["ok"] is None` 把一个**取决于环境的值钉死了**** ✗
#   ★★★★★★ **⇒ 修法**：★ **断言只查**语义**、★ 不查那个值本身** ——
#     ★ 语义是「★ **取不到计数时**不报成功**」⇒ ★ 写成 **`is not True`** ⇒
#     ★★ **两种环境下都成立**（★ `None` 与 `False` 都不是 `True`）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
F = REPO / "tests" / "test_sw_sketch_edit_contract.py"


def test_mirror_asserts_semantics_not_a_environment_value() -> None:
    """★★★ 核心断言：★ **`sketch_mirror` 那一条**的 `ok` 断言是 `is not True` ✓

    ★★ **为什么**：★ `sketch_mirror` 的 `ok` 的**具体值**取决于 `sw_connect` 是真是桩
      （★ 实测：★ 单跑 `None` · ★ 桩环境 `False`）⇒ ★★★ **钉死它就是钉死环境** ✓
    ★★★★ **⚠ 而判据必须**限定到那一个函数**** —— ★ 本测试第一版查整个文件，
      ★★ **于是误伤了 `convert_entities` 那条 `is False`** ⇒
      ★★★ **而实测证明那条**没问题**（★ `ok` 两种环境下**都是 `False`**）** ✓
      ⇒ ★ **⇒ 判据要按"那个**值**变不变"来定、★ 不能按"两种写法像不像"** ✓
      （★ 与**事实 51**「分析范围要贴合组织单元」同族）✓
    """
    t = F.read_text(encoding="utf-8", errors="replace")
    #: ★★ 只取 `sketch_mirror` 那个测试函数的源码（★ 用 `ast` 的 end_lineno）✓
    import ast
    tree = ast.parse(t)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef)
              and n.name == "test_mirror_calls_the_official_zero_arg_member")
    lines = t.splitlines()
    body = "\n".join(lines[fn.lineno - 1:getattr(fn, "end_lineno", fn.lineno)])
    assert 'r["ok"] is not True' in body, (
        "★ `sketch_mirror` 的 `ok` 断言退回了钉死具体值 ⇒ 会再次「单独绿、全量红」")
    #: ★★ 而**钉死值**那个形态**不许**出现在**这个函数**里 ✓
    code = "\n".join(l for l in body.splitlines() if not l.strip().startswith("#"))
    assert not re.search(r'r\["ok"\] is (?:None|False)', code), (
        "★ 又把 `sketch_mirror` 的 `ok` 钉死成某个具体值了 ⇒ 那个值取决于环境")
    #: ★★★ 而 `convert_entities` 那条**可以**留 `is False` —— ★ 实测它**两种环境都是 False** ✓
    assert 'r["ok"] is False' in t, (
        "★ `convert_entities` 那条被误改了 —— ★ 实测它的 `ok` 两种环境下都是 `False`")


def test_the_three_state_semantics_is_still_recorded() -> None:
    """★★★ 核心断言：★ 「不报成功」那句**记录**还在（★ 判据来源不许被删）✓"""
    t = F.read_text(encoding="utf-8", errors="replace")
    assert "不报成功" in t, "★ 判据来源那句被删了"


def test_negative_case_both_orders_pass() -> None:
    """★★★★ **负例 · 两种顺序都要绿**（★ 用 `pytest` 真的跑、★ 且**两个顺序都跑**）✓

    ★★ **为什么两个顺序**：★ 顺序依赖**只在一个方向现形** ⇒
      ★★★ **只跑一个顺序等于没测** ✓
    """
    import subprocess
    import sys
    for pair in (["tests/test_extended_modules_contract.py",
                  "tests/test_sw_sketch_edit_contract.py"],
                 ["tests/test_sw_sketch_edit_contract.py",
                  "tests/test_extended_modules_contract.py"]):
        p = subprocess.run([sys.executable, "-m", "pytest", *pair, "-q"],
                           cwd=str(REPO), capture_output=True)
        out = (p.stdout or b"").decode("utf-8", "replace") + \
              (p.stderr or b"").decode("utf-8", "replace")
        assert p.returncode == 0, "★ 顺序 %r 下红了：%s" % (pair[0], out[-400:])
        assert " failed" not in out, "★ 顺序 %r 下有 failed：%s" % (pair[0], out[-300:])


def test_negative_case_the_polluter_is_named_in_the_record() -> None:
    """★★★ **负例 · 污染源要点名**：★ 记录里写明是哪个文件、以及**为什么** ✓

    ★★ **为什么**：★ 下一个人再遇到"单独绿、全量红"时，
      ★★★ **要能一眼看到那个 `sys.modules` 桩** ⇒ **不必重查一遍** ✓
    """
    t = F.read_text(encoding="utf-8", errors="replace")
    for need in ("test_extended_modules_contract.py", "sys.modules",
                 "safe_get_com_member"):
        assert need in t, "★ 记录里少了 `%s`（★ 污染源要说清）" % need
