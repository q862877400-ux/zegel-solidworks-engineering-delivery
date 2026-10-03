"""★ 测：★ `tests/conftest.py` **自己把三个目录加进 `sys.path`**（★ 一处修、处处好 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tests/conftest.py`（★ **改的就是它**）· `output/_audit_test_syspath.py`（★ 只报不动）
# 定位:   ★ **起因（★ 可核）**：★ 轮 110 我改了 `scripts/sw_drawing_view.py` 之后**单跑**
#   `tests/test_sw_drawing_view_contract.py` ⇒ ★★ **12 failed** ⇒ 看着像我改坏了 ✓
#   ★★★ **真因**：★ 那个文件 L83 `import sw_connect` ⇒
#     ★ **而它自己没把 `scripts/` 加进 `sys.path`** ⇒
#     ★★★★ **⇒ 那是**预先存在的**测试顺序依赖****（★ 与**事实 57**同族：
#       ★ "一直是绿的、只是环境恰好满足" —— ★ 同进程里别的测试文件加过 path）✓
#   ★★★★★ **静态扫的数**（★ `output/_audit_test_syspath.py`）：
#     ★ 测试文件 **225 个** ⇒ ★★ **16 个**「导入了 `scripts/` 模块却没自己加 path」·
#     ★★ **对照 94 个**自己加了 ⇒ ★★★ **⇒ 那 16 个是**少数派**** ✓
#   ★★★★★★ **修法**：★ **`tests/conftest.py` 是 pytest 的标准入口**、
#     ★ 它在**每个测试文件被导入之前**执行 ⇒ ★★ **在那儿加一次、★ 16 个都好** ✓
#     ★★★ **⚠ 而本文件**早就有 `import sys`、★ **却一次都没用它** ——
#       ★★ **那正是"准备好加、★ 而没加"的痕迹** ✓
#   ★★★★ **修后读数**：★ **16 个文件逐个单跑** ⇒ **14 个全绿**、
#     ★ **2 个各 1 条**已知存量失败**（★ `test_mold_undercut_detect_*` · ★ `test_sketch_spline_*`）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONFTEST = REPO / "tests" / "conftest.py"
TESTS = REPO / "tests"


def test_conftest_adds_the_three_dirs() -> None:
    """★★★ 核心断言：★ conftest **确实**把三个目录加进 `sys.path` ✓"""
    t = CONFTEST.read_text(encoding="utf-8", errors="replace")
    assert "sys.path.insert" in t, "★ conftest 没加 `sys.path`"
    for d in ('"scripts"', '"mcp-server"'):
        assert d in t, "★ conftest 没加 `%s` 目录" % d
    #: ★★ 而它**必须**用上那个 `sys`（★ 否则就是"写了没用"）✓
    assert re.search(r"sys\.path\.insert\(0, str\(", t), "★ 插入写法变了"


def test_conftest_runs_before_any_test_module() -> None:
    """★★★ 核心断言：★ 那段 `sys.path` 代码在**模块层**（★ 不是 fixture 里）✓

    ★★ **为什么**：★ pytest 收集期就要 `import` 各测试文件 ⇒
      ★★★ **若放在 fixture 里就太晚了**（★ 那时 import 已经失败）✓
    """
    t = CONFTEST.read_text(encoding="utf-8", errors="replace")
    i = t.find("sys.path.insert")
    assert i != -1, "★ 找不到那段"
    #: ★ 它前面**不许**出现 `def ` 之后的缩进块（★ 即必须在模块层、顶格）✓
    for line in t[:i].splitlines()[::-1]:
        if "def " in line or "class " in line:
            raise AssertionError("★ `sys.path.insert` 被放在函数/类里了：%r" % line)
        if line.startswith("sys.path"):
            break


def test_negative_case_the_sixteen_files_are_still_there() -> None:
    """★★★★ **负例 · 那 16 个文件还在**（★ 若有人"顺手"把它们删了，判据就失效）✓

    ★★ 判据：★ 那些文件**必须仍然存在** ⇒
      ★★★ **因为修法是"在 conftest 里加一次"、★ 而**不是**去改那 16 个文件** ✓
    """
    names = ["test_sw_drawing_view_contract.py", "test_sw_mold_contract.py",
             "test_sw_sketch_contract.py", "test_sw_simulation_loads_contract.py",
             "test_sw_simulation_results_contract.py", "test_sw_simulation_study_contract.py",
             "test_sw_simulation_study_options_contract.py", "test_sw_routing_contract.py",
             "test_sw_pdm_contract.py", "test_sw_featureworks_contract.py",
             "test_sw_pattern_contract.py", "test_sw_selection_contract.py",
             "test_sw_view_contract.py", "test_sw_assembly_doc_contract.py",
             "test_official_names_only_contract.py", "test_union_gap_regression.py"]
    missing = [n for n in names if not (TESTS / n).is_file()]
    assert not missing, "★ 这些文件不见了：%r" % missing


def test_negative_case_conftest_still_guards_input() -> None:
    """★★★ **负例 · 原来的守卫不能丢**：★ conftest **仍然**拦真实键鼠 ✓

    ★★ **为什么**：★ 本文件**存在的原因**是那次「测试真的在用户桌面按键」的事故 ⇒
      ★★★ **我加 `sys.path` 时绝不能把那个 `autouse` 守卫弄丢** ✓
    """
    t = CONFTEST.read_text(encoding="utf-8", errors="replace")
    for need in ("autouse=True", "keybd_event", "mouse_event", "SetCursorPos",
                 "input_injection_log"):
        assert need in t, "★ conftest 丢了 `%s` ⇒ 那次事故的守卫被削弱了" % need
