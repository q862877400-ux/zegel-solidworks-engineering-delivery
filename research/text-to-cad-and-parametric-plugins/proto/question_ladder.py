"""Demonstrate audience-adaptive parameter elicitation: probe with the engineering term,
degrade on "不知道", decide-then-disclose on "你定", and render the resolved value back
in the language of the rung the user actually answered on.

All material numbers come from the local mech-design knowledge base, not from memory:
  - 材料选型.md  (E: 钢 210 / 铝 70 GPa; ρE 排序)
  - material_db.yaml (45钢 σs=355 ρ=7.85; 6061-T6 σs=276 E=69 ρ=2.70; ZL101 σs=145 E=70 ρ=2.70)
304 stainless has NO mechanical entry in that DB, which is exercised as the "missing data" path.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# ── 材料库（来自本机 mech-design 知识库）────────────────────────────────
MATERIALS = {
    "45钢": dict(rho=7.85, E=210_000.0, sy=355.0, family="钢", source="material_db.yaml + 材料选型.md(E=210)"),
    "6061-T6": dict(rho=2.70, E=69_000.0, sy=276.0, family="铝", source="material_db.yaml"),
    "ZL101": dict(rho=2.70, E=70_000.0, sy=145.0, family="铝", source="material_db.yaml"),
}

# 工艺常用板厚序列（车间序列，非核对过的标准，落地前要按厂内料单替换）
SHEET_T = [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0]


@dataclass
class Case:
    """悬臂板端部受集中力：L 悬臂长, b 板宽, F 端部载荷。"""
    F_n: float = 200.0
    L_mm: float = 150.0
    b_mm: float = 30.0
    delta_limit_mm: float = 1.0
    safety_factor: float = 2.0


def t_for_stiffness(mat: dict, c: Case) -> float:
    """δ = F L³/(3 E I), I = b t³/12  →  t = (4 F L³/(E b δ))^(1/3)"""
    return (4.0 * c.F_n * c.L_mm**3 / (mat["E"] * c.b_mm * c.delta_limit_mm)) ** (1.0 / 3.0)


def t_for_strength(mat: dict, c: Case) -> float:
    """σ = 6 F L/(b t²) ≤ σy/SF  →  t = sqrt(6 F L/(b σ_allow))"""
    sigma_allow = mat["sy"] / c.safety_factor
    return math.sqrt(6.0 * c.F_n * c.L_mm / (c.b_mm * sigma_allow))


def check(mat: dict, c: Case, t: float) -> dict:
    I = c.b_mm * t**3 / 12.0
    delta = c.F_n * c.L_mm**3 / (3.0 * mat["E"] * I)
    sigma = 6.0 * c.F_n * c.L_mm / (c.b_mm * t**2)
    return dict(
        t_mm=t,
        delta_mm=delta,
        sigma_mpa=sigma,
        sf=mat["sy"] / sigma,
        mass_g=mat["rho"] * (c.b_mm * c.L_mm * t) / 1000.0,
    )


def standardise(t_req: float) -> float:
    for t in SHEET_T:
        if t >= t_req:
            return t
    return SHEET_T[-1]


# ── 语义卡：同一参数的多级措辞 ───────────────────────────────────────────
THICKNESS_LADDER = {
    4: "壁厚 t 取多少？给个数值，我按 δ≤{d}mm、SF≥{sf} 校核。",
    3: "按强度算要 {t_s:.1f} mm，按刚度算要 {t_f:.1f} mm，你要哪一个当判据？",
    2: "这东西装上以后，你更在意「按下去别软」，还是「别被压坏」？",
    1: "要不要我按最常用的做法定？（我会告诉你我定了多厚、为什么）",
    0: "我直接按最常用配置定了，最后给你一张「我替你决定了什么」的清单。",
}

MATERIAL_LADDER = {
    4: "材料牌号？（如 304 / 6061-T6 / 45钢；有牌号我直接取 σs、E）",
    3: "要碳钢、不锈钢，还是铝合金？",
    2: "这零件会碰水生锈吗？会不会要求轻一点？",
    1: "用在室内干燥的地方，还是一直见水/户外？",
    0: "我按常规结构钢定了，需要防腐我再改。",
}


def render_customer(material: str, mat: dict, c: Case, r: dict, driver: str) -> str:
    """L2：给后果和可比物，不给公式。"""
    share = 100.0 * r["t_mm"] / c.b_mm
    return (
        f"用 {material} 的话，这块板要做到约 {r['t_mm']:.1f} mm 厚"
        f"（差不多是你这个零件宽度的 {share:.0f}%）。"
        f"装上去以后，{c.F_n:.0f} N 的力压在上面大约会弯 {r['delta_mm']:.2f} mm，"
        f"手按不出软的感觉。这个厚度是按「{driver}」定的。"
    )


def render_engineer(material: str, mat: dict, c: Case, r: dict, driver: str) -> str:
    """L4：给判据和数字。"""
    return (
        f"{material}: t={r['t_mm']:.1f} mm（标准板厚序列取值），"
        f"δ={r['delta_mm']:.3f} mm ≤ {c.delta_limit_mm}, "
        f"σ={r['sigma_mpa']:.1f} MPa, SF={r['sf']:.2f} ≥ {c.safety_factor}, "
        f"m={r['mass_g']:.0f} g；控制项={driver}"
    )


def resolve(material: str, c: Case, requirement: str) -> dict:
    if material not in MATERIALS:
        raise KeyError(
            f"材料库无 {material} 的力学数据 —— 不猜，回去补录或向用户确认牌号"
        )
    mat = MATERIALS[material]
    t_s = t_for_stiffness(mat, c)
    t_f = t_for_strength(mat, c)
    if requirement == "stiffness":
        t_req, driver = t_s, "刚度/挠度"
    elif requirement == "strength":
        t_req, driver = t_f, "强度/不断"
    else:
        t_req, driver = max(t_s, t_f), "两者取大"
    t_std = standardise(t_req)
    r = check(mat, c, t_std)
    r.update(t_req_raw=t_req, t_stiff=t_s, t_strength=t_f)
    return dict(material=material, driver=driver, result=r)


def show(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


if __name__ == "__main__":
    c = Case()

    show("实验 1｜同一块板，换材料：厚度差多少（刚度判据 vs 强度判据）")
    rows = []
    for m in ("45钢", "6061-T6", "ZL101"):
        rs = resolve(m, c, "stiffness")["result"]
        rf = resolve(m, c, "strength")["result"]
        rows.append((m, rs, rf))
        print(f"{m:9s} 刚度控制 t={rs['t_req_raw']:.2f} mm  "
              f"强度控制 t={rf['t_req_raw']:.2f} mm  "
              f"比值 {rs['t_req_raw'] / rf['t_req_raw']:.2f}")

    base = rows[0]
    print("\n相对 45钢 的厚度倍数：")
    for m, rs, rf in rows:
        print(f"  {m:9s} 刚度路线 ×{rs['t_req_raw'] / base[1]['t_req_raw']:.2f}   "
              f"强度路线 ×{rf['t_req_raw'] / base[2]['t_req_raw']:.2f}")

    show("实验 2｜同一个问题，两种受众，两种说法")
    for m in ("45钢", "6061-T6"):
        r = resolve(m, c, "stiffness")
        print("\n[工程师视图 L4] " + render_engineer(m, MATERIALS[m], c, r["result"], r["driver"]))
        print("[客户视图  L2] " + render_customer(m, MATERIALS[m], c, r["result"], r["driver"]))

    show("实验 3｜同一种材料，两种需求判据 → 结论不同（所以「结实」必须先拆开）")
    for req in ("stiffness", "strength"):
        r = resolve("6061-T6", c, req)["result"]
        print(f"  判据={req:10s} t={r['t_mm']:.1f} mm  δ={r['delta_mm']:.2f}  SF={r['sf']:.2f}")

    show("实验 4｜降级链：同一个问题，三种用户，三条路径")
    persona = {
        "A 工程师": "4",     # 直接给数值
        "B 半懂": "不知道",   # 降一级
        "C 委托": "你定",     # 直接定 + 交代
    }
    for name, answer in persona.items():
        level = 4
        transcript = []
        transcript.append(f"系统(L{level}): " + THICKNESS_LADDER[4].format(d=c.delta_limit_mm, sf=c.safety_factor))
        if answer == "不知道":
            level = 2
            transcript.append(f"用户: 不知道")
            transcript.append(f"系统(L{level}): " + THICKNESS_LADDER[2])
            transcript.append("用户: 别软就行")
            req = "stiffness"
            transcript.append("系统: 收到 → 按刚度判据算")
        elif answer == "你定":
            transcript.append("用户: 你定")
            req = "both"
            transcript.append("系统: 我不再问了，按两者取大定。以下是我替你决定的：")
            transcript.append("        · 材料 = 6061-T6（未说明用途，取最通用的铝）")
            transcript.append("        · 判据 = 刚度与强度同时满足（取较大厚度）")
            transcript.append("        · 载荷 = 200 N 静载、无冲击（未提工况，按最轻工况）")
            transcript.append("        · 板厚序列 = 车间常用冷轧板厚（未核对厂内料单）")
            transcript.append("      交付时会原样带上这份清单，你可以逐条推翻。")
        else:
            req = "both"
            transcript.append(f"用户: 按 δ≤{c.delta_limit_mm}、SF≥{c.safety_factor} 来")
        r = resolve("6061-T6", c, req)["result"]
        transcript.append("结果: t=%.1f mm, δ=%.2f mm, SF=%.2f" % (r["t_mm"], r["delta_mm"], r["sf"]))
        print(f"\n--- {name} ---")
        for line in transcript:
            print("  " + line)

    show("实验 5｜数据缺失路径：客户说「不锈钢」")
    try:
        resolve("304", c, "stiffness")
    except KeyError as e:
        print("  " + str(e))
        print("  → 正确动作：不猜 σs，改问「304 还是 316L？要不要焊接？」，并把这族标成待补录")

    show("实验 6｜误读的代价：把「结实」当成强度，实际客户要的是刚度")
    wrong = resolve("6061-T6", c, "strength")["result"]
    right = resolve("6061-T6", c, "stiffness")["result"]
    print(f"  按强度定 t={wrong['t_mm']:.1f} mm → 实际挠度 {wrong['delta_mm']:.2f} mm（客户会觉得软）")
    print(f"  按刚度定 t={right['t_mm']:.1f} mm → 实际挠度 {right['delta_mm']:.2f} mm")
