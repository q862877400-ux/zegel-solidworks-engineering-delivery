

# ── 24h 计划 段 2.1（Spec Kit `143`）：**四类常用载荷的「回读报告」包装** ──────────
# ★★★ 为什么四个都要包（与 `sw_simulation` 的 `create_mesh_report` 同一理由）：
#   `add_pressure` / `add_torque` / `add_gravity` / `add_centrifugal_force` **都回 COM 对象**
#   （`_check(...)` 直接回 `get_com_member(manager, member, *args)`）
#   ⇒ ★ **MCP 回不了对象** ⇒ 必须翻成**可 JSON 化**的东西。
# ★★ 判据用**既有脚本那条**（`tools/capture_simulation_loads_evidence.py`）：
#   「夹具/载荷 | 选区计数 = 1 **且** `LoadsAndRestraintsManager.Count` 增加」
#   ⇒ 本组函数一律**回读 `Count` 的前后差**，★ **不看返回对象**（★ 铁律：回读优先）。


def _loads_count(manager) -> int:
    """回读载荷条数（`ICWLoadsAndRestraintsManager.Count`）。★ 取不到回 -1（**不静默成 0**）。"""
    try:
        v = get_com_member(manager, "Count")
        return int(v) if v is not None else -1
    except Exception:                                          # noqa: BLE001
        return -1


def _report(manager, fn, label: str):
    """★ 通用：**施加载荷 → 回读 Count 前后差** → 组装回读报告。

    `fn` 是「真正施加载荷」的零参可调用（★ 它在 `try` 里跑 ⇒ 异常**序列化回调用方**，不吞）。
    """
    before = _loads_count(manager)
    obj = None
    err = None
    try:
        obj = fn()
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    after = _loads_count(manager)
    return {
        "ok": err is None and after == before + 1,
        "load": label,
        "count_before": before,
        "count_after": after,
        "created_object": type(obj).__name__ if obj is not None else None,
        "error": err,
        "★": "ok 判的是 count_after == count_before + 1（★ 回读优先，不看返回对象）",
    }


def apply_pressure_report(manager, entities, pressure_type: int = 0, reg_geom=None):
    """**加压力**并回**回读报告**（★ 参数同 `add_pressure`，只是不再回 COM 对象）。"""
    return _report(manager, lambda: add_pressure(manager, entities, pressure_type, reg_geom),
                   "pressure")


def apply_torque_report(manager, entities, ref_geom=None):
    """**加力矩**并回**回读报告**。"""
    return _report(manager, lambda: add_torque(manager, entities, ref_geom), "torque")


def apply_gravity_report(manager, entity):
    """**加重力**并回**回读报告**（★ `entity` 是**单**实体）。"""
    return _report(manager, lambda: add_gravity(manager, entity), "gravity")


def apply_centrifugal_force_report(manager, entity):
    """**加离心力**并回**回读报告**（★ `entity` 是**单**实体）。"""
    return _report(manager, lambda: add_centrifugal_force(manager, entity), "centrifugal_force")
