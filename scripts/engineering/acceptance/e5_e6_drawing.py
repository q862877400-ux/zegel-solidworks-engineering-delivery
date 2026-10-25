"""★ E5 图样合规 / E6 工艺可行：采集器与判定器。

## E5 判据（`docs/ENGINEERING-PATH.md` 第四节）

**必须读什么**：先由功能/制造/检验要求生成必要标注清单；
逐项绑定实际尺寸/基准/公差/技术要求及所指几何；核模型配置、尺寸值、悬空、重复矛盾和版面。

**必须能拒绝的负例**：注释数量没变但孔位标错、少关键定位尺寸、错误基准、
旧模型视图、默认材料、公差无依据。

**不能当替代品**：注释数量达标、文件非空、模板名带 GB。

## ★★ 关键：空 evidence 不得给覆盖率 1.0

`drawing_obligations.coverage` 只统计 `covered` 布尔，不看 `evidence`
（出处：`docs/state/facts/R-engineering-path.md` R-06）。
`mark_covered(obls, name)` 的 evidence 默认空串 ⇒ **覆盖率仍为 1.0**。

判定器必须要求**每条 covered 都有非空证据**。

## E6 判据

**必须读什么**：首件只选已确认机加工路线；从实际几何和工艺输入检查
刀具可达、孔深/刀具、壁厚/余量、装夹与装配空间等适用项。

**必须能拒绝的负例**：刀具进不去、无有效加工基准、越过已验证工艺范围、删除必需检查。

**不能当替代品**：通用 DFM 分数、固定经验阈值、仅声明「机加工」。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/e5_e6_drawing.py
# 定位:   `specs/349-e1-e7-acceptance` 的 E5（图样合规）与 E6（工艺可行）。
#          ★ E5 要求每条 covered 都有**非空证据** —— 因为
#            `drawing_obligations.coverage` 只数 covered 布尔、不看 evidence，
#            `mark_covered` 用默认空串也能把覆盖率刷到 1.0
#            （实测出处 `docs/state/facts/R-engineering-path.md` R-06）。
#          ★ E6 要求至少一条真正适用的检查项 —— 不得靠「全不适用」通过。
# 官方依据: 不适用（本文件不调 COM；真机采集器留 S4）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .result import CheckResult, Observation, Status

CHECKER_VERSION = "s1-1"


# ────────────────────────────── E5 ──────────────────────────────


def collect_drawing(
    *, target: str, required_items: tuple, bound_items: tuple,
    model_revision: str, drawing_revision: str,
    material_from_requirement: bool, template_ok: bool, version: str = "",
) -> Observation:
    """★ 采集器：记录「要求哪些标注」与「实际绑定了哪些」。

    `required_items` 由功能/制造/检验要求生成；
    `bound_items` 每项形如 `{"name": str, "evidence": str, "value_ok": bool}`。
    """
    return Observation(
        target=target,
        complete=bool(required_items) and bool(model_revision),
        values={
            "required_items": list(required_items),
            "bound_items": list(bound_items),
            "model_revision": model_revision,
            "drawing_revision": drawing_revision,
            "material_from_requirement": material_from_requirement,
            "template_ok": template_ok,
            "version": version,
        },
        note="" if required_items else "没有必要的标注清单 ⇒ 采集不完整",
    )


def judge_drawing(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E5 图样合规。"""
    base = dict(
        check_id="E5.drawing",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E5：必要标注清单由要求生成，逐项绑定真实图纸对象并核其值/基准/所指几何/版本",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values
    required = set(v["required_items"])
    bound = {str(b.get("name", "")): b for b in v["bound_items"]}

    #: ★★ ① 每条 covered 必须有**非空证据**（R-06 的伪造手法）
    empty_ev = [n for n, b in bound.items() if not str(b.get("evidence", "")).strip()]
    if empty_ev:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"empty_evidence": empty_ev[:5], "count": len(empty_ev)},
            expected={"empty_evidence": 0},
            reason=(
                "★ %d 条标注标了 covered 却**没有证据** ⇒ 覆盖率是空的"
                "（R-06 的伪造手法）" % len(empty_ev)
            ),
        )

    #: ② 必要标注必须逐项绑定
    missing = sorted(required - set(bound))
    if missing:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"missing": missing[:8], "count": len(missing)},
            expected={"missing": 0},
            reason="★ 少了 %d 项必要标注：%s" % (len(missing), missing[:5]),
        )

    #: ③ 绑定了但值不对
    bad_val = [n for n, b in bound.items() if b.get("value_ok") is not True]
    if bad_val:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"value_mismatch": bad_val[:8]},
            reason="★ %d 项标注绑定了但数值/基准不对" % len(bad_val),
        )

    #: ④ 图纸必须与同一模型修订绑定
    if v["drawing_revision"] != v["model_revision"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"drawing": v["drawing_revision"], "model": v["model_revision"]},
            reason="★ 图纸修订 %r ≠ 模型修订 %r ⇒ 是旧图"
            % (v["drawing_revision"], v["model_revision"]),
        )

    #: ★★ ④b 模板必须合格
    #:
    #:   ★ 为什么需要：`template_ok` 一直在采集，但判定器从没读过它 ——
    #:     实测一张 `template_ok=False` 的图纸照样判 **pass**（真洞，第 21 轮修）。
    #:   ⚠ **别矫枉**：E5 的「不能当替代品」栏逐字写着「**模板名带 GB**」不算理由
    #:     ⇒ `template_ok=True` 只是必要条件，不是通过的理由；
    #:       真正的通过还要下面那几条一起满足。
    if v.get("template_ok") is not True:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"template_ok": v.get("template_ok")},
            expected={"template_ok": True},
            reason=(
                "★ 图框模板不合格 ⇒ 整张图不合规"
                "（⚠ 注意：模板名带 GB 也**不是**通过的理由，见本模块「不能当替代品」）"
            ),
        )

    #: ⑤ 材料必须来自批准需求，不能是默认值
    if not v["material_from_requirement"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"material_from_requirement": False}, expected=True,
            reason="★ 材料不是从批准需求取的（很可能是写死的默认值）",
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"bound": len(bound), "required": len(required)},
        reason="必要标注逐项绑定、证据非空、值正确、图纸与模型同修订、材料来自需求",
    )


