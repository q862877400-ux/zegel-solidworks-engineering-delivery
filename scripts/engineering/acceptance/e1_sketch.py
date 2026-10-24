"""★ E1 草图全约束：采集器与判定器。

## 判据（`docs/ENGINEERING-PATH.md` 第四节）

**必须读什么**：枚举全部适用草图；读取实际求解状态、欠约束实体、关系对象和驱动尺寸；
位置/形状/大小均由约束表达。无异常、无欠约束；全固定还须检查设计意图。

**必须能拒绝的负例**：删定位关系、删尺寸、重复关系、全部固定却无驱动参数、采集失败。

**不能当替代品**：数关系、预填 expected_status、截图颜色、把未知 DOF 写 0。

## ★★ 关键：重复关系必须被拒

`part_loop.DofPlan.total_dof` 的公式是 `2×实体数 − 关系数 − 尺寸数`，
**同一条关系重复 8 次会算出 DOF = 0**（出处：`docs/state/facts/R-engineering-path.md` R-04）。

判定器必须**按关系的唯一性**去重后再算，而不是直接吃公式的结果。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/e1_sketch.py
# 定位:   `specs/349-e1-e7-acceptance` 的 E1（草图全约束）采集器 + 判定器。
#          ★ 判定器按**关系唯一性去重**后再算 DOF，并拒绝含重复的输入 ——
#            因为 `part_loop.DofPlan.total_dof` 按数量算，同一条关系重复 8 次
#            也能算出 DOF=0（实测出处 `docs/state/facts/R-engineering-path.md` R-04）。
# 官方依据: 不适用（本文件不调 COM；真机采集器留 S3，届时按铁律 4 三源互证）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .result import CheckResult, Observation, Status

CHECKER_VERSION = "s1-1"


def collect_sketch_constraint(
    *, target: str, entities: int, relations: tuple, dimensions: tuple,
    intentional_dof: int = 0, solver_state: str = "", version: str = "",
) -> Observation:
    """★ 采集器：只把数装进来，**不判断**。

    `relations` 与 `dimensions` 是**原始清单**（可能含重复），
    去重是判定器的事 —— 采集器不做任何「看起来合理」的清洗。
    """
    complete = bool(solver_state) and entities > 0
    return Observation(
        target=target,
        complete=complete,
        values={
            "entities": entities,
            "relations": list(relations),
            "dimensions": list(dimensions),
            "intentional_dof": intentional_dof,
            "solver_state": solver_state,
        },
        unit={},
        note="" if complete else "缺 solver_state 或 entities=0 ⇒ 采集不完整",
    )


def judge_sketch_constraint(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：对冻结要求判断，**不取数**。

    判据顺序：
      ① 采集不完整 ⇒ `unknown`（不是 fail —— 我们没测到，不等于产品坏了）
      ② 重复关系 / 重复尺寸 ⇒ `fail`（★★ 这是 R-04 的伪造手法）
      ③ 去重后 DOF ≠ 有意自由度 ⇒ `fail`
      ④ 全固定但无驱动尺寸 ⇒ `fail`（设计意图检查）
      ⑤ 其余 ⇒ `pass`
    """
    base = dict(
        check_id="E1.dof",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        unit="自由度",
        basis="E1：草图全约束（几何约束 + 尺寸约束驱动，非坐标硬拽）",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )

    #: ① 采集不完整 ⇒ unknown
    if not obs.complete:
        return CheckResult(
            **base, status=Status.UNKNOWN,
            reason="采集不完整：%s" % (obs.note or "缺必要读数"),
        )

    rels = obs.values["relations"]
    dims = obs.values["dimensions"]
    n_ent = obs.values["entities"]

    #: ② ★★ 重复关系 / 重复尺寸 ⇒ fail（R-04 的伪造手法）
    #:   ⚠ 不能直接吃 `2E − R − D`：重复贴同一条关系能把 DOF 压到 0
    uniq_rels = list(dict.fromkeys(rels))
    uniq_dims = list(dict.fromkeys(dims))
    dup_rels = len(rels) - len(uniq_rels)
    dup_dims = len(dims) - len(uniq_dims)
    if dup_rels or dup_dims:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dup_relations": dup_rels, "dup_dimensions": dup_dims},
            expected={"dup_relations": 0, "dup_dimensions": 0},
            reason=(
                "★ 存在重复约束：关系重复 %d 条、尺寸重复 %d 条 ⇒ "
                "按 `2E−R−D` 算出的 DOF 是**假的**（R-04 的伪造手法）"
                % (dup_rels, dup_dims)
            ),
        )

    #: ③ 去重后算 DOF
    dof = max(0, 2 * n_ent - len(uniq_rels) - len(uniq_dims))
    want = obs.values["intentional_dof"]
    if dof != want:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dof": dof}, expected={"dof": want},
            reason="★ 自由度 %d ≠ 有意自由度 %d ⇒ 欠约束或过约束" % (dof, want),
        )

    #: ④ 全固定但无驱动尺寸 ⇒ 设计意图不成立
    if dof == 0 and not uniq_dims:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dof": 0, "dimensions": 0}, expected={"dimensions": "≥1"},
            reason="★ DOF=0 但一条驱动尺寸都没有 ⇒ 靠固定几何凑出来的，不可参数化",
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"dof": dof, "relations": len(uniq_rels), "dimensions": len(uniq_dims)},
        expected={"dof": want},
        reason="自由度符合设计意图，且约束无重复、有驱动尺寸",
    )
