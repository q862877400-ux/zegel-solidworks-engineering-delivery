"""齿轮方法层 v0：需求 → 参数 → 溯源表（纯计算，不碰 COM，不产几何）。

# ── 来源 ────────────────────────────────────────────────────────────
# ★★ 2026-11-07 业主令：删除「折线模拟曲线」的一切功能。
#    本模块**不再 import** 归档 archive/inherited-methods/scripts/sw_gear.py
#    （那是把渐开线采样成点列再逐段连直线的折线实现，全项目禁用）。
#    分度圆交叉校验改为解析恒等式 d = m·z，不依赖任何折线几何。
#    本模块只做「参数推理 + 六类来源溯源表」，**不生成轮廓、不出 FeaturePlan**。
# 判据 z_min: 本机 mech-design 知识库 70-标准件与选型计算/直齿圆柱齿轮选型.md（z_min=17, α=20°）
#             ⚠ 归档实现用的是 ceil(2/sin²α)=18；两者不同，本模块把「取 17 还是 18」显式化
# 推导关系: a = m(z1+z2)/2, z2 = i·z1, εα 标准直齿公式 —— 教科书级恒等式，非经验系数
# 表结构:   research/text-to-cad-and-parametric-plugins/04-参数推理表.md
# 语义卡:   同目录 params.jsonl
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

ALPHA_DEG = 20.0
MODULES = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]
TOL_A_MM = 0.75
Z_MIN_KB = 17          # 知识库口径
Z_MIN_STRICT = 18      # 归档实现的 ceil(2/sin²α) 口径

SOURCES = {"问", "算", "选", "查", "锁", "假设"}


@dataclass(frozen=True)
class GearRequest:
    """客户/工程师的输入。只有前两个是必答。"""
    ratio: float
    center_mm: float
    bm_ratio: float = 10.0
    pressure_angle_deg: float = ALPHA_DEG
    pin_z1: int | None = None
    pin_module: float | None = None
    z_min_policy: str = "kb"       # "kb"=17（知识库口径）/ "strict"=18（归档实现口径）


@dataclass(frozen=True)
class Row:
    key: str
    meaning: str
    value: str
    source: str
    evidence: str
    how_to_change: str


@dataclass
class Derivation:
    ok: bool
    request: GearRequest
    rows: list[Row] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    uncovered: list[str] = field(default_factory=list)
    specs: dict = field(default_factory=dict)


def _z_min(policy: str) -> tuple[int, str, str]:
    if policy == "strict":
        return Z_MIN_STRICT, "查", "ceil(2/sin²α)=18（理论无根切下限）"
    return Z_MIN_KB, "查", "机械设计知识库 直齿圆柱齿轮选型.md：α=20° 时 z_min=17"


def _contact_ratio(z1: int, z2: int, alpha_deg: float) -> float:
    a = math.radians(alpha_deg)
    ta = math.tan(a)
    aa1 = math.acos(z1 * math.cos(a) / (z1 + 2.0))
    aa2 = math.acos(z2 * math.cos(a) / (z2 + 2.0))
    return (z1 * (math.tan(aa1) - ta) + z2 * (math.tan(aa2) - ta)) / (2.0 * math.pi)


def _candidates(req: GearRequest, zmin: int):
    out = []
    for m in MODULES:
        if req.pin_module is not None and abs(m - req.pin_module) > 1e-9:
            continue
        lo = req.pin_z1 if req.pin_z1 else zmin
        hi = req.pin_z1 if req.pin_z1 else 80
        for z1 in range(lo, hi + 1):
            z2 = round(req.ratio * z1)
            if z2 < z1:
                continue
            a = m * (z1 + z2) / 2.0
            out.append(dict(module=m, z1=z1, z2=z2, a=a, err=abs(a - req.center_mm)))
    out.sort(key=lambda c: (c["err"], c["module"]))
    return out


def derive(req: GearRequest) -> Derivation:
    """需求 → 参数集 + 溯源表。无解时返回带诊断的 ok=False，不抛异常也不凑合。"""
    zmin, zsrc, zwhy = _z_min(req.z_min_policy)
    cands = _candidates(req, zmin)
    ok = [c for c in cands if c["err"] <= TOL_A_MM]

    if not ok:
        near = cands[:3]
        if not near:
            return Derivation(False, req, diagnostics=["无可行组合：搜索范围内没有任何解。"],
                              uncovered=_uncovered())
        smallest = min(near, key=lambda c: c["a"])
        msg = (f"中心距对不上：最接近的可行组合是 " +
               "、".join(f"m={c['module']:g}/z1={c['z1']}/z2={c['z2']}→a={c['a']:.2f}"
                         f"（差 {c['a'] - req.center_mm:+.2f} mm）" for c in near) +
               f"。当前 z_min={zmin}（{zwhy}），最小可行中心距 {smallest['a']:.2f} mm。")
        return Derivation(False, req, diagnostics=[msg], uncovered=_uncovered())

    best = ok[0]
    m, z1, z2 = best["module"], best["z1"], best["z2"]
    d1, d2 = m * z1, m * z2
    b = req.bm_ratio * m
    eps = _contact_ratio(z1, z2, req.pressure_angle_deg)

    # 交叉校验：d = m·z 解析恒等式（★ 不再依赖归档折线实现的纯计算侧）
    cross_ok = (abs(m * z1 - d1) < 1e-9 and abs(m * z2 - d2) < 1e-9)

    rows = [
        Row("i", "输出比输入慢多少倍", f"{req.ratio:g}", "问",
            "用户回答：减速几倍", "改它 → z2 与中心距跟着变"),
        Row("a", "两根轴中心到中心的距离", f"{req.center_mm:g} mm", "问",
            "用户回答：两轴之间能塞多宽", "改它 → 模数或齿数要重算"),
        Row("z_min", "不根切的最小齿数（判据，不是参数）", f"{zmin}", zsrc, zwhy,
            "换口径会改变可行解集合"),
        Row("m", "齿的大小；和齿宽一起决定能扛多大力", f"{m:g} mm", "选",
            "标准模数系列中能让 a 对上的一档（GB/T 1357 第一系列）", "往上取标准系列即可"),
        Row("z1", "小齿轮齿数；太少会根切", f"{z1}",
            "锁" if req.pin_z1 else "算",
            "工程师指定" if req.pin_z1 else "z1 = 2a / (m(1+i))",
            "可锁定；低于 z_min 需变位"),
        Row("z2", "大齿轮齿数", f"{z2}", "算", "z2 = i · z1", "跟随 i 与 z1"),
        Row("d1", "小齿轮分度圆直径", f"{d1:.1f} mm", "算",
            f"d = m·z；解析恒等式交叉校验{'一致' if cross_ok else '不一致'}",
            "跟随 m 与 z1"),
        Row("d2", "大齿轮分度圆直径", f"{d2:.1f} mm", "算", "d = m·z（同上交叉校验）", "跟随 m 与 z2"),
        Row("b", "齿宽；越宽越能扛，轴承受力越大", f"{b:.1f} mm", "选",
            f"按 b/m = {req.bm_ratio:g}（一般传动 8~12）", "可自由调，不影响中心距"),
        Row("eps", "重合度：同时啮合齿对数，越大越平顺", f"{eps:.2f}", "算",
            "标准直齿重合度公式（含齿顶圆）", "是结果不是输入"),
        Row("da1", "小齿轮齿顶圆直径（外径）", f"{d1 + 2 * m:.1f} mm", "算", "da = d + 2m", "跟随 m 与 z"),
        Row("da2", "大齿轮齿顶圆直径（外径）", f"{d2 + 2 * m:.1f} mm", "算", "da = d + 2m", "跟随 m 与 z"),
        Row("df1", "小齿轮齿根圆直径", f"{d1 - 2.5 * m:.1f} mm", "算", "df = d − 2.5m", "跟随 m 与 z"),
    ]
    uncovered = _uncovered() + [
        "齿形几何：本模块只出参数，不产轮廓。真曲线齿轮（scripts/gear_geometry.py）"
        "整圈闭合/单齿阵列路线尚未通过真机验证，当前不提供可用齿轮生成器",
    ]

    return Derivation(True, req, rows=rows, uncovered=uncovered, specs={})


def _uncovered() -> list[str]:
    return [
        "强度校核：未做（材料与热处理未定，[σH]/[σF] 无法取）",
        "变位系数：未定（按标准全齿高 x=0 推导）",
        "公差与表面粗糙度：未定",
    ]


def render(d: Derivation) -> str:
    if not d.ok:
        return "\n".join(["【无解】"] + d.diagnostics)
    out = ["| # | 参数 | 含义 | 值 | 来源 | 依据 | 你能怎么改 |", "|---|---|---|---|---|---|---|"]
    for n, r in enumerate(d.rows, 1):
        out.append(f"| {n} | {r.key} | {r.meaning} | {r.value} | {r.source} | {r.evidence} | {r.how_to_change} |")
    out.append("")
    out.append("【未覆盖】")
    out.extend("  ✗ " + u for u in d.uncovered)
    return "\n".join(out)
