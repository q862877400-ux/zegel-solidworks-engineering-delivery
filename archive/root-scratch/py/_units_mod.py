

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
    pref = None
    try:
        ext = get_com_member(model, "Extension")
        #: ★ `swUserPreferenceIntegerValue_e.swUnitsLinear` 的数值 ⇒ ★ 真机核（见证据）
        for code in (48, 47, 49):
            try:
                pref = get_com_member(ext, "GetUserPreferenceInteger", code, "")
                if pref is not None:
                    out["pref_linear_code"] = code
                    break
            except Exception:                                  # noqa: BLE001
                continue
    except Exception as exc:                                   # noqa: BLE001
        out["pref_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
    out["pref_linear"] = pref
    if pref is not None and seq:
        out["sources_agree"] = (int(pref) == int(seq[0]))
    out["★"] = ("★ 双源：`IModelDoc2.GetUnits()`（0 参 · 官方 Remarks：5 个 short = "
                "[LengthUnit, FractionBase, FractionValue, SignificantDigits, RoundToFraction]）"
                "× 用户偏好 `swUnitsLinear`；★ 期望 `LengthUnit == 0`（`swMM`）—— "
                "★ 因为本仓库建模一律按毫米")
    return out
