

# ── 24h 计划 段 5 续（Spec Kit `157`）：**显式形参的验证包装** ─────────────────────
# ★★★★ 为什么包一层：★ 底层 `validate_motion_studies(asm_model, **requirements)`
#   用 `**requirements` ⇒ ★ **`check_param_binding.py` 无法把工具层的声明名对上形参**
#   （★ 与轮 272 的 `configure_*_solver` **同一次教训**）⇒ ★★ **正解：显式形参** ——
#   ★ 而**显式更好**：★ **形参即文档**（★ 调用方一眼看到能传什么）。
#
# ★ 判据：★ **不吞错**（★ 底层怎么报就怎么回）· ★ 并把 **`requirements` 里实际传了哪些**记进返回。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_motion.py —— 本段
# 定位:   段 5 续：把 `validate_motion_studies` 的 `**requirements` 变成**显式形参**。
# 官方依据: `IMotionStudyManager`（★ 见 `scripts/sw_motion.py` 的既有来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 1 个包装
# ─────────────────────────────────────────────────────────────────────────────


def validate_motion_studies_report(asm_model, study_name=None, expected_study_type=None,
                                   minimum_duration_seconds=None, minimum_motor_count=None,
                                   require_results=None):
    """★ **显式形参版的 `validate_motion_studies`**（★ 只传非 None 的那些）。

    ★ 返回里带上 **`asked`**（实际传下去的键）⇒ ★ 于是"我到底验了什么"可从结果里读出来。
    """
    req = {}
    for k, v in (("study_name", study_name),
                 ("expected_study_type", expected_study_type),
                 ("minimum_duration_seconds", minimum_duration_seconds),
                 ("minimum_motor_count", minimum_motor_count),
                 ("require_results", require_results)):
        if v is not None:
            req[k] = v
    try:
        r = validate_motion_studies(asm_model, **req)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "asked": sorted(req),
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    return {"ok": True, "asked": sorted(req), "returned": r}
