r"""@brief A9 关键验证：`CreateMesh` 的**正确参数顺序**。

## 突破的由来
前七次都失败。第八次去解包 **VB6 版 API CHM**（`lang\english\api\cworksapivb6.chm`，
1.8 MB / 3000 页）—— 那里有**每个方法一页的 VBA 签名**，含**参数名**：

    CosmosWorksLib~CWStudy~CreateMesh.html
      Public Function CreateMesh( _
          ByVal NUnits As Long, _          ← 第 1 参是**单位**
          ByVal DElementSize As Double, _  ← 第 2 参是**单元尺寸**
          ByVal DTolerance As Double _     ← 第 3 参是**容差**
      ) As Long

**⇒ 我前七次一直按 `(meshType, tolerance, size)` 传 ⇒ `ElementSize`/`Tolerance` **前后颠倒**，
且第 1 参根本不是网格类型。**这就是「19.5M 单元」的成因**：
把 4.9339 当成了 **Tolerance**（容差），而真正的 ElementSize 只有 0.2467。

对照同族页（都已读到）：
    GetDefaultElementSizeAndTolerance(NUnits As Long, ByRef DElementSize, ByRef DTolerance)
    CWMesh.ElementSize As Double / CWMesh.Tolerance As Double / CWMesh.Unit As Long

**⇒ 本脚本按正确顺序调用，并**读 `mesh.Unit` 作为第 1 参**（不自选单位）。**

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks 官方 Simulation **VB6 类型库 CHM**（方法签名页）
# 文件:   D:\AI\SW\probe_createmesh_order.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步）；铁律 4「签名三源互证」——
#         本案里 CHM 的 VBA 签名是**唯一**给出参数名的源（反射只给类型，用户手册只讲界面）。
# 官方签名依据: 见上（`cworksapivb6.chm` 的 `CosmosWorksLib~CWStudy~CreateMesh` 页）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格。带内存守护（覆盖 mesh 与 run 两阶段）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import subprocess
import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

import pythoncom  # noqa: E402
from win32com.client import VARIANT  # noqa: E402

from scripts.sw_connect import connect_solidworks, get_com_member, new_document, out_i4  # noqa: E402
from scripts import sw_part, sw_simulation as sim  # noqa: E402

MEM_LIMIT_MB = 6000
SYS_FREE_MIN_GB = 8.0
TOTAL_TIMEOUT_S = 420
MESH_ERR = {0: "Succeeded", 3: "ElementSizeTooSmall", 4: "ElementSizeTooBig",
            5: "SpecifyPositiveValue"}
RUN_ERR = {0: "Successful", 19: "MaterialNotDefined", 23: "MeshNotFound", 24: "AnalysisFailed"}


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def guard(tag: str) -> bool:
    v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
            "Measure-Object WorkingSet64 -Sum).Sum")
    mb = int(int(v) / 1_048_576) if v.isdigit() else 0
    v2 = _ps("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory")
    gb = int(v2) / 1_048_576 if v2.isdigit() else 99.0
    bad = mb > MEM_LIMIT_MB or gb < SYS_FREE_MIN_GB
    print("    [守护 %-14s] 网格器=%5d MB 系统=%.1f GB%s"
          % (tag, mb, gb, "  ⚠" if bad else ""), flush=True)
    if bad:
        _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
    return not bad


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 零件 %r（100×60×20 mm）" % title, flush=True)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "ORDER_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        study = get_com_member(mgr, "CreateNewStudy3", name, 0, 0, out_i4())
        print("[2] 静力学研究 %r" % (study is not None), flush=True)
        if study is None:
            return 2

        sw_part._select_by_id(model.Extension, "", "SOLIDBODY", append=False, mark=0)
        get_com_member(get_com_member(study, "SolidManager"),
                       "SetFavLibraryMaterialToSelectedEntities",
                       "solidworks materials", "Plain Carbon Steel")
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        print("[3] 材料 + 夹具 + 载荷 就绪", flush=True)

        mesh = get_com_member(study, "Mesh")
        print()
        print("=== mesh.Unit（第 1 参就用它，不自选）===", flush=True)
        try:
            raw_unit = get_com_member(mesh, "Unit")
        except Exception as exc:
            print("    读 Unit 失败: %s" % str(exc)[:50], flush=True)
            raw_unit = None
        print("    mesh.Unit（原始）= %r   （swsUnit_e: SI=0 English=1 Metric=2）" % (raw_unit,), flush=True)
        # ⚑ `Unit = -1` 是「未设置」，不是合法枚举；`GetDefault*` 接受 -1，
        #   但 `CreateMesh` 不接受（实测：传 -1 抛 `<unknown>.CreateMesh`）。
        #   ⇒ 传合法值。文档是毫米 ⇒ Metric=2；由环境变量可覆盖以便对照。
        import os as _os
        unit = int(_os.environ.get("MESH_UNIT", "2"))
        print("    ⇒ 本次 CreateMesh 用 unit=%d（可用 MESH_UNIT 覆盖）" % unit, flush=True)

        # 官方建议值（用同一个 unit 去问，保证口径一致）
        vs = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
        vt = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
        get_com_member(mesh, "GetDefaultElementSizeAndTolerance", int(unit), vs, vt)
        print("    官方建议（unit=%r）: ElementSize=%r  Tolerance=%r"
              % (unit, vs.value, vt.value), flush=True)
        size, tol = float(vs.value), float(vt.value)

        # ── ★ 正确顺序：CreateMesh(NUnits, DElementSize, DTolerance) ──
        print()
        print("=== ★ CreateMesh(unit=%r, ElementSize=%r, Tolerance=%r) —— **正确顺序** ==="
              % (unit, size, tol), flush=True)
        res = {"mesh": None, "run": None, "exc": None, "cnt": None, "nds": None}
        t0 = time.time()

        def _work():
            try:
                res["mesh"] = get_com_member(study, "CreateMesh",
                                             int(unit), float(size), float(tol))
                res["cnt"] = get_com_member(mesh, "ElementCount")
                res["nds"] = get_com_member(mesh, "NodeCount")
                res["run"] = get_com_member(study, "RunAnalysis")
            except Exception as exc:
                res["exc"] = str(exc)[:100]

        import threading
        th = threading.Thread(target=_work, daemon=True)
        th.start()
        while th.is_alive():
            time.sleep(5)
            el = time.time() - t0
            if not guard("mesh+run %.0fs" % el):
                print("    ⇒ 守护触发，已中止", flush=True)
                return 3
            if el > TOTAL_TIMEOUT_S:
                print("    ⇒ 超 %ds 主动中止" % TOTAL_TIMEOUT_S, flush=True)
                _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
                return 4
        print("    CreateMesh = %r (%s)   用时 %.0f 秒"
              % (res["mesh"], MESH_ERR.get(res["mesh"], "?"), time.time() - t0), flush=True)
        print("    ★ ElementCount = %r   NodeCount = %r" % (res["cnt"], res["nds"]), flush=True)
        print("    RunAnalysis = %r (%s)" % (res["run"], RUN_ERR.get(res["run"], "?")), flush=True)
        if res["exc"]:
            print("    异常: %s" % res["exc"], flush=True)

        results = get_com_member(study, "Results")
        print()
        print("=== 结果 ===", flush=True)
        print("    study.Results 非空 = %r" % (results is not None), flush=True)
        if results is not None:
            for p in ("GetPlotCount", "GetPlotNames"):
                try:
                    print("    %s = %r" % (p, str(get_com_member(results, p))[:110]), flush=True)
                except Exception as exc:
                    print("    %s ✗ %s" % (p, str(exc)[:50]), flush=True)
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
        print("收尾完成（文档未保存）", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
