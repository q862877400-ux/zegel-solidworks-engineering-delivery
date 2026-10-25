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
def _mate_kind_key(kind) -> str:
    """把配合类型归一化成 `_DOF_REMOVED` 的键。

    ★ 第 61 轮：真机读到的是**特征类型名** `MateCoincident`，
      而表里写的是 `coincident` ⇒ 查不到 ⇒ 扣常数算成 0。
      归一化：去前缀 `Mate`、转小写、去掉非字母。
    """
    s = str(kind or "").strip().lower()
    if s.startswith("mate"):
        s = s[4:]
    return "".join(ch for ch in s if ch.isalpha())


#: enum-gate: not-enum derived
#: ★ 这张表**不是官方枚举值**，是「每种配合约束掉几个自由度」的**推算常数**
#:   （coincident 3 / concentric 4 / distance 1 / parallel 2 / perpendicular 2）。
#:   它只在 dof_measured=True 时参与计算；本机读不到 DOF ⇒ 默认走 unknown。
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
    #: ★★ 第 61 轮：DOF 是否**实测**。本机没有数值 DOF 读取入口（三源确认）
    #:   ⇒ 默认 False ⇒ 判定器必须给 `unknown`，**不许**拿配合数估算去判 fail。
    dof_measured: bool = False,
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
            "dof_measured": bool(dof_measured),
            "interference_count": interference_count,
            "min_clearance_mm": min_clearance_mm,
            "clearance_basis": clearance_basis,
            "configuration": configuration,
            "version": version,
        },
        note="" if components and mates else "缺组件或配合记录 ⇒ 采集不完整",
    )


def judge_assembly_interference(
    obs: Observation, *, requirement_id: str
) -> CheckResult:
    """★ 判定器：E4 的**真机可验**子项 —— 配合存在 + 干涉 0 + 间隙有依据。

    ## ★★ 为什么拆出这一条

    `specs/350-first-part-delivery/source-verification.md` 三源确认：
    **SolidWorks API 没有数值自由度读取入口**（1032 接口 / 20627 成员零命中）。

    ⇒ 若 E4 只有一个「DOF 必须等于目标」的判定器，它在真机上**永远拿不到数**
      ⇒ E4 永远 `unknown` ⇒ 报告永远不绿 ⇒ 但产物可能完全合格。

    ⇒ 拆成两条检查，各自独立出结论：

    | check_id | 内容 | 真机可验 |
    |---|---|---|
    | `E4.interference` | 配合存在、干涉 0、间隙有依据 | ✅ 可验 |
    | `E4.dof` | 剩余自由度符合意图 | ❌ 读不到 ⇒ `unknown` |

    ★ 这不是放宽 E4 —— 拆分后**两条都要绿**才算 E4 成立。
      拆分只是让报告能说清「是哪一项验不了」，而不是把整条判成不合格。
    """
    base = dict(
        check_id="E4.interference",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E4：配合有功能约束对象、无实体干涉、关键间隙有依据（真机可验子项）",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values
    #: ★★★ 第 44 轮：**配合文件夹不能冒充配合**。
    #:
    #:   仓库自己的 `collect_mate_feature_summary` 把 `MateGroup` 文件夹也收进列表
    #:   ⇒ 零个真实配合时它的长度也是 1 ⇒ 原判据 `if not mates:` 被绕过 ⇒ 假绿。
    #:   真机佐证：同一个装配里 `AddMate5` 报 `error_status=4`
    #:   （`swAddMateError_e` 逐字：4 = IncorrectSelections）⇒ 配合没建成，而 `mates` 读成 1。
    #:   ⇒ 只认**有配合对象**（`a` 与 `b` 都非空）的条目。
    _all_mates = list(v["mates"])
    mates = [
        m
        for m in _all_mates
        if str(m.get("a", "")).strip() and str(m.get("b", "")).strip()
    ]

    #: ① 同一对组件上的重复配合 ⇒ fail（R-05 的伪造手法；真机能读到配合对象）
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

    #: ② 必须有真实功能配合（全固定不算）
    if not mates:
        #: ★ 分清两种「没有」：列表空 vs 只有文件夹/无对象条目
        if _all_mates:
            return CheckResult(
                **base, status=Status.FAIL,
                observed={
                    "mates_entries": len(_all_mates),
                    "mates_with_objects": 0,
                    "sample": str(_all_mates[0])[:160],
                },
                expected={"mates_with_objects": "≥1"},
                reason=(
                    "★ 读到 %d 条「配合类」条目，但**没有一条带配合对象**"
                    "（`a`/`b` 都空，典型是 `MateGroup` 配合文件夹）"
                    "⇒ 这不叫功能配合，不能靠它通过 E4" % len(_all_mates)
                ),
            )
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"mates": 0}, expected={"mates": "≥1"},
            reason="★ 没有功能配合 ⇒ 若靠「全固定」定位，不是配合约束表达",
        )

    #: ③ 干涉必须为 0（`IInterferenceDetectionMgr.GetInterferenceCount()` 真机可取）
    if v["interference_count"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"interference": v["interference_count"]}, expected=0,
            reason="★ 有 %d 处实体干涉" % v["interference_count"],
        )

    #: ④ 间隙必须有依据
    #:   ★★ 第 61 轮改 `fail` → `unknown`：**「没量过」不是「不合格」**
    #:     （第 33 轮定下的口径）。间隙 -1 表示没测，不是间隙为负。
    #:     判 fail 会把「我方没测」说成「产物坏了」，那是编事实。
    if not v["clearance_basis"]:
        return CheckResult(
            **base, status=Status.UNKNOWN,
            observed={"clearance_mm": v["min_clearance_mm"]},
            expected={"basis": "非空（实测间隙 + 依据）"},
            reason=(
                "★ 最小间隙**没有实测依据**（读数 %s）⇒ 这一项没量过，"
                "不是不合格。要判它得先量出关键间隙并写明依据"
                % v["min_clearance_mm"]
            ),
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={
            "mates": len(seen),
            "interference": v["interference_count"],
            "clearance_mm": v["min_clearance_mm"],
        },
        reason="配合无重复、无干涉、间隙有依据",
    )


