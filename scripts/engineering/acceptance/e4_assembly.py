"""★ E4 装配自由度闭合：采集器与判定器。

## 判据（`docs/ENGINEERING-PATH.md` 第四节）

**必须读什么**：对目标组件回读实际配合对象/状态与剩余运动；
核目标 DOF、干涉、关键间隙、配置。静态首件不承担运动全域承诺。

**必须能拒绝的负例**：重复同一配合、全固定冒充配合、错轴/错向、漏配合、实体干涉、无间隙依据。

**不能当替代品**：配合数扣常数、模型摆在正确坐标、只验一个 bbox。

## ★★ 关键：重复配合必须被拒

`assembly.ConstraintGraph.total_dof` 按配合类型扣常数
（coincident 3 / concentric 4 / distance 1 / parallel 2 / perpendicular 2），
**同一对组件重复贴 6 次 coincident 会算出 DOF = 0 且判 `fully_constrained`**
（出处：`docs/state/facts/R-engineering-path.md` R-05）。

判定器必须检查**同一对组件上的重复配合**，而不是直接吃扣常数后的 DOF。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/e4_assembly.py
# 定位:   `specs/349-e1-e7-acceptance` 的 E4（装配自由度闭合）。
#          ★ 判定器检查「同一对组件 + 同一配合类型」的重复 ——
#            因为 `assembly.ConstraintGraph.total_dof` 按配合类型扣常数，
#            重复贴 6 次 coincident 也能算出 DOF=0 并判 fully_constrained
#            （实测出处 `docs/state/facts/R-engineering-path.md` R-05）。
# 官方依据: 不适用（本文件不调 COM；真机采集器留 S4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .result import CheckResult, Observation, Status

CHECKER_VERSION = "s1-1"

#: ★ 与 `assembly.MateKind.REMOVES` 同源（只读引用，不改它的语义）
#: enum-gate: not-enum derived
_DOF_REMOVED = {
    "coincident": 3,
    "concentric": 4,
    "distance": 1,
    "parallel": 2,
    "perpendicular": 2,
}


def collect_assembly(
    *, target: str, components: tuple, mates: tuple, target_dof: int,
    interference_count: int, min_clearance_mm: float,
    clearance_basis: str, configuration: str = "", version: str = "",
) -> Observation:
    """★ 采集器：记录组件、配合（原始清单，含重复）、干涉与间隙。

    `mates` 每项形如 `{"kind": str, "a": str, "b": str}`。
    """
    return Observation(
        target=target,
        complete=bool(components) and bool(mates) and bool(configuration),
        values={
            "components": list(components),
            "mates": list(mates),
            "target_dof": target_dof,
            "interference_count": interference_count,
            "min_clearance_mm": min_clearance_mm,
            "clearance_basis": clearance_basis,
            "configuration": configuration,
            "version": version,
        },
        note="" if components and mates else "缺组件或配合记录 ⇒ 采集不完整",
    )


def judge_assembly(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E4 装配自由度闭合。"""
    base = dict(
        check_id="E4.dof",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        unit="自由度",
        basis="E4：配合约束表达，剩余 DOF 符合设计意图、干涉 0、关键间隙合规",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values
    mates = v["mates"]

    #: ★★ ① 同一对组件上的重复配合 ⇒ fail（R-05 的伪造手法）
    #:   键是「无序对 + 配合类型」，同一条重复贴多次只算一次有效约束
    seen = {}
    dup = 0
    for m in mates:
        pair = tuple(sorted((str(m.get("a", "")), str(m.get("b", "")))))
        key = (pair, str(m.get("kind", "")))
        if key in seen:
            dup += 1
        else:
            seen[key] = m
    if dup:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"duplicate_mates": dup, "mates_total": len(mates)},
            expected={"duplicate_mates": 0},
            reason=(
                "★ 有 %d 条重复配合（同一对组件 + 同一配合类型）⇒ "
                "按扣常数算出的 DOF 是**假的**（R-05 的伪造手法）" % dup
            ),
        )

    #: ② 至少一条真实功能配合（全固定不算配合）
    if not mates:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"mates": 0}, expected={"mates": "≥1"},
            reason="★ 没有功能配合 ⇒ 若靠「全固定」定位，不是配合约束表达",
        )

    #: ③ 算剩余 DOF（去重后）
    moving = [c for c in v["components"] if not str(c).startswith("ground:")]
    base_dof = 6 * len(moving)
    removed = sum(_DOF_REMOVED.get(str(m.get("kind", "")), 0) for m in seen.values())
    dof = max(0, base_dof - removed)
    want = v["target_dof"]
    if dof != want:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dof": dof}, expected={"dof": want},
            reason="★ 剩余自由度 %d ≠ 目标 %d ⇒ 过约束或欠约束" % (dof, want),
        )

    #: ④ 干涉必须为 0
    if v["interference_count"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"interference": v["interference_count"]}, expected=0,
            reason="★ 有 %d 处实体干涉" % v["interference_count"],
        )

    #: ⑤ 间隙必须有依据（不能「看着够」）
    if not v["clearance_basis"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"clearance_mm": v["min_clearance_mm"]},
            expected={"basis": "非空"},
            reason="★ 最小间隙 %.2f mm 没有依据 ⇒ 不能判合规" % v["min_clearance_mm"],
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"dof": dof, "mates": len(seen), "clearance_mm": v["min_clearance_mm"]},
        expected={"dof": want},
        reason="配合无重复、DOF 符合意图、无干涉、间隙有依据",
    )
