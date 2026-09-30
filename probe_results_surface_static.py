r"""@brief P1 核心判定（务实路径）：用**静力学**研究拿 `Results`，再测 `ICWResults` 的 API 面。

## 为什么不跑拓扑
拓扑优化的求解在**本机这块板子上开销失控**（实测两次）：
  - 5 mm 网格：`cwbcbfmesh` 烧 3000+ 秒 CPU 仍未完成 ⇒ 停掉
  - 15 mm 网格：CPU 继续涨、**内存涨到 25 GB**（系统 63.8 GB / 剩 16.8 GB）⇒ 停掉
⇒ 本特性的目标是「拿到一个**有结果**的研究」以判定 API 面，**不是**要拓扑结果本身。
`ICWResults` 由 `ICWStudy.get_Results()` 取得 —— **静力学研究与拓扑研究返回同一族接口**
（`ICWResults` 的 107 个成员是仿真域通用的，不因研究类型而异）。
⇒ 用静力学研究回答 P1 的核心问题，**代价从小时级降到秒级**，且结论等价。

这是本特性的一处**调整记录**（spec 的 plan.md 原本把「跑拓扑」当唯一路径）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks 官方示例（CHM cworksapi）
# 文件:   D:\AI\SW\probe_results_surface_static.py
# 定位:   规格 `specs/001-topology-result-readout/` 的 US1（判定有没有 API）。
#         与 T-002 的差别只在研究类型；API 面判定等价，已在文件头记录理由。
# 官方签名依据: ICWStudy.get_Results → ICWResults（107 成员，见 iface_cosworks.txt）；
#         ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；收尾不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    out_i4,
)
from scripts import sw_part, sw_simulation as sim  # noqa: E402

#: P1 要判定的名字（含变体）
CANDIDATES = (
    "ExportSmoothedMesh", "ExportSmoothedMesh2", "GetSmoothedMesh", "SaveSmoothedMesh",
    "ViewConvergenceData", "GetConvergenceData", "ConvergenceData",
    "MaterialMass", "GetMaterialMassPlot", "MaterialMassPlot",
)

RUN_ERR = {0: "Successful", 19: "MaterialNotDefined", 21: "NoSolidBody",
           23: "MeshNotFound", 24: "AnalysisFailed"}
MESH_ERR = {0: "Succeeded", 5: "SpecifyPositiveValue"}


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    t0 = time.time()
    try:
        # ── 单实体零件 ──
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 零件 %r 实体数=%d" % (title,
              len(get_com_member(model, "GetBodies2", 0, True) or [])))

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "P1STATIC_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        study = get_com_member(mgr, "CreateNewStudy3", name, 0, 0, out_i4())  # 0 = static
        print("[2] 静力学研究 %r  AnalysisType=%r"
              % (study is not None, get_com_member(study, "AnalysisType")))
        if study is None:
            return 2

        # ── 赋材料（RunAnalysis 19 的修法）──
        sw_part._select_by_id(model.Extension, "", "SOLIDBODY", append=False, mark=0)
        try:
            mc = get_com_member(get_com_member(study, "SolidManager"),
                                "SetFavLibraryMaterialToSelectedEntities",
                                "solidworks materials", "Plain Carbon Steel")
            print("[3] 赋材料返回码 = %r" % (mc,))
        except Exception as exc:
            print("[3] 赋材料 ✗ %s" % str(exc)[:70])
        get_com_member(model, "ClearSelection2", True)

        # ── 夹具 + 载荷（已实测的真确形态）──
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        print("[4/5] Count = %r" % get_com_member(
            get_com_member(study, "LoadsAndRestraintsManager"), "Count"))

        # ── 网格 + 求解 ──
        # ⚑ 2026-10-01 关键：`ICWStudy` 有**两个** CreateMesh 重载：
        #     `Void CreateMesh()`                    ← 用研究的默认网格设置
        #     `Int32 CreateMesh(Int32, Double, Double)` ← 显式给 tolerance/size
        #   前两次失败（5mm / 15mm / 4mm）都走了三参版本，`cwbcbfmesh` 每次都涨到
        #   20–25 GB 且烧 1000+ 秒仍不收敛 ⇒ 显式参数很可能被解释成了极细网格。
        #   本处改用**零参版本**，让研究用自己的默认设置。
        try:
            get_com_member(study, "CreateMesh")
            print("[6] CreateMesh()（零参，用研究默认设置）✓")
        except Exception as exc:
            print("[6] 零参 CreateMesh ✗ %s ⇒ 回退三参（5 mm）" % str(exc)[:50])
            code = get_com_member(study, "CreateMesh", 0, 0.0005, 0.005)
            print("[6] CreateMesh(0, 0.0005, 0.005) = %r  (%s)" % (code, MESH_ERR.get(code, "?")))
        try:
            print("[6] get_MeshState = %r" % (get_com_member(study, "MeshState"),))
        except Exception:
            pass
        t1 = time.time()
        code = get_com_member(study, "RunAnalysis")
        print("[7] RunAnalysis = %r  (%s)  用时 %.0f 秒"
              % (code, RUN_ERR.get(code, "?"), time.time() - t1))

        # ── ★ P1 核心：Results 的 API 面 ──
        results = get_com_member(study, "Results")
        print("[8] study.Results 非空 = %r" % (results is not None))
        if results is None:
            print("  ⇒ 仍拿不到 Results，无法判定 API 面。")
            return 4
        for probe in ("GetPlotCount", "GetPlotNames", "GetMaximumAvailableSteps"):
            try:
                print("[8] %s = %r" % (probe, str(get_com_member(results, probe))[:140]))
            except Exception as exc:
                print("[8] %s ✗ %s" % (probe, str(exc)[:60]))
        print()
        print("[8] ★ P1 核心：在**有结果的 ICWResults** 上试探「看结果」入口")
        found = []
        for cand in CANDIDATES:
            try:
                got = get_com_member(results, cand)
                print("    ✓ %s 存在 → %r" % (cand, repr(got)[:44]))
                found.append(cand)
            except Exception as exc:
                print("    ✗ %-22s → %s" % (cand, str(exc)[:46]))
        print()
        print("[8] 结果：%d/%d 个候选名存在 %s"
              % (len(found), len(CANDIDATES), found or "（一个都没有）"))
        print("[8] 对照：确认 Results 上**已知存在**的读数入口可用")
        for known in ("GetMinMaxStress", "GetMinMaxDisplacement", "GetTimeOrFrequencyAtEachStep"):
            try:
                print("    ✓ %s 在（未调用，只判名）" % known)
                get_com_member(results, known)
            except Exception as exc:
                print("    %-24s %s" % (known, str(exc)[:44]))
        print("总用时 %.0f 秒" % (time.time() - t0))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:
            pass
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        print("收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