def judge_assembly(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E4 装配自由度闭合（**完整版**，含 DOF 子项）。

    ⚠ 本函数含「剩余 DOF 必须等于目标」——而真机**读不到** DOF
      （三源确认，见 `source-verification.md`）。
    ⇒ 真机报告请**同时**收 `judge_assembly_interference` 的结论，
      让读者能区分「干涉/配合不合格」与「DOF 这一项验不了」。
    ⇒ 只收本函数时，DOF 读不到会表现为 `unknown`，那是**如实**，
      不是产物不合格。
    """
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

    #: ★★★ 第 61 轮：**干涉 = 0 是可直接判的事实**，放在 DOF 之前 ——
    #:   否则「DOF 没实测 ⇒ unknown」会把确凿的实体干涉挡住。
    #:   ★ 原则：**能判的先判，不能判的才 unknown**。
    if v["interference_count"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"interference": v["interference_count"]}, expected=0,
            reason="★ 有 %d 处实体干涉" % v["interference_count"],
        )

    #: ★★★ 第 61 轮：**DOF 没实测 ⇒ 直接 unknown**，不许拿估算判 fail。
    #:   本机没有数值 DOF 读取入口（`source-verification.md` 三源确认），
    #:   下面的 `base_dof - removed` 是**模型推算**，不是观测值。
    #:   ⇒ 拿它判 `fail` 就是「拿估算当观测」（本项目红线）。
    if not v.get("dof_measured"):
        moving0 = [c for c in v["components"] if not str(c).startswith("ground:")]
        est = 6 * len(moving0) - sum(
            _DOF_REMOVED.get(_mate_kind_key(m.get("kind")), 0) for m in seen.values()
        )
        return CheckResult(
            **base,
            status=Status.UNKNOWN,
            observed={"mates": len(seen), "estimated_dof": max(0, est)},
            expected={"target_dof": v["target_dof"]},
            reason=(
                "★ 剩余自由度**没有实测入口**（本机 API 无数值 DOF 读取）⇒ "
                "这一项验不了。按配合数推算约为 %d，但**估算不作为观测**" % max(0, est)
            ),
        )

    #: ③ 算剩余 DOF（去重后）
    moving = [c for c in v["components"] if not str(c).startswith("ground:")]
    base_dof = 6 * len(moving)
    removed = sum(
        _DOF_REMOVED.get(_mate_kind_key(m.get("kind")), 0) for m in seen.values()
    )
    dof = max(0, base_dof - removed)
    want = v["target_dof"]
    if dof != want:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dof": dof}, expected={"dof": want},
            reason="★ 剩余自由度 %d ≠ 目标 %d ⇒ 过约束或欠约束" % (dof, want),
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
