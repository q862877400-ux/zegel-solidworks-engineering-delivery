# ── 24h 计划 段 6 续（Spec Kit `172` 的批次声明）：**传感器（读）** ────────────────
# ★★★★★ 2026-10-01（轮 338）真机（`output/sensor-evidence.json`）**PASS 3/3**：
# ★ 空零件 / 有几何的零件 / 带外部参考的示例图 —— 三处都 `ok=True` · `count=0` · `errors
# =[]`。
#   ★★ **即：遍历不炸、空路径正确** ⇒ ★ **而那正是这一批能验的那一半**。
#
# ⚠ **如实标注（★ 不写成"全支持"）**：
#   ① ★ **非空路径未验** —— 那三个文档**都没有传感器**。
#      ★ 根因：★ **官方 API 能读不能建**（★ 反射里搜不到 `AddXxxSensor` / `CreateXxxSensor`
#      ⇒ ★ 建传感器是 **UI 功能**）⇒ ★ 要造一个非空场景**只能手工在 UI 里建**。
# ② ★ **单位**：★ `GetSensorValue(out double Value, out string Units)` 的 `Units` 是第二
# 个 out，
#      ★ 本模块先只取原样（★ 非空路径没验到 ⇒ **不声称单位已处理**）。
#
# ★★ **它补的是核实的真缺之三**：★ 全仓 grep `sensor` ⇒ **工具 0 · 函数 0**
# （★ 同批四条真缺：`wrap`（已补 · 187 个工具）· `vertices`（已补）· `sensor`（本条）· `
# units`（未补））。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch51.py —— 本文件
# 定位:   段 6 续：传感器（读）（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\ISensor\`（10 个成员）· `ISensor/GetSensorValue.md`
# （`bool GetSensorValue(out double Value, out string Units)` · ★ 反射 arity 那行是 **0*
# *）·
#   `ISensor/SensorType.md`（属性 get/set）· `ISensor/GetSensorFeatureData.md`（0 参）·
#   `ISensor/SensorAlertState.md`（**只读**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import ToolSpec

SPECS_BATCH51 = [
    ToolSpec(
        name="solidworks_read_sensors",
        title="Read Sensors",
        module="sw_sensor",
        function="read_sensors_report",
        inject="model",
        params=[],
        evidence=(
            "★ **列出文档里的传感器并读它们当前的值** —— 走 `ISensor`（10 个成员）。★ 官方入口现状：★ **能读不能建**（"
            "反射里没有 `AddXxxSensor`）· ★ **也没有「列出所有传感器」的成员** ⇒ ★ 本工具走**特征树遍历 + `GetSpecificF"
            "eature2()`**。★ `GetSensorValue(out double Value, out string Units)` 的官方签名是 **0 参 + 2 个 out**（★ "
            "反射里 `'GetSensorValue': 0` 那行才是 arity）。★ 判据：**函数跑到尾且结构完整** —— ★ 空文档回 `count=0` 且"
            "不炸是对的。★ 真机证据（PASS 3/3）：空零件 / 有几何的零件 / 带外部参考的示例图，三处 `ok=True` · `count=0`"
            " · `errors=[]`。⚠ **未真机验证**：**非空路径**（★ 那三个文档都没有传感器，而官方**不能建** —— 要造非空场景"
            "只能手工在 UI 里建）· 以及 `Units` 那个 out 参数的实际取值。"
        ),
        doc=(
            "List the sensors in the active document and read their current values. Read-only; it walks the feature tre"
            "e because SolidWorks has no member that lists all sensors, and an empty document correctly returns a count"
            " of 0."
        ),
    ),
]
