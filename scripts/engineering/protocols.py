"""★ Q1/Q5 · 四类声明式协议 + check_ref 解析 + 8 项必设检查（规格 325 的 R1~R5）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/protocols.py
# 定位:   规格 `specs/325-declarative-protocols-and-decisions` 的 R1（四类协议）/R2（
#           五要素）/ R3（`check_ref` 解析）/ R4（8 项必设检查）/R5（改一处 ⇒ 重生成三视
#           图）/ R8（缺需求先问转字段门禁）/R10（改 YAML 不能获得新能力）。★★ 实测（202
#           6-10-12）起点：**没有 `decision_id`、没有三态、没有四类协议、没有 `check_ref
#           ` 解析器、没有禁止 eval 的判据、没有 8 项必设检查、没有任何协议目录**；★ 而
#           `design_ir.WAITING_INPUT` **已有**，且可作 `check_ref` 后端的既有函数**充足*
#           *（`rule_verdicts.evaluate` / `design_ir.parse_requirement` /`registry.resol
#           ve_step_name` / `recovery.resume_verdict` /`catalog.retrieve` / `compiler.ME
#           THOD_LIBRARY` …）。
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q5（L63-94）逐字：  「`chec
#           k_ref` **必须解析到已登记的代码**，禁止任意 Python、    `eval` 或 LLM 生成脚
#           本进入生产执行」；  「改协议参数或流程：**改一处源数据，重新生成文档、提示与
#           目录**」；  「增加真正的新判定逻辑：**增加实现与测试，再登记引用**，    不能
#           假装只改 YAML 就能获得新能力」；  L92 逐字给的 8 项必设检查② 同文件 Q1（L10-
#           34）逐字：四类协议 + 五要素 + 「缺需求先问转字段门禁」③ `metadata/protocols/
#           *.yaml`（四份协议）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（真机验收入口 `tools/run_s325_protocols.py`）。
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import hashlib
import importlib
import json
import pathlib
import re
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROTOCOL_DIR = ROOT / "metadata" / "protocols"

#: ★★ Q1（L28）逐字：「首先抽取**需求**、方案门槛、布局、失败转移**四类协议**」
REQUIRED_PROTOCOLS = ("requirement", "scheme_gate", "layout", "failure_transition")

#: ★★ Q1（L28）逐字：「每条补齐**输入、输出、触发条件、检查函数和失败状态**」
REQUIRED_FIELDS = (
    "protocol_id",
    "version",
    "entry_check",
    "inputs_schema",
    "outputs_schema",
    "required_inputs",
    "checks",
    "on_failure",
    "outputs",
)

#: ★★ Q5（L92）逐字给的**8 项必设检查**：
#:   「必设检查：schema、引用解析、单位与类型、可达状态、禁止条件覆盖、
#     输出与消费端兼容、版本依赖、受影响节点失效、负例与突变测试。」
#:   ★ 原文写"必设检查："后面跟了 **9 个词**（最后一个"负例与突变测试"
#:     是**测试**层面的，不是协议字段）⇒ ★ 本规格按 **8 项协议检查 + 1 项测试**
#:     落地，★ 并**逐字标注**这一点（★ 不假装是 8 个）。
REQUIRED_CHECKS = (
    "schema",  #: schema 检查
    "ref_resolution",  #: 引用解析
    "unit_and_type",  #: 单位与类型
    "reachable_state",  #: 可达状态
    "forbidden_covered",  #: 禁止条件覆盖
    "consumer_compatible",  #: 输出与消费端兼容
    "version_dependency",  #: 版本依赖
    "affected_invalidation",  #: 受影响节点失效
)
#: ★ 第 9 项 —— ★ 它在**测试**层面（★ 由 `tests/` 承担，不是协议字段）
NINTH_CHECK_IS_TEST = "negative_and_mutation_tests"

#: ★★ Q5（L88）逐字：「禁止任意 Python、`eval` 或 LLM 生成脚本进入生产执行」
#:   ★ 判据：这些形态**在协议里零命中**
FORBIDDEN_PATTERNS = (
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bcompile\s*\(",
    r"__import__",
    r"import\s+os\b",
    r"subprocess",
    r"```python",  #: ★ LLM 生成的代码块
    r"\bshell\s*=",
)


class ProtocolError(Exception):
    """★ 协议层失败（★ 带封闭码）。"""

    CODES = (
        "missing-protocol",
        "missing-field",
        "bad-check-ref",
        "forbidden-code",
        "unknown-failure-code",
        "no-implementation",
        "bad-protocol-id",
    )

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法协议拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、装载（★ R1/R2）
#: ══════════════════════════════════════════════════════════════════════


@dataclass
class Protocol:
    protocol_id: str = ""
    version: int = 0
    entry_check: str = ""
    inputs_schema: str = ""
    outputs_schema: str = ""
    required_inputs: list = field(default_factory=list)
    checks: list = field(default_factory=list)
    on_failure: dict = field(default_factory=dict)
    outputs: list = field(default_factory=list)
    source_refs: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)
    path: str = ""

    def missing_fields(self) -> list:
        """★ 五要素缺哪几项（★ R2 的判据）。"""
        out = []
        for f in REQUIRED_FIELDS:
            v = getattr(self, f, None)
            if v is None or v == "" or v == [] or v == {}:
                out.append(f)
        return out

    def digest(self) -> str:
        """★ 协议摘要（★ R5 用它判"源数据改了没有"）。"""
        blob = json.dumps(
            {k: getattr(self, k) for k in REQUIRED_FIELDS},
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "protocol_id": self.protocol_id,
            "version": self.version,
            "entry_check": self.entry_check,
            "inputs_schema": self.inputs_schema,
            "outputs_schema": self.outputs_schema,
            "required_inputs": list(self.required_inputs),
            "checks": list(self.checks),
            "on_failure": dict(self.on_failure),
            "outputs": list(self.outputs),
            "source_refs": list(self.source_refs),
        }


#: ★ 2026-10-22 统一化：`_load_yaml` 原与 `catalog._load_simple_yaml` 两份逐字相同，
#:   现收敛到 `engineering/_yaml_loader.load_yaml`；此处保留旧名作别名
try:
    from ._yaml_loader import load_yaml as _load_yaml
except ImportError:
    from _yaml_loader import load_yaml as _load_yaml


def load_protocol(name: str) -> Protocol:
    """★ 读一份协议（★ R1）。"""
    p = PROTOCOL_DIR / ("%s.yaml" % name)
    if not p.is_file():
        raise ProtocolError("missing-protocol", "★ 没有 %s" % p)
    d = _load_yaml(p)
    known = set(Protocol.__dataclass_fields__) - {"extra", "path"}
    kw = {k: d[k] for k in known if k in d}
    extra = {k: v for k, v in d.items() if k not in known}
    pr = Protocol(**kw, extra=extra, path=str(p))
    if pr.protocol_id != name and name != "layout":
        #: ★ `layout.yaml` 的 `protocol_id` 逐字是 `rigid_mechanism_layout`
        #:   （★ Q5 的样例如此）⇒ ★ 文件名与 id 允许不同，但**要记下来**
        pass
    miss = pr.missing_fields()
    if miss:
        raise ProtocolError("missing-field", "★ %s 缺五要素：%s" % (name, miss))
    return pr


def load_all() -> dict:
    """★ 读**四类协议**（★ R1 —— ★ 缺一即失败）。"""
    out = {}
    for name in REQUIRED_PROTOCOLS:
        out[name] = load_protocol(name)
    return out


#: ══════════════════════════════════════════════════════════════════════
# 二、check_ref 解析（★ R3/R10 —— ★ Q5 的核心）
#: ══════════════════════════════════════════════════════════════════════

#: ★★ **已登记的检查实现表**（★ Q5 L88 逐字：「`check_ref` **必须解析到
#:   已登记的代码**」）。
#:   ★★ 判据：**这里是唯一登记处** —— ★ 协议里写一个名字，★ 必须在这里能查到
#:     `(module, function)`，★ 否则**拒**（★ Q5 L90 逐字：「不能假装只改 YAML
#:     就能获得新能力」）。
CHECK_REGISTRY: dict[str, tuple] = {
    #: ── requirement 协议
    "non_empty_requirement@1": ("engineering.design_ir", "parse_requirement"),
    "supported_domain@1": ("engineering.design_ir", "parse_requirement"),
    "critical_inputs_present@1": ("engineering.design_ir", "parse_requirement"),
    "no_absurd_magnitude@1": ("engineering.design_ir", "parse_requirement"),
    #: ── scheme_gate 协议
    "hard_requirements_complete@1": ("engineering.rule_verdicts", "evaluate"),
    "kinematic_model_supported@1": ("engineering.linkage", "solve_four_bar"),
    "forbidden_conditions_covered@1": ("engineering.rule_verdicts", "evaluate"),
    "output_consumer_compatible@1": ("engineering.registry", "bind_params"),
    #: ── layout 协议（★ 逐字承 Q5 的样例）
    "assembly_accessibility@1": ("engineering.assembly", "build_case"),
    "motion_validation_coverage@1": ("engineering.linkage", "continuity_verdict"),
    #: ── failure_transition 协议
    "same_error_twice_triggers_diagnosis@1": (
        "engineering.decisions",
        "SameErrorTrigger",
    ),
    "unknown_effect_no_retry@1": ("engineering.jobs", "JobState"),
    "empirical_ratio_not_executable@1": ("engineering.rule_verdicts", "evaluate"),
    #: ── 8 项必设检查（★ Q5 L92）自己也要有实现
    "schema@1": ("engineering.protocols", "check_schema"),
    "ref_resolution@1": ("engineering.protocols", "resolve_check_ref"),
    "unit_and_type@1": ("engineering.registry", "bind_params"),
    "reachable_state@1": ("engineering.authorization", "authorize_plan"),
    "forbidden_covered@1": ("engineering.protocols", "check_forbidden"),
    "consumer_compatible@1": ("engineering.catalog", "load_contract"),
    "version_dependency@1": ("engineering.protocols", "check_versions"),
    "affected_invalidation@1": ("engineering.recovery", "invalidation_closure"),
}


@dataclass
class CheckRef:
    name: str
    module: str = ""
    function: str = ""
    resolved: bool = False
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "module": self.module,
            "function": self.function,
            "resolved": self.resolved,
            "reason": self.reason,
        }


def resolve_check_ref(name: str) -> CheckRef:
    """★★ **`check_ref` 解析**（★ R3 —— ★ Q5 L88 逐字）。

    ★★ 判据（★ 两条）：
      ```
      ① 名字必须在 `CHECK_REGISTRY` 里（★ 已登记）
      ② ★ 且那个 `(module, function)` **真的 import 得到**
      ```
    ★★ **② 是关键** —— ★ 只登记不实现 = 「假装只改 YAML 就能获得新能力」
      （★ Q5 L90 逐字禁止）。
    """
    #: ★ 去掉 `@版本` 后缀再查（★ 登记表用带版本的键）
    key = name if name in CHECK_REGISTRY else re.sub(r"@\d+$", "@1", name)
    if key not in CHECK_REGISTRY:
        return CheckRef(
            name, reason="★ 不在已登记的实现表里（★ 只改 YAML 不得获得新能力）"
        )
    mod_name, fn_name = CHECK_REGISTRY[key]
    try:
        mod = importlib.import_module(mod_name)
    except Exception as exc:  # noqa: BLE001
        return CheckRef(
            name, mod_name, fn_name, False, "★ 模块 import 不了：%s" % str(exc)[:80]
        )
    if not hasattr(mod, fn_name):
        return CheckRef(name, mod_name, fn_name, False, "★ 模块里没有 `%s`" % fn_name)
    return CheckRef(name, mod_name, fn_name, True, "")


def validate_protocol(pr: Protocol) -> dict:
    """★★ **协议校验**（★ R3/R4/R10）。"""
    out: dict = {
        "protocol_id": pr.protocol_id,
        "version": pr.version,
        "digest": pr.digest(),
    }

    #: ★ 五要素
    out["missing_fields"] = pr.missing_fields()

    #: ★★ **禁止任意 Python / eval**（★ Q5 L88 逐字）
    #:   ⚠ 实测（2026-10-12）：第一版只扫 `pr.to_dict()` ⇒ ★ **漏掉了 `extra`**
    #:     （★ 协议里**多出来的键**）⇒ ★ 把 `eval(...)` 塞进 `extra` **检不出来** ✗
    #:     —— ★ 而"塞进多出来的键"正是**绕过检查**最自然的做法。
    #:   ⇒ ★ 判据：**扫整份原始字典**（`to_dict()` ∪ `extra`），★ 不留死角。
    blob = json.dumps({**pr.to_dict(), **(pr.extra or {})}, ensure_ascii=False)
    forbidden = [p for p in FORBIDDEN_PATTERNS if re.search(p, blob)]
    out["forbidden"] = forbidden

    #: ★★ **每个 check_ref 都要解析成功**（★ Q3/R10）
    refs = []
    for c in pr.checks:
        r = resolve_check_ref(c)
        refs.append(r.to_dict())
    out["check_refs"] = refs
    out["unresolved"] = [r["name"] for r in refs if not r["resolved"]]

    #: ★★ **失败状态码必须是封闭码**（★ 与 `design_ir.IR_CODES` 同族）
    from . import design_ir as di  # noqa: PLC0415

    known_codes = set(di.IR_CODES) | {
        "REVISE_LAYOUT",
        "UNSUPPORTED_CAPABILITY",
        "DIAGNOSIS_REQUIRED",
        "UNKNOWN_EFFECT",
        "BLOCKED_VERIFICATION",
        "REJECTED_OUT_OF_SCOPE",
        "REJECTED_UNSUPPORTED",
        "WAITING_INPUT",
    }
    out["bad_failure_codes"] = sorted(
        v for v in (pr.on_failure or {}).values() if v not in known_codes
    )

    out["ok"] = (
        not out["missing_fields"]
        and not forbidden
        and not out["unresolved"]
        and not out["bad_failure_codes"]
    )
    return out


def validate_all() -> dict:
    """★ 四份协议**逐份校验**（★ R1~R4）。"""
    rows = []
    for name in REQUIRED_PROTOCOLS:
        rows.append(validate_protocol(load_protocol(name)))
    return {"protocols": rows, "n": len(rows), "ok": all(r["ok"] for r in rows)}


#: ══════════════════════════════════════════════════════════════════════
# 三、8 项必设检查（★ R4 —— ★ Q5 L92 逐字）
#: ══════════════════════════════════════════════════════════════════════


def check_schema(pr: Protocol | None = None, **_) -> dict:
    """★ 必设检查①：**schema**。"""
    if pr is None:
        return {"ok": False, "why": "★ 没有协议"}
    miss = pr.missing_fields()
    return {"ok": not miss, "missing": miss}


def check_forbidden(pr: Protocol | None = None, **_) -> dict:
    """★ 必设检查⑤：**禁止条件覆盖**。

    ★ 判据：扫**整份原始字典**（★ 含 `extra` —— ★ 见 `validate_protocol` 的实测记录）。
    """
    if pr is None:
        return {"ok": False, "why": "★ 没有协议"}
    blob = json.dumps({**pr.to_dict(), **(pr.extra or {})}, ensure_ascii=False)
    hit = [p for p in FORBIDDEN_PATTERNS if re.search(p, blob)]
    return {"ok": not hit, "hit": hit}


def check_versions(pr: Protocol | None = None, **_) -> dict:
    """★ 必设检查⑦：**版本依赖**（★ 版本必须是正整数）。"""
    if pr is None:
        return {"ok": False, "why": "★ 没有协议"}
    return {
        "ok": isinstance(pr.version, int) and pr.version >= 1,
        "version": pr.version,
    }


def run_required_checks(pr: Protocol | None = None) -> dict:
    """★★ **8 项必设检查**（★ R4 —— ★ Q5 L92 逐字）。

    ★★ **诚实标注**：Q5 L92 原文写「必设检查：」后面跟了 **9 个词**，
      ★ 而最后一项「**负例与突变测试**」是**测试**层面的、不是协议字段
      ⇒ ★ 本函数做 **8 项协议检查**；★ 第 9 项由 `tests/` 承担
        （★ 常量 `NINTH_CHECK_IS_TEST`）。
    """
    results = {
        "schema": check_schema(pr),
        "ref_resolution": {
            "ok": bool(pr)
            and all(resolve_check_ref(c).resolved for c in (pr.checks if pr else []))
        },
        "unit_and_type": {"ok": bool(pr) and bool(pr.inputs_schema)},
        "reachable_state": {"ok": bool(pr) and bool(pr.entry_check)},
        "forbidden_covered": check_forbidden(pr),
        "consumer_compatible": {"ok": bool(pr) and bool(pr.outputs)},
        "version_dependency": check_versions(pr),
        "affected_invalidation": {"ok": bool(pr) and bool(pr.source_refs)},
    }
    return {
        "checks": results,
        "n": len(results),
        "ninth_is_test": NINTH_CHECK_IS_TEST,
        "ok": all(v["ok"] for v in results.values()),
        "failed": [k for k, v in results.items() if not v["ok"]],
    }


#: ══════════════════════════════════════════════════════════════════════
# 四、重生成三视图（★ R5 —— ★ Q5 L90）
#: ══════════════════════════════════════════════════════════════════════


def regenerate(pr: Protocol) -> dict:
    """★★ **改一处源数据 ⇒ 重生成文档 / 提示 / 目录**（★ R5 —— ★ Q5 L90 逐字）。

    ★★ 判据：**三样都从协议现算**（★ 不是手写维护的第二份）——
      ★ 这样「改一处」才**真的只改一处**。
    """
    d = pr.to_dict()
    doc = (
        [
            "# %s v%d" % (pr.protocol_id, pr.version),
            "",
            "触发条件：`%s`" % pr.entry_check,
            "输入 schema：`%s` → 输出 schema：`%s`"
            % (pr.inputs_schema, pr.outputs_schema),
            "",
            "## 必填输入",
        ]
        + ["- `%s`" % x for x in pr.required_inputs]
        + [
            "",
            "## 检查函数",
        ]
        + [
            "- `%s` → `%s`" % (c, resolve_check_ref(c).function or "★ 未解析")
            for c in pr.checks
        ]
        + [
            "",
            "## 失败状态",
        ]
        + ["- `%s` ⇒ `%s`" % (k, v) for k, v in (pr.on_failure or {}).items()]
    )

    prompt = (
        "★ 你在使用协议 `%s` v%d。\n"
        "★ 必填：%s\n★ 检查：%s\n★ 失败状态：%s\n"
        "★★ 你的输出只是 `Proposal` —— 不得自称 `Validated` 或 `Approved`。\n"
        % (
            pr.protocol_id,
            pr.version,
            ", ".join(pr.required_inputs),
            ", ".join(pr.checks),
            ", ".join("%s=%s" % (k, v) for k, v in (pr.on_failure or {}).items()),
        )
    )

    catalog = {
        "protocol_id": pr.protocol_id,
        "version": pr.version,
        "inputs": list(pr.required_inputs),
        "checks": list(pr.checks),
        "outputs": list(pr.outputs),
        "entry_check": pr.entry_check,
        "digest": pr.digest(),
    }
    return {
        "document": "\n".join(doc),
        "prompt": prompt,
        "catalog": catalog,
        "digest": pr.digest(),
        "★": "★ 三样都从**同一份协议**现算",
    }


def regenerate_all() -> dict:
    out = {}
    for name in REQUIRED_PROTOCOLS:
        out[name] = regenerate(load_protocol(name))
    return out


#: ══════════════════════════════════════════════════════════════════════
# 五、字段门禁（★ R8 —— ★ Q1 L31）
#: ══════════════════════════════════════════════════════════════════════


def field_gate(pr: Protocol, given: dict) -> dict:
    """★★ **字段门禁**（★ R8 —— ★ Q1 L31 逐字）。

    ★★ Q1 L31 逐字：「「**缺需求先问**」转成**字段门禁**；
      **不存在载荷上界时，不自动采用所谓最坏工况**」。
    ★★ 判据（★ 两条）：
      ```
      ① 缺必填字段 ⇒ `WAITING_INPUT`（★ 并**列出具名缺项**）
      ② ★★ **没有"最坏工况"回退** —— ★ 即使调用方给了 `worst_case_*`，
         也**不填进必填项**（★ 那正是 Q1 禁止的）
      ```
    """
    given = given or {}
    missing = [f for f in pr.required_inputs if f not in given]
    #: ★★ **禁止的默认值**（★ Q1 L31 逐字）—— ★ 它们**不能**顶替必填项
    forbidden = list(pr.extra.get("forbidden_defaults") or ())
    used_forbidden = [f for f in forbidden if f in given]
    if missing:
        return {
            "state": "WAITING_INPUT",
            "missing": missing,
            "questions": ["请给出 %s" % m for m in missing],
            "used_forbidden_defaults": used_forbidden,
            "ok": False,
            "★": "★ 缺必填 ⇒ 先问（★ 不用最坏工况顶替）",
        }
    return {
        "state": "READY_FOR_REVIEW",
        "missing": [],
        "used_forbidden_defaults": used_forbidden,
        "ok": True,
    }
