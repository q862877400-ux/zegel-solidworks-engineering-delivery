

# ── 24h 计划 段 6 续（Spec Kit `173`）：**文档单位** ────────────────────────────────
# ★★★★★ 2026-10-01（轮 339）**这是"四家有我们没有"里核实的真缺之四（最后一条）**：
#   ★ 全仓 grep `units` ⇒ ★ **工具 0**（★ 唯一的命中是 `sw_review._unit_vector` ——
#     ★ 那是"单位**向量**"的数学，★ **不是文档单位**）。
#
# ★★★ **两条独立入口（★ 本模块**双源互证**）**：
# ```
# ① IModelDoc2.GetUnits()  —— **0 参**，回 `System.object`
#    官方 Remarks 原话：★ 返回的是 **5 个 short 的数组** ——
#      `[ LengthUnit, FractionBase, FractionValue, SignificantDigits, RoundToFraction ]`
#    · LengthUnit ⇒ `swLengthUnit_e`（★ `swMM = 0` · `swCM = 1` · `swMETER = 2` · `swINCHES = 3` · …）
# ② IModelDoc2.Extension.GetUserPreferenceInteger(swUserPreferenceIntegerValue_e.swUnitsLinear, "")
#    —— ★ 同一件事的**用户偏好**读法。
# ⇒ ★★ **两个入口给同一个答案才算坐实**（★ 本仓库"签名三源互证"的同精神）。
# ```
#
# ★★★ **期望值（★ 用本仓库的约定推出，不是"看着像对"）**：
#   ★ 本仓库**建模一律按毫米**（★ `_mm` 命名约定 · 所有几何参数都是 mm）⇒
#   ★★ **`LengthUnit` 应当 = 0（`swMM`）** ⇒ ★ 那是一个**可证伪的期望** ✓
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_units.py —— 本文件（新）
# 定位:   24h 段 6 续：文档单位（★ 补「四家有我们没有」的最后一条真缺）。
# 官方签名依据: `C:\swapi\types\IModelDoc2\GetUnits.md`（0 参 · ★ Remarks 给了 5 元组格式）·
#   `IModelDoc2/SetUnits.md`（5 参）· `C:\swapi\enums\swLengthUnit_e.md`（`swMM=0` 等 11 项）·
#   `C:\swapi\enums\swUserPreferenceIntegerValue_e.md`（`swUnitsLinear` 等）·
#   ★ 反射 `scripts/sw_api_sldworks.py`（`GetUnits: 0` · `SetUnits: 5`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from sw_connect import get_com_member

#: ★ `swLengthUnit_e`（★ 官方枚举文本给的名字与数值；★ 数值以官方类型表为准）
LENGTH_UNIT_NAMES = {
    0: "swMM", 1: "swCM", 2: "swMETER", 3: "swINCHES", 4: "swFEET", 5: "swFEETINCHES",
    6: "swANGSTROM", 7: "swNANOMETER", 8: "swMICRON", 9: "swMIL", 10: "swUIN",
}

#: ★ 官方 Remarks 给的 5 元组字段名（★ 顺序就是数组顺序）
UNIT_TUPLE_FIELDS = ("LengthUnit", "FractionBase", "FractionValue",
                     "SignificantDigits", "RoundToFraction")


def _flatten_units(raw):
    """★ 把 `GetUnits()` 的返回值摊成 5 个 short（★ 形态可能是 tuple/list/嵌套）。"""
    if raw is None:
        return None
    seq = list(raw) if isinstance(raw, (list, tuple)) else [raw]
    #: ★ 迟到绑定下有时会回 `((a,b,c,d,e),)` 这种嵌套
    if len(seq) == 1 and isinstance(seq[0], (list, tuple)):
        seq = list(seq[0])
    return [int(x) for x in seq]


