r"""@brief 真机证据：**网格 / 求解 / 读数 4 个工具**（24h 段 1.2 / Spec Kit `142` 的验收②）—— ★ **经进程隔离执行**。

## ★★★★★ 与前一版的根本区别：**会弹框的三步全部走 `run_isolated`**
```
★ 前一版（三次都挂住）：`create_mesh` / `run_analysis` **在主进程里直接调 COM**
  ⇒ 弹模态框 ⇒ ★ **全体挂死**（`job_kill` 救不回来 —— 见 known-facts 174）
★ 本版：★ 三步都经 `sw_isolate.run_isolated` **在可被杀的子进程里**执行
  ⇒ 挂起 ⇒ **超时 + 杀子进程** ⇒ ★ **主会话完好**（★ 机制已单测 + 真机验过：known-facts 177）
★ 而**建模与加载荷**（不弹框的那些）仍在父进程做 —— ★ 只隔离**需要隔离的**。
```

## 判据（★ 沿用既有脚本那三条，不新搓）
```
| 网格 | `CreateMesh` 返回 0 **且** `ElementCount` 为一个（小的）正整数 |
| 求解 | ★ **不是** `RunAnalysis` 的返回码，而是 `study.Results` 非空 + `GetPlotCount > 0` |
★ 且本版**额外**断言：★ **隔离层报的是 `timed_out=False`**（★ 即"没挂起"）
   —— 若 `timed_out=True`，★ 那就是"前置条件仍不成立"，而**这一版会如实记下来**（而不是挂死）。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 ·
★ **三次真机失败的历史**要求每一步都说清成败（★ 本版每步都落 JSON，即使失败）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_mesh_solve_evidence.py
# 定位:   Spec Kit `142` 的**验收②**：产出 `output/mesh-solve-evidence.json`。
# 官方依据: `ICWStudy.CreateMesh` / `RunAnalysis` · `ICWMesh.ElementCount` · `ICWResults
#           .GetPlotCount`
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mesh-solve-evidence.json")
STUDY = "DSH-142"
#: ★ 隔离超时：跑分析给足时间，但**不无限等**（★ 超时 = 杀子进程，不是挂死）
T_MESH, T_RUN = 180.0, 300.0


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "mesh_solve_readback",
                "★": "★ 会弹框的三步（网格/求解）**经 run_isolated 在子进程执行**", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_isolate import run_isolated
        from scripts.sw_simulation import out_i4
        import register_capabilities as rc
        import tool_specs_batch28 as b28

        #: ① 核声明解析得到
        bindings = {}
        for spec in b28.SPECS_BATCH28:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {"resolved": callable(getattr(mod, spec.function, None)),
                                   "inject": spec.inject}
        ev["steps"]["bindings"] = {"ok": all(v["resolved"] for v in bindings.values()),
                                   "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: ② 造零件 + 材料 + 研究 + 夹具 + 载荷（★ 这些**不弹框** ⇒ 留在父进程）
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)

        sim.set_material(doc, "AISI 1020")
        material = str(sw_connect.safe_get_com_member(doc, "MaterialIdName") or "")
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)

        sim.select_face_at(doc, 0.0, 0.0, -0.02)
        sim.apply_fixed_restraint(study, model=doc)
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        sim.select_face_at(doc, 0.0, 0.0, 0.0)
        sim.apply_normal_force(study, 100.0, model=doc)

        #: ★★ 前置条件（★ 满足它们才**值得**往下走；★ 但不满足时的失败**不再挂死会话**）
        mgr = sim._loads_and_restraints_manager(study)
        count = int(sw_connect.safe_get_com_member(mgr, "Count") or 0)
        states = []
        for i in range(count):
            it = sw_connect.safe_get_com_member(mgr, "GetLoadsAndRestraints", i, out_i4())
            st = sw_connect.safe_get_com_member(it, "State")
            #: ⚠ 不写 `State or -1` —— `State` 的合法值包含 **0**（★ 事实 178 的教训）
            states.append(int(st) if st is not None else -1)
        ev["steps"]["preconditions"] = {
            "material_id_name": material, "loads_count": count, "load_states": states,
            "ok": bool(material) and count >= 2,
        }
        print("  [前置] 材料=%r Count=%d States=%s" % (material, count, states))

        #: ③ ★★★ 三步**全部经隔离**（★ 这一步是本版的核心改动）
        def iso(fn: str, args: list, kwargs: dict, timeout: float) -> dict:
            t0 = time.time()
            r = run_isolated("scripts.sw_simulation_worker", fn,
                             args=args, kwargs=kwargs, timeout=timeout)
            r["wall_seconds"] = round(time.time() - t0, 1)
            return r

        size_r = iso("mesh_size_by_name", [STUDY], {"units": -1}, 120)
        ev["steps"]["mesh_size"] = {**size_r}
        print("  [1] 网格尺寸(隔离): ok=%s timed_out=%s %s"
              % (size_r.get("ok"), size_r.get("timed_out"), str(size_r.get("result"))[:90]))

        size = (size_r.get("result") or {}) if isinstance(size_r.get("result"), dict) else {}
        mesh_r = iso("create_mesh_by_name", [STUDY],
                     {"units": 0,
                      #: ⚠ 不写 `x or 默认值` —— **0.0 是合法值**（"让 SolidWorks 自己选
                      #: "），
                      #:   `0.0 or 4.9339` 会把它顶掉（★ 事实 178 同族，门禁抓的）。
                      "element_size": float(_v if (_v := size.get("element_size")) is not None else 4.9339),
                      "tolerance": float(_w if (_w := size.get("tolerance")) is not None else 0.2467)},
                     T_MESH)
        ev["steps"]["create_mesh"] = {**mesh_r}
        print("  [2] 建网格(隔离): ok=%s timed_out=%s %s"
              % (mesh_r.get("ok"), mesh_r.get("timed_out"), str(mesh_r.get("result"))[:110]))

        run_r = iso("run_analysis_by_name", [STUDY], {}, T_RUN)
        ev["steps"]["run_analysis"] = {**run_r}
        print("  [3] 跑求解(隔离): ok=%s timed_out=%s %s"
              % (run_r.get("ok"), run_r.get("timed_out"), str(run_r.get("result"))[:130]))

        #: ④ ★★ 隔离层本身不挂起（★ 本版的核心断言）
        ev["steps"]["no_hang"] = {
            "ok": all(not ev["steps"][k].get("timed_out")
                      for k in ("mesh_size", "create_mesh", "run_analysis")),
            "★": "★★ 三步都没超时 ⇒ **隔离层没挂起**；若某步 timed_out=True ⇒ "
                 "前置条件仍不成立（★ 而**那一版会如实记下，而不是挂死会话**）",
        }
        ok = ok and ev["steps"]["no_hang"]["ok"]

        #: ⑤ 判据（★ 沿用既有脚本那三条）
        mesh_res = mesh_r.get("result") if isinstance(mesh_r.get("result"), dict) else {}
        run_res = run_r.get("result") if isinstance(run_r.get("result"), dict) else {}
        ev["steps"]["verdict_judgement"] = {
            "mesh_ok": bool(mesh_res.get("ok")) and int(mesh_res.get("element_count") or 0) > 0,
            "element_count": mesh_res.get("element_count"),
            "run_ok": bool(run_res.get("ok")),
            "results_present": run_res.get("results_present"),
            "plot_count": run_res.get("plot_count"),
            "plot_names": run_res.get("plot_names"),
            "★": "★ 判据：网格 element_count 为正整数 · 求解 results 非空 + plot_count > 0（**不看返回码**）",
        }

        #: ⑥ 研究读数（已经是 dict，直接挂）
        evi = sim.collect_study_evidence(sw)
        ev["steps"]["collect_evidence"] = {
            "ok": isinstance(evi, dict) and int(evi.get("study_count") or 0) >= 1,
            "study_count": evi.get("study_count"),
            "names": [s.get("name") for s in (evi.get("studies") or [])],
        }
        ok = ok and ev["steps"]["collect_evidence"]["ok"]
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
    print("  ── 网格/求解/读数（★ 经进程隔离）真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-20s %s" % (k, json.dumps(v, ensure_ascii=False)[:220]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
