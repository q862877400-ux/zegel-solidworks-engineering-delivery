r"""@brief A9 第六次尝试 —— **按文档点名的那一项**：关掉 `AutomaticTransition`。

## 这一轮的推理链（每一步都有出处）
1. 前四次换参数组合全部同一现象 ⇒ 按纪律停下**查文档**（此前一直没读 Simulation 用户手册）
2. 解包 `lang\english\cworks.chm`（16.8 MB / **2052 页**）到 `C:\cworks_manual`
3. 读 `IDC_HELP_MESHSOLID.htm`（网格 PropertyManager）⇒ 得知：
   - 默认 mesher 是 **Blended curvature-based**；`Global Size` / `Tolerance`
     **「Available for standard mesh only」**
   - **`Automatic transition`**（仅 standard mesh）「automatically applies mesh controls to
     small features, holes, fillets … **Clear Automatic transition before meshing large
     models … to avoid generating large numbers of elements**」
4. 读 `c_Meshing_Tips.htm` 再次印证：「`Automatic transition` can result in generating an
   **unnecessarily large number of elements**」
5. 反射里找到确切入口：`set_AutomaticTransition(Int32)` / `set_AutomaticTransition2(Boolean)`

## 第五次尝试的两个教训（本脚本据此修正）
- **`cwbcbfmesh` 是网格器（CWB CBF Mesh），不是求解器** ⇒ 内存爆炸发生在 **`CreateMesh`**
- 我上次只给 `RunAnalysis` 加守护，而探针**卡在 `CreateMesh` 里** ⇒ 守护从未运行
  ⇒ **本次把 mesh+run 整体放进后台线程，主线程统一守护**

## 内存守护
`cwbcbfmesh` 内存 > 6 GB 或系统可用 < 8 GB ⇒ 立刻停掉网格器并退出。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks 官方 Simulation 用户手册（CHM）
# 文件:   D:\AI\SW\probe_automatic_transition.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步）。
# 官方签名依据: ICWStudy.set_AutomaticTransition(Int32) / set_MesherType(Int32) /
#         SetMeshOption(Int32) / SetMeshQuality(Int32) / CreateMesh(Int32, Double, Double)
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格。**带内存守护**（覆盖 mesh 与 run 两阶段）。
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

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    out_i4,
    set_com_member,
)
from scripts import sw_part, sw_simulation as sim  # noqa: E402

MESHER_STANDARD = 0
MESH_SOLID = 0
MEM_LIMIT_MB = 6000
SYS_FREE_MIN_GB = 8.0
TOTAL_TIMEOUT_S = 480


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def solver_mem_mb() -> int:
    v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
            "Measure-Object WorkingSet64 -Sum).Sum")
    return int(int(v) / 1_048_576) if v.isdigit() else 0


def sys_free_gb() -> float:
    v = _ps("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory")
    return int(v) / 1_048_576 if v.isdigit() else 99.0


def guard(label: str) -> bool:
    mb, gb = solver_mem_mb(), sys_free_gb()
    bad = mb > MEM_LIMIT_MB or gb < SYS_FREE_MIN_GB
    print("    [守护 %-14s] 网格器=%5d MB  系统可用=%5.1f GB%s"
          % (label, mb, gb, "  ⚠ 触发" if bad else ""), flush=True)
    if bad:
        _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
        return False
    return True


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
        print("[1] 零件 %r" % title, flush=True)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "AT_%d" % int(time.time())
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

        # ── ★ 读当前网格选项 ──
        print()
        print("=== 读网格选项（文档点名 AutomaticTransition 是元凶）===", flush=True)
        for prop in ("AutomaticTransition", "AutomaticTransition2", "MesherType",
                     "MeshType", "MeshQuality"):
            try:
                print("    %-22s = %r" % (prop, get_com_member(study, prop)), flush=True)
            except Exception as exc:
                print("    %-22s ✗ %s" % (prop, str(exc)[:44]), flush=True)

        # ── ★ 关掉它 + 设 Standard mesher ──
        print()
        print("=== 设 AutomaticTransition=0（关）+ MesherType=0（Standard）===", flush=True)
        for prop, val in (("AutomaticTransition", 0), ("AutomaticTransition2", False),
                          ("MesherType", MESHER_STANDARD)):
            try:
                set_com_member(study, prop, val)
                back = get_com_member(study, prop)
                print("    %-22s ← %r  回读=%r" % (prop, val, back), flush=True)
            except Exception as exc:
                print("    %-22s ✗ %s" % (prop, str(exc)[:60]), flush=True)

        # ── 网格 + 求解：**整体放后台线程**，主线程守护 ──
        print()
        size, tol = 0.008, 0.0004      # 8 mm；tolerance = size 的 5%
        print("=== CreateMesh(%d, %.5f, %.4f) + RunAnalysis（守护覆盖两阶段）==="
              % (MESH_SOLID, tol, size), flush=True)
        res = {"mesh": None, "run": None, "exc": None}
        t0 = time.time()

        def _work():
            try:
                res["mesh"] = get_com_member(study, "CreateMesh",
                                             MESH_SOLID, float(tol), float(size))
                res["run"] = get_com_member(study, "RunAnalysis")
            except Exception as exc:
                res["exc"] = str(exc)[:90]

        th = threading.Thread(target=_work, daemon=True)
        th.start()
        while th.is_alive():
            time.sleep(5)
            el = time.time() - t0
            if not guard("mesh+run %.0fs" % el):
                print("    ⇒ 守护触发，已中止", flush=True)
                return 3
            if el > TOTAL_TIMEOUT_S:
                print("    ⇒ 超过 %ds，主动中止" % TOTAL_TIMEOUT_S, flush=True)
                _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
                return 4
        print("    CreateMesh = %r" % (res["mesh"],), flush=True)
        print("    RunAnalysis = %r   用时 %.0f 秒" % (res["run"], time.time() - t0), flush=True)
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
