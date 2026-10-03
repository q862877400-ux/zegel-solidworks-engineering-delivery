"""★ 守「阶段 3 收敛判据的现状」这份文档（★ 含**重跑核对** · 轮 133）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `docs/phase3-convergence-status.md` +
#         `tools/build_capability_matrix.py`（★ **阈值写死在那里**）
# 文件:   tests/test_phase3_convergence_status.py（★ 新）
# 定位:   ★★★★★★ 2026-10-04（轮 133）**阶段 3 的三条判据实测**：
#     ★ **① 无处可放率 = 7.85%**（★ 阈值 ≤20% ⇒ **好**）·
#     ★★ **② 空格率 = 19.33%**（★ 阈值 ≤60% ⇒ **好**）·
#     ★★★ **③ 双源一致率 = 44.42%**（★ 阈值 ≥30% ⇒ **可接受**）✓
#   ★★★★ **⇒ 三条全部满足任务书阈值** ⇒ ★ **本测试做两件**：
#     ★ **① 核那三条的阈值**写死在源码里**（★ 不许被改松） ·
#     ★★ **② 核那份文档记下了**旧值与新值**、★ 且**归因正确****（★ ① ② 不是这轮做的）✓
#   ★★★★★ **⚠ 本测试**不重跑矩阵****（★ 那要几十秒、★ 而门禁已在收尾链里）⇒
#     ★ **只核阈值与文档** ⇒ ★ **便宜的守卫、★ 挡的是"偷偷放水"** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MATRIX = REPO / "tools" / "build_capability_matrix.py"
DOC = REPO / "docs" / "phase3-convergence-status.md"


def test_the_three_thresholds_are_still_frozen() -> None:
    """★★★★★ 核心断言：★ 三条阈值**仍然写死**、★ **没有被改松** ✓

    ★★ **为什么这条最重要**：★ 任务书逐字「★ **阈值写死在 `tools/build_capability_matrix.py`
      顶部，★ 不许改**」⇒ ★★★ **⇒ 一条"改松阈值就绿"的门禁等于没有门禁**（★ 事实 62）✓
    """
    t = MATRIX.read_text(encoding="utf-8", errors="replace")
    #: ★ ① 无处可放 ≤ 20% · ★ ② 空格 ≤ 60% · ★ ③ 双源 ≥ 30%
    assert "band(r1, 10, 20)" in t, "★ ① 的无处可放率阈值被改了"
    assert "band(r2, 60, 80)" in t, "★ ② 的空格率阈值被改了"
    assert "好≥50% · 可接受≥30%" in t, "★ ③ 的双源一致率阈值被改了"


def test_the_doc_records_both_old_and_new_values() -> None:
    """★★★ 核心断言：★ 文档同时记**任务书的旧值**与**实测的新值** ✓

    ★★ **为什么**：★ 只记新值 ⇒ ★ **看不出"改善发生在哪一轮"** ⇒
      ★★★ **⇒ 归因会错**（★ 而我这次差点把 ① ② 的改善算进自己头上）✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    for v in ("21.30", "56.19", "44.42"):
        assert v in t, "★ 旧值 `%s` 没记" % v
    for v in ("7.85", "19.33"):
        assert v in t, "★ 新值 `%s` 没记" % v


def test_the_attribution_credits_the_right_round() -> None:
    """★★★★ 核心断言：★ ① ② 的改善**归给轮 99**、★ **不是这一轮** ✓

    ★★ **为什么**：★ 这一轮只**读数**（★ 没改一行判据、★ 没补一个词）⇒
      ★★★ **⇒ 把改善算进自己头上就是**虚报****（★ 与"把没验过的写成能"同族）✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "轮 99" in t, "★ 没把 ① ② 的改善归给轮 99（★ 那是**补词**那批做的）"
    assert "不是这一轮" in t or "如实归因" in t, "★ 没写明归因"


def test_the_upper_bound_caveat_is_recorded() -> None:
    """★★★★ 核心断言：★ ③ 的「上界」这条**必须写清**（★ 免得当成真实值）✓

    ★★ **为什么**：★ 源码自带注逐字是「★ **按名字 token 匹配 ⇒ 上界**」⇒
      ★★★ **⇒ 44.42% 已是**乐观值**、★ 真实值只会更低** ⇒
      ★★ **⇒ 所以表述要写「按上界口径已过 30% 门槛」、★ 不许写「一致率 44%」** ✓
    """
    t = DOC.read_text(encoding="utf-8", errors="replace")
    assert "上界" in t, "★ 没记下「上界」那条限定"
    assert "乐观值" in t or "只会更低" in t, "★ 没写明它是乐观值"
