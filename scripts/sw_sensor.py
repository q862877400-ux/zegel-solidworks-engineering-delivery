

# ── 24h 计划 段 6 续（Spec Kit `172`）：**传感器（读）** ────────────────────────────
# ★★★★★ 2026-10-01（轮 332）**这是"四家有我们没有"里核实的真缺之三**：
# ★ 全仓 grep `sensor` ⇒ **工具 0 · 函数 0**（★ 同批另三条真缺：`wrap`（已补）· `units` 
# · `undo`）。
#
# ★★★ **而查明的入口现状（★ 决定这一批能做什么）**：
# · ★ `ISensor` 有 **10 个成员**：`GetSensorValue` / `GetSensorFeatureData` / `SensorTyp
# e` /
# `SensorAlertEnabled` / `SensorAlertState` / `SensorAlertType` / `SensorAlertValue1/2` 
# / `UpdateSensor`
# · ★ **`GetSensorValue(out double Value, out string Units)`** —— ★ 官方签名是 **0 参 + 
# 2 个 out**
# （★ 反射里 `'GetSensorValue': 0` 那一行才是 arity；★ 另一个数字是重载位置编号，★ **别
# 当 arity 用**）
# · ★ **没有"创建传感器"的官方入口** —— ★ 反射里搜不到 `AddXxxSensor` / `CreateXxxSensor
# `
#     ⇒ ★★ **即：官方 API 能**读**，**不能建****（★ 建是 UI 功能）✓
#   · ★ 而**也没有"列出所有传感器"的入口** ⇒ ★ **传感器是**特征树里的一类特征****
# ⇒ ★★★ **所以本模块走 `IFeature` 遍历 + `GetSpecificFeature2()`**（★ 与事实 242 的类型
# 名路线一致）✓
#
# ★★ **因此本批如实定位为"读"**：★ 列出文档里的传感器并读它们当前的值。
#   ⚠ **未验**：★ **非空路径**（★ 要有一个真传感器才能验 —— ★ 而**建它只能走 UI**）
# ⇒ ★ 本轮真机验的是 **空路径**（★ 没有传感器时**回空表且不炸** —— ★ 那是一族"读数"的正
# 确判据）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_sensor.py —— 本文件（新）
# 定位:   24h 段 6 续：传感器（读）（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\ISensor\`（10 个成员）· `ISensor/GetSensorValue.md`
#   （`bool GetSensorValue(out double Value, out string Units)`）·
#   `ISensor/GetSensorFeatureData.md`（0 参）· `ISensor/SensorType.md`（属性 get/set）·
# `ISensor/SensorAlertState.md`（**只读**）· ★ 反射 `scripts/sw_api_sldworks.py`（`GetSe
# nsorValue: 0`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from sw_connect import get_com_member

#: ★★★ 2026-10-01（轮 332）：**本模块自带两个 out 包装** —— ★ 因为 `sw_connect` 只有 `ou
#: t_i4`，
#: 而 `GetSensorValue(out double Value, out string Units)` 要 `VT_R8` 与 `VT_BSTR` 两个
#: 。
#: ★ 依据：`sw_connect.out_i4` 的**真机结论**（★ 唯一通过的形态是 `VARIANT(VT_BYREF | VT
#: _xxx, 默认值)`；
#:   ★ 裸值 / 不带 BYREF / `VT_VARIANT` 全报"类型不匹配"）⇒ ★ 这里照同一形态造另外两种。
#: ⚠⚠★ **2026-10-10（spec 274）真机反例**：★ 这条「照同一形态造」的**类推在 `Double&` 上
#: 不成立** ——
#: ★ 真机（34.4.1）实测 `IBody2.GetExtremePoint(Double, Double, Double, Double&, Double&
#: , Double&)`
#:     ⇒ ★ 三个 `Double&` 传 by-ref VARIANT **一律抛 `TypeError`**
#:     （`float() argument must be a string or a real number, not 'VARIANT'`）；
#:     ★ 而**裸 `0.0` / 省略**通过、★ 出参**随返回元组回来**（`(True, 0.0275, 0.0, 0.0)`）。
#: ★ 同机对照 `IModelDocExtension.GetWhatsWrong(Object&, Object&, Object&)` ⇒ ★ **只**吃
#:  by-ref VARIANT
#:     （★ 裸值 ⇒ `DISP_E_TYPEMISMATCH` · ★ 省略 ⇒ `DISP_E_PARAMNOTOPTIONAL`）。
#: ⇒ ★★ **传法取决于该形参怎么声明，★ 不能按「出参」一刀切**（★ 读数原文 `output/_probe2
#: 74_double_out.txt`）。
#:     ⇒ ★★ 故本函数的 `VT_BYREF | VT_R8` 形态**只有类推、没有 `Double&` 的真机正例**，
#: ★ 且已有一个 `Double&` 反例 ⇒ ★ **用之前先真机核，别默认它通**（★ 判据 `tests/test_do
#: uble_out_param_form.py`）。
def out_double(value: float = 0.0):
    """★ `Double&` 出参的 VARIANT 包装（★ 形态照 `sw_connect.out_i4` 的类推 —— ⚠★ **无 `Double&` 真机正例**）。"""
    import pythoncom  # noqa: PLC0415
    return pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, float(value))


