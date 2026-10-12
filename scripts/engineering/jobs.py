"""★ EC04 安全作业、恢复、版本与证据链 —— 租约 / 围栏 / 版本绑定 / 独立验收。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC04**（★ T01–T08 逐字）
#         `specs/306-ec04-safe-jobs-and-evidence/spec.md`（★ FR · V）
#         `specs/302-ec00-trustworthy-tool-base/data-model.md` §五（★ 效果状态机 —— ★ **复用**）
#         `specs/302-*/quickstart.md` §5.2（★ **EC00 → EC04 的边界**）
# 定位:   ★ **EC04** 的作业与证据层。★★★ 计划 §5 EC04 验收逐字：
#           「★ 双客户端争抢**只能一个**得到执行权；★ **超时未回读不重试**；
#            ★ **旧证据不能放行新模型**；★ **失败不丢用户文件**；
#            ★ 没有许可/权限的动作**停在设计建议**」
#         ★★ **EC00 的边界**（★ 逐字）：「★ EC00 只接现有本地互斥与上下文边界；
#           ★★ **完整节点租约、围栏令牌和批准失效机制属于 EC04**」
# 官方依据: 不适用（本仓的作业编排层 —— ★ **不调 SolidWorks API**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 见 `assert_no_com_imports`）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "JobState", "JobError", "Lease", "FenceToken", "NodeLease",
    "VersionBinding", "EvidenceChain", "ArtifactRecord",
    "IndependentVerifier", "RecoveryPlan", "assert_no_com_imports",
    "InjectionKind", "inject_worker_exit", "inject_approval_expired",
    "inject_model_externally_modified", "injection_coverage",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ Job 状态机（★ EC04-T01 逐字）
# ══════════════════════════════════════════════════════════════════════

class JobState:
    """★★ Job 状态（★ 逐字承 EC04-T01）：

    「★ queued/planned/approved/running/uncertain/validating/blocked/completed/failed」
    """

    QUEUED = "queued"
    PLANNED = "planned"
    APPROVED = "approved"
    RUNNING = "running"
    UNCERTAIN = "uncertain"          #: ★★ **超时/语义不明的 COM 错误** ⇒ ★ **不重试**
    #: ★★★★ 2026-10-12 新增（★ 规格 318 · E4）：**效应不明**。
    #:   ★★ 与 `UNCERTAIN` 的分工（★ 两个都要，★ **不是替代**）：
    #:     · `UNCERTAIN`      说的是「**调用**结果不明」⇒ ★ 可以靠**回读**补救
    #:     · `UNKNOWN_EFFECT` 说的是「**这个工具到底写没写**都不知道」
    #:       ⇒ ★★ **连该回读什么都不知道** ⇒ ★ **停下交人**
    #:   ★ 依据：外部方案阶段 3 逐字要求「单写者所有权与 **`UNKNOWN_EFFECT` 状态**」。
    UNKNOWN_EFFECT = "unknown_effect"
    VALIDATING = "validating"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"

    ALL = (QUEUED, PLANNED, APPROVED, RUNNING, UNCERTAIN, UNKNOWN_EFFECT,
           VALIDATING, BLOCKED, COMPLETED, FAILED)

    #: ★★ **允许的迁移**（★ 封闭表）
    TRANSITIONS = {
        QUEUED: (PLANNED, BLOCKED, FAILED),
        PLANNED: (APPROVED, BLOCKED, FAILED),
        APPROVED: (RUNNING, BLOCKED, FAILED),
        RUNNING: (UNCERTAIN, UNKNOWN_EFFECT, VALIDATING, FAILED),
        #: ★★★ **`uncertain` 只能去 `validating`（回读）或 `blocked`/`failed`**
        #:   ★★ **不能回 `running`** ⇒ ★ 那是「不重试」的**结构性保证**
        UNCERTAIN: (VALIDATING, BLOCKED, FAILED),
        #: ★★★★ **`unknown_effect` 只能去 `blocked`/`failed`** ——
        #:   ★★ **连 `validating` 都不给**：因为「不知道该回读什么」⇒
        #:     ★ 进 `validating` 会**假装有回读判据**。★ 比 `UNCERTAIN` **更严**的一档。
        UNKNOWN_EFFECT: (BLOCKED, FAILED),
        VALIDATING: (COMPLETED, FAILED, UNCERTAIN),
        BLOCKED: (QUEUED, FAILED),
        COMPLETED: (),
        FAILED: (),
    }
    #: ★★ **终态**
    TERMINAL = (COMPLETED, FAILED)
    #: ★★★ **绝不从这些状态重试**（★ 承 EC00 的效果状态机）
    #:   ★ `UNKNOWN_EFFECT` 与 `UNCERTAIN` **同族但更严**（★ 连回读都不给）
    NEVER_RETRY_FROM = (UNCERTAIN, UNKNOWN_EFFECT)


class JobError(Exception):
    """★ 作业错误（★ 带**封闭码** —— ★ 与 EC00/EC01/EC02/EC03 同族）。"""


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 节点租约与围栏令牌（★ EC04-T02）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class FenceToken:
    """★★★ **围栏令牌**（★ EC04-T02 逐字：★「★ 单 SW 会话互斥、租约续期、围栏令牌；
    ★ **过期 worker 不能继续修改**」）。

    ★★★ **机制**：★ 每次获得租约 ⇒ **令牌单调递增**；★ 持有者提交时**必须**带当前令牌；
      ★★ **令牌落后 ⇒ 拒绝**（★ 那个 worker 已过期）。
    """

    value: int = 0

    def next(self) -> "FenceToken":
        return FenceToken(self.value + 1)

    def accepts(self, presented: int) -> bool:
        """★★ **只接受当前令牌**（★ 落后或超前 ⇒ 拒）。"""
        return presented == self.value


@dataclass
class Lease:
    """★★ 租约（★ 带**过期时刻** —— ★ 续期可延长）。"""

    holder: str
    token: int
    expires_at: float
    ttl_seconds: float = 60.0

    def is_expired(self, now: float | None = None) -> bool:
        return (now if now is not None else time.time()) >= self.expires_at

    def renew(self, now: float | None = None) -> None:
        base = now if now is not None else time.time()
        self.expires_at = base + self.ttl_seconds


@dataclass
class NodeLease:
    """★★★ **节点级租约**（★ 单 SW 会话互斥 —— ★ **EC04 的交付**，★ 承 EC00 的边界声明）。

    ★★★ **验收（★ 计划逐字）**：★「★ 双客户端争抢**只能一个**得到执行权」。
    """

    session_id: str = "sw-session-1"
    fence: FenceToken = field(default_factory=FenceToken)
    current: Lease | None = None
    _acquisitions: int = 0

    def acquire(self, holder: str, *, ttl_seconds: float = 60.0,
                now: float | None = None) -> Lease:
        """★★★ **取得租约**（★ **只有一个能拿到**）。

        ★★ 若当前租约**未过期** ⇒ ★ **拒绝**（★ 那是「双客户端争抢」的处置）。
        ★ 若**已过期** ⇒ ★ 可以让出（★ 且**令牌递增** ⇒ ★ 老 worker 会被围栏挡住）。
        """
        t = now if now is not None else time.time()
        if self.current is not None and not self.current.is_expired(t):
            raise JobError("★ 会话 %s 已被 %r 持有（★ 未过期）⇒ **只能一个执行者**"
                           % (self.session_id, self.current.holder))
        self.fence = self.fence.next()
        self._acquisitions += 1
        self.current = Lease(holder=holder, token=self.fence.value,
                             expires_at=t + ttl_seconds, ttl_seconds=ttl_seconds)
        return self.current

    def renew(self, holder: str, token: int, *, now: float | None = None) -> bool:
        """★ 续期（★ **必须**带对令牌 —— ★ 否则那是过期的 worker）。"""
        if self.current is None or self.current.holder != holder:
            return False
        if not self.fence.accepts(token):
            return False
        self.current.renew(now)
        return True

    def may_modify(self, holder: str, token: int, *, now: float | None = None) -> bool:
        """★★★★ **能不能改**（★ EC04-T02 逐字：★「★ **过期 worker 不能继续修改**」）。

        ★★ 三条都要满足：★ ① 有当前租约；★ ② 持有人一致；★ ③ **令牌是当前的** 且 **未过期**。
        """
        t = now if now is not None else time.time()
        if self.current is None:
            return False
        if self.current.holder != holder:
            return False
        if not self.fence.accepts(token):
            return False
        return not self.current.is_expired(t)


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 版本绑定（★ EC04-T03 —— ★ 「旧证据不能放行新模型」）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class VersionBinding:
    """★★★ **批准绑三个版本**（★ EC04-T03 逐字：★「★ 比较并交换模型版本；
    ★ **批准绑定 contract/plan/model 版本**，★ **跨版本立即失效**」）。

    ★★★ **验收（★ 计划逐字）**：★「★ **旧证据不能放行新模型**」。
    """

    contract_hash: str
    plan_hash: str
    model_revision: str

    def matches(self, contract_hash: str, plan_hash: str, model_revision: str) -> bool:
        """★★★ **三版本全等才算匹配**（★ 任何一个变了 ⇒ **立即失效**）。"""
        return (self.contract_hash == contract_hash
                and self.plan_hash == plan_hash
                and self.model_revision == model_revision)

    def invalidated_by(self, contract_hash: str, plan_hash: str,
                       model_revision: str) -> list[str]:
        """★ **哪几个版本变了**（★ 具名 —— ★ 便于定位）。"""
        bad = []
        if self.contract_hash != contract_hash:
            bad.append("contract")
        if self.plan_hash != plan_hash:
            bad.append("plan")
        if self.model_revision != model_revision:
            bad.append("model")
        return bad


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 证据链（★ EC04-T07）
# ══════════════════════════════════════════════════════════════════════

#: ★★ **敏感字段**（★ 与 EC00 的 `data-model.md` §七 **同一套**）
SENSITIVE_KEYS = ("token", "api_key", "apikey", "password", "authorization",
                  "secret", "credential", "private_key")


@dataclass
class ArtifactRecord:
    """★ 工件记录（★ EC04-T07 逐字：★「★ `Artifact`/`EvidenceManifest` **哈希、相对路径**、
    ★ **敏感信息过滤**和**保留策略**」）。"""

    relative_path: str                    #: ★★ **相对路径**（★ 不是绝对 —— ★ 防泄漏本机结构）
    sha256: str
    bytes_size: int = 0
    retention_days: int = 90              #: ★ 保留策略

    def is_relative(self) -> bool:
        """★★ **必须是相对路径**（★ 绝对路径会泄漏本机目录结构）。"""
        p = self.relative_path.replace("\\", "/")
        return not (p.startswith("/") or (len(p) > 1 and p[1] == ":"))

    def is_valid(self) -> bool:
        return (self.is_relative()
                and self.sha256.startswith("sha256:")
                and len(self.sha256) == len("sha256:") + 64)


def filter_sensitive(payload: dict) -> dict:
    """★★ **敏感信息过滤**（★ EC04-T07 逐字 —— ★ 与 EC00 的脱敏**同一口径**）。

    ★★ 判据：★ 键名命中 `SENSITIVE_KEYS` ⇒ ★ **值替换为 `***REDACTED***`**（★ **不是删键**
      —— ★ 删了就看不出「这里本该有个东西」）。
    """
    out: dict = {}
    for k, v in (payload or {}).items():
        if isinstance(v, dict):
            out[k] = filter_sensitive(v)
        elif str(k).strip().lower() in SENSITIVE_KEYS:
            out[k] = "***REDACTED***"
        else:
            out[k] = v
    return out


@dataclass
class EvidenceChain:
    """★★ **证据链**（★ 逐条**绑定版本** —— ★ 「旧证据不能放行新模型」）。"""

    records: list = field(default_factory=list)

    def add(self, binding: VersionBinding, artifact: ArtifactRecord, *,
            payload: dict | None = None) -> dict:
        rec = {
            "binding": binding,
            "artifact": artifact,
            "payload": filter_sensitive(payload or {}),
            "chain_index": len(self.records),
            #: ★★ **上一条的哈希** ⇒ ★ 链式（★ 改中间一条就断链）
            "prev": (self.records[-1]["self_hash"] if self.records else ""),
        }
        blob = json.dumps({
            "c": [binding.contract_hash, binding.plan_hash, binding.model_revision],
            "a": [artifact.relative_path, artifact.sha256],
            "p": rec["payload"], "i": rec["chain_index"], "prev": rec["prev"],
        }, ensure_ascii=False, sort_keys=True, default=str)
        rec["self_hash"] = "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
        self.records.append(rec)
        return rec

    def verify_chain(self) -> bool:
        """★★ **链完整**（★ 逐条重算 + 校验 `prev`）。"""
        prev = ""
        for i, rec in enumerate(self.records):
            if rec.get("prev", "") != prev or rec.get("chain_index") != i:
                return False
            blob = json.dumps({
                "c": [rec["binding"].contract_hash, rec["binding"].plan_hash,
                      rec["binding"].model_revision],
                "a": [rec["artifact"].relative_path, rec["artifact"].sha256],
                "p": rec["payload"], "i": rec["chain_index"], "prev": rec["prev"],
            }, ensure_ascii=False, sort_keys=True, default=str)
            want = "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
            if rec.get("self_hash") != want:
                return False
            prev = want
        return True

    def releasing_records(self, contract_hash: str, plan_hash: str,
                          model_revision: str) -> list:
        """★★★★ **能放行当前版本的证据**（★ **旧证据不在内** —— ★ 验收核心）。

        ★★ 依据（★ 计划逐字）：★「★ **旧证据不能放行新模型**」。
        """
        return [r for r in self.records
                if r["binding"].matches(contract_hash, plan_hash, model_revision)]


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 独立验收器（★ EC04-T06）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class IndependentVerifier:
    """★★★ **独立验收器**（★ EC04-T06 逐字：★「★ **独立验收器只读最终模型**；
    ★ **不把同一 Agent 自评当放行者**」）。

    ★★★ **验收（★ 计划逐字）**：★「★ 没有许可/权限的动作**停在设计建议**」。
    """

    executor_id: str                      #: ★ 执行者（★ 与验收者**必须不同**）
    verifier_id: str                      #: ★ 验收者
    read_only: bool = True                #: ★★ **只读**（★ 不改模型）

    def may_verify(self) -> bool:
        """★★★ **同一 Agent 不能自评**（★ EC04-T06 逐字）。"""
        return bool(self.verifier_id) and self.verifier_id != self.executor_id

    def verdict(self, *, checks_passed: bool, authorized: bool) -> str:
        """★★★ **验收结论**（★ 三条门）。

        ★★ ① **自评 ⇒ 拒**；★ ② **无许可/权限 ⇒ 停在设计建议**；★ ③ 只读 + 检查通过 ⇒ 放行。
        """
        if not self.may_verify():
            return "reject-self-review"
        if not self.read_only:
            return "reject-not-read-only"
        if not authorized:
            #: ★★★ **停在设计建议**（★ 不是「通过」也不是「失败」）
            return "design_advice_only"
        return "pass" if checks_passed else "fail"


# ══════════════════════════════════════════════════════════════════════
# 六、★★★★ 恢复（★ EC04-T05 —— ★ **不宣称全局事务**）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class RecoveryPlan:
    """★★★ **阶段检查点与前向补偿**（★ EC04-T05 逐字：★「★ 阶段检查点与前向补偿；
    ★ **不宣称 COM 有数据库式全局事务**」）。

    ★★★ **验收（★ 计划逐字）**：★「★ **失败不丢用户文件**」。
    """

    checkpoints: list = field(default_factory=list)
    #: ★★★ **显式声明**：★ COM **没有**全局事务
    HAS_GLOBAL_TRANSACTION = False

    def add_checkpoint(self, stage: str, artifact: str) -> None:
        self.checkpoints.append({"stage": stage, "artifact": artifact})

    def forward_compensation(self, failed_stage: str) -> dict:
        """★★★ **前向补偿**（★ 不是「回滚」 —— ★ 因为**没有事务**）。

        ★★ 依据（★ EC04-T05 逐字）：★ COM **不是**数据库 ⇒ ★ 只能**向前**补（★ 或停下）。
        ★★ **⇒ 绝不删用户文件**（★ 那是「失败不丢用户文件」的硬要求）。
        """
        idx = next((i for i, c in enumerate(self.checkpoints)
                    if c["stage"] == failed_stage), None)
        if idx is None:
            return {"ok": False, "reason": "★ 找不到阶段 %r 的检查点" % failed_stage}
        return {
            "ok": True,
            "strategy": "forward_compensation",
            "rollback_available": False,          #: ★★★ **没有回滚**（★ 无事务）
            "from_checkpoint": self.checkpoints[idx]["artifact"],
            "deletes_user_files": False,          #: ★★★ **绝不删**
            "basis": ("★ COM 无全局事务（★ `HAS_GLOBAL_TRANSACTION = False`）"
                      "⇒ ★ 用**前向补偿**，★ **不删任何文件**"),
        }


# ══════════════════════════════════════════════════════════════════════
# 七、★★★★ 纯离线自证（★ 与 EC03 同族）
# ══════════════════════════════════════════════════════════════════════

COM_MODULE_MARKERS = ("win32com", "comtypes", "pythoncom", "pywintypes",
                      "SldWorks", "sw_connect", "sw_part", "sw_session")


def assert_no_com_imports() -> dict:
    """★★★ **纯离线自证**（★ 本模块**不 import** 任何 COM 模块）。

    ★★ 依据（★ 承 EC03 的同名函数）：★ 让「作业与证据层」在**没有 SolidWorks 的机器上**也能验。
    """
    import pathlib
    src = pathlib.Path(__file__).read_text(encoding="utf-8", errors="replace")
    hits = []
    for ln in src.splitlines():
        s = ln.strip()
        if not (s.startswith("import ") or s.startswith("from ")):
            continue
        for marker in COM_MODULE_MARKERS:
            if marker in s:
                hits.append(s)
    return {"ok": not hits, "offending_imports": hits}


# ══════════════════════════════════════════════════════════════════════
# 八、★★★★★ 故障注入（★ FR-008 · EC04-T08 —— ★ **可离线注入的三类**）
# ══════════════════════════════════════════════════════════════════════

class InjectionKind:
    """★★ 可**离线**注入的故障（★ EC04-T08 逐字点名的四类里，★ **前三类不需要 COM**）。

    ★★ 第四类（★ 模态框/读写失败）**需要 COM** ⇒ ★ **属 EC05**（★ 如实登记，★ 不假装做了）。
    """

    WORKER_EXIT = "worker_exit"                  #: ★ worker 退出
    APPROVAL_EXPIRED = "approval_expired"        #: ★ 审批过期
    MODEL_EXTERNALLY_MODIFIED = "model_externally_modified"  #: ★ 模型被外部修改
    #: ★★ **需要 COM** ⇒ ★ 本层**不注入**（★ 属 EC05）
    MODAL_OR_IO_FAILURE = "modal_or_io_failure"

    OFFLINE_INJECTABLE = (WORKER_EXIT, APPROVAL_EXPIRED, MODEL_EXTERNALLY_MODIFIED)
    REQUIRES_COM = (MODAL_OR_IO_FAILURE,)


def inject_worker_exit(lease: NodeLease, holder: str, token: int, *,
                       now: float | None = None) -> dict:
    """★★★ **注入 ①：worker 退出**（★ 判据：★ 它**不能再改**，★ 但**别人可以接手**）。"""
    can_still_modify = lease.may_modify(holder, token, now=now)
    t = now if now is not None else time.time()
    if lease.current is not None and lease.current.holder == holder:
        lease.current.expires_at = t            #: ★ 立刻过期（★ 等价于「它走了」）
    return {
        "kind": InjectionKind.WORKER_EXIT,
        "could_modify_before_exit": can_still_modify,
        "can_modify_after_exit": lease.may_modify(holder, token, now=t),
        "lease_releasable": lease.current is None or lease.current.is_expired(t),
        "ok": True,
    }


def inject_approval_expired(binding: VersionBinding, *, current_contract: str,
                            current_plan: str, current_model: str) -> dict:
    """★★★ **注入 ②：审批过期**（★ 判据：★ **旧批准不能放行新版本**）。"""
    changed = binding.invalidated_by(current_contract, current_plan, current_model)
    return {
        "kind": InjectionKind.APPROVAL_EXPIRED,
        "still_valid": not changed,
        "invalidated_by": changed,
        "ok": True,
    }


def inject_model_externally_modified(binding: VersionBinding, *,
                                     new_model_revision: str) -> dict:
    """★★★ **注入 ③：模型被外部修改**（★ 判据：★ **旧证据立即失效**）。"""
    return {
        "kind": InjectionKind.MODEL_EXTERNALLY_MODIFIED,
        "old_revision": binding.model_revision,
        "new_revision": new_model_revision,
        "evidence_still_releases": binding.matches(
            binding.contract_hash, binding.plan_hash, new_model_revision),
        "ok": True,
    }


def injection_coverage() -> dict:
    """★★ **故障注入覆盖表**（★ 如实 —— ★ 哪些能离线注、哪些要 COM）。"""
    return {
        "offline_injectable": list(InjectionKind.OFFLINE_INJECTABLE),
        "requires_com": list(InjectionKind.REQUIRES_COM),
        "note": ("★ 第四类（★ 模态框/读写失败）**需要真实 COM** ⇒ ★ **属 EC05**；"
                 "★ 本层**不假装做了**"),
    }
