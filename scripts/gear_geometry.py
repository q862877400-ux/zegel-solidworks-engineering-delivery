"""★ 机械工程规范：★ **标准直齿轮的渐开线齿廓与摆线齿根过渡**（★ 真曲线，★ 不是折线）。

★★★★★ **业主原话**：「★ **像什么直接用直线去逼近曲线这种野路子，你就全部都改掉**」✓

★★★ **本模块取代什么**：★ 原 `sw_gear.py` 用 `involute_segments=12` 把渐开线
  **离散成 12 段直线**（★ `sketch_line` 逐段画）⇒ ★★ 那是**野路子**：
    · ★ 齿面是**多段折线**（★ 不是渐开线）⇒ ★ 齿形有**弦差**；
    · ★ 与**配对齿轮的共轭**被破坏（★ 渐开线的**唯一**价值就是共轭）⇒
      ★★ 传动比会**周期性波动**、★ 冲击与噪声↑；
    · ★ 齿根是**径向直线 + 圆弧**（★ 不是**摆线**）⇒ ★ 根**应力集中**算不准；
    · ★ 段数还是**可调的**（12/24/64）⇒ ★★ 同一份规格能建出**不同齿形** ✗

★★★ **改成什么（★ 机械工程的标准做法）**：
  ★ ① **齿廓 = 真渐开线**（★ 方程式驱动曲线）：
      `x(t) = rb·(cos t + t·sin t)` · `y(t) = rb·(sin t − t·cos t)`
      ★ 其中 `rb = m·z/2·cos α`（★ 基圆）· ★ `t` = 展开角参数（rad）
      ★★ 半径关系：★ `r(t) = rb·√(1+t²)` ⇒ ★ 反解 `t = √((r/rb)² − 1)` ✓
  ★ ② **齿根过渡 = 真摆线（trochoid）**（★ 齿条刀具顶圆角**包络**）：
      ```
      ★ a = hf − ρ        （★ hf = 1.25m 齿根高 · ★ ρ = 0.38m 刀顶圆角）
      ★ x(φ) = (r−hf+ρ)cos φ + rφ sin φ + ρ(−a cos φ + rφ sin φ)/√(a²+r²φ²)
      ★ y(φ) = (r−hf+ρ)sin φ − rφ cos φ + ρ(−a sin φ − rφ cos φ)/√(a²+r²φ²)
      ```
      ★★ 这是**滚齿/插齿实际加工出来的**齿根形状 ⇒ ★ 根应力算得准 ✓

★★★ **真机证据**（★ 走 `sw_guard` · ★ 零弹窗）：
  · ★ `output/involute-equation-curve-evidence.json` ⇒ ★ **渐开线方程式曲线 OK**（段 0→1）✓
  · ★ `output/equation-expression-power-evidence.json` ⇒ ★ **sqrt ✓ · 长表达式(77 字符) ✓ ·
    pi ✓ · 幂 `^` ✗** ⇒ ★★ 摆线那种含 `sqrt` 的长式子**能建** ✓

★★ **本模块是「方法」**（★ 判据：★「那个数字错了，回读能不能查出来」⇒
  ★ 齿形错了，回读只能看到「它是个齿轮」⇒ **不能** ⇒ 方法）✓
  ★★ 所以它**不带工具**（★ 工具只暴露**驱动 CAD 的机械能力**）✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 重写 —— ★ 原 `sw_gear.py` 的**离散逼近**被替换）
# 文件:   scripts/gear_geometry.py
# 定位:   ★ 业主 2026-10-10 指令：★ 「方法要按机械工程的**规范做法**」——
#         ★ 把「12 段直线逼近渐开线」改成**真渐开线 + 真摆线齿根**。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ 11 参 · ★ 方程式
#           曲线）
#         `C:\swapi\examples\Create_Equation-driven_Curve_Example_VB.md`（★ 调用序）
#         ★ 渐开线定义：★ GB/T 1356 · ★ ISO 53 · ★ ANSI B6.1（★ 全齿高制）
#         ★ 摆线齿根：★ 齿条刀具顶圆角包络（★ GB/T 1356 附录 / ★ ISO 53）
# 许可:   本仓库 MIT。★ 无第三方代码引入（★ 公式是**标准定义**，★ 不是抄某份代码）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "GearSpec",
    "GearGeometry",
    "STANDARD_MODULES_GB_T_1357",
    "involute_xy_mm",
    "trochoid_xy_mm",
    "tool_tip_arc_offset_mm",
    "calculate_gear_geometry",
    "involute_x_expression",
    "involute_y_expression",
    "trochoid_x_expression",
    "trochoid_y_expression",
]

#: ★★★ **标准模数系列**（★ GB/T 1357 **第一系列**）——
#:   ★★ 机械工程的规矩：★ 算出模数后**必须向上取到标准值**（★ 不是随便用算出来的数）✓
STANDARD_MODULES_GB_T_1357 = (
    1.0,
    1.25,
    1.5,
    2.0,
    2.5,
    3.0,
    4.0,
    5.0,
    6.0,
    8.0,
    10.0,
    12.0,
    16.0,
    20.0,
)
#: ★★ **标准齿条刀具参数**（★ GB/T 1356 · ★ 全齿高制 · ★ 压力角 20°）：
#:   · ★ 齿顶高系数 `ha* = 1.0`（★ 齿顶高 = 1.0m）
#:   · ★ 齿根高系数 `hf* = 1.25`（★ 齿根高 = 1.25m ⇒ ★ 顶隙 `c* = 0.25`）
#:   · ★ 刀顶圆角系数 `ρ* = 0.38`（★ 标准齿条刀具 · ★ 它决定摆线齿根的形状）✓
ADDENDUM_COEFF = 1.0
DEDENDUM_COEFF = 1.25
TOOL_TIP_RADIUS_COEFF = 0.38


@dataclass(frozen=True)
class GearSpec:
    """★ 标准外啮合直齿轮规格（★ 尺寸毫米 · ★ 角度度）。"""

    module_mm: float
    teeth: int
    face_width_mm: float
    pressure_angle_deg: float = 20.0
    bore_diameter_mm: float = 0.0
    #: ★ 展开角参数的采样数（★ **只用于离线验算/出图**，★ 建模用**真曲线**，不用它）✓
    verify_samples: int = 65


@dataclass(frozen=True)
class GearGeometry:
    """★ 校验过的齿轮解析尺寸（★ 全部按标准定义算）。"""

    spec: GearSpec
    pitch_diameter_mm: float
    base_diameter_mm: float
    outside_diameter_mm: float
    root_diameter_mm: float
    circular_pitch_mm: float
    tooth_thickness_at_pitch_mm: float
    whole_depth_mm: float
    clearance_mm: float
    tool_tip_radius_mm: float
    t_root: float
    t_tip: float
    minimum_teeth_without_undercut: int
    undercut_risk: bool
    contact_ratio: float
    warnings: tuple[str, ...]

    def evidence(self) -> dict:
        """★ 可序列化的读数（★ 供判据用）。"""
        return {
            "gear_type": "standard_external_spur_involute",
            "profile_curve": "true_involute_equation_driven",
            "root_form": "true_trochoid_rack_tool_envelope",
            "standards": ["GB/T 1356", "GB/T 1357", "ISO 53", "ANSI B6.1"],
            "input": {
                "module_mm": self.spec.module_mm,
                "teeth": self.spec.teeth,
                "face_width_mm": self.spec.face_width_mm,
                "pressure_angle_deg": self.spec.pressure_angle_deg,
                "bore_diameter_mm": self.spec.bore_diameter_mm,
            },
            "coefficients": {
                "addendum": ADDENDUM_COEFF,
                "dedendum": DEDENDUM_COEFF,
                "tool_tip_radius": TOOL_TIP_RADIUS_COEFF,
            },
            "dimensions_mm": {
                "pitch_diameter": self.pitch_diameter_mm,
                "base_diameter": self.base_diameter_mm,
                "outside_diameter": self.outside_diameter_mm,
                "root_diameter": self.root_diameter_mm,
                "circular_pitch": self.circular_pitch_mm,
                "tooth_thickness_at_pitch": self.tooth_thickness_at_pitch_mm,
                "whole_depth": self.whole_depth_mm,
                "clearance": self.clearance_mm,
                "tool_tip_radius": self.tool_tip_radius_mm,
            },
            "involute_parameter_range": {"t_root": self.t_root, "t_tip": self.t_tip},
            "minimum_teeth_without_undercut": self.minimum_teeth_without_undercut,
            "undercut_risk": self.undercut_risk,
            "contact_ratio": self.contact_ratio,
            "warnings": list(self.warnings),
        }


def _finite_positive(value: float, name: str) -> float:
    """★ 校验有限正数。"""
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError("%s 必须是有限正数" % name)
    return number


def involute_xy_mm(t: float, base_radius_mm: float) -> tuple[float, float]:
    """★ **渐开线**（★ 标准定义 · ★ 直角坐标 · 毫米）。

    ★ 参数方程（★ 本仓的规范形式）：
        `x(t) = rb·(cos t + t·sin t)`
        `y(t) = rb·(sin t − t·cos t)`
    ★ 半径：`r(t) = rb·√(1 + t²)` ⇒ ★ `t = √((r/rb)² − 1)` ✓
    ★★ **这是**共轭齿廓**的唯一正确形状** —— ★ 折线逼近会破坏共轭 ✓
    """
    return (
        base_radius_mm * (math.cos(t) + t * math.sin(t)),
        base_radius_mm * (math.sin(t) - t * math.cos(t)),
    )


def trochoid_xy_mm(
    phi: float,
    *,
    pitch_radius_mm: float,
    dedendum_mm: float,
    tool_tip_radius_mm: float,
    module_mm: float | None = None,
    pressure_angle_rad: float | None = None,
) -> tuple[float, float]:
    """★ **摆线齿根过渡**（★ 齿条刀具顶圆角**包络** · ★ 毫米）。

    ★★ 这就是**滚齿/插齿实际加工出来**的齿根形状 ⇒ ★ 根应力集中算得准 ✓
    ★ 与「径向直线 + 圆弧」那种近似相比，★ 它才反映真实刀具留下的过渡曲线 ✓

    ★★★★★ **2026-10-10 修正（★ 由独立核验抓出 · ★ 我原来的公式有真缺陷）**：
      ★★ **缺陷**：★ 我原来把**刀顶圆角中心**放在齿廓上（★ 等价于 `u_c = 0`）✗
        ★★★ 而**标准齿条**要求圆角中心**偏移**一个量：
        ```
        ★ u_c = π·m/4 − a·tan α − ρ/cos α
        ★ 其中 a = hf − ρ
        ```
        ★★ 本机算（★ m=1 · α=20° · hf=1.25 · ρ=0.38）：
          ★ `u_c = 0.06435650604500565 mm`（★ 占模数 **6.4357%**）✓
      ★★★ **为什么 `u_c = 0` 是错的**（★ 判据）：
        ★ `u_c = 0` 时，刀顶圆心到齿廓的**距离 ≠ ρ** ⇒ ★ **刀具本身有台阶**（★ 不光滑）✗
        ★★ 而 `u_c = 0` **且** 与齿廓相切，★ 会**反过来要求 `ρ = 0.4719·m`**（★ 不是 0.38）⇒
          ★★★ **两个条件不能同时成立** ⇒ ★ **`u_c = 0` 不是一种有效读法** ✓
      ★★ **后果（★ 若用旧式）**：★ 摆线与渐开线在**成形圆**处
        ★ 切向错位 **0.3687°** ⇒ ★ 台阶 **0.0606 mm**（★ 占模数 **6.06%**）✗
      ★★★ **修法**：★ 把 `r·φ` 换成 `u_c + r·φ`（★ 等价于相位平移 `u_c/r`）✓
        ★ 核验：★ 修正式 `φ = −u_c/r` 处半径 = `rf` **精确**（★ 旧式在 `φ=0` 处给 rf，
        ★★ 那是**平移掩盖**，★ 不是标准位置）✓

    ★ 公式（★ 修正后）：
        `a = hf − ρ` · `u_c = πm/4 − a·tan α − ρ/cos α` · `v = u_c + r·φ`
        `s = √(a² + v²)`
        `x(φ) = (r−a)cos φ + v sin φ + ρ(−a cos φ + v sin φ)/s`
        `y(φ) = (r−a)sin φ − v cos φ + ρ(−a sin φ − v cos φ)/s`

    ⚠ **`module_mm` / `pressure_angle_rad` 不给时退回 `u_c = 0`**（★ 保持向后兼容）——
      ★★ **但那不是标准齿形** ⇒ ★★ 新代码**必须**传这两个参数 ✓
    """
    r = float(pitch_radius_mm)
    hf = float(dedendum_mm)
    rho = float(tool_tip_radius_mm)
    a = hf - rho
    #: ★★★ `u_c`：★ 刀顶圆角中心相对齿廓的偏移（★ 标准齿条的核心量）
    if module_mm is not None and pressure_angle_rad is not None:
        u_c = (
            math.pi * float(module_mm) / 4.0
            - a * math.tan(float(pressure_angle_rad))
            - rho / math.cos(float(pressure_angle_rad))
        )
    else:
        u_c = 0.0
    v = u_c + r * phi
    den = math.sqrt(a * a + v * v)
    x = (
        (r - a) * math.cos(phi)
        + v * math.sin(phi)
        + rho * (-a * math.cos(phi) + v * math.sin(phi)) / den
    )
    y = (
        (r - a) * math.sin(phi)
        - v * math.cos(phi)
        + rho * (-a * math.sin(phi) - v * math.cos(phi)) / den
    )
    return x, y


def tool_tip_arc_offset_mm(
    module_mm: float,
    pressure_angle_rad: float,
    dedendum_mm: float,
    tool_tip_radius_mm: float,
) -> float:
    """★ **标准齿条的刀顶圆角中心偏移** `u_c`（★ 毫米）。

    ★★ 定义：`u_c = π·m/4 − a·tan α − ρ/cos α`，★ 其中 `a = hf − ρ` ✓
    ★★★ **它是标准齿形的一部分** —— ★ 不把它算进去，★ 摆线就接不上渐开线 ✗
    """
    a = float(dedendum_mm) - float(tool_tip_radius_mm)
    return (
        math.pi * float(module_mm) / 4.0
        - a * math.tan(float(pressure_angle_rad))
        - float(tool_tip_radius_mm) / math.cos(float(pressure_angle_rad))
    )


def calculate_gear_geometry(spec: GearSpec) -> GearGeometry:
    """★ 算标准外啮合直齿轮的**解析几何**（★ 全部按 GB/T 1356 定义）。

    ★★ 与旧实现的区别：★ 旧实现**返回一串离散点**（★ 那本身就是"折线"的源头）；
      ★ 本实现返回**解析尺寸 + 参数范围** —— ★★ 曲线由**方程式驱动曲线**直接建 ✓
    """
    module_mm = _finite_positive(spec.module_mm, "模数")
    face_width_mm = _finite_positive(spec.face_width_mm, "齿宽")
    if isinstance(spec.teeth, bool) or int(spec.teeth) != spec.teeth:
        raise ValueError("齿数必须是整数")
    teeth = int(spec.teeth)
    if teeth < 6 or teeth > 300:
        raise ValueError("齿数必须位于 6..300；更大轮廓应使用专用齿轮软件或原生插件")
    alpha_deg = float(spec.pressure_angle_deg)
    if not math.isfinite(alpha_deg) or not 10.0 <= alpha_deg <= 35.0:
        raise ValueError("压力角必须位于 10..35 度")
    bore_mm = float(spec.bore_diameter_mm)
    if not math.isfinite(bore_mm) or bore_mm < 0.0:
        raise ValueError("轴孔直径不能为负数")

    alpha = math.radians(alpha_deg)
    r = module_mm * teeth / 2.0  #: ★ 分度圆半径 d = mz
    rb = r * math.cos(alpha)  #: ★ 基圆 db = d·cosα
    ra = r + ADDENDUM_COEFF * module_mm  #: ★ 齿顶圆 da = m(z+2)
    hf = DEDENDUM_COEFF * module_mm  #: ★ 齿根高 hf = 1.25m
    rf = r - hf  #: ★ 齿根圆 df = m(z−2.5)
    rho = TOOL_TIP_RADIUS_COEFF * module_mm  #: ★ 刀顶圆角 ρ = 0.38m
    if rf <= 0.0:
        raise ValueError("齿根圆半径非正；请增大齿数或调整齿制")
    if bore_mm >= 2.0 * rf:
        raise ValueError("轴孔直径必须小于齿根圆直径")

    #: ★★ 渐开线的**参数范围**（★ t = 展开角）
    #:   ★ 起点：★ 齿根圆与基圆的**较大者**（★ 基圆以内没有渐开线）✓
    r_start = max(rf, rb)
    t_root = math.sqrt(max(0.0, (r_start / rb) ** 2 - 1.0))
    t_tip = math.sqrt(max(0.0, (ra / rb) ** 2 - 1.0))
    if t_tip <= t_root:
        raise ValueError("齿顶未超出渐开线起点；该参数组合不可用")

    #: ★ 齿顶厚检查（★ 标准做法：★ 齿顶不能变尖）
    pitch = 2.0 * math.pi / teeth
    inv_alpha = math.tan(alpha) - alpha
    half_at_pitch = math.pi / (2.0 * teeth) + inv_alpha
    tip_half = half_at_pitch - (math.tan(math.acos(rb / ra)) - math.acos(rb / ra))
    if tip_half <= 0.0:
        raise ValueError("齿顶厚度退化为零；该参数组合需要变位或其他齿制")

    #: ★★ **重合度 εα**（★ 机械工程的规矩：★ 直齿轮 εα 应 > 1，否则传动不连续）✓
    #:   ★ 与标准齿条啮合（★ 齿条齿顶高 = m）：
    #:     εα = [√(ra²−rb²) + m/sinα − r·sinα] / (π·m·cosα)
    eps_alpha = (
        math.sqrt(max(0.0, ra * ra - rb * rb))
        + module_mm / math.sin(alpha)
        - r * math.sin(alpha)
    ) / (math.pi * module_mm * math.cos(alpha))

    minimum_teeth = int(math.ceil(2.0 / (math.sin(alpha) ** 2)))
    undercut_risk = teeth < minimum_teeth
    warnings: list[str] = []
    if undercut_risk:
        warnings.append(
            "齿数 %d 小于当前压力角的理论无根切下限 %d，存在根切风险。"
            % (teeth, minimum_teeth)
        )
    if eps_alpha <= 1.0:
        warnings.append(
            "重合度 εα = %.3f ≤ 1.0 ⇒ 传动不连续（★ 啮合会中断）⇒ 应增大齿数或齿顶高。"
            % eps_alpha
        )

    return GearGeometry(
        spec=spec,
        pitch_diameter_mm=2.0 * r,
        base_diameter_mm=2.0 * rb,
        outside_diameter_mm=2.0 * ra,
        root_diameter_mm=2.0 * rf,
        circular_pitch_mm=math.pi * module_mm,
        tooth_thickness_at_pitch_mm=math.pi * module_mm / 2.0,
        whole_depth_mm=(ADDENDUM_COEFF + DEDENDUM_COEFF) * module_mm,
        clearance_mm=(DEDENDUM_COEFF - ADDENDUM_COEFF) * module_mm,
        tool_tip_radius_mm=rho,
        t_root=t_root,
        t_tip=t_tip,
        minimum_teeth_without_undercut=minimum_teeth,
        undercut_risk=undercut_risk,
        contact_ratio=eps_alpha,
        warnings=tuple(warnings),
    )


# ── ★ 给 `CreateEquationSpline2` 的**表达式字符串**（★ 真曲线，★ 不是点列）──────────
#: ★★★ 为什么给字符串而不是点：★ `CreateEquationSpline2` 收的是**方程**——
#:   ★★ SolidWorks **自己**按它的精度生成真曲线 ⇒ ★ 齿面是**渐开线**，不是折线 ✓
#:
#: ★★★★★ **单位（★ 真机裁决 · ★ 扫描法 · ★ 4/4 一致）**：
#:   ★ 证据 `output/_probe_parametric_scale_law.json`（★ 走 `sw_guard`）——
#:   ★★ 做法：★ 用 4 条参数式曲线建正方形（★ `x = A·t`，★ t: 0→1），
#:     ★ 拉伸 10 mm，★ **读体积反解边长** ⇒
#:     | ★ 表达式系数 A | ★ 反解边长 | ★ 比值 |
#:     |---|---|---|
#:     | ★ `0.01` | ★ **0.01 mm** | ★ **1.0** |
#:     | ★ `0.1`  | ★ **0.1 mm**  | ★ **1.0** |
#:     | ★ `1.0`  | ★ **1.0 mm**  | ★ **1.0** |
#:     | ★ `10.0` | ★ **10.0 mm** | ★ **1.0** |
#:   ★★★ **裁决：★ 表达式系数就是**毫米**（★ 比值恒为 1）** ✓
#:   ★★ **订正**：★ 我先前一版探针（`output/equation-units-evidence.json`）判成
#:     "expression_in_METRES" ⇒ ★★ **那是错的**（★ 该探针对 9.4 那种超大曲线读回失真）✗
#:     ★★★ **本版以 4 点扫描法为准**（★ 它的判据是**体积反解**，★ 与表达式无共同假设）✓
#:   ⚠ 与 `sketch_line`（★ 收**毫米**）**同口径** · ★ 而 `extrude_boss` **收米** ⇒
#:     ★★ **一次建模里两种口径** ⇒ ★ 逐处标注 ✓


def involute_x_expression(base_radius_mm: float) -> str:
    """★ 渐开线 x(t) 的表达式（★ 交给 SolidWorks · ★ 系数单位 = **毫米**）。"""
    return "%.9f*(cos(t)+t*sin(t))" % float(base_radius_mm)


def involute_y_expression(base_radius_mm: float) -> str:
    """★ 渐开线 y(t) 的表达式（★ 交给 SolidWorks · ★ 系数单位 = **毫米**）。"""
    return "%.9f*(sin(t)-t*cos(t))" % float(base_radius_mm)


def involute_flank_expressions(
    base_radius_mm: float, half_tooth_angle_rad: float, *, right: bool = True
) -> tuple[str, str]:
    """★ **一条齿廓（渐开线）的表达式**（★ 真曲线 · ★ 已含相位）。

    ★★ **推导**（★ 本仓自证 · ★ 不是抄的）：
      · ★ 标准渐开线 `x=rb(cos t+t sin t)` · `y=rb(sin t−t cos t)`
        ★★ 的极角恰为 `inv(t) = t − atan(t)`（★ 随 t **增大**）
      · ★ 而**齿面**要求极角随半径**减小**（★ 齿顶比齿根薄）
        ⇒ ★ 取**镜像**（`y → −y`）：★ 极角 = `−inv(t)`
      · ★ 再转相位 `P`：★ 极角 = `P − inv(t)`
      · ★★ 规范定位：★ 令**分度圆**处 `P − inv(α) = π/(2z)` ⇒ ★ `P = π/(2z) + inv(α)` ✓
      · ★ 实现上等价于**把 t 平移 P**：★ `u = t − P` ⇒
        ★ `x = rb(cos u + t sin u)` · ★ `y = rb(t cos u − sin u)`
      · ★ **左齿廓** = 右齿廓对 x 轴镜像 ⇒ ★ 相位取 `−P`（★ `u = t + P`）✓
    ★★★ **数值已核**（★ 半径 = `rb√(1+t²)` 逐位吻合、极角 = `P − inv(t)` 逐位吻合）✓
    """
    rb_m = float(base_radius_mm)  #: ★ **表达式单位是毫米**（★ 真机扫描法裁决）
    P = float(half_tooth_angle_rad) if right else -float(half_tooth_angle_rad)
    #: ★ 用 `cos(t∓P)` 展开成 `cos t·cos P ± sin t·sin P`（★ 纯 cos/sin/乘/加 —— ★ 已证
    #: 可用）
    cp, sp = math.cos(P), math.sin(P)
    x = "%.12f*((cos(t)*%.12f+sin(t)*%.12f)+t*(sin(t)*%.12f-cos(t)*%.12f))" % (
        rb_m,
        cp,
        sp,
        cp,
        sp,
    )
    y = "%.12f*(t*(cos(t)*%.12f+sin(t)*%.12f)-(sin(t)*%.12f-cos(t)*%.12f))" % (
        rb_m,
        cp,
        sp,
        cp,
        sp,
    )
    return x, y


def trochoid_flank_expressions(
    *,
    pitch_radius_mm: float,
    dedendum_mm: float,
    tool_tip_radius_mm: float,
    base_angle_rad: float,
    module_mm: float,
    pressure_angle_rad: float,
    right: bool = True,
) -> tuple[str, str]:
    """★ **一条齿根过渡（摆线）的表达式**（★ 真曲线 · ★ 已含相位 · ★ 含 `u_c`）。

    ★★ **必须传 `module_mm` / `pressure_angle_rad`** —— ★ 它们决定**刀顶圆角中心偏移** `u_c`
      ⇒ ★★★ **不传就没有标准齿根**（★ 见 `trochoid_xy_mm` 的长注）✗

    ★ 摆线原始极角随 φ **增大**；★ 右齿根用 `+base_angle`、★ 左齿根用 `−base_angle`，
      ★★ 使它与**齿廓在基圆处**相接 ✓

    ★★ **表达式里的 `φ` 用 `u_c + r·φ`**（★ 修正项）——
      ★ 展开成 SolidWorks 能算的形式：★ `u_c + r*t` ✓
    """
    r = float(pitch_radius_mm)
    hf = float(dedendum_mm)
    rho = float(tool_tip_radius_mm)
    a = hf - rho
    #: ★★★ **标准齿条的刀顶圆角中心偏移**（★ 修正项 · ★ 缺它就接不上渐开线）
    u_c = tool_tip_arc_offset_mm(module_mm, pressure_angle_rad, hf, rho)
    #: ★ 相位用 `t + P` 形式（★ 摆线的角度参数与 t 同向）
    P = float(base_angle_rad) if right else -float(base_angle_rad)
    #: ★ `v = u_c + r·t` ⇒ ★ 表达式里写成 `(u_c+r*t)`
    ve = "(%.12f+%.12f*t)" % (u_c, r)
    sq = "%.12f+%s*%s" % (a * a, ve, ve)
    x = (
        "%.12f*cos(t+%.12f)+%s*sin(t+%.12f)+%.12f*(-%.12f*cos(t+%.12f)"
        "+%s*sin(t+%.12f))/sqrt(%s)" % (r - a, P, ve, P, rho, a, P, ve, P, sq)
    )
    y = (
        "%.12f*sin(t+%.12f)-%s*cos(t+%.12f)+%.12f*(-%.12f*sin(t+%.12f)"
        "-%s*cos(t+%.12f))/sqrt(%s)" % (r - a, P, ve, P, rho, a, P, ve, P, sq)
    )
    return x, y


def trochoid_x_expression(
    *,
    pitch_radius_mm: float,
    dedendum_mm: float,
    tool_tip_radius_mm: float,
    module_mm: float,
    pressure_angle_rad: float,
) -> str:
    """★ 摆线齿根 x(φ) 的表达式（★ 含 `sqrt` + `u_c` 修正 · ★ 单位毫米）。"""
    return trochoid_flank_expressions(
        pitch_radius_mm=pitch_radius_mm,
        dedendum_mm=dedendum_mm,
        tool_tip_radius_mm=tool_tip_radius_mm,
        module_mm=module_mm,
        pressure_angle_rad=pressure_angle_rad,
        base_angle_rad=0.0,
        right=True,
    )[0]


def trochoid_y_expression(
    *,
    pitch_radius_mm: float,
    dedendum_mm: float,
    tool_tip_radius_mm: float,
    module_mm: float,
    pressure_angle_rad: float,
) -> str:
    """★ 摆线齿根 y(φ) 的表达式（★ 含 `sqrt` + `u_c` 修正 · ★ 单位毫米）。"""
    return trochoid_flank_expressions(
        pitch_radius_mm=pitch_radius_mm,
        dedendum_mm=dedendum_mm,
        tool_tip_radius_mm=tool_tip_radius_mm,
        module_mm=module_mm,
        pressure_angle_rad=pressure_angle_rad,
        base_angle_rad=0.0,
        right=True,
    )[1]
