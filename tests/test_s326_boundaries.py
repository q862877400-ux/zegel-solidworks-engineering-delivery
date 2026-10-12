"""★ 规格 326 契约测试：问题持久化 + DoD 边界 + 止损关口 + 运行边界（S1~S19）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s326_boundaries.py
# 定位:   规格 `specs/326-question-persistence-and-boundaries` 的 S1~S19 契约测试
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q8（L163-174）逐字
#           ② 同文件 Q9（L176-199）· Q11（L201-212）· Q15（L299-327）逐字
#           ③ `metadata/scope-v1.json`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import boundaries as B                          # noqa: E402
from scripts.engineering import questions as Q                           # noqa: E402
from scripts.engineering import scope as S                               # noqa: E402


def _q(**kw) -> Q.Question:
    base = dict(run_id="t-run", requirement_revision="rev-1",
                field_name="load_upper", value_schema="number", unit="N",
                reason="缺载荷上界")
    base.update(kw)
    return Q.make_question(**base)


#: ══ S1 问题对象 12 字段 ══════════════════════════════════════════════

def test_eleven_question_fields() -> None:
    """★★ Q8 L165 逐字给的字段 —— ★ **实数是 11 个**。

    ⚠ 实测（2026-10-12）：我在规格里写成「12 字段」—— ★ **数错了**。
      ★ 逐字切分 `/` 得 **11 个** ⇒ ★ 以**原文**为准（★ 规格与代码已同步更正）。
    """
    assert len(Q.QUESTION_FIELDS) == 11, \
        "★ 字段数不是 11（★ Q8 L165 逐字切分的结果）"
    want = {"question_id", "run_id", "requirement_revision", "field",
            "value_schema", "unit", "reason", "blocking",
            "allowed_default_ref", "answer_source", "status"}
    assert want == set(Q.QUESTION_FIELDS)


def test_question_validates() -> None:
    """★ 造出来的问题**过校验**。"""
    q = _q()
    q.validate()
    assert q.question_id.startswith("q-")


def test_question_id_is_deterministic() -> None:
    """★ `question_id` 可复核（★ 同输入同 id）。"""
    assert _q().question_id == _q().question_id


def test_bad_status_rejected() -> None:
    """★ 状态是封闭值。"""
    with pytest.raises(Q.QuestionError) as ei:
        Q.Question(status="乱写的")
    assert ei.value.code == "bad-status"


def test_bad_source_rejected() -> None:
    """★ 来源是封闭值。"""
    with pytest.raises(Q.QuestionError) as ei:
        Q.Question(answer_source="乱写的")
    assert ei.value.code == "bad-source"


#: ══ S2 落盘读回 ══════════════════════════════════════════════════════

def test_save_and_load_roundtrip() -> None:
    """★★ Q8 L167 逐字：「**先保存问题，再请求输入**」⇒ 落盘可读回。"""
    qs = [_q(), _q(field_name="travel_upper")]
    p = Q.save_questions("t-run", "rev-1", qs)
    assert p.is_file()
    back = Q.load_questions("t-run", "rev-1")
    assert len(back) == 2
    assert {x["question_id"] for x in back} == {q.question_id for q in qs}


def test_load_missing_returns_empty() -> None:
    """★ 没有 ⇒ 空列表（★ 不抛）。"""
    assert Q.load_questions("no-such-run", "rev-9") == []


def test_waiting_payload_is_structured() -> None:
    """★★ Q8 L170 逐字：「返回**持久化的 `WAITING_INPUT`、问题对象和回答入口**，
    **而不只是自然语言提示**」。"""
    p = Q.waiting_payload("t-run", "rev-1", [_q()])
    assert p["state"] == "WAITING_INPUT"
    assert p["questions"] and p["answer_entry"]
    assert p["answer_entry"]["must_carry"] == ["question_id",
                                               "requirement_revision"]


#: ══ S3 可信人工确认 ══════════════════════════════════════════════════

def test_llm_self_reported_human_is_rejected() -> None:
    """★★★ Q8 L171 逐字：「**LLM 自己提交 `source=human` 不算人工确认**」。

    ★★ 判据：`source=human` **必须带可信通道证明** ——
      ★ 只写字符串 `"human"` **不算**（★ 那正是 LLM 能做的）。
    """
    q = _q()
    with pytest.raises(Q.QuestionError) as ei:
        Q.answer(q, 15000, source=Q.SRC_HUMAN)
    assert ei.value.code == "untrusted-human"
    assert q.status == Q.OPEN, "★ 状态不该变"


def test_human_with_trusted_channel_is_accepted() -> None:
    """★ 带可信通道 ⇒ 接受。"""
    q = _q()
    Q.answer(q, 15000, source=Q.SRC_HUMAN, channel_proof="local_confirm_ui")
    assert q.status == Q.ANSWERED
    assert q.answer_source == Q.SRC_HUMAN


def test_bogus_channel_proof_rejected() -> None:
    """★ 伪造的通道证明 ⇒ 拒。"""
    q = _q()
    with pytest.raises(Q.QuestionError):
        Q.answer(q, 1, source=Q.SRC_HUMAN, channel_proof="llm_says_so")


def test_approved_default_needs_ref() -> None:
    """★★ Q8 L169 逐字：「**默认值也要记录出处**」。"""
    q = _q()
    with pytest.raises(Q.QuestionError) as ei:
        Q.resolve_with_default(q, 100)
    assert ei.value.code == "bad-source"
    #: ★ 有出处 ⇒ 可
    q2 = _q(allowed_default_ref="policy://naming")
    S_ = Q.resolve_with_default(q2, "part-001")
    assert S_.answer_source == Q.SRC_DEFAULT


#: ══ S4 补答拒旧版本 ══════════════════════════════════════════════════

def test_stale_revision_is_rejected() -> None:
    """★★ Q8 L170 逐字：「补答必须携带问题 ID 与期望版本，**拒绝旧版本覆盖**」。"""
    q = _q()
    with pytest.raises(Q.QuestionError) as ei:
        Q.apply_answer(q, 1, source=Q.SRC_HUMAN, carried_revision="rev-0",
                       current_revision="rev-1",
                       channel_proof="local_confirm_ui")
    assert ei.value.code == "stale-revision"
    assert q.status == Q.STALE


def test_current_revision_is_accepted() -> None:
    """★ 携带**当前**版本 ⇒ 接受。"""
    q = _q()
    Q.apply_answer(q, 1, source=Q.SRC_HUMAN, carried_revision="rev-1",
                   current_revision="rev-1", channel_proof="local_confirm_ui")
    assert q.status == Q.ANSWERED


#: ══ S5 等待时释放执行锁 ══════════════════════════════════════════════

def test_waiting_releases_everything() -> None:
    """★★ Q8 L167 逐字：「**等待用户时释放执行锁**，
    **不保持 COM 调用或选区**」。"""
    w = Q.WaitingState()
    assert w.holds_execution_lock is True
    w.enter_waiting()
    assert w.released is True
    assert w.holds_com is False and w.holds_selection is False


#: ══ S6 v1 上界 ═══════════════════════════════════════════════════════

def test_scope_file_has_five_limits() -> None:
    """★★ Q9 L180-182 逐字给的**五条上界**。"""
    sc = S.load_scope()
    assert sc["limits"] == {"max_self_made_parts": 10,
                            "max_assembly_instances": 30,
                            "max_assembly_levels": 2,
                            "max_driven_dof": 1,
                            "max_method_level_nodes": 100}


def test_within_scope_passes() -> None:
    """★ 正好在上界 ⇒ 过。"""
    r = S.check_scope(self_made_parts=10, assembly_instances=30,
                      assembly_levels=2, driven_dof=1, method_level_nodes=100)
    assert r["ok"] is True


@pytest.mark.parametrize("kw", [
    {"self_made_parts": 11},
    {"assembly_instances": 31},
    {"assembly_levels": 3},
    {"driven_dof": 2},
    {"method_level_nodes": 101},
])
def test_over_scope_is_rejected(kw) -> None:
    """★★ Q9 L180-182：**五条上界**，任一条超 ⇒ 拒。"""
    r = S.check_scope(**kw)
    assert r["ok"] is False
    assert r["over"]


def test_scope_does_not_count_api_calls() -> None:
    """★★ Q9 L182 逐字：「**不按底层 API 次数衡量产品复杂度**」。"""
    import inspect
    params = set(inspect.signature(S.check_scope).parameters)
    assert not any("api" in p.lower() for p in params), \
        "★★ `check_scope` 收了 API 次数 ⇒ 违反 Q9 L182"


#: ══ S7 不承诺清单 ════════════════════════════════════════════════════

def test_not_promised_list() -> None:
    """★★ Q9 L185 逐字：**五类不进入自主承诺**。"""
    sc = S.load_scope()
    for k in ("freeform_surface", "compliant_mechanism",
              "arbitrary_spatial_mechanism", "multiphysics",
              "unverified_contact_friction"):
        assert k in sc["not_promised"], "★ 缺 %s" % k


def test_not_promised_is_rejected() -> None:
    """★ 命中清单 ⇒ 拒。"""
    r = S.check_not_promised("freeform_surface")
    assert r["ok"] is False and r["code"] == "not-promised"


def test_normal_feature_passes() -> None:
    """★ 不在清单里 ⇒ 过。"""
    assert S.check_not_promised("hole_group")["ok"] is True


#: ══ S8 DELIVERED 需人工批准 ══════════════════════════════════════════

def test_auto_done_is_only_ready_for_review() -> None:
    """★★★ Q9 L197 逐字：「`READY_FOR_REVIEW` 表示**自动流程完成待审核**；
    **`DELIVERED` 还需可信人工批准**」。"""
    r = S.delivery_state(auto_done=True)
    assert r["state"] == S.READY_FOR_REVIEW
    assert r["delivered"] is False
    assert r["code"] == "missing-approval"


def test_trusted_approval_yields_delivered() -> None:
    """★ 有**可信**批准 ⇒ `DELIVERED`。"""
    r = S.delivery_state(auto_done=True, approved_by="owner_typed")
    assert r["state"] == S.DELIVERED and r["delivered"] is True


def test_llm_self_approval_does_not_deliver() -> None:
    """★★ LLM 自报批准 ⇒ **不算**（★ 与 Q8 同口径：要**通道**不要字符串）。"""
    r = S.delivery_state(auto_done=True, approved_by="llm")
    assert r["delivered"] is False
    assert r["state"] == S.READY_FOR_REVIEW


def test_not_auto_done_is_neither() -> None:
    """★ 自动流程没完 ⇒ 连 `READY_FOR_REVIEW` 都不是。"""
    assert S.delivery_state(auto_done=False)["state"] == ""


#: ══ S9 人工接管单独计数 ══════════════════════════════════════════════

def test_takeover_counted_separately() -> None:
    """★★★ Q9 L195 逐字：「**人工接管的任务要单独计数，不能计作自主完成**」。"""
    t = S.TakeoverLedger(autonomous=5)
    t.record("t1", hand_built=True)
    assert t.autonomous_only == 5, "★★ 接管被算进自主了！"
    assert len(t.taken_over) == 1
    assert t.total == 6


def test_takeover_two_forms() -> None:
    """★ 两种接管形态都要记（★ Q9 L195：「不手工补建零件、不改脚本救火」）。"""
    t = S.TakeoverLedger()
    t.record("t1", hand_built=True)
    t.record("t2", script_patched=True)
    d = t.to_dict()
    assert d["hand_built"] == 1 and d["script_patched"] == 1


#: ══ S10 两个止损关口 ═════════════════════════════════════════════════

def test_two_stop_gates() -> None:
    """★★ Q11 L203 逐字：「**两个投入止损关口**」。"""
    assert len(S.STOP_GATES) == 2
    assert set(S.STOP_GATES) == {S.GATE_STAGE2, S.GATE_STAGE4}


def test_stage2_gate_stops_below_three_passes() -> None:
    """★★ Q11 L205 逐字：「无法……**稳定通过三次独立启动验证**」。"""
    assert S.stage2_gate(passes=3)["stop"] is False
    assert S.stage2_gate(passes=2)["stop"] is True
    assert S.stage2_gate(passes=2)["action"] == "STOP_EXPANDING_AUTONOMY"


def test_stage2_gate_budget_exceeded() -> None:
    """★ 超预算 ⇒ 也停（★ Q11 L205「在阶段预算上限内」）。"""
    assert S.stage2_gate(passes=5, budget_exceeded=True)["stop"] is True


def test_stage4_gate_two_attributed_rounds() -> None:
    """★★ Q11 L206 逐字：「在**两轮有明确归因的改进后**仍达不到冻结盲测门槛」。"""
    assert S.stage4_gate(attributed_rounds=2, meets_threshold=False)["stop"] is True
    assert S.stage4_gate(attributed_rounds=1, meets_threshold=False)["stop"] is False
    assert S.stage4_gate(attributed_rounds=5, meets_threshold=True)["stop"] is False


def test_stage4_gate_misrelease_stops() -> None:
    """★ 把**关键需求不满足**的计划放进真实执行 ⇒ 停（★ Q11 L206 后半句）。"""
    assert S.stage4_gate(attributed_rounds=0, meets_threshold=True,
                         misreleased=1)["stop"] is True


#: ══ S11 三次失败停补丁 ══════════════════════════════════════════════

def test_three_failures_stop_patching() -> None:
    """★★★ Q11 L208 逐字：「同一假设**连续三次修复失败**停止补丁式尝试，
    **重新检查契约或架构**」。"""
    t = S.HypothesisTracker()
    assert t.record("h1", succeeded=False)["stop_patching"] is False
    assert t.record("h1", succeeded=False)["stop_patching"] is False
    r = t.record("h1", succeeded=False)
    assert r["stop_patching"] is True
    assert r["action"] == "RECHECK_CONTRACT_OR_ARCHITECTURE"


def test_success_resets_counter() -> None:
    """★★ 判据是「**连续**三次」⇒ ★ 成功要**归零**。"""
    t = S.HypothesisTracker()
    t.record("h1", succeeded=False)
    t.record("h1", succeeded=False)
    t.record("h1", succeeded=True)
    assert t.record("h1", succeeded=False)["stop_patching"] is False


def test_different_hypotheses_are_independent() -> None:
    """★ 不同假设**互不影响**。"""
    t = S.HypothesisTracker()
    t.record("h1", succeeded=False)
    t.record("h1", succeeded=False)
    assert t.record("h2", succeeded=False)["stop_patching"] is False


#: ══ S12 Plan B ═══════════════════════════════════════════════════════

def test_plan_b_separates_human_and_system() -> None:
    """★★★ Q11 L210 逐字：「**Plan B：人工确认 DesignIR／选择方法**，
    系统负责**确定性**编译、执行、变更、出图和验证」。"""
    p = S.PlanB()
    assert set(p.human_confirms) == {"DesignIR", "method_selection"}
    assert set(p.system_does) == {"compile", "execute", "change", "draw",
                                 "verify"}


def test_plan_b_requires_human_first() -> None:
    """★ 人工那两件没做完 ⇒ Plan B **不启动**。"""
    p = S.PlanB()
    assert p.route(human_did=["DesignIR"])["ready"] is False
    assert p.route(human_did=["DesignIR", "method_selection"])["ready"] is True


#: ══ S13 盲题转回开发集 ═══════════════════════════════════════════════

def test_seen_failure_moves_to_dev() -> None:
    """★★★ Q11 L206 逐字：「**已看过的失败盲题转回开发集**，
    **不能继续把原题称为盲测**」。"""
    b = S.BlindSet(dev=["d1"], blind=["b1", "b2"])
    r = b.see_failure("b1")
    assert r["moved"] is True
    assert "b1" in b.dev and "b1" not in b.blind


def test_unseen_case_stays_blind() -> None:
    """★ 没看过的 ⇒ 仍在盲测集。"""
    b = S.BlindSet(blind=["b1"])
    b.see_failure("b9")
    assert b.blind == ["b1"]


#: ══ S14 叶子方法可增长 ═══════════════════════════════════════════════

def test_method_growth_is_allowed() -> None:
    """★★★ Q11 L212 逐字：「**允许有契约、可组合、可验证的叶子方法持续增长**」。"""
    p = S.method_growth_policy()
    assert p["allowed"] is True
    assert set(p["requirements"]) == {"contract", "composable", "verifiable"}


def test_leaf_method_needs_three_gates() -> None:
    """★ 三条门槛缺一不可。"""
    assert S.admit_leaf_method(has_contract=True, composable=True,
                               verifiable=True)["admitted"] is True
    assert S.admit_leaf_method(has_contract=True, composable=True,
                               verifiable=False)["admitted"] is False


def test_growth_is_not_rejected_for_being_many() -> None:
    """★★ **不因为"方法多了"就拒绝**（★ Q11 L212 逐字：
    「**排除一切方法增长不合理**」）。"""
    import inspect
    params = set(inspect.signature(S.admit_leaf_method).parameters)
    assert not any("count" in p or "total" in p for p in params), \
        "★★ 准入看的是「方法数」⇒ 违反 Q11 L212"


#: ══ S15 事务边界 ═════════════════════════════════════════════════════

def test_transaction_boundary_is_declared() -> None:
    """★★★ Q15 L314 逐字：「事务边界是「**自有副本＋已验证检查点＋提交清单**」，
    **不是 COM 撤销栈**」。"""
    t = B.transaction_boundary()
    assert set(t["boundary"]) == {"own_copy", "verified_checkpoint",
                                 "commit_manifest"}
    assert "com_undo_stack" in t["is_not"]
    assert t["has_global_transaction"] is False


def test_no_rollback_claim() -> None:
    """★★ Q15 L314 逐字：「失败分支保留，**不能冒称原地回滚成功**」。"""
    t = B.transaction_boundary()
    assert t["on_failure"] == "KEEP_FAILURE_BRANCH"
    assert t["rollback_claim"] is False


#: ══ S16 无人值守门槛 ═════════════════════════════════════════════════

def test_current_env_is_attended() -> None:
    """★★★ Q15 L317 逐字：「当前环境若达不到此门槛，**就只提供有人值守模式**，
    **不宣称无人值守安全**」。

    ★★ 判据：**`mode=attended` 且 `unattended_claim=False`**（★ 不许含糊）。
    """
    m = B.current_environment_mode()
    assert m["mode"] == "attended"
    assert m["unattended_claim"] is False
    assert m["missing"]


def test_prompt_isolation_does_not_count() -> None:
    """★★★ Q15 L317 逐字：「同一 Windows 用户下让 Agent 拥有任意脚本权限，
    再**靠提示词限制写入，不构成强隔离**」。"""
    m = B.AttendedMode(separate_execution_identity=True,
                       business_files_readonly=True,
                       os_level_isolation=True,
                       prompt_based_isolation_only=True).evaluate()
    assert m["mode"] == "attended", "★★ 只靠提示词也被当成隔离了"
    assert "no_prompt_based_isolation" in m["missing"]


def test_all_four_requirements_yield_unattended() -> None:
    """★ 四个门槛**全满足** ⇒ 可宣称无人值守。"""
    m = B.AttendedMode(separate_execution_identity=True,
                       business_files_readonly=True,
                       os_level_isolation=True,
                       prompt_based_isolation_only=False).evaluate()
    assert m["mode"] == "unattended" and m["unattended_claim"] is True


def test_no_account_or_registry_changes() -> None:
    """★ Q15 L319 逐字：「本轮**不创建账户、不更改注册表或系统策略**」。"""
    m = B.current_environment_mode()
    assert "不创建账户" in m["why"] or "注册表" in m["why"]


#: ══ S17 自动回收 ═════════════════════════════════════════════════════

def test_reclaim_own_instance_without_owner_docs() -> None:
    """★★ Q15 L315 逐字：「自动回收只能针对**可证明由本任务拥有、且没有业主文档**
    的实例」。"""
    r = B.can_reclaim(owned_by_this_task=True, has_owner_documents=False)
    assert r["reclaim"] is True


def test_reclaim_stops_for_not_owned() -> None:
    """★★ **无法证明自有 ⇒ 停住**。"""
    r = B.can_reclaim(owned_by_this_task=False, has_owner_documents=False)
    assert r["reclaim"] is False and r["action"] == "STOP"
    assert r["kill_process"] is False and r["click_save"] is False


def test_reclaim_stops_for_owner_documents() -> None:
    """★★ **有业主文档 ⇒ 停住**（★ 且**不点保存提示**）。"""
    r = B.can_reclaim(owned_by_this_task=True, has_owner_documents=True)
    assert r["reclaim"] is False and r["click_save"] is False


#: ══ S18 磁盘 ═════════════════════════════════════════════════════════

def test_disk_gate_refuses_when_tight() -> None:
    """★★★ Q15 L324 逐字：「**磁盘不足以容纳下一检查点、暂存及保留版本就拒绝开始**；
    **不自动清删证据或旧 CAD**」。"""
    r = B.disk_gate(free_bytes=100, needed_bytes=1000)
    assert r["ok"] is False and r["action"] == "REFUSE_START"
    assert r["auto_delete_evidence"] is False
    assert r["auto_delete_old_cad"] is False


def test_disk_gate_starts_when_roomy() -> None:
    """★ 空间够 ⇒ 开始。"""
    r = B.disk_gate(free_bytes=10**12, needed_bytes=1000)
    assert r["ok"] is True and r["action"] == "START"


def test_disk_gate_uses_safety_factor() -> None:
    """★ 有**安全系数**（★ 不是刚好够就开始）。"""
    r = B.disk_gate(free_bytes=1000, needed_bytes=1000, safety_factor=1.5)
    assert r["ok"] is False, "★ 刚好够也被放行了"


#: ══ S19 公网 ═════════════════════════════════════════════════════════

def test_execution_process_has_no_network() -> None:
    """★★★ Q15 L327 逐字：「**执行进程不访问公网**」。"""
    for actor in ("execution_process", "cad_session", "solver"):
        r = B.network_gate(actor)
        assert r["allowed"] is False
        assert r["code"] == "EXECUTION_NO_NETWORK"


def test_cloud_client_needs_classification_and_budget() -> None:
    """★★ Q15 L327 逐字：「网络、数据密级和预算**在进入云端客户端之前**控制」。"""
    assert B.network_gate("cloud_client")["code"] == "NOT_CLASSIFIED"
    assert B.network_gate("cloud_client",
                          data_classified=True)["code"] == "BUDGET_UNCHECKED"
    assert B.network_gate("cloud_client", data_classified=True,
                          budget_checked=True)["allowed"] is True


def test_unknown_actor_is_denied() -> None:
    """★ 未知角色 ⇒ 拒。"""
    assert B.network_gate("random_thing")["allowed"] is False


#: ══ ★★ 反向验证 Y1~Y10 ══════════════════════════════════════════════

def test_y1_llm_self_reported_human_is_rejected() -> None:
    """★★ **Y1**：**LLM 自报 `source=human`** ⇒ 必须**拒**。"""
    with pytest.raises(Q.QuestionError) as ei:
        Q.answer(_q(), 1, source=Q.SRC_HUMAN, channel_proof="")
    assert ei.value.code == "untrusted-human"


def test_y2_stale_revision_is_rejected() -> None:
    """★★ **Y2**：**旧 revision 补答** ⇒ 必须**拒**。"""
    with pytest.raises(Q.QuestionError) as ei:
        Q.apply_answer(_q(), 1, source=Q.SRC_HUMAN, carried_revision="old",
                       current_revision="new",
                       channel_proof="local_confirm_ui")
    assert ei.value.code == "stale-revision"


def test_y3_over_scope_is_rejected() -> None:
    """★★ **Y3**：**超上界** ⇒ 必须**拒**（★ 四种都试）。"""
    for kw in ({"self_made_parts": 11}, {"assembly_instances": 31},
               {"driven_dof": 2}, {"method_level_nodes": 101}):
        assert S.check_scope(**kw)["ok"] is False, kw


def test_y4_delivered_without_approval_is_rejected() -> None:
    """★★ **Y4**：**无人工批准就标 `DELIVERED`** ⇒ 必须**拒**。"""
    r = S.delivery_state(auto_done=True)
    assert r["state"] != S.DELIVERED


def test_y5_takeover_counted_as_autonomous_is_detected() -> None:
    """★★ **Y5**：**把人工接管算作自主完成** ⇒ 必须**检出**。"""
    t = S.TakeoverLedger(autonomous=3)
    t.record("t1", hand_built=True)
    #: ★ 突变体：把接管也算进自主
    mutated = t.autonomous + len(t.taken_over)
    assert t.autonomous_only != mutated, "★ 两者相等 ⇒ Y5 抓不到"
    assert t.autonomous_only == 3


def test_y6_fourth_patch_attempt_is_stopped() -> None:
    """★★ **Y6**：**同一假设第 4 次继续打补丁** ⇒ 必须**被停**。"""
    t = S.HypothesisTracker()
    for _ in range(3):
        t.record("h1", succeeded=False)
    r = t.record("h1", succeeded=False)
    assert r["stop_patching"] is True, "★★ 第 4 次还在打补丁"
    assert r["action"] == "RECHECK_CONTRACT_OR_ARCHITECTURE"


def test_y7_seen_blind_case_still_called_blind_is_detected() -> None:
    """★★ **Y7**：**把看过的盲题仍叫盲测** ⇒ 必须**检出**。"""
    b = S.BlindSet(blind=["b1"])
    b.see_failure("b1")
    assert "b1" not in b.blind, "★★ 看过的题还在盲测集里"


def test_y8_unattended_claim_without_identity_is_detected() -> None:
    """★★ **Y8**：**没有独立执行身份却宣称无人值守安全** ⇒ 必须**检出**。"""
    m = B.AttendedMode(separate_execution_identity=False,
                       business_files_readonly=True,
                       os_level_isolation=True,
                       prompt_based_isolation_only=False).evaluate()
    assert m["unattended_claim"] is False
    assert m["mode"] == "attended"


def test_y9_reclaiming_foreign_instance_is_stopped() -> None:
    """★★ **Y9**：**回收一个非自有实例** ⇒ 必须**停住**。"""
    r = B.can_reclaim(owned_by_this_task=False, has_owner_documents=True)
    assert r["action"] == "STOP"
    assert r["kill_process"] is False


def test_y10_starting_with_insufficient_disk_is_refused() -> None:
    """★★ **Y10**：**磁盘不足仍开始** ⇒ 必须**拒**。"""
    r = B.disk_gate(free_bytes=1, needed_bytes=10**9)
    assert r["action"] == "REFUSE_START"
    assert r["auto_delete_evidence"] is False
