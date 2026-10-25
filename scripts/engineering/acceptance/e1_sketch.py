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
    solver_status_int: int | None = None,
    driving_dimensions: int | None = None,
) -> Observation:
    """★ 采集器：只把数装进来，**不判断**。

    `relations` 与 `dimensions` 是**原始清单**（可能含重复），
    去重是判定器的事 —— 采集器不做任何「看起来合理」的清洗。

    ## ★★ 两条采集路径（`specs/350-first-part-delivery/source-verification.md`）

    真机 API 与合成数据能给出的信号**不同**：

    | 路径 | 信号 | 来源 |
    |---|---|---|
    | 枚举 | `solver_status_int` = `ISketch.GetConstrainedStatus()` 的返回值 | **真机可取** |
    | 数值 | `entities` / `relations` / `dimensions` | 真机**取不到**，只能合成 |

    ⇒ 有枚举就只判枚举（`swFullyConstrained = 3` 是权威结论）；
      没有枚举才退回数值路径；两者都没有 ⇒ `unknown`。

    ## ★★★ `driving_dimensions`：枚举「全约束」时必须配套的数

    ★ 真机实测（`tools/probe_s3_autodim_why_fully_defined.py`）暴露了一个洞：
      把草图的每一段都加 `sgFIXED`（**一条驱动尺寸都没有**），
      `GetConstrainedStatus()` 也回 **3（全约束）**。

    ⇒ 只看枚举，「全固定」与「尺寸驱动」**无法区分**。
      而 E1 明令的负例里就有「**全部固定却无驱动参数**」这一条。
    ⇒ 所以枚举说 3 时，必须再给一个 `driving_dimensions`：
      - `>= 1` ⇒ 尺寸在驱动，可以判 pass
      - `== 0` ⇒ 判 **fail**（全固定）
      - `None` ⇒ 判 **unknown**（没数过，不能当成合格）

    ⚠ **不要把数值路径当默认** —— 真机拿不到那三个数，
      填 0 就是「先填返回值」（`AGENTS.md` 环节条件第 7 条禁止）。
    """
    #: ★★★ 第 34 轮修：三个数值路径字段接受 `None`，语义是「**没量过**」。
    #:
    #:   原实现 `entities > 0` 在 `entities=None` 时崩
    #:   （`TypeError: '>' not supported between NoneType and int`），
    #:   而 docstring 又禁止填 0（那是「先填返回值」）
    #:   ⇒ 真机调用方**没有合法表达方式**。这是设计缺口。
    _entities = 0 if entities is None else int(entities)
    _relations = [] if relations is None else list(relations)
    _dimensions = [] if dimensions is None else list(dimensions)
    numeric_measured = entities is not None
    has_enum = solver_status_int is not None
    has_numeric = numeric_measured and _entities > 0
    complete = bool(solver_state) and (has_enum or has_numeric)
    return Observation(
        target=target,
        complete=complete,
        values={
            "entities": _entities,
            "relations": _relations,
            "dimensions": _dimensions,
            #: ★ 数值路径是否真的量过 —— 没有它就分不清「量到 0」与「没量」
            "numeric_measured": numeric_measured,
            "intentional_dof": intentional_dof,
            "solver_state": solver_state,
            "solver_status_int": solver_status_int,
            #: ★ 枚举说「全约束」时必须配套：0 = 全固定，>=1 = 尺寸驱动，None = 没数过
            "driving_dimensions": driving_dimensions,
        },
        unit={},
        note="" if complete else "缺 solver_state，或既没有枚举也没有数值 ⇒ 采集不完整",
    )


