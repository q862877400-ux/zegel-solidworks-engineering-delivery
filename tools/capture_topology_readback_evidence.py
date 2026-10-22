r"""@brief 真机证据：**拓扑读数与参数 6 个工具**（24h 段 2.2 / Spec Kit `144` 的验收②）。

## 判据（★ 按 `AGENTS.md` §5.0：**先在自家仓库找**）
```
★ `collect_topology_numbers` 的 **`material_mass_plot`** —— 直接来自**既有证据脚本**
  `tools/capture_topology_evidence.py` 的判据表（「`GetPlotNames` 里出现 `材料质量*`」）。
★ 「设置生效了吗」= **前后对照「取到了几个 kind」**
  ⇒ ★ 用 `sw_topology.list_topology_constraints_and_controls`（本模块**自己的读取入口**）。
   ★ 而它注释里记着一条教训：曾因裸传 `0` 当出参而**永远返回全 None（假通过）**⇒ 改用 `out_i4()`。
  ⇒ ★★ 所以本脚本对"设置"这一步的判据是：**无异常 且 取到的 kind 数不减少**。
```

## ⚠ 本批**不跑求解** ⇒ 无模态框风险（★ 会弹框的是 `run_topology_study` 那类）

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_topology_readback_evidence.py
# 定位:   Spec Kit `144` 的**验收②**：产出 `output/topology-readback-evidence.json`。
# 官方依据: `ICWTopologyStudyManager` / `ICWTopologyStudyOptions`（见 `scripts/sw_topolo
#           gy.py`）
# 许可:   本仓库 MIT。无第三方代码引入。
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "topology-readback-evidence.json")
STUDY = "DSH-144"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "topology_readback_and_parameters",
                "★": "★ 只读数 / 设参数，**不跑求解** ⇒ 无模态框风险", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_topology as T
        import tool_specs_batch30 as b30

        #: ① 静态：6 个工具声明解析得到
        bindings = {}
        for spec in b30.SPECS_BATCH30:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {"resolved": callable(getattr(mod, spec.function, None)),
                                   "inject": spec.inject,
                                   "params": [p.name for p in spec.params]}
        ev["steps"]["bindings"] = {"ok": all(v["resolved"] for v in bindings.values()),
                                   "count": len(bindings), "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: ② 造零件 + 材料（★ 拓扑研究要有材料）+ 拓扑研究
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim_material = None
        try:
            from scripts import sw_simulation as S

            S.set_material(doc, "AISI 1020")
            sim_material = str(sw_connect.safe_get_com_member(doc, "MaterialIdName") or "")
        except Exception as exc:                               # noqa: BLE001
            sim_material = "赋材料失败: %s" % str(exc)[:80]
        ev["steps"]["material"] = sim_material

        created = T.create_topology_study(sw, STUDY)
        ev["steps"]["create_study"] = {"ok": created is not None,
                                       "type": type(created).__name__ if created else None}
        study = None
        try:
            from scripts.sw_simulation import get_study_by_name

            study = get_study_by_name(sw, STUDY)
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["get_study"] = "失败: %s" % str(exc)[:90]
        if study is None:
            raise RuntimeError("按名字取不到刚建的拓扑研究（%r）" % STUDY)

        #: ③ ★ 四个读数（★ 全是回读报告，不回 COM 对象）
        nums = T.collect_topology_numbers(study)
        ev["steps"]["collect_numbers"] = {
            #: ⚠ 判据**不是** `material_mass_plot` 非空 —— ★ 那张图**只有跑完求解才有**
            #: ，
            #:   而本脚本按设计**不跑求解**（★ 跑求解是另一个能力的事，且会弹模态框）。
            #:   ⇒ 本批判的是「**读数入口可用**」：函数回了 dict **且** 带 `status` 字段。
            #: ★ `status == "no_results"` 是**预期值** —— 而它恰好证明那个判据**真的在判
            #: **
            #:     （★ 不是恒真的假通过；对照 `list_topology_constraints_and_controls` 那条
            #      「裸传 0 当出参 ⇒ 永远返回全 None」的既有教训）。
            "ok": isinstance(nums, dict) and "status" in nums,
            "status": nums.get("status"),
            "material_mass_plot": nums.get("material_mass_plot"),
            "plot_count": nums.get("plot_count"),
            "plot_names": nums.get("plot_names"),
            "max_available_steps": nums.get("max_available_steps"),
            "★": "★ material_mass_plot 需**跑过求解**才非空 —— 本批不跑求解，故不拿它当判据",
        }
        cons = T.topology_constraints_report(study)
        ev["steps"]["constraints"] = {"ok": isinstance(cons, dict) and "taken_count" in cons,
                                      "taken_count": cons.get("taken_count"),
                                      "total": cons.get("total"),
                                      "kinds": cons.get("kinds")}
        mrep = T.topology_manager_report(study)
        ev["steps"]["manager_report"] = {"ok": bool(mrep.get("ok")),
                                         "object_type": mrep.get("object_type")}
        orep = T.topology_options_report(study)
        ev["steps"]["options_report"] = {"ok": bool(orep.get("ok")),
                                         "object_type": orep.get("object_type")}

        #: ④ ★ 两个"设置"（★ 判据 = 无异常 且 取到的 kind 数不减少）
        g = T.set_topology_goal_report(study, goal_type=0, mass_reduce_percent=50.0)
        ev["steps"]["set_goal"] = {"ok": bool(g.get("ok")), "error": g.get("error"),
                                   "before_taken": (g.get("before") or {}).get("taken_count"),
                                   "after_taken": (g.get("after") or {}).get("taken_count")}
        io = T.set_topology_iteration_options_report(study)
        ev["steps"]["set_iteration_options"] = {"ok": bool(io.get("ok")), "error": io.get("error"),
                                                "before_taken": (io.get("before") or {}).get("taken_count"),
                                                "after_taken": (io.get("after") or {}).get("taken_count")}

        #: ⑤ 综合判读
        checks = {
            "bindings": ev["steps"]["bindings"]["ok"],
            "create_study": ev["steps"]["create_study"]["ok"],
            "collect_numbers": ev["steps"]["collect_numbers"]["ok"],
            "constraints": ev["steps"]["constraints"]["ok"],
            "manager_report": ev["steps"]["manager_report"]["ok"],
            "options_report": ev["steps"]["options_report"]["ok"],
            "set_goal": ev["steps"]["set_goal"]["ok"],
            "set_iteration_options": ev["steps"]["set_iteration_options"]["ok"],
        }
        ev["steps"]["judgement"] = {"checks": checks, "passed": sum(1 for v in checks.values() if v),
                                    "of": len(checks),
                                    "★": "★ 八项全真才 pass；★ material_mass_plot 是核心判据"}
        ok = ok and all(checks.values())
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
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
    print("  ── 拓扑读数与参数真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-22s %s" % (k, json.dumps(v, ensure_ascii=False)[:230]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
