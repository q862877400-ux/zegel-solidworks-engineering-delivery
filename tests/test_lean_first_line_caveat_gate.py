"""★ 首句自证门禁的契约测试 + **双侧负例**（该报的报、不该报的不报）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_lean_first_line_caveat.py`（被测门禁）
#         `specs/215-tool-surface-decisions/spec.md` §二-④（判据与实测数据）
# 定位:   ★ 事实 62（**负例是门禁有效的唯一证明**）在这里落地 ——
#         ★ 本门禁的判据是**从三组实测里选的**（宽标记 12 命中 / `建不出` 7 命中且 0 真阳性 /
#         本组 3 命中且 3 真阳性）⇒ ★ **"选了哪一组"这件事必须被负例钉住**，
#         否则后来人把标记集放宽一格，门禁就会开始误伤 ✓
# 官方依据: 不适用（纯静态：读 `ToolSpec.doc`，不连 SolidWorks）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_lean_first_line_caveat.py"


def _load():
    spec = importlib.util.spec_from_file_location("lean_first_line_gate_under_test", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lean_first_line_gate_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


G = _load()


# ── ① lean 投影口径（★ 门禁与插件必须数同一件事）────────────────────────
def test_lean_first_matches_the_plugin_window():
    """★ 口径：**第一句** + 截断到 **120** 字（★ 与 `@local/dsh-lean-mode` 的 `firstLine()` 一致）。"""
    assert G.LEAN_CHARS == 120
    assert G.lean_first("第一句。第二句。") == "第一句"
    assert G.lean_first("换行\n后面的都不算") == "换行"
    #: ★ 边界：恰好 120 字不截断、121 字截成 120 ✓
    assert len(G.lean_first("A" * 130)) == 120
    assert G.lean_first("A" * 100) == "A" * 100


def test_ascii_period_is_not_a_sentence_break():
    """★★ **本次实测钉住的一条口径**：lean 只按 **`。` 与换行**断句 —— **ASCII 句号不算** ✓

    ⚠ 我写本文件的第一版正例时正好栽在这上面：夹具写成
      `"Create a thing. Some detail. Yet another line. ★ 仍不可用：…"`，
      而 ★ **整串其实是一句**（ASCII `.` 不断句）⇒ 标记**就在**第一句里 ⇒ 门禁（正确地）没报 ✗
    ⇒ ★ 对**英文**文档，真正的失败条件是「标记落在**前 120 字之外**」；
      ★ 对中文文档，才是「标记不在第一个 `。` 之前」✓
    ★★ 这条不许被"修夹具"绕过去 —— ★ 它是本门禁的**输入口径**，写错就会把判据测歪 ✓
    """
    long_prose = "Create a native thing on a SELECTED face. " * 6      #: ★ > 120 字
    assert len(long_prose) > 120
    assert "." in long_prose and G.lean_first(long_prose) != long_prose.split(".")[0], (
        "★ 若这条断言红了 ⇒ 说明 lean 开始把 ASCII 句号当分隔符了，本门禁的口径要跟着改")
    assert G.lean_first("很长" + "。" + "第一句到这里为止") == "很长"


# ── ② 正例：该报的必须报 ────────────────────────────────────────────────
def test_unavailable_late_in_doc_is_reported():
    """★★ 正例：`仍不可用` 落在 120 字窗口**之外** ⇒ ★ **必须报**（模型看不到这个结论）。"""
    doc = "Create a thing on a selected face. " * 5 + "★ **仍不可用**：指针族调不动。"
    assert len(doc) > G.LEAN_CHARS
    assert G.judge("solidworks_x", doc), "标记在窗口外 ⇒ 必须命中"


def test_not_usable_late_in_doc_is_reported():
    doc = "Create a native draft on a SELECTED face. " * 5 + "*** NOT USABLE ON THE TEST MACHINE ***"
    assert len(doc) > G.LEAN_CHARS
    assert G.judge("solidworks_x", doc), "NOT USABLE 在窗口外 ⇒ 必须命中"


def test_pipeline_step_without_internal_mark_is_reported():
    """★★ 正例：承认自己是 `generate_macro_with_guard` 的一步、却**没自证内部件** ⇒ 必须报。"""
    doc = ("Build the prompt that asks a model to write SolidWorks VBA for `user_request`. "
           "★ Pure string function; it is one step of `sw_macro_guard.generate_macro_with_guard`.")
    problems = G.judge("solidworks_x", doc)
    assert problems, "管线内部件没自证身份 ⇒ 必须命中"


# ── ③ 反例：不该报的一条都不许报（★ 这三条正是"宽标记"会误伤的那几类）──────
def test_first_sentence_already_says_unavailable_is_clean():
    """★ 反例：结论**已经在首句**里 ⇒ 绿（★ 这就是改完之后的形态）。"""
    assert G.judge("solidworks_x", "★ **本机仍不可用**：指针族。Create a thing. 后面随便。") == []


def test_loose_unavailable_word_is_not_a_subject():
    """★★ 反例（★ 最要紧的一条）：说**别的路**不可用 ⇒ ★ **不是本门禁的对象**。

    ★ 依据：实测「`不可用`（宽）」命中 **12** 条而真阳性只有 **3** ⇒
      ★ 那 9 条正是这个形态（"该族到不了，本工具只走直入法"之类）✓
    """
    doc = ("★ **本工具可用**：它只走直入法，★ \u4e0d\u78b0\u6307\u9488\u65cf\u3002"
           "官方那族在 pywin32 上不可用 —— ★ 那是**别的路**，与本工具无关。")
    assert G.judge("solidworks_x", doc) == []


def test_historical_build_failure_note_is_not_a_subject():
    """★★ 反例：`建不出` 的**历史叙述** ⇒ 不是本门禁的对象（★ 实测 7 命中 / 0 真阳性）。"""
    doc = "Create a hole table. 早期版本建不出孔表，现已改走另一条路并建成。"
    assert G.judge("solidworks_x", doc) == []


def test_pipeline_step_with_internal_mark_is_clean():
    """★ 反例：管线内部件**已自证**（★ 这就是改完之后的形态）⇒ 绿。"""
    doc = ("★ **内部件（模型不必直接调用）**：本工具是 "
           "`sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Build the prompt …")
    assert G.judge("solidworks_x", doc) == []


# ── ④ 真仓库：集成判据（★ 改完之后必须是绿的）──────────────────────────
def test_current_repo_passes():
    """★ 集成：真仓库上跑判据 ⇒ **0 命中**（★ 规格 215 的 C1 / C2 由这条守着）。"""
    rows, checked, subject = G.scan()
    assert checked >= 300, "只看到 %d 条 spec ⇒ 注册表没加载全" % checked
    assert subject >= 5, "受约束的条目骤减（现 %d）⇒ 判据可能失效了" % subject
    assert rows == [], "★ 仍有结论落在 lean 窗口外：%s" % [r["name"] for r in rows]


def test_gate_exits_zero_on_the_real_repo():
    """★ 判据模式的退出码（★ 接进 `release_check` 靠的就是它）。"""
    assert G.main([]) == 0
