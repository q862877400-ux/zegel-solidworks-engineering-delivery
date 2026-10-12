"""★ 规格 327 契约测试：发布清单 + 规则取证 + 落点持久化（T1~T15）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s327_manifest_rules_runs.py
# 定位:   规格 `specs/327-release-manifest-rules-and-runs` 的 T1~T15 契约测试
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q12（L214-231）逐字
#           ② 同文件 Q13（L233-259）· Q14（L261-297）逐字
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

from scripts.engineering import release_manifest as RM                   # noqa: E402
from scripts.engineering import rule_service as RS                       # noqa: E402
from scripts.engineering import runs as RN                               # noqa: E402

TEST_RUN = "_test-s327-run"


def _req(**kw) -> RS.RuleRequest:
    base = dict(rule_id="bolt-strength", rule_version=1,
                inputs=[{"name": "F", "value": 15000, "unit": "N",
                         "source": "需求"}],
                application_context={"use": "夹具", "date": "2026-10-12"},
                required_standard_editions=["GB/T 5796-2005"],
                evidence_bundle_ref="ev-1")
    base.update(kw)
    return RS.RuleRequest(**base)


#: ══ T1 同一发布清单 ══════════════════════════════════════════════════

def test_manifest_has_four_parts() -> None:
    """★★ Q12 L229 逐字：「**工具、元数据、方法和规则**构成同一发布清单」。"""
    assert set(RM.MANIFEST_PARTS) == {"tools", "metadata", "methods", "rules"}
    m = RM.build_manifest()
    assert not m.missing_parts()
    assert m.release_digest


def test_manifest_digest_is_composite() -> None:
    """★ 合成摘要 = **四部分的摘要**（★ 改任一部分 ⇒ 合成摘要变）。"""
    m = RM.build_manifest()
    parts = dict(m.parts)
    parts["tools"] = "different"
    assert RM._digest(parts) != m.release_digest


def test_manifest_validates_self_consistency() -> None:
    """★ 摘要必须**自洽**（★ 篡改 ⇒ 拒）。"""
    m = RM.build_manifest()
    m.parts["tools"] = "tampered"
    with pytest.raises(RM.ManifestError) as ei:
        m.validate()
    assert ei.value.code == "digest-mismatch"


def test_missing_part_rejected() -> None:
    """★ 缺一部分 ⇒ 拒。"""
    m = RM.ReleaseManifest(parts={"tools": "x"})
    with pytest.raises(RM.ManifestError) as ei:
        m.validate()
    assert ei.value.code == "missing-part"


#: ══ T2 原子切换 ══════════════════════════════════════════════════════

def test_publish_is_atomic() -> None:
    """★★ Q12 L229 逐字：「**原子切换**」⇒ 走临时名 + `replace`。"""
    m = RM.build_manifest()
    m.version = 9001
    p = RM.publish_manifest(m)
    assert p.is_file()
    #: ★ 临时文件**不该留下**
    assert not (p.parent / (".tmp-" + p.name)).exists()
    #: ★ 读回一致
    back = RM.load_manifest(9001)
    assert back.release_digest == m.release_digest
    p.unlink()


#: ══ T3 计划固定摘要 ══════════════════════════════════════════════════

def test_plan_binds_digest() -> None:
    """★★ Q12 L229 逐字：「**计划固定摘要**」。"""
    m = RM.build_manifest()
    bp = RM.bind_plan("p1", ["a", "b"], m)
    assert bp.release_digest == m.release_digest
    assert bp.check(m)["ok"] is True


def test_plan_rejected_after_manifest_change() -> None:
    """★★★ Q12 L229 逐字：「**升级不能悄悄重绑旧计划**」。

    ★★ 判据：清单变了 ⇒ **旧计划拒跑**（★ 不是"自动升级"）。
    """
    m = RM.build_manifest()
    bp = RM.bind_plan("p1", ["a"], m)
    m2 = RM.ReleaseManifest(version=2, parts=dict(m.parts))
    m2.parts["tools"] = "changed"
    m2.release_digest = RM._digest(m2.parts)
    r = bp.check(m2)
    assert r["ok"] is False
    assert r["code"] == "stale-plan"


def test_plan_without_digest_is_rejected() -> None:
    """★ 没绑摘要 ⇒ 也拒。"""
    m = RM.build_manifest()
    assert RM.BoundPlan(plan_id="x").check(m)["code"] == "stale-plan"


#: ══ T4 唯一裁决者 ════════════════════════════════════════════════════

def test_single_arbiter_per_property() -> None:
    """★★ Q12 L225 逐字：「**不能由不同消费者自行选边**」。"""
    r = RM.check_single_arbiter()
    assert r["ok"] is True and r["n"] > 0
    assert RM.arbiters_for("dof_verdict")


def test_second_arbiter_is_rejected() -> None:
    """★★★ 同一性质再登记**不同**的裁决者 ⇒ 拒。"""
    with pytest.raises(RM.ManifestError) as ei:
        RM.register_arbiter("dof_verdict", "some.other", "fn")
    assert ei.value.code == "multiple-arbiters"


def test_same_arbiter_reregistration_is_ok() -> None:
    """★ 登记**同一个** ⇒ 幂等。"""
    cur = RM.arbiters_for("dof_verdict")
    assert RM.register_arbiter("dof_verdict", cur[0], cur[1])["ok"] is True


#: ══ T5 RuleRequest ═══════════════════════════════════════════════════

def test_request_six_fields() -> None:
    """★★ Q13 L239-243 逐字给的 `RuleRequest` 字段。"""
    assert len(RS.REQUEST_FIELDS) == 6
    assert _req().missing() == []


def test_request_inputs_need_unit_and_source() -> None:
    """★★ Q13 L240 逐字：「带**单位、来源**、必要时带区间的数据」。"""
    with pytest.raises(RS.RuleError) as ei:
        _req(inputs=[{"name": "F", "value": 1}]).validate()
    assert ei.value.code == "missing-field"


def test_request_missing_context_rejected() -> None:
    """★ 缺 `application_context` ⇒ 拒（★ Q13 L241：「产品用途、工况、司法辖区…」）。"""
    with pytest.raises(RS.RuleError) as ei:
        _req(application_context={}).validate()
    assert ei.value.code == "missing-field"


#: ══ T6 RuleResult ════════════════════════════════════════════════════

def test_result_eight_fields() -> None:
    """★★ Q13 L245-251 逐字给的 `RuleResult` 字段（★ 含 `rule_code_digest`）。"""
    assert len(RS.RESULT_FIELDS) == 8
    for f in ("verdict", "outputs", "checked_preconditions",
              "failed_obligations", "citations", "authority_status",
              "missing_evidence", "rule_code_digest"):
        assert f in RS.RESULT_FIELDS


def test_four_verdicts() -> None:
    """★★ Q13 L245 逐字给的四档 verdict。"""
    assert set(RS.VERDICTS) == {"PASS", "FAIL", "INDETERMINATE",
                                "NOT_APPLICABLE"}


def test_result_has_code_digest() -> None:
    """★ `rule_code_digest` 是**实现的摘要**（★ 与 citations **分开**）。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=True,
                         authority_status={"source": RS.SRC_OFFICIAL})
    assert r.rule_code_digest, "★ 没有 rule_code_digest"
    #: ★★ 两者**是不同字段**（★ Q13 L235「规则实现与依据必须分开」）
    assert "citations" in RS.RESULT_FIELDS
    assert "rule_code_digest" in RS.RESULT_FIELDS


