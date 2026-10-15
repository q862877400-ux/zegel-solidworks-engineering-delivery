"""★ EC10 判据 —— 诊断 / 能力包 / 单会话 / 访问控制 / 升级回滚。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/nodes.py`（★ EC10 的实现）
#         `specs/312-ec10-install-and-nodes/spec.md`
# 定位:   ★ EC10 的判据（★ 逐字承计划 §5 EC10 的「验收」）。
# 官方依据: 不适用（本仓的安装与节点层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不建云）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import nodes as N


# ══════════════════════════════════════════════════════════════════════
# V1 · 安装失败有明确原因
# ══════════════════════════════════════════════════════════════════════

def test_v1_all_checks_pass_means_ready():
    """★★★ V1：★ **全部通过 ⇒ 就绪**。"""
    d = N.DiagnosisResult()
    for k in ("python", "com", "mcp", "sw_version", "license", "addin",
              "template", "write_dir", "single_node"):
        d.add(k, True)
    out = d.verdict()
    assert out["ok"] is True, "★ 全通过却判不就绪：%r" % out
    assert out["ready"] is True
    #: ★★★ **诊断必须只读**
    assert out["read_only"] is True, "★★ 诊断不是只读 ⇒ ★ 它会自动启动真实修改"


def test_v1_failure_requires_a_remedy():
    """★★★★★ V1：★ **失败必须给明确原因（修法）**（★ 逐字承验收）。

    ★★ 判据：★ 不 ok 的项**没给 `remedy`** ⇒ ★ **不算「明确原因」** ✗
    """
    d = N.DiagnosisResult()
    d.add("python", True)
    d.add("com", False, detail="★ COM 未注册")            #: ★ **没给修法**
    out = d.verdict()
    assert out["ok"] is False
    assert out["without_remedy"] == ["com"], (
        "★★ 没给修法的失败项**没被点名** ⇒ ★ 安装失败会「原因不明」")
    assert "没给修法" in out["reason"]


def test_v1_failure_with_remedy_is_named():
    """★★ V1：★ **给了修法 ⇒ 如实报**（★ 且点名哪项失败）。"""
    d = N.DiagnosisResult()
    d.add("python", True)
    d.add("com", False, detail="★ COM 未注册",
          remedy="★ 以管理员运行 regsvr32 注册 sldworks.tlb")
    out = d.verdict()
    assert out["ok"] is False
    assert out["failed"] == ["com"]
    assert out["without_remedy"] == [], "★ 有修法却被当成没修法"


def test_v1_no_checks_is_not_ready():
    """★★ V1：★ **一项都没诊断 ⇒ 不算就绪**（★ 不能「没检查=没问题」）。"""
    out = N.DiagnosisResult().verdict()
    assert out["ok"] is False
    assert "一项都没诊断" in out["reason"]


# ══════════════════════════════════════════════════════════════════════
# V2 · 两个宿主不能同时控制同一会话
# ══════════════════════════════════════════════════════════════════════

def test_v2_second_host_is_rejected():
    """★★★★★ V2：★ **DSH 和 WorkBuddy 不能同时控制同一会话**（★ 逐字承验收）。"""
    r = N.SessionLeaseRegistry()
    a = r.acquire("DSH")
    assert a["ok"] is True, "★ 第一个宿主该拿到"
    b = r.acquire("WorkBuddy")
    assert b["ok"] is False, "★★★ 第二个宿主**拿到了**控制权 ⇒ ★ 违反验收"
    assert b["holder"] == "DSH"
    assert "不能同时控制" in b["reason"]


def test_v2_same_host_can_reacquire():
    """★★ V2：★ **同一个宿主可重入**（★ 不是死锁）。"""
    r = N.SessionLeaseRegistry()
    r.acquire("DSH")
    assert r.acquire("DSH")["ok"] is True, "★ 同一宿主被自己挡住"


def test_v2_release_then_other_host_can_take_it():
    """★★★ V2：★ **释放后另一个宿主可以接**（★ 串行而非永久独占）。"""
    r = N.SessionLeaseRegistry()
    r.acquire("DSH")
    assert r.release("DSH")["ok"] is True
    assert r.acquire("WorkBuddy")["ok"] is True, "★ 释放后接不上"


def test_v2_non_holder_cannot_release():
    """★★ V2：★ **非持有者不能释放**（★ 否则会「抢释放」）。"""
    r = N.SessionLeaseRegistry()
    r.acquire("DSH")
    out = r.release("WorkBuddy")
    assert out["ok"] is False, "★★ 非持有者释放成功 ⇒ ★ 会话会被误放"
    #: ★★ 且持有者**仍是** DSH
    assert r.acquire("WorkBuddy")["ok"] is False


# ══════════════════════════════════════════════════════════════════════
# V3 · 无凭据入包
# ══════════════════════════════════════════════════════════════════════

def test_v3_clean_text_passes():
    """★★ V3：★ **干净文本 ⇒ 通过**。"""
    r = N.redact_package("★ 这是一个说明文件，讲怎么用 SolidWorks API。")
    assert r["clean"] is True, "★ 干净文本被误报：%r" % r
    assert r["count"] == 0


def test_v3_credentials_are_detected_and_named():
    """★★★★★ V3：★ **凭据必须检出且点名**（★ 逐字承验收：★「★ **无凭据入包**」）。"""
    samples = [
        ("Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc", "Authorization 头"),
        ("api_key = sk-live-abcdefghijklmnop", None),
        ("password = hunter2xyz", None),
        ("ghp_abcdefghijklmnopqrstuvwxyz0123456789", "GitHub token"),
        ("-----BEGIN RSA PRIVATE KEY-----", "PEM 私钥"),
    ]
    for text, _ in samples:
        r = N.redact_package(text)
        assert r["clean"] is False, "★★ 凭据没检出：%r" % text
        assert r["hits"], "★ 没给命中详情"
        assert r["hits"][0]["kind"], "★ 没点名是哪一类凭据"


def test_v3_package_scan_covers_every_file():
    """★★★★ V3：★ **整包都要扫**（★ 不是抽查一个文件）。"""
    p = N.CapabilityPackage(name="sw-skill", version="1.3.0",
                            version_manifest={"sw-skill": "1.3.0"},
                            files={"a.md": "★ 干净", "b.json": '{"token": "abc123456789"}'})
    out = p.scan_for_credentials()
    assert out["clean"] is False, "★★ 只扫了第一个文件 ⇒ 漏了 `b.json`"
    assert out["files_with_credentials"][0]["file"] == "b.json", "★ 没点名是哪个文件"
    assert out["scanned_files"] == 2


def test_v3_package_verdict_blocks_on_credentials():
    """★★★ V3：★ **有凭据 ⇒ 整包不合格**（★ 不管别的内容多齐）。"""
    p = N.CapabilityPackage(
        name="x", version="1", version_manifest={"x": "1"},
        contents=list(("methods", "rules", "schemas", "diagnostics", "tests", "guide")),
        files={"a.md": "token: abcdef1234567890"})
    out = p.verdict()
    assert out["ok"] is False, "★★ 有凭据却判合格"
    assert out["credentials"]["clean"] is False


def test_v3_package_requires_six_content_kinds():
    """★★★ V3：★ **能力包六类内容齐**（★ 逐字承 EC10-T01）。"""
    p = N.CapabilityPackage(name="x", version="1", version_manifest={"x": "1"},
                            contents=["methods", "rules"])
    out = p.contents_are_complete()
    assert out["ok"] is False
    assert set(out["missing"]) == {"schemas", "diagnostics", "tests", "guide"}


# ══════════════════════════════════════════════════════════════════════
# V4 · 未授权用户不能读另一项目产物
# ══════════════════════════════════════════════════════════════════════

def test_v4_cross_project_read_is_rejected():
    """★★★★★ V4：★ **未授权用户不能读另一项目产物**（★ 逐字承验收）。"""
    p = N.AccessPolicy(grants={"alice": ["proj-A"], "bob": ["proj-B"]})
    ok = p.may_read("alice", "proj-A")
    assert ok["ok"] is True, "★ 授权项目读不了"
    bad = p.may_read("alice", "proj-B")
    assert bad["ok"] is False, "★★★ alice 读到了 proj-B ⇒ ★ 违反验收"
    assert "未被授权" in bad["reason"]
    #: ★★ **要列出它**能读什么**（★ 可执行）
    assert bad["allowed_projects"] == ["proj-A"]


def test_v4_user_without_grants_reads_nothing():
    """★★ V4：★ **没授权的用户 ⇒ 什么都读不了**。"""
    p = N.AccessPolicy(grants={"alice": ["proj-A"]})
    assert p.may_read("mallory", "proj-A")["ok"] is False
    assert p.may_read("mallory", "proj-A")["allowed_projects"] == []


def test_v4_four_controls_must_be_present():
    """★★★ V4：★ **四项控制齐**（★ 逐字承 EC10-T06）。"""
    ok = N.AccessPolicy(retention_days=90, log_redaction=True,
                        download_authorization=True, external_send_confirmation=True)
    assert ok.controls_are_complete()["ok"] is True
    #: ★★ **缺一项 ⇒ 报出来**
    for kw, key in (({"retention_days": 0}, "retention_days"),
                    ({"log_redaction": False}, "log_redaction"),
                    ({"download_authorization": False}, "download_authorization"),
                    ({"external_send_confirmation": False}, "external_send_confirmation")):
        base = dict(retention_days=90, log_redaction=True,
                    download_authorization=True, external_send_confirmation=True)
        base.update(kw)
        out = N.AccessPolicy(**base).controls_are_complete()
        assert out["ok"] is False, "★★ 缺 %r 却判齐" % key
        assert key in out["missing"]


# ══════════════════════════════════════════════════════════════════════
# V5 · 升级失败可回到已知良好版本
# ══════════════════════════════════════════════════════════════════════

def test_v5_upgrade_without_known_good_is_blocked():
    """★★★★★ V5：★ **没记下已知良好版本 ⇒ 不许升级**（★ 逐字承验收：

    「★ **升级失败可回到已知良好版本**」）。
    """
    u = N.UpgradePlan(from_version="1.0", to_version="1.1", known_good_version="",
                      steps=["★ 停服务", "★ 换包"])
    out = u.can_rollback()
    assert out["ok"] is False, "★★★ 没有已知良好版本却允许升级 ⇒ ★ 回不去"
    assert "已知良好版本" in out["reason"]
    #: ★★ 且**整个升级计划**也不可行
    assert u.verdict()["ok"] is False


def test_v5_rollback_restores_known_good():
    """★★★★ V5：★ **回滚到已知良好版本**（★ 且**不污染用户全局环境**）。"""
    u = N.UpgradePlan(from_version="1.0", to_version="1.1", known_good_version="1.0",
                      steps=["★ 停服务", "★ 换包", "★ 起服务"])
    out = u.rollback(failure_reason="★ 新版本启动失败")
    assert out["ok"] is True, "★ 回滚失败：%r" % out
    assert out["restored_to"] == "1.0"
    assert out["from_failed"] == "1.1"
    #: ★★★ **不污染用户全局环境**（★ EC10-T04 逐字）
    assert out["touched_user_global_env"] is False, (
        "★★★ 回滚动了用户全局环境 ⇒ ★ 违反 EC10-T04")


def test_v5_unknown_rollback_target_is_blocked():
    """★★★ V5：★ **回滚目标必须被证明可用**（★ 不是随便填一个版本号）。"""
    u = N.UpgradePlan(from_version="1.0", to_version="1.1",
                      known_good_version="0.9", steps=["★ 换包"])
    out = u.can_rollback()
    assert out["ok"] is False, "★★ 填了个不在场的版本号却判可回滚"
    assert "得先证明它可用" in out["reason"]


def test_v5_upgrade_requires_steps():
    """★★ V5：★ **升级要有步骤**（★ 不能「直接换」）。"""
    u = N.UpgradePlan(from_version="1.0", to_version="1.1", known_good_version="1.0")
    assert u.verdict()["ok"] is False, "★★ 没步骤却判可行"
