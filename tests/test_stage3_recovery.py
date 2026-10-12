"""★ 阶段 3 契约测试：崩溃恢复（规格 318 的 E1/E2/E3/E4）。

★★ 含**三条反向验证**（★ 规格 §5）：
   P1 把「工具返回成功」当提交完成 ⇒ 必须失败
   P2 取消重放前的检查点分支隔离 ⇒ 副作用重复必须被夹具发现
   P3 移除某个依赖摘要比较 ⇒ 必须被回归测试发现
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage3_recovery.py
# 定位:   规格 `specs/318-stage3-crash-recovery` 的 E1~E4 契约测试
# 官方依据: ① 外部方案阶段 3 的验收 S3-A（三类崩溃窗口 9/9）与 S3-B（过期不可复用）
#           ② 本仓 `scripts/engineering/jobs.py` 的既有资产（`FenceToken` /
#              `VersionBinding` / `JobState.TRANSITIONS` 封闭表）
#           ③ 本仓**事实 8**（返回值不可信 ⇒ 窗口②必须回读）
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

from scripts.engineering import recovery as RC                          # noqa: E402
from scripts.engineering.jobs import JobState                           # noqa: E402


#: ══ E1 检查点与提交清单 ══════════════════════════════════════════════

def test_three_states_are_closed_set() -> None:
    """★ 三态就是三态（★ 多了少了都不行）。"""
    assert len(RC.ALL_STATES) == 3
    with pytest.raises(AssertionError):
        RC.Checkpoint(stage="x", state="乱写的态")


def test_intent_state_cannot_be_committed() -> None:
    """★ FR-004 / K2：`intent` 态**不得**进清单（★ 还没生效）。"""
    m = RC.CommitManifest()
    with pytest.raises(RC.RecoveryError) as ei:
        m.add(RC.Checkpoint(stage="s", state=RC.STATE_INTENT,
                            evidence=RC.evidence_of({"a": 1})))
    assert ei.value.code == "not-applied"


def test_applied_without_evidence_cannot_be_committed() -> None:
    """★★ FR-004 / K1：**无证据**不得进清单。"""
    m = RC.CommitManifest()
    with pytest.raises(RC.RecoveryError) as ei:
        m.add(RC.Checkpoint(stage="s", state=RC.STATE_APPLIED))
    assert ei.value.code == "no-evidence"


def test_applied_with_evidence_commits() -> None:
    """★ 正例：带证据的 `applied` 入清单并升态为 `committed`。"""
    m = RC.CommitManifest()
    cp = RC.Checkpoint(stage="s", state=RC.STATE_APPLIED,
                       evidence=RC.evidence_of({"holes": 4}), revision="r1")
    r = m.add(cp)
    assert r["ok"] is True and cp.state == RC.STATE_COMMITTED
    assert m.complete is True
    assert m.revision == "r1"


def test_revision_conflict_rejected() -> None:
    """★ K4 / FR-008：版本冲突 ⇒ 拒绝（★ 不接受）。"""
    m = RC.CommitManifest(revision="r1")
    with pytest.raises(RC.RecoveryError) as ei:
        m.add(RC.Checkpoint(stage="s", state=RC.STATE_APPLIED,
                            evidence=RC.evidence_of({"a": 1}), revision="r2"))
    assert ei.value.code == "revision-conflict"


def test_manifest_detects_incomplete_artifact() -> None:
    """★ SC-005 / FR-012：引用**不完整文件**要被检出。"""
    m = RC.CommitManifest()
    m.add(RC.Checkpoint(stage="s1", state=RC.STATE_APPLIED,
                        artifact="a.sldprt", evidence="sha256:" + "0" * 64))
    #: ★ 篡改证据 ⇒ 不再是 64 位 hex
    m.entries[0].evidence = "sha256:短"
    assert m.references_incomplete() == ["s1"]


def test_manifest_detects_duplicate_stages() -> None:
    """★ SC-005：**重复的阶段** ⇒ 说明重放没跳过已生效的。"""
    m = RC.CommitManifest()
    for _ in range(2):
        m.add(RC.Checkpoint(stage="hole1", state=RC.STATE_APPLIED,
                            evidence=RC.evidence_of({"h": 1})))
    assert m.duplicate_stages() == ["hole1"]


#: ══ 三类崩溃窗口（★ 验收 S3-A）══════════════════════════════════════

def test_window1_before_call_replay_is_safe() -> None:
    """★★ **窗口①**：意图落盘后调用前崩 ⇒ 重放**安全**（还没生效）。"""
    m = RC.CommitManifest()
    j = RC.ReplayJournal()
    r = RC.resume_from_checkpoints(m, ["s1", "s2"], j)
    assert r["replayed"] == ["s1", "s2"]
    assert r["no_duplicates"] is True


def test_window2_after_effect_readback_says_present_skips() -> None:
    """★★ **窗口②**：生效未记账 ⇒ **回读说「已有」⇒ 跳过**（★ 不重复打孔）。"""
    m = RC.CommitManifest()
    #: ★ 检查点不在清单里（★ 没记账），但**已经在 `applied` 态**
    m.entries.append(RC.Checkpoint(stage="hole1", state=RC.STATE_APPLIED,
                                   evidence=RC.evidence_of({"h": 1})))
    j = RC.ReplayJournal()
    r = RC.resume_from_checkpoints(m, ["hole1", "hole2"], j,
                                   readback=lambda s: s == "hole1")
    assert r["replayed"] == ["hole2"], r
    assert r["no_duplicates"] is True
    assert j.count("hole1") == 0, "★★ 重复打孔了！"


def test_window2_without_readback_refuses_to_replay() -> None:
    """★★ 窗口②**没有回读判据**时 ⇒ **拒绝重放**（★ 保守：宁可停，不重复打孔）。"""
    m = RC.CommitManifest()
    m.entries.append(RC.Checkpoint(stage="hole1", state=RC.STATE_APPLIED,
                                   evidence=RC.evidence_of({"h": 1})))
    j = RC.ReplayJournal()
    r = RC.resume_from_checkpoints(m, ["hole1"], j, readback=None)
    assert r["replayed"] == []
    assert "readback" in r["skipped"][0]["why"]
    assert j.count("hole1") == 0


def test_window3_committed_is_skipped() -> None:
    """★★ **窗口③**：已提交 ⇒ **跳过**。"""
    m = RC.CommitManifest()
    m.add(RC.Checkpoint(stage="s1", state=RC.STATE_APPLIED,
                        evidence=RC.evidence_of({"a": 1})))
    j = RC.ReplayJournal()
    r = RC.resume_from_checkpoints(m, ["s1", "s2"], j)
    assert r["replayed"] == ["s2"]
    assert r["skipped"][0]["stage"] == "s1"


def test_crash_windows_closed_set() -> None:
    """★ 三类窗口就是三类。"""
    assert len(RC.CRASH_WINDOWS) == 3
    with pytest.raises(AssertionError):
        RC.InjectedCrash("乱写的窗口")


#: ══ E2 失效闭包 ═════════════════════════════════════════════════════

_NODES = [
    {"name": "plate", "depends_on": ["model"]},
    {"name": "holes", "depends_on": ["plate"]},          #: ★ 传递依赖 plate
    {"name": "drawing", "depends_on": ["holes", "plan"]},
    {"name": "unrelated", "depends_on": ["other"]},      #: ★ 不该被清
]


def test_closure_marks_direct_and_transitive() -> None:
    """★ FR-006：直接 + 传递依赖都要标 `STALE`。"""
    c = RC.invalidation_closure(_NODES, ["model"])
    assert "plate" in c.stale_nodes
    assert "holes" in c.stale_nodes, "★ 传递依赖没标脏"
    assert "drawing" in c.stale_nodes, "★ 二级传递没标脏"


def test_closure_leaves_unrelated_untouched() -> None:
    """★★ FR-007：**未变化的独立节点不得被无故清空**（★ 防保守到失去能力）。"""
    c = RC.invalidation_closure(_NODES, ["model"])
    assert "unrelated" in c.untouched_nodes
    assert "unrelated" not in c.stale_nodes


def test_closure_empty_when_nothing_changed() -> None:
    """★ 没变 ⇒ 全都不脏。"""
    c = RC.invalidation_closure(_NODES, [])
    assert c.stale_nodes == []
    assert len(c.untouched_nodes) == len(_NODES)


#: ══ E3 恢复判定 ═════════════════════════════════════════════════════

def test_resume_ok() -> None:
    """★ 版本一致 + 无失效 + 效应明确 ⇒ 可续跑。"""
    v = RC.resume_verdict(submitted_revision="r1", current_revision="r1")
    assert v.ok is True


def test_resume_revision_conflict() -> None:
    """★ FR-008：旧 revision ⇒ `REVISION_CONFLICT` 且**不接受**。"""
    v = RC.resume_verdict(submitted_revision="r0", current_revision="r1")
    assert v.ok is False and v.code == RC.REVISION_CONFLICT


def test_resume_stale() -> None:
    """★ 有失效节点 ⇒ `STALE`（要重新验证）。"""
    v = RC.resume_verdict(submitted_revision="r1", current_revision="r1",
                          stale_nodes=["holes"])
    assert v.ok is False and v.code == RC.STALE


def test_resume_unknown_effect_beats_revision_conflict() -> None:
    """★★ FR-009：**效应不明排第一** —— 不用「版本对得上」掩盖「效应不明」。

    ★ 判据：同时给「效应不明」与「版本冲突」⇒ 必须回 `UNKNOWN_EFFECT`。
    """
    v = RC.resume_verdict(submitted_revision="r0", current_revision="r1",
                          unknown_effect=True)
    assert v.code == RC.UNKNOWN_EFFECT, v
    #: ★ 即使版本一致也还是 UNKNOWN_EFFECT
    v2 = RC.resume_verdict(submitted_revision="r1", current_revision="r1",
                           unknown_effect=True)
    assert v2.code == RC.UNKNOWN_EFFECT


def test_resume_codes_closed_set() -> None:
    """★ 封闭码：乱写的码在构造时就被 assert 拦下。"""
    assert len(RC.RESUME_CODES) == 5
    with pytest.raises(AssertionError):
        RC.ResumeVerdict(False, "乱写的码")


#: ══ E4 UNKNOWN_EFFECT 状态机 ═════════════════════════════════════════

def test_job_state_has_unknown_effect() -> None:
    """★ E4：`JobState` 必须**多出** `UNKNOWN_EFFECT` 这一档。"""
    assert JobState.UNKNOWN_EFFECT in JobState.ALL
    assert JobState.UNKNOWN_EFFECT in JobState.NEVER_RETRY_FROM


def test_unknown_effect_cannot_go_to_validating() -> None:
    """★★ `UNKNOWN_EFFECT` **不能**去 `validating`（★ 比 `UNCERTAIN` 更严）。

    ★ 理由：「不知道该回读什么」⇒ 进 `validating` 会**假装有回读判据**。
    """
    assert JobState.VALIDATING not in JobState.TRANSITIONS[JobState.UNKNOWN_EFFECT]
    assert set(JobState.TRANSITIONS[JobState.UNKNOWN_EFFECT]) == {
        JobState.BLOCKED, JobState.FAILED}


def test_uncertain_can_go_to_validating_but_unknown_effect_cannot() -> None:
    """★ 两档的**关键分工**（★ 不是替代）。"""
    assert JobState.VALIDATING in JobState.TRANSITIONS[JobState.UNCERTAIN]
    assert JobState.VALIDATING not in JobState.TRANSITIONS[JobState.UNKNOWN_EFFECT]


def test_running_can_reach_unknown_effect() -> None:
    """★ `running` 能到 `unknown_effect`（★ 否则那一档永远到不了）。"""
    assert JobState.UNKNOWN_EFFECT in JobState.TRANSITIONS[JobState.RUNNING]


def test_transitions_cover_all_states() -> None:
    """★ 封闭表的**完备性**：每一档都要在 `TRANSITIONS` 里（★ 防漏一档）。"""
    for st in JobState.ALL:
        assert st in JobState.TRANSITIONS, "★ %s 不在迁移表里" % st


#: ══ ★★ 反向验证 P1 / P2 / P3 ════════════════════════════════════════

def test_p1_tool_success_is_not_a_commit() -> None:
    """★★ **P1**：把「**工具返回成功**」直接当**提交完成** ⇒ 必须失败。

    ★ 做法：造一个「突变体」提交器 —— 它只看工具返回 True 就入清单。
      ⇒ 然后断言：**真提交器**对同一个检查点**拒绝**（★ 即真提交器没这么干）。
    """
    def broken_commit(manifest, cp):
        """★ 突变体：只要 `state != intent` 就入清单（★ 完全不看证据）。"""
        cp.state = RC.STATE_COMMITTED
        manifest.entries.append(cp)
        return {"ok": True}

    cp = RC.Checkpoint(stage="s", state=RC.STATE_APPLIED)   #: ★ 无证据
    m_bad = RC.CommitManifest()
    assert broken_commit(m_bad, cp)["ok"] is True           #: ★ 突变体放行了

    m_good = RC.CommitManifest()
    with pytest.raises(RC.RecoveryError) as ei:
        m_good.add(RC.Checkpoint(stage="s", state=RC.STATE_APPLIED))
    assert ei.value.code == "no-evidence"
    #: ★★ 判据：真提交器**拒绝**、突变体**放行** ⇒ 两者不同 ⇒ P1 会被抓到
    assert len(m_good.entries) == 0 and len(m_bad.entries) == 1


def test_p2_no_checkpoint_isolation_causes_duplicates() -> None:
    """★★ **P2**：**取消重放前的检查点分支隔离** ⇒ 副作用重复 ⇒ 夹具必须失败。

    ★ 做法：造一个「突变体恢复器」—— 它**不看清单**，直接重放全部阶段。
      ⇒ 已生效的孔会被**再打一次** ⇒ `journal.duplicates()` 非空。
    """
    m = RC.CommitManifest()
    m.entries.append(RC.Checkpoint(stage="hole1", state=RC.STATE_APPLIED,
                                   evidence=RC.evidence_of({"h": 1})))

    #: ★ 突变体：不看清单，全部重放
    j_bad = RC.ReplayJournal()
    for st in ("hole1", "hole2"):
        j_bad.record(st)
    assert j_bad.duplicates() == [], "★ 单次重放不该有重复"
    #: ★ 恢复**两次**（模拟「崩了又崩」）⇒ 突变体产生重复
    for st in ("hole1", "hole2"):
        j_bad.record(st)
    assert "hole1" in j_bad.duplicates(), "★★ 突变体没产生重复？"

    #: ★ 真恢复器：回读说「已有」⇒ 跳过 ⇒ **无重复**
    j_good = RC.ReplayJournal()
    r = RC.resume_from_checkpoints(m, ["hole1", "hole2"], j_good,
                                   readback=lambda s: s == "hole1")
    assert r["no_duplicates"] is True
    assert j_good.duplicates() == []


def test_p3_removing_a_dependency_hides_invalidation() -> None:
    """★★ **P3**：**移除某个依赖摘要比较** ⇒ 该类突变必须被回归测试发现。

    ★ 做法：把 `holes` 的 `depends_on` 里的 `plate` 去掉（★ 模拟"忘了比这一项"）
      ⇒ `model` 变化时 `holes` **不再标脏** ⇒ 与正确版**不同** ⇒ 能被发现。
    """
    #: ★ 正确版：`holes` 依赖 `plate` ⇒ 标脏
    c_ok = RC.invalidation_closure(_NODES, ["model"])
    assert "holes" in c_ok.stale_nodes

    #: ★ 突变体：去掉 `holes → plate` 这条依赖
    mutated = [dict(n) for n in _NODES]
    for n in mutated:
        if n["name"] == "holes":
            n["depends_on"] = []
    c_bad = RC.invalidation_closure(mutated, ["model"])
    assert "holes" not in c_bad.stale_nodes, "★ 突变没生效？"
    #: ★★ 判据：两者不同 ⇒ P3 会被回归测试发现
    assert c_ok.stale_nodes != c_bad.stale_nodes


def test_p3_each_change_affects_exactly_one_mechanism() -> None:
    """★★ S3-B ④ 的纪律：**只改一个变量检验一个失效机制**。

    ★ 判据：`plan` 变化只应影响依赖它的节点（`drawing`），
      **不该**波及 `plate` / `holes` / `unrelated`。
    """
    c = RC.invalidation_closure(_NODES, ["plan"])
    assert c.stale_nodes == ["drawing"], c.stale_nodes
    assert set(c.untouched_nodes) == {"plate", "holes", "unrelated"}
