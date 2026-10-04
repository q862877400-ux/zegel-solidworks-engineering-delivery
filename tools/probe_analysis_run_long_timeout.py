"""★ 给足超时 + 正确网格尺寸，验 `analysis_run_readback` 的「跑求解」能不能算出结果。

（★ 处置 SPEC `202-user-coverage-gaps` 的 SC-004：★ 第 3 条候选 `analysis_run_readback`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/capture_mesh_solve_evidence.py`（★ 本探针照它的流程写 —— ★ 照 AGENTS.md 的
#         「按 ToolSpec 的契约调，别手调内部实现」）· `tools/capture_simulation_evidence.py`
#         （★ **它才是跑通的那条链**） · `scripts/sw_simulation.py` · `scripts/sw_isolate.py`
# 定位:   ★★★ **第四版（★ 2026-10-04）—— 前三版都栽在同一个前提上，而那个前提是错的**：
#     | 版本 | element_size | 单元数 | 求解读数 |
#     |---|---|---|---|
#     | ①（T_RUN=300） | 4.9339（默认，**正确**）| **7310** | ★ **1 秒 · 4 张图**（★ 成功）|
#     | ② 12.0 mm     | 退化 ⇒ 静默退回默认 | 7250 | 无结果 |
#     | ③ 20.0 mm     | 退化 ⇒ 静默退回默认 | 7250 | 无结果 |
#     ★★ **⇒ 真因（本版据此改写，★ 且它推翻了 `capabilities.yaml` 的一段措辞）**：
#     ① `create_mesh` 的 `element_size` **吃毫米** —— ★ 证据：`capture_simulation_evidence.py`
#        传 **4.9339** ⇒ **7310 单元**（那才是"正确网格"）；
#     ② ★★ 而 `capabilities.yaml` 把 **7250 单元那一次**记成了「`run_analysis` 进入求解即挂
#        （timed_out=True · 300 s）」—— ★ 而**同一份证据**（`output/mesh-solve-evidence.json`，
#        `captured_at: 2026-10-02T23:50:18`）逐字写着 `timed_out=False` · `wall_seconds=1.5`
#        ⇒ ★★★ **7250 那一次没挂，只是**没有结果**（网格退化 ⇒ 无解）** ——
#        ★ 而它是**上一版手工把 4930.5 喂进去**造成的（4.9 米一个单元 > 零件 100 mm）✓
#     ③ ★ 真正 `timed_out=True` 的是 **element_size=4.9339** 那一次，而**那一次网格是对的**
#        ⇒ 求解**真的在算**（观察窗：建立刚度矩阵 · 已用 33 分钟 · 自由度 30,456 · 7250 单元）✓
#     ★★★★ **⇒ 故本版做三件事**：① `element_size` **照 `units=-1` 的原值喂**（4.9339）；
#     ② `T_RUN` 300 s → **1800 s**；③ **求解后轮询 `Results`**（★ 求解可能异步 ——
#     ★ 而"算完了"的判据是**结果读数**、不是返回码）✓
#   ★★★ **判据（★ 含几何/结果读数）**：★ ① `element_count`（网格读数）·
#     ★ ② `results_present` / `plot_count` / `plot_names`（★ **解算结果读数**）·
#     ★ ③ `timed_out` · ★ ④ `wall_seconds` ✓
#   ★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` · ★ 关掉**自己开的**那份文档 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "analysis-run-long-timeout-evidence.json"
#: ★ 带时间戳的唯一名（★ 本仓逐字：「算例**重名**会让计数回读取不到」）✓
STUDY = "SPEC202_LongSolve_%d" % int(time.time())
T_RUN = 1800.0        # ① 300 s → 1800 s
T_MESH = 600.0
#: ③ 求解后轮询：★ 每 15 s 读一次 `Results`，最多 40 次（10 分钟）
POLL_EVERY, POLL_MAX = 15.0, 40


def main() -> int:
    ev: dict = {"★_目的": "给足超时 + **正确网格尺寸**，验「跑求解」能不能算出结果",
                "★_T_RUN_秒": T_RUN,
                "★_根因假设": "create_mesh 的 element_size 吃**毫米**；"
                              "mesh_size_report(units=-1) 回的是**米** ⇒ 上一版喂 4930.5 毫米 = 4.9 米/单元",
                "★_前情": "① element_size=4.9339(mm) ⇒ 7310 单元 ⇒ 求解 1 秒出 4 张图（跑通）"
                          "；② element_size=4930.5 ⇒ 退化退回默认 7250 单元 ⇒ 结果为空"
                          "；③ 真正 timed_out=True 的那次网格是对的（观察窗：建立刚度矩阵 33 分钟）",
                "steps": {}}
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_isolate import run_isolated

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                             # noqa: BLE001
            pass

        #: ① 造零件 + 材料 + 研究 + 夹具 + 载荷（★ 这些不弹框 ⇒ 留父进程）
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        material = str(sw_connect.safe_get_com_member(doc, "MaterialIdName") or "")
        sim.ensure_simulation_addin(sw)

        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
        if study is None:
            raise RuntimeError("按名字取不到研究 %r" % STUDY)
        sim.select_face_at(doc, 0.0, 0.0, -0.02)
        sim.apply_fixed_restraint(study, model=doc)
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        sim.select_face_at(doc, 0.0, 0.0, 0.0)
        sim.apply_normal_force(study, 100.0, model=doc)
        ev["steps"]["setup"] = {"material": material, "study": STUDY}

        def iso(fn: str, args: list, kwargs: dict, timeout: float) -> dict:
            t0 = time.time()
            r = run_isolated("scripts.sw_simulation_worker", fn,
                             args=args, kwargs=kwargs, timeout=timeout)
            r["wall_seconds"] = round(time.time() - t0, 1)
            return r

        #: ② ★★★ **单位口径**：★ `create_mesh` 的 `element_size` 与**实测那条跑通的链**
        #:   （`tools/capture_simulation_evidence.py` 传 **4.9339** ⇒ 7310 单元）**同口径** ⇒
        #:   ★ **吃毫米** ⇒ 本版**直接传 `units=-1` 读回的那个数**（★ 4.9339 mm），
        #:   ★★ **而上一版手工喂的 4930.5 是同一口径下的「把米当毫米」**（★ 4.9 米/单元）
        #:   ⇒ ★ 判据：★ 若 `CreateMesh` 后 `element_count` ≈ 7000（而不是退回默认的 7250 附近）
        #:     且求解出结果 ⇒ ★ **毫米口径坐实** ✓
        #:   ⚠ ★ **只在读了 `units=-1` 而那个数看起来像米（< 1.0）时**才 ×1000 —— ★ 而本机
        #:     实测它回的是 **4.9339**（= 毫米）⇒ ★ **因子应为 1.0**，两个口径都记进证据 ✓
        size_r = iso("mesh_size_by_name", [STUDY], {"units": -1}, 120)
        raw = (size_r.get("result") or {}) if isinstance(size_r.get("result"), dict) else {}
        raw_size = raw.get("element_size")
        raw_tol = raw.get("tolerance")
        #: ★ 判据：`< 1.0` 才当成"这个数是米"（100 mm 的零件，建议单元尺寸若按米就该是 0.0049）
        factor = 1000.0 if (raw_size is not None and abs(float(raw_size)) < 1.0) else 1.0
        element_size = float(raw_size) * factor if raw_size is not None else 0.0
        tolerance = float(raw_tol) * factor if raw_tol is not None else 0.0
        ev["steps"]["mesh_size"] = {
            "ok": size_r.get("ok"), "timed_out": size_r.get("timed_out"),
            "raw_from_units_minus1": raw,
            "★_换算因子": factor,
            "★_喂给_create_mesh_的值": {"element_size": element_size,
                                        "tolerance": tolerance},
            "★": "★ `units=-1` 实测回 4.9339（毫米）；★ 它与跑通那条链（4.9339 ⇒ 7310 单元）同口径",
        }
        print("  [1] 网格尺寸: raw=%r ×%g ⇒ element_size=%.4f · tol=%.4f"
              % (raw_size, factor, element_size, tolerance))

        #: ★ 建网格前的合理性判据（★ 既有的那道闸）
        sane = sim.check_mesh_size_sane(doc, element_size)
        ev["steps"]["mesh_size_sane"] = sane
        print("      check_mesh_size_sane: ok=%s max_dim=%s %s"
              % (sane.get("ok"), sane.get("max_dim"), str(sane.get("reason"))[:90]))
        if not sane.get("ok"):
            raise RuntimeError("网格尺寸不合理 ⇒ 停下（%s）" % sane.get("reason"))

        #: ③ 建网格（★ 粗网格 ⇒ 单元少 ⇒ 刚度矩阵小 ⇒ 算得快）
        mesh_r = iso("create_mesh_by_name", [STUDY],
                     {"units": 0, "element_size": element_size, "tolerance": tolerance},
                     T_MESH)
        mesh_res = mesh_r.get("result") if isinstance(mesh_r.get("result"), dict) else {}
        ev["steps"]["create_mesh"] = {k: mesh_r.get(k) for k in
                                      ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["create_mesh"]["result"] = mesh_r.get("result")
        print("  [2] 建网格: ok=%s timed_out=%s wall=%ss element_count=%s"
              % (mesh_r.get("ok"), mesh_r.get("timed_out"), mesh_r.get("wall_seconds"),
                 mesh_res.get("element_count")))

        #: ④ ★★ 跑求解 —— 本探针的核心（★ T_RUN=1800）✓
        run_r = iso("run_analysis_by_name", [STUDY], {}, T_RUN)
        run_res = run_r.get("result") if isinstance(run_r.get("result"), dict) else {}
        ev["steps"]["run_analysis"] = {k: run_r.get(k) for k in
                                       ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["run_analysis"]["result"] = run_r.get("result")
        print("  [3] 跑求解: ok=%s **timed_out=%s** wall=%ss"
              % (run_r.get("ok"), run_r.get("timed_out"), run_r.get("wall_seconds")))
        print("      results_present=%s plot_count=%s"
              % (run_res.get("results_present"), run_res.get("plot_count")))

        #: ⑤ ★★★ **轮询结果读数**（★ 求解可能异步 ⇒ 判据是**结果**、不是返回码）
        poll = []
        if not run_res.get("results_present"):
            for i in range(POLL_MAX):
                time.sleep(POLL_EVERY)
                try:
                    res = sw_connect.safe_get_com_member(study, "Results")
                    cnt = None
                    if res is not None:
                        cnt = sw_connect.safe_get_com_member(res, "GetPlotCount")
                    poll.append({"i": i + 1, "elapsed_s": round((i + 1) * POLL_EVERY, 1),
                                 "results_present": res is not None, "plot_count": cnt})
                    print("      [poll %d] +%ss results=%s plot_count=%s"
                          % (i + 1, round((i + 1) * POLL_EVERY, 1), res is not None, cnt))
                    if res is not None and int(cnt or 0) > 0:
                        break
                except Exception as exc:                              # noqa: BLE001
                    poll.append({"i": i + 1, "error": str(exc)[:120]})
                    break
        ev["steps"]["results_poll"] = poll

        #: ⑥ ★ 终局回读：★ **重用契约里那一条**（`run_analysis_by_name` 走 `run_analysis_report`）
        #:   —— ★ **不自己搓读数器**（★ 它复跑一次 `RunAnalysis` 只为回读 `Results`/图数，
        #:   而求解已完成 ⇒ 秒级返回）✓
        final_r = iso("run_analysis_by_name", [STUDY], {}, 600)
        final_res = final_r.get("result") if isinstance(final_r.get("result"), dict) else {}
        ev["steps"]["final_readback"] = {k: final_r.get(k) for k in
                                         ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["final_readback"]["result"] = final_r.get("result")
        print("      [终局回读] results_present=%s plot_count=%s"
              % (final_res.get("results_present"), final_res.get("plot_count")))
        evi = sim.collect_study_evidence(sw)
        ev["steps"]["collect_evidence"] = {
            "ok": isinstance(evi, dict) and int(evi.get("study_count") or 0) >= 1,
            "study_count": evi.get("study_count"),
            "names": [s.get("name") for s in (evi.get("studies") or [])],
        }

        #: ⑦ 判据汇总
        plot_count = run_res.get("plot_count")
        if plot_count in (None, 0) and poll:
            plot_count = poll[-1].get("plot_count")
        #: ★ 终局回读优先（★ 它跑在轮询之后、读数最新）
        if final_res.get("plot_count") not in (None, 0):
            plot_count = final_res.get("plot_count")
        ev["★_timed_out"] = run_r.get("timed_out")
        ev["★_element_count"] = mesh_res.get("element_count")
        ev["★_results_present"] = bool(run_res.get("results_present")
                                       or final_res.get("results_present")
                                       or (poll and poll[-1].get("results_present")))
        ev["★_plot_count"] = plot_count
        ev["★_ok"] = bool(ev["★_results_present"] and int(plot_count or 0) > 0)
        ev["★_判据"] = ("★ ① element_count（网格读数）② results_present/plot_count/plot_names"
                        "（**解算结果读数**）③ timed_out ④ wall_seconds")
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
    finally:
        try:
            import sw_connect
            if doc is not None:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)                                    #: ★ 只关自己那份
        except Exception:                                             # noqa: BLE001
            pass

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ ★_timed_out =", ev.get("★_timed_out"), "· ★_element_count =", ev.get("★_element_count"),
          "· ★_results_present =", ev.get("★_results_present"), "· ★_plot_count =", ev.get("★_plot_count"),
          "· ★_ok =", ev.get("★_ok"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