def read_units_report(model) -> dict:
    """★ **读文档单位**（★ 双源：`GetUnits()` + 用户偏好 `swUnitsLinear`）。

    ★ 判据（★ 规则 6 + 本仓库约定）：★ **`LengthUnit` 应为 0（`swMM`）** ——
      ★ 因为本仓库**建模一律按毫米**（★ `_mm` 命名约定）；★ **不是 0 就说明该文档单位不是毫米**，
      ★ 而那时"我们的 mm 参数"与文档单位之间就存在**未声明的换算**（★ 那正是要暴露的事）。
    ★ 回 `{"ok", "length_unit", "length_unit_name", "is_mm", "tuple", "pref_linear", "sources_agree"}`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    out = {"ok": True}
    raw = None
    try:
        raw = get_com_member(model, "GetUnits")
    except Exception as exc:                                   # noqa: BLE001
        out["ok"] = False
        out["units_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    seq = _flatten_units(raw)
    out["raw"] = repr(raw)[:80]
    out["tuple"] = seq
    if seq:
        out["tuple_named"] = dict(zip(UNIT_TUPLE_FIELDS, seq))
        out["length_unit"] = seq[0]
        out["length_unit_name"] = LENGTH_UNIT_NAMES.get(seq[0], "?")
        out["is_mm"] = (seq[0] == 0)
    #: ★★ 第二源：用户偏好 `swUnitsLinear`（★ 与上面应给同一答案）
    #: ★★★ 2026-10-01（轮 339）**对照源在 `ISldWorks` 上，不在 `IModelDocExtension` 上** ——
    #:   真机踩到：★ 我先试 `Extension.GetUserPreferenceInteger(47, "")` ⇒ 四个 code 全报
    #:   `(-2147352571, '类型不匹配')`（`0x80020005`）⇒ ★★ **那不是「code 猜错了」**
    #:   （★ 反射里 `swUnitsLinear = **47**` 正是我试的第一个），★ 而是**宿主对象不对**：
    #:   官方示例 `Get_and_Set_User_Preferences_Example_VB.md` 里**全是**
    #:   `swApp.GetUserPreferenceIntegerValue(...)` —— ★ **在 `ISldWorks` 上** ✓
    #:   ⇒ ★ 与事实 36 同形（★ 同名分属不同族 ⇒ 报「类型不匹配」而非「方法不存在」）。
    #: ★★ **而两条路是**不同层次**，不是「同一件事的两个源」**：
    #:   · `IModelDoc2.GetUnits()` ⇒ **这一个文档**的单位（★ 可被文档属性覆盖）
    #:   · `ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` ⇒ **系统默认**（★ 新建文档的默认）
    #:   ⇒ ★★★ **所以它们**允许不同**** —— ★ 本函数把两者都报出来，★ **而不是断言「必须相等」**。
    pref, pref_sys = None, None
    try:
        ext = get_com_member(model, "Extension")
        for code in (47,):
            try:
                pref = get_com_member(ext, "GetUserPreferenceInteger", code, "")
                if pref is not None:
                    out["pref_linear_via"] = "IModelDocExtension"
                    break
            except Exception:                                  # noqa: BLE001
                pref = None
    except Exception:                                          # noqa: BLE001
        pref = None
    try:
        app = None
        for getter in ("GetSldWorks", "IGetSldWorks"):
            try:
                #: dispatch-arg: probe 试名探测：`GetSldWorks`/`IGetSldWorks` 两源均查不到，按序试
                app = get_com_member(model, getter)
                if app is not None:
                    break
            except Exception:                                  # noqa: BLE001
                continue
        if app is None:
            #: ★ 兜底：★ `IModelDoc2.GetSldWorks` 在迟到绑定下拿不到 ⇒ 直接连正在跑的那个实例。
            #:   ★ 本仓库是**单源运行**（事实 24：多个进程抢同一 COM 连接会死锁）
            #:   ⇒ ★ `Dispatch("SldWorks.Application")` 拿到的是**同一个**实例，安全。
            try:
                import win32com.client as _w                              # noqa: PLC0415
                app = _w.Dispatch("SldWorks.Application")
                out["app_via"] = "Dispatch"
            except Exception as exc:                                      # noqa: BLE001
                out["app_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
        else:
            out["app_via"] = "IModelDoc2.GetSldWorks"
        if app is not None:
            #: ★★★★★ 2026-10-01（轮 339）**arity = 1，不是 2** —— 三源一致：
            #:   · 官方签名 `System.int GetUserPreferenceIntegerValue( System.int UserPreferenceValue )`
            #:   · 反射 `'GetUserPreferenceIntegerValue': 1`（★ 三处都是 1）
            #:   · 官方示例 `swApp.GetUserPreferenceIntegerValue(swUserPreferenceIntegerValue_e.swViewRotationMouseSpeed)`
            #:   ⇒ ★★ 我先前传 `(47, "")` 两个 ⇒ `DISP_E_BADPARAMCOUNT`（`0x8002000E`「无效的参数数目」）。
            #:   ⚠ **别与 `IModelDocExtension.GetUserPreferenceInteger(UserPref, UserPrefOption)` 混** ——
            #:     ★ 那是**另一个方法**（2 参、另一个宿主）⇒ ★ 两个同名前缀、不同 arity。
            pref_sys = get_com_member(app, "GetUserPreferenceIntegerValue", 47)
            if pref_sys is not None and pref is None:
                out["pref_linear_via"] = "ISldWorks"
                pref = pref_sys
    except Exception as exc:                                   # noqa: BLE001
        out["pref_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    out["pref_linear"] = pref
    out["pref_linear_system_default"] = pref_sys
    #: ★ 注意：这是**文档级**与**系统默认**的关系，**不是**两个源互证 ⇒ 允许不同。
    if pref_sys is not None and seq:
        out["doc_matches_system_default"] = (int(pref_sys) == int(seq[0]))
    out["★"] = ("★ 主源：`IModelDoc2.GetUnits()`（0 参 · 官方 Remarks：5 个 short = "
                "[LengthUnit, FractionBase, FractionValue, SignificantDigits, RoundToFraction]）；"
                "★ 对照源：`ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` —— "
                "★ **系统默认**（★ 与文档级**允许不同**，★ **不是互证**）；"
                "★ 期望 `LengthUnit == 0`（`swMM`）—— ★ 因为本仓库建模一律按毫米")
    return out