#: ══ T7 公式与依据分开 ════════════════════════════════════════════════

def test_formula_ok_but_not_applicable() -> None:
    """★★★ Q13 L235 逐字：「**一个公式能运行，不表示它对当前材料、工况和
    标准版本适用**」。

    ★★ 判据：`formula_ok=True` 而 `applicability_ok=False`
      ⇒ **`NOT_APPLICABLE`**（★ **不是** `PASS`）。
    """
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=False,
                         authority_status={"source": RS.SRC_OFFICIAL})
    assert r.verdict == RS.NOT_APPLICABLE, "★★ 能运行被当成适用了！"
    assert r.applicability["ok"] is False


def test_formula_fail_is_fail() -> None:
    """★ 公式跑不通 ⇒ `FAIL`。"""
    r = RS.evaluate_rule(_req(), formula_ok=False, applicability_ok=True,
                         authority_status={"source": RS.SRC_OFFICIAL})
    assert r.verdict == RS.FAIL


def test_both_ok_is_pass() -> None:
    """★ 都过 ⇒ `PASS`。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=True,
                         authority_status={"source": RS.SRC_OFFICIAL})
    assert r.verdict == RS.PASS


def test_result_separates_code_from_citations() -> None:
    """★★ 结果里**实现摘要**与**依据**是两个**独立**字段。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=True,
                         authority_status={"source": RS.SRC_OFFICIAL,
                                           "edition": "2005"})
    d = r.to_dict()
    assert "rule_code_digest" in d and "citations" in d
    assert d["rule_code_digest"] != str(d["citations"])


