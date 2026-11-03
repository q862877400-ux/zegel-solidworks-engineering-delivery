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
# · LengthUnit ⇒ `swLengthUnit_e`（★ `swMM = 0` · `swCM = 1` · `swMETER = 2` · `swINCHES
#  = 3` · …）
# ② IModelDoc2.Extension.GetUserPreferenceInteger(swUserPreferenceIntegerValue_e.swUnits
# Linear, "")
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
# 官方签名依据: `C:\swapi\types\IModelDoc2\GetUnits.md`（0 参 · ★ Remarks 给了 5 元组格
# 式）·
# `IModelDoc2/SetUnits.md`（5 参）· `C:\swapi\enums\swLengthUnit_e.md`（`swMM=0` 等 11
# 项）·
#   `C:\swapi\enums\swUserPreferenceIntegerValue_e.md`（`swUnitsLinear` 等）·
#   ★ 反射 `scripts/sw_api_sldworks.py`（`GetUnits: 0` · `SetUnits: 5`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

import math

from sw_connect import get_com_member

#: ★ `swLengthUnit_e`（★ 官方枚举文本给的名字与数值；★ 数值以官方类型表为准）
LENGTH_UNIT_NAMES = {
    0: "swMM",
    1: "swCM",
    2: "swMETER",
    3: "swINCHES",
    4: "swFEET",
    5: "swFEETINCHES",
    6: "swANGSTROM",
    7: "swNANOMETER",
    8: "swMICRON",
    9: "swMIL",
    10: "swUIN",
}