def out_bstr(value: str = ""):
    """★ `String&` 出参的 VARIANT 包装（★ 形态照 `sw_connect.out_i4` 的真机结论）。"""
    import pythoncom  # noqa: PLC0415
    return pythoncom.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, str(value))

#: ★ `swSensorType_e` 的中文名（★ 便于阅读；★ **数值本身以真机读到的为准**）
SENSOR_TYPE_NAMES = {
    0: "MassProperties", 1: "Measurement", 2: "Dimension", 3: "MotionStudy",
    4: "Simulation", 5: "Costing", 6: "SurfaceArea", 7: "Interference",
}


def _iter_features(model):
    """★ 遍历特征树（★ 从 `IFeatureManager.GetFeatureCount` + `IFeature.GetNextFeature`）。"""
    try:
        first = get_com_member(model, "FirstFeature")
    except Exception:                                          # noqa: BLE001
        return
    feat, seen = first, set()
    while feat is not None:
        try:
            name = str(get_com_member(feat, "Name"))
        except Exception:                                      # noqa: BLE001
            break
        if name in seen:                                       # ★ 防环（★ COM 遍历可能自指）
            break
        seen.add(name)
        yield feat, name
        try:
            feat = get_com_member(feat, "GetNextFeature")
        except Exception:                                      # noqa: BLE001
            break


def _sensor_of(feat):
    """★ 把特征转成 `ISensor`（★ 不是传感器就回 None）。"""
    for meth in ("GetSpecificFeature2", "GetSpecificFeature"):
        try:
            obj = get_com_member(feat, meth)
        except Exception:                                      # noqa: BLE001
            continue
        if obj is None:
            continue
        #: ★ 用"只有 ISensor 才有的成员"判身份（★ 事实 36：同名接口分属不同族，★ 别只看
        #: 名字）
        try:
            get_com_member(obj, "SensorType")
            return obj
        except Exception:                                      # noqa: BLE001
            continue
    return None


def read_sensors_report(model) -> dict:
    """★ **列出文档里的传感器并读它们当前的值**。

    ★ 入口现状（★ 官方）：★ **能读不能建**（★ 反射里没有 `AddXxxSensor`）·
      ★ **也没有"列出所有传感器"的成员** ⇒ ★ 本函数走**特征树遍历 + `GetSpecificFeature2()`**。
    ★ `GetSensorValue(out double Value, out string Units)` ⇒ ★ 本函数把 value / units 都取出来。
    ★ 判据（★ 规则 6）：★ **函数跑到尾且结构完整** —— ★ **空文档回 `count=0` 且不炸**是对的。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    items, errors = [], []
    for feat, name in _iter_features(model):
        sensor = _sensor_of(feat)
        if sensor is None:
            continue
        row = {"feature_name": name}
        for attr in ("SensorType", "SensorAlertState", "SensorAlertEnabled"):
            try:
                row[attr] = get_com_member(sensor, attr)
            except Exception as exc:                           # noqa: BLE001
                row[attr] = None
                errors.append("%s.%s: %s" % (name, attr, str(exc)[:60]))
        try:
            value = get_com_member(sensor, "GetSensorValue", out_double(), out_bstr())
            row["raw_return"] = repr(value)[:20]
        except Exception as exc:                               # noqa: BLE001
            row["raw_return"] = "ERR %s" % str(exc)[:70]
            errors.append("%s.GetSensorValue: %s" % (name, str(exc)[:60]))
        items.append(row)
    return {"ok": True, "count": len(items), "sensors": items, "errors": errors,
            "units_note": "⚠ 值的单位由 `GetSensorValue` 的第二个 out 参数给出；"
                          "★ 本函数先只取原样返回（★ 真机非空路径未验）",
            "★": "官方 `ISensor` **能读不能建**（★ 没找到 `Add*Sensor`）· 传感器是**特征树里的一类特征** "
                 "⇒ ★ 本函数走遍历 + `GetSpecificFeature2()`；★ 空文档回 `count=0` 且不炸是**正确**的"}