#: ══ T8 效力来源 ══════════════════════════════════════════════════════

def test_summary_only_source_is_indeterminate() -> None:
    """★★★ Q13 L255 逐字：「**效力来源不可只引用检索引擎生成的摘要**」。"""
    r = RS.check_authority({"source": RS.SRC_SUMMARY})
    assert r["ok"] is False
    assert r["verdict"] == RS.INDETERMINATE


def test_official_source_is_ok() -> None:
    """★ 官方状态记录 ⇒ 可用。"""
    assert RS.check_authority({"source": RS.SRC_OFFICIAL})["ok"] is True


def test_contract_source_is_ok() -> None:
    """★ 合同指定 ⇒ 可用（★ Q13 L255：「合同指定版本」）。"""
    assert RS.check_authority({"source": RS.SRC_CONTRACT})["ok"] is True


def test_unknown_source_is_rejected() -> None:
    """★ 未知来源 ⇒ 拒。"""
    assert RS.check_authority({"source": "made_up"})["ok"] is False


#: ══ T9 30 天新鲜度 ═══════════════════════════════════════════════════

def test_thirty_day_freshness() -> None:
    """★★ Q13 L257 逐字：「**交付日前 30 天内**的官方状态记录」。"""
    assert RS.FRESHNESS_DAYS == 30
    assert RS.check_freshness("2026-10-01", today="2026-10-12")["stale"] is False
    assert RS.check_freshness("2026-09-01", today="2026-10-12")["stale"] is True


