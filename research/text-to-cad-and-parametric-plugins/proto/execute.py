"""execute.py —— FeaturePlan → 真机建模。全项目**唯一**碰 SolidWorks COM 的地方。

# ── 来源 ─────────────────────────────────────────────────────────────
# 契约:   specs/354-make-side-generation/contracts/execute.contract.md
# 单位:   两套并存（T001 实测 + sw_part.py:1320 逐字）
#           sketch_line / sketch_circle → 毫米
#           extrude_boss                → 米   ⇒ 必须 sw_connect.mm() 转换
# ★★ 2026-11-07 业主令：--gear（折线模拟渐开线）已删除，全项目禁止折线拟合曲线。
#    本执行器当前只服务轴族（Revolve，真直线半剖轮廓）。
# 模板:   C:\\ProgramData\\SOLIDWORKS\\SOLIDWORKS 2026\\templates\\gb_part.prtdot
#         实测：\\SOLIDWORKS Data\\Templates\\Part.prtdot **不存在**，NewDocument 会静默返 None
# 回读:   solid_body_extent_mm（用 GetBodyBox）
#         ⚠ 禁用 IFeature.GetBox() —— 官方 Remarks「approximate … not for comparison」
# 体积:   mass_properties()["volume"] 的**实际单位是 m^3**（T004 实测 2e-06 ↔ 2000 mm^3），
#         虽然 UNITS 常量写的是 mm^3 ⇒ 本模块强制 ×1e9，不信常量
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from build_plan import (  # noqa: E402
    Circle,
    Extrude,
    FeaturePlan,
    Line,
    Revolve,
    plan_shaft,
)

TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot"
FAIL_DIR = ROOT / "output" / "execute_failures"
OUT_DIR = ROOT / "output" / "make_side"

#: 坐标量级窗口（1000× 事故回归）
COORD_MIN = 1.0
COORD_MAX = 1000.0


class ExecuteError(RuntimeError):
    """建模失败。带 stage 与 plan 快照，便于落 FailureRecord。"""

    def __init__(self, message: str, *, stage: str, plan: FeaturePlan | None = None):
        super().__init__(message)
        self.stage = stage
        self.plan = plan


# ── 前置校验（纯数据，不碰 COM）──────────────────────────────────────
def check_plan(plan: FeaturePlan) -> None:
    """契约 §前置条件 1–4。全部不碰 COM，可离线单测。"""
    if plan.units != "mm":
        raise ValueError(f"plan.units 必须是 'mm'，实际 {plan.units!r}")
    if not plan.sketch_entities:
        raise ValueError("plan.sketch_entities 为空")
    if not plan.features:
        raise ValueError("plan.features 为空")
    if not isinstance(plan.features[0], (Extrude, Revolve)):
        raise ValueError(
            f"features[0] 必须是 Extrude 或 Revolve，实际 {type(plan.features[0]).__name__}")
    if isinstance(plan.features[0], Revolve) and not plan.axis_entities:
        raise ValueError("Revolve 计划必须有 axis_entities（轴线段），否则无法定旋转轴")

    # ★ 判据用「全局最大绝对坐标」，不是「每个坐标」——
    #   真实齿轮轮廓会穿过原点附近（实测有 -0.816 这样的合法毫米坐标），
    #   逐点判最小值会把正常齿轮误判成 1000× 事故。
    #   米制误传的指纹是 **全局最大绝对坐标 ≈ 0.011**（而不是 11），所以看最大值足够。
    max_abs = 0.0
    sample = ""
    for e in plan.sketch_entities:
        coords = (
            [e.x1_mm, e.y1_mm, e.x2_mm, e.y2_mm] if isinstance(e, Line)
            else [e.cx_mm, e.cy_mm, e.r_mm] if isinstance(e, Circle)
            else []
        )
        for c in coords:
            if abs(c) > max_abs:
                max_abs = abs(c)
                sample = f"{type(e).__name__}({c:.6g})"
    if not (COORD_MIN <= max_abs <= COORD_MAX):
        raise ValueError(
            f"坐标量级异常（全局最大 |c| = {max_abs:.6g}，要求 {COORD_MIN} <= |c| <= {COORD_MAX}；"
            f"米制误传会给出 ≈0.011）：{sample}"
        )


# ── 失败留证 ─────────────────────────────────────────────────────────
def write_failure(exc: BaseException, plan: FeaturePlan | None, *, stage: str,
                  screenshot: str | None = None) -> Path:
    """契约 §失败契约：落 FailureRecord，不掩盖。"""
    FAIL_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rec = {
        "plan_name": plan.name if plan else None,
        "plan_snapshot": _plan_snapshot(plan) if plan else None,
        "exception_type": type(exc).__name__,
        "exception_message": str(exc)[:2000],
        "stage": stage,
        "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-4000:],
        "screenshot": screenshot,
        "timestamp": ts,
    }
    p = FAIL_DIR / f"{ts}-{stage}.json"
    p.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def _plan_snapshot(plan: FeaturePlan) -> dict:
    return {
        "name": plan.name,
        "units": plan.units,
        "entity_count": len(plan.sketch_entities),
        "line_count": sum(isinstance(e, Line) for e in plan.sketch_entities),
        "circle_count": sum(isinstance(e, Circle) for e in plan.sketch_entities),
        "depth_mm": plan.features[0].depth_mm if plan.features else None,
        "expected": asdict(plan.expected),
        "provenance": plan.provenance,
    }


# ── 执行 ─────────────────────────────────────────────────────────────
def execute(plan: FeaturePlan, *, model: Any = None, plane_name: str = "Front Plane",
            sw: Any = None) -> tuple[Any, dict]:
    """按计划建模型。

    :param plan: 已校验的计划（内部一律毫米）
    :param model: 已有 `IModelDoc2`；None 则新建零件
    :param plane_name: 建模基准面
    :param sw: 已连接的 `ISldWorks`；None 则自连
    :returns: `(model, evidence)`
    :raises ValueError: 前置条件不满足（**不碰 COM**）
    :raises ExecuteError: 建模失败（**已落 FailureRecord**）
    """
    check_plan(plan)

    import sw_connect
    from sw_feature_readback import feature_present, solid_body_extent_mm
    from sw_part import extrude_boss, sketch, sketch_circle, sketch_line

    if sw is None:
        sw, _ = sw_connect.connect_solidworks(visible=True)
    if model is None:
        model = sw.NewDocument(TEMPLATE, 0, 0, 0)
        if model is None:
            exc = ExecuteError(f"NewDocument 返回 None（模板不可用：{TEMPLATE}）", stage="newdoc", plan=plan)
            write_failure(exc, plan, stage="newdoc")
            raise exc

    feat_spec = plan.features[0]
    is_revolve = isinstance(feat_spec, Revolve)
    entity_count = 0

    def _draw(entities, plane: str) -> str:
        """在一个新草图里画 entities，返回草图名。"""
        nonlocal entity_count
        with sketch(model, plane) as sk_name:
            manager = model.SketchManager
            old_add_db = old_display = None
            try:
                old_add_db = bool(manager.AddToDB)
                old_display = bool(manager.DisplayWhenAdded)
                manager.AddToDB = True
                manager.DisplayWhenAdded = False
            except Exception:  # noqa: BLE001 — 属性不支持时不影响主流程
                old_add_db = old_display = None
            try:
                for e in entities:
                    if isinstance(e, Line):
                        if sketch_line(model, e.x1_mm, e.y1_mm, e.x2_mm, e.y2_mm) is None:
                            raise ExecuteError("sketch_line 返回 None", stage="sketch", plan=plan)
                    elif isinstance(e, Circle):
                        if sketch_circle(model, e.cx_mm, e.cy_mm, e.r_mm) is None:
                            raise ExecuteError("sketch_circle 返回 None", stage="sketch", plan=plan)
                    else:
                        raise ExecuteError(f"未知实体类型 {type(e).__name__}", stage="sketch", plan=plan)
                    entity_count += 1
            finally:
                try:
                    if old_add_db is not None:
                        manager.AddToDB = old_add_db
                    if old_display is not None:
                        manager.DisplayWhenAdded = old_display
                except Exception:  # noqa: BLE001 — 还原失败不掩盖主错误
                    pass
        return sk_name

    # ── 草图（轮廓）──
    try:
        profile_sketch = _draw(plan.sketch_entities, plane_name)
    except ExecuteError:
        raise
    except Exception as exc:  # noqa: BLE001
        err = ExecuteError(f"草图阶段失败：{exc}", stage="sketch", plan=plan)
        write_failure(exc, plan, stage="sketch")
        raise err from exc

    # ── 成型：拉伸（收米）或旋转（360°）──
    try:
        if is_revolve:
            import math as _m

            from sw_part import _select_com_object, _select_revolve_axis, revolve_boss

            # ★ 轴必须独占一个草图：`_select_revolve_axis` 会把该草图的**所有**
            #   线段都选成轴（`for seg in segments: _select_com_object(seg, mark=4)`）。
            axis_sketch = _draw(plan.axis_entities, plane_name)

            # ★★★ 2026-11-06 **不能走 axis_sketch_name 这条路**：
            #   `revolve_boss` 内部是「先选轴 → 再 `_ensure_sketch_selected(轮廓)`」，
            #   而后者经 `_select_sketch_ref` 的第一行 `model.ClearSelection2(True)`
            #   把刚选好的轴**清空**（sw_part.py:396）⇒ `FeatureRevolve2` 只见轮廓
            #   不见轴 ⇒ 静默返回 None（真机实测）。
            #   ⇒ 改为在本层把「轴 + 轮廓」都选好，再用 `__current_selection__`
            #     走 `_ensure_sketch_selected` 的提前返回分支，选择集不被清。
            n_axis = _select_revolve_axis(model, axis_sketch)
            if n_axis <= 0:
                raise ExecuteError(
                    f"轴线段选择失败（axis_sketch={axis_sketch}）",
                    stage="revolve", plan=plan)

            profile_feature = model.FeatureByName(profile_sketch)
            if profile_feature is None or not _select_com_object(
                    profile_feature, append=True, mark=0, model=model):
                raise ExecuteError(
                    f"轮廓选择失败（profile_sketch={profile_sketch}）",
                    stage="revolve", plan=plan)

            feat = revolve_boss(
                model, "__current_selection__", _m.radians(feat_spec.angle_deg))
            if feat is None:
                raise ExecuteError(
                    f"revolve_boss 返回 None（轴线段 {n_axis} 条已选）",
                    stage="revolve", plan=plan)
        else:
            feat = extrude_boss(model, profile_sketch, sw_connect.mm(feat_spec.depth_mm))
            if feat is None:
                raise ExecuteError("extrude_boss 返回 None", stage="extrude", plan=plan)
    except ExecuteError:
        raise
    except Exception as exc:  # noqa: BLE001
        stage_name = "revolve" if is_revolve else "extrude"
        err = ExecuteError(f"{stage_name} 阶段失败：{exc}", stage=stage_name, plan=plan)
        write_failure(exc, plan, stage=stage_name)
        raise err from exc

    # ── 改名 + rebuild（T005：rebuild 非必须，但保留更稳）──
    try:
        feat.Name = plan.name
    except Exception:  # noqa: BLE001 — 改不了名不影响几何
        pass
    try:
        model.ForceRebuild3(False)
    except Exception:  # noqa: BLE001
        pass

    evidence = {
        "status": "ok",
        "feature_name": plan.name,
        "primitive": "revolve" if is_revolve else "extrude",
        "sketch_entity_count": entity_count,
        "plane_name": plane_name,
        "profile_form": plan.provenance.get("profile_form", "unknown"),
        "feature_present": bool(feature_present(model, plan.name)),
        "bbox": {k: solid_body_extent_mm(model).get(k) for k in ("x_mm", "y_mm", "z_mm")},
        "uncovered": list(plan.provenance.get("uncovered", [])) or [
            "强度校核：未做（材料与热处理未定）",
            "公差与表面粗糙度：未定",
        ],
    }
    if is_revolve:
        evidence["angle_deg"] = feat_spec.angle_deg
    else:
        evidence["depth_m"] = sw_connect.mm(feat_spec.depth_mm)
    return model, evidence


# ── CLI ──────────────────────────────────────────────────────────────
def _parse_kv(argv: list[str]) -> dict[str, str]:
    out = {}
    for a in argv:
        if "=" in a:
            k, v = a.split("=", 1)
            out[k] = v
    return out


def main(argv: list[str]) -> int:
    # Windows 控制台默认 GBK：shaft_method.render() 里有 U+2212「−」会直接抛
    # UnicodeEncodeError 而炸在打印阶段（不是建模阶段）。
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 — 非 TTY/老 Python 无此方法时按原样输出
        pass

    # ★★ 2026-11-07 业主令：--gear 分支已删除。
    #    它把渐开线采样成点列逐段连直线（折线模拟曲线），全项目禁止。
    #    真曲线齿轮（scripts/gear_geometry.py）尚未通过真机验证，不提供 CLI 入口。

    if "--shaft" in argv:
        from shaft_method import ShaftRequest, derive_shaft, render as render_shaft

        kv = _parse_kv(argv)
        req = ShaftRequest(
            torque_nm=float(kv.get("T", 120.0)),
            length_mm=float(kv.get("L", 300.0)),
            material=kv.get("mat", "45钢"),
            shock=kv.get("shock", "none"),
            stepped=kv.get("stepped", "1") not in ("0", "false", "no"),
            step_ratio=float(kv.get("ratio", 0.4)),
        )
        der = derive_shaft(req)
        print(render_shaft(der))

        plan = plan_shaft(req)
        print()
        print(f"plan: {plan.name}  实体 {len(plan.sketch_entities)}  "
              f"轴线段 {len(plan.axis_entities)}  旋转 {plan.features[0].angle_deg:g}°")
        print(f"预期体积 {plan.expected.volume_mm3:.2f} mm³  "
              f"包围盒 {plan.expected.bbox_x_mm:.2f}×{plan.expected.bbox_y_mm:.2f}"
              f"×{plan.expected.bbox_z_mm:.2f}")

        from verify import verify
        model, ev = execute(plan)
        print(f"execute: {ev['feature_name']}  原语 {ev['primitive']}  "
              f"草图实体 {ev['sketch_entity_count']}")

        v = verify(model, plan, views_dir=OUT_DIR / "views")
        print(v.report())
        return 0 if v.ok else 1

    print("用法: python execute.py --shaft T=120 L=300 [mat=45钢] [shock=none]")
    print("注：--gear 已按业主令删除（禁止折线模拟曲线）")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
