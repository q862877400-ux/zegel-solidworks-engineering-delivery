

# ── 24h 计划 段 6 续（Spec Kit `167`）：**几何量测（IMeasure）** ──────────────────────
# ★★★★★ 2026-10-01（轮 311）**这一族是"四家有我们没有"里核实的真缺**：
#   ★ 我们有 `part_mass_properties`（**整体**质量属性）· ★ 而**逐几何量测**（两点距离 / 边长度 /
#     面积 / 角度）**一个都没有** —— ★ 全仓 grep `measure` / `volume` / `area` / `distance` **均为 0**。
#   ★ 而四家强候选里正有 `measure` 与 `measure_distance`。
#
# ★★ **调用序来自官方示例**（★ §5.0：判据先找后搓 —— ★ 不自己搓）：
#   `C:\swapi\examples\Measure_Selected_Entities_Example_VB.md`
#   ```
#   ① ext = model.Extension
#   ② ext.SelectByID2("", "FACE", x,y,z, …)      ← 先选中要量的实体
#   ③ m = ext.CreateMeasure
#   ④ m.ArcOption = 0                            （0=中心到中心 · 1=最小距离 · 2=最大距离）
#   ⑤ status = m.Calculate(Nothing)              ← 算
#   ⑥ 读 m.Length / m.Area / …                    ← **-1 表示该项不适用**
#   ```
# ★★★ **官方约定很重要**：★ **每个量回 `-1` 表示"这项对当前选择不适用"** ——
#   ★ 本包装**如实转达**（★ 而不是把 -1 当 0 或 None）✓
#
# ★ 规则 3：★ 不传坐标 —— ★ **量的是"当前已选中的实体"**（★ 与官方示例一致），
#   而"选中"本身由 `sw_selection_spec` 那族工具负责（★ 声明式）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_measure.py —— 本文件（新）
# 定位:   24h 段 6 续：几何量测族（★ 补"四家有我们没有"的真缺）。
# 官方签名依据: `C:\swapi\types\IModelDocExtension\CreateMeasure.md`（`Measure CreateMeasure()`）·
#   `C:\swapi\types\IMeasure\`（33 个成员：`Distance` / `NormalDistance` / `CenterDistance` / `Angle` /
#    `Length` / `TotalLength` / `ArcLength` / `ChordLength` / `Area` / `TotalArea` / `Perimeter` /
#    `Diameter` / `Radius` / `DeltaX` / `DeltaY` / `DeltaZ` / `IsIntersect` / `IsParallel` /
#    `IsPerpendicular` / `Calculate` / `ArcOption` …）+
#   ★ 官方示例 `Measure_Selected_Entities_Example_VB.md`（★ 调用序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

#: ★ **要读的量**（★ 名字 → 官方成员名）—— ★ 只收 `IMeasure` 上**确实存在**的
MEASURE_FIELDS = (
    ("distance", "Distance"),
    ("normal_distance", "NormalDistance"),
    ("center_distance", "CenterDistance"),
    ("angle", "Angle"),
    ("length", "Length"),
    ("total_length", "TotalLength"),
    ("arc_length", "ArcLength"),
    ("chord_length", "ChordLength"),
    ("area", "Area"),
    ("total_area", "TotalArea"),
    ("perimeter", "Perimeter"),
    ("diameter", "Diameter"),
    ("radius", "Radius"),
    ("delta_x", "DeltaX"),
    ("delta_y", "DeltaY"),
    ("delta_z", "DeltaZ"),
)

#: ★ **要读的布尔判定**
MEASURE_FLAGS = (
    ("is_intersect", "IsIntersect"),
    ("is_parallel", "IsParallel"),
    ("is_perpendicular", "IsPerpendicular"),
)


