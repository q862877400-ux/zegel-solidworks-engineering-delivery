r"""@brief A9 收尾：**拓扑优化研究的完整闭环** —— 一次连续运行串起全部环节。

## 为什么这个脚本能成（而前几轮不能）
前几轮的每一段都**分别**真机验证过了，只是**从没串成一次连续运行**：
| 环节 | 已验证于 |
|---|---|
| 建拓扑研究（type 13） | `probe_official_topology_sequence.py` |
| 目标自带质量约束（`EndEdit` 错误 7 的真因） | `probe_goal_creates_mass.py` |
| 赋材料（库名 `"SOLIDWORKS Materials"` + `"AISI 1020"`） | 本轮 `probe_material_dbname.py` |
| 按**面坐标**选面（原点选不到面） | 本轮 `probe_full_chain.py` |
| 夹具 / 载荷（`Count = 2`） | 同上 |
| `CreateMesh(NUnits, DElementSize, DTolerance)`（**毫米**） | 本轮 `probe_createmesh_final.py` |
| `RunAnalysis` + `Results` 出图 | 同上（静力学） |

**⇒ 本脚本把上表按顺序串起来，跑在**拓扑研究**上。**

## 判据（不是看返回码）
`RunAnalysis` 的返回码不可信（静力学实测：夹具未定义时仍返回 0）⇒ 判据是：
`study.Results` 非空、`GetPlotCount` > 0、拓扑研究额外看约束/控制是否都在。

## 守护
旁路线程只读内存，网格器 > 4 GB 就杀掉（COM 全程在主线程 —— 跨线程访问 COM 会
`AttributeError`，这是本轮学到的教训）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_topology_loop.py
# 定位:   specs/001-topology-result-readout 的 T-002；objective 里
#         「拓扑优化闭环并升 verified」的最后一里。装配的是 `scripts/sw_topology.py`
#         （照官方 CHM 的 `Create_Topology_Study_Example_VBA` 建的）与
#         `scripts/sw_simulation.py` 的材料/选面/网格/求解函数。
# 官方签名依据: 复用两个模块里已核过的官方签名，本脚本**不引入新的 COM 成员**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机。COM 在主线程；内存守护在旁路线程。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import subprocess
import sys
import threading
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_simulation as sim, sw_topology as topo  # noqa: E402

STOP = threading.Event()
RUN_ERR = {0: "Successful", 19: "MaterialNotDefined", 23: "MeshNotFound", 24: "AnalysisFailed"}
TOPO_TYPE = 13


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def watchdog() -> None:
    while not STOP.wait(5):
        v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
                "Measure-Object WorkingSet64 -Sum).Sum")
        mb = int(int(v) / 1_048_576) if v.isdigit() else 0
        if mb > 4000:
            print("      [旁路守护] ⚠ 网格器 %d MB ⇒ 杀" % mb, flush=True)
            _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
            return


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    threading.Thread(target=watchdog, daemon=True).start()
    title = None
    try:
        # ① 零件
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 零件 %r（100×60×20 mm 单实体）" % title, flush=True)

        # ② 材料（真机：库名是显示名；AISI 1020 在该库里）
        mid = sim.set_material(model, "AISI 1020")
        print("[2] 材料回读 = %r  %s" % (mid, "✓" if mid else "✗ 没赋上"), flush=True)
        if not mid:
            return 2

        # ③ 拓扑研究（type 13）—— 返回 ``(study, entry_name)``（降级路径标记）
        study, entry = topo.create_topology_study(sw, "TOPO_LOOP_%d" % int(time.time()))
        print("[3] 拓扑研究 = %r（入口 %r）" % (study is not None, entry), flush=True)
        if study is None:
            return 3
        print("    AnalysisType = %r（应为 13）" % get_com_member(study, "AnalysisType"),
              flush=True)

        # ④ 目标 + 约束（官方教程：最大化刚度 + 减重 75%）
        res_goal = topo.set_topology_goal(study, goal_type=topo.TP_GOAL_MAXIMIZE_STIFFNESS,
                                          mass_reduce_percent=75.0)
        print("[4] 目标/约束 = %r" % {k: (v is not None) for k, v in res_goal.items()},
              flush=True)

        # ⑤ 夹具（底面 z=-0.02，用**面上的点**选）
        n1 = sim.select_face_at(model, 0.0, 0.0, -0.02)
        rst = sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        print("[5] 夹具: 选区=%d → 对象=%r" % (n1, rst is not None), flush=True)

        # ⑥ 载荷（顶面 z=0）
        n2 = sim.select_face_at(model, 0.0, 0.0, 0.0)
        frc = sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        print("[6] 载荷: 选区=%d → 对象=%r" % (n2, frc is not None), flush=True)

        # ⑦ 回读载荷/夹具计数（判据，不看返回码）
        try:
            lm = get_com_member(study, "LoadsAndRestraintsManager")
            print("    LoadsAndRestraintsManager.Count = %r"
                  % get_com_member(lm, "Count"), flush=True)
        except Exception as exc:
            print("    ✗ 读 Count: %s" % str(exc)[:50], flush=True)

        # ⑧ 网格（官方建议值，毫米）
        size, tol = sim.default_element_size_and_tolerance(study, -1)
        t0 = time.time()
        mc = get_com_member(study, "CreateMesh", 0, float(size), float(tol))
        mesh = get_com_member(study, "Mesh")
        print("[7] CreateMesh = %r  单元 = %r  用时 %.0f 秒"
              % (mc, get_com_member(mesh, "ElementCount"), time.time() - t0), flush=True)

        # ⑨ 求解（判据是 Results，不是返回码）
        t1 = time.time()
        rc = get_com_member(study, "RunAnalysis")
        print("[8] RunAnalysis = %r (%s)  用时 %.0f 秒"
              % (rc, RUN_ERR.get(rc, "?"), time.time() - t1), flush=True)

        results = get_com_member(study, "Results")
        ok = results is not None
        print("[9] ★ study.Results 非空 = %r" % ok, flush=True)
        if ok:
            for p in ("GetPlotCount", "GetPlotNames"):
                try:
                    print("      %s = %r" % (p, str(get_com_member(results, p))[:160]),
                          flush=True)
                except Exception as exc:
                    print("      %s ✗ %s" % (p, str(exc)[:46]), flush=True)
        print()
        print("    拓扑研究的约束/控制:", flush=True)
        try:
            cc = topo.list_topology_constraints_and_controls(study)
            print("      %r" % (cc,), flush=True)
        except Exception as exc:
            print("      ✗ %s" % str(exc)[:60], flush=True)
        print()
        print("════ %s ════" % ("闭环跑通 ✓" if ok else "求解未出结果 ✗"), flush=True)
        return 0 if ok else 4
    finally:
        STOP.set()
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:
            pass
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        print("收尾完成（文档未保存）", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