# ────────────────────────────── E6 ──────────────────────────────


def collect_process(
    *, target: str, route: str, checks: tuple, verified_scope: tuple,
    version: str = "",
) -> Observation:
    """★ 采集器：记录已确认工艺路线与各适用项的实际读数。

    `checks` 每项形如 `{"name": str, "applicable": bool, "passed": bool, "value": any}`。
    """
    return Observation(
        target=target,
        complete=bool(route) and bool(checks),
        values={
            "route": route,
            "checks": list(checks),
            "verified_scope": list(verified_scope),
            "version": version,
        },
        note="" if route and checks else "缺工艺路线或检查项 ⇒ 采集不完整",
    )


def judge_process(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E6 工艺可行。"""
    base = dict(
        check_id="E6.process",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E6：从实际几何与工艺输入检查已确认工艺路线的适用项",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values

    #: ① 工艺路线必须在已验证范围内
    if v["route"] not in v["verified_scope"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"route": v["route"]},
            expected={"in": v["verified_scope"]},
            reason="★ 工艺路线 %r 不在已验证范围 %r 内" % (v["route"], v["verified_scope"]),
        )

    #: ② 必须有真正适用的检查项（不能全是「不适用」）
    applicable = [c for c in v["checks"] if c.get("applicable")]
    if not applicable:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"applicable": 0, "total": len(v["checks"])},
            expected={"applicable": "≥1"},
            reason="★ 一条适用检查项都没有 ⇒ 不能靠「全不适用」通过 E6",
        )

    #: ③ 适用项必须全过
    failed = [c.get("name") for c in applicable if c.get("passed") is not True]
    if failed:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"failed": failed[:8]},
            reason="★ %d 项适用工艺检查未过：%s" % (len(failed), failed[:5]),
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"route": v["route"], "applicable": len(applicable)},
        reason="工艺路线在已验证范围内，且 %d 项适用检查全过" % len(applicable),
    )
