"""★ 判据 —— **弹窗分级器已上工具面**（★ 业主 2026-10-10 点破的那一件）。

★★★ **业主原话**：「★ **把这个检测的，也注册成一个MCP工具什么的，加入你的工具列表，
  不然每次都不知道主动用**」✓
★★ **实测缺口**（★ 本判据守的就是它）：★ 工具面**已有 9 个** `solidworks_gui_*`，
  ★★ **但没有任何一个**暴露 `classify_dialog` —— ★ 而它才是那套机制的**大脑**。
★★★ **真实代价（★ 我自己的实例）**：★ 本会话 EC09 求解时我只用了 `--scan`/`--clear`
  ⇒ ★ 看到弹窗却**没读分级理由** ⇒ ★★ 把「求解**失败**（未定义载荷）」误读成「求解**很慢**」
  ⇒ ★ **把根因判错了** ✗ —— ★ 本判据让那个错误**不能再悄悄发生** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_gui_dialog_classify.py`（★ 工具层包装）
#         `mcp-server/tool_specs_batch114.py`（★ ToolSpec 声明）
#         `tools/sw_guard.py`（★ `classify_dialog` —— ★ 分级逻辑的真源）
#         `tests/test_sw_guard_dialog_tiers.py`（★ 三级契约）
# 定位:   ★ 守卫「分级器必须在工具面上」+ ★ 四级结论的**端到端**行为。
# 官方依据: 不适用（本仓自研的 GUI 护栏）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰窗口）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
           str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def test_the_classifier_is_exposed_as_a_tool():
    """★★★★★ **分级器必须在工具面上**（★ 本判据的**全部意义**）。

    ★★ 依据（★ 业主逐字）：★「★ **加入你的工具列表，不然每次都不知道主动用**」——
      ★★ 若它只在 `tools/sw_guard.py` 里 ⇒ ★ 我**看不见** ⇒ ★ **就不会主动用** ✗
    """
    import register_capabilities as rc
    names = {s.name for s in rc.all_specs()}
    assert "solidworks_gui_classify_dialog" in names, (
        "★★★ 分级器**没在工具面上** ⇒ ★ 会重演「看不到就不会主动用」")


def test_all_nine_existing_gui_tools_are_still_there():
    """★★ 原有的 9 个 `solidworks_gui_*` **一个都不能少**（★ 本批是**加法**）。"""
    import register_capabilities as rc
    names = {s.name for s in rc.all_specs()}
    for n in ("solidworks_gui_assert_focus", "solidworks_gui_assert_no_modal",
              "solidworks_gui_close_modals", "solidworks_gui_ensure_focus",
              "solidworks_gui_find_modals", "solidworks_gui_focus_state",
              "solidworks_gui_get_foreground_window", "solidworks_gui_modal_report",
              "solidworks_gui_screen_png"):
        assert n in names, "★★ 原有的 %r 不见了" % n


def test_tool_spec_declares_no_injection_and_scalar_params():
    """★★★★ ToolSpec 必须：★ **不注入宿主** + ★ **参数都是标量**。

    ★★ 依据：★ MCP 边界**只过标量**（★ 无 `list` 型 `Param` 先例 ——
      `tool_specs_batch15.py:21-25`）⇒ ★ 本工具用 **`str` + 分隔符** ✓
    """
    import register_capabilities as rc
    s = {x.name: x for x in rc.all_specs()}["solidworks_gui_classify_dialog"]
    assert s.inject == "", "★★ 它**纯离线**（只读文本）⇒ 不该注入宿主对象"
    assert s.module == "sw_gui_dialog_classify", (
        "★★ module 应为工具层包装（★ 直接挂 `sw_guard` 会因多传 `title` 而 `TypeError`）")
    #: ⚠ 第一版写 `p.type` ⇒ `AttributeError: 'Param' object has no attribute 'type'`
    #:   （★ 本判据自己抓出来的）⇒ ★ 真字段是 **`annotation`** ✓
    names = {p.name for p in (s.params or [])}
    assert names == {"buttons", "texts", "title"}, (
        "★★ 参数集不对：%r" % sorted(names))


def test_end_to_end_auto_tier():
    """★★★★ **`auto` 档**：★ 只有一个确认按钮 ⇒ **可自动点**。

    ★★ 依据（★ 业主截图那个弹窗）：★ 按钮 `确定` · 正文「未定义载荷或规定的位移」——
      ★★ 它是**求解失败的通知** ⇒ ★ 点掉是安全的 ✓
    """
    from scripts.sw_gui_dialog_classify import classify_dialog
    r = classify_dialog(buttons="确定",
                        texts="未定义载荷或规定的位移|固定-刚性零件上的载荷将不处于活动状态。",
                        title="Simulation")
    assert r["mode"] == "auto", "★ 判成 %r" % r["mode"]
    assert r["should_auto_dismiss"] is True
    assert r["must_not_touch"] is False
    assert "close_modals" in r["next_tool"], "★ 没给出下一步该用哪个工具"


def test_end_to_end_forbidden_tier_on_danger_words():
    """★★★★★ **`forbidden` 档**：★ 正文含危险词 ⇒ **绝不自动点**。

    ★★ 依据（★ `classify_dialog` 的分级逐字）：★「文本含危险词（删除/覆盖/替换/丢失/
      不可逆/remove/overwrite/delete…）⇒ **绝不自动点**」✓
    """
    from scripts.sw_gui_dialog_classify import classify_dialog
    for texts in ("删除后不可恢复，是否继续？", "是否覆盖现有文件？", "数据将丢失"):
        r = classify_dialog(buttons="确定", texts=texts)
        assert r["mode"] == "forbidden", (
            "★★★ 危险词正文 %r 判成 %r ⇒ ★ 会被自动点掉" % (texts, r["mode"]))
        assert r["must_not_touch"] is True
        assert r["should_auto_dismiss"] is False


def test_end_to_end_progress_window_is_never_touched():
    """★★★★★ **`progress` 档**：★ 正常求解的进度窗 ⇒ **既不点、也不中止**。

    ★★ 依据（★ **事实 297** 逐字）：★ 点掉它 = ★ **中断一个正在跑的正常任务** ✗
      ★★ 而这**正是本会话 EC09 的真实场景**（★ 进度窗显示「建立刚度矩阵 · 已用时间 37m:46s」）✓
    """
    from scripts.sw_gui_dialog_classify import classify_dialog
    r = classify_dialog(buttons="暂停,取消,更多>>",
                        texts="当前任务: 建立刚度矩阵|已用时间:37m:46s|自由度:42,033|单元数:8,711",
                        title="Simulation")
    assert r["mode"] == "progress", (
        "★★★ 求解进度窗判成 %r ⇒ ★ 可能被点掉（★ 中断正常任务）" % r["mode"])
    assert r["must_not_touch"] is True
    assert r["should_auto_dismiss"] is False
    assert "不要点" in r["next_tool"], "★ 没给出「不要点」的明确指示"


def test_end_to_end_needs_llm_tier():
    """★★★ **`needs_llm` 档**：★ 多同权按钮 ⇒ **不点**，交人/LLM 判。"""
    from scripts.sw_gui_dialog_classify import classify_dialog
    r = classify_dialog(buttons="上一步,下一步", texts="请选择安装类型")
    assert r["mode"] == "needs_llm", "★ 判成 %r" % r["mode"]
    assert r["escalate_to_human_or_llm"] is True
    assert r["should_auto_dismiss"] is False


def test_the_wrapper_does_not_reimplement_the_grading():
    """★★★★ **包装**不重写**分级逻辑**（★ 铁律 1：★ 只缝合，不发明）。

    ★★ 判据：★ 包装**必须**调用 `sw_guard.classify_dialog` ——
      ★★ 否则就出现了**第二套**分级（★ 两处口径会漂移）✗
    """
    src = (ROOT / "scripts" / "sw_gui_dialog_classify.py").read_text(encoding="utf-8")
    assert "classify_dialog(" in src, "★★ 包装没调用分级器"
    assert "import sw_guard" in src, "★★ 包装没走 `sw_guard`（★ 那是分级逻辑的真源）"
    #: ⚠ 第二版仍**假红**：★ 我按 `ast.walk` 跳过 `Constant` —— 但**模块级 docstring**
    #:   是一个 `Expr(Constant)` ⇒ ★ `get_source_segment` 取的是**整段文本**（含三引号）✗
    #:   ★★ ⇒ 正解：★ **直接删掉所有字符串常量节点**（★ 本仓既有手法：
    #:      `check_env_pitfalls.strip_comments_and_strings()`）—— ★ 用**逐行剥**更稳 ✓
    import io
    import tokenize
    kept: list[str] = []
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.STRING, tokenize.COMMENT):
            continue
        kept.append(tok.string)
    code = " ".join(kept)
    for word in ("overwrite", "remove", "delete", "不可逆", "覆盖"):
        assert word not in code, (
            "★★★ 包装的**代码**里出现了危险词表（%r）⇒ ★ 那是**第二套分级逻辑**" % word)
