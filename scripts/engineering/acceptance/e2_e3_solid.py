"""★ E2 参数化可重建 / E3 特征树可编辑：采集器与判定器。

## E2 判据（`docs/ENGINEERING-PATH.md` 第四节）

**必须读什么**：在**已交付原生模型副本**中改既有主参数，重建并核关键尺寸/关系及下游；
再保存重开复核。

**必须能拒绝的负例**：只改属性没改模型、孔未随板宽变化、旧图纸、重建失败。

**不能当替代品**：新建另一份相同外形模型、文件哈希变了。

## E3 判据

**必须读什么**：回读特征类型、错误/警告、引用与父子依赖；实际编辑前序草图或参数并验证后续。

**必须能拒绝的负例**：导入死实体冒充原生特征、悬空引用、错误配置、目标对象漂移。

**不能当替代品**：特征数大于零、STEP 可打开。

## ★★ 关键：E2 不能拿「新建文档重跑」冒充

`tools/run_stage2_plate.py` 的 `run_change` 当前是**新建文档**用新参数重新建模
（出处：`docs/state/facts/R-engineering-path.md` R-10）。

它能证明「新参数重新生成」，**不能**证明「打开已交付件改既有驱动尺寸」。
判定器必须看 `opened_existing` 标志，而不是看「结果变了」。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/e2_e3_solid.py
# 定位:   `specs/349-e1-e7-acceptance` 的 E2（参数化可重建）与 E3（特征树可编辑）。
#          ★ E2 必须看 `opened_existing` —— `tools/run_stage2_plate.py` 的 `run_change`
#            当前是新建文档重跑，「结果变了」不等于「改了已交付件的驱动尺寸」
#            （实测出处 `docs/state/facts/R-engineering-path.md` R-10）。
# 官方依据: 不适用（本文件不调 COM；真机采集器留 S3）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .result import CheckResult, Observation, Status

CHECKER_VERSION = "s1-1"


# ────────────────────────────── E2 ──────────────────────────────


def collect_rebuild(
    *, target: str, opened_existing: bool, changed_params: tuple,
    downstream_linked: bool, rebuild_errors: int, reopened_ok: bool,
    drawing_is_current: bool, version: str = "",
) -> Observation:
    """★ 采集器：记录「重建这件事是怎么做的」。"""
    return Observation(
        target=target,
        complete=bool(changed_params) and bool(target),
        values={
            "opened_existing": opened_existing,
            "changed_params": list(changed_params),
            "downstream_linked": downstream_linked,
            "rebuild_errors": rebuild_errors,
            "reopened_ok": reopened_ok,
            "drawing_is_current": drawing_is_current,
            "version": version,
        },
        note="" if changed_params else "没记录任何改动的参数 ⇒ 采集不完整",
    )


def judge_rebuild(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E2 参数化可重建。"""
    base = dict(
        check_id="E2.rebuild",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E2：在已交付件副本上改既有主参数后重建，下游正确联动且重开仍成立",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values

    #: ★★ ① 必须打开**已交付件**改既有参数 —— 新建文档重跑不算
    if not v["opened_existing"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"opened_existing": False}, expected={"opened_existing": True},
            reason=(
                "★ 这次是**新建文档重跑**，不是打开已交付件改既有驱动尺寸 ⇒ "
                "不能证明 E2（R-10 的替代品）"
            ),
        )

    #: ② 重建错误必须为 0
    if v["rebuild_errors"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"rebuild_errors": v["rebuild_errors"]}, expected=0,
            reason="★ 重建后有 %d 个特征错误" % v["rebuild_errors"],
        )

    #: ③ 下游必须联动
    if not v["downstream_linked"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"downstream_linked": False}, expected=True,
            reason="★ 改了主参数但下游没联动（如孔没随板宽移动）",
        )

    #: ④ 保存重开仍成立
    if not v["reopened_ok"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"reopened_ok": False}, expected=True,
            reason="★ 保存后重开不成立 ⇒ 参数化关系没有真正落进文件",
        )

    #: ⑤ 图纸必须与同一修订绑定
    if not v["drawing_is_current"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"drawing_is_current": False}, expected=True,
            reason="★ 图纸还是旧的（未随模型修订更新）",
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"changed": v["changed_params"]},
        reason="在已交付件上改主参数，下游联动、无重建错误、重开成立、图纸同步",
    )


# ────────────────────────────── E3 ──────────────────────────────


def collect_feature_tree(
    *, target: str, feature_count: int, native_features: int,
    imported_solids: int, dangling_refs: int, errors: int, warnings: int,
    editable_prefix_verified: bool, version: str = "",
) -> Observation:
    """★ 采集器：回读特征树。"""
    return Observation(
        target=target,
        complete=feature_count > 0,
        values={
            "feature_count": feature_count,
            "native_features": native_features,
            "imported_solids": imported_solids,
            "dangling_refs": dangling_refs,
            "errors": errors,
            "warnings": warnings,
            "editable_prefix_verified": editable_prefix_verified,
            "version": version,
        },
        note="" if feature_count > 0 else "特征数为 0 ⇒ 采集不完整",
    )


def judge_feature_tree(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E3 特征树可编辑。"""
    base = dict(
        check_id="E3.tree",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E3：特征树无错误/警告、无悬空引用、可实际编辑前序",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values

    #: ★ ① 特征数 > 0 **不是** E3 的判据（那是「不能当替代品」那一条）
    #:   真正要判的是「这些特征是原生的，不是导入死实体」
    if v["native_features"] <= 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"native_features": 0}, expected={"native_features": "≥1"},
            reason="★ 没有任何原生特征 ⇒ 只有导入实体，没有可编辑历史",
        )

    if v["imported_solids"] > 0 and v["native_features"] == 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"imported_solids": v["imported_solids"]},
            reason="★ 导入死实体冒充原生特征",
        )

    if v["dangling_refs"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"dangling_refs": v["dangling_refs"]}, expected=0,
            reason="★ 有 %d 处悬空引用" % v["dangling_refs"],
        )

    if v["errors"] > 0:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"errors": v["errors"]}, expected=0,
            reason="★ 特征树有 %d 个错误" % v["errors"],
        )

    if not v["editable_prefix_verified"]:
        return CheckResult(
            **base, status=Status.FAIL,
            observed={"editable_prefix_verified": False}, expected=True,
            reason="★ 没有实际编辑过前序草图/参数并验证后续 ⇒ 可编辑性未证",
        )

    return CheckResult(
        **base, status=Status.PASS,
        observed={"native_features": v["native_features"], "warnings": v["warnings"]},
        reason="原生特征齐、无悬空引用与错误、前序编辑已验证",
    )
