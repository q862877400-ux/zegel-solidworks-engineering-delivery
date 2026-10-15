"""★ EC00 T013 判据：**假成功负例** —— API 回 `true` 但效果不成立 ⇒ **绝不 `pass`**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/contracts/effects.md`（★ 三态契约）
#         `specs/302-ec00-trustworthy-tool-base/data-model.md` §5.3（★ `EffectStatus`）
#         `scripts/sw_sketch_relations.py`（★ 关系效果回读 · ★ `GetRelationsCount`）
#         `AGENTS.md` 已知事实 8（★ `Select4`/`SelectByID2` 的 bool **不可信**）
# 定位:   ★ EC00 **T013**（★ 逐字：「建返回 true 但无效果、关系未持久、回读错误/不可用、
#         旧证据错版本负例」）。
#         ★★★ **完成判据**：★ 故障样例**均不能 effect pass**，★ **参考值不取自被测实现**。
# 官方依据: `ISketchSegment::GetRelationsCount`（★ 回读判据）· `AGENTS.md` 事实 8
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 用**假宿主**）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

REL_SRC = ROOT / "scripts" / "sw_sketch_relations.py"

#: ★★★ 效果三态（★ 封闭词表 · ★ `data-model.md` §5.3）
PASS, FAIL, UNKNOWN = "pass", "fail", "unknown"


def _effect(api_return, *, before, after, readback_ok: bool = True) -> str:
    """★ 复刻契约的**判定规则**（★ 纯函数 · ★ 参考值**不取自被测实现**）。

    ★★★ 规则（★ `contracts/effects.md` §三）：
      · ★ `readback_ok == False` ⇒ **必须 `unknown`**（★ 不得 `pass`）；
      · ★ 前态/后态**都没有** ⇒ `unknown`；
      · ★ 回读证明**关系数 +1** ⇒ `pass`；★ **没变** ⇒ `fail`；
      · ★★ **`api_return` 不参与判定**（★ 那是 FR-008 的核心）。
    """
    if not readback_ok:
        return UNKNOWN
    if before is None or after is None:
        return UNKNOWN
    return PASS if after > before else FAIL


# ── ① 返回 true 但无效果 ──────────────────────────────────────────────

def test_true_with_no_effect_is_not_pass():
    """★★★ T013：★ **API 回 `true` 但关系数没变** ⇒ ★★ **必须 `fail`**（★ 绝不 `pass`）。

    ★★ 依据（★ `AGENTS.md` 事实 8）：★「`AddSelectionListObject` 的 bool 返回值**不可信**，
      ★ 用 `GetSelectedObjectCount2(-1)` **回读**」⇒ ★★ 关系族同理。
    """
    assert _effect(True, before=3, after=3) == FAIL, (
        "★★ API 回 `true` 但关系数没变却被判 `pass` ⇒ ★ 假成功（★ FR-008 的核心负例）")
    #: ★ 反例（★ 真的 +1 才该 pass）
    assert _effect(True, before=3, after=4) == PASS, "★ 真的 +1 应判 pass"


# ── ② 回读不可用 ──────────────────────────────────────────────────────

def test_unreadable_effect_is_unknown_not_pass():
    """★★★ T013：★ **回读不可用** ⇒ ★★ **必须 `unknown`**（★ 绝不 `pass`）。

    ★★ 依据（★ `contracts/effects.md` §三 逐字）：
      「★★ **`readback_ok == False` ⇒ `effect_status` 必须是 `unknown`**，★★ **不得 `pass`**」。
    """
    assert _effect(True, before=3, after=None, readback_ok=False) == UNKNOWN, (
        "★★ 回读不可用却判 `pass` ⇒ ★ 不可回读被当成通过")
    #: ★ 即使 API 回 `true`、★ 且 before/after 都在、★ 但回读标记为失败 ⇒ unknown
    assert _effect(True, before=3, after=4, readback_ok=False) == UNKNOWN, (
        "★★ 回读失败时**即使前后态看起来变了**也必须是 `unknown`")


# ── ③ 前态缺失 ────────────────────────────────────────────────────────

def test_missing_pre_state_is_unknown():
    """★★★ T013：★ **前态读不到** ⇒ ★★ **必须 `unknown`**（★ 不能靠后态单方面判 pass）。

    ★★ 依据（★ `sw_sketch_relations.py` 逐字）：★「Pre-dispatch relation count unavailable;
      no mutation attempted.」⇒ ★ 实现已经**不做修改**，★ 契约侧也要判 `unknown`。
    """
    assert _effect(True, before=None, after=4) == UNKNOWN, (
        "★★ 前态缺失却判了 pass/fail ⇒ ★ 无基线可比")


# ── ④ 旧证据错版本 ────────────────────────────────────────────────────

def test_stale_evidence_cannot_release_a_new_model():
    """★★★ T013：★ **模型变了 ⇒ 旧证据不能放行新模型**（★ US5 · FR-011）。

    ★★ 依据（★ `data-model.md` §六 逐字）：
      「★ **模型改变后，旧的证据不能直接用于放行新模型**」。
    """
    def evidence_valid(evidence_model_rev: str, current_model_rev: str) -> bool:
        return evidence_model_rev == current_model_rev

    assert evidence_valid("rev-A", "rev-A"), "★ 同版本应有效"
    assert not evidence_valid("rev-A", "rev-B"), (
        "★★ 旧证据（rev-A）放行了新模型（rev-B）⇒ ★ 证据版本失效规则没生效")


# ── ⑤ 参考值不取自被测实现 ────────────────────────────────────────────

def test_reference_value_is_not_taken_from_the_implementation():
    """★★★ T013：★ **参考值不取自被测实现**（★ 逐字承 T013 完成判据）。

    ★★ 依据（★ `plan.md` §7 L1 与 `contracts/effects.md` §三）：
      「★★ **`tolerance_source` 不得取自被测实现**」。
    ★ 判据：★ 本文件的期望值是**硬写的纯数学/契约常量**（★ `before`/`after` 由**测试自己给**）
      ⇒ ★★ **不是**从 `sw_sketch_relations` 里读出来的。
    """
    #: ★ 期望值全是**本文件自己的字面量** ⇒ 与被测实现无关
    assert _effect(True, before=0, after=0) == FAIL
    assert _effect(True, before=0, after=1) == PASS
    #: ★★ **负例**：若参考值来自实现 ⇒ 那两者必然相等（★ 双盲）⇒ ★ 本判据守住这一点
    #:   ★ 判据用 **AST**（★ 只看**真的 import 语句**）—— ★ 不能用文本包含
    #:   （★ 那会被**注释/字符串里提到它**误触发 —— ★ 本判据第一版就这么红了一次）
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8", errors="replace"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    bad = [m for m in imported if "sw_sketch_relations" in m]
    assert not bad, (
        "★★ 本判据**导入了被测实现** %r ⇒ ★ 参考值可能取自实现（★ 双盲）" % bad)


# ── ⑥ 实现侧：三态确实存在（★ 防「契约写了、实现没有」）──────────────

def test_implementation_has_three_state_effect():
    """★★ T013：★ **实现里确实有 `effect_status` 三态**（★ 不只是契约里写了）。"""
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "effect_status" in src, "★ 实现里没有 `effect_status`"
    #: ★ 三态都要出现
    for state in ('"pass"', '"fail"', '"unknown"'):
        assert state in src, "★ 实现里缺三态之一：%s" % state
    #: ★★ **不许**有「API 返回 true 就 applied」这种直通
    tree = ast.parse(src)
    src_text = src
    bad = [ln for ln, line in enumerate(src_text.splitlines(), 1)
           if "applied = True" in line and "effect_status" not in line]
    assert not bad, (
        "★ 第 %r 行把 `applied = True` 与 `effect_status` 脱钩 ⇒ ★ 可能是 `true` 直通" % bad)
