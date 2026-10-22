"""★ 阶段 3 · 崩溃恢复：检查点 + 提交清单 + 失效闭包 + 恢复判定（规格 318 的 E1/E2/E3）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/recovery.py
# 定位:   规格 `specs/318-stage3-crash-recovery` 的 E1（检查点+提交清单）/E2（失效闭包
#           ）/ E3（恢复判定）。★★ 实测（2026-10-12）起点：`jobs.py` 已有 `Lease` / `Nod
#           eLease` /`VersionBinding` / `ArtifactRecord` / `EvidenceChain` / `RecoveryPl
#           an`与 4 个测试，**而 5 个封闭码（COMMITTED / STALE / REVISION_CONFLICT /UNKN
#           OWN_EFFECT / BLOCKED_VERIFICATION）全仓没有**，也**没有三类崩溃窗口的注入与
#           恢复编排**、**没有失效闭包**。
# 官方依据: ① 外部方案阶段 3 的验收 S3-A / S3-B（逐字）② 本仓 `scripts/engineering/jobs.
#           py` 的既有资产（`FenceToken` /   `VersionBinding.matches` / `RecoveryPlan.HA
#           S_GLOBAL_TRANSACTION = False`）③ 本仓**事实 8**（返回值不可信 ⇒ 窗口②必须**
#           回读**判）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_stage3_recovery.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、封闭码（★ 新增码必须同时加进 `RESUME_CODES`，否则 `assert` 拦下）
#: ══════════════════════════════════════════════════════════════════════

REVISION_CONFLICT = "REVISION_CONFLICT"
STALE = "STALE"
UNKNOWN_EFFECT = "UNKNOWN_EFFECT"
COMMITTED = "COMMITTED"
BLOCKED_VERIFICATION = "BLOCKED_VERIFICATION"

RESUME_CODES = (REVISION_CONFLICT, STALE, UNKNOWN_EFFECT, COMMITTED,
                BLOCKED_VERIFICATION)


class RecoveryError(Exception):
    """★ 恢复期失败（★ 带封闭码）。"""

    CODES = (
        "no-evidence",              #: ★ 无证据 ⇒ 不得进清单（★ P1 突变要抓的）
        "not-applied",              #: ★ 还没生效 ⇒ 不得进清单
        "incomplete-artifact",      #: ★ 引用了不完整文件
        "revision-conflict",        #: ★ 版本冲突
        "lease-held",               #: ★ 会话已被别人持有
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法恢复拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 二、检查点（★ E1 —— ★ 三态对应三类崩溃窗口）
#: ══════════════════════════════════════════════════════════════════════

#: ★ 三态（★ 见 data-model §1）
STATE_INTENT = "intent"          #: 意图已落盘、COM **还没调** ⇒ ★ 窗口①
STATE_APPLIED = "applied"        #: COM 已生效、**结果还没记账** ⇒ ★ 窗口②
STATE_COMMITTED = "committed"    #: 已记账 + 证据齐 ⇒ 安全

ALL_STATES = (STATE_INTENT, STATE_APPLIED, STATE_COMMITTED)


@dataclass
class Checkpoint:
    stage: str
    intent_at: str = ""
    artifact: str = ""
    revision: str = ""
    evidence: str = ""
    state: str = STATE_INTENT

    def __post_init__(self) -> None:
        assert self.state in ALL_STATES, "★ 非法检查点状态：%r" % self.state

    @property
    def is_committable(self) -> bool:
        """★★ **能不能进提交清单**（★ 不变式 K1/K2）。

        ★★ 判据（★ 两条都要）：
          · `state == applied` —— ★ **`intent` 不够**（还没生效）
          · `evidence` 非空   —— ★ **「工具返回成功」不算证据**（★ P1 突变要抓的）
        """
        return self.state == STATE_APPLIED and bool(str(self.evidence).strip())


#: ══════════════════════════════════════════════════════════════════════
# 三、提交清单（★ E1 —— ★ FR-004/005/012）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class CommitManifest:
    entries: list = field(default_factory=list)
    revision: str = ""

    def add(self, cp: Checkpoint) -> dict:
        """★★ **入清单**（★ 只接受带证据的 `applied`）。

        ★★ 三条拒绝（★ 都抛，★ 不静默）：
          · `intent` 态        ⇒ `not-applied`（★ 还没生效）
          · 证据为空           ⇒ `no-evidence`（★ **这是 P1 突变的核心**）
          · 版本与清单不符     ⇒ `revision-conflict`
        """
        if cp.state != STATE_APPLIED:
            raise RecoveryError(
                "not-applied",
                "★ %s 还在 %r 态（★ 只有 `applied` 能进清单）" % (cp.stage, cp.state))
        if not str(cp.evidence).strip():
            raise RecoveryError(
                "no-evidence",
                "★ %s **没有证据** ⇒ 不得标 %s（★ 「工具返回成功」不是证据）"
                % (cp.stage, COMMITTED))
        if self.revision and cp.revision and cp.revision != self.revision:
            raise RecoveryError(
                "revision-conflict",
                "★ %s 的 revision=%r ≠ 清单的 %r" % (cp.stage, cp.revision,
                                                     self.revision))
        if not self.revision and cp.revision:
            self.revision = cp.revision
        #: ★ 入清单时**升态**
        cp.state = STATE_COMMITTED
        self.entries.append(cp)
        return {"ok": True, "stage": cp.stage, "state": cp.state,
                "revision": self.revision}

    @property
    def stages(self) -> list:
        return [e.stage for e in self.entries]

    @property
    def complete(self) -> bool:
        """★ 清单里**每条**都有证据（★ 不变式 K1 的总体判据）。"""
        return bool(self.entries) and all(
            str(e.evidence).strip() for e in self.entries)

    def references_incomplete(self) -> list:
        """★ 引用了**不完整文件**的条目（★ SC-005 / FR-012）。

        ★ 判据：产物路径非空，而证据（sha256）为空或不是 64 位十六进制。
        """
        bad = []
        for e in self.entries:
            if not e.artifact:
                continue
            ev = str(e.evidence).strip()
            hexpart = ev.split(":")[-1]
            if len(hexpart) != 64 or not all(
                    c in "0123456789abcdef" for c in hexpart.lower()):
                bad.append(e.stage)
        return bad

    def duplicate_stages(self) -> list:
        """★ **重复的阶段**（★ SC-005：恢复后不得含重复操作）。

        ★ 判据：同一个 `stage` 出现 >1 次 ⇒ 说明**重放没有跳过已生效的**。
        """
        seen: dict[str, int] = {}
        for e in self.entries:
            seen[e.stage] = seen.get(e.stage, 0) + 1
        return sorted(k for k, v in seen.items() if v > 1)

    def to_dict(self) -> dict:
        return {"revision": self.revision, "complete": self.complete,
                "entries": [{"stage": e.stage, "state": e.state,
                             "artifact": e.artifact, "evidence": e.evidence[:24]}
                            for e in self.entries]}


#: ══════════════════════════════════════════════════════════════════════
# 四、失效闭包（★ E2 —— ★ FR-006/007）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class InvalidationClosure:
    changed: list = field(default_factory=list)
    stale_nodes: list = field(default_factory=list)
    untouched_nodes: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.changed) and bool(self.stale_nodes)


def invalidation_closure(nodes: list, changed: list) -> InvalidationClosure:
    """★★ **失效闭包**（★ E2）：变了哪几个版本 ⇒ **哪些节点要重新验证**。

    ★★ 算法（★ 见 data-model §3）：
      ```
      ① 直接依赖 changed 的节点 ⇒ STALE
      ② 传递依赖 ① 的节点       ⇒ STALE（★ 闭包）
      ③ 其余                    ⇒ untouched
      ```
    ★★ **为什么不能「全都标脏」**（★ FR-007）：那是**保守到失去能力** ——
      ★ 阶段 6 的反向验证专门抓这一类（「将一切图中有环都拒绝」必须失败）。
      ★ 同族纪律：**只改一个变量检验一个失效机制**。

    :param nodes: `[{name, depends_on: [版本键]}]`
    :param changed: 变了的版本键（★ 来自 `VersionBinding.invalidated_by`）
    """
    ch = set(changed or ())
    #: ★ 建反向索引：版本键 → 直接依赖它的节点
    by_dep: dict[str, list[str]] = {}
    for n in nodes or ():
        for d in (n.get("depends_on") or ()):
            by_dep.setdefault(d, []).append(n["name"])

    stale: set[str] = set()
    #: ① 直接依赖
    for d in ch:
        stale.update(by_dep.get(d, ()))
    #: ② 传递闭包（★ 依赖「已脏节点」的也要脏）
    grew = True
    while grew:
        grew = False
        for n in nodes or ():
            if n["name"] in stale:
                continue
            if any(x in stale for x in (n.get("depends_on") or ())):
                stale.add(n["name"])
                grew = True
    untouched = [n["name"] for n in (nodes or ()) if n["name"] not in stale]
    return InvalidationClosure(changed=sorted(ch),
                               stale_nodes=sorted(stale),
                               untouched_nodes=untouched)


#: ══════════════════════════════════════════════════════════════════════
# 五、恢复判定（★ E3 —— ★ FR-008/009）
#: ══════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ResumeVerdict:
    ok: bool
    code: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.ok:
            assert self.code in RESUME_CODES, "★ 非法恢复码：%r" % self.code


def resume_verdict(*, submitted_revision: str, current_revision: str,
                   stale_nodes: list = (), unknown_effect: bool = False) -> ResumeVerdict:
    """★★ **能不能续跑**（★ E3）。

    ★★ 判据顺序（★ **最严的在前** —— ★ 与阶段 2 的七档同族）：
      ```
      ① 效应不明          ⇒ UNKNOWN_EFFECT（★ 连该回读什么都不知道 ⇒ 停下交人）
      ② revision 冲突     ⇒ REVISION_CONFLICT（★ **不接受该提交**）
      ③ 有 STALE 节点     ⇒ STALE（★ 要重新验证）
      ④ 都不沾            ⇒ ok
      ```
    ★★ **为什么 `UNKNOWN_EFFECT` 排第一**：它说的是「**连该回读什么都不知道**」，
      而 `REVISION_CONFLICT` 至少还知道该拿哪两个版本比。
      ★ 先判它 ⇒ 不会用「版本对得上」掩盖「效应不明」。
    """
    if unknown_effect:
        return ResumeVerdict(
            False, UNKNOWN_EFFECT,
            "★ 效应不明（★ 不重试、不标完成、不续跑 —— ★ 停下交人）")
    if str(submitted_revision or "") != str(current_revision or ""):
        return ResumeVerdict(
            False, REVISION_CONFLICT,
            "★ 提交的 revision=%r ≠ 当前 %r ⇒ **不接受该提交**"
            % (submitted_revision, current_revision))
    if stale_nodes:
        return ResumeVerdict(
            False, STALE,
            "★ 有 %d 个节点已失效 ⇒ 要重新验证：%s"
            % (len(stale_nodes), list(stale_nodes)[:6]))
    return ResumeVerdict(True, detail="★ 版本一致、无失效节点、效应明确 ⇒ 可续跑")


#: ══════════════════════════════════════════════════════════════════════
# 六、三类崩溃窗口（★ E1 —— ★ 验收 S3-A）
#: ══════════════════════════════════════════════════════════════════════

BEFORE_CALL = "before_call"      #: ★ 窗口① 意图落盘后、调用前
AFTER_EFFECT = "after_effect"    #: ★ 窗口② 生效未记账
AFTER_SAVE = "after_save"        #: ★ 窗口③ 保存未发布

CRASH_WINDOWS = (BEFORE_CALL, AFTER_EFFECT, AFTER_SAVE)


class InjectedCrash(Exception):
    """★ 注入的崩溃（★ 带窗口名）。"""

    def __init__(self, window: str) -> None:
        assert window in CRASH_WINDOWS, "★ 非法崩溃窗口：%r" % window
        self.window = window
        super().__init__("★ 注入崩溃 @ %s" % window)


@dataclass
class ReplayJournal:
    """★ 重放日志（★ 判「有没有重复操作」的**唯一判据**）。

    ★★ 为什么需要它：SC-005 要求「恢复后的发布产物**不含重复操作**」——
      ★ 判据是**副作用计数**，不是「跑完了」。
    """

    side_effects: list = field(default_factory=list)

    def record(self, stage: str) -> None:
        self.side_effects.append(stage)

    def count(self, stage: str) -> int:
        return self.side_effects.count(stage)

    def duplicates(self) -> list:
        seen: dict[str, int] = {}
        for s in self.side_effects:
            seen[s] = seen.get(s, 0) + 1
        return sorted(k for k, v in seen.items() if v > 1)


def resume_from_checkpoints(manifest: CommitManifest, stages: list,
                            journal: ReplayJournal, *,
                            readback=None) -> dict:
    """★★ **从已提交检查点恢复**（★ E1 —— ★ FR-002/005）。

    ★★ 判据（★ 三个窗口各不相同）：
      · **窗口①**（`intent`）⇒ ★ **重放安全**（还没生效）
      · **窗口②**（`applied`）⇒ ★★ **必须先回读**：
          回读说「已有」⇒ **跳过**（★ 不重复打孔）；
          回读说「没有」⇒ 重放
      · **窗口③**（`committed`）⇒ 已在清单里 ⇒ **跳过**

    ★★ `readback(stage) -> bool` 是**回读判据**（★ 事实 8：返回值不可信）。
      ★ 没给 `readback` 时：对 `applied` 态**拒绝重放**（★ 保守 —— ★ 宁可停，不重复打孔）。
    """
    #: ★★ **只有 `committed` 才算「已在清单里」** ——
    #:   ⚠ 实测（2026-10-12）：第一版用 `set(manifest.stages)` 判，
    #:     而 `entries` 里可能有**没进清单的 `applied`**（★ 那正是窗口②）
    #:     ⇒ 它会被误判成「已提交」⇒ **跳过而不回读** ⇒ ★★ 窗口② 的判据失效。
    #:   ⇒ ★ 判据必须是 **`state == committed`**，不是「在 entries 里」。
    committed = {e.stage for e in manifest.entries
                 if e.state == STATE_COMMITTED}
    done: list = []
    skipped: list = []
    replayed: list = []

    for st in stages:
        if st in committed:
            skipped.append({"stage": st, "why": "★ 已在提交清单里（窗口③）"})
            continue
        #: ★ 找该阶段的检查点（★ **只认 `applied`** —— ★ `committed` 已在上面跳过）
        cp = next((c for c in manifest.entries
                   if c.stage == st and c.state == STATE_APPLIED), None)
        if cp is not None:
            if readback is None:
                #: ★★ 保守：不知道生效没有 ⇒ **不重放**（★ 宁可停，不重复打孔）
                skipped.append({"stage": st,
                                "why": "★ 是 `applied` 态而没有 `readback` ⇒ "
                                       "**拒绝重放**（★ 不重复打孔）"})
                continue
            if readback(st):
                skipped.append({"stage": st,
                                "why": "★ 回读说「已有」⇒ 跳过（★ 不重复打孔）"})
                continue
        #: ★ 重放（★ 窗口① 与「回读说没有」的窗口②）
        journal.record(st)
        done.append(st)
        replayed.append(st)

    return {"ok": True, "done": done, "skipped": skipped, "replayed": replayed,
            "duplicates": journal.duplicates(),
            "no_duplicates": not journal.duplicates()}


#: ══════════════════════════════════════════════════════════════════════
# 七、辅助：算证据（★ 用**内容摘要**，不是「返回值」）
#: ══════════════════════════════════════════════════════════════════════

def evidence_of(payload: object) -> str:
    """★ 由**内容**算证据（★ 不是「工具返回成功」那种东西）。"""
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()
