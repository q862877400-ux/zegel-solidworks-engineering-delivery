"""★ E1–E7 验收的统一结果结构。

## 判据（逐字承 `docs/ENGINEERING-PATH.md` 第四节）

统一结果必须含：检查 ID、要求 ID、对象/配置、观测是否完整、原始值与单位、
期望值/依据、状态、原因、证据引用、产物版本、检查器版本。

## 四值状态

`pass / fail / unknown / not_applicable`。

★★ **`unknown` 不是 `fail` 的别名** ——
  - `fail` = 取到了数，且数不符合要求 ⇒ **产物不合格**
  - `unknown` = 没取到数（采集失败 / 上游失败 / 对象未覆盖）⇒ **报告不绿，但不能说产物不合格**

  两者必须可区分。把 `unknown` 当 `fail` 会把「我们没测」说成「产品坏了」；
  把 `unknown` 当 `pass` 就是自我认证。

★★ **禁止把其他非空字符串当 true** ——
  既有多套 verdict（`PASS` / `pass` / `OK` / `True` / `是`）必须显式映射到本枚举，
  不得用 `bool(x)` 判。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/result.py
# 定位:   `specs/349-e1-e7-acceptance` 的 FR-008/FR-009 —— E1–E7 的统一结果结构。
#          ★ 11 个必填字段与四值状态逐字承 `docs/ENGINEERING-PATH.md` 第四节。
#          两条硬不变式在 `CheckResult.__post_init__` 强制：
#            ① 观测不完整 ⇒ 状态必为 unknown（不许在没取到数时判 pass/fail）
#            ② 状态必须是 Status 枚举（堵住「非空字符串当 true」）
# 官方依据: 不适用（纯 Python 层）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    """★ 四值状态（封闭枚举 —— 不接受表外取值）。"""

    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"

    @classmethod
    def of(cls, value: object) -> Status:
        """★ 把外部 verdict 显式映射到本枚举。

        ⚠ **不做** `bool(value)` 这类隐式转换 —— 那会把 `"no"` 判成 True。
        表外取值一律 `unknown`（不是 pass，也不是 fail）。
        """
        if isinstance(value, Status):
            return value
        if isinstance(value, bool):
            return cls.PASS if value else cls.FAIL
        if isinstance(value, str):
            v = value.strip().lower()
            mapping = {
                "pass": cls.PASS,
                "ok": cls.PASS,
                "true": cls.PASS,
                "yes": cls.PASS,
                "是": cls.PASS,
                "fail": cls.FAIL,
                "failed": cls.FAIL,
                "false": cls.FAIL,
                "no": cls.FAIL,
                "否": cls.FAIL,
                "unknown": cls.UNKNOWN,
                "未测": cls.UNKNOWN,
                "not_applicable": cls.NOT_APPLICABLE,
                "n/a": cls.NOT_APPLICABLE,
                "不适用": cls.NOT_APPLICABLE,
            }
            return mapping.get(v, cls.UNKNOWN)
        return cls.UNKNOWN

    @property
    def is_green(self) -> bool:
        """★ 只有 `pass` 与 `not_applicable` 让报告变绿。"""
        return self in (Status.PASS, Status.NOT_APPLICABLE)


@dataclass
class CheckResult:
    """★ 一条检查的统一结果（11 个必填字段）。"""

    #: ① 检查 ID（如 `E1.dof`）
    check_id: str
    #: ② 要求 ID（对应需求表里的编号）
    requirement_id: str
    #: ③ 对象 / 配置（哪个零件、哪个配置）
    target: str
    #: ④ 观测是否完整（采集器给；False ⇒ 状态必为 unknown）
    observation_complete: bool
    #: ⑤ 原始值与单位
    observed: object = None
    unit: str = ""
    #: ⑥ 期望值 / 依据
    expected: object = None
    basis: str = ""
    #: ⑦ 状态
    status: Status = Status.UNKNOWN
    #: ⑧ 原因
    reason: str = ""
    #: ⑨ 证据引用
    evidence: tuple = ()
    #: ⑩ 产物版本
    artifact_version: str = ""
    #: ⑪ 检查器版本
    checker_version: str = "s1-1"

    def __post_init__(self) -> None:
        #: ★ 不变式 ①：观测不完整 ⇒ 状态必须是 unknown
        #:   （不许在没取到数的情况下判 pass 或 fail）
        if not self.observation_complete and self.status is not Status.UNKNOWN:
            raise ValueError(
                "★ 观测不完整却给了 %r —— 采集失败只能是 unknown" % self.status
            )
        #: ★ 不变式 ②：状态必须是四值之一（封闭枚举由类型系统保证，这里挡字符串）
        if not isinstance(self.status, Status):
            raise TypeError("★ status 必须是 Status 枚举，收到 %r" % type(self.status))

    @property
    def is_green(self) -> bool:
        return self.status.is_green

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "requirement_id": self.requirement_id,
            "target": self.target,
            "observation_complete": self.observation_complete,
            "observed": self.observed,
            "unit": self.unit,
            "expected": self.expected,
            "basis": self.basis,
            "status": self.status.value,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "artifact_version": self.artifact_version,
            "checker_version": self.checker_version,
        }


@dataclass
class Observation:
    """★ 采集器的产出：只装数，不装判断。

    ★ `complete=False` 表示「没取到」——判定器据此必须给 `unknown`，
      不得因为「没看到问题」就给 `pass`。
    """

    target: str
    complete: bool
    values: dict = field(default_factory=dict)
    unit: dict = field(default_factory=dict)
    evidence: tuple = ()
    note: str = ""


def rollup(results: list) -> dict:
    """★ 把一组 `CheckResult` 汇总成一个报告判定。

    ★ 判据：**任一 `fail` 或任一 `unknown` 都使整体不绿**。
      `not_applicable` 不算失败，但必须有理由（由判定器保证）。
    """
    bad = [r for r in results if r.status is Status.FAIL]
    unknown = [r for r in results if r.status is Status.UNKNOWN]
    return {
        "total": len(results),
        "pass": sum(1 for r in results if r.status is Status.PASS),
        "fail": len(bad),
        "unknown": len(unknown),
        "not_applicable": sum(1 for r in results if r.status is Status.NOT_APPLICABLE),
        "failed_ids": [r.check_id for r in bad],
        "unknown_ids": [r.check_id for r in unknown],
        "ok": not bad and not unknown and bool(results),
    }