def measure_selection_report(model, arc_option: int = 1) -> dict:
    """★ **量当前选中的实体**（★ 走 `IModelDocExtension.CreateMeasure` → `IMeasure`）。

    ★ 调用序**照官方示例**：★ `Extension` → `CreateMeasure` → 设 `ArcOption` → `Calculate(Nothing)` → 读。

    ★ `arc_option`：★ **0 = 中心到中心 · 1 = 最小距离 · 2 = 最大距离**（★ 官方示例的原话）。
    ★★ **读数约定**：★ **`-1` 表示"这一项对当前选择不适用"** —— ★ 本函数**如实保留 `-1`**，
      ★ 并另给 `applicable` 列表（★ 哪些项真的量到了）。
    ★ 判据（★ 规则 6）：★ **`Calculate` 回真** 且 ★ **至少有一项不等于 -1**
      （★ 否则说明"没选中东西"或"选的东西量不出"）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        opt = int(arc_option)
    except (TypeError, ValueError):
        return {"ok": False, "error": "arc_option 必须是整数（0=中心到中心 · 1=最小距离 · 2=最大距离）"}
    if opt not in (0, 1, 2):
        return {"ok": False, "stage": "validate",
                "error": "arc_option 只能是 **0 / 1 / 2**（★ 官方示例给的语义）；收到 %r" % arc_option}
    from sw_connect import get_com_member as _get
    #: ★ ① 选中了几何？★ 回读计数（★ 事实 8：不信返回值）
    try:
        sel_n = int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1))
    except Exception:                                          # noqa: BLE001
        sel_n = -1
    if sel_n == 0:
        return {"ok": False, "stage": "selection", "selected_count": sel_n,
                "error": "没有选中的实体 —— ★ 量测要先选中（★ 用声明式选择那族工具），★ 规则 3"}
    #: ★ ② 官方调用序
    try:
        ext = _get(model, "Extension")
        m = _get(ext, "CreateMeasure")
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "create", "selected_count": sel_n,
                "error": "CreateMeasure 失败：%s: %s" % (type(exc).__name__, str(exc)[:180])}
    if m is None:
        return {"ok": False, "stage": "create", "selected_count": sel_n,
                "error": "CreateMeasure 回了 None（★ 本机不可用？）"}
    geometry = {"arc_option": opt}
    try:
        from sw_connect import set_com_member as _set
        _set(m, "ArcOption", opt)
        geometry["arc_option_set"] = True
    except Exception as exc:                                   # noqa: BLE001
        geometry["arc_option_set"] = False
        geometry["arc_option_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
    try:
        #: ★★★ 2026-10-01（轮 311）**真机：`Calculate` 必须无参调**（★ 事实 227）——
        #:   官方示例写 `Calculate(Nothing)`，而 `get_com_member` 的语义是「取或调」：
        #:   传了实参 ⇒ 它**先无参调一次**（回 `True`）、★ 再拿那个 `True` 去"调用"
        #:   ⇒ `TypeError: 'bool' object is not callable`。★ 改成无参即回 `True` ✓
        ok_calc = _get(m, "Calculate")
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "calculate", "selected_count": sel_n, "geometry": geometry,
                "error": "Calculate 失败：%s: %s" % (type(exc).__name__, str(exc)[:180])}
    values, applicable = {}, []
    for label, member in MEASURE_FIELDS:
        try:
            v = _get(m, member)
        except Exception:                                      # noqa: BLE001
            continue
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        values[label] = fv
        if fv != -1.0:
            applicable.append(label)
    flags = {}
    for label, member in MEASURE_FLAGS:
        try:
            flags[label] = bool(_get(m, member))
        except Exception:                                      # noqa: BLE001
            continue
    return {"ok": bool(ok_calc) and bool(applicable), "calculate_returned": bool(ok_calc),
            "selected_count": sel_n, "values": values, "applicable": applicable, "flags": flags,
            "geometry": geometry,
            "★": "★ `-1` = 该项对当前选择**不适用**（★ 官方约定，如实保留）；"
                 "★ `applicable` 列出真量到的项；★ 调用序照官方示例（Extension→CreateMeasure→ArcOption→Calculate）"}
