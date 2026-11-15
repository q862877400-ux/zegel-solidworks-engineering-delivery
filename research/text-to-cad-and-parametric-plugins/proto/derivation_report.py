"""Render the post-dialogue derivation report: every parameter with its one-line meaning,
its value, where the value came from (问/算/选/查/锁/假设), the evidence, and how a
professional can change it.

Imports the solver from derive_gear.py so the numbers cannot drift from the earlier demo.
"""
from __future__ import annotations

from derive_gear import ALPHA, EPS_MIN, Z_MIN, Request, solve

# 来源类型：问=用户答的 · 算=公式推出来的 · 选=在候选里按规则挑的 · 查=查表/查标准
#           锁=工程师指定 · 假设=我替他定的（可推翻）
MEANING = {
    "i": "输出比输入慢多少倍",
    "a": "两根轴中心到中心的距离",
    "m": "齿的大小；它和齿宽一起决定能扛多大力",
    "z1": "小齿轮齿数；太少会根切",
    "z2": "大齿轮齿数",
    "d1": "小齿轮分度圆直径（齿轮的“名义直径”）",
    "d2": "大齿轮分度圆直径",
    "b": "齿宽；越宽越能扛，但轴承受力变大",
    "eps": "重合度：同时啮合的齿对数，越大越平顺、越安静",
    "da1": "小齿轮齿顶圆直径（零件外径）",
    "da2": "大齿轮齿顶圆直径（零件外径）",
    "df1": "小齿轮齿根圆直径",
}

HOWTO = {
    "i": "改它会连带改 z2 与中心距；要单独改 i 就得重算整条链",
    "a": "改它 → 模数或齿数要重算；这是最常被现场约束推翻的一项",
    "m": "改它 → 中心距变或齿数变；往上取标准系列即可",
    "z1": "可直接锁定（有现成刀具时）；<17 会根切，需变位",
    "z2": "跟随 i 与 z1，一般不单独改",
    "b": "可自由调，不影响中心距；只影响承载与轴向尺寸",
    "eps": "是结果不是输入；想改它只能改 z 或压力角",
}


def rows(req: Request, best: dict) -> list[tuple[str, str, str, str, str, str]]:
    m, z1, z2 = best["module"], best["z1"], best["z2"]
    d1, d2 = m * z1, m * z2
    b = req.bm_ratio * m
    out = [
        ("i", f"{req.ratio:g}", "问", "你说的“减速几倍”", "改它会连带改 z2 与中心距"),
        ("a", f"{req.center_mm:g} mm", "问", "你说的“两轴之间能塞多宽”", "改它 → 模数或齿数要重算"),
        ("m", f"{m:g} mm", "选", "在标准模数系列里挑能让 a 对上的一档（GB/T 1357 第一系列）", "往上取标准系列即可"),
        ("z1", f"{z1}", "算", "z1 = 2a / (m(1+i))", "可锁定（有现成刀具时）；<17 会根切，需变位"),
        ("z2", f"{z2}", "算", "z2 = i · z1", "跟随 i 与 z1，一般不单独改"),
        ("d1", f"{d1:.1f} mm", "算", "d = m · z", "跟随 m 与 z1"),
        ("d2", f"{d2:.1f} mm", "算", "d = m · z", "跟随 m 与 z2"),
        ("b", f"{b:.1f} mm", "选", f"按 b/m = {req.bm_ratio:g}（一般传动 8~12）", "可自由调，不影响中心距"),
        ("eps", f"{best['eps']:.2f}", "算", "标准直齿重合度公式（含齿顶圆）",
         "是结果不是输入；想改只能改 z 或压力角"),
        ("da1", f"{d1 + 2 * m:.1f} mm", "算", "da = d + 2m（标准全齿高）", "跟随 m 与 z"),
        ("da2", f"{d2 + 2 * m:.1f} mm", "算", "da = d + 2m", "跟随 m 与 z"),
        ("df1", f"{d1 - 2.5 * m:.1f} mm", "算", "df = d − 2.5m（标准顶隙 0.25m）", "跟随 m 与 z"),
    ]
    return out


def render(tag: str, req: Request) -> None:
    best, near = solve(req)
    print("\n" + "#" * 78)
    print("# " + tag)
    print("#" * 78)
    if best is None:
        print("（本组参数无解，不出推导表；失败诊断见 derive_gear.py 的 explain）")
        return

    print("\n## A. 我问了什么，你怎么答的")
    print(f"   · 「减速几倍」→ {req.ratio:g}")
    print(f"   · 「两轴之间能塞多宽」→ {req.center_mm:g} mm")
    if req.pin_z1:
        print(f"   · （工程师接管）z1 锁定为 {req.pin_z1}")
    if req.pin_module:
        print(f"   · （工程师接管）模数锁定为 {req.pin_module:g}")

    print("\n## B. 我据此推出的全部参数")
    print("| # | 参数 | 一句话含义 | 值 | 来源 | 依据 | 你能怎么改 |")
    print("|---|---|---|---|---|---|---|")
    for n, (k, v, src, why, how) in enumerate(rows(req, best), 1):
        if k in ("z1", "m") and (req.pin_z1 and k == "z1" or req.pin_module and k == "m"):
            src, why = "锁", "你指定的，我没有按规则推导"
        print(f"| {n} | {k} | {MEANING.get(k, '')} | {v} | {src} | {why} | {how} |")

    print("\n## C. 我没算的 / 我替你定了的")
    print("   ✗ 强度校核：没做。材料与热处理未定，[σH]/[σF] 无法取；"
          "载荷系数 K 需要工况（冲击/连续）")
    print("   ✗ 变位系数：未定（当前按标准全齿高 x=0 推导）")
    print("   ✗ 公差与表面粗糙度：未定")
    print("   ⚠ 假设：齿宽按 b/m=10 选（一般传动，无重载依据）")
    print("   ⚠ 假设：模数只搜了 1~10 这一段第一系列")
    print(f"   ⚠ 判据：εα={best['eps']:.2f} 对照下限 {EPS_MIN}（工程惯例，未核标准原文）")
    print(f"   ⚠ 判据：z1≥{Z_MIN} 取自本机知识库 直齿圆柱齿轮选型.md")


if __name__ == "__main__":
    render("方案 1｜客户：减速 3 倍，中心距 40mm", Request(ratio=3.0, center_mm=40.0))
    render("方案 2｜工程师：减速 2.5，中心距 43mm，锁定 z1=20",
           Request(ratio=2.5, center_mm=43.0, pin_z1=20))
