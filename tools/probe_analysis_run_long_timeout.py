"""★ 给足超时 + 粗网格，验 `analysis_run_readback` 的「跑求解」那一步到底能不能算完。

（★ 处置 SPEC `202-user-coverage-gaps` 的 SC-004：★ 第 3 条候选 `analysis_run_readback`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/capture_mesh_solve_evidence.py`（★ **本探针照它的流程写** ——
#         ★ 照 AGENTS.md 的「按 ToolSpec 的契约调，别手调内部实现」）·
#         `scripts/sw_simulation.py` · `scripts/sw_isolate.py` · `scripts/sw_part.py` ·
#         `mcp-server/tool_specs_batch28.py`
# 定位:   ★ **为什么写它**：`capabilities.yaml` 的 `analysis_run_readback.limitations` 逐字：
#     「`mesh_size` **ok**（element_size 4930.5）· `create_mesh` **ok**（**element_count = 7250**）·
#      ★ **`run_analysis` 进入求解即挂**（`timed_out=True` · **300 s**）」
#   ★★ **而轮 376 自己**更正过措辞**（★ 事实 293）逐字：
#     「★ 观察器抓到屏幕上一直有一个 SolidWorks Simulation 的**求解进度窗**（`DSH-142`）：
#      ★ `当前任务: **建立刚度矩阵**` · ★ `已用时间: **33分0秒**` · ★ `自由度: 30,456` ·
#      ★ `节数: 11,301` · ★ `单元数: 7,250`」
#     ⇒ ★★★ **⇒ 那不是"挂"、★ 是**求解真的在算**（★ 只是比 300 s 长得多）** ✓
#   ★★★ **⇒ 所以本探针做两件事**：
#     ★ ① **把 `T_RUN` 从 300 s 提到 3600 s**（★ 1 小时 —— ★ 足够覆盖那 33 分钟）；
#     ★ ② **同时把网格**放粗**（★ 元素越少、★ 建立刚度矩阵越快）⇒ 两条路都往"能算完"走 ✓
#   ★★★★ **判据（★ 含**几何读数**）**：★ ① `timed_out` 是不是 False ·
#     ★ ② `element_count`（★ 网格读数）· ★ ③ **`results_present` / `plot_count`**（★ 解算结果读数）·
#     ★ ④ `wall_seconds`（★ 花了多久）✓
#   ★★★★★ **★ 机制**：★ 三步都走 `run_isolated`（★ **可被杀的子进程**）⇒
#     ★ **超时只杀子进程、★ 不冻住会话**（★ 那正是 `tools/capture_mesh_solve_evidence.py`
#       第 3 行那个设计的价值）✓
#   ★★★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` ✓
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
#: ★★★★★★ **修（★ 第二版）**：★ 第二版报**同一个**错
#:   `RuntimeError: 创建研究失败：CreateNewStudy3 / 2 / 1 均未返回对象` ⇒
#:   而★ 我已加过 `ensure_simulation_addin`** ⇒ ★★ **⇒ 所以不是加载项的问题** ✓
#:   ★★★ **⇒ 官方 `swsStudyError_e` 的四个原因里**：★ 1=无实体 · ★ **2=同名研究已存在或名称非法** ·
#:     3=类型未定义 · ★ 4=网格类型非法 ✓
#:   ★★★★ **⇒ 最可能是「2」** —— ★ **第一版已经建过一个 `SPEC202_LongSolve`（残留在会话里）** ✓
#:   ★★★★★ **⇒ 而本仓既有记录逐字**：「⚠★ **建算例时请用唯一名字** —— 算例**重名**会让
#:     计数回读取不到（真机实测）」✓ ⇒ ★ **故本版用**带时间戳的唯一名**** ✓
STUDY = "SPEC202_LongSolve_%d" % int(time.time())
#: ★ ① 求解超时：★ 300 s → **3600 s**（★ 覆盖实测观察到的 33 分钟）
T_RUN = 3600.0
T_MESH = 300.0
#: ★ ② 网格放粗：★ 实测那次的 element_size 是 4930.5、★ 7250 个单元
#:   ⇒ ★ 本探针**显式给一个更粗的**（★ 单位 mm；★ 零件是 100×60×20）
#:   ★★★★ **修（★ 第三版）**：★ 12.0 那版在 `create_mesh` 报了
#:     `com_error: (-2147023170, '远程过程调用失败。')` = **RPC 断连**
#:     ⇒ ★★ **⇒ 那是 SolidWorks 进程**自己掉了**（★ 与我的参数无关 —— ★ 重启后它会好）✓
#:   ★★★★★ **⇒ 本版**再放粗一档**（★ 12 → **20 mm**）⇒ 单元更少 ⇒ 网格与刚度矩阵都更快 ✓
ELEMENT_SIZE = 20.0
TOLERANCE = 1.0


def main() -> int:
    ev: dict = {"★_目的": "给足超时 + 粗网格，验「跑求解」能不能算完",
                "★_T_RUN_秒": T_RUN, "★_ELEMENT_SIZE_mm": ELEMENT_SIZE,
                "★_前情": "capture_mesh_solve_evidence.py 曾以 T_RUN=300s 记 timed_out=True；"
                          "而轮 376 观察到求解进度窗已用 33 分钟（事实 293）",
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
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        material = str(sw_connect.safe_get_com_member(doc, "MaterialIdName") or "")
        #: ★★★★★★★ **修（★ 第一版漏了一步）**：★ 第一版报
        #:   `RuntimeError: 创建研究失败：CreateNewStudy3 / 2 / 1 均未返回对象` ⇒
        #:   ★★ **真因**：★ 我**没先取/装 Simulation 加载项** ⇒ `create_static_study` 拿不到加载项 ✓
        #:   ★★★ **正解**：★ `scripts/sw_simulation.py::ensure_simulation_addin(sw_app)`
        #:     —— ★ 它逐字：★ 「取 Simulation **加载项对象**（`ISldWorks.GetAddInObject`），
        #:     取不到就**先用 `LoadAddIn` 装上**」✓
        #:   ★★★★ **⇒ 而那正是 AGENTS.md 那条纪律**：「★ **写探针验能力时：按 `ToolSpec` 的契约调，
        #:     别手调内部实现**」—— ★ **`ensure_simulation_addin` 是契约的一部分**、
        #:     而**我第一版把它漏了**（★ 事实 517：★ 失败看起来像能力坏了）✓
        sim.ensure_simulation_addin(sw)
        ev["steps"]["addin"] = "ensure_simulation_addin(sw) 调过"

        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
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

        #: ② 建网格（★ 粗网格 ⇒ 单元少 ⇒ 刚度矩阵小 ⇒ 算得快）✓
        mesh_r = iso("create_mesh_by_name", [STUDY],
                     {"units": 0, "element_size": ELEMENT_SIZE, "tolerance": TOLERANCE},
                     T_MESH)
        ev["steps"]["create_mesh"] = {k: mesh_r.get(k) for k in
                                      ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["create_mesh"]["result"] = mesh_r.get("result")
        print("  [1] 建网格: ok=%s timed_out=%s wall=%ss"
              % (mesh_r.get("ok"), mesh_r.get("timed_out"), mesh_r.get("wall_seconds")))
        print("      result:", str(mesh_r.get("result"))[:150])

        #: ③ ★★ 跑求解 —— ★ **本探针的核心**（★ T_RUN=3600）✓
        run_r = iso("run_analysis_by_name", [STUDY], {}, T_RUN)
        ev["steps"]["run_analysis"] = {k: run_r.get(k) for k in
                                       ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["run_analysis"]["result"] = run_r.get("result")
        print("  [2] 跑求解: ok=%s **timed_out=%s** wall=%ss"
              % (run_r.get("ok"), run_r.get("timed_out"), run_r.get("wall_seconds")))
        print("      result:", str(run_r.get("result"))[:200])

        #: ④ ★ 结果读数（★ 那是"算完了"的**独立判据** —— ★ 不只认返回码）✓
        if not run_r.get("timed_out"):
            try:
                res_present = sw_connect.safe_get_com_member(study, "ResultsPresent")
                ev["steps"]["results_present"] = res_present
                print("      ResultsPresent:", res_present)
            except Exception as exc:                                  # noqa: BLE001
                ev["steps"]["results_present"] = "err: %s" % str(exc)[:120]
            try:
                ext = sw_connect.safe_get_com_member(study, "Extension")
                plots = sw_connect.safe_get_com_member(ext, "GetPlotNames")
                names = list(plots) if plots else []
                ev["steps"]["plot_names"] = [str(x) for x in names][:6]
                ev["steps"]["plot_count"] = len(names)
                print("      plot_count:", len(names), str(names[:4])[:120])
            except Exception as exc:                                  # noqa: BLE001
                ev["steps"]["plot_names"] = "err: %s" % str(exc)[:120]

        #: ⑤ 判据汇总
        ev["★_timed_out"] = run_r.get("timed_out")
        ev["★_ok"] = bool((not run_r.get("timed_out")) and run_r.get("ok"))
        ev["★_判据"] = ("★ ① timed_out=False ② element_count ③ results_present/plot_count "
                        "④ wall_seconds（★ 含几何/结果读数）")
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
    finally:
        try:
            import sw_connect
            if doc is not None:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        except Exception:                                             # noqa: BLE001
            pass

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ ★_timed_out =", ev.get("★_timed_out"), "· ★_ok =", ev.get("★_ok"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