#: ★ 官方 Remarks 给的 5 元组字段名（★ 顺序就是数组顺序）
UNIT_TUPLE_FIELDS = (
    "LengthUnit",
    "FractionBase",
    "FractionValue",
    "SignificantDigits",
    "RoundToFraction",
)


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
    except Exception as exc:  # noqa: BLE001
        out["ok"] = False
        out["units_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    seq = _flatten_units(raw)
    out["raw"] = repr(raw)[:80]
    out["tuple"] = seq
    if seq:
        out["tuple_named"] = dict(zip(UNIT_TUPLE_FIELDS, seq))
        out["length_unit"] = seq[0]
        out["length_unit_name"] = LENGTH_UNIT_NAMES.get(seq[0], "?")
        out["is_mm"] = seq[0] == 0
    #: ★★ 第二源：用户偏好 `swUnitsLinear`（★ 与上面应给同一答案）
    #: ★★★ 2026-10-01（轮 339）**对照源在 `ISldWorks` 上，不在 `IModelDocExtension` 上**
    #:  ——
    #:   真机踩到：★ 我先试 `Extension.GetUserPreferenceInteger(47, "")` ⇒ 四个 code 全报
    #:   `(-2147352571, '类型不匹配')`（`0x80020005`）⇒ ★★ **那不是「code 猜错了」**
    #:   （★ 反射里 `swUnitsLinear = **47**` 正是我试的第一个），★ 而是**宿主对象不对**：
    #:   官方示例 `Get_and_Set_User_Preferences_Example_VB.md` 里**全是**
    #:   `swApp.GetUserPreferenceIntegerValue(...)` —— ★ **在 `ISldWorks` 上** ✓
    #:   ⇒ ★ 与事实 36 同形（★ 同名分属不同族 ⇒ 报「类型不匹配」而非「方法不存在」）。
    #: ★★ **而两条路是**不同层次**，不是「同一件事的两个源」**：
    #:   · `IModelDoc2.GetUnits()` ⇒ **这一个文档**的单位（★ 可被文档属性覆盖）
    #: · `ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` ⇒ **系统默认**（★
    #:  新建文档的默认）
    #: ⇒ ★★★ **所以它们**允许不同**** —— ★ 本函数把两者都报出来，★ **而不是断言「必须相
    #: 等」**。
    pref, pref_sys = None, None
    try:
        ext = get_com_member(model, "Extension")
        for code in (47,):
            try:
                pref = get_com_member(ext, "GetUserPreferenceInteger", code, "")
                if pref is not None:
                    out["pref_linear_via"] = "IModelDocExtension"
                    break
            except Exception:  # noqa: BLE001
                pref = None
    except Exception:  # noqa: BLE001
        pref = None
    try:
        app = None
        for getter in ("GetSldWorks", "IGetSldWorks"):
            try:
                #: dispatch-arg: probe 试名探测：`GetSldWorks`/`IGetSldWorks` 两源均查不到，按序试
                app = get_com_member(model, getter)
                if app is not None:
                    break
            except Exception:  # noqa: BLE001
                continue
        if app is None:
            #: ★ 兜底：★ `IModelDoc2.GetSldWorks` 在迟到绑定下拿不到 ⇒ 直接连正在跑的那
            #: 个实例。
            #:   ★ 本仓库是**单源运行**（事实 24：多个进程抢同一 COM 连接会死锁）
            #:   ⇒ ★ `Dispatch("SldWorks.Application")` 拿到的是**同一个**实例，安全。
            try:
                import win32com.client as _w  # noqa: PLC0415

                app = _w.Dispatch("SldWorks.Application")
                out["app_via"] = "Dispatch"
            except Exception as exc:  # noqa: BLE001
                out["app_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
        else:
            out["app_via"] = "IModelDoc2.GetSldWorks"
        if app is not None:
            #: ★★★★★ 2026-10-01（轮 339）**arity = 1，不是 2** —— 三源一致：
            #: · 官方签名 `System.int GetUserPreferenceIntegerValue( System.int UserPref
            #: erenceValue )`
            #:   · 反射 `'GetUserPreferenceIntegerValue': 1`（★ 三处都是 1）
            #: · 官方示例 `swApp.GetUserPreferenceIntegerValue(swUserPreferenceIntegerVa
            #: lue_e.swViewRotationMouseSpeed)`
            #: ⇒ ★★ 我先前传 `(47, "")` 两个 ⇒ `DISP_E_BADPARAMCOUNT`（`0x8002000E`「无
            #: 效的参数数目」）。
            #: ⚠ **别与 `IModelDocExtension.GetUserPreferenceInteger(UserPref, UserPrefO
            #: ption)` 混** ——
            #:     ★ 那是**另一个方法**（2 参、另一个宿主）⇒ ★ 两个同名前缀、不同 arity。
            pref_sys = get_com_member(app, "GetUserPreferenceIntegerValue", 47)
            if pref_sys is not None and pref is None:
                out["pref_linear_via"] = "ISldWorks"
                pref = pref_sys
    except Exception as exc:  # noqa: BLE001
        out["pref_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
    out["pref_linear"] = pref
    out["pref_linear_system_default"] = pref_sys
    #: ★ 注意：这是**文档级**与**系统默认**的关系，**不是**两个源互证 ⇒ 允许不同。
    if pref_sys is not None and seq:
        out["doc_matches_system_default"] = int(pref_sys) == int(seq[0])
    out["★"] = (
        "★ 主源：`IModelDoc2.GetUnits()`（0 参 · 官方 Remarks：5 个 short = "
        "[LengthUnit, FractionBase, FractionValue, SignificantDigits, RoundToFraction]）；"
        "★ 对照源：`ISldWorks.GetUserPreferenceIntegerValue(swUnitsLinear = 47)` —— "
        "★ **系统默认**（★ 与文档级**允许不同**，★ **不是互证**）；"
        "★ 期望 `LengthUnit == 0`（`swMM`）—— ★ 因为本仓库建模一律按毫米"
    )
    return out


# ── 数值的**量纲分派**（2026-10-26 起：杜绝「万能 ×1000」）──────────────────────
#
# 事故：示教器把 `IDimension.GetSystemValue2` 的返回值一律 ×1000 当成毫米，
# 于是业主草图的 `ANGLE` 被记成 `785.398 mm`（= 0.7854 rad × 1000）——
# **假数值**，比读不到更危险（读不到会去查，读错会照着做）。
#
# 根因不是「这次算错了」，而是**存在一个不分量纲的换算函数**。⇒ 现在只提供
#   ① `m_to_mm` / `rad_to_deg`：名字写明「从什么到什么」，传错量纲是调用方的错；
#   ② `dimension_reading(dim, relation_type)`：**按关系类型决定量纲**，
#      未实测的关系类型原样保留并标 `unit_unverified`，**不猜单位**。

#: 长度类关系（`GetSystemValue2` 回**米**）—— 只收已真机实测的
LENGTH_RELATION_TYPES = frozenset({1, 3, 15})     #: DISTANCE / RADIUS / DIAMETER
#: 角度类关系（回**弧度**）—— 只收已真机实测的
ANGLE_RELATION_TYPES = frozenset({2})             #: ANGLE（实测 0.785398 ⇒ 45°）


def m_to_mm(value_m: float) -> float:
    """**米 → 毫米**。只接受米；调用方负责保证传进来的是长度。"""
    return round(float(value_m) * 1000.0, 4)


def rad_to_deg(value_rad: float) -> float:
    """**弧度 → 度**。"""
    return round(math.degrees(float(value_rad)), 4)


def dimension_reading(dim, relation_type_int) -> dict:
    """读一个尺寸的数值，**按关系类型决定量纲**，一次取全。

    :param dim: `IDimension`（`IDisplayDimension.GetDimension2(0)` 得到）
    :param relation_type_int: `ISketchRelation.GetRelationType()` 的原始整数
    :returns: `{"value_mm": 100.0}`（长度）· `{"value_rad": 0.7854, "value_deg": 45.0}`
              （角度）· `{"raw_system_value": …, "unit_unverified": True}`（未实测量纲）；
              读不到回 `{}`，**不编数值**。

    ⚠ `ARCANG*` / `ANGLE3P` 等虽然名字含 ANGLE，但**未实测其 GetSystemValue2 的量纲**
      ⇒ 落到 `unit_unverified` 分支，原样保留 + 标注，而不是当成弧度。
    """
    if dim is None:
        return {}
    try:
        raw = dim.GetSystemValue2("")
    except Exception:  # noqa: BLE001
        return {}
    if raw is None:
        return {}
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return {}

    if relation_type_int in LENGTH_RELATION_TYPES:
        return {"value_mm": m_to_mm(v)}
    if relation_type_int in ANGLE_RELATION_TYPES:
        return {"value_rad": round(v, 6), "value_deg": rad_to_deg(v)}
    return {"raw_system_value": round(v, 6), "unit_unverified": True}


# ═══════════════════════════════════════════════════════════════════════════════
# ★★★ 单位契约真源（★ 2026-11-02 业主指令：按官方文档把全项目的量纲口径钉死）
# ═══════════════════════════════════════════════════════════════════════════════
#
# ★★★★★ **官方总纲（逐字）** —— `C:\swapi\docs\Programming with the SOLIDWORKS
#   API\Units.md`：
#   「**Unless otherwise stated, all SOLIDWORKS API functions use metric units.
#     Specifically, the SOLIDWORKS API accepts or returns values as meters, radians,
#     kilograms, square meters, or cubic meters.**」
#
# ★★★ **为什么官方这样设计**（`IModelDoc2::SetUnits` 的说明逐字）：
#   「Sets the units used by the **end-user** for the model.」
#   ⇒ ★★ **文档单位是「给终端用户看的显示属性」，API 层是固定的 SI 米制契约**。
#     这是**有意的分层**：同一份宏在毫米文档 / 英寸文档里跑出同样的几何。
#   ⇒ ★ **因此「把文档单位改成米」并不能让 API 不再需要换算** —— API 本来就是米，
#     改的只是 UI 显示；而换算关系（我们的 `_mm` 包装 ↔ API 米）一点没消失。
#
# ★★★ **四个不同口径（必须分别对齐，混用即 1000× 错）**：
#   ┌──────────────────────────────┬──────────┬───────────────────────────────┐
#   │ 边界                          │ 口径      │ 依据                           │
#   ├──────────────────────────────┼──────────┼───────────────────────────────┤
#   │ 几何 API 默认（含方程式曲线、  │ **米**    │ 官方 Units.md 总纲             │
#   │ FeatureExtrusion3 的 D1 等）  │          │ + 事实 517 之补（D1 吃米）      │
#   │ GetSystemValue3 / SetSystem-  │ **文档     │ 事实 517（真机）               │
#   │ Value3（尺寸值）              │  单位**   │                               │
#   │ IBody2.GetBodyBox             │ **毫米**  │ 事实 71（官方未写，实测）       │
#   │ 本仓 `sketch_*` 包装           │ **毫米**  │ AGENTS.md §十四之二 既有约定    │
#   └──────────────────────────────┴──────────┴───────────────────────────────┘
#
# ★★ **所以「不被量纲影响」的官方答案不是某个开关，而是**：
#   ① 默认一律按米（总纲）· ② 例外必须被**显式记录**（「unless otherwise stated」）
#   ③ 工程落地 = **单位进名字 + 单一换算点**（AGENTS.md §十四之二 的根因解法）
#   ⇒ ★ 换算不能被消灭，只能被**收敛到一处并让门禁看得见**。
#
#: ★★ **这不是第二真源，是索引**（AGENTS.md §十四之四「同一个东西只许有一个名字」）：
#:   权威正文在 `specs/212-unit-discipline/`（判据 C1–C7 · 25 个任务全 [x]）
#:   + `docs/unit-conflicts.md`（「官方声明 vs 真机读数」冲突台账）
#:   + `docs/known-facts.md` 事实 71 / 517；运行时守卫在 `mcp-server/server.py::_unit_guard`。
#:   ⇒ ★ 口径若与上述任一处冲突，**以那三处为准**，改这里不算数。
#: ★ 用途单一：给**几何包装函数**一个查表入口，避免每次现场判断（规格 212 的中心思想）。
UNIT_CONTRACT_INDEX = {
    "api_geometry_default": "m",
    "ISketchManager.CreateEquationSpline2": "m",     #: 官方总纲；2026-11-02 实测 0.01→直径20mm
    "IFeatureManager.FeatureExtrusion3.D1": "m",     #: 事实 517 之补
    "IModelDocExtension.GetSystemValue3": "document",  #: 事实 517
    "IBody2.GetBodyBox": "mm",                       #: 事实 71（官方未写，实测）
    "sw_part.sketch_circle/sketch_line": "mm",        #: AGENTS.md §十四之二
}


def mm_to_m(value_mm: float) -> float:
    """**毫米 → 米**（★ 进 API 几何口时用；与 `m_to_mm` 互逆）。"""
    return float(value_mm) / 1000.0


def length_scale_to_mm(model) -> float:
    """★ **文档单位 → 毫米** 的倍数（事实 517 的 `_document_length_unit_scale` 同精神）。

    :returns: 1.0（`swMM`）· 10.0（`swCM`）· 1000.0（`swMETER`）· 25.4（`swINCHES`）…
               读不到文档单位回 `None`，**不猜**。
    """
    rep = read_units_report(model)
    lu = rep.get("length_unit")
    return {
        0: 1.0,          # swMM
        1: 10.0,         # swCM
        2: 1000.0,       # swMETER
        3: 25.4,         # swINCHES
        4: 304.8,        # swFEET
        6: 1e-7,         # swANGSTROM
        7: 1e-6,         # swNANOMETER
        8: 1e-3,         # swMICRON
        9: 0.0254,       # swMIL
        10: 25.4,        # swUIN
    }.get(lu)


def meters_expr(expr_mm: str) -> str:
    """★ 把**以毫米为系数**的表达式整体换算成**米**（用于方程式曲线）。

    ★ 为什么可以整体乘：表达式里的长度都出现在**系数位**，参数 `t` 是无量纲的
      ⇒ `0.001*(expr)` 就是一次干净的 mm→m 换算（2026-11-02 实测：`0.01*cos(t)`
      得到直径 20 mm，即表达式吃米）。
    """
    return "0.001*(%s)" % expr_mm


def equation_curve_mm(model, x_expr_mm, y_expr_mm, t_start, t_end, *,
                      z_expr_mm="", is_angle_range=False):
    """★ **名字带单位的方程曲线**：表达式按**毫米**给，内部一次性转米后调 SW。

    ★★ 为什么需要它：`CreateEquationSpline2` 吃**米**（官方总纲），而本仓建模一律
      **毫米**；直接在调用点写 `*0.001` 就会渗到十几处，混用即成 1000× 错
      （2026-11-02 实测：同一草图里两条曲线一个按毫米一个按米写 ⇒ 轮廓永远接不上 ⇒
      拉伸静默回 `None`）。⇒ 换算只在这一处发生。

    :param model: `IModelDoc2`，且**必须已在活动草图中**
    :param x_expr_mm: x 关于 `t` 的表达式，**长度系数按毫米写**
    :param y_expr_mm: y 关于 `t` 的表达式，**长度系数按毫米写**
    :param t_start: 参数起点（★ 无量纲，或角度见 `is_angle_range`）
    :param t_end: 参数终点
    :param z_expr_mm: 3D 曲线的 z 表达式（可选）
    :param is_angle_range: True 时范围按弧度解释
    :returns: `ISketchSpline`；**调用方仍须回读段数**才能判定是否真的进了草图
              （★ 该接口失败时**不抛异常**，只静默不成段）。
    """
    sm = get_com_member(model, "SketchManager")
    return get_com_member(
        sm,
        "CreateEquationSpline2",
        meters_expr(x_expr_mm),
        meters_expr(y_expr_mm),
        meters_expr(z_expr_mm) if z_expr_mm else "",
        "%r" % t_start,
        "%r" % t_end,
        bool(is_angle_range),
        0.0,
        0.0,
        0.0,
        True,
        True,
    )
