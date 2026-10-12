"""★ Q7 · 规划上云、执行本地，离线保留确定性能力（规格 328 的 U1~U7）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/cloud_policy.py
# 定位:   规格 `specs/328-cloud-whitelist-and-degradation` 的 U1（离线承诺收窄）/
#           U2（不声称断网能自主）/ U3（关闭的能力清单）/ U4（固定快照）/
#           U5（降级顺序）/ U6（三条禁止）/ U7（业主三条拍板被尊重）。
#           ★★ 实测（2026-10-12）起点：云端白名单、数据分级、预算预占、
#           断网继续本地执行、KV 公式**都有表述**；
#           ★ 而**没有「关闭的能力」清单**、**没有降级顺序**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q7（L114-161）逐字：
#           L118-120「采用**路线 2**。……**已批准计划的执行、恢复、规则计算、
#             证据和交付管理必须离线可用**；**新需求的自主语义规划属于可关闭的
#             联网增强功能**。**断网不声称仍能自主处理任意新需求**」
#           L122「这是**显式收窄离线承诺**，不是措辞上的例外掩盖。
#             **当前只记录这一决策，不修改 AGENTS.md 或现有配置**」
#           L129「固定快照，通过项目评测后才能启用生产；**不跟随 latest 自动升级**」
#           L130「**关闭云端执行、文件托管、向量库、远程 shell 和云端 CAD 控制**」
#           L161「降级顺序：减少当前候选与上下文 → 卸载可选模型 → 退回人工／确定性
#             流程；**不与 SolidWorks 抢显存，不并行冷启动，不自动换成更低量化
#             然后继续声称质量不变**」
#           ★★ 业主 2026-10-12 三条拍板（★ 见 `metadata/cloud-policy.json`）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 本规格**全是静态判据**，不碰 SolidWorks）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
POLICY_FILE = ROOT / "metadata" / "cloud-policy.json"


class CloudPolicyError(Exception):
    """★ 云政策失败（★ 带封闭码）。"""

    CODES = ("no-policy", "claim-too-broad", "capability-enabled",
             "latest-tracking", "degradation-skipped", "vram_conflict",
             "local_model_service")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法云政策拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


def load_policy() -> dict:
    if not POLICY_FILE.is_file():
        raise CloudPolicyError("no-policy", "★ 没有 %s" % POLICY_FILE)
    return json.loads(POLICY_FILE.read_text(encoding="utf-8"))


#: ══════════════════════════════════════════════════════════════════════
# 一、离线承诺的收窄（★ U1/U2 —— ★ Q7 L118-122）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q7 L120 逐字：「**五类必须离线可用**」
OFFLINE_REQUIRED = ("approved_plan_execution", "recovery", "rule_computation",
                    "evidence", "delivery_management")


def offline_commitment(policy: dict | None = None) -> dict:
    """★★ **离线承诺**（★ U1 —— ★ Q7 L120 逐字）。

    ★★ 判据（★ 三条）：
      ```
      ① 五类**必须离线可用**
      ② **新需求规划**是**可关闭的联网增强**
      ③ ★★ **明确收窄**（★ 不是措辞掩盖）
      ```
    """
    p = (policy or load_policy())["offline_commitment"]
    return {
        "must_be_offline": list(p["must_be_offline"]),
        "offline_count": len(p["must_be_offline"]),
        "online_enhancement": list(p["online_enhancement"]),
        "online_can_be_disabled": bool(p["online_can_be_disabled"]),
        "offline_claim_narrowed": bool(p["offline_claim_narrowed"]),
        "★": ("★ Q7 L120：「已批准计划的执行、恢复、规则计算、证据和交付管理"
              "**必须离线可用**；新需求的自主语义规划属于**可关闭的联网增强**」"),
    }


def offline_verdict(*, online: bool) -> dict:
    """★★ **断网时的判定**（★ U2 —— ★ Q7 L120/L134 逐字）。

    ★★ Q7 L120 逐字：「**断网不声称仍能自主处理任意新需求**」。
    ★★ Q7 L134 逐字：「已批准计划继续本地执行；新需求改为**人工提交类型化
      需求／计划，或等待恢复**」。

    ★★ 判据（★ 结构性）：
      ```
      ① 已批准计划 ⇒ **继续本地执行**（★ 不看联网与否）
      ② 新需求 ⇒ 断网时 **`manual_or_wait`**
      ③ ★★ `autonomous_new_requirement` **永远是 False**（★ 断网时）
      ```
    """
    if online:
        return {"online": True,
                "approved_plan": "continue_local",
                "new_requirement": "autonomous_planning_available",
                "autonomous_new_requirement": True,
                "★": "★ 联网 ⇒ 新需求可走自主语义规划（★ 那是**可关闭的增强**）"}
    return {"online": False,
            "approved_plan": "continue_local",
            "new_requirement": "manual_or_wait",
            #: ★★ **结构性保证**：断网时**不许**声称能自主
            "autonomous_new_requirement": False,
            "★": ("★★ Q7 L120：「**断网不声称仍能自主处理任意新需求**」"
                  " ⇒ 新需求走**人工提交或等待**")}


def check_offline_claim(claim: str) -> dict:
    """★★ **检查一条离线声明有没有说过头**（★ U2 —— ★ W1 的判据）。

    ★★ 判据：声明里出现「断网 + 自主处理新需求」这种组合 ⇒ **检出**。
    """
    over = ("断网.*自主.*新需求", "离线.*自主.*任意", "断网.*仍能.*自主",
            "offline.*autonomous.*new")
    import re                                                           # noqa: PLC0415
    hit = [p for p in over if re.search(p, claim)]
    return {"ok": not hit, "hit": hit,
            "code": "" if not hit else "claim-too-broad",
            "★": "★ Q7 L120 逐字：断网**不声称**仍能自主处理任意新需求"}


#: ══════════════════════════════════════════════════════════════════════
# 二、关闭的能力（★ U3 —— ★ Q7 L130）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ Q7 L130 逐字：「关闭**云端执行、文件托管、向量库、远程 shell 和
#:   云端 CAD 控制**」—— **五项**
DISABLED_CAPABILITIES = ("cloud_execution", "file_hosting", "vector_store",
                         "remote_shell", "cloud_cad_control")


def disabled_capabilities(policy: dict | None = None) -> dict:
    """★★ **关闭的能力清单**（★ U3 —— ★ Q7 L130 逐字）。"""
    p = (policy or load_policy())["disabled_cloud_capabilities"]
    rows = {k: bool(p.get(k)) for k in DISABLED_CAPABILITIES}
    enabled = [k for k, v in rows.items() if v]
    return {"capabilities": rows, "n": len(rows),
            "all_disabled": not enabled, "enabled": enabled,
            "code": "" if not enabled else "capability-enabled",
            "★": "★ Q7 L130：五项**全关**（★ 云端执行/文件托管/向量库/远程 shell/云端 CAD）"}


#: ══ U4 固定快照（★ Q7 L129）══════════════════════════════════════════

def check_model_pinning(policy: dict | None = None) -> dict:
    """★★ **模型固定快照**（★ U4 —— ★ Q7 L129 逐字）。

    ★★ 判据：`follow_latest` 必须 **False**（★ 「**不跟随 latest 自动升级**」）。
    """
    p = (policy or load_policy())["cloud_whitelist"]
    bad = bool(p.get("follow_latest"))
    return {"ok": not bad, "snapshot": p.get("model_snapshot"),
            "follow_latest": bad, "provider": p.get("provider"),
            "code": "" if not bad else "latest-tracking",
            "★": "★ Q7 L129：「固定快照……**不跟随 latest 自动升级**」"}


#: ══ U5/U6 降级顺序 + 三条禁止（★ Q7 L161）════════════════════════════

#: ★★ Q7 L161 逐字的**三级降级顺序**
DEGRADATION_STEPS = ("reduce_candidates_and_context", "unload_optional_models",
                     "fall_back_to_manual_or_deterministic")

#: ★★ Q7 L161 逐字的**三条禁止**
DEGRADATION_FORBIDDEN = ("compete_with_solidworks_for_vram",
                         "parallel_cold_start", "silent_lower_quantization")


def degradation_order(policy: dict | None = None) -> dict:
    """★★ **降级顺序**（★ U5 —— ★ Q7 L161 逐字）。"""
    p = (policy or load_policy())["degradation_order"]
    return {"steps": list(p["steps"]), "n": len(p["steps"]),
            "forbidden": {k: bool(p["forbidden"].get(k))
                          for k in DEGRADATION_FORBIDDEN},
            "★": "★ Q7 L161：减少候选 → 卸载可选模型 → 退回人工／确定性"}


def check_degradation(*, used_steps: list,
                      policy: dict | None = None) -> dict:
    """★★ **降级路径合法性**（★ U5/U6 —— ★ W4/W5 的判据）。

    ★★ 判据（★ 两条）：
      ```
      ① ★★ **不许跳级** —— 用到的步骤必须是**前 N 级**（★ 从第 1 步起连续）
      ② 三条禁止**一条都不许犯**
      ```
    """
    p = (policy or load_policy())["degradation_order"]
    order = list(p["steps"])
    used = list(used_steps)
    #: ★ ① 连续性：用到的必须是**前缀**
    idx = [order.index(s) for s in used if s in order]
    contiguous = idx == list(range(len(idx))) if idx else True
    #: ★ ② 禁止项
    forbidden_hit = [k for k in DEGRADATION_FORBIDDEN
                     if p["forbidden"].get(k)]
    ok = contiguous and not forbidden_hit
    code = ""
    if not contiguous:
        code = "degradation-skipped"
    elif forbidden_hit:
        code = "vram_conflict"
    return {"ok": ok, "used": used, "contiguous": contiguous,
            "forbidden_hit": forbidden_hit, "code": code,
            "reason": ("★ 跳级：用到 %s 而不是前 %d 级" % (used, len(idx))
                       if not contiguous else
                       ("★ 犯了禁止项 %s" % forbidden_hit if forbidden_hit
                        else "★ 合法降级路径")),
            "★": ("★ Q7 L161：**不与 SolidWorks 抢显存，不并行冷启动，"
                  "不自动换成更低量化然后继续声称质量不变**")}


#: ══ U7 业主三条拍板（★ 2026-10-12）══════════════════════════════════

#: ★★ **业主三条拍板**（★ 原话见 `metadata/cloud-policy.json`）
OWNER_DECISIONS = ("no_local_model", "no_budget", "no_client_auth")


def owner_decisions(policy: dict | None = None) -> dict:
    """★★ **业主三条拍板被尊重**（★ U7）。

    ★★ 判据（★ 三条**都要**成立）：
      ```
      ① 本地模型生产服务 **没建**
      ② 预算引擎 **没实现**
      ③ 客户端认证 **没做**
      ```
    """
    p = policy or load_policy()
    rows = {
        "no_local_model": not bool(
            p["local_model"].get("production_service")),
        "no_budget": not bool(p["budget"].get("engine_implemented")),
        "no_client_auth": not bool(
            p["client_authentication"].get("implemented")),
    }
    bad = [k for k, v in rows.items() if not v]
    return {"decisions": rows, "respected": not bad, "violated": bad,
            "code": "" if not bad else "local_model_service",
            "★": ("★ 业主 2026-10-12 三条：「不考虑本地模型」·「不考虑预算」·"
                  "「客户端认证这个也不管」"),
            "owner_quotes": {
                "no_local_model": "为什么你们都在看什么本地模型，不考虑本地模型",
                "no_budget": "月预算 300 元 / 单任务 10 元 是怎么定的?"
                             "这个你别管了，不考虑预算",
                "no_client_auth": "「不认证未纳管客户端」这条怎么执行？"
                                  "这个也不管",
            }}


def check_no_local_service(*, builds: list) -> dict:
    """★ **不许偷建本地模型服务**（★ W6 的判据）。"""
    bad = [b for b in builds if "local_model" in b or "llm_server" in b]
    return {"ok": not bad, "built": bad,
            "code": "" if not bad else "local_model_service",
            "★": "★ 业主拍板：「**不考虑本地模型**」"}


def check_config_untouched() -> dict:
    """★ **`AGENTS.md` 与现有配置未被本规格改动**（★ Q7 L122 逐字）。"""
    p = load_policy()["not_modified"]
    ok = (not p.get("agents_md_modified")
          and not p.get("existing_config_modified"))
    return {"ok": ok,
            "agents_md_modified": bool(p.get("agents_md_modified")),
            "existing_config_modified": bool(
                p.get("existing_config_modified")),
            "★": "★ Q7 L122：「当前只记录这一决策，**不修改 AGENTS.md 或现有配置**」"}


#: ══ 总报告 ═══════════════════════════════════════════════════════════

def policy_report() -> dict:
    """★ **云政策总报告**（★ U1~U7 一起）。"""
    return {
        "offline": offline_commitment(),
        "offline_verdict_offline": offline_verdict(online=False),
        "offline_verdict_online": offline_verdict(online=True),
        "disabled": disabled_capabilities(),
        "pinning": check_model_pinning(),
        "degradation": degradation_order(),
        "owner_decisions": owner_decisions(),
        "config": check_config_untouched(),
        "★": ("★ 规划上云（★ 可关闭）· 执行本地（★ 五类离线可用）· "
              "★ 断网不声称能自主处理新需求 · ★ 五项云端能力全关 · "
              "★ 业主三条拍板被尊重"),
    }
