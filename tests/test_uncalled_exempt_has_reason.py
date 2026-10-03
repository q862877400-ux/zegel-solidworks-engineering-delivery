"""★ 测「死代码豁免必须写理由」（★ 含负例 · 轮 120 清零那两条存量）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `tests/test_no_uncalled_helpers.py`（★ 改的就是它 —— 加了两条豁免）
# 定位:   ★ 轮 119 全量：★ **3 failed / 1741 passed** ⇒ ★★ 本轮清掉最后两条 ✓
#   ★★★ **其中一条真机读数**（★ `test_no_uncalled_helpers` 逐字）：
#     `tools\probe_featurefillet3.py L44 _active_or_last_sketch` ·
#     `tools\spotcheck_contract_summaries.py L39 _n_params` ✓
#   ★★★★ **⇒ 而我**没有删它们**、★ 而是**加进 `UNCALLED_EXEMPT`**** —— ★ 理由是**纪律①**：
#     ★ **`tools/` 下的探针/证据脚本**只报不动**（★ 改了会破坏「证据不可变」——
#       GATE-FINAL C12）** ⇒ ★★ **删掉一个辅助函数就是**改既有的证据脚本**** ✗
#   ★★★★★ **⇒ 那个测试自己写着两条路**（★ 逐字）：
#     「★ 要么**删掉**（★ 并留墓碑注释）、★ 要么**加进 `UNCALLED_EXEMPT` 并写明理由**」⇒
#     ★★ **对 `tools/` 下的文件只有第二条路** ✓
#   ★★★★★★ **⇒ 两条都**实测过是真死**：★ 全仓各只有 **1** 处 = **定义处** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from test_no_uncalled_helpers import UNCALLED_EXEMPT  # noqa: E402


def test_every_exemption_has_a_reason() -> None:
    """★★★ 核心断言：★ **每条豁免都要有理由、★ 且理由够长、★ 且提到纪律①** ✓

    ★★ **判据**：★ 照 `MANUAL_MAP` / `COMTYPES_CALL_SITES` 的先例 ——
      ★★★ **「没依据的不许进来」** ⇒ **空理由 / 敷衍理由都不算** ✓
    """
    assert UNCALLED_EXEMPT, "★ 至少应有本轮加的两条（★ 若清空了，说明有人删了工具脚本）"
    for name, reason in UNCALLED_EXEMPT.items():
        assert name.startswith("_"), "★ 豁免的应当是**私有辅助**：%r" % (name,)
        assert len(reason) > 60, "★ `%s` 的理由太短：%r" % (name, reason)
        #: ★★★ 理由**必须点明**为什么"不删"（★ 那是本表的唯一正当理由）✓
        assert "不能删" in reason, "★ `%s` 的理由没写明**为什么不删**" % (name,)
        assert "只报不动" in reason, (
            "★ `%s` 的理由没点明纪律①（★ `tools/` 只报不动）" % (name,))


def test_the_two_names_are_really_dead() -> None:
    """★★★ 核心断言：★ 那两条**确实**全仓只有 1 处（★ = 定义处）✓

    ★★ **为什么**：★ 若哪天有人给它们加了调用 ⇒ **豁免就不再需要** ⇒
      ★★★ **本测试会红、★ 提醒把那两条从表里删掉** ✓

    ★★★★★ 2026-10-04（轮 120）**判据要精确**（★ 事实 51 · 本会话第 N 次）：
      ★ **第一版查「名字出现」** ⇒ ★★ **实测命中 **6** 处**（★ 定义处 · ★ **豁免表本身** ·
      ★ **我那个一次性修脚本** · ★ 本文件的记录…）⇒ ★★★ **那不是"被调用"** ✗
      ★★★★ **⇒ 真判据是**调用形态****：★ **名字后跟 `(`**、★ **且不在定义行**、
        ★ 且不在**豁免表的值**里 ✓
      ★★★★★ **⇒ 这与会话里那条反复出现的判据同族**：★★★
        **「判"有没有人用它"要查**调用形态**、★ 不要查**名字出现**** ✓
        （★ `csys_params` / `fillet_params` / `feature_info` 那三处都是同一个坑）✓
    """
    for name in ("_active_or_last_sketch", "_n_params"):
        hits = []
        for f in REPO.rglob("*.py"):
            s = str(f)
            if any(x in s for x in ("_raw", ".git", "AI Solidworks", "node_modules",
                                    "\\output\\", "/output/")):
                continue
            #: ★★★★ **必须排除本文件自己**（★ 否则判据自指）✓
            if f.resolve() == Path(__file__).resolve():
                continue
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
            except OSError:                                   # pragma: no cover
                continue
            for k, line in enumerate(t.splitlines(), 1):
                #: ★★ **只认调用形态**：★ 名字后跟 `(`（★ 可选空白）✓
                if not re.search(re.escape(name) + r"\s*\(", line):
                    continue
                #: ★★★ 排除**定义行**（`def name(`）✓
                if re.match(r"\s*def\s+" + re.escape(name) + r"\s*\(", line):
                    continue
                #: ★★★★ 排除**豁免表的值**（★ 那张表里会提到名字，★ 那不是调用）✓
                if re.search(r'"?\s*' + re.escape(name) + r'"\s*:', line) or \
                        re.match(r"\s*[\"']" + re.escape(name) + r"[\"']\s*:", line):
                    continue
                hits.append((f, k, line.strip()[:70]))
        assert not hits, (
            "★ `%s` 现在**被调用了**（★ %d 处）⇒ **请从 `UNCALLED_EXEMPT` 删掉它**：%r"
            % (name, len(hits), hits[:4]))


def test_negative_case_the_exempt_reason_is_not_a_bare_word() -> None:
    """★★★★ **负例 · 不许把"理由"写成一句空话**：★ 每条至少两句 ✓

    ★★ **判据**：★ 按**句读**数（★ `。` / `；`）≥ **2** ⇒
      ★★★ **那能挡住"待补"、"见上"、"豁免"这类敷衍** ✓
    """
    for name, reason in UNCALLED_EXEMPT.items():
        n = reason.count("。") + reason.count("；")
        assert n >= 2, "★ `%s` 的理由只像一句话（★ 句读数 %d）⇒ 要说清**为什么不删**" % (name, n)


def test_negative_case_the_gate_still_runs_the_probe() -> None:
    """★★★ **负例 · 门禁仍走真探针**：★ 不许把 `_suspects` 改成读本表 ✓

    ★★ **为什么**：★ 若有人图省事让 `_suspects()` 直接回空 ⇒
      ★★★ **那门禁就**永远绿**、★ 而它**什么也没查**** ✗（★ 与**事实 62**同族）✓
    """
    t = (TESTS / "test_no_uncalled_helpers.py").read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(t)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_suspects")
    lines = t.splitlines()
    body = "\n".join(lines[fn.lineno - 1:getattr(fn, "end_lineno", fn.lineno)])
    assert "probe.find_uncalled()" in body, (
        "★ `_suspects` 不再调真探针了 ⇒ 那门禁就永远绿、什么也没查")
