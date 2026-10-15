

# ── 24h 计划 段 2.2（Spec Kit `144`）：**拓扑柜台的读数/参数 4 个回读报告** ──────────
# ★★★ 为什么这四个要包：
#   上面 10 个拓扑工具已挂（create_* / run / evidence），但**读数与参数**这一组从未上柜：
#     · `get_topology_study_manager`        ⇒ 回 **COM 对象**
#     · `get_topology_study_options`        ⇒ 回 **COM 对象**
#     · `set_topology_goal`                 ⇒ 回 **COM 对象**（★ 而它是"设置"⇒ 要**回读确认**）
#     · `set_topology_iteration_options`    ⇒ 回 **COM 对象**
#   ⇒ ★ MCP 回不了对象 ⇒ 必须翻成**可 JSON 化**的回读报告。
# ★★ 判据（★ 按 §5.0：**先找自家仓库**）：
#   · 取到了几个 kind ⇒ 用 `list_topology_constraints_and_controls`（★ **本模块自己的读取入口**）
#     —— ★ 而它的注释里记着一条教训：曾因裸传 `0` 当出参而**永远返回全 None（假通过）**，
#       改用 `out_i4()` 后才是真的。⇒ 本组一律**只回"哪个 kind 非 None"**（布尔，可 JSON 化）。
#   · `collect_topology_numbers` 的 `material_mass_plot` 是**既有证据脚本**的核心判据
#     （`tools/capture_topology_evidence.py`：「`GetPlotNames` 里出现 `材料质量*`」）——
#     ★ 本组**不重复**造它，直接复用那个函数。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_topology.py —— 本段
# 定位:   拓扑研究的**读数与参数**回读报告（24h 段 2.2）。
# 官方依据: `ICWTopologyStudyManager` / `ICWTopologyStudyOptions` 的官方成员
#          （见本模块上方各来源块；官方例 `Create_Topology_Study_Example_VBA.txt`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本段整体
# ─────────────────────────────────────────────────────────────────────────────


def _kinds_taken(study) -> dict[str, bool]:
    """★ **回读**：该研究上「哪些约束/控制**真的取到了**」（★ JSON 可化）。

    ★ 不把 COM 对象本身回出去 —— 只回**布尔**（★ 这也让"取到了"这件事**可断言**）。
    """
    raw = list_topology_constraints_and_controls(study)
    return {k: (v is not None) for k, v in raw.items() if not k.endswith("__error")}


def _kinds_summary(study) -> dict[str, Any]:
    """回读摘要（★ 计数 + 明细 + 出错项）—— 供 setter 做**前后对照**。"""
    raw = list_topology_constraints_and_controls(study)
    kinds = {k: (v is not None) for k, v in raw.items() if not k.endswith("__error")}
    errors = {k: v for k, v in raw.items() if k.endswith("__error") and v}
    return {"kinds": kinds, "taken_count": sum(1 for v in kinds.values() if v),
            "total": len(kinds), "errors": errors}


def topology_manager_report(study) -> dict[str, Any]:
    """★ 回**管理器**的**可 JSON 化**报告（★ 不回 COM 对象）。"""
    mgr = get_topology_study_manager(study)
    return {
        "ok": mgr is not None,
        "object_type": type(mgr).__name__ if mgr is not None else None,
        "study_name": str(get_com_member(study, "Name") or ""),
        **({"kinds": _kinds_taken(study)} if mgr is not None else {}),
        "★": "ok 判的是管理器对象非 None（★ 回读优先，不靠异常）",
    }


def topology_options_report(study) -> dict[str, Any]:
    """★ 回**研究选项**的**可 JSON 化**报告（★ 不回 COM 对象）。"""
    opt = get_topology_study_options(study)
    out: dict[str, Any] = {
        "ok": opt is not None,
        "object_type": type(opt).__name__ if opt is not None else None,
        "study_name": str(get_com_member(study, "Name") or ""),
        "★": "ok 判的是选项对象非 None；★ 具体选项值由 set_*_report 的前后对照体现",
    }
    return out


def set_topology_goal_report(study, *, goal_type: int = 0,
                             mass_reduce_percent: float = 0.0) -> dict[str, Any]:
    """★ 设**拓扑目标**并回**回读报告**（★ 前后对照「取到了几个 kind」）。"""
    before = _kinds_summary(study)
    err = None
    try:
        set_topology_goal(study, goal_type=goal_type, mass_reduce_percent=mass_reduce_percent)
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _kinds_summary(study)
    return {
        "ok": err is None and after["taken_count"] >= before["taken_count"],
        "before": before, "after": after, "error": err,
        "★": "ok 判的是「无异常 **且** 取到的 kind 数不减少」（★ 回读，不看返回对象）",
    }


def set_topology_iteration_options_report(study, *, iteration_option: int | None = None,
                                          iteration_count: int | None = None) -> dict[str, Any]:
    """★ 设**迭代选项**并回**回读报告**（★ 前后对照）。"""
    before = _kinds_summary(study)
    err = None
    try:
        set_topology_iteration_options(study, iteration_option=iteration_option,
                                       iteration_count=iteration_count)
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _kinds_summary(study)
    return {
        "ok": err is None and after["taken_count"] >= before["taken_count"],
        "before": before, "after": after, "error": err,
        "★": "ok 判的是「无异常 **且** 取到的 kind 数不减少」（★ 回读，不看返回对象）",
    }
