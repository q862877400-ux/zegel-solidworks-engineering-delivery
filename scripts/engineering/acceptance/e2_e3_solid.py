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
    """★ 采集器：回读特征树。

    ★★★ 第 33 轮修：`complete` 原来只看 `feature_count > 0` ——
      `native_features=-1`（本仓惯用 `-1` 表示「读不出」）时仍然 complete=True
      ⇒ 判定器报「没有任何原生特征 ⇒ fail」，把「**读不出**」说成了「**一个都没有**」。
      ⇒ 任一计数为负即视为采集不完整。
    """
    _counts = (feature_count, native_features, imported_solids, dangling_refs)
    _readable = all(int(c) >= 0 for c in _counts)
    return Observation(
        target=target,
        complete=feature_count > 0 and _readable,
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
        note=(
            ""
            if (feature_count > 0 and _readable)
            else (
                "特征数为 0 ⇒ 采集不完整"
                if feature_count <= 0
                else "有计数为负（读不出）⇒ 采集不完整：%r" % (_counts,)
            )
        ),
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

# ────────────────────── E3 子项：引用稳定性 ──────────────────────

#: ★ 不可跨重建的选区形态（下标 / 当前选区）。
#:   出处：`scripts/engineering/reference_resolver.py:LIMITATIONS` 逐字 ——
#:     「索引不跨编辑保持 …… 改完模型后，之前算出来的 face/edge index 全部作废」
#:   ⇒ 计划里若**存**下标，改一个主参数后「第 0 条边」可能是另一条边。
_FRAGILE_PATTERNS = (
    ("index:", "下标（第 n 条边/面）—— 改几何后可能指到别处"),
    ("__current_selection__", "依赖当前选区 —— 不是模型里的稳定事实"),
)


def collect_reference_stability(
    *, target: str, steps: tuple, version: str = ""
) -> Observation:
    """★ 采集器：记录计划里**存的**选区形态。

    `steps` 每项形如 `{"step": str, "params": dict}`。
    采集器只原样装进来，**不判断**哪个形态对不对。
    """
    return Observation(
        target=target,
        complete=bool(steps),
        values={"steps": list(steps), "version": version},
        note="" if steps else "没有步骤记录 ⇒ 采集不完整",
    )


def judge_reference_stability(
    obs: Observation, *, requirement_id: str
) -> CheckResult:
    """★ 判定器：E3 的引用稳定性 —— **跨重建不依赖选区或下标**。

    ★ 判据（`docs/ENGINEERING-PATH.md` 第四节 E3「必须读什么」）：
      「主尺寸/基准/孔位必须有稳定语义引用，跨重建不依赖选区或下标」

    ★ 接受的形态（`reference_resolver.resolve()` 支持的）：
      `+x` / `-x` / `+y` / `-y` / `+z` / `-z` · `top_face` · `near:<x>,<y>,<z>`
      —— 这些是**几何事实**，改主参数后仍然指同一类几何。

    ★ 拒绝的形态：
      `index:<n>` —— 下标会漂
      `__current_selection__` —— 取决于调用时选了什么，不是模型属性
    """
    base = dict(
        check_id="E3.reference_stability",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E3：主尺寸/基准/孔位用稳定语义引用，跨重建不依赖选区或下标",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    fragile: list = []
    for st in obs.values["steps"]:
        name = str(st.get("step", ""))
        for key, val in (st.get("params") or {}).items():
            sval = str(val)
            for pat, why in _FRAGILE_PATTERNS:
                if pat in sval:
                    fragile.append(
                        {"step": name, "param": key, "value": sval, "why": why}
                    )
                    break

    if fragile:
        first = fragile[0]
        return CheckResult(
            **base,
            status=Status.FAIL,
            observed={"fragile": fragile[:6], "count": len(fragile)},
            expected={"fragile": 0},
            reason=(
                "★ %d 处选区是**不可跨重建**的形态。首例：步骤 %r 的 %s=%r —— %s。"
                "应改用语义选择器（`+z` / `top_face` / `near:x,y,z`），"
                "由 `reference_resolver.resolve()` 在**用时**解析成下标"
                % (
                    len(fragile),
                    first["step"],
                    first["param"],
                    first["value"],
                    first["why"],
                )
            ),
        )

    return CheckResult(
        **base,
        status=Status.PASS,
        observed={"steps": len(obs.values["steps"]), "fragile": 0},
        reason="计划里没有下标或当前选区形态的引用",
    )

# ────────────────────── E2 子项：孔逐项回读 ──────────────────────

#: ★ 允许的孔型（封闭词表）。表外一律不算「已识别」。
HOLE_TYPES = (
    "through",       #: 通孔
    "blind",         #: 盲孔
    "counterbore",   #: 沉头孔
    "countersink",   #: 锥沉孔
    "threaded",      #: 螺纹孔
)


def collect_hole_readback(
    *,
    target: str,
    requested: tuple,
    measured: dict,
    position_tol_mm: float = 0.1,
    diameter_tol_mm: float = 0.05,
    version: str = "",
) -> Observation:
    """★ 采集器：记录「要求什么孔」与「B-Rep 里量到什么」。

    `requested` 每项形如
      `{"id": str, "kind": str, "diameter_mm": float, "position_mm": [x, y, z]}`
    `measured` 是 `sw_review.collect_geometry_measurements()` 的返回
      （形如 `{"holes": [...], "envelope_mm": ...}`）。

    ⚠ 真机取不到孔型（`validate_hole_positions` 的 docstring 自己写着
      「盲孔深度、通孔状态和沉头类型必须继续使用特征参数回读」）
      ⇒ 若 `measured` 里没有 `kind` 字段，采集器如实标 `unknown_kind`。
    """
    holes = list((measured or {}).get("holes") or ())
    #: ★★★ 第 33 轮修：`complete` 原来只看 `bool(requested)` ——
    #:   `measured={}` 时仍然 complete=True ⇒ 判定器报「B-Rep 里有 0 个孔 ⇒ fail」，
    #:   把「**没量过**」说成了「**量到 0 个**」。
    #:
    #:   ★ 两种情况必须分开：
    #:     · 零件真的没孔 ⇒ `{"holes": [], "errors": []}` ⇒ complete=True ⇒ fail（正确）
    #:     · 量测失败   ⇒ `{}` 或 `{"holes": [], "errors": [...]}` ⇒ complete=False ⇒ unknown
    _errs = list((measured or {}).get("errors") or ())
    _usable = bool(measured) and not (_errs and not holes)
    return Observation(
        target=target,
        complete=bool(requested) and _usable,
        values={
            "requested": list(requested),
            "measured": measured or {},
            "actual_holes": holes,
            "position_tol_mm": position_tol_mm,
            "diameter_tol_mm": diameter_tol_mm,
            #: ★ 真机常拿不到孔型 ⇒ 这个标志让判定器知道「是没测到」而非「不匹配」
            "kind_observable": bool(holes) and all("kind" in h for h in holes),
            "version": version,
        },
        note="" if requested else "没有要求孔清单 ⇒ 采集不完整",
    )


def judge_hole_readback(obs: Observation, *, requirement_id: str) -> CheckResult:
    """★ 判定器：E2 子项 —— 孔型/孔位**逐项**回读。

    ## ★★ 为什么不许只比总体积

    `docs/ENGINEERING-PATH.md` 第四节 E2 的「不能当替代品」逐字：
      「新建另一份相同外形模型、文件哈希变了」

    `s3-prep.md` 记的同族问题：比较**总切除体积**也会通过 ——
    四个 φ6 孔换成两个 φ12 孔，体积一样，但需求是四个孔。

    ## 判据

    ① 采集不完整 ⇒ `unknown`
    ② 孔数不符 ⇒ `fail`（这一条就挡住「体积相同但数量不对」）
    ③ 逐个孔的孔径与孔位必须过 `sw_review.validate_hole_positions`
    ④ 孔型：**只在 B-Rep 真的给出 `kind` 时判**；给不出 ⇒ 这一项记 `unknown`
       整体状态取 `unknown`（不是 pass —— 我们没测到孔型）
    """
    base = dict(
        check_id="E2.hole_readback",
        requirement_id=requirement_id,
        target=obs.target,
        observation_complete=obs.complete,
        basis="E2：孔型/孔位逐项回读，不得用总切除体积之类的聚合量代替",
        evidence=obs.evidence,
        artifact_version=obs.values.get("version", ""),
        checker_version=CHECKER_VERSION,
    )
    if not obs.complete:
        return CheckResult(**base, status=Status.UNKNOWN, reason="采集不完整")

    v = obs.values
    requested = v["requested"]
    actual = v["actual_holes"]

    #: ② 孔数不符 ⇒ fail（最直接的「聚合量代替」防线）
    if len(actual) != len(requested):
        return CheckResult(
            **base,
            status=Status.FAIL,
            observed={"holes": len(actual)},
            expected={"holes": len(requested)},
            reason=(
                "★ B-Rep 里有 %d 个孔，需求是 %d 个 ⇒ 数量不符"
                "（总切除体积相同的换法不算通过）"
                % (len(actual), len(requested))
            ),
        )

    #: ③ 复用既有校验：孔位 + 孔径逐孔
    try:
        from sw_review import validate_hole_positions
    except ImportError:  # 顶层载入
        import sys as _sys
        from pathlib import Path as _Path

        _sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))
        from sw_review import validate_hole_positions

    per_hole = validate_hole_positions(
        v["measured"],
        [dict(h, position_mm=h.get("position_mm") or []) for h in requested],
        position_tolerance_mm=v["position_tol_mm"],
        diameter_tolerance_mm=v["diameter_tol_mm"],
    )
    if per_hole["status"] != "pass":
        bad = [c for c in per_hole["checks"] if not c["passed"]]
        first = bad[0] if bad else {}
        return CheckResult(
            **base,
            status=Status.FAIL,
            observed={"failed": [c["id"] for c in bad][:6], "count": len(bad)},
            expected={"failed": 0},
            reason=(
                "★ %d 个孔的孔径或孔位超差。首例 %r："
                "孔径误差 %r mm、孔位误差 %r mm（容差 %.3f / %.3f）"
                % (
                    len(bad),
                    first.get("id"),
                    first.get("diameter_error_mm"),
                    first.get("position_error_mm"),
                    v["diameter_tol_mm"],
                    v["position_tol_mm"],
                )
            ),
        )

    #: ④ 孔型：B-Rep 给不出 ⇒ unknown（不是 pass）
    if not v["kind_observable"]:
        return CheckResult(
            **base,
            status=Status.UNKNOWN,
            observed={"kind_observable": False, "holes": len(actual)},
            expected={"kind_observable": True},
            reason=(
                "★ 孔径与孔位逐项通过，但 B-Rep **没有给出孔型** ⇒ "
                "「通孔 / 盲孔 / 沉头 / 螺纹」这一项没测到"
                "（`sw_review.validate_hole_positions` 的 docstring 自述该限制）"
            ),
        )

    #: ⑤ 逐个孔的孔型必须匹配
    #:   ⚠ 实测孔**没有 id**（`collect_geometry_measurements` 只给直径/位置/轴线）
    #:   ⇒ 按**孔位就近**配对，不依赖 id。孔位已在 ③ 通过容差校验，
    #:     所以这里的配对是明确的（除非两个孔重合，而那本身是设计错误）。
    def _dist(a, b):
        try:
            return sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)) ** 0.5
        except (TypeError, ValueError):
            return float("inf")

    kind_bad: list = []
    used_actual: set = set()
    for want in requested:
        rid = str(want.get("id", ""))
        want_kind = str(want.get("kind", ""))
        want_pos = want.get("position_mm") or []
        best_i, best_d = None, float("inf")
        for i, cand in enumerate(actual):
            if i in used_actual:
                continue
            d = _dist(want_pos, cand.get("position_mm") or [])
            if d < best_d:
                best_i, best_d = i, d
        if best_i is not None:
            used_actual.add(best_i)
        got_kind = (
            str(actual[best_i].get("kind", "")) if best_i is not None else ""
        )

        if want_kind not in HOLE_TYPES:
            kind_bad.append({"id": rid, "why": "要求里的孔型 %r 不在允许词表" % want_kind})
        elif got_kind != want_kind:
            kind_bad.append(
                {"id": rid, "want": want_kind, "got": got_kind or "(空)"}
            )
    if kind_bad:
        return CheckResult(
            **base,
            status=Status.FAIL,
            observed={"kind_mismatch": kind_bad[:6], "count": len(kind_bad)},
            reason=(
                "★ %d 个孔的**孔型**不符。首例 %r：要求 %r，实测 %r"
                % (
                    len(kind_bad),
                    kind_bad[0].get("id"),
                    kind_bad[0].get("want", kind_bad[0].get("why")),
                    kind_bad[0].get("got"),
                )
            ),
        )

    return CheckResult(
        **base,
        status=Status.PASS,
        observed={"holes": len(actual), "kinds": sorted({str(h.get("kind")) for h in actual})},
        reason="孔数、孔径、孔位、孔型逐项匹配",
    )
