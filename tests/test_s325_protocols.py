"""★ 规格 325 契约测试：四类协议 + check_ref + 三态决策（Q1/Q5 的 R1~R10）。

★★ 含**反向验证**（★ 规格 §5 的 X1~X8）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s325_protocols.py
# 定位:   规格 `specs/325-declarative-protocols-and-decisions` 的 R1~R10 契约测试
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q1（L10-34）逐字
#           ② 同文件 Q5（L59-94）逐字
#           ③ `metadata/protocols/*.yaml`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import decisions as D                          # noqa: E402
from scripts.engineering import protocols as P                           # noqa: E402


def _dec(**kw) -> D.Decision:
    base = dict(proposer=D.PROPOSER_LLM, input_version="r1",
                alternatives=["A", "B"], visible_rationale="按 8mm",
                basis=["GB/T 5796"], affected_nodes=["上箱体"])
    base.update(kw)
    return D.make_decision(**base)


#: ══ R1 四类协议 ══════════════════════════════════════════════════════

def test_four_protocols_exist() -> None:
    """★★ Q1 L28 逐字：「首先抽取**需求**、方案门槛、布局、失败转移**四类协议**」。"""
    assert len(P.REQUIRED_PROTOCOLS) == 4
    allp = P.load_all()
    assert set(allp) == set(P.REQUIRED_PROTOCOLS)


def test_protocol_files_are_versioned_yaml() -> None:
    """★★ Q5 L61 逐字：「选择**版本化 YAML/JSON 协议**」。"""
    for name in P.REQUIRED_PROTOCOLS:
        f = P.PROTOCOL_DIR / ("%s.yaml" % name)
        assert f.is_file(), "★ 缺 %s" % f
        pr = P.load_protocol(name)
        assert isinstance(pr.version, int) and pr.version >= 1


def test_layout_matches_q5_verbatim() -> None:
    """★★ **`layout.yaml` 逐字承 Q5 的样例**（`rigid_mechanism_layout`）。"""
    pr = P.load_protocol("layout")
    assert pr.protocol_id == "rigid_mechanism_layout"
    assert pr.entry_check == "requires_supported_rigid_body_motion"
    assert pr.inputs_schema == "LayoutInputs@1"
    assert pr.outputs_schema == "LayoutResult@1"
    assert pr.required_inputs == ["target_motion", "installation_envelope",
                                  "load_cases", "interface_constraints"]
    assert pr.on_failure["missing_critical_input"] == "WAITING_INPUT"
    assert pr.source_refs == ["front_end_workflow", "scheme_selection"]


#: ══ R2 五要素 ════════════════════════════════════════════════════════

def test_every_protocol_has_five_elements() -> None:
    """★★ Q1 L28 逐字：「每条补齐**输入、输出、触发条件、检查函数和失败状态**」。"""
    for name in P.REQUIRED_PROTOCOLS:
        pr = P.load_protocol(name)
        assert pr.required_inputs, "★ %s 缺输入" % name
        assert pr.outputs, "★ %s 缺输出" % name
        assert pr.entry_check, "★ %s 缺触发条件" % name
        assert pr.checks, "★ %s 缺检查函数" % name
        assert pr.on_failure, "★ %s 缺失败状态" % name
        assert pr.missing_fields() == []


#: ══ R3 check_ref 解析 ════════════════════════════════════════════════

def test_all_check_refs_resolve() -> None:
    """★★★ Q5 L88 逐字：「`check_ref` **必须解析到已登记的代码**」。"""
    v = P.validate_all()
    assert v["ok"] is True, v
    for r in v["protocols"]:
        assert r["unresolved"] == [], \
            "★ %s 有未解析的 check_ref：%s" % (r["protocol_id"], r["unresolved"])


def test_resolve_returns_real_function() -> None:
    """★ 解析结果**真的能 import**（★ 不是只查表）。"""
    r = P.resolve_check_ref("kinematic_model_supported@1")
    assert r.resolved is True
    assert r.module and r.function


def test_unregistered_check_ref_is_rejected() -> None:
    """★★ R10 / Q5 L90：**新 `check_ref` 无实现 ⇒ 拒**
    （★ 「不能假装只改 YAML 就能获得新能力」）。"""
    r = P.resolve_check_ref("totally_new_capability@1")
    assert r.resolved is False
    assert "已登记" in r.reason


def test_registered_but_missing_function_is_rejected() -> None:
    """★★ 只登记**不实现** ⇒ 也拒（★ 这是 Q5 L90 的关键）。"""
    P.CHECK_REGISTRY["ghost_check@1"] = ("engineering.protocols",
                                         "no_such_function_xyz")
    try:
        r = P.resolve_check_ref("ghost_check@1")
        assert r.resolved is False
        assert "没有" in r.reason
    finally:
        del P.CHECK_REGISTRY["ghost_check@1"]


#: ══ R4 8 项必设检查 ══════════════════════════════════════════════════

def test_eight_required_checks() -> None:
    """★★ Q5 L92 逐字给的必设检查 —— ★ 本规格做 **8 项协议检查**。"""
    assert len(P.REQUIRED_CHECKS) == 8
    #: ★ 第 9 项（负例与突变测试）在**测试**层面 —— ★ 诚实标注
    assert P.NINTH_CHECK_IS_TEST == "negative_and_mutation_tests"


def test_required_checks_all_pass() -> None:
    """★ 四份协议的 8 项检查**都过**。"""
    for name in P.REQUIRED_PROTOCOLS:
        rc = P.run_required_checks(P.load_protocol(name))
        assert rc["ok"] is True, (name, rc["failed"])


def test_required_checks_cover_q5_list() -> None:
    """★ 8 项**逐字对应** Q5 的清单。"""
    for k in ("schema", "ref_resolution", "unit_and_type", "reachable_state",
              "forbidden_covered", "consumer_compatible", "version_dependency",
              "affected_invalidation"):
        assert k in P.REQUIRED_CHECKS, "★ 缺 %s" % k


#: ══ R5 改一处 ⇒ 重生成三视图 ═════════════════════════════════════════

def test_regenerate_produces_three_views() -> None:
    """★★ Q5 L90 逐字：「改一处源数据，**重新生成文档、提示与目录**」。"""
    rg = P.regenerate(P.load_protocol("layout"))
    assert rg["document"] and rg["prompt"] and rg["catalog"]
    assert rg["digest"]


def test_regenerate_all_four() -> None:
    """★ 四份都能重生成。"""
    assert len(P.regenerate_all()) == 4


def test_prompt_reminds_proposal_only() -> None:
    """★★ 生成的**提示**必须提醒「你的输出只是 `Proposal`」。"""
    rg = P.regenerate(P.load_protocol("scheme_gate"))
    assert "Proposal" in rg["prompt"]
    assert "Validated" in rg["prompt"]


#: ══ R6 decision_id 五要素 ════════════════════════════════════════════

def test_decision_has_five_elements() -> None:
    """★★ Q1 L24 逐字：「记录**输入版本、备选方案、可见理由、依据和受影响节点**」。"""
    d = _dec()
    for f in ("input_version", "alternatives", "visible_rationale", "basis",
              "affected_nodes"):
        assert getattr(d, f), "★ 缺 %s" % f
    assert d.decision_id.startswith("dec-")


def test_decision_id_is_deterministic() -> None:
    """★ `decision_id` 是**五要素的摘要** ⇒ 同输入同 id（★ 可复核）。"""
    assert _dec().decision_id == _dec().decision_id


def test_decision_id_changes_with_input_version() -> None:
    """★ 输入版本变了 ⇒ id 必须变（★ 追责要能区分版本）。"""
    assert _dec(input_version="r1").decision_id != \
        _dec(input_version="r2").decision_id


def test_missing_element_is_rejected() -> None:
    """★ 缺五要素 ⇒ 拒。"""
    with pytest.raises(D.DecisionError) as ei:
        D.make_decision(proposer=D.PROPOSER_LLM, input_version="r1",
                        alternatives=[], visible_rationale="x", basis=["b"],
                        affected_nodes=["n"])
    assert ei.value.code == "missing-field"


def test_hidden_cot_is_rejected() -> None:
    """★★ Q1 L24 逐字：「**无需记录模型隐藏思维链**」⇒ ★ **收进来就拒**。"""
    d = _dec()
    d.hidden_cot = "模型心里想的是……"
    with pytest.raises(D.DecisionError) as ei:
        d.validate()
    assert ei.value.code == "hidden-cot"


def test_decision_to_dict_has_no_cot() -> None:
    """★ 输出里**没有**思维链字段。"""
    assert "hidden_cot" not in _dec().to_dict()


#: ══ R7 三态 ══════════════════════════════════════════════════════════

def test_three_states() -> None:
    """★★ Q1 L22 逐字：「`Proposal` / `Validated` / `Approved`」。"""
    assert D.STATES == ("Proposal", "Validated", "Approved")


def test_starts_as_proposal() -> None:
    """★★ 起始态**永远是 `Proposal`**（★ 无论谁提的）。"""
    for pr in D.PROPOSERS:
        assert _dec(proposer=pr).state == D.PROPOSAL


def test_validated_requires_code_verdict() -> None:
    """★★ 进 `Validated` **必须带代码裁决结果**。"""
    d = _dec()
    p = D.promote(d, D.VALIDATED, by=D.PROPOSER_CODE)
    assert p.ok is False
    assert "代码裁决" in p.detail


def test_validated_requires_pass_verdict() -> None:
    """★ 裁决**不是 PASS** ⇒ 也不给升。"""
    d = _dec()
    p = D.promote(d, D.VALIDATED, by=D.PROPOSER_CODE,
                  code_verdict={"verdict": "FAIL"})
    assert p.ok is False


def test_happy_path_proposal_to_validated_to_approved() -> None:
    """★ 正路：LLM 提案 → 代码裁决 ⇒ `Validated` → 人 ⇒ `Approved`。"""
    d = _dec()
    assert D.promote(d, D.VALIDATED, by=D.PROPOSER_CODE,
                     code_verdict={"verdict": "PASS"}).ok
    assert d.state == D.VALIDATED
    assert D.promote(d, D.APPROVED, by=D.PROPOSER_HUMAN).ok
    assert d.state == D.APPROVED


#: ══ R9 同错两次 ⇒ 诊断 ══════════════════════════════════════════════

def test_same_error_twice_triggers() -> None:
    """★★ Q1 L32 逐字：「「**同错误两次停下**」转成**诊断触发**」。"""
    t = D.SameErrorTrigger()
    assert t.observe("E1")["triggered"] is False
    assert t.observe("E1")["triggered"] is True


def test_trigger_action_is_diagnosis() -> None:
    """★ 触发后的动作是 `DIAGNOSIS_REQUIRED`。"""
    t = D.SameErrorTrigger()
    t.observe("E1")
    assert t.observe("E1")["action"] == "DIAGNOSIS_REQUIRED"


def test_no_root_cause_in_output() -> None:
    """★★★ Q1 L32 逐字：「**不转成「一定是方法选错」的根因判定**」。

    ★★ 判据是**结构性**的：`to_dict()` 里**根本没有** `root_cause` 这个键。
    """
    t = D.SameErrorTrigger()
    for _ in range(3):
        t.observe("E1")
    assert "root_cause" not in t.to_dict()
    assert t.observe("E1")["root_cause"] is None


def test_different_errors_do_not_trigger() -> None:
    """★ 不同错误码**不**触发（★ 判据是"**同**错"）。"""
    t = D.SameErrorTrigger()
    t.observe("E1")
    t.observe("E2")
    assert t.observe("E3")["triggered"] is False


#: ══ R8 字段门禁 ══════════════════════════════════════════════════════

def test_field_gate_waiting_input() -> None:
    """★★ Q1 L31 逐字：「「缺需求先问」转成**字段门禁**」。"""
    pr = P.load_protocol("requirement")
    g = P.field_gate(pr, {"requirement_text": "打孔"})
    assert g["state"] == "WAITING_INPUT"
    assert g["missing"] == ["deliverable_kind"]
    assert g["questions"]


def test_field_gate_ready_when_complete() -> None:
    """★ 齐了 ⇒ `READY_FOR_REVIEW`。"""
    pr = P.load_protocol("requirement")
    g = P.field_gate(pr, {"requirement_text": "打孔",
                          "deliverable_kind": "part"})
    assert g["state"] == "READY_FOR_REVIEW"


def test_no_worst_case_fallback() -> None:
    """★★★ Q1 L31 逐字：「**不存在载荷上界时，不自动采用所谓最坏工况**」。

    ★ 判据：协议里**显式列了 `forbidden_defaults`**，
      且给了 `worst_case_load` 也**照样** `WAITING_INPUT`。
    """
    pr = P.load_protocol("requirement")
    assert "worst_case_load" in (pr.extra.get("forbidden_defaults") or [])
    g = P.field_gate(pr, {"requirement_text": "打孔",
                          "worst_case_load": "999kN"})
    assert g["state"] == "WAITING_INPUT", "★★ 最坏工况被当默认值顶替了！"
    assert "worst_case_load" in g["used_forbidden_defaults"]


#: ══ ★★ 反向验证 X1~X8 ═══════════════════════════════════════════════

def test_x1_proposal_cannot_jump_to_approved() -> None:
    """★★ **X1**：**让 `Proposal` 直接晋升 `Approved`** ⇒ 必须**失败**。"""
    d = _dec()
    p = D.promote(d, D.APPROVED, by=D.PROPOSER_HUMAN)
    assert p.ok is False
    assert p.code == "illegal-transition"
    assert d.state == D.PROPOSAL, "★ 态被改了"


def test_x2_llm_cannot_self_validate() -> None:
    """★★ **X2**：**让 LLM 自评就能 `Validated`** ⇒ 必须**失败**。"""
    d = _dec()
    #: ★ 即使带一个 PASS 的"自评"，LLM 也不许
    p = D.promote(d, D.VALIDATED, by=D.PROPOSER_LLM,
                  code_verdict={"verdict": "PASS"})
    assert p.ok is False
    assert p.code == "not-authorized"
    assert d.state == D.PROPOSAL


def test_x3_check_ref_to_missing_function_is_rejected() -> None:
    """★★ **X3**：**把 `check_ref` 指向不存在的函数** ⇒ 必须**拒**。"""
    P.CHECK_REGISTRY["bogus@1"] = ("engineering.protocols", "nope_nope")
    try:
        assert P.resolve_check_ref("bogus@1").resolved is False
    finally:
        del P.CHECK_REGISTRY["bogus@1"]
    #: ★ 且**整份协议**会被判不 ok
    pr = P.load_protocol("layout")
    pr.checks = list(pr.checks) + ["bogus@1"]
    v = P.validate_protocol(pr)
    assert v["ok"] is False
    assert "bogus@1" in v["unresolved"]


def test_x4_eval_in_protocol_is_detected() -> None:
    """★★ **X4**：**在协议里塞一段 `eval` 代码** ⇒ 必须**检出**。"""
    pr = P.load_protocol("layout")
    pr.extra["sneaky"] = "eval('__import__(\"os\").system(\"x\")')"
    v = P.validate_protocol(pr)
    assert v["ok"] is False
    assert v["forbidden"], "★★ eval 没被检出"


def test_x4b_python_code_block_is_detected() -> None:
    """★ X4 同族：**LLM 生成的代码块**也要检出。"""
    pr = P.load_protocol("layout")
    pr.extra["sneaky"] = "```python\nimport os\n```"
    assert P.validate_protocol(pr)["forbidden"]


def test_x5_yaml_only_cannot_add_capability() -> None:
    """★★ **X5**：**只改 YAML 加一个新检查** ⇒ 必须**拒**（★ 无实现）。"""
    pr = P.load_protocol("requirement")
    pr.checks = list(pr.checks) + ["brand_new_check@1"]
    v = P.validate_protocol(pr)
    assert v["ok"] is False
    assert "brand_new_check@1" in v["unresolved"]


def test_x6_missing_required_field_stops() -> None:
    """★★ **X6**：**缺必填字段却继续** ⇒ 必须 `WAITING_INPUT`。"""
    pr = P.load_protocol("scheme_gate")
    g = P.field_gate(pr, {})
    assert g["state"] == "WAITING_INPUT"
    assert g["ok"] is False


def test_x7_repeated_error_must_trigger_diagnosis() -> None:
    """★★ **X7**：**两次同错却继续重试** ⇒ 必须**触发诊断**。"""
    out = D.check_same_error(["E1", "E1"])
    assert out["triggered"] == ["E1"]
    assert out["last"]["action"] == "DIAGNOSIS_REQUIRED"


def test_x8_worst_case_as_default_is_detected() -> None:
    """★★ **X8**：**把「最坏工况」当默认值填进去** ⇒ 必须**检出**。"""
    pr = P.load_protocol("requirement")
    g = P.field_gate(pr, {"requirement_text": "x", "deliverable_kind": "part",
                          "worst_case_load": "999kN"})
    #: ★ 齐了也能跑，★ 但**如实报出用了禁用默认值**
    assert g["used_forbidden_defaults"] == ["worst_case_load"]
    #: ★ 而缺必填时，**它不能顶替**
    g2 = P.field_gate(pr, {"worst_case_load": "999kN"})
    assert g2["state"] == "WAITING_INPUT"
    assert "deliverable_kind" in g2["missing"]


#: ══ ★ 与既有资产的一致性 ════════════════════════════════════════════

def test_failure_codes_align_with_design_ir() -> None:
    """★ 协议的失败状态码**与 `design_ir.IR_CODES` 同族**（★ 不另造一套）。"""
    from scripts.engineering import design_ir as DI
    pr = P.load_protocol("requirement")
    assert pr.on_failure["missing_critical_input"] == DI.WAITING_INPUT
    assert pr.on_failure["out_of_scope"] == DI.REJECTED_OUT_OF_SCOPE


def test_protocol_digest_changes_with_content() -> None:
    """★ 协议摘要**随内容变**（★ R5 用它判"源数据改了没有"）。"""
    a = P.load_protocol("layout")
    b = P.load_protocol("layout")
    assert a.digest() == b.digest()
    b.version = 2
    assert a.digest() != b.digest()
