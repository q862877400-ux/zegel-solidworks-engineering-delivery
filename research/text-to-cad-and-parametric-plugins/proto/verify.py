"""verify.py —— L3（体积/包围盒）+ L4（三视图）判定器。只读，不改模型。

# ── 来源 ─────────────────────────────────────────────────────────────
# 契约:   specs/354-make-side-generation/contracts/verify.contract.md
# 体积:   sw_mass_property.mass_properties()["volume"]
#         ★ T004 实测：原始单位是 **m^3**（20×20×5 读回 2.0e-06），
#           而 UNITS 常量写 mm^3 ⇒ **本模块强制 ×1e9，不信常量**。
# 包围盒: sw_feature_readback.solid_body_extent_mm()（用 GetBodyBox）
#         ⚠ 禁用 IFeature.GetBox() —— 官方 Remarks「approximate … not for comparison」
# 三视图: sw_review.save_review_previews()（T006 实测输出 **BMP**，4.8 MB/张）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from build_plan import FeaturePlan  # noqa: E402

#: 体积偏差上限（%）
VOLUME_TOL_PCT = 1.0
#: 包围盒单轴偏差上限（mm）
BBOX_TOL_MM = 0.5
#: m^3 → mm^3
M3_TO_MM3 = 1e9
#: 三视图应有的张数
VIEW_NAMES = ("isometric", "front", "top", "right")


@dataclass(frozen=True)
class Verification:
    ok: bool
    measured_volume_mm3: float | None
    expected_volume_mm3: float
    volume_deviation_pct: float | None
    measured_bbox_mm: tuple[float, float, float] | None
    expected_bbox_mm: tuple[float, float, float]
    bbox_deviation_mm: tuple[float, float, float] | None
    views: list[str] = field(default_factory=list)
    failure: str | None = None

    def report(self) -> str:
        """人读报告。三条判据逐条给结论。"""
        lines = []
        if self.volume_deviation_pct is None:
            lines.append("verify: 体积 ✗ 读不到")
        else:
            mark = "✓" if self.volume_deviation_pct < VOLUME_TOL_PCT else "✗"
            lines.append(
                f"verify: 体积 {self.measured_volume_mm3:.1f} mm³"
                f"（预期 {self.expected_volume_mm3:.2f}，偏差 {self.volume_deviation_pct:.2f}%）{mark}"
            )
        if self.bbox_deviation_mm is None:
            lines.append("verify: 包围盒 ✗ 读不到")
        else:
            mark = "✓" if max(self.bbox_deviation_mm) < BBOX_TOL_MM else "✗"
            mx, my, mz = self.measured_bbox_mm or (0, 0, 0)
            dx, dy, dz = self.bbox_deviation_mm
            lines.append(
                f"verify: 包围盒 {mx:.2f}×{my:.2f}×{mz:.2f}"
                f"（偏差 {dx:.3f}/{dy:.3f}/{dz:.3f}）{mark}"
            )
        mark = "✓" if len(self.views) >= len(VIEW_NAMES) else "✗"
        lines.append(f"verify: 三视图 {len(self.views)}/{len(VIEW_NAMES)} {mark}")
        if self.failure:
            lines.append(f"verify: 失败原因 = {self.failure}")
        lines.append(f"VERDICT: {'OK' if self.ok else 'FAIL'}")
        return "\n".join(lines)


def _read_volume_mm3(model) -> tuple[float | None, str | None]:
    """读体积并转 mm³。返回 (值, 错误)。"""
    try:
        from sw_mass_property import mass_properties
        mp = mass_properties(model)
        raw = mp.get("volume")
        if raw is None:
            return None, "mass_properties 回空（volume 字段为 None）"
        # ★ T004 实测：raw 是 m^3
        return float(raw) * M3_TO_MM3, None
    except Exception as exc:  # noqa: BLE001
        return None, f"mass_properties 异常：{type(exc).__name__}: {exc}"


def _read_bbox(model) -> tuple[tuple[float, float, float] | None, str | None]:
    try:
        from sw_feature_readback import solid_body_extent_mm
        r = solid_body_extent_mm(model)
        if not r.get("ok"):
            return None, f"solid_body_extent_mm 失败：{r.get('error')}"
        return (float(r["x_mm"]), float(r["y_mm"]), float(r["z_mm"])), None
    except Exception as exc:  # noqa: BLE001
        return None, f"solid_body_extent_mm 异常：{type(exc).__name__}: {exc}"


def _export_views(model, plan: FeaturePlan, views_dir: Path | None) -> tuple[list[str], str | None]:
    if views_dir is None:
        return [], "未指定 views_dir，跳过三视图"
    try:
        from sw_review import save_review_previews
        views_dir = Path(views_dir)
        views_dir.mkdir(parents=True, exist_ok=True)
        paths = save_review_previews(model, views_dir, basename=plan.name, views=VIEW_NAMES)
        out = []
        for p in paths:
            pp = Path(str(p))
            if pp.exists() and pp.stat().st_size > 0:
                out.append(str(pp))
        if len(out) < len(VIEW_NAMES):
            return out, f"三视图只出了 {len(out)}/{len(VIEW_NAMES)}"
        return out, None
    except Exception as exc:  # noqa: BLE001
        return [], f"三视图导出异常：{type(exc).__name__}: {exc}"


def verify(model, plan: FeaturePlan, *, views_dir: str | Path | None = None) -> Verification:
    """三条判据逐条判，失败不掩盖。

    :param model: 已建成的 `IModelDoc2`
    :param plan: 对应的计划（提供预期值）
    :param views_dir: 三视图落点；None 则跳过（但会记入 failure）
    :returns: `Verification`
    """
    if model is None:
        raise ValueError("model 为 None")
    if plan.units != "mm":
        raise ValueError(f"plan.units 必须是 'mm'，实际 {plan.units!r}")
    if not plan.expected.volume_mm3 > 0:
        raise ValueError("plan.expected.volume_mm3 必须 > 0（没有预期值就无从比对）")

    failures: list[str] = []
    expected_v = plan.expected.volume_mm3
    expected_bbox = (plan.expected.bbox_x_mm, plan.expected.bbox_y_mm, plan.expected.bbox_z_mm)

    # ── L3-a 体积 ──
    measured_v, err_v = _read_volume_mm3(model)
    dev_pct = None
    if err_v:
        failures.append(err_v)
    else:
        dev_pct = abs(measured_v - expected_v) / expected_v * 100.0
        if dev_pct >= VOLUME_TOL_PCT:
            failures.append(
                f"体积偏差 {dev_pct:.2f}% ≥ {VOLUME_TOL_PCT}%（实测 {measured_v:.2f}，预期 {expected_v:.2f}）"
            )

    # ── L3-b 包围盒 ──
    measured_bbox, err_b = _read_bbox(model)
    dev_bbox = None
    if err_b:
        failures.append(err_b)
    else:
        dev_bbox = tuple(abs(a - b) for a, b in zip(measured_bbox, expected_bbox))
        if max(dev_bbox) >= BBOX_TOL_MM:
            failures.append(
                f"包围盒偏差超限 {BBOX_TOL_MM}mm（实测 {measured_bbox}，预期 {expected_bbox}）"
            )

    # ── L4 三视图 ──
    views, err_view = _export_views(model, plan, Path(views_dir) if views_dir else None)
    if err_view:
        failures.append(err_view)

    return Verification(
        ok=not failures,
        measured_volume_mm3=measured_v,
        expected_volume_mm3=expected_v,
        volume_deviation_pct=dev_pct,
        measured_bbox_mm=measured_bbox,
        expected_bbox_mm=expected_bbox,
        bbox_deviation_mm=dev_bbox,  # type: ignore[arg-type]
        views=views,
        failure="; ".join(failures) if failures else None,
    )
