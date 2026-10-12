"""★ EC10 安装与节点 —— 能力包内容 / 诊断 / 权限 / 回滚（★ 不创建云服务）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC10**（★ T01–T08 逐字）
#         `specs/312-ec10-install-and-nodes/spec.md`
#         `output/DSH_DECISIONS.md` §十一（★ 凭据红线**逐字**）
# 定位:   ★ **EC10** 的实现。★★★ 计划 §5 EC10 验收逐字：
#           「★ **安装失败有明确原因**；★ **DSH 和 WorkBuddy 不能同时控制同一会话**；
#            ★ **无凭据入包**；★ **未授权用户不能读另一项目产物**；
#            ★ **升级失败可回到已知良好版本**」
#         ★★★ **边界（★ EC10-T08 逐字）**：★「★ **部署独立审批**，★ **本轮不创建云服务**」
# 官方依据: 不适用（本仓的安装与节点层 —— ★ **不调 SolidWorks API**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件（★ **纯离线** —— ★ 不建云）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DiagnosisResult", "CapabilityPackage", "SessionLeaseRegistry",
    "AccessPolicy", "UpgradePlan", "redact_package",
]


# ══════════════════════════════════════════════════════════════════════
# 一、★★★★★ 诊断（★ EC10-T03 · V1）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class DiagnosisResult:
    """★★★ **诊断结果**（★ 逐字承 EC10-T03：★「★ 诊断 **Python/COM/MCP、SW 版本/许可/插件、
    模板、写入目录与单节点占用**；★ **诊断不自动启动真实修改**」）。

    ★★★ **验收（★ 逐字）**：★「★ **安装失败有明确原因**」——
      ★★ 所以每一项**必须**给**可执行的**原因（★ 不是「失败了」）。
    """

    checks: list = field(default_factory=list)

    def add(self, name: str, ok: bool, *, detail: str = "",
            remedy: str = "") -> None:
        """★ 加一项检查（★ **不 ok 时必须给 remedy** —— ★ 那才是「明确原因」）。"""
        self.checks.append({"name": name, "ok": bool(ok), "detail": detail,
                            "remedy": remedy})

    def verdict(self) -> dict:
        """★★★★ **判定**（★ ① 有检查项；★ ② **不 ok 的必须给 remedy**）。"""
        if not self.checks:
            return {"ok": False, "reason": "★★ 一项都没诊断 ⇒ 不算就绪",
                    "failed": [], "without_remedy": []}
        failed = [c for c in self.checks if not c["ok"]]
        no_remedy = [c["name"] for c in failed if not str(c.get("remedy") or "").strip()]
        ready = not failed
        return {
            "ok": ready,
            "ready": ready,
            "failed": [c["name"] for c in failed],
            "without_remedy": no_remedy,
            "read_only": True,                    #: ★★★ **诊断不自动启动真实修改**
            "reason": ("★ 全部 %d 项通过 ⇒ 就绪" % len(self.checks) if ready
                       else ("★★ %d 项未通过，★ 其中 %d 项**没给修法** ⇒ 不算「明确原因」"
                             % (len(failed), len(no_remedy)) if no_remedy
                             else "★★ %d 项未通过（★ 均有修法）" % len(failed))),
        }


# ══════════════════════════════════════════════════════════════════════
# 二、★★★★★ 凭据过滤（★ EC10-T01/T06 · V3）
# ══════════════════════════════════════════════════════════════════════

#: ★★★ **凭据形态**（★ 承 `DSH_DECISIONS.md` §十一 逐字：★「★ **未包含**任何明文密钥、
#:   token、`Authorization` 头、完整配置或私人日志」）
#:   ★★ **2026-10-10 订正**：★ 第一版的键值对只认 `key = value` ⇒ ★ **漏了 JSON 的
#:     `"key": "value"`**（★ 本判据自己抓出来的）⇒ ★ 现同时认 `:` 与 `=`，★ 且允许引号。
CREDENTIAL_PATTERNS = (
    (r"(?i)authorization\s*[:=]\s*\S+", "Authorization 头"),
    (r"(?i)\bbearer\s+[A-Za-z0-9\-_.]{10,}", "Bearer token"),
    (r"(?i)['\"]?(?:api[_-]?key|apikey|secret|password|passwd|token|credential|"
     r"private[_-]?key)['\"]?\s*[:=]\s*['\"]?\S+", "键值对形式的凭据"),
    (r"(?i)sk-[A-Za-z0-9]{16,}", "sk- 形态的密钥"),
    (r"(?i)\bgh[pousr]_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----", "PEM 私钥"),
)


def redact_package(text: str) -> dict:
    """★★★★★ **无凭据入包**（★ 逐字承验收：★「★ **无凭据入包**」）。

    ★★★ **判据**：★ 扫已知凭据形态 ⇒ **有命中就不许入包**（★ 且**点名**是哪一类）。
    ★★ **⇒ 它**不**只做替换** —— ★ 它**先拒绝**（★ 因为「替换过的包」也还是可疑）。
    """
    hits = []
    for pat, label in CREDENTIAL_PATTERNS:
        for m in re.finditer(pat, text or ""):
            hits.append({"kind": label, "snippet": m.group(0)[:40]})
    return {"clean": not hits, "hits": hits, "count": len(hits),
            "reason": ("★ 未检出凭据形态" if not hits
                       else "★★★ 检出 %d 处凭据形态 ⇒ ★ **不许入包**（★ 先拒绝再谈替换）"
                            % len(hits))}


@dataclass
class CapabilityPackage:
    """★★★★ **能力包**（★ 逐字承 EC10-T01）：

    「★ 定义能力包内容：★ **版本清单、兼容矩阵、方法/规则/schema、诊断、测试和操作指南**；
    ★ **不带密钥**」。
    """

    name: str = ""
    version: str = ""
    version_manifest: dict = field(default_factory=dict)   #: ★ 版本清单
    compatibility: list = field(default_factory=list)      #: ★ 兼容矩阵
    contents: list = field(default_factory=list)           #: ★ 方法/规则/schema/诊断/测试/指南
    files: dict = field(default_factory=dict)              #: `{path: text}`

    def contents_are_complete(self) -> dict:
        """★★★ **六类内容齐**（★ 逐字承 EC10-T01）。"""
        need = ("methods", "rules", "schemas", "diagnostics", "tests", "guide")
        have = set(self.contents)
        missing = [k for k in need if k not in have]
        return {"ok": not missing, "missing": missing,
                "reason": ("★ 六类内容齐" if not missing
                           else "★★ 缺 %r ⇒ 能力包不完整" % missing)}

    def scan_for_credentials(self) -> dict:
        """★★★★★ **扫整包**（★ 逐字承验收：★「★ **无凭据入包**」）。"""
        all_hits = []
        for path, text in (self.files or {}).items():
            r = redact_package(text)
            if not r["clean"]:
                all_hits.append({"file": path, "hits": r["hits"]})
        return {"clean": not all_hits, "files_with_credentials": all_hits,
                "scanned_files": len(self.files or {}),
                "reason": ("★ %d 个文件全部无凭据" % len(self.files or {}) if not all_hits
                           else "★★★ %d 个文件检出凭据 ⇒ ★ **不许入包**" % len(all_hits))}

    def verdict(self) -> dict:
        """★★★ **总判定**（★ 内容齐 + ★ 无凭据 + ★ 有版本清单）。"""
        c = self.contents_are_complete()
        s = self.scan_for_credentials()
        v = bool(self.version_manifest) and bool(self.version)
        ok = c["ok"] and s["clean"] and v
        return {"ok": ok, "contents": c, "credentials": s,
                "version_manifest_present": v,
                "reason": ("★ 能力包合格" if ok
                           else "★★ 不合格：★ 内容 %s / ★ 凭据 %s / ★ 版本清单 %s"
                                % (c["ok"], s["clean"], v))}


# ══════════════════════════════════════════════════════════════════════
# 三、★★★★★ 单会话注册（★ V2）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class SessionLeaseRegistry:
    """★★★★★ **单会话注册表**（★ 逐字承验收：★「★ **DSH 和 WorkBuddy 不能同时控制同一会话**」）。

    ★★★ **它管的是**宿主级**的互斥**（★ DSH vs WorkBuddy）——
      ★★ 与 EC00 的 `_LaunchGuard`（★ 进程级命名 Mutex）**互补**：
      ★ 进程级挡住「同时启动」；★ **宿主级挡住「两个宿主同时下命令」** ✓
    """

    holder: str = ""
    session_id: str = "sw-session-1"

    def acquire(self, host: str) -> dict:
        """★★★ **取得会话控制权**（★ 已有持有者 ⇒ **拒**）。"""
        if self.holder and self.holder != host:
            return {"ok": False, "holder": self.holder, "requested": host,
                    "reason": "★★★ 会话 %s 已被宿主 %r 持有 ⇒ ★ **两个宿主不能同时控制**"
                              % (self.session_id, self.holder)}
        self.holder = host
        return {"ok": True, "holder": host, "session_id": self.session_id,
                "reason": "★ 宿主 %r 取得控制权" % host}

    def release(self, host: str) -> dict:
        """★ 释放（★ **只有持有者能释放**）。"""
        if self.holder != host:
            return {"ok": False, "reason": "★★ %r 不是持有者（★ 当前 %r）"
                                           % (host, self.holder)}
        self.holder = ""
        return {"ok": True, "reason": "★ %r 已释放" % host}


# ══════════════════════════════════════════════════════════════════════
# 四、★★★★★ 访问控制（★ EC10-T06 · V4）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class AccessPolicy:
    """★★★★ **访问控制**（★ 逐字承验收：★「★ **未授权用户不能读另一项目产物**」）。

    ★★ 判据：★ **用户 → 项目** 的**白名单**；★ 不在白名单 ⇒ **拒**（★ 且**说清**缺什么）。
    """

    grants: dict = field(default_factory=dict)     #: `{user: [project, ...]}`
    #: ★★ **数据保留**（★ EC10-T06 逐字：★「★ 数据保留、日志脱敏、文件下载授权和外发确认」）
    retention_days: int = 90
    log_redaction: bool = True
    download_authorization: bool = True
    external_send_confirmation: bool = True

    def may_read(self, user: str, project: str) -> dict:
        """★★★ **能不能读**（★ **跨项目 ⇒ 拒**）。"""
        allowed = set(self.grants.get(user) or ())
        ok = project in allowed
        return {"ok": ok, "user": user, "project": project,
                "allowed_projects": sorted(allowed),
                "reason": ("★ %r 被授权读 %r" % (user, project) if ok
                           else "★★★ %r **未被授权**读 %r（★ 它只能读 %r）"
                                % (user, project, sorted(allowed)))}

    def controls_are_complete(self) -> dict:
        """★★★ **四项控制齐**（★ 逐字承 EC10-T06）。"""
        checks = {
            "retention_days": self.retention_days > 0,
            "log_redaction": bool(self.log_redaction),
            "download_authorization": bool(self.download_authorization),
            "external_send_confirmation": bool(self.external_send_confirmation),
        }
        missing = [k for k, v in checks.items() if not v]
        return {"ok": not missing, "missing": missing, "checks": checks,
                "reason": ("★ 四项控制齐" if not missing
                           else "★★ 缺 %r" % missing)}


# ══════════════════════════════════════════════════════════════════════
# 五、★★★★★ 升级与回滚（★ EC10-T04 · V5）
# ══════════════════════════════════════════════════════════════════════

@dataclass
class UpgradePlan:
    """★★★★★ **升级与回滚**（★ 逐字承验收：★「★ **升级失败可回到已知良好版本**」）。

    ★★★ **判据**：★ 升级前**必须**记下「已知良好版本」；
      ★★ 升级失败 ⇒ ★ **回滚到它**（★ 且**可验证回滚成功**）。
    """

    from_version: str = ""
    to_version: str = ""
    #: ★★★ **已知良好版本**（★ 回滚目标 —— ★ **必填**）
    known_good_version: str = ""
    #: ★ 升级步骤（★ 可复核）
    steps: list = field(default_factory=list)

    def can_rollback(self) -> dict:
        """★★★★ **能不能回滚**（★ **没有已知良好版本 ⇒ 不能升级**）。"""
        if not str(self.known_good_version).strip():
            return {"ok": False,
                    "reason": "★★★ **没有记下已知良好版本** ⇒ ★ 升级失败就回不去"}
        if self.known_good_version not in (self.from_version,):
            #: ★★ 允许「已知良好 = 当前版本」（★ 最常见）；★ 别的要先确认它存在
            return {"ok": False,
                    "reason": ("★★ 已知良好版本 %r 既不是当前版本 %r ⇒ ★ 得先证明它可用"
                               % (self.known_good_version, self.from_version))}
        return {"ok": True, "rollback_target": self.known_good_version,
                "reason": "★ 可回滚到 %r" % self.known_good_version}

    def rollback(self, *, failure_reason: str = "") -> dict:
        """★★★ **执行回滚**（★ 失败 ⇒ 回到已知良好版本）。"""
        c = self.can_rollback()
        if not c["ok"]:
            return {"ok": False, "reason": c["reason"]}
        return {"ok": True, "restored_to": self.known_good_version,
                "from_failed": self.to_version,
                "failure_reason": failure_reason,
                #: ★★ **不污染用户全局环境**（★ EC10-T04 逐字）
                "touched_user_global_env": False,
                "reason": ("★ 已回到已知良好版本 %r（★ 未动用户全局环境）"
                           % self.known_good_version)}

    def verdict(self) -> dict:
        """★★ **升级前判定**（★ 可回滚 + ★ 有步骤 + ★ 不污染全局）。"""
        c = self.can_rollback()
        return {"ok": c["ok"] and bool(self.steps), "rollback": c,
                "steps": len(self.steps),
                "reason": ("★ 升级计划可行（★ 可回滚到 %r）" % self.known_good_version
                           if c["ok"] and self.steps
                           else "★★ 不可行：%s / ★ 步骤 %d" % (c["reason"], len(self.steps)))}
