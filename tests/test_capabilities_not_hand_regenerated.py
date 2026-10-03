"""★ 给那张审计文档的**事故段**加一条守它的测试（★ 轮 132）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `docs/verified-evidence-audit.md` §六。
# 文件:   tests/test_capabilities_not_hand_regenerated.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 132）**事故的两条教训**（★ 都要有机器守）：
#     ★ **① `git checkout -- <file>` 的源是**索引**、★ 不是 HEAD** ⇒
#       ★★ 已 `git add` 过的坏内容**恢复不掉** ⇒ ★ **要用 `git checkout HEAD -- <file>`** ✓
#       ★★★ **⇒ 这条**没法做成门禁**（★ 它是一次性操作）⇒ ★ **写进文档 + 本测试核它写着** ✓
#     ★★ **② 不该手跑生成器** —— `tools/round_chain.ps1` **自己会跑**它们 ⇒
#       ★★★ **⇒ 这一条**可以**做成门禁**：★ **核 `capabilities.yaml` 是**合法 JSON**** ✓
#       ★★★★ （★ 而 `release_check` 已经会读它 ⇒ 它坏了就会红 —— ★ **所以机制本来就有**）✓
#   ★★★★★ **⇒ 本测试做两件**：★ ① 核 `capabilities.yaml` **当下**可解析 ·
#     ★★ ② 核文档里**两条教训都在**（★ 免得后人重踩）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CAP = REPO / "capabilities.yaml"
DOC = REPO / "docs" / "verified-evidence-audit.md"


def test_capabilities_manifest_is_parseable() -> None:
    """★★★ 核心断言：★ `capabilities.yaml` **当下**是合法 JSON ✓

    ★★ **为什么**：★ 本轮它被某个生成器写坏过（★ 串内引号规范化）⇒
      ★★★ **⇒ 而它是全仓最关键的一份清单**（★ `release_check` 读它、★ 能力等级都在里面）✓
    """
    data = json.loads(CAP.read_text(encoding="utf-8", errors="replace"))
    caps = data["capabilities"] if isinstance(data, dict) else data
    assert isinstance(caps, list) and len(caps) > 50, "★ 清单形状不对：%r" % type(caps)


def test_no_json_breaking_quote_normalization_in_manifest() -> None:
    """★★★★ 核心断言：★ 清单**字符串内部**不许出现能破坏 JSON 的形态 ✓

    ★★ **为什么**：★ 那次事故的形态是"在串内把 `"` 换成 `「」`" ⇒
      ★★★ **⇒ 那样改**不该由生成器做**（★ 本仓纪律：★ 引号在**写的时候**就该用 `「」`）✓
    ★★★★ **⚠ 本判据不查"有没有 `「」`"**（★ 那是**正常的**）—— ★ 它查**可解析性**，
      而可解析性由上一条覆盖 ⇒ ★ **本条只核"没有再出那种事故"的可观测痕迹**：
      ★ **`capabilities.yaml` 里不应有**未转义的裸 `"`**（★ 那必然让 JSON 解析失败）✓
    """
    raw = CAP.read_text(encoding="utf-8", errors="replace")
    #: ★ 有裸引号 ⇒ `json.loads` 早炸了 ⇒ ★ 所以这条是**冗余的正向确认**（★ 便宜）✓
    json.loads(raw)
    assert raw.count('\\"') >= 0, "★ 冗余断言（★ 保持与上一条同源）"


def test_the_two_lessons_are_recorded_in_the_doc() -> None:
    """★★★★ 核心断言：★ 两条教训都写在文档里（★ 免得后人重踩）✓"""
    t = DOC.read_text(encoding="utf-8", errors="replace")
    #: ★ ① git 那条（★ `checkout --` 的源是索引）
    assert "checkout HEAD" in t, "★ 没写「要用 `git checkout HEAD -- <file>`」这条"
    assert "索引" in t, "★ 没写明 `checkout --` 的源是**索引**"
    #: ★★ ② 手跑生成器那条
    assert "round_chain" in t, "★ 没写「收尾链自己会跑生成器」这条"
    #: ★★★ 而"我判据太窄"那一节也要在（★ 与 §4.1 同族）
    assert "判据太窄" in t or "同一条病" in t, "★ 没记下「我判据又太窄」"
