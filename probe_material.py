r"""@brief A9 第九次：**材料赋值**（RunAnalysis=19 的卡点）。

## 已知（第八次尝试的结论）
网格已通（`CreateMesh(0, 4.9339, 0.2467)` → 7,219 单元），但
`RunAnalysis` 返回 **19** = `swsRunAnalysisErrorMaterialNotDefined`，
而材料赋值调用本身返回 0。

## 排查方向（反射里已找到材料入口）
    ICWSolidBody.SetLibraryMaterial(String, String)    ← 库名 + 材料名
    ICWSolidBody.get_MaterialName() / set_MaterialName(String)
    ICWStudy.SolidManager.SetFavLibraryMaterialToSelectedEntities(String, String)
                                                       ← 我一直在用的那个，**依赖选中集**
**怀疑**：选实体那一步没真的选中 —— 现在传的是空名
`_select_by_id(ext, "", "SOLIDBODY", …)`。

## 本脚本做法
**先查明到底哪个环节断了**，而不是换写法乱试：
1. 列出 `study.SolidManager` 上的实体与它们的 `MaterialName`（**改之前**）
2. 试三种赋值路径，**每次都回读 `MaterialName`** 判断是否真的生效
3. 若材料生效，再 `CreateMesh` + `RunAnalysis`，看 19 是否消失

**守护**：旁路线程读内存，超阈值杀网格器（COM 全程在主线程）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ 反射（`iface_cosworks.txt`）
# 文件:   D:\AI\SW\probe_material.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步的最后一段）。
# 官方签名依据: ICWSolidBody.SetLibraryMaterial(String, String) /
#         get_MaterialName / set_MaterialName；ICWSolidManager 的实体枚举
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机。COM 在主线程；内存守护在旁路线程。未在本机实测跑通（本脚本即为此而写）。
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

from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4  # noqa: E402
from scripts import sw_part, sw_simulation as sim  # noqa: E402

STOP = threading.Event()
RUN_ERR = {0: "Successful", 19: "MaterialNotDefined", 23: "MeshNotFound", 24: "AnalysisFailed"}


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
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 零件 %r" % title, flush=True)

        # ① 先看**零件级**材料（不是研究级）
        print()
        print("=== 零件级材料（改之前）===", flush=True)
        for path in ("MaterialIdName", "MaterialUserName"):
            try:
                print("    model.%-18s = %r" % (path, get_com_member(model, path)), flush=True)
            except Exception as exc:
                print("    model.%-18s ✗ %s" % (path, str(exc)[:44]), flush=True)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "MAT_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        study = get_com_member(mgr, "CreateNewStudy3", name, 0, 0, out_i4())
        print("[2] 静力学研究 %r" % (study is not None), flush=True)
        if study is None:
            return 2

        # ② 看 SolidManager 暴露了什么
        print()
        print("=== study.SolidManager 的成员探测 ===", flush=True)
        sm = get_com_member(study, "SolidManager")
        print("    SolidManager 非空 = %r" % (sm is not None), flush=True)
        for p in ("GetSolidBodyCount", "SolidBodyCount", "Count", "GetMaterialName"):
            try:
                print("    %-20s = %r" % (p, get_com_member(sm, p)), flush=True)
            except Exception as exc:
                print("    %-20s ✗ %s" % (p, str(exc)[:42]), flush=True)

        # ③ 试三种赋材料路径，**每次回读**
        print()
        print("=== 三条赋材料路径（每条都回读研究级与零件级）===", flush=True)

        def probe_material(tag: str) -> None:
            for where, obj, p in (("study", study, "MaterialName"),
                                  ("model", model, "MaterialIdName")):
                try:
                    print("      %-6s.%-14s = %r" % (where, p, get_com_member(obj, p)),
                          flush=True)
                except Exception as exc:
                    print("      %-6s.%-14s ✗ %s" % (where, p, str(exc)[:34]), flush=True)

        # 路径 1：沿用旧写法（选 SOLIDBODY，空名）
        sw_part._select_by_id(model.Extension, "", "SOLIDBODY", append=False, mark=0)
        try:
            r = get_com_member(sm, "SetFavLibraryMaterialToSelectedEntities",
                               "solidworks materials", "Plain Carbon Steel")
            print("    路径1 选中+SetFavLibraryMaterialToSelectedEntities → %r" % (r,), flush=True)
        except Exception as exc:
            print("    路径1 ✗ %s" % str(exc)[:60], flush=True)
        get_com_member(model, "ClearSelection2", True)
        probe_material("路径1后")

        # 路径 2：直接在零件上设（IModelDocExtension.SetMaterialPropertyName2）
        try:
            ext = get_com_member(model, "Extension")
            r2 = get_com_member(ext, "SetMaterialPropertyName2", "", "Plain Carbon Steel",
                                "solidworks materials")
            print("    路径2 Extension.SetMaterialPropertyName2 → %r" % (r2,), flush=True)
        except Exception as exc:
            print("    路径2 ✗ %s" % str(exc)[:60], flush=True)
        probe_material("路径2后")

        # 路径 3：选中实体后用 SetLibraryMaterial（若 SolidManager 暴露实体对象）
        try:
            body = get_com_member(sm, "GetSolidBodyAt", 0)
            print("    SolidManager.GetSolidBodyAt(0) = %r" % (body is not None), flush=True)
            if body is not None:
                r3 = get_com_member(body, "SetLibraryMaterial",
                                    "solidworks materials", "Plain Carbon Steel")
                print("    路径3 body.SetLibraryMaterial → %r" % (r3,), flush=True)
        except Exception as exc:
            print("    路径3 ✗ %s" % str(exc)[:60], flush=True)
        probe_material("路径3后")

        # ④ 夹具 + 载荷 + 网格 + 求解
        print()
        print("=== 夹具 + 载荷 + 网格 + 求解 ===", flush=True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)

        size, tol = sim.default_element_size_and_tolerance(study, -1)
        print("    官方建议 size=%.4f tol=%.4f（毫米）" % (size, tol), flush=True)
        t0 = time.time()
        mc = get_com_member(study, "CreateMesh", 0, float(size), float(tol))
        mesh = get_com_member(study, "Mesh")
        print("    CreateMesh = %r   单元数=%r   用时 %.0f 秒"
              % (mc, get_com_member(mesh, "ElementCount"), time.time() - t0), flush=True)
        t1 = time.time()
        rc = get_com_member(study, "RunAnalysis")
        print("    ★ RunAnalysis = %r (%s)   用时 %.0f 秒"
              % (rc, RUN_ERR.get(rc, "?"), time.time() - t1), flush=True)
        res = get_com_member(study, "Results")
        print("    ★ study.Results 非空 = %r" % (res is not None), flush=True)
        if res is not None:
            for p in ("GetPlotCount", "GetPlotNames"):
                try:
                    print("      %s = %r" % (p, str(get_com_member(res, p))[:120]), flush=True)
                except Exception as exc:
                    print("      %s ✗ %s" % (p, str(exc)[:46]), flush=True)
        return 0
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
