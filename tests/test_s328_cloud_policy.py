"""★ 规格 328 契约测试：云政策 + 离线承诺 + 降级顺序（Q7 的 U1~U7）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s328_cloud_policy.py
# 定位:   规格 `specs/328-cloud-whitelist-and-degradation` 的 U1~U7 契约测试
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q7（L114-161）逐字
#           ② `metadata/cloud-policy.json`
#           ③ ★★ 业主 2026-10-12 三条拍板
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

from scripts.engineering import cloud_policy as CP                       # noqa: E402


#: ══ U1 离线承诺 ══════════════════════════════════════════════════════

def test_five_offline_required() -> None:
    """★★★ Q7 L120 逐字：「**已批准计划的执行、恢复、规则计算、证据和
    交付管理必须离线可用**」。"""
    c = CP.offline_commitment()
    assert c["offline_count"] == 5
    assert set(c["must_be_offline"]) == set(CP.OFFLINE_REQUIRED)


def test_planning_is_online_enhancement() -> None:
    """★★ Q7 L120 逐字：「**新需求的自主语义规划属于可关闭的联网增强功能**」。"""
    c = CP.offline_commitment()
    assert "new_requirement_semantic_planning" in c["online_enhancement"]
    assert c["online_can_be_disabled"] is True


def test_offline_claim_is_narrowed() -> None:
    """★★ Q7 L122 逐字：「这是**显式收窄离线承诺**，不是措辞上的例外掩盖」。"""
    assert CP.offline_commitment()["offline_claim_narrowed"] is True


#: ══ U2 不声称断网能自主 ══════════════════════════════════════════════

def test_offline_does_not_claim_autonomy() -> None:
    """★★★ Q7 L120 逐字：「**断网不声称仍能自主处理任意新需求**」。

    ★★ 判据：断网时 **`autonomous_new_requirement` 必须是 `False`**。
    """
    v = CP.offline_verdict(online=False)
    assert v["autonomous_new_requirement"] is False
    assert v["new_requirement"] == "manual_or_wait"


def test_offline_keeps_approved_plan_local() -> None:
    """★★ Q7 L134 逐字：「**已批准计划继续本地执行**」。"""
    assert CP.offline_verdict(online=False)["approved_plan"] == "continue_local"
    assert CP.offline_verdict(online=True)["approved_plan"] == "continue_local"


def test_online_allows_planning() -> None:
    """★ 联网 ⇒ 新需求可走自主规划（★ 那是**可关闭的增强**）。"""
    v = CP.offline_verdict(online=True)
    assert v["autonomous_new_requirement"] is True


def test_overbroad_offline_claim_is_detected() -> None:
    """★★ W1 的判据：**说过头的离线声明** ⇒ 检出。"""
    assert CP.check_offline_claim("断网仍能自主处理新需求")["ok"] is False
    assert CP.check_offline_claim(
        "已批准计划继续本地执行")["ok"] is True


#: ══ U3 关闭的能力 ════════════════════════════════════════════════════

def test_five_capabilities_disabled() -> None:
    """★★★ Q7 L130 逐字：「关闭**云端执行、文件托管、向量库、远程 shell 和
    云端 CAD 控制**」—— **五项**。"""
    d = CP.disabled_capabilities()
    assert d["n"] == 5
    assert d["all_disabled"] is True
    assert set(CP.DISABLED_CAPABILITIES) == {
        "cloud_execution", "file_hosting", "vector_store", "remote_shell",
        "cloud_cad_control"}


def test_enabling_any_capability_is_detected() -> None:
    """★★ W2 的判据：**开一项** ⇒ 检出。"""
    pol = CP.load_policy()
    pol["disabled_cloud_capabilities"]["vector_store"] = True
    d = CP.disabled_capabilities(pol)
    assert d["all_disabled"] is False
    assert d["enabled"] == ["vector_store"]
    assert d["code"] == "capability-enabled"


#: ══ U4 固定快照 ══════════════════════════════════════════════════════

def test_model_snapshot_is_pinned() -> None:
    """★★ Q7 L129 逐字：「**固定快照**……**不跟随 latest 自动升级**」。"""
    r = CP.check_model_pinning()
    assert r["ok"] is True
    assert r["follow_latest"] is False
    assert r["snapshot"] == "gpt-5.4-2026-03-05"


def test_latest_tracking_is_detected() -> None:
    """★★ W3 的判据：**跟随 latest** ⇒ 检出。"""
    pol = CP.load_policy()
    pol["cloud_whitelist"]["follow_latest"] = True
    r = CP.check_model_pinning(pol)
    assert r["ok"] is False and r["code"] == "latest-tracking"


def test_provider_is_first_party() -> None:
    """★ Q7 L128 逐字：「OpenAI 第一方 API；**不使用未审计的代充／转售接口**」。"""
    pol = CP.load_policy()
    assert pol["cloud_whitelist"]["provider"] == "OpenAI 第一方 API"
    assert pol["cloud_whitelist"]["not_allowed_providers"]


#: ══ U5 降级顺序 ══════════════════════════════════════════════════════

def test_three_degradation_steps() -> None:
    """★★★ Q7 L161 逐字：「降级顺序：**减少当前候选与上下文 → 卸载可选模型
    → 退回人工／确定性流程**」。"""
    d = CP.degradation_order()
    assert d["n"] == 3
    assert tuple(d["steps"]) == CP.DEGRADATION_STEPS


def test_contiguous_degradation_is_ok() -> None:
    """★ 按顺序走 ⇒ 合法。"""
    r = CP.check_degradation(
        used_steps=["reduce_candidates_and_context",
                    "unload_optional_models"])
    assert r["ok"] is True and r["contiguous"] is True


def test_skipping_a_step_is_detected() -> None:
    """★★ W4 的判据：**跳过降级顺序** ⇒ 检出。"""
    r = CP.check_degradation(used_steps=["unload_optional_models"])
    assert r["ok"] is False
    assert r["code"] == "degradation-skipped"


#: ══ U6 三条禁止 ══════════════════════════════════════════════════════

def test_three_forbidden_degradation_behaviors() -> None:
    """★★★ Q7 L161 逐字：「**不与 SolidWorks 抢显存，不并行冷启动，
    不自动换成更低量化然后继续声称质量不变**」。"""
    d = CP.degradation_order()
    assert set(CP.DEGRADATION_FORBIDDEN) == {
        "compete_with_solidworks_for_vram", "parallel_cold_start",
        "silent_lower_quantization"}
    #: ★ 三项**都没犯**
    assert not any(d["forbidden"].values())


def test_vram_conflict_is_detected() -> None:
    """★★ W5 的判据：**抢显存** ⇒ 检出。"""
    pol = CP.load_policy()
    pol["degradation_order"]["forbidden"][
        "compete_with_solidworks_for_vram"] = True
    r = CP.check_degradation(used_steps=[], policy=pol)
    assert r["ok"] is False
    assert r["code"] == "vram_conflict"


def test_silent_lower_quantization_is_forbidden() -> None:
    """★ 「**不自动换成更低量化然后继续声称质量不变**」。"""
    pol = CP.load_policy()
    assert pol["degradation_order"]["forbidden"][
        "silent_lower_quantization"] is False


#: ══ U7 业主三条拍板 ══════════════════════════════════════════════════

def test_owner_three_decisions_respected() -> None:
    """★★★ 业主 2026-10-12 三条拍板：
    ①「不考虑本地模型」②「不考虑预算」③「客户端认证这个也不管」。"""
    r = CP.owner_decisions()
    assert r["respected"] is True
    assert set(r["decisions"]) == set(CP.OWNER_DECISIONS)


def test_no_local_model_production_service() -> None:
    """★★ 业主：「**不考虑本地模型**」⇒ **不建**生产服务。"""
    pol = CP.load_policy()
    assert pol["local_model"]["production_service"] is False


def test_local_model_only_recorded_as_experiment() -> None:
    """★ Q7 L146 逐字：「保留本地实验候选……**Q4 只是实验量化方案，
    不是可靠性承诺**」⇒ ★ **只记录**。"""
    pol = CP.load_policy()
    cand = pol["local_model"]["experimental_candidate_recorded_only"]
    assert cand["model"] == "Qwen/Qwen2.5-14B-Instruct"
    assert cand["license"] == "Apache-2.0"
    assert cand["is_reliability_promise"] is False


def test_no_budget_engine() -> None:
    """★★ 业主：「**不考虑预算**」⇒ **不实现**预算引擎。"""
    pol = CP.load_policy()
    assert pol["budget"]["engine_implemented"] is False
    #: ★ 但既有的 `BudgetHold` **保留**（★ 只做结构，不算账）
    assert pol["budget"]["existing_primitive"].endswith("BudgetHold")


def test_no_client_authentication() -> None:
    """★★ 业主：「**这个也不管**」⇒ **不做**客户端认证。"""
    pol = CP.load_policy()
    assert pol["client_authentication"]["implemented"] is False


def test_building_local_service_is_detected() -> None:
    """★★ W6 的判据：**偷偷建本地模型服务** ⇒ 检出。"""
    r = CP.check_no_local_service(builds=["local_model_server"])
    assert r["ok"] is False and r["code"] == "local_model_service"
    assert CP.check_no_local_service(builds=["drawing"])["ok"] is True


def test_config_is_untouched() -> None:
    """★★ Q7 L122 逐字：「当前只记录这一决策，**不修改 AGENTS.md 或现有配置**」。"""
    r = CP.check_config_untouched()
    assert r["ok"] is True
    assert r["agents_md_modified"] is False
    assert r["existing_config_modified"] is False


#: ══ 总报告 ═══════════════════════════════════════════════════════════

def test_policy_report_is_complete() -> None:
    """★ 总报告**七块都在**。"""
    r = CP.policy_report()
    for k in ("offline", "disabled", "pinning", "degradation",
              "owner_decisions", "config"):
        assert k in r, "★ 缺 %s" % k


def test_kv_formula_is_recorded() -> None:
    """★ Q7 L148-155 的 KV 公式**只记录**（★ 不作可靠性承诺）。"""
    pol = CP.load_policy()
    kv = pol["local_model"]["kv_cache_formula"]
    assert kv["layers"] == 48 and kv["kv_heads"] == 8 and kv["head_dim"] == 128
    assert kv["examples"]["8192"] == "1.5 GiB"
