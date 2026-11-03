"""★ EC04 判据 —— 租约 / 围栏 / 版本绑定 / 证据链 / 独立验收 / 恢复。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/jobs.py`（★ EC04 的作业与证据层）
#         `specs/306-ec04-safe-jobs-and-evidence/spec.md`（★ FR · V）
# 定位:   ★ EC04 的判据（★ 逐字承计划 §5 EC04 的「验收」）。
# 官方依据: 不适用（本仓的作业编排层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import jobs as J


# ══════════════════════════════════════════════════════════════════════
# V1 · Job 状态机（★ 含「不重试」的结构性保证）
# ══════════════════════════════════════════════════════════════════════

def test_v1_all_nine_job_states_exist():
    """★★ V1：★ **九个状态必须齐**（★ 逐字承 EC04-T01）。

    ★★ 2026-10-12 更新（★ 规格 318 · E4）：★ **多出第 10 档 `unknown_effect`**。
      ★ 依据：外部方案阶段 3 逐字要求「单写者所有权与 **`UNKNOWN_EFFECT` 状态**」。
      ★★ 与 `uncertain` 的分工（★ **两个都要，不是替代**）：
        · `uncertain`      说的是「**调用**结果不明」⇒ 可以靠**回读**补救
        · `unknown_effect` 说的是「**这个工具到底写没写**都不知道」
          ⇒ ★ **连该回读什么都不知道** ⇒ 只能去 `blocked`/`failed`
    ★ 判据仍是「**九档必须齐**」—— ★ 只是现在**多了第 10 档**。
    """
    nine = {"queued", "planned", "approved", "running", "uncertain",
            "validating", "blocked", "completed", "failed"}
    #: ★ 九档必须齐（★ 原判据不动）
    assert nine <= set(J.JobState.ALL), (
        "★ 状态不齐：%r" % (J.JobState.ALL,))
    #: ★ 第 10 档（★ 规格 318 加的）
    assert J.JobState.UNKNOWN_EFFECT in J.JobState.ALL
    assert set(J.JobState.ALL) == nine | {"unknown_effect"}, (
        "★ 状态集与预期不符：%r" % (J.JobState.ALL,))
    #: ★★ 且它**绝不重试**（★ 与 `uncertain` 同族但更严）
    assert J.JobState.UNKNOWN_EFFECT in J.JobState.NEVER_RETRY_FROM


def test_v1_uncertain_cannot_go_back_to_running():
    """★★★★★ V1：★ **`uncertain` 不能回 `running`**（★ 「不重试」的**结构性保证**）。

    ★★ 依据（★ 计划验收逐字）：★「★ **超时未回读不重试**」。
    ★★★ **⇒ 不靠纪律，靠状态机** —— ★ 没有那条迁移，★ 想重试也走不通 ✓
    """
    allowed = J.JobState.TRANSITIONS[J.JobState.UNCERTAIN]
    assert J.JobState.RUNNING not in allowed, (
        "★★★ `uncertain` 可以回 `running` ⇒ ★ **重试在状态机上是通的**（★ 违反验收）")
    #: ★★ 但**必须**能去 `validating`（★ 那是「先回读」）
    assert J.JobState.VALIDATING in allowed, (
        "★ `uncertain` 不能去 `validating` ⇒ ★ 连回读都做不了")
    #: ★★ 且**显式声明**绝不从它重试
    assert J.JobState.UNCERTAIN in J.JobState.NEVER_RETRY_FROM


def test_v1_terminal_states_are_terminal():
    """★★ V1：★ **终态不可迁移**（★ 否则「完成」还能再改）。"""
    for st in J.JobState.TERMINAL:
        assert J.JobState.TRANSITIONS[st] == (), "★★ `%s` 不是终态" % st


def test_v1_no_state_transitions_to_itself():
    """★★ V1：★ **没有自环**（★ 自环 = 可以无限重入）。"""
    for st, targets in J.JobState.TRANSITIONS.items():
        assert st not in targets, "★★ `%s` 有自环 ⇒ ★ 可以无限重进" % st


# ══════════════════════════════════════════════════════════════════════
# V2 · 双客户端争抢只能一个得执行权
# ══════════════════════════════════════════════════════════════════════

def test_v2_only_one_holder_at_a_time():
    """★★★★★ V2：★ **双客户端争抢 ⇒ 只能一个得到执行权**（★ 逐字承计划验收）。"""
    lease = J.NodeLease()
    a = lease.acquire("ds h", now=1000.0)
    assert a.holder == "ds h"
    #: ★★★ **第二个客户端 ⇒ 拒绝**
    with pytest.raises(J.JobError) as exc:
        lease.acquire("workbuddy", now=1001.0)
    assert "只能一个" in str(exc.value), "★ 错误信息没说清原因"


def test_v2_expired_lease_can_be_taken_over_with_a_new_token():
    """★★★ V2：★ **过期后可以让出** ⇒ ★ **但令牌递增**（★ 老 worker 被挡住）。"""
    lease = J.NodeLease()
    first = lease.acquire("A", ttl_seconds=10.0, now=1000.0)
    #: ★ 过期后 B 可以拿
    second = lease.acquire("B", ttl_seconds=10.0, now=1020.0)
    assert second.holder == "B"
    assert second.token > first.token, "★★ 换手后令牌**没有递增** ⇒ ★ 围栏失效"
    #: ★★★ **A 拿着旧令牌 ⇒ 不能改**
    assert lease.may_modify("A", first.token, now=1021.0) is False, (
        "★★★ 过期 worker 仍能修改 ⇒ ★ 违反 EC04-T02「过期 worker 不能继续修改」")


def test_v2_fence_token_rejects_stale_presenters():
    """★★★ V2：★ **围栏令牌只接受当前值**（★ 落后或超前都拒）。"""
    f = J.FenceToken(5)
    assert f.accepts(5) is True
    assert f.accepts(4) is False, "★★ 落后令牌被接受 ⇒ ★ 过期 worker 能改"
    assert f.accepts(6) is False, "★★ 超前令牌被接受 ⇒ ★ 未获授权者能改"


def test_v2_may_modify_requires_all_three():
    """★★ V2：★ `may_modify` 要**三条都满足**（★ 持有人 + 令牌 + 未过期）。"""
    lease = J.NodeLease()
    got = lease.acquire("A", ttl_seconds=10.0, now=1000.0)
    #: ① 全对 ⇒ 可以
    assert lease.may_modify("A", got.token, now=1005.0) is True
    #: ② 换了人 ⇒ 不行
    assert lease.may_modify("B", got.token, now=1005.0) is False
    #: ③ 令牌错 ⇒ 不行
    assert lease.may_modify("A", got.token + 99, now=1005.0) is False
    #: ④ 过期 ⇒ 不行
    assert lease.may_modify("A", got.token, now=1100.0) is False


def test_v2_renew_requires_the_right_token():
    """★★ V2：★ **续期必须带对令牌**（★ 否则是过期 worker 在续命）。"""
    lease = J.NodeLease()
    got = lease.acquire("A", ttl_seconds=10.0, now=1000.0)
    assert lease.renew("A", got.token, now=1005.0) is True
    assert lease.renew("A", got.token + 1, now=1006.0) is False, (
        "★★ 用错令牌续期成功 ⇒ ★ 围栏失效")


# ══════════════════════════════════════════════════════════════════════
# V3 · 旧证据不能放行新模型
# ══════════════════════════════════════════════════════════════════════

def test_v3_binding_requires_all_three_versions():
    """★★★★★ V3：★ **批准绑 contract/plan/model 三个版本**（★ 逐字承 EC04-T03）。

    ★★★ **验收（★ 计划逐字）**：★「★ **旧证据不能放行新模型**」。
    """
    b = J.VersionBinding(contract_hash="c1", plan_hash="p1", model_revision="m1")
    assert b.matches("c1", "p1", "m1") is True
    #: ★★★ **任何一个变了 ⇒ 失效**
    assert b.matches("c2", "p1", "m1") is False, "★★ 契约变了仍匹配"
    assert b.matches("c1", "p2", "m1") is False, "★★ 计划变了仍匹配"
    assert b.matches("c1", "p1", "m2") is False, (
        "★★★ **模型变了仍匹配** ⇒ ★ 旧证据放行了新模型（★ 验收核心负例）")


def test_v3_invalidation_is_named():
    """★★ V3：★ **失效原因要具名**（★ 哪几个版本变了）。"""
    b = J.VersionBinding(contract_hash="c1", plan_hash="p1", model_revision="m1")
    assert b.invalidated_by("c2", "p1", "m2") == ["contract", "model"]
    assert b.invalidated_by("c1", "p1", "m1") == []


def test_v3_evidence_chain_excludes_stale_records():
    """★★★★ V3：★ **旧证据不进「能放行」的清单**。"""
    chain = J.EvidenceChain()
    art = J.ArtifactRecord(relative_path="output/a.step",
                           sha256="sha256:" + "a" * 64)
    old = J.VersionBinding("c1", "p1", "m1")
    chain.add(old, art)
    #: ★★ 当前版本是 **m2**（★ 模型换了）
    assert chain.releasing_records("c1", "p1", "m1"), "★ 同版本应能放行"
    assert chain.releasing_records("c1", "p1", "m2") == [], (
        "★★★ 模型换版后**旧证据仍能放行** ⇒ ★ 违反验收（★ 旧证据不能放行新模型）")


# ══════════════════════════════════════════════════════════════════════
# V4 · 证据链完整性 + 敏感过滤 + 相对路径
# ══════════════════════════════════════════════════════════════════════

def test_v4_chain_is_tamper_evident():
    """★★ V4：★ **改中间一条 ⇒ 断链**（★ EC04-T07 的哈希要求）。"""
    chain = J.EvidenceChain()
    b = J.VersionBinding("c1", "p1", "m1")
    chain.add(b, J.ArtifactRecord("output/a.step", "sha256:" + "a" * 64))
    chain.add(b, J.ArtifactRecord("output/b.step", "sha256:" + "b" * 64))
    assert chain.verify_chain() is True, "★ 未改动却断链"
    #: ★★ **改中间一条的 payload**
    chain.records[0]["payload"] = {"tampered": True}
    assert chain.verify_chain() is False, (
        "★★ 改了证据链却仍校验通过 ⇒ ★ 链没有防篡改")


def test_v4_sensitive_fields_are_redacted_not_deleted():
    """★★★ V4：★ **敏感字段被替换成 `***REDACTED***`**（★ **不是删键** —— ★ EC04-T07）。"""
    out = J.filter_sensitive({"token": "abc123", "user": "alice",
                              "nested": {"api_key": "sk-xyz", "n": 1}})
    assert out["token"] == "***REDACTED***", "★★ token 没被脱敏"
    assert out["user"] == "alice", "★ 普通字段被误脱敏"
    assert out["nested"]["api_key"] == "***REDACTED***", "★★ 嵌套里的没脱敏"
    #: ★★★ **键必须还在**（★ 删了就看不出来「这里本该有个东西」）
    assert "token" in out, "★★ 敏感键被**删掉**了 ⇒ ★ 看不出本该有它"


def test_v4_artifacts_must_use_relative_paths():
    """★★ V4：★ **工件必须是相对路径**（★ 绝对路径泄漏本机目录结构 —— ★ EC04-T07）。"""
    ok = J.ArtifactRecord("output/a.step", "sha256:" + "a" * 64)
    assert ok.is_relative() is True and ok.is_valid() is True
    for bad in ("C:/Users/x/a.step", "C:\\Users\\x\\a.step", "/etc/passwd"):
        rec = J.ArtifactRecord(bad, "sha256:" + "a" * 64)
        assert rec.is_relative() is False, "★★ 绝对路径被当成合法：%r" % bad


def test_v4_artifact_hash_must_be_well_formed():
    """★★ V4：★ **哈希必须形如 `sha256:` + 64 位**（★ 占位不算）。"""
    assert J.ArtifactRecord("a.step", "sha256:" + "a" * 64).is_valid() is True
    for bad in ("", "sha256:short", "md5:" + "a" * 64, "sha256:" + "a" * 63):
        assert J.ArtifactRecord("a.step", bad).is_valid() is False, (
            "★★ 非法哈希被当成合法：%r" % bad)


# ══════════════════════════════════════════════════════════════════════
# V5 · 独立验收器
# ══════════════════════════════════════════════════════════════════════

def test_v5_self_review_is_rejected():
    """★★★★ V5：★ **同一 Agent 自评 ⇒ 拒**（★ 逐字承 EC04-T06：
    「★ **不把同一 Agent 自评当放行者**」）。"""
    v = J.IndependentVerifier(executor_id="agent-1", verifier_id="agent-1")
    assert v.may_verify() is False, "★★ 自评被允许 ⇒ ★ 违反 EC04-T06"
    assert v.verdict(checks_passed=True, authorized=True) == "reject-self-review"


def test_v5_separate_verifier_can_verify():
    """★★ V5：★ **不同 Agent ⇒ 可以验收**。"""
    v = J.IndependentVerifier(executor_id="agent-1", verifier_id="agent-2")
    assert v.may_verify() is True
    assert v.verdict(checks_passed=True, authorized=True) == "pass"


def test_v5_unauthorized_action_stops_at_design_advice():
    """★★★★★ V5：★ **无许可/权限 ⇒ 停在设计建议**（★ 逐字承计划验收）。"""
    v = J.IndependentVerifier(executor_id="a", verifier_id="b")
    out = v.verdict(checks_passed=True, authorized=False)
    assert out == "design_advice_only", (
        "★★★ 无许可却回了 %r ⇒ ★ 它不该「通过」也不该「失败」" % out)
    assert out not in ("pass", "fail"), "★★ 无许可被当成了判定"


def test_v5_verifier_must_be_read_only():
    """★★ V5：★ **验收器必须只读**（★ EC04-T06 逐字：「★ 独立验收器**只读**最终模型」）。"""
    v = J.IndependentVerifier(executor_id="a", verifier_id="b", read_only=False)
    assert v.verdict(checks_passed=True, authorized=True) == "reject-not-read-only"


# ══════════════════════════════════════════════════════════════════════
# V6 · 恢复：失败不丢用户文件 + 不宣称全局事务
# ══════════════════════════════════════════════════════════════════════

def test_v6_no_global_transaction_is_declared():
    """★★★★ V6：★ **显式声明「COM 没有全局事务」**（★ 逐字承 EC04-T05）。"""
    assert J.RecoveryPlan.HAS_GLOBAL_TRANSACTION is False, (
        "★★ 宣称 COM 有全局事务 ⇒ ★ 违反 EC04-T05（★ 它没有）")


def test_v6_forward_compensation_never_deletes_user_files():
    """★★★★★ V6：★ **前向补偿绝不删用户文件**（★ 逐字承计划验收：「★ **失败不丢用户文件**」）。"""
    plan = J.RecoveryPlan()
    plan.add_checkpoint("stage-1", "output/ck1.SLDPRT")
    out = plan.forward_compensation("stage-1")
    assert out["ok"] is True
    assert out["rollback_available"] is False, (
        "★★ 宣称有回滚 ⇒ ★ 违反「无全局事务」")
    assert out["deletes_user_files"] is False, (
        "★★★ 补偿会删文件 ⇒ ★ 违反「失败不丢用户文件」")


def test_v6_unknown_stage_is_reported_not_guessed():
    """★★ V6：★ **找不到阶段的检查点 ⇒ 明说**（★ 不猜）。"""
    out = J.RecoveryPlan().forward_compensation("no-such-stage")
    assert out["ok"] is False
    assert "找不到" in out["reason"]


# ══════════════════════════════════════════════════════════════════════
# V7 · 纯离线
# ══════════════════════════════════════════════════════════════════════

def test_v7_jobs_module_has_no_com_imports():
    """★★★ V7：★ **作业层不 import COM**（★ 与 EC03 同族 —— ★ 让它在没装 SW 的机器上也能验）。"""
    out = J.assert_no_com_imports()
    assert out["ok"] is True, "★★ import 了 COM：%r" % out["offending_imports"]


def test_v7_test_file_itself_does_not_import_com():
    """★★ V7：★ 判据自身也不 import COM（★ 用 AST 核 —— ★ 不用文本包含）。"""
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8", errors="replace"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    bad = [m for m in imported
           if any(k in m for k in ("win32com", "comtypes", "sw_part", "sw_session"))]
    assert not bad, "★★ 判据 import 了 COM：%r" % bad


# ══════════════════════════════════════════════════════════════════════
# V8 · 复用目标存在（★ 铁律 1）
# ══════════════════════════════════════════════════════════════════════

def test_v8_reuse_targets_exist():
    """★★ V8：★ 计划 §5 EC04 点名的**复用目标必须存在**（★ 不另建）。"""
    for rel in ("scripts/cad_workbench/queue_worker.py",
                "scripts/cad_workbench/reviewer_gate.py",
                "scripts/cad_workbench/engineering_orchestrator.py",
                "tools/sw_guard.py"):
        assert (ROOT / rel).is_file(), "★★ 复用目标不见了：%s" % rel
