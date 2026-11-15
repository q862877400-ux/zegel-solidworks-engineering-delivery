"""M0：把零件规格变成一份可校验的 FeaturePlan（纯数据，不碰 COM）。

# ── 来源 ────────────────────────────────────────────────────────────
# 单位:   计划层一律毫米；唯一出口在 `FeaturePlan.to_meters()` 转成米。
# 轴族:   plan_shaft（几何原语 2：绕轴旋转），轮廓是**真直线半剖**，不是拟合曲线。
# 禁用:   ★★ 齿轮折线生成器 `plan_spur_gear` 已删除（2026-11-07 业主令）——
#         它把渐开线采样成点列再逐段连 `Line`，属「折线模拟曲线」，全项目禁止。
#         真曲线齿轮见 `scripts/gear_geometry.py`（方程式驱动曲线），
#         但整圈闭合/单齿阵列路线尚未通过真机验证，当前**不提供**可用齿轮生成器。
# 验证:   体积/包围盒可在建模前算出，建模后直接比对（把验证左移到计划阶段）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# ── 计划层：一律毫米 ────────────────────────────────────────────────
@dataclass(frozen=True)
class Line:
    x1_mm: float
    y1_mm: float
    x2_mm: float
    y2_mm: float


@dataclass(frozen=True)
class Circle:
    cx_mm: float
    cy_mm: float
    r_mm: float


@dataclass(frozen=True)
class Extrude:
    depth_mm: float
    plane: str = "Front Plane"


@dataclass(frozen=True)
class Revolve:
    """绕轴旋转（几何原语 2）。轴线段另放在 `FeaturePlan.axis_entities`。

    ⚑ 真机契约（`scripts/sw_part.py:revolve_boss` 的 docstring，轮 360 定）：
      · **轴必须在轮廓之前进选择集** —— 反了 `feature_created=False`
      · 轴的类型名是 `EXTSKETCHSEGMENT`（不是 `SKETCHSEGMENT`），mark=4
      · `_select_revolve_axis` 收的是**草图名**，会把该草图的**所有**线段选为轴
        ⇒ 轴必须独占一个草图，不能与轮廓同草图
    """
    angle_deg: float = 360.0
    plane: str = "Front Plane"


@dataclass(frozen=True)
class Expected:
    """建模前就能算出来的判据，用来做 L3 校验（体积/包围盒）。"""
    volume_mm3: float
    bbox_x_mm: float
    bbox_y_mm: float
    bbox_z_mm: float


@dataclass
class FeaturePlan:
    name: str
    units: str
    sketch_entities: list
    features: list
    expected: Expected
    provenance: dict = field(default_factory=dict)
    #: 旋转轴线段（仅 Revolve 用）。★ 必须是**独占草图**的线段：
    #: `sw_part._select_revolve_axis` 会遍历该草图的所有线段并全部选为轴。
    axis_entities: list = field(default_factory=list)

    def to_meters(self) -> dict:
        """唯一一处单位转换：计划是毫米，SolidWorks 的 extrude 收米。"""
        return {"depth_m": self.features[0].depth_mm / 1000.0}


def render_plan(p: FeaturePlan) -> str:
    e = p.expected
    f0 = p.features[0]
    if isinstance(f0, Extrude):
        form = (f"  拉伸 {f0.depth_mm:g} mm（送 SolidWorks 时转成 "
                f"{p.to_meters()['depth_m']:.6g} m）")
    else:
        form = f"  旋转 {f0.angle_deg:g}°"
    return (
        f"{p.name}｜单位={p.units}｜草图实体 {len(p.sketch_entities)} 个"
        f"（线段 {sum(isinstance(x, Line) for x in p.sketch_entities)}"
        f" / 圆 {sum(isinstance(x, Circle) for x in p.sketch_entities)}）\n"
        f"{form}\n"
        f"  预期体积 {e.volume_mm3:.2f} mm³｜预期包围盒 "
        f"{e.bbox_x_mm:.2f} × {e.bbox_y_mm:.2f} × {e.bbox_z_mm:.2f} mm\n"
        f"  形式={p.provenance.get('profile_form', 'unknown')}"
    )


# ── 轴族：几何原语 2（绕轴旋转）────────────────────────────────────
def plan_shaft(req, name: str | None = None) -> FeaturePlan:
    """需求 → 轴的计划（旋转体）。

    轮廓（Front Plane，x=半径，y=轴向）—— 这些是**真直线**，不是拟合曲线：
        (0,0) → (r1,0) → (r1,L1) → (r2,L1) → (r2,L) → (0,L)

    ★ 轴线段放 `axis_entities` 而**不是** `sketch_entities` ——
      `sw_part._select_revolve_axis` 会遍历该草图的**所有**线段并全部选为轴
      （读源码所得；docstring 未提）。轴必须独占一个草图。
    """
    from shaft_method import derive_shaft

    d = derive_shaft(req)
    if not d.ok:
        raise ValueError("需求无解：" + "；".join(d.diagnostics))

    r1, r2 = d.d1_mm / 2.0, d.d2_mm / 2.0
    L1, L2, L = d.l1_mm, d.l2_mm, req.length_mm

    if req.stepped and L1 > 0:
        pts = [(0.0, 0.0), (r1, 0.0), (r1, L1), (r2, L1), (r2, L), (0.0, L)]
        vol = math.pi * r1**2 * L1 + math.pi * r2**2 * L2
        rmax = r2
    else:
        pts = [(0.0, 0.0), (r1, 0.0), (r1, L), (0.0, L)]
        vol = math.pi * r1**2 * L
        rmax = r1

    ents = [
        Line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0], pts[(i + 1) % len(pts)][1])
        for i in range(len(pts))
    ]

    return FeaturePlan(
        name=name or f"Shaft_d{d.d1_mm:g}_L{L:g}",
        units="mm",
        sketch_entities=ents,
        features=[Revolve(angle_deg=360.0, plane="Front Plane")],
        expected=Expected(
            volume_mm3=vol,
            bbox_x_mm=2.0 * rmax,
            bbox_y_mm=L,
            bbox_z_mm=2.0 * rmax,
        ),
        provenance={
            "primitive": "revolve",
            "profile_form": "closed_half_section",
            "profile_points": len(pts),
            "r_max_mm": rmax,
            "source": "shaft_method.derive_shaft + design_rules.yaml shaft 节",
        },
        axis_entities=[Line(0.0, 0.0, 0.0, L)],
    )


if __name__ == "__main__":
    import sys
    from shaft_method import ShaftRequest

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    print(render_plan(plan_shaft(ShaftRequest(torque_nm=120.0, length_mm=300.0))))
