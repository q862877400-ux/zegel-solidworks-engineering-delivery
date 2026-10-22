"""★ Q12 · 同一发布清单 + 原子切换 + 计划固定摘要（规格 327 的 T1~T4）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/release_manifest.py
# 定位:   规格 `specs/327-release-manifest-rules-and-runs` 的 T1（同一发布清单）/T2（
#           原子切换）/ T3（计划固定摘要）/ T4（禁止多份规则各自裁决）。★★ 实测（2026-10
#           -12）起点：独立元数据目录、`ToolSpec` 接口事实所有权、`ToolDescriptor` 合成
#           、效应六类**都已具备**；★ 而**没有「工具+元数据+方法+规则」同一发布清单**、*
#           *没有「计划固定摘要」**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q12（L214-231）逐字：L229「工
#           具、元数据、方法和规则构成**同一发布清单及摘要，原子切换**；  **计划固定摘要
#           ，升级不能悄悄重绑旧计划**」L229「普通元数据修改只动一个源；工具签名变化会使
#           绑定门禁失败，  而不是默默兼容」L225「**无裁决的冲突保守处理，不能由不同消费
#           者自行选边**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_s327_manifest.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / "metadata" / "manifests"

#: ★★ **发布清单的四个部分**（★ Q12 L229 逐字）
MANIFEST_PARTS = ("tools", "metadata", "methods", "rules")


class ManifestError(Exception):
    """★ 发布清单失败（★ 带封闭码）。"""

    CODES = ("missing-part", "digest-mismatch", "stale-plan",
             "no-manifest", "multiple-arbiters")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法清单拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


def _digest(obj) -> str:
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


#: ══════════════════════════════════════════════════════════════════════
# 一、四部分的摘要（★ T1 —— ★ Q12 L229）
#: ══════════════════════════════════════════════════════════════════════

def part_digest_tools() -> str:
    """★ 工具面摘要（★ 521 个工具名 + 效应）。"""
    from . import registry as REG                                       # noqa: PLC0415
    reg = REG.build_registry()
    rows = sorted((n, getattr(d, "effect", ""), getattr(d, "admitted", False))
                  for n, d in reg.items())
    return _digest(rows)


def part_digest_metadata() -> str:
    """★ 元数据摘要（★ `metadata/` 下**所有**文件内容）。"""
    md = ROOT / "metadata"
    rows = []
    for p in sorted(md.rglob("*")):
        if p.is_file() and p.suffix in (".yaml", ".yml", ".json"):
            rows.append((str(p.relative_to(ROOT)),
                         hashlib.sha256(p.read_bytes()).hexdigest()))
    return _digest(rows)


def part_digest_methods() -> str:
    """★ 方法摘要（★ `METHOD_LIBRARY` 的 id 与步骤）。"""
    from .compiler import METHOD_LIBRARY                                # noqa: PLC0415
    rows = sorted((mid, tuple(getattr(m, "steps", ()) or ()))
                  for mid, m in METHOD_LIBRARY.items())
    return _digest(rows)


def part_digest_rules() -> str:
    """★ 规则摘要（★ 规则层的实现文件内容）。"""
    files = ("rule_verdicts.py", "rules.py", "compliance.py",
             "rule_service.py")
    rows = []
    for f in files:
        p = ROOT / "scripts" / "engineering" / f
        if p.is_file():
            rows.append((f, hashlib.sha256(p.read_bytes()).hexdigest()))
    return _digest(rows)


PART_FUNCS = {"tools": part_digest_tools, "metadata": part_digest_metadata,
              "methods": part_digest_methods, "rules": part_digest_rules}


#: ══════════════════════════════════════════════════════════════════════
# 二、发布清单（★ T1/T2）
#: ══════════════════════════════════════════════════════════════════════

@dataclass
class ReleaseManifest:
    """★★ **同一发布清单**（★ T1 —— ★ Q12 L229 逐字）。

    ★★ 判据：**四部分各有摘要**，★ 且**合成一个 `release_digest`** ——
      ★ 这样「换清单」就是**换一个整体**（★ 原子，★ T2）。
    """

    version: int = 1
    parts: dict = field(default_factory=dict)
    release_digest: str = ""
    created_at: str = ""

    def compute(self) -> "ReleaseManifest":
        self.parts = {k: PART_FUNCS[k]() for k in MANIFEST_PARTS}
        self.release_digest = _digest(self.parts)
        return self

    def missing_parts(self) -> list:
        return [k for k in MANIFEST_PARTS if not self.parts.get(k)]

    def validate(self) -> None:
        miss = self.missing_parts()
        if miss:
            raise ManifestError("missing-part", "★ 缺部分：%s" % miss)
        #: ★ 摘要必须**自洽**（★ 重算一遍）
        if self.release_digest != _digest(self.parts):
            raise ManifestError("digest-mismatch",
                                "★ 合成摘要与四部分不符")

    def to_dict(self) -> dict:
        return {"version": self.version, "parts": dict(self.parts),
                "release_digest": self.release_digest,
                "created_at": self.created_at,
                "★": "★ 工具+元数据+方法+规则 = **同一发布清单**（★ 原子切换）"}


def build_manifest(*, created_at: str = "") -> ReleaseManifest:
    import time                                                         # noqa: PLC0415
    m = ReleaseManifest(created_at=created_at or time.strftime(
        "%Y-%m-%dT%H:%M:%S"))
    m.compute()
    m.validate()
    return m


def publish_manifest(m: ReleaseManifest) -> pathlib.Path:
    """★★ **原子发布**（★ T2 —— ★ Q12 L229 逐字「**原子切换**」）。

    ★★ 判据：**先写临时名，再 `os.replace`** —— ★ 与 Q14 的
      「同卷原子重命名」**同口径**。
    """
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    final = MANIFEST_DIR / ("release-v%d.json" % m.version)
    tmp = MANIFEST_DIR / (".tmp-release-v%d.json" % m.version)
    tmp.write_text(json.dumps(m.to_dict(), ensure_ascii=False, indent=1),
                   encoding="utf-8")
    tmp.replace(final)          #: ★ 同卷原子重命名
    return final


def load_manifest(version: int) -> ReleaseManifest:
    p = MANIFEST_DIR / ("release-v%d.json" % version)
    if not p.is_file():
        raise ManifestError("no-manifest", "★ 没有 %s" % p)
    d = json.loads(p.read_text(encoding="utf-8"))
    m = ReleaseManifest(version=d["version"], parts=d["parts"],
                        release_digest=d["release_digest"],
                        created_at=d.get("created_at", ""))
    m.validate()
    return m


#: ══ T3 计划固定摘要（★ Q12 L229 逐字）════════════════════════════════

@dataclass
class BoundPlan:
    """★★ **绑定了发布摘要的计划**（★ T3）。

    ★★ Q12 L229 逐字：「**计划固定摘要，升级不能悄悄重绑旧计划**」。

    ★★ 判据（★ 结构性）：
      ```
      ① 计划里**存了**当时的 `release_digest`
      ② 跑之前**必须**核对当前清单摘要
      ③ ★ 不一致 ⇒ **拒跑**（★ 不是"自动升级"）
      ```
    """

    plan_id: str = ""
    release_digest: str = ""
    steps: list = field(default_factory=list)

    def check(self, current: ReleaseManifest) -> dict:
        if not self.release_digest:
            return {"ok": False, "code": "stale-plan",
                    "reason": "★ 计划没绑定发布摘要"}
        if self.release_digest != current.release_digest:
            return {"ok": False, "code": "stale-plan",
                    "reason": ("★★ 计划的发布摘要 %s 与当前 %s 不符 ⇒ **拒跑**"
                               "（★ 不悄悄重绑）"
                               % (self.release_digest[:12],
                                  current.release_digest[:12])),
                    "plan_digest": self.release_digest,
                    "current_digest": current.release_digest}
        return {"ok": True, "code": "", "reason": "★ 摘要一致"}


def bind_plan(plan_id: str, steps: list,
              manifest: ReleaseManifest) -> BoundPlan:
    """★ 造一个**绑定当前发布摘要**的计划（★ T3）。"""
    return BoundPlan(plan_id=plan_id, release_digest=manifest.release_digest,
                     steps=list(steps))


#: ══ T4 禁止多份规则各自裁决（★ Q12 L225 逐字）═══════════════════════

#: ★★ **每个性质只有一个裁决者**（★ Q12 L225 逐字：「**不能由不同消费者
#:   自行选边**」）
#:   ★ 判据：**登记表** —— 一个性质名只能映射到一个 `(module, function)`。
ARBITER_TABLE: dict[str, tuple] = {
    "release_readiness": ("engineering.release_manifest", "build_manifest"),
    "rule_verdict": ("engineering.rule_service", "evaluate_rule"),
    "dof_verdict": ("engineering.assembly", "ConstraintGraph"),
    "tool_admission": ("engineering.authorization", "check_tool"),
    "recovery_verdict": ("engineering.recovery", "resume_verdict"),
    "scope_limit": ("engineering.scope", "check_scope"),
    "evidence_circularity": ("engineering.housing", "evidence_is_noncircular"),
}


def register_arbiter(property_name: str, module: str, function: str) -> dict:
    """★★ **登记唯一裁决者**（★ T4 —— ★ Q12 L225 逐字）。

    ★★ 判据：**同一性质**再登记一个**不同**的裁决者 ⇒ **拒**
      （★ 那正是「多份规则各自裁决」）。
    """
    cur = ARBITER_TABLE.get(property_name)
    if cur is not None and cur != (module, function):
        raise ManifestError(
            "multiple-arbiters",
            "★★ 性质 `%s` 已有裁决者 %s ⇒ **不能由不同消费者自行选边**"
            "（★ Q12 L225）" % (property_name, list(cur)))
    ARBITER_TABLE[property_name] = (module, function)
    return {"ok": True, "property": property_name,
            "arbiter": [module, function]}


def arbiters_for(property_name: str) -> list:
    """★ 查一个性质的裁决者（★ 只可能有一个）。"""
    cur = ARBITER_TABLE.get(property_name)
    return list(cur) if cur else []


def check_single_arbiter() -> dict:
    """★ 全表**每个性质恰好一个裁决者**（★ T4 的整体判据）。"""
    return {"ok": True, "n": len(ARBITER_TABLE),
            "arbiters": {k: list(v) for k, v in ARBITER_TABLE.items()},
            "★": "★ 一个性质 ⇒ 一个裁决者（★ Q12 L225：「不能由不同消费者自行选边」）"}