def judge_sketch_constraint(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：对冻结要求判断，**不取数**。

    判据顺序：
      ① 采集不完整 ⇒ `unknown`（不是 fail —— 我们没测到，不等于产品坏了）
      ② ★ 有枚举 ⇒ **只信枚举**（真机权威信号），按 `swConstrainedStatus_e` 判
      ③ 重复关系 / 重复尺寸 ⇒ `fail`（★★ 这是 R-04 的伪造手法）
      ④ 去重后 DOF ≠ 有意自由度 ⇒ `fail`
      ⑤ 全固定但无驱动尺寸 ⇒ `fail`（设计意图检查）
      ⑥ 其余 ⇒ `pass`

    ⚠ ② 为什么优先：真机只能拿到枚举
      （`source-verification.md`：`GetConstrainedStatus()` 回状态枚举、非数值 DOF）。
      有枚举时再用数值去「补算」只会引入合成数据的误差。
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

    #: ② ★★ 有枚举 ⇒ 只信枚举（真机权威信号）
    status_int = obs.values.get("solver_status_int")
    if status_int is not None:
        return _judge_by_enum(
        base,
        status_int,
        obs.values.get("intentional_dof", 0),
        obs.values.get("driving_dimensions"),
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

#: ★ swConstrainedStatus_e 的官方取值 → 判定结论。
#:   出处：C:\\swapi\\enums\\swConstrainedStatus_e.md（7 个成员），
#:   归口在 scripts/sw_sketch_status.py:CONSTRAINED_STATUS。
#:   ⚠ 本表**不复制**那个 enum 表 —— 只写「这个值对 E1 意味着什么」。
_ENUM_VERDICT = {
    2: ("under", "欠定义 ⇒ 未满足 E1"),
    3: ("ok", "完全定义 ⇒ 满足 E1"),
    4: ("over", "过定义 ⇒ 不是「刚好约束」，而是约束过头"),
    5: ("bad", "无解"),
    6: ("bad", "无效解"),
}
#: ★ 1 = swUnknownConstraint、7 = swAutosolveOff ⇒ **判不了**（不是 pass、也不是 fail）
_ENUM_UNJUDGEABLE = {
    1: "swUnknownConstraint —— 求解器自己都不知道状态",
    7: "swAutosolveOff —— 自动求解关着，状态没意义",
}


def _judge_by_enum(
    base: dict,
    status_int: object,
    intentional_dof: int,
    driving_dimensions: int | None = None,
) -> CheckResult:
    """★ 按 GetConstrainedStatus() 的枚举判 E1。

    ★ 判据（真机唯一可得的信号）：
      · 3 swFullyConstrained ⇒ **还要看 `driving_dimensions`**（见下）
      · 2 swUnderConstrained ⇒ 有 intentional_dof > 0 时 pass（**有意保留**），否则 fail
      · 4 swOverConstrained / 5 / 6 ⇒ **fail**
      · 1 / 7 / 表外 ⇒ **unknown**（判不了，不猜）

    ## ★★★ 为什么 3 不能直接 pass

    真机实测（`tools/probe_s3_autodim_why_fully_defined.py`）：
    **把草图每一段都加 `sgFIXED`、一条驱动尺寸都不加，`GetConstrainedStatus()` 也回 3。**

    ⇒ 只看枚举，「全固定」与「尺寸驱动」**分不开**。
      而 E1 的负例明令包含「全部固定却无驱动参数」。

    ⇒ 所以 3 要再看 `driving_dimensions`：
      · `>= 1` ⇒ 尺寸在驱动 → pass
      · `== 0` ⇒ **fail**（全固定，不是尺寸驱动）
      · `None` ⇒ **unknown**（没数过；按「unknown ≠ pass」不得判绿）
    """
    try:
        n = int(status_int)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return CheckResult(
            **base, status=Status.UNKNOWN,
            reason="★ 枚举值 %r 不是整数 ⇒ 判不了" % (status_int,),
        )

    if n in _ENUM_UNJUDGEABLE:
        return CheckResult(
            **base, status=Status.UNKNOWN,
            observed={"solver_status": n},
            reason="★ 状态 %d 不可判定：%s" % (n, _ENUM_UNJUDGEABLE[n]),
        )

    #: ★★★ 状态 3（全约束）必须再核驱动尺寸数 —— 否则「全固定」会冒充「尺寸驱动」
    if n == 3:
        if driving_dimensions is None:
            return CheckResult(
                **base,
                status=Status.UNKNOWN,
                observed={"solver_status": 3, "driving_dimensions": None},
                expected={"driving_dimensions": ">=1"},
                reason=(
                    "★ 状态 3（全约束），但**没数过驱动尺寸** ⇒ "
                    "分不清「尺寸驱动」与「全靠 sgFIXED 固定」"
                    "（真机实测：全固定且零尺寸时状态也是 3）"
                ),
            )
        if int(driving_dimensions) <= 0:
            return CheckResult(
                **base,
                status=Status.FAIL,
                observed={"solver_status": 3, "driving_dimensions": 0},
                expected={"driving_dimensions": ">=1"},
                reason=(
                    "★ 状态 3（全约束）但**一条驱动尺寸都没有** ⇒ "
                    "这是「全部固定」，不是尺寸驱动（E1 明令的负例）"
                ),
            )

    kind, why = _ENUM_VERDICT.get(n, ("bad", "表外取值 ⇒ 不猜"))
    if kind == "ok":
        return CheckResult(
            **base, status=Status.PASS,
            observed={"solver_status": n}, expected={"solver_status": 3},
            reason="★ 状态 %d：%s" % (n, why),
        )
    if kind == "under":
        #: ★ 有意保留自由度时，欠定义是**设计意图**，不是缺陷
        if intentional_dof > 0:
            return CheckResult(
                **base, status=Status.PASS,
                observed={"solver_status": n, "intentional_dof": intentional_dof},
                expected={"solver_status": "2 且有意保留 %d" % intentional_dof},
                reason="★ 状态 %d（欠定义），但已声明有意保留 %d 个自由度 ⇒ 符合设计意图"
                % (n, intentional_dof),
            )
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"solver_status": n}, expected={"solver_status": 3},
            reason="★ 状态 %d：%s" % (n, why),
        )
    return CheckResult(
        **base, status=Status.FAIL,
        observed={"solver_status": n}, expected={"solver_status": 3},
        reason="★ 状态 %d：%s" % (n, why),
    )