def test_stale_authority_yields_indeterminate() -> None:
    """★ 效力记录 stale ⇒ 结果 `INDETERMINATE`。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=True,
                         authority_status={"source": RS.SRC_OFFICIAL},
                         checked_on="2026-01-01", today="2026-10-12")
    assert r.verdict == RS.INDETERMINATE


def test_cache_cannot_claim_today() -> None:
    """★★ Q13 L257 逐字：「**离线缓存可按其快照日期使用，但不能宣称已经
    核对到今天**」。"""
    f = RS.check_freshness("2026-08-01", today="2026-10-12")
    assert f["stale"] is True
    assert f["age_days"] > 30


#: ══ T10 runs 目录结构 ════════════════════════════════════════════════

def test_seven_subdirs() -> None:
    """★★ Q14 L271-281 逐字给的**七个子目录**。"""
    assert len(RN.RUN_SUBDIRS) == 7
    assert set(RN.RUN_SUBDIRS) == {"plans", "interfaces", "questions",
                                   "events", "attempts", "checkpoints",
                                   "commits"}


def test_init_run_creates_all() -> None:
    """★ 建运行目录 ⇒ 七个都在。"""
    RN.init_run(TEST_RUN)
    r = RN.check_structure(TEST_RUN)
    assert r["ok"] is True and not r["missing"]


def test_unknown_subdir_rejected() -> None:
    """★ 未知子目录 ⇒ 拒。"""
    with pytest.raises(RN.RunError) as ei:
        RN.write_revision(TEST_RUN, "nope", "r1", {})
    assert ei.value.code == "missing-subdir"


#: ══ T11/T12 原子写 + 不覆盖 ══════════════════════════════════════════

def test_atomic_write_uses_temp_then_replace() -> None:
    """★★ Q14 L283 逐字：「**以同卷原子重命名发布**新的提交清单」。"""
    p = RN.run_dir(TEST_RUN) / "plans" / "rev-atomic.json"
    r = RN.atomic_write(p, {"a": 1})
    assert r["atomic"] is True
    assert not (p.parent / (".tmp-" + p.name)).exists()


def test_old_revision_is_not_overwritten() -> None:
    """★★★ Q14 L283 逐字：「**旧版本不覆盖、不删除**」。"""
    RN.write_revision(TEST_RUN, "plans", "rev-keep", {"v": 1})
    with pytest.raises(RN.RunError) as ei:
        RN.write_revision(TEST_RUN, "plans", "rev-keep", {"v": 2})
    assert ei.value.code == "overwrite"
    #: ★ 旧内容**还在**
    import json                                                         # noqa: PLC0415
    p = RN.run_dir(TEST_RUN) / "plans" / "rev-keep.json"
    assert json.loads(p.read_text(encoding="utf-8"))["v"] == 1


#: ══ T13 孤立暂存不算完成 ═════════════════════════════════════════════

def test_orphan_is_not_complete() -> None:
    """★★★ Q14 L283 逐字：「**孤立的暂存文件保留，但没有提交记录就不能
    自动视作完成**」。"""
    RN.write_revision(TEST_RUN, "plans", "rev-orphan", {"x": 1})
    r = RN.is_complete(TEST_RUN, "plans/rev-orphan.json")
    assert r["on_disk"] is True
    assert r["referenced"] is False
    assert r["complete"] is False, "★★ 孤立暂存被当成完成了！"


def test_referenced_artifact_is_complete() -> None:
    """★ 被提交引用 ⇒ 算完成。"""
    RN.write_revision(TEST_RUN, "plans", "rev-ref", {"x": 1})
    RN.commit(TEST_RUN, 1, ["plans/rev-ref.json"], note="ok")
    r = RN.is_complete(TEST_RUN, "plans/rev-ref.json")
    assert r["complete"] is True


def test_commit_chain_is_the_authority() -> None:
    """★ Q14 L283 逐字：「唯一权威是**完整的提交链**」。"""
    chain = RN.load_commits(TEST_RUN)
    assert chain and chain[0]["sequence"] == 1


#: ══ T14 四类持久化 ═══════════════════════════════════════════════════

def test_four_persisted_kinds() -> None:
    """★★ Q14 L297 逐字：「**任务树、接口、证据、未决问题四类均持久化**」。"""
    assert set(RN.PERSISTED_KINDS) == {"task_tree", "interfaces", "evidence",
                                       "open_questions"}


def test_rebuildable_kinds_are_not_persisted() -> None:
    """★★ Q14 L297 逐字：「可重建的是**派生展示、调度就绪队列和 COM 对象**」。"""
    assert set(RN.REBUILDABLE) == {"derived_views", "scheduler_ready_queue",
                                   "com_objects"}
    with pytest.raises(RN.RunError):
        RN.persist(TEST_RUN, "derived_views", "r1", {})


def test_persist_all_four() -> None:
    """★ 四类都能持久化。"""
    for k in RN.PERSISTED_KINDS:
        RN.persist(TEST_RUN, k, "p-rev", {"kind": k})
    r = RN.check_persistence(TEST_RUN)
    assert r["ok"] is True, r


#: ══ T15 B 侧薄编排 ═══════════════════════════════════════════════════

def test_thin_orchestrator_reuses_core() -> None:
    """★★ Q14 L265 逐字：「后续 A 只能做**同一核心的另一个适配器**」。"""
    r = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:4]), builds=[])
    assert r["ok"] is True and r["reused_n"] >= 3


def test_thin_orchestrator_rejects_second_loop() -> None:
    """★★★ Q14 L265 逐字：「**不先启用其 UI 和另一套规划循环**」。"""
    r = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:4]),
                             builds=["second_planning_loop"])
    assert r["ok"] is False
    assert r["forbidden_built"] == ["second_planning_loop"]


def test_thin_orchestrator_rejects_second_rule_system() -> None:
    """★★ **第二套规则体系** ⇒ 也拒。"""
    r = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:4]),
                             builds=["second_rule_system"])
    assert r["ok"] is False


def test_thin_orchestrator_needs_three_core_modules() -> None:
    """★ 复用**少于 3 个**核心模块 ⇒ 不算"复用同一核心"。"""
    r = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:2]), builds=[])
    assert r["ok"] is False


def test_shared_core_modules_exist() -> None:
    """★ 共享核心**都在**。"""
    assert RN.core_status()["ok"] is True


#: ══ ★★ 反向验证 Z1~Z6 ═══════════════════════════════════════════════

def test_z1_stale_plan_must_be_rejected() -> None:
    """★★ **Z1**：**清单变了却让旧计划跑** ⇒ 必须**拒**。"""
    m = RM.build_manifest()
    bp = RM.bind_plan("z1", ["a"], m)
    m2 = RM.ReleaseManifest(version=9, parts=dict(m.parts))
    m2.parts["rules"] = "changed"
    m2.release_digest = RM._digest(m2.parts)
    assert bp.check(m2)["ok"] is False


def test_z2_summary_only_must_be_indeterminate() -> None:
    """★★ **Z2**：**只引检索摘要当效力来源** ⇒ 必须 **`INDETERMINATE`**。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=True,
                         authority_status={"source": RS.SRC_SUMMARY})
    assert r.verdict == RS.INDETERMINATE


