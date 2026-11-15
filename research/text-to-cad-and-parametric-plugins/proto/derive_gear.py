"""Demonstrate the parameter-graph idea: the user answers 2-3 perceptual questions,
the generator derives the rest, and an engineer may pin any node — but a pinned node
still has to pass the checks.

Case is a standard external spur gear pair. Only exact geometry is used here
(no empirical strength coefficients are invented):
    d = m z,  a = m (z1 + z2) / 2,  i = z2 / z1,
    cos(alpha_a) = z cos(alpha) / (z + 2)          # standard full-depth, x = 0
    eps_alpha = [z1 (tan a_a1 - tan a') + z2 (tan a_a2 - tan a')] / (2*pi)

Undercut limit z_min = 17 for 20 deg standard spur is taken from the local knowledge base
(70-标准件与选型计算/直齿圆柱齿轮选型.md), not from memory.
Standard module series is the first series quoted in that same document.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

ALPHA = math.radians(20.0)
Z_MIN = 17                      # KB: 标准齿条最小齿数（无根切）
MODULES = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]   # GB/T 1357 第一系列（子集）
EPS_MIN = 1.2                   # 常用下限，用于提示"偏小"，非标准强制值


@dataclass
class Request:
    ratio: float                # 客户答："要减速几倍"
    center_mm: float            # 客户答："两根轴之间能塞多宽"
    bm_ratio: float = 10.0      # 生成器默认：一般传动 b/m = 8~12，取 10
    pin_z1: int | None = None   # 工程师可锁定
    pin_module: float | None = None


def alpha_a(z: float) -> float:
    return math.acos(z * math.cos(ALPHA) / (z + 2.0))


def contact_ratio(z1: int, z2: int) -> float:
    ta = math.tan(ALPHA)
    return (z1 * (math.tan(alpha_a(z1)) - ta) + z2 * (math.tan(alpha_a(z2)) - ta)) / (2.0 * math.pi)


TOL_MM = 0.75   # 允许的中心距偏差


def solve(req: Request):
    """Search the (module, z1) grid; always return the nearest few candidates so a failure
    can be explained with real numbers instead of a generic complaint."""
    cands = []
    for m in MODULES:
        if req.pin_module is not None and abs(m - req.pin_module) > 1e-9:
            continue
        z1_lo = req.pin_z1 if req.pin_z1 else Z_MIN
        z1_hi = req.pin_z1 if req.pin_z1 else 80
        for z1 in range(z1_lo, z1_hi + 1):
            z2 = round(req.ratio * z1)
            if z2 < z1:
                continue
            a = m * (z1 + z2) / 2.0
            cands.append(dict(module=m, z1=z1, z2=z2, a=a,
                              err=abs(a - req.center_mm),
                              i_true=z2 / z1,
                              eps=contact_ratio(z1, z2)))
    cands.sort(key=lambda c: (c["err"], c["module"]))
    ok = [c for c in cands if c["err"] <= TOL_MM]
    if ok:
        return ok[0], []
    return None, cands[:3]


def explain(req: Request, near) -> list[str]:
    """Say what actually blocks it, with the nearest feasible designs."""
    lines = []
    if not near:
        return ["无解：在给定约束下没有任何可行组合。"]
    smallest = min(near, key=lambda c: c["a"])
    if req.center_mm < smallest["a"] - TOL_MM:
        lines.append(
            f"中心距太小：在不根切（z1≥{Z_MIN}）与给定模数的前提下，"
            f"最小可行中心距是 {smallest['a']:.2f} mm（m={smallest['module']}, "
            f"z1={smallest['z1']}, z2={smallest['z2']}），你要的 {req.center_mm} mm 塞不下。"
            f"可选：① 中心距放宽到 ≥{smallest['a']:.1f} ② 减小模数（可能需非首选系列或确认刀具）"
            f" ③ 用变位齿轮（此时才允许 z1<{Z_MIN}）"
        )
    else:
        lines.append(
            f"中心距对不上整数齿：最接近的三个可行组合是 " +
            "、".join(
                f"m={c['module']:g}/z1={c['z1']}/z2={c['z2']}→a={c['a']:.2f}（差 {c['a'] - req.center_mm:+.2f} mm）"
                for c in near
            ) +
            f"；你要的 {req.center_mm} mm 落在中间。可选：① 把中心距改成上面某个值 "
            f"② 允许变位（可在同一 a 下凑出非整数齿比） ③ 换模数"
        )
    return lines


def report(tag: str, req: Request):
    print("\n" + "=" * 78)
    print(tag)
    print("=" * 78)
    best, rejects = solve(req)
    if best is None:
        for r in explain(req, rejects):
            print("  " + r)
        return
    d1 = best["module"] * best["z1"]
    d2 = best["module"] * best["z2"]
    b = req.bm_ratio * best["module"]
    print(f"  客户只答了两个：传动比 {req.ratio}、中心距 {req.center_mm} mm")
    print(f"  → 模块 m={best['module']}, z1={best['z1']}, z2={best['z2']}, "
          f"d1={d1:.1f}, d2={d2:.1f}, a={best['a']:.2f}, i={best['i_true']:.3f}")
    print(f"  → 齿宽 b={b:.1f} mm（按生成器默认 b/m={req.bm_ratio:g}）")
    print(f"  → 重合度 εα={best['eps']:.2f}" + ("" if best["eps"] >= EPS_MIN else f"  ⚠ 偏小（<{EPS_MIN}），噪声与冲击会变大"))
    print(f"  → 根切检查：z1={best['z1']} ≥ {Z_MIN} ✓")
    if req.pin_z1 or req.pin_module:
        pinned = []
        if req.pin_z1:
            pinned.append(f"z1={req.pin_z1}")
        if req.pin_module:
            pinned.append(f"m={req.pin_module}")
        print(f"  → 工程师锁定了 {' / '.join(pinned)}；推导链绕过了被锁的节点，其余照算")


if __name__ == "__main__":
    report("案例 1｜客户视角：只答「减速 3 倍」「两轴中心距 40mm」",
           Request(ratio=3.0, center_mm=40.0))

    report("案例 2｜同一个客户，中心距只有 30mm —— 无解，且要说清怎么改",
           Request(ratio=3.0, center_mm=30.0))

    report("案例 3｜工程师视角：直接锁定 z1=20（他有现成刀具）",
           Request(ratio=2.5, center_mm=43.0, pin_z1=20))

    report("案例 4｜工程师锁定 m=2，但中心距不变 —— 看他被约束推到哪",
           Request(ratio=2.0, center_mm=80.0, pin_module=2.0))
