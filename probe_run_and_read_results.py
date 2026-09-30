r"""@brief T-002 修正版：赋材料 + 正网格尺寸后跑通拓扑优化，拿到真实结果。

前一轮的两条错误码（本文件即为其修正）：
```
CreateMesh(0, 0.0, 0.0) → 5 = swsStudyErrorSpecifyPositiveValue      ← 尺寸必须为正
RunAnalysis()           → 19 = swsRunAnalysisErrorMaterialNotDefined ← 没赋材料
```
错误码真源：`D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt` 的
`swsStudyMeshError_e` 与 `swsRunAnalysisError_e`。

官方赋材料调用（`_raw\cworksapi\Create_Topology_Study_Example_VBA.txt`）：
```vb
Set StudyObj = StudyManagerObj.GetStudy(1)
Set SolidManagerObj = StudyObj.SolidManager()
ErrorCodeObj = SolidManagerObj.SetFavLibraryMaterialToSelectedEntities("solidworks materials", "Plain Carbon Steel")
```

# ── 来源 ──
# 仓库:   本项目自身（真机全流程）+ SolidWorks 官方示例（CHM cworksapi）
# 文件:   D:\AI\SW\probe_run_and_read_results.py
# 定位:   规格 `specs/001-topology-result-readout/tasks.md` 的 T-002；
#         满足 spec 的 FR-001（必须在真的跑过优化的研究上做运行期试探）。
# 官方签名依据: ICWSolidManager.SetFavLibraryMaterialToSelectedEntities(String, String)；
#         ICWStudy.CreateMesh(Int32, Double, Double) / RunAnalysis()；
#         enum_cosworks.txt 的 swsStudyMeshError_e / swsRunAnalysisError_e
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且**会跑求解**。收尾不保存。
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
    create_empty_dispatch_variant,
    get_com_member,
    new_document,
    out_i4,
    set_com_member,
)
from scripts import sw_part, sw_simulation as sim, sw_topology as topo  # noqa: E402

MATERIAL_ERR = {
    0: "Succeeded", 1: "SetOperationNotSupported", 2: "InvalidConstraintValue",
}
MESH_ERR = {
    0: "Succeeded", 1: "NoValidShells", 2: "NoSolidBody", 3: "ElementSizeTooSmall",
    4: "ElementSizeTooBig", 5: "SpecifyPositiveValue", 6: "SpecifyElementSizeScaleFactor",
    7: "SpecifyToleranceScaleFactor",
}
RUN_ERR = {
    0: "Successful", 19: "MaterialNotDefined", 21: "NoSolidBody", 22: "AuthorizationFailed",
    23: "MeshNotFound", 24: "AnalysisFailed",
}


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    t0 = time.time()
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        bodies = get_com_member(model, "GetBodies2", 0, True)
        print("[1] 零件 %r  实体数=%d" % (title, len(bodies) if bodies else 0))

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "RUN2_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        study = get_com_member(mgr, "CreateNewStudy3", name, 13, 0, out_i4())
        print("[2] 拓扑研究 %r  AnalysisType=%r"
              % (study is not None, get_com_member(study, "AnalysisType")))
        if study is None:
            return 2

        # ── 3. 目标 + 自带质量约束 ──
        r = topo.set_topology_goal(study, mass_reduce_percent=75.0)
        print("[3] 目标+质量约束 ✓ 复用自带=%r" % r.get("mass_constraint_reused"))

        # ── 3b. ★ 赋材料（官方：SetFavLibraryMaterialToSelectedEntities）──
        sw_part._select_by_id(model.Extension, "", "SOLIDBODY", append=False, mark=0)
        sel = get_com_member(get_com_member(model, "SelectionManager"),
                             "GetSelectedObjectCount2", -1)
        print("[3b] 选中实体数 = %r" % sel)
        solid_mgr = get_com_member(study, "SolidManager")
        code = None
        try:
            code = get_com_member(solid_mgr, "SetFavLibraryMaterialToSelectedEntities",
                                  "solidworks materials", "Plain Carbon Steel")
        except Exception as exc:
            print("[3b] 赋材料抛异常: %s" % str(exc)[:70])
        print("[3b] 赋材料返回码 = %r  (%s)" % (code, MATERIAL_ERR.get(code, "?")))
        get_com_member(model, "ClearSelection2", True)

        # ── 4/5. 夹具 + 载荷 ──
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        lrm = get_com_member(study, "LoadsAndRestraintsManager")
        print("[4/5] Count = %r" % get_com_member(lrm, "Count"))

        # ── 6. 网格（★ 尺寸必须为正）──
        size = 0.005   # 5 mm
        tol = size / 20.0
        code = get_com_member(study, "CreateMesh", 0, float(tol), float(size))
        print("[6] CreateMesh(tol=%.4f, size=%.4f) = %r  (%s)"
              % (tol, size, code, MESH_ERR.get(code, "?")))

        # ── 7. 求解（耗时）──
        print("[7] RunAnalysis…（最多等 20 分钟）")
        t1 = time.time()
        code = get_com_member(study, "RunAnalysis")
        print("[7] RunAnalysis = %r  (%s)  用时 %.0f 秒"
              % (code, RUN_ERR.get(code, "?"), time.time() - t1))

        # ── 8. 结果 ──
        results = get_com_member(study, "Results")
        print("[8] study.Results 非空 = %r" % (results is not None))
        if results is not None:
            for probe in ("GetPlotCount", "GetPlotNames"):
                try:
                    print("[8] %s = %r" % (probe, str(get_com_member(results, probe))[:120]))
                except Exception as exc:
                    print("[8] %s ✗ %s" % (probe, str(exc)[:60]))
            # ★ P1 的核心试探：三个目标名在**有结果的对象**上试
            print("[8] === P1 核心：ICWResults 上试探「看结果」三个入口 ===")
            for cand in ("ExportSmoothedMesh", "GetSmoothedMesh", "ExportSmoothedMesh2",
                         "ViewConvergenceData", "MaterialMass", "GetMaterialMassPlot",
                         "GetConvergenceData", "SaveSmoothedMesh"):
                try:
                    got = get_com_member(results, cand)
                    print("    ✓ %s 存在 → %r" % (cand, repr(got)[:40]))
                except Exception as exc:
                    msg = str(exc)
                    print("    ✗ %s → %s" % (cand, msg[:52]))
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
