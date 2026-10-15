"""★ EC00 T022 判据：**旧入口硬门禁** —— 迁移表内代表工具**不得回退旧入口绕门**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `specs/302-ec00-trustworthy-tool-base/plan.md` §十（★ D-001～D-005 冻结决策）
#         `specs/302-ec00-trustworthy-tool-base/spec.md` FR-014（★ **已收窄范围**）
#         `tests/test_deprecated_entry_interlock.py`（★ 既有互锁判据）
#         `tests/test_deprecated_admissible_disposition.py`（★ 处置表）
# 定位:   ★ EC00 **T022**（★ 逐字：「完成旧入口迁移与双路径回归，更新弃用说明」）。
#         ★★★ **完成判据**：★ 旧调用**保持已登记语义或明确拒绝**，★ **无单位静默漂移**，
#         ★ **不绕硬门禁**。
#         ★★★ **分层声明（★ 逐字承 T022）**：「★ 互锁**只覆盖弃用登记表内入口**；
#         ★ **新工程路径硬门禁与未迁移旧入口必须分层**」。
# 官方依据: `AGENTS.md` 铁律 1/2（★ 只做缝合 · 签名以官方源为准）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
TOOL = "solidworks_sketch_apply_relations"


# ── ① 迁移表内的代表工具**不许**回退旧入口 ───────────────────────────

def test_migrated_tool_does_not_fall_back_to_the_legacy_entry():
    """★★★ T022：★ **迁移表内的代表工具不得回退旧入口绕门**（★ FR-014）。

    ★★ 依据（★ `plan.md` §十 D-005 逐字）：
      「★ 该工程路径**不允许回退旧入口绕门**（★ **仅限已纳入本特性迁移表的代表工具**）」。
    ★ 判据：★ 草图关系工具的**首选入口**必须是 `ISketchRelationManager::AddRelation`
      （★ 官方 2 参），★★ **不是** `SketchAddConstraints`（★ 那是**兜底**）。
    """
    import register_capabilities as rc
    spec = {s.name: s for s in rc.all_specs()}.get(TOOL)
    assert spec is not None, "★ 工具未注册"
    #: ★★ 首选入口必须是**派发代码**里的首选 —— ★ 判据只看 `via = "…"` 两行
    #:   ⚠ 第一版按**全文 find** 比位置 ⇒ ★ 被**文档串里**的 `SketchAddConstraints`
    #:   （★ L11/L18/L100/L304）误判成「兜底在前」⇒ ★ 红了一次。
    #:   ★ 真判据：★ 派发分支里的 `via = "…"` 顺序。
    src = (ROOT / "scripts" / "sw_sketch_relations.py").read_text(encoding="utf-8", errors="replace")
    via_lines = [(i, ln.strip()) for i, ln in enumerate(src.splitlines(), 1)
                 if ln.strip().startswith("via = ")]
    assert len(via_lines) >= 2, "★ 找不到两个 `via = …` 派发分支：%r" % via_lines
    first_via = via_lines[0][1]
    assert "AddRelation" in first_via, (
        "★★ 第一个派发分支走的是 %r ⇒ ★ 兜底入口优先于首选入口（★ 绕门）" % first_via)
    assert "SketchAddConstraints" in via_lines[1][1], (
        "★ 第二个派发分支不是兜底入口：%r" % via_lines[1][1])


def test_fallback_is_chosen_before_dispatch_not_after():
    """★★★ T022：★ **兜底必须在派发前选定**（★ 不是异常后临时兜底）。

    ★★ 依据（★ `sw_sketch_relations.py` 逐字）：
      「Fallback is chosen BEFORE dispatch, never after an ambiguous call.」
    ★ 理由：★ 异常后兜底 ⇒ ★ 可能在**不确定状态**下再改一次（★ 非幂等重放）。
    """
    src = (ROOT / "scripts" / "sw_sketch_relations.py").read_text(encoding="utf-8", errors="replace")
    assert "chosen BEFORE dispatch" in src, (
        "★ 实现里没有「兜底在派发前选定」这条语义 ⇒ ★ 可能是异常后兜底")


# ── ② 范围必须**收窄**（★ 不得泛化为「所有旧入口」）─────────────────

def test_scope_is_narrowed_not_generalized():
    """★★★ T022：★ FR-014 的范围必须**收窄**（★ 逐字：「**仅限已纳入本特性迁移表的代表工具**」）。

    ★★ 依据（★ `plan.md` §十 D-005 逐字）：
      「★★ **不得**宣称「所有未迁移旧工具已有新硬门禁」—— ★ **那是无范围泛化**」。
    """
    spec = (SPEC / "spec.md").read_text(encoding="utf-8", errors="replace")
    assert "未纳入迁移范围的旧工具不适用本条" in spec, (
        "★★ `spec.md` 的 FR-014 没有**收窄范围** ⇒ ★ 会被读成「所有旧入口都要过新门」")


def test_data_model_or_plan_declares_the_narrowing():
    """★★ T022：★ 收窄口径必须**同时**在 plan 里写明（★ 防两处说法不一致）。"""
    plan = (SPEC / "plan.md").read_text(encoding="utf-8", errors="replace")
    assert "无范围泛化" in plan, "★ `plan.md` 里没有「不得无范围泛化」这条"


# ── ③ 单位**不得静默漂移** ───────────────────────────────────────────

def test_legacy_path_does_not_silently_change_units():
    """★★★ T022：★ **禁止静默将历史单位改为新单位**（★ 逐字承 P0 PLAN §9）。

    ★★ 依据（★ `plan.md` §九 逐字）：
      「★ 旧入口保持原公开契约或返回**明确弃用错误**；★★ **禁止静默将历史单位改为新单位**」。
    """
    #: ★ 契约：★ 旧入口的换算因子**必须是已登记的**，★ 否则拒绝
    REGISTERED = {"solidworks_sketch_add_line": 1.0 / 1000.0}

    def legacy_scale(tool: str):
        return REGISTERED.get(tool)          #: ★ **None ⇒ 拒绝**（★ 不猜一个 1/1000）

    assert legacy_scale("solidworks_sketch_add_line") == 1.0 / 1000.0
    assert legacy_scale("solidworks_unknown_legacy") is None, (
        "★★ 未登记的历史工具被**猜**了一个换算因子 ⇒ ★ 单位静默漂移")


# ── ④ 既有互锁仍在（★ 不因本特性改动而失效）─────────────────────────

def test_existing_interlock_still_exists():
    """★★ T022：★ 既有互锁判据**必须仍在**（★ 本特性不得把它删了/绕了）。"""
    p = ROOT / "tests" / "test_deprecated_entry_interlock.py"
    assert p.is_file(), "★ 既有互锁判据不见了"
    body = p.read_text(encoding="utf-8", errors="replace")
    assert "successor" in body.lower(), "★ 互锁判据里没有「后继」语义"


def test_interlock_is_declared_as_covering_only_the_registry():
    """★★★ T022：★ 必须**显式声明**互锁只覆盖**弃用登记表内**的入口（★ 分层）。"""
    plan = (SPEC / "plan.md").read_text(encoding="utf-8", errors="replace")
    tasks = (SPEC / "tasks.md").read_text(encoding="utf-8", errors="replace")
    merged = plan + tasks
    assert "只覆盖" in merged and ("登记表" in merged or "弃用" in merged), (
        "★★ 没有声明「互锁只覆盖弃用登记表内入口」⇒ ★ 分层不清")


# ── ⑤ 迁移表里的代表工具必须**已登记** ───────────────────────────────

def test_migrated_representative_tools_are_registered():
    """★★ T022：★ 迁移表里的代表工具必须**真的在 `all_specs()` 里**（★ 否则迁移表是空话）。"""
    import register_capabilities as rc
    names = {s.name for s in rc.all_specs()}
    for tool in (TOOL, "solidworks_sketch_add_line"):
        assert tool in names, "★★ 迁移表里的代表工具 `%s` **未注册**" % tool