def test_z3_formula_pass_alone_is_not_enough() -> None:
    """★★ **Z3**：**公式跑通就判 PASS**（不看适用性）⇒ 必须**检出**。"""
    r = RS.evaluate_rule(_req(), formula_ok=True, applicability_ok=False,
                         authority_status={"source": RS.SRC_OFFICIAL})
    assert r.verdict != RS.PASS, "★★ 只看公式就放行了"


def test_z4_overwriting_revision_is_detected() -> None:
    """★★ **Z4**：**直接覆盖旧 revision** ⇒ 必须**检出**。"""
    RN.write_revision(TEST_RUN, "plans", "z4-rev", {"v": 1})
    with pytest.raises(RN.RunError) as ei:
        RN.write_revision(TEST_RUN, "plans", "z4-rev", {"v": 2})
    assert ei.value.code == "overwrite"


def test_z5_orphan_as_complete_is_detected() -> None:
    """★★ **Z5**：**把孤立暂存当完成** ⇒ 必须**检出**。"""
    RN.write_revision(TEST_RUN, "interfaces", "z5-rev", {"x": 1})
    assert RN.is_complete(TEST_RUN, "interfaces/z5-rev.json")["complete"] is False


def test_z6_second_state_system_is_detected() -> None:
    """★★ **Z6**：**B 侧入口另建一套状态** ⇒ 必须**检出**。"""
    r = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:4]),
                             builds=["second_state_system"])
    assert r["ok"] is False
    assert "second_state_system" in r["forbidden_built"]
