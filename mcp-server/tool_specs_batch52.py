# ── 24h 计划 段 6 续（Spec Kit `173` 的批次声明）：**文档单位** ────────────────────
# ★★★★★ 2026-10-01（轮 339）真机（`output/units-evidence.json`）**PASS 4/4**：
# ★ `GetUnits()` ⇒ **`(0, 1, 8, 2, 0)`** ⇒ `LengthUnit = 0` = **`swMM`** · `is_mm = true
# ` ✓
# ★ 对照源 `ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` ⇒ **0**（系统默
# 认也是毫米）✓
#   ★ `doc_matches_system_default = true` ✓
# ★★ **它补的是「四家有我们没有」核实的**最后一条真缺**** —— ★ 全仓 grep `units` 曾只有
#   `sw_review._unit_vector`（★ 那是"单位**向量**"的数学，★ **不是文档单位**）。
#
# ★★★ **两条路是**不同层次**，不是"同一件事的两个源"**（★ 真机踩到才分清）：
#   · `IModelDoc2.GetUnits()` ⇒ **这一个文档**的单位（★ 官方 Remarks：5 个 short =
#     `[LengthUnit, FractionBase, FractionValue, SignificantDigits, RoundToFraction]`）
# · `ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear)` ⇒ **系统默认**（★ 新建文档
# 的默认）
#   ⇒ ★ **两者**允许不同**** ⇒ ★ 本工具**都报**，★ **不断言必须相等**。
#
# ⚠ **两个坑（★ 都在真机上踩到，★ 都记进 known-facts）**：
#   ① ★ **宿主对象**：★ `IModelDocExtension` 上**没有** `GetUserPreferenceIntegerValue`
#      （★ 我先前在它上面调 ⇒ `0x80020005`「类型不匹配」—— ★ 与事实 36 同形：
#        ★ 同名分属不同族时报"类型不匹配"而不是"方法不存在"）。
# ② ★ **arity**：★ `GetUserPreferenceIntegerValue` 是 **1 参**（★ 官方签名 · 反射三处 ·
# 官方示例**三源一致**）；
# ★ 而 `IModelDocExtension.GetUserPreferenceInteger(UserPref, UserPrefOption)` 才是 **2
# 参** ——
#      ★★ **两个同名前缀、不同 arity 的不同方法** ⇒ ★ 传两个给前者报 `DISP_E_BADPARAMCOUNT`。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch52.py —— 本文件
# 定位:   段 6 续：文档单位（★ 补「四家有我们没有」的最后一条真缺）。
# 官方签名依据: `C:\swapi\types\IModelDoc2\GetUnits.md`（0 参 · ★ Remarks 给了 5 元组格
# 式）·
# `IModelDoc2/SetUnits.md`（5 参）· `C:\swapi\enums\swLengthUnit_e.md`（`swMM=0` 等 11
# 项）·
#   `ISldWorks/GetUserPreferenceIntegerValue.md`（**1 参**）·
#   `C:\swapi\examples\Get_and_Set_User_Preferences_Example_VB.md`（★ 调用形态）·
# ★ 反射 `scripts/sw_api_sldworks.py`（`GetUnits: 0` · `GetUserPreferenceIntegerValue: 1
# `）·
#   ★ `swUnitsLinear = 47` 取自 `D:\AI\SW\_raw\**\enum_values_sldworks.txt`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH52 = [
    ToolSpec(
        name="solidworks_read_document_units",
        title="Read Document Units",
        module="sw_units",
        function="read_units_report",
        inject="model",
        params=[],
        evidence=(
            "★ **读文档单位**（★ 两条路：主源 + 对照源，★ 它们是**不同层次**、**允许不同**）。★ 主源 `IModelDoc2.GetUni"
            "ts()`（**0 参**）—— 官方 Remarks 原话：返回 **5 个 short 的数组** `[LengthUnit, FractionBase, FractionValu"
            "e, SignificantDigits, RoundToFraction]`，`LengthUnit` 取 `swLengthUnit_e`（`swMM = 0`）。★ 对照源 `ISldWor"
            "ks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` —— ★ **1 参**（★ 三源一致：官方签名 / 反射 / 官方示"
            "例），★ 它是**系统默认**（★ 新建文档的默认），**不是**文档级。★★ 判据：**`LengthUnit` 应为 0（`swMM`）** —"
            "— ★ 因为本仓库**建模一律按毫米**；★ 不是 0 就说明该文档单位不是毫米，★ 而那时「我们的 mm 参数」与文档单位"
            "之间存在**未声明的换算**。★ 真机证据（PASS 4/4）：`GetUnits()` ⇒ `(0, 1, 8, 2, 0)` ⇒ `LengthUnit = 0` = `s"
            "wMM` · `is_mm = true`；系统默认也 = 0；`doc_matches_system_default = true`。⚠ **未真机验证**：`SetUnits`（"
            "★ 5 参，★ 本工具只读不写）· 非毫米文档下的读数（★ 本机文档都是毫米）。"
        ),
        doc=(
            "Read the length unit of the active document and compare it with the system default. Read-only; length_unit"
            " should be 0 for millimetres, and any other value means the millimetre arguments used elsewhere in this se"
            "rver sit on an undeclared conversion."
        ),
    ),
]

