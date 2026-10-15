"""★ spec 259：**② 段 6 条待办的逐条前提核对** —— 每条定类 + 附证据（★ 不为了缩表而删）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/AUTO_HANDOFF.md（★ ② 段的 6 条）· output/GOAL.md（★ 目标真源）
#         specs/258-todo-premise-audit/（★ 同法的第一轮：核出并核销 1 伪待办 + 2 条「不是待办」）
#         scripts/sw_sheet_metal.py:154-165（★ `create_hem` 五种形态全回 `None` 的真机实录）
#         tests/test_obsolete_host_review_family.py（★ 250 的真命中表）
# 定位:   ★ 258 只核了 1 条；★ 本文件把**其余 5 条**也逐条核完 ⇒ ★ **6 条全部有类与证据**。
# 官方依据: 本仓纪律「交接单自己的前提也要核」（★ 227/232–240 已连续九轮核出错）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不改 `scripts/`
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.test_obsolete_host_review_family import REAL_HIT, _HOST_EXPR_REVIEW  # noqa: E402

#: ★ 分类封闭词表（★ 同 258）。
ACTIONABLE = "actionable"
NEEDS_OWNER = "needs-owner"
GATED = "gated"                  #: ★ 真待办但**有前置**（★ 例如「发版前」）
CODES = {ACTIONABLE, NEEDS_OWNER, GATED}

#: ★★★ **② 段 6 条的逐条定类**（★ 值 = `(类, 证据)`）。
#: ★★ **本轮**不删任何一条** —— ★ `create_hem` 那条**有真机实录**（★ 不是伪待办）。
_TODOS: dict[str, tuple[str, str]] = {
    "① 只读真机复核（16 条 arity 已定罪；★ 剩余 = `counted_positions` 口径缺陷）": (
        ACTIONABLE, "★ 253 实测：`counted_positions` 会把**全 by-ref 形参**剥光 ⇒ 4 条假阳性"),
    "② 换路由 + 真机验（250 的 7 处真命中）": (
        ACTIONABLE, "★ 250 实测：**4 名 · 5 处** `real-hit`（★ 规格 301 订正：移出 `KFactor`（现判 "
                    "`false-hit`）与 `MaterialIdName`（不在 250 表里）—— 两条**已在 spec 261 真机复验**）"),
    "③ 高危/写盘（`SaveAs3` · `create_draft` · `create_profile_center_mate`）": (
        ACTIONABLE, "★ 业主已授权 C 级"),
    "④ `create_hem` 的行为证据": (
        ACTIONABLE, "★ **真机实录**：`sw_sheet_metal.py:154-165` —— 2026-10-06 · SW 2026 SP4.1 · 五种形态全回 `None`"),
    "⑤ 223 的 8 条 `HEAD` 即红既有失败": (
        NEEDS_OWNER, "★ 权属不明 ⇒ 只登记不动"),
    "⑥ 发版前同步打包副本": (
        GATED, "★ **前置 = 发版**：`scripts/sync_bundled_skill.py` 把桌面内嵌 Skill 快照同步到打包目录；"
               "★ 不发版就没有可同步的对象"),
}

#: ★★ 本轮**不许**删任何一条（★ 与 258 的区别：258 核销的是**伪待办**，这里都是真待办）。
BASELINE_TODOS = 6


def _class_failures(todos: dict) -> list[str]:
    """★ 纯函数：每条必须有**合法类** + **非空证据**。"""
    out: list[str] = []
    for k, (code, why) in sorted(todos.items()):
        if code not in CODES:
            out.append("%s 的类 %r 不在封闭词表 %s" % (k, code, sorted(CODES)))
        if len(why) < 10:
            out.append("%s 的证据太短（★ 不许空口定类）" % k)
    if len(todos) != BASELINE_TODOS:
        out.append("条数 %d ≠ 基线 %d ⇒ ② 段变了，请同步本表" % (len(todos), BASELINE_TODOS))
    return out


# ── ① ★★ 6 条全部有类与证据 ────────────────────────────────────────
def test_all_six_todos_are_classified_with_evidence():
    """★★ ② 段的 **6** 条逐条定类 + 附证据（★ 空口定类即红）。"""
    bad = _class_failures(_TODOS)
    assert not bad, "定类不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ `create_hem` 那条**不是**伪待办（★ 有真机实录）─────────────
def test_create_hem_todo_has_machine_evidence():
    """★★★ 核 `create_hem` 那条的**前提**：★ 它**有真机实录** ⇒ ★ **不许**当伪待办核销。

    ★ 依据逐字（`scripts/sw_sheet_metal.py:154-165`）：★ **2026-10-06 · SW 2026 SP4.1 · pywin32**，
    ★ **五种形态全部回 `None`** ⇒ ★ 这是**可证伪的实测**，★ 不是猜测。
    """
    src = (SCRIPTS / "sw_sheet_metal.py").read_text(encoding="utf-8")
    assert "五种形态全部回 `None`" in src, \
        "`sw_sheet_metal.py` 里找不到「五种形态全部回 `None`」⇒ `create_hem` 待办的**依据**没了"
    assert "2026-10-06" in src, "找不到真机实录的日期 ⇒ 依据不完整"
    key = [k for k in _TODOS if "create_hem" in k]
    assert key, "`create_hem` 那条不在本表里"
    assert _TODOS[key[0]][0] == ACTIONABLE, "`create_hem` 应是**真待办**（★ 不是伪待办）"


# ── ③ ★★ 换路由那条的靶子必须与 250 一致 ────────────────────────────
def test_routing_todo_targets_match_250():
    """★★ 第 ② 条的靶子 = 250 的 `real-hit`（★ **4 名 · 5 处**）—— ★ 与本表**逐条一致**。

    ★★ 2026-10-10（规格 301）：★ 基线从 **6 名 · 7 处**订正为 **4 名 · 5 处** ——
      ★ 移出 `KFactor`（★ 250 现判 `false-hit`）与 `MaterialIdName`（★ 不在 250 表里）；
      ★★ 两条的换路由**已在 `spec 261` 完成并真机复验** ✓
    """
    got = {k: len(v[3]) for k, v in _HOST_EXPR_REVIEW.items() if v[0] == REAL_HIT}
    assert sum(got.values()) == 5, "真命中站点数应为 5（★ 规格 301 订正），实测 %d" % sum(got.values())
    assert len(got) == 4, "真命中名数应为 4（★ 规格 301 订正），实测 %d" % len(got)


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 类不在词表；② 证据为空；③ 条数变了。"""
    assert not _class_failures(_TODOS), "正常表被判红 ⇒ 判据过严"
    bad1 = dict(_TODOS)
    k = next(iter(bad1))
    bad1[k] = ("待定", bad1[k][1])
    assert any("封闭词表" in b for b in _class_failures(bad1)), "非法类未判出 ⇒ **空判据**"
    bad2 = dict(_TODOS)
    bad2[k] = (ACTIONABLE, "")
    assert any("证据太短" in b for b in _class_failures(bad2)), "空证据未判出 ⇒ **空判据**"
    bad3 = dict(list(_TODOS.items())[:5])
    assert any("条数" in b for b in _class_failures(bad3)), "条数变了未判出 ⇒ **空判据**"
