"""轴族：需求 → 参数 + 溯源表（纯计算，不碰 COM）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 公式:   本机 mech-design 知识库 design_rules.yaml 的 `shaft` 节
#           d ≥ A × (P/n)^(1/3)，A_values = {45钢:118, 40Cr:108, Q235:135, 20钢:130}
#         等价扭矩式：d = (16T/(π·τ_allow))^(1/3)；A=118 ⟺ τ_allow ≈ 29.6 MPa
# 阶梯:   design_rules.yaml `shaft.step_ratio.shoulder_height` = "0.07d + 3~5"
# 标准径: GB/T 2822 标准尺寸系列（10,12,14,16,18,20,22,25,28,30,32,35,38,40…）
# 坑:     `工作流W1_从需求到交付做一根轴.md` 记的实测错误 ——
#           「ke = 1/Kf 写成 ×Kf → Se 算出 349MPa（比试件 302 还高，荒谬）」
#         本模块不做疲劳校核（属未覆盖项），但把这条写进 warnings 提醒调用方。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

#: design_rules.yaml `shaft.diameter_estimate.A_values`
A_VALUES: dict[str, float] = {
    "45钢": 118.0,
    "40Cr": 108.0,
    "Q235": 135.0,
    "20钢": 130.0,
}

#: GB/T 2822 标准直径系列（常用段）
STD_DIAMETERS = [
    10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42,
    45, 48, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100,
]

#: 冲击系数（无国标规定，工程惯例；写进 evidence 而不是假装是标准）
SHOCK_FACTORS = {"none": 1.0, "light": 1.2, "heavy": 1.5}

SOURCES = {"问", "算", "选", "查", "锁", "假设"}


@dataclass(frozen=True)
class ShaftRequest:
    """轴的输入。前两个必答。"""
    torque_nm: float                 # 传递扭矩
    length_mm: float                 # 轴总长
    material: str = "45钢"
    shock: str = "none"              # none / light / heavy
    stepped: bool = True             # 是否做阶梯轴
    step_ratio: float = 0.4          # 第一段占总长比例


@dataclass(frozen=True)
class Row:
    key: str
    meaning: str
    value: str
    source: str
    evidence: str
    how_to_change: str


@dataclass
class ShaftDerivation:
    ok: bool
    request: ShaftRequest
    rows: list[Row] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)
    #: 几何量（毫米），供 plan_shaft 用
    d1_mm: float = 0.0
    d2_mm: float = 0.0
    l1_mm: float = 0.0
    l2_mm: float = 0.0


def _snap_up(d: float) -> int:
    for s in STD_DIAMETERS:
        if s >= d:
            return s
    return STD_DIAMETERS[-1]


def derive_shaft(req: ShaftRequest) -> ShaftDerivation:
    """需求 → 轴的直径与分段 + 溯源表。"""
    diag: list[str] = []
    rows: list[Row] = []

    if req.torque_nm <= 0:
        return ShaftDerivation(False, req, diagnostics=["扭矩必须 > 0"])
    if req.length_mm <= 0:
        return ShaftDerivation(False, req, diagnostics=["轴长必须 > 0"])
    if req.material not in A_VALUES:
        return ShaftDerivation(
            False, req,
            diagnostics=[f"材料 {req.material} 不在 A 值表里（可选：{'/'.join(A_VALUES)}）"])
    if req.shock not in SHOCK_FACTORS:
        return ShaftDerivation(
            False, req,
            diagnostics=[f"冲击工况 {req.shock} 非法（可选：{'/'.join(SHOCK_FACTORS)}）"])

    A = A_VALUES[req.material]
    k = SHOCK_FACTORS[req.shock]

    # ── 直径：d = A·(T/9550)^(1/3)，再乘冲击系数 ──
    d_calc = A * (req.torque_nm / 9550.0) ** (1.0 / 3.0) * k
    d_std = _snap_up(d_calc)

    # 反推等效许用切应力，作为「这个 A 值意味着什么」的交叉校验
    tau_equiv = 16000.0 * req.torque_nm / (math.pi * d_calc ** 3) if d_calc > 0 else 0.0
    if not (10.0 <= tau_equiv <= 60.0):
        diag.append(
            f"等效许用切应力 {tau_equiv:.1f} MPa 超出常见范围 10~60 —— A 值可能选错")

    # ── 阶梯 ──
    shoulder = 0.07 * d_std + 4.0          # design_rules: 0.07d + 3~5，取中间值 4
    d2_std = _snap_up(d_std + 2.0 * shoulder) if req.stepped else d_std
    l1 = req.length_mm * req.step_ratio if req.stepped else 0.0
    l2 = req.length_mm - l1

    rows += [
        Row("T", "传递多大扭矩", f"{req.torque_nm:g} N·m", "问",
            "用户回答：要传多大劲", "改它 → 直径跟着变（1/3 次方，变化平缓）"),
        Row("L", "轴多长", f"{req.length_mm:g} mm", "问",
            "用户回答：轴总长", "只影响长度与长径比，不影响直径"),
        Row("material", "材料牌号", req.material, "问",
            "用户回答：材料", "换材料 → A 值变 → 直径变"),
        Row("shock", "冲击工况", req.shock, "问",
            "用户回答：是否有冲击（无国标规定，工程惯例）",
            "有冲击 → 直径放大"),
        Row("A", "材料系数（扭转强度经验式）", f"{A:g}", "查",
            "design_rules.yaml shaft.diameter_estimate.A_values",
            "该系数由材料定，不单独改"),
        Row("d_calc", "按扭转强度算出的最小直径", f"{d_calc:.2f} mm", "算",
            f"d = A·(T/9550)^(1/3)·k = {A:g}·({req.torque_nm:g}/9550)^(1/3)·{k:g}",
            "改 T / 材料 / 冲击系数都会让它变"),
        Row("d1", "轴颈直径（已取标准系列）", f"{d_std} mm", "选",
            "GB/T 2822 标准直径系列，向上取整", "可直接锁定为你有的轴承内径"),
        Row("d2", "轴肩直径", f"{d2_std} mm", "算",
            f"d2 = d1 + 2×(0.07·d1+4) = {d_std}+2×{shoulder:.1f}", "改 d1 它会跟着变"),
        Row("L1", "第一段长度", f"{l1:.1f} mm", "算",
            f"L1 = L × {req.step_ratio:g}", "改分段比例"),
        Row("L2", "第二段长度", f"{l2:.1f} mm", "算", "L2 = L − L1", "改分段比例"),
        Row("tau_equiv", "等效许用切应力（交叉校验）", f"{tau_equiv:.1f} MPa", "算",
            "由 A 值反推，与 τ_allow 常见区间 10~60 MPa 比对", "超范围说明 A 值不对"),
    ]

    uncovered = [
        "疲劳校核：未做（需 Kt/Kf/ka/kb，且无表面加工与几何细节）",
        "弯曲校核：未做（需支点跨距与径向载荷）",
        "键槽削弱：未做（开槽后 W 会减小，需按 GB/T 1096 重算）",
        "公差与表面粗糙度：未定",
        "轴承与密封位配合：未选",
    ]

    return ShaftDerivation(
        ok=not diag, request=req, rows=rows, diagnostics=diag, uncovered=uncovered,
        d1_mm=float(d_std), d2_mm=float(d2_std),
        l1_mm=l1, l2_mm=l2,
    )


def render(d: ShaftDerivation) -> str:
    if not d.ok:
        return "\n".join(["【无解】"] + d.diagnostics)
    out = ["| # | 参数 | 含义 | 值 | 来源 | 依据 | 你能怎么改 |",
           "|---|---|---|---|---|---|---|"]
    for n, r in enumerate(d.rows, 1):
        out.append(f"| {n} | {r.key} | {r.meaning} | {r.value} | {r.source} | "
                   f"{r.evidence} | {r.how_to_change} |")
    out.append("")
    out.append("【未覆盖】")
    out.extend("  ✗ " + u for u in d.uncovered)
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(render(derive_shaft(ShaftRequest(torque_nm=120.0, length_mm=300.0))))