# ── objective② / 四家缺口 `undo`：**撤销（`IModelDoc2.EditUndo2`）** ──────────────────
# ───
# ★★★★ 2026-10-03（轮 395）真机（`output/undo-evidence.json`）**PASS**：
#   · ★ 前置 `凸台-拉伸1` ⇒ 特征树 **7**；★ 负例 `steps = 0` ⇒ **显式拒绝**
#   · ★★ `undo_report(doc, 1)` ⇒ **特征树 7 → 6** · `undone: true` ·
#     **`removed_features: ["凸台-拉伸1"]`**（★ 指名撤掉了哪个）✓
# ★★ **对应四家缺口名 `undo`**（★ objective② 三层证据判定的真缺 —— 事实 311）。
# ★★ **为什么它对自动化 agent 有用**：★ 我们的工具会**改模型**；★ 改错时**没有撤销就只能
# 重来**。
# ⚠ **调用纪律**：★ `EditUndo2` 撤的是**会话里的动作**、**不区分是不是我们做的** ⇒
#   ★ **只在我们自己的改动之后调用**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch52.py —— 追加本声明
# 定位:   把 `sw_session.undo_report` 挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IModelDoc2\EditUndo2.md`（★ `void EditUndo2(int Steps)`
# ·
#   反射 arity **1**）· `EditUndo`（★ **Obsolete**）· `SketchUndo()`（★ 零参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_UNDO = ToolSpec(
    name="solidworks_undo",
    title="Undo Actions",
    module="sw_session",
    function="undo_report",
    inject="model",
    params=[
        Param(
            "steps",
            int,
            default=1,
            description="Number of actions to undo; it must be at least 1. Defaults to 1.",
        ),
    ],
    evidence=(
        "★ **撤销** —— 走 `IModelDoc2.EditUndo2`（官方 **1 参** · ★★ **返回 `void`**）。★★ 判据（规则 6）：**特征树真的"
        "退回了**（真机：7 → 6 · 撤掉 `凸台-拉伸1`）。★ 负例 `steps = 0` ⇒ 显式拒绝。⚠ **调用纪律**：★ 它撤的是**会话里"
        "的动作**、**不区分是不是我们做的** ⇒ ★ **只在我们自己的改动之后调用**（★ 例如「建完发现参数错 ⇒ 撕掉重来」）。"
    ),
    doc=(
        "Undo model actions in the active document and report the feature tree before and after. It modifies the docume"
        "nt and does not save it; use it only after your own edits, because it undoes whatever happened last in the ses"
        "sion without knowing whose change it was."
    ),
)

SPECS_BATCH52 = SPECS_BATCH52 + [_SPEC_UNDO]
