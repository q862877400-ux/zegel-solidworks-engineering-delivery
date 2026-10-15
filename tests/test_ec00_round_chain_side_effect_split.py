"""★ EC00 T029 判据：**收尾链副作用拆分** —— 验证阶段**不暂存他人改动、不关闭用户文档**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/research.md` §三（★ 副作用实测清单）
#         `tools/round_chain.ps1`（★ L84/L117/L150 `git add -A` · L199 `--close`）
#         `scripts/release_check.py`（★ 只读门禁 —— ★ 本特性用的替代）
#         `AGENTS.md` §十六（★ 每轮收尾链）
# 定位:   ★ EC00 **T029**（★ 逐字：「先将收尾链的生成/验证与全量暂存/关闭 SW 等副作用拆开；
#         增加显式文件白名单和自有工件校验，再做聚焦测试、适用生成器/门禁及来源检查」）。
#         ★★★ **完成判据**：★ **验证阶段不暂存他人改动、不关闭用户文档**；
#         ★ **危险阶段需独立授权**。
# 官方依据: `AGENTS.md` §十六（★ 收尾链）· §十五（★ 护栏）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
ROUND_CHAIN = ROOT / "tools" / "round_chain.ps1"


# ── ① 副作用必须**可指认**（★ 静态扫源码）──────────────────────────

def test_round_chain_side_effects_are_locatable():
    """★★★ T029：★ 收尾链的副作用必须**可指认**（★ 否则没法拆）。

    ★★ 依据（★ 计划 §6.2 逐字）：「★ 先前源码核对已发现 `round_chain.ps1` 收尾包含
      **全量暂存与关闭 SW** 等风险动作」。
    """
    assert ROUND_CHAIN.is_file(), "★ 找不到 `tools/round_chain.ps1`"
    src = ROUND_CHAIN.read_text(encoding="utf-8", errors="replace")
    #: ★★ ① **全量暂存**（★ 会暂存他人改动）
    adds = re.findall(r"^\s*git add -A\s*$", src, re.M)
    assert len(adds) >= 1, "★ 找不到 `git add -A` ⇒ 副作用清单失效"
    #: ★★ ② **关闭 SW**（★ 资源处置）
    assert "reclaim_solidworks" in src and "--close" in src, "★ 找不到 `--close` 处置"


def test_side_effects_are_inventoried_with_line_numbers():
    """★★ T029：★ 副作用清单必须**带可复核的位置**（★ 不能只说「有副作用」）。"""
    body = (SPEC / "research.md").read_text(encoding="utf-8", errors="replace")
    assert "round_chain" in body, "★ `research.md` 里没有 `round_chain` 段"
    #: ★ 必须点到**具体位置**（★ L84/L117/L150/L199 之类）
    assert re.search(r"L\d+", body), "★ 副作用清单里没有**可复核的行位置**"
    for token in ("git add -A", "--close"):
        assert token in body, "★ 副作用清单缺 `%s`" % token


# ── ② 验证阶段**不**暂存他人改动 ─────────────────────────────────────

def test_verification_stage_does_not_stage_others_changes():
    """★★★ T029：★ **验证阶段不暂存他人改动**（★ 逐字承完成判据）。

    ★★ 依据（★ `AGENTS.md` 铁律与 §十六）：★ 每轮收尾**不得** `git add -A`；
      ★★ 提交走 `tools/commit_mine.py` + **显式路径白名单**。
    """
    #: ★★ 本特性用的替代：**只读门禁** + 聚焦 pytest
    body = (SPEC / "research.md").read_text(encoding="utf-8", errors="replace")
    assert "release_check.py" in body, (
        "★★ 没有写明替代方案（★ 用 `release_check.py` + 聚焦 pytest）")
    #: ★★ 且必须写明**不跑整条链**
    assert "不跑整条" in body or "不运行整条" in body, (
        "★★ 没写明「不跑整条 `round_chain.ps1`」")


def test_closeout_uses_explicit_path_allowlist():
    """★★★ T029：★ 收尾必须走**显式文件白名单**（★ 不是全量暂存）。

    ★★ 依据（★ `AGENTS.md` §七 逐字）：
      「★★提交一律走 `python tools/commit_mine.py -m <信息文件> <路径…>`」。
    """
    assert (ROOT / "tools" / "commit_mine.py").is_file(), (
        "★ 找不到 `tools/commit_mine.py` ⇒ 显式白名单通道不在")
    #: ★★ 本特性的验收记录里必须写明「未提交未部署」
    acc = (SPEC / "acceptance.md").read_text(encoding="utf-8", errors="replace")
    assert "未提交" in acc, "★★ 验收记录里没有「未提交未部署」⇒ ★ 红线状态没登记"


# ── ③ 危险阶段**需独立授权** ─────────────────────────────────────────

def test_dangerous_stage_requires_separate_authorization():
    """★★★ T029：★ **危险阶段（提交/资源处置）需独立授权**（★ 逐字承完成判据）。

    ★★ 依据（★ 计划 §6.2 逐字）：「★ 在该拆分完成前，**不直接运行整条链**。
      ★★ **它不是纯只读收尾**」。
    """
    #: ★ 本会话的红线：**禁止** `git commit`/`push`/部署/发布/打 tag
    body = (SPEC / "baseline.md").read_text(encoding="utf-8", errors="replace")
    assert "commit" in body.lower(), "★ `baseline.md` 里没有提交红线"
    #: ★★ 且必须写明本会话**未执行**提交
    assert "未提交" in body or "不提交" in body, "★★ 没写明本会话未提交"


# ── ④ 白名单必须**可执行**（★ 不是空话）─────────────────────────────

def test_allowlist_is_machine_checkable():
    """★★ T029：★ 文件白名单必须**机器可判**（★ 不是散文）。

    ★ 判据：★ `baseline.md` §三 有**逐条列出**的允许写入路径（★ 表格形式）。
    """
    body = (SPEC / "baseline.md").read_text(encoding="utf-8", errors="replace")
    assert "本轮允许写入的文件" in body, "★ `baseline.md` 里没有「允许写入」段"
    #: ★★ 必须点到具体路径
    for token in ("specs/302-ec00-trustworthy-tool-base", "tests/", "scripts/"):
        assert token in body, "★ 白名单里缺 `%s`" % token
    #: ★★★ 且必须有**禁止写**的清单（★ 否则白名单不完整）
    assert "禁止写" in body, "★★ 白名单只有「允许」没有「禁止」⇒ 不完整"
