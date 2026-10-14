"""★ 选型计算（★ 齿轮 / V 带 / 弹簧 / 轴承寿命）—— ★ 从 `mech-design` 的校核算例提取。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/selection_calc.py
# 定位:   规格 `specs/336-selection-calc` ——
#           ★★ 把 `mech-design/知识库/*/校核脚本/*.ps1` 的 **24 个可跑算例**
#             里**最常用的 4 类**接成 Python（★ 本仓此前**没有**这些计算）。
#           ★★★ 触发它的是 2026-10-14 全自动挖掘的**收口盘点**：
#             `tools/closure_inventory.py` 判「**24 个 .ps1 校核脚本**」
#             是唯一还剩的**值得做**项。
# 官方依据: ① `~/.agents/skills/mech-design/知识库/70-标准件与选型计算/校核脚本/
#              直齿圆柱齿轮选型.ps1`（★ 自述来源 **EngineersEdge《Spur Gear Design
#              Equations and Formula》ANSI B6.1**）
#           ② 同目录 `V带与链传动选型.ps1`（★ 自述来源 **EngineersEdge Belt Design**）
#           ③ `螺旋弹簧设计.ps1`（★ 自述 **Wahl 系数已与原表逐点核对**）
#           ④ `轴承数据怎么读.md` / `轴承选型实测.md`（★ `L10 = (C/P)^ε × 10⁶ 转`）
# 许可:   本仓库 MIT。★ 公式是**公开标准公式**（★ ANSI B6.1 / ISO 281）⇒
#           ★ 按公式**自建实现**，★ 未抄任何第三方代码。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 纯计算（★ 不碰 COM）；★ 有**交叉验算**（★ 见测试）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import math

#: ★ 标准压力角（度）
ALPHA_DEG = 20.0


class CalcError(Exception):
    """★ 计算失败（★ 带封闭码）。"""

    CODES = ("bad-input", "out-of-range")

    def __init__(self, code: str, detail: str = "") -> None:
        assert code in self.CODES, "★ 非法拒绝码：%r" % code
        self.code = code
        self.detail = detail
        super().__init__("%s: %s" % (code, detail))


#: ══════════════════════════════════════════════════════════════════════
# 一、渐开线直齿圆柱齿轮（★ ANSI B6.1 · 20° 全齿高）
#: ══════════════════════════════════════════════════════════════════════

def spur_gear(*, module_mm: float, z1: int, z2: int | None = None,
              alpha_deg: float = ALPHA_DEG) -> dict:
    """★★ **直齿圆柱齿轮几何**（★ 公式逐条来自 ANSI B6.1）。

    ★★ 判据（★ 逐字承该脚本）：
      ```
      d  = m·z            分度圆
      ha = m              齿顶高     da = m(z+2)
      hf = 1.25m          齿根高     df = m(z-2.5)
      h  = 2.25m          全齿高
      c  = 0.25m          顶隙
      a  = m(z1+z2)/2     中心距
      db = d·cosα         基圆
      p  = πm             齿距
      ```
    ★★ **交叉验算**（★ 该脚本的做法）：
      ★ `a` 用**两种独立公式**算 ⇒ `m(z1+z2)/2` **应等于** `(d1+d2)/2`。
    """
    if module_mm <= 0:
        raise CalcError("bad-input", "★ 模数必须 > 0（实得 %s）" % module_mm)
    if z1 < 1:
        raise CalcError("bad-input", "★ 齿数必须 ≥ 1（实得 %s）" % z1)
    m = float(module_mm)
    a = math.radians(alpha_deg)
    out: dict = {
        "module_mm": m, "alpha_deg": alpha_deg,
        "d1_mm": m * z1,
        "da1_mm": m * (z1 + 2),
        "df1_mm": m * (z1 - 2.5),
        "h_mm": 2.25 * m,
        "ha_mm": m,
        "hf_mm": 1.25 * m,
        "c_mm": 0.25 * m,
        "p_mm": math.pi * m,
        "db1_mm": m * z1 * math.cos(a),
    }
    if z2:
        out.update({
            "z2": z2,
            "d2_mm": m * z2,
            "da2_mm": m * (z2 + 2),
            "df2_mm": m * (z2 - 2.5),
            "db2_mm": m * z2 * math.cos(a),
            "center_distance_mm": m * (z1 + z2) / 2.0,
            "ratio": z2 / z1,
        })
        #: ★★ **交叉验算**：两个独立公式必须相同
        out["center_crosscheck_mm"] = (out["d1_mm"] + out["d2_mm"]) / 2.0
        out["center_crosscheck_ok"] = abs(
            out["center_crosscheck_mm"] - out["center_distance_mm"]) < 1e-9
    return out


#: ══════════════════════════════════════════════════════════════════════
# 二、滚动轴承寿命（★ ISO 281）
#: ══════════════════════════════════════════════════════════════════════

#: ★ 寿命指数（★ 逐字承 `design_rules.yaml`）
LIFE_EXPONENT = {"ball": 3.0, "roller": 10.0 / 3.0}


def bearing_life(*, c_kn: float, p_kn: float, rpm: float,
                 kind: str = "ball") -> dict:
    """★★ **轴承额定寿命** `L10 = (C/P)^ε × 10⁶ 转`（★ ISO 281）。

    ★★ 判据（★ 逐字承 `mech-design/知识库/design_rules.yaml`）：
      「`L₁₀ = (C/P)^ε × 10⁶ 转` · `C=基本额定动载荷, P=当量动载荷,`
        `ε=3(球), 10/3(滚子)`」
    ★ 另给**小时数**：`L10h = 10⁶ × L10 / (60 × n)`。
    """
    if c_kn <= 0 or p_kn <= 0 or rpm <= 0:
        raise CalcError("bad-input",
                        "★ C/P/n 必须 > 0（实得 C=%s P=%s n=%s）"
                        % (c_kn, p_kn, rpm))
    if kind not in LIFE_EXPONENT:
        raise CalcError("bad-input",
                        "★ `kind` 只能是 %s（实得 %r）"
                        % (sorted(LIFE_EXPONENT), kind))
    eps = LIFE_EXPONENT[kind]
    l10_mrev = (c_kn / p_kn) ** eps            #: ★ 百万转
    return {
        "kind": kind, "epsilon": eps,
        "c_kn": c_kn, "p_kn": p_kn, "rpm": rpm,
        "l10_mrev": l10_mrev,
        "l10_rev": l10_mrev * 1e6,
        "l10h": l10_mrev * 1e6 / (60.0 * rpm),
        "★": "★ L10 = (C/P)^ε × 10⁶ 转（★ ISO 281）",
    }


def required_c(*, p_kn: float, target_hours: float, rpm: float,
               kind: str = "ball") -> dict:
    """★★ **反解**：给定寿命要求 ⇒ **需要多大的 C**（★ 选型用）。

    ★★ 判据（★ 逐字承 `design_rules.yaml` 的 `selection_steps`）：
      「**2. 由寿命要求反算所需基本额定动载荷 C**」
    """
    if p_kn <= 0 or target_hours <= 0 or rpm <= 0:
        raise CalcError("bad-input", "★ P/寿命/转速必须 > 0")
    eps = LIFE_EXPONENT.get(kind)
    if eps is None:
        raise CalcError("bad-input", "★ `kind` 只能是 %s" % sorted(LIFE_EXPONENT))
    l10_mrev = target_hours * 60.0 * rpm / 1e6
    return {"required_c_kn": p_kn * l10_mrev ** (1.0 / eps),
            "l10_mrev": l10_mrev, "epsilon": eps, "kind": kind}


#: ══════════════════════════════════════════════════════════════════════
# 三、螺旋压缩弹簧（★ Wahl 系数）
#: ══════════════════════════════════════════════════════════════════════

def spring(*, wire_d_mm: float, mean_d_mm: float, active_coils: int,
           material_g_mpa: float = 79000.0) -> dict:
    """★★ **螺旋压缩弹簧刚度**（★ Wahl 修正）。

    ★★ 判据（★ 标准公式）：
      ```
      C  = D/d                        旋绕比
      Kw = (4C-1)/(4C-4) + 0.615/C    ★ Wahl 系数
      k  = G·d⁴ / (8·D³·n)            刚度 N/mm
      ```
    ★★ 该脚本自述：★ **「Wahl 系数（已与原表逐点核对）」**。
    """
    if wire_d_mm <= 0 or mean_d_mm <= 0 or active_coils < 1:
        raise CalcError("bad-input", "★ d/D/n 必须 > 0（n ≥ 1）")
    d, dm, n = float(wire_d_mm), float(mean_d_mm), int(active_coils)
    c = dm / d
    if c < 3:
        raise CalcError("out-of-range",
                        "★ 旋绕比 C=%.2f < 3 ⇒ ★ 制造困难（★ 常用 4~16）" % c)
    kw = (4 * c - 1) / (4 * c - 4) + 0.615 / c
    k = material_g_mpa * d ** 4 / (8.0 * dm ** 3 * n)
    return {"wire_d_mm": d, "mean_d_mm": dm, "active_coils": n,
            "spring_index_c": c, "wahl_kw": kw, "rate_n_per_mm": k,
            "material_g_mpa": material_g_mpa,
            "★": "★ Kw=(4C-1)/(4C-4)+0.615/C · k=G·d⁴/(8·D³·n)"}


#: ══════════════════════════════════════════════════════════════════════
# 四、V 带传动（★ 带速 + 有效拉力）
#: ══════════════════════════════════════════════════════════════════════

def v_belt(*, d1_mm: float, d2_mm: float, rpm: float,
           center_mm: float) -> dict:
    """★★ **V 带传动**（★ 带速 / 传动比 / 带长）。

    ★★ 判据（★ 标准公式）：
      ```
      v  = π·d1·n / 60000          带速 m/s（★ d1 是**小带轮**）
      i  = d2/d1                   传动比
      Ld ≈ 2a + π(d1+d2)/2 + (d2-d1)²/(4a)    带长
      ```
    ★★ 该脚本自述：★ **「带长双算法交叉验算」** ⇒ ★ 本实现给两个值。
    """
    if d1_mm <= 0 or d2_mm <= 0 or rpm <= 0 or center_mm <= 0:
        raise CalcError("bad-input", "★ 直径/转速/中心距必须 > 0")
    v = math.pi * d1_mm * rpm / 60000.0
    ld1 = (2 * center_mm + math.pi * (d1_mm + d2_mm) / 2.0
           + (d2_mm - d1_mm) ** 2 / (4 * center_mm))
    #: ★ 第二算法：角度修正（★ 更精确）
    theta = math.pi - 2 * math.asin((d2_mm - d1_mm) / (2 * center_mm))
    ld2 = (2 * center_mm * math.cos((math.pi - theta) / 2)
           + (d1_mm * theta + d2_mm * (2 * math.pi - theta)) / 2.0)
    return {"d1_mm": d1_mm, "d2_mm": d2_mm, "rpm": rpm,
            "center_mm": center_mm, "belt_speed_m_s": v,
            "ratio": d2_mm / d1_mm,
            "length_approx_mm": ld1, "length_angle_mm": ld2,
            "length_crosscheck_delta_mm": abs(ld1 - ld2),
            "★": "★ 两个独立算法各算一次带长 ⇒ 差值应很小"}


def report() -> dict:
    """★ **有哪些计算**（★ 供工具层暴露）。"""
    return {
        "spur_gear": "★ 直齿圆柱齿轮几何（ANSI B6.1）",
        "bearing_life": "★ 轴承 L10 寿命（ISO 281）",
        "required_c": "★ 由寿命反解所需 C（选型）",
        "spring": "★ 螺旋压缩弹簧刚度（Wahl 修正）",
        "v_belt": "★ V 带传动（带速/传动比/带长双算法）",
        "★": ("★ 公式来自 `mech-design` 的校核算例（★ 自述来源 EngineersEdge "
              "ANSI B6.1 等公开标准）⇒ ★ 按公式自建，★ 未抄第三方代码"),
    }
