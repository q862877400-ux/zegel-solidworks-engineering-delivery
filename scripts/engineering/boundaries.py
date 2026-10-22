"""★ Q15 · 运行边界：事务边界 / 无人值守门槛 / 回收 / 磁盘 / 公网（规格 326 的 S15~S19）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/boundaries.py
# 定位:   规格 `specs/326-question-persistence-and-boundaries` 的 S15（事务边界）/S16
#           （无人值守需独立执行身份）/ S17（回收只针对自有实例）/S18（磁盘不足拒开始）/
#            S19（执行进程不访问公网）。★★ 实测（2026-10-12）起点：`jobs.HAS_GLOBAL_TRAN
#           SACTION` 与`authorization.check_path`（只写 output）**已有**；★ 而**没有无人
#           值守门槛、没有回收判据、没有磁盘判据、没有公网判据**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q15（L299-327）逐字：L314「事
#           务边界是「**自有副本＋已验证检查点＋提交清单**」，  **不是 COM 撤销栈**。失
#           败分支保留，不能冒称原地回滚成功」L317「对**无人值守安全承诺**，必须有**独立
#           执行身份或等效沙箱**，  原始业务文件对执行进程**不可写**；……**当前环境若达不
#           到此门槛，  就只提供有人值守模式，不宣称无人值守安全**」L319「「**只写 outpu
#           t**」约束所有业务产物。……**本轮不创建账户、  不更改注册表或系统策略**」L315
#           「**自动回收只能针对可证明由本任务拥有、且没有业主文档的实例**。  否则**停住
#           ，不杀进程、不点保存提示**」L324「**磁盘不足以容纳下一检查点、暂存及保留版本
#           就拒绝开始**；  **不自动清删证据或旧 CAD**」L327「网络、数据密级和预算**在进
#           入云端客户端之前**控制；  **执行进程不访问公网**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import shutil
from dataclasses import dataclass, field

#: ══════════════════════════════════════════════════════════════════════
# 一、事务边界（★ S15 —— ★ Q15 L314）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **事务边界的三个组成部分**（★ Q15 L314 逐字）
TRANSACTION_PARTS = ("own_copy", "verified_checkpoint", "commit_manifest")

#: ★★ **它不是**什么（★ Q15 L314 逐字：「**不是 COM 撤销栈**」）
NOT_A_TRANSACTION = ("com_undo_stack", "in_place_rollback")

#: ★★ **全局事务 = False**（★ 与 `jobs.HAS_GLOBAL_TRANSACTION` 同口径）
HAS_GLOBAL_TRANSACTION = False


def transaction_boundary() -> dict:
    """★★ **如实声明事务边界**（★ S15 —— ★ Q15 L314 逐字）。

    ★★ 判据：**明确说"不是 COM 撤销栈"**，★ 且**失败分支保留**
      （★ Q15 L314 逐字：「失败分支保留，**不能冒称原地回滚成功**」）。
    """
    return {
        "boundary": TRANSACTION_PARTS,
        "is": "自有副本 + 已验证检查点 + 提交清单",
        "is_not": NOT_A_TRANSACTION,
        "has_global_transaction": HAS_GLOBAL_TRANSACTION,
        "on_failure": "KEEP_FAILURE_BRANCH",
        "rollback_claim": False,
        "★": (
            "★ Q15 L314：「事务边界是『自有副本＋已验证检查点＋提交清单』，"
            "**不是 COM 撤销栈**」；★ **不冒称原地回滚成功**"
        ),
    }


#: ══════════════════════════════════════════════════════════════════════
# 二、无人值守门槛（★ S16 —— ★ Q15 L317）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **无人值守安全承诺的四个门槛**（★ Q15 L317 逐字）
UNATTENDED_REQUIREMENTS = (
    "separate_execution_identity",  #: 独立执行身份
    "business_files_readonly",  #: 原始业务文件对执行进程不可写
    "no_prompt_based_isolation",  #: ★ **不能靠提示词限制写入**
    "os_level_isolation",  #: 或等效沙箱
)


@dataclass
class AttendedMode:
    """★★ **有人值守 / 无人值守的门槛**（★ S16 —— ★ Q15 L317 逐字）。

    ★★ Q15 L317 逐字：「**当前环境若达不到此门槛，就只提供有人值守模式，
      不宣称无人值守安全**」。

    ★★ 判据（★ **结构性**）：
      ```
      ① 四个门槛**全满足** ⇒ 可宣称无人值守
      ② ★★ **任一不满足** ⇒ `mode=attended`，★ 且
         **`unattended_claim` 必须是 False**（★ 不许含糊）
      ```
    """

    separate_execution_identity: bool = False
    business_files_readonly: bool = False
    os_level_isolation: bool = False
    #: ★★ 注意：**「靠提示词限制写入」不算隔离** —— ★ 它在这张表里是**反面**
    prompt_based_isolation_only: bool = True

    def evaluate(self) -> dict:
        met = {
            "separate_execution_identity": self.separate_execution_identity,
            "business_files_readonly": self.business_files_readonly,
            "os_level_isolation": self.os_level_isolation,
            #: ★★ 「只靠提示词」⇒ **这一条不满足**
            "no_prompt_based_isolation": not self.prompt_based_isolation_only,
        }
        missing = [k for k, v in met.items() if not v]
        unattended = not missing
        return {
            "mode": "unattended" if unattended else "attended",
            "met": met,
            "missing": missing,
            #: ★★ **结构性保证**：不满足 ⇒ **明确不许宣称**
            "unattended_claim": unattended,
            "★": (
                "★ Q15 L317：「达不到此门槛，就**只提供有人值守模式**，"
                "**不宣称无人值守安全**」"
                + ("" if unattended else " ⇒ ★ 当前：**只提供有人值守**")
            ),
        }

    def to_dict(self) -> dict:
        return self.evaluate()


def current_environment_mode() -> dict:
    """★★ **本机环境的实际判定**（★ 如实 —— ★ 不美化）。

    ★ 依据（★ Q15 L317 + L319 逐字）：★ 本轮**不创建账户、不改注册表或系统策略**
      ⇒ ★ 独立执行身份与 OS 级隔离**都没做** ⇒ ★ **只能宣称有人值守**。
    """
    return AttendedMode(
        separate_execution_identity=False,
        business_files_readonly=False,
        os_level_isolation=False,
        prompt_based_isolation_only=True,
    ).evaluate() | {
        "why": (
            "★ Q15 L319 逐字：「本轮**不创建账户、不更改注册表或系统策略**」"
            " ⇒ 独立执行身份与 OS 级隔离**都没做**"
            " ⇒ ★ **只能宣称有人值守**（★ 不宣称无人值守安全）"
        ),
    }


#: ══════════════════════════════════════════════════════════════════════
# 三、自动回收（★ S17 —— ★ Q15 L315）
#: ══════════════════════════════════════════════════════════════════════


def can_reclaim(
    *, owned_by_this_task: bool, has_owner_documents: bool, process_name: str = ""
) -> dict:
    """★★ **能不能自动回收**（★ S17 —— ★ Q15 L315 逐字）。

    ★★ Q15 L315 逐字：「**自动回收只能针对可证明由本任务拥有、且没有业主文档的
      实例**。否则**停住，不杀进程、不点保存提示**」。

    ★★ 判据（★ 两条都要）：
      ```
      ① 可证明**由本任务拥有**
      ② ★ **没有业主文档**
      ```
      ★ 任一不满足 ⇒ **停住**（★ 且明确"不杀进程、不点保存提示"）。
    """
    if not owned_by_this_task:
        return {
            "reclaim": False,
            "reason": "★ 无法证明由本任务拥有",
            "action": "STOP",
            "kill_process": False,
            "click_save": False,
            "★": "★ Q15 L315：「否则**停住，不杀进程、不点保存提示**」",
        }
    if has_owner_documents:
        return {
            "reclaim": False,
            "reason": "★ 该实例里有业主文档",
            "action": "STOP",
            "kill_process": False,
            "click_save": False,
            "★": "★ Q15 L315：同上",
        }
    return {
        "reclaim": True,
        "reason": "★ 自有且无业主文档",
        "action": "RECLAIM",
        "kill_process": True,
        "click_save": False,
        "★": "★ Q15 L315：可回收",
    }


#: ══════════════════════════════════════════════════════════════════════
# 四、磁盘（★ S18 —— ★ Q15 L324）
#: ══════════════════════════════════════════════════════════════════════


def disk_gate(
    *, free_bytes: int, needed_bytes: int, safety_factor: float = 1.5
) -> dict:
    """★★ **磁盘不足就拒绝开始**（★ S18 —— ★ Q15 L324 逐字）。

    ★★ Q15 L324 逐字：「**磁盘不足以容纳下一检查点、暂存及保留版本就拒绝开始**；
      **不自动清删证据或旧 CAD**」。

    ★★ 判据：`free < needed × safety_factor` ⇒ **拒**（★ 且**不自动清删**）。
    """
    need = int(needed_bytes * safety_factor)
    ok = free_bytes >= need
    return {
        "ok": ok,
        "free_bytes": free_bytes,
        "needed_bytes": needed_bytes,
        "with_safety": need,
        "action": "START" if ok else "REFUSE_START",
        #: ★★ **结构性保证**：**不自动清删**
        "auto_delete_evidence": False,
        "auto_delete_old_cad": False,
        "★": ("★ Q15 L324：「磁盘不足……就**拒绝开始**；**不自动清删证据或旧 CAD**」"),
    }


def disk_free(path: str = ".") -> int:
    """★ 读真实可用空间（★ 只读）。"""
    try:
        return int(shutil.disk_usage(path).free)
    except OSError:
        return -1


#: ══════════════════════════════════════════════════════════════════════
# 五、公网（★ S19 —— ★ Q15 L327）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **执行进程的网络策略**（★ Q15 L327 逐字）
EXECUTION_NETWORK_POLICY = "deny"
#: ★★ **谁可以访问网络**：★ 只有**云端客户端**（★ 且**在进入之前**控制）
NETWORK_ALLOWED_ACTORS = ("cloud_client",)
#: ★★ **执行进程**（★ 它**不许**碰网）
NETWORK_DENIED_ACTORS = ("execution_process", "cad_session", "solver")


def network_gate(
    actor: str, *, data_classified: bool = False, budget_checked: bool = False
) -> dict:
    """★★ **网络闸门**（★ S19 —— ★ Q15 L327 逐字）。

    ★★ Q15 L327 逐字：「网络、数据密级和预算**在进入云端客户端之前**控制；
      **执行进程不访问公网**」。

    ★★ 判据（★ 顺序）：
      ```
      ① 执行进程 / CAD 会话 / 求解器 ⇒ **一律拒**（★ 不看其他条件）
      ② 云端客户端 ⇒ 必须**已分级**且**已查预算**（★ 在进入之前）
      ```
    """
    if actor in NETWORK_DENIED_ACTORS:
        return {
            "allowed": False,
            "actor": actor,
            "code": "EXECUTION_NO_NETWORK",
            "reason": "★★ 执行进程**不访问公网**（★ Q15 L327 逐字）",
        }
    if actor not in NETWORK_ALLOWED_ACTORS:
        return {
            "allowed": False,
            "actor": actor,
            "code": "UNKNOWN_ACTOR",
            "reason": "★ 未知角色",
        }
    #: ★★ ① 在**进入之前**控制：分级与预算**都要先做**
    if not data_classified:
        return {
            "allowed": False,
            "actor": actor,
            "code": "NOT_CLASSIFIED",
            "reason": "★ 数据**未分级** ⇒ 不许进云端客户端（★ Q15 L327）",
        }
    if not budget_checked:
        return {
            "allowed": False,
            "actor": actor,
            "code": "BUDGET_UNCHECKED",
            "reason": "★ 预算**未查** ⇒ 不许进云端客户端（★ Q15 L327）",
        }
    return {
        "allowed": True,
        "actor": actor,
        "code": "",
        "reason": "★ 已分级 + 已查预算 ⇒ 放行",
    }


#: ══════════════════════════════════════════════════════════════════════
# 六、整体边界报告（★ S15~S19 一起）
#: ══════════════════════════════════════════════════════════════════════


def boundary_report(*, free_bytes: int | None = None, needed_bytes: int = 0) -> dict:
    """★ **运行边界总报告**（★ 如实报 —— ★ 不美化）。"""
    out: dict = {
        "transaction": transaction_boundary(),
        "unattended": current_environment_mode(),
        "network": {
            "policy": EXECUTION_NETWORK_POLICY,
            "allowed": list(NETWORK_ALLOWED_ACTORS),
            "denied": list(NETWORK_DENIED_ACTORS),
            "★": "★ Q15 L327：执行进程**不访问公网**",
        },
        "write_scope": "output-only",
    }
    if free_bytes is not None:
        out["disk"] = disk_gate(free_bytes=free_bytes, needed_bytes=needed_bytes)
    out["★"] = (
        "★ 事务边界=自有副本+检查点+清单（★ 不是 COM 撤销栈）· "
        "★ 无人值守门槛不达标 ⇒ 只提供有人值守 · "
        "★ 执行进程不访问公网 · ★ 只写 output"
    )
    return out
