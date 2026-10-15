"""★ EC04 T08 判据 —— **故障注入**（★ 三类离线 · ★ 一类如实标「需 COM」）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/jobs.py`（★ `inject_*` · `injection_coverage`）
#         `specs/306-ec04-safe-jobs-and-evidence/spec.md`（★ FR-008 · US1–US6）
# 定位:   ★ EC04 **T08**（★ 逐字：「★ 注入 **worker 退出、审批过期、模型被外部修改、
#         模态框与读写失败**」）。
# 官方依据: 不适用（本仓的作业层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import jobs as J


def test_t08_injection_kinds_cover_the_four_named_ones():
    """★★ T08：★ **四类故障必须被点名**（★ 逐字承 EC04-T08）。"""
    named = set(J.InjectionKind.OFFLINE_INJECTABLE) | set(J.InjectionKind.REQUIRES_COM)
    assert named == {"worker_exit", "approval_expired", "model_externally_modified",
                     "modal_or_io_failure"}, "★ 四类不齐：%r" % named


def test_t08_worker_exit_stops_modification_but_frees_the_lease():
    """★★★ T08 注入 ①：★ **worker 退出 ⇒ 它不能再改，★ 但租约可以让出**。"""
    lease = J.NodeLease()
    got = lease.acquire("A", ttl_seconds=60.0, now=1000.0)
    out = J.inject_worker_exit(lease, "A", got.token, now=1005.0)
    assert out["could_modify_before_exit"] is True, "★ 退出前应能改"
    assert out["can_modify_after_exit"] is False, (
        "★★ worker 退出后仍能改 ⇒ ★ 围栏没生效")
    assert out["lease_releasable"] is True, (
        "★★ 租约没释放 ⇒ ★ 别人接手不了（★ 会永久占住会话）")


def test_t08_approval_expiry_invalidates_the_binding():
    """★★★ T08 注入 ②：★ **审批过期 ⇒ 失效**（★ 且**具名**哪个版本变了）。"""
    b = J.VersionBinding("c1", "p1", "m1")
    out = J.inject_approval_expired(b, current_contract="c1", current_plan="p1",
                                    current_model="m2")
    assert out["still_valid"] is False, "★★ 模型换了审批却仍有效"
    assert out["invalidated_by"] == ["model"], "★ 没点名：%r" % out["invalidated_by"]
    #: ★ 负例：全没变 ⇒ 仍有效
    same = J.inject_approval_expired(b, current_contract="c1", current_plan="p1",
                                     current_model="m1")
    assert same["still_valid"] is True


def test_t08_external_model_modification_kills_the_evidence():
    """★★★ T08 注入 ③：★ **模型被外部修改 ⇒ 旧证据立即失效**（★ 验收核心）。"""
    b = J.VersionBinding("c1", "p1", "m1")
    out = J.inject_model_externally_modified(b, new_model_revision="m9")
    assert out["evidence_still_releases"] is False, (
        "★★★ 模型被外部改了，旧证据**仍能放行** ⇒ ★ 违反「旧证据不能放行新模型」")
    assert out["old_revision"] == "m1" and out["new_revision"] == "m9"


def test_t08_modal_failure_is_honestly_marked_as_requiring_com():
    """★★★★ T08：★ **模态框/读写失败必须**如实**标「需 COM」**（★ 不假装做了）。

    ★★ 依据（★ 本特性**不碰 COM** —— ★ `spec.md` §五 非目标）⇒ ★ 那一类**属 EC05**。
    """
    cov = J.injection_coverage()
    assert "modal_or_io_failure" in cov["requires_com"], (
        "★★ 模态框类被标成「可离线注」⇒ ★ 那是**假装做了**")
    assert "modal_or_io_failure" not in cov["offline_injectable"], (
        "★★ 模态框类进了离线清单 ⇒ ★ 判据不诚实")
    #: ★★ 三条离线的必须在
    for k in ("worker_exit", "approval_expired", "model_externally_modified"):
        assert k in cov["offline_injectable"], "★ `%s` 不在离线清单" % k
    #: ★ 且必须写明它属 EC05
    assert "EC05" in cov["note"], "★ 没写明那一类属 EC05"
