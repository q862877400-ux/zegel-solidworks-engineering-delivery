r"""@brief 真机证据：**仿真载荷 2 个工具**（砌墙 W7 / Spec Kit `140` 的验收②）。

## ★★★ 为什么还要写一个（既有 `capture_simulation_evidence.py` 已 PASS）
```
★ 那个脚本走的是**能力层直调**（`sim.apply_fixed_restraint(study, model=model)`）
  ⇒ 它证明**能力层**能跑，**没证明本批新挂的接线**能跑。
★ 而本项目第 4 条可复用套路是「**证据走工具真实路径**」⇒
  ★ 本脚本按**工具层**的三件套走一遍：
     `inject="study"`（用注册器**同一个** `resolve_study`）+
     `pre_call`（**先按 selection 选面**）+ `derived_args`（**补 `model`**）
  ⇒ ★ 若这条链能跑通，才说明**挂上去的那个工具**真的可用。
```

## 判据（★ 沿用既有脚本那三条 —— 那是本项目自己的判据）
```
| 夹具/载荷 | **选区计数 = 1** 且 `LoadsAndRestraintsManager.Count == 2` |
| 网格      | `CreateMesh` 返回 0 **且** `ElementCount` 是一个小的正整数 |
| 求解      | ★ **不是** `RunAnalysis` 的返回码，而是 `study.Results` 非空 + `GetPlotCount > 0` |
★ 第 2/3 条本脚本**不断言**（那一步已被既有脚本覆盖）—— 本脚本只管**接线**是否正确：
  ★ 用工具的 `pre_call` + `derived_args` 把夹具与载荷施上去，并回读 `Count == 2`。
```

## ⚠ 安全
**只在新零件上跑**（造一个 100×60×20 板）· `CommandInProgress` 抑制弹窗 · 收尾**关件不保存** ·
★ 仿真会**自动装配 Simulation 加载项**（`ensure_simulation_addin` 走 `LoadAddIn` 真路径）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_simulation_loads_evidence.py
# 定位:   砌墙 W7（Spec Kit `140`）的**验收②**：产出 `output/simulation-loads-evidence.json`。
# 官方依据: `ICWLoadsAndRestraintsManager.AddRestraint` / `AddForce`；
#          判据三条**沿用** `tools/capture_simulation_evidence.py`（本项目既有，不新造）。
# 许可:   本仓库 MIT。无第三方代码引入（★ 四家**没有**这一域 ⇒ 护城河）。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\simulation-loads-evidence.json")


class _P:
    """最小 params 容器（注册器传进来的那个形状）。"""

    def __init__(self, study_name="", selection="", magnitude_n=0.0):
        self.study_name = study_name
        self.selection = selection
        self.magnitude_n = magnitude_n
        self.response_format = "json"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "simulation_loads_wiring", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        import register_capabilities as rc
        import tool_specs_batch26 as b26

        #: ① 核声明解析得到 + 记下三件套
        bindings = {}
        for spec in b26.SPECS_BATCH26:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {
                "resolved": callable(getattr(mod, spec.function, None)),
                "inject": spec.inject,
                "has_pre_call": spec.pre_call is not None,
                "has_derived_args": spec.derived_args is not None,
            }
        ev["steps"]["bindings"] = {"ok": all(v["resolved"] and v["has_pre_call"]
                                            and v["has_derived_args"]
                                            for v in bindings.values()), "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: ② 造 100×60×20 板（与既有证据脚本同一工况，便于对照）
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sw_part.set_material(doc, "AISI 1020") if hasattr(sw_part, "set_material") else None
        try:
            sim.set_material(doc, "AISI 1020")
        except Exception:                                      # noqa: BLE001
            pass
        sim.create_static_study(sw, "DSH-W7")
        ev["steps"]["part"] = {"ok": True, "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        #: ③ ★★ 走**工具真实路径**：inject(resolve_study) + pre_call(选面) + derived_args(补 model)
        def call_via_tool(spec_name: str, params: _P, **extra):
            spec = next(s for s in b26.SPECS_BATCH26 if s.name == spec_name)
            #: ★ 与注册器 L409-432 同一顺序：inject → extra_op → pre_call → derived_args
            kwargs = {}
            for p in spec.params:
                if p.name in (spec.param_alias or {}) and spec.param_alias[p.name] is None:
                    continue
                kwargs[(spec.param_alias or {}).get(p.name, p.name)] = getattr(params, p.name)
            kwargs[spec.inject] = rc.RESOLVERS[spec.inject](params)      #: inject
            spec.pre_call(params)                                        #: pre_call
            kwargs.update(spec.derived_args(params) or {})               #: derived_args
            kwargs.update(extra)
            fn = getattr(__import__("scripts.%s" % spec.module, fromlist=[spec.function]),
                         spec.function)
            return fn(**kwargs), kwargs

        #: 夹具：选底面（z=-0.02，板厚 20 ⇒ 底面在 -0.02 米处）
        n_fix = sim.select_face_at(doc, 0.0, 0.0, -0.02)
        rst, kw1 = call_via_tool("solidworks_simulation_apply_fixed_restraint",
                                 _P(study_name="DSH-W7", selection="__current_selection__"))
        #: ★★ **必须先清空选区**再选施力面 —— 照既有脚本 `capture_simulation_evidence.py` 的
        #:   L145/L148（它用 `ClearSelection2(True)`）。
        #:   ⚠ 我第一版**漏了这一步** ⇒ 夹具那个面**仍在选区里** ⇒ 第二次回读计数变成 **2**
        #:   （`select_face_at` 默认 `append=False` 只表示"不追加"，**不清空**）⇒ 判据假红。
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        #: 载荷：选顶面（z=0）
        n_frc = sim.select_face_at(doc, 0.0, 0.0, 0.0)
        frc, kw2 = call_via_tool("solidworks_simulation_apply_normal_force",
                                 _P(study_name="DSH-W7", selection="__current_selection__",
                                    magnitude_n=100.0))
        ev["steps"]["via_tool_path"] = {
            "ok": (rst is not None and frc is not None),
            "restraint": str(getattr(rst, "Name", "") or type(rst).__name__) if rst else None,
            "force": str(getattr(frc, "Name", "") or type(frc).__name__) if frc else None,
            "injected_keys": {k: type(v).__name__ for k, v in kw1.items()},
            "★": "★ 走的是 inject(resolve_study) + pre_call(选面) + derived_args(补 model) 这条链",
        }
        ok = ok and ev["steps"]["via_tool_path"]["ok"]

        #: ④ ★ 判据：选区计数 + LoadsAndRestraintsManager.Count == 2
        mgr = sim._loads_and_restraints_manager(rc.RESOLVERS["study"](_P(study_name="DSH-W7")))
        count = int(sw_connect.safe_get_com_member(mgr, "Count") or 0)
        ev["steps"]["judgement"] = {
            "ok": (n_fix == 1 and n_frc == 1 and count == 2),
            "selected_for_fixture": n_fix, "selected_for_force": n_frc, "loads_count": count,
            "★": "★ 判据沿用既有脚本那条：选区计数 = 1 且 Count = 2",
        }
        ok = ok and ev["steps"]["judgement"]["ok"]
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)                             #: ★ 关件不保存
        except Exception:                                      # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 仿真载荷（走工具路径）真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-16s %s" % (k, json.dumps(v, ensure_ascii=False)[:230]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
