"""★ 弹窗处置三级判据（`auto` / `needs_llm` / `forbidden`）的契约测试。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_sw_guard_dialog_tiers.py
# 定位:   ★ 2026-10-02（轮 381）**用户点破"处置层写死很危险"** ⇒ 把三级判据钉成测试：
#   ★ 凡是"点哪个按钮要看语义"的弹窗，★ **一律不许自动点**。
# 官方依据: 不适用（★ 用真机观察到的按钮组合当样本：`确定` · `是|否|确定` · `暂停|取消`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 为什么这几条必须有测试（★ 都是真机撞出来的）：
# ```
# ① `不可恢复` 曾被判成 `auto` —— 危险词表里只有"不可逆" ⇒ ★ **"删除后不可恢复"会被自动点掉**（不可逆后果）。
# ② `是否继续？` 曾被判成 `auto` —— 只要唯一按钮是"确定"就算安全，★ 而**"在提问"意味着至少两条分支**。
# ③ `暂停|取消`（求解进度窗）若判 `auto` ⇒ ★ **点掉 = 中断一个正在跑的正常任务**。
# ```
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))


def _classify(controls):
    import sw_guard as G

    return G.classify_dialog({"controls": controls})


def _b(*texts):
    return [{"class": "Button", "text": t} for t in texts]


def _s(text):
    return [{"class": "Static", "text": text}]


def test_plain_confirm_is_auto():
    """★ 唯一一个语义明确的确认按钮 ⇒ **可自动点**（★ 那是"确定"这条常见路径）。"""
    for btn in ("确定", "OK", "关闭", "Close"):
        v = _classify(_b(btn) + _s("零件41-DSH-142 : 失败"))
        assert v["mode"] == "auto", (btn, v)


def test_destructive_text_is_forbidden_even_with_single_ok():
    """★★ **负例**：只有一个"确定"，而文本说了破坏性后果 ⇒ **绝不自动点**。

    ★ 依据：`不可恢复` 曾漏网（表里只有"不可逆"）⇒ 真机后果**不可逆**。
    """
    for text in ("删除后不可恢复", "将覆盖现有文件", "此操作无法撤销", "permanently delete"):
        v = _classify(_b("确定") + _s(text))
        assert v["mode"] == "forbidden", (text, v)


def test_question_dialog_is_forbidden():
    """★★ **负例**：弹窗在**提问**（问号 / "是否" / "吗"）⇒ **绝不自动点** —— 至少两条分支。

    ★ 依据：`是否继续？` 曾被判成 `auto`（★ 因为只看按钮不问文本）。
    """
    for text in ("是否继续？", "真的要执行吗", "Are you sure?"):
        v = _classify(_b("确定") + _s(text))
        assert v["mode"] == "forbidden", (text, v)


def test_progress_window_is_its_own_tier():
    """★★★ **求解进度窗 ⇒ 自成一档 `progress`**（★ 2026-10-04 改，★ 真机证据在此）。

    ★ 旧契约（本测试原来写的）：`暂停|取消` ⇒ `needs_llm` —— ★ 那**保住了"不点"**，
      ★★ 但**顺带把调用也中止了**（`run_guarded` 对任何 `needs_llm` ⇒ `taskkill` + 早返回）✓
    ★★★ 真机代价（2026-10-04）：★ 一次**已经成功**的求解（`results_present=True · plot_count=4`）
      被标成 `aborted_for_llm: true`、`ok: false` —— ★★ 而那正是**事实 297 明令禁止的
      "中断一个正在跑的正常任务"** ✓
    ⇒ ★ 新契约：`progress` 档 ⇒ ★ **既不点、也不中止**（★ 只记证）——
      ★ 而"**不点**"这条不变量**原样保住**（★ 见下面 `test_needs_llm_or_forbidden_never_auto_dismiss`）✓
    """
    v = _classify(_b("暂停", "取消", "更多>>") + _s("当前任务: 建立刚度矩阵"))
    assert v["mode"] == "progress", v
    assert v["mode"] != "auto", v


def test_cancel_only_is_needs_llm():
    """★ 唯一按钮是"取消" ⇒ `needs_llm`（★ "取消"不是"确认"）。

    ⚠ ★ **注意与上一档的区别**：★ 这里是**没有运行态读数**的框（`Static` 只有 "abc"）
      ⇒ ★ 它**不是**"正在跑的任务"，而是一个**等回答的框** ⇒ `needs_llm` ✓
    """
    v = _classify(_b("取消") + _s("abc"))
    assert v["mode"] == "needs_llm", v


def test_empty_controls_is_needs_llm():
    """★ 读不到控件 ⇒ `needs_llm`（★ **不做**"没有按钮就当安全"的假设）。"""
    assert _classify([])["mode"] == "needs_llm"


def test_needs_llm_or_forbidden_never_auto_dismiss():
    """★★ **本组的核心不变量**：`needs_llm` / `forbidden` / **`progress`** ⇒ **一律不许自动点**。

    ★ 2026-10-04：★ `progress` 档加进来之后，**这条不变量必须一起覆盖它** ——
      ★★ 否则"新增一档"就成了"新增一个能被点的地方"✓
    """
    risky = [
        _b("是", "否") + _s("是否替换现有文件？"),
        _b("删除") + _s("不可恢复"),
        _b("暂停", "取消") + _s("当前任务"),
        _b("上一步", "下一步") + _s("向导"),
        [],
    ]
    for ctls in risky:
        v = _classify(ctls)
        assert v["mode"] in ("needs_llm", "forbidden", "progress"), (ctls, v)
        assert v["mode"] != "auto", (ctls, v)
