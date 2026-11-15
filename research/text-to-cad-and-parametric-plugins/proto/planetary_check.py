"""Assembly-level check for a single-stage NGW planetary gear set.

Why this file exists: each of sun / planet / ring can be a perfectly valid gear on its own
and the set still cannot be assembled. The four coupling conditions below are the reason the
sub-system layer cannot be "solved independently and glued together".

Conditions (standard, x = 0, same module on all three members):
  1. 同心  z_r = z_s + 2 z_p
  2. 传动比 i = 1 + z_r / z_s          （内齿圈固定，太阳轮输入，行星架输出）
  3. 装配  (z_s + z_r) / n_p  必须整除
  4. 邻接  (z_s + z_p) * sin(pi / n_p) > z_p + 2   （相邻行星轮齿顶不相碰）

z_min = 17 for the external sun/planet mesh comes from the local knowledge base
(70-标准件与选型计算/直齿圆柱齿轮选型.md), not from memory.
"""
from __future__ import annotations

import math

Z_MIN = 17


def ratios(zs: int, np_: int) -> dict:
    zr = 4 * zs if False else None  # placeholder, never used
    return {}


def check(zs: int, zp: int, zr: int, np_: int, i_target: float) -> dict:
    """Return per-condition verdicts plus the resulting ratio."""
    i_actual = 1.0 + zr / zs
    conc = abs(zr - (zs + 2 * zp)) < 1e-9
    ratio_ok = abs(i_actual - i_target) < 1e-6
    asm_val = (zs + zr) / np_
    asm_ok = abs(asm_val - round(asm_val)) < 1e-9
    adj_lhs = (zs + zp) * math.sin(math.pi / np_)
    adj_rhs = zp + 2
    adj_ok = adj_lhs > adj_rhs
    undercut_ok = zs >= Z_MIN and zp >= Z_MIN
    return dict(
        z_s=zs, z_p=zp, z_r=zr, n_p=np_, i=i_actual,
        conc=conc, ratio_ok=ratio_ok,
        asm_value=asm_val, asm_ok=asm_ok,
        adj_lhs=adj_lhs, adj_rhs=adj_rhs, adj_ok=adj_ok,
        undercut_ok=undercut_ok,
        all_ok=all([conc, ratio_ok, asm_ok, adj_ok, undercut_ok]),
    )


def build(zs: int, i_target: float) -> tuple[int, int]:
    """From (z_s, i) derive the planet and ring counts by the concentric condition."""
    zr = round((i_target - 1.0) * zs)
    if abs((zr / zs) - (i_target - 1.0)) > 1e-9:
        return zr, -1
    rem = zr - zs
    if rem % 2:
        return zr, -1          # z_p must be an integer
    return zr, rem // 2


def scan(i_target: float, np_: int, z_hi: int = 60) -> list[dict]:
    out = []
    for zs in range(Z_MIN, z_hi + 1):
        zr, zp = build(zs, i_target)
        if zp < 0:
            continue
        out.append(check(zs, zp, zr, np_, i_target))
    return out


def show(tag: str, r: dict) -> None:
    mark = lambda b: "✓" if b else "✗"
    print(f"  {tag}")
    print(f"    z_s={r['z_s']}  z_p={r['z_p']}  z_r={r['z_r']}  n_p={r['n_p']}  i={r['i']:.3f}")
    print(f"    同心 {mark(r['conc'])}   档位/传动比 {mark(r['ratio_ok'])}   "
          f"不根切 {mark(r['undercut_ok'])}")
    print(f"    装配 {mark(r['asm_ok'])}  (z_s+z_r)/n_p = {r['asm_value']:.3f}"
          + ("" if r["asm_ok"] else "  ← 不是整数，装不上"))
    print(f"    邻接 {mark(r['adj_ok'])}  (z_s+z_p)sin(π/n_p)={r['adj_lhs']:.2f} "
          f"vs z_p+2={r['adj_rhs']:.2f}" + ("" if r["adj_ok"] else "  ← 行星轮互相碰到"))
    print(f"    ⇒ {'可以装配' if r['all_ok'] else '不能装配'}")


if __name__ == "__main__":
    print("=" * 78)
    print("案例 A｜客户要「减速 5 倍的 planetary」，最省的齿数 + 最常见的 3 个行星轮")
    print("=" * 78)
    zr, zp = build(20, 5.0)
    show("z_s=20, i=5 ⇒ z_r=80, z_p=30, 三行星轮", check(20, zp, zr, 3, 5.0))
    print("    每个齿轮单独看都是合法的标准直齿；配不成套，卡在装配条件上。\n")

    print("=" * 78)
    print("案例 B｜同样减速 5 倍，改成 4 个行星轮")
    print("=" * 78)
    show("z_s=20, i=5 ⇒ z_r=80, z_p=30, 四行星轮", check(20, zp, zr, 4, 5.0))

    print("\n" + "=" * 78)
    print("案例 C｜客户坚持要 3 个行星轮 —— 反推齿数必须满足什么")
    print("=" * 78)
    good = [r for r in scan(5.0, 3) if r["all_ok"]]
    for r in good[:4]:
        show("可行解", r)
    print("    ⇒ 规律：i=5 且 3 行星轮时，z_s 必须是 6 的倍数（既要 (z_s+z_r)=5z_s 被 3 整除，")
    print("      又要 z_p=1.5z_s 是整数 ⇒ z_s 被 6 整除）。这就是「分系统各自能算」推不出来的东西。\n")

    print("=" * 78)
    print("案例 D｜减速 4 倍，同样 4 个行星轮 vs 5 个行星轮")
    print("=" * 78)
    zr4, zp4 = build(24, 4.0)
    show(f"z_s=24, i=4 ⇒ z_r={zr4}, z_p={zp4}, 4 行星轮", check(24, zp4, zr4, 4, 4.0))
    show(f"z_s=24, i=4 ⇒ z_r={zr4}, z_p={zp4}, 5 行星轮", check(24, zp4, zr4, 5, 4.0))

    print("\n" + "=" * 78)
    print("案例 E｜扫描：i=5，不同 n_p 各自有多少可行 z_s（z_s ≤ 60）")
    print("=" * 78)
    for np_ in (2, 3, 4, 5, 6):
        ok = [r["z_s"] for r in scan(5.0, np_) if r["all_ok"]]
        print(f"  n_p={np_}: {len(ok):2d} 个可行  前几个 z_s = {ok[:8]}")
    print()
    print("  ★ 为什么 n_p=5 和 6 是 0 个：i=5 ⇒ z_p = 1.5 z_s，邻接条件变成")
    print("       2.5 z_s · sin(π/n_p) > 1.5 z_s + 2  ⇒  sin(π/n_p) > 0.6 + 0.8/z_s")
    print("     sin(π/5)=0.588、sin(π/6)=0.500，都 ≤ 0.6 —— 与 z_s 无关，永远不成立。")
    print("     不是「没搜到」，是「几何上不可能」。")
