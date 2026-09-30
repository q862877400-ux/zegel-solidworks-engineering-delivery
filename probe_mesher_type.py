r"""@brief A9 第五次尝试 —— **先读文档再动手**：显式设 mesher 类型，并带内存守护。

## 为什么这次不一样
前四次都是「换参数组合」的蛮干（5mm / 15mm / 4mm / 零参），**四次同一现象**
（`cwbcbfmesh` 涨到 20–25 GB、烧 1000–3000 秒不收敛）。
按纪律「两次失败就停下查文档」，本轮去读了一直没读的 **Simulation 用户手册**
（`lang\english\cworks.chm` 解包 2052 页到 `C:\cworks_manual`）。

**文档给出的关键事实**（`C:\cworks_manual\IDC_HELP_MESHSOLID.htm`）：
- **默认 mesher 是 Blended curvature-based（BCB）**，而 **`Global Size` / `Tolerance`
  两个参数「Available for standard mesh only」**
- BCB 用的是 **Min/Max element size**（按曲率），**不是** global size
- **`Automatic transition`**（仅 standard mesh）勾选时会自动给小特征加密
- `Tolerance` 的默认是「global element size 的 5%」

**⇒ 假设**：本研究用的是 BCB mesher，而我传的 `tolerance=0.0005`（5 mm 单元的 10%）
可能被 BCB 当成**最小单元尺寸** ⇒ 单元数爆炸。
**⇒ 对策**：显式设 `MesherType = swsMesherTypeStandard(0)`，让 size/tolerance 按其本义生效。

**枚举真源**：`D:\AI\SW\_raw\topo-reflect\enum_cosworks.txt`
    swsMesherType_e: Standard=0 / Alternate=1 / AlternateCB=2

## 内存守护（前四次的教训）
本脚本每 5 秒检查 `cwbcbfmesh` 的内存与系统可用内存；**超过阈值就立刻停掉求解器并退出**，
不重蹈「涨到 25 GB」的覆辙。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks 官方 Simulation 用户手册（CHM）
# 文件:   D:\AI\SW\probe_mesher_type.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步）；
#         AGENTS.md 铁律 2「本机实测」+「查文档优先于蛮干」。
# 官方签名依据: ICWStudy.get_/set_MesherType(Int32) / CreateMesh(Int32, Double, Double)；
#         swsMesherType_e / swsMeshType_e / swsStudyMeshError_e
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格。**带内存守护**，超阈值立即中止。
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

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    out_i4,
    set_com_member,
)
from scripts import sw_part, sw_simulation as sim, sw_topology as topo  # noqa: E402

MESHER_STANDARD = 0     # swsMesherTypeStandard
MESH_SOLID = 0          # swsMeshTypeSolid
MEM_LIMIT_MB = 8000     # 求解器内存上限（MB）—— 超过就中止
SYS_FREE_MIN_GB = 8.0   # 系统可用内存下限（GB）


def solver_mem_mb() -> int:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
             "Measure-Object WorkingSet64 -Sum).Sum"],
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
        return int(int(out) / 1_048_576) if out.isdigit() else 0
    except Exception:
        return 0


def sys_free_gb() -> float:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
        return int(out) / 1_048_576 if out.isdigit() else 99.0
    except Exception:
        return 99.0


def guard(label: str) -> bool:
    """返回 True 表示安全可继续。"""
    mb, gb = solver_mem_mb(), sys_free_gb()
    tag = ""
    if mb > MEM_LIMIT_MB:
        tag = "  ⚠ 求解器内存超上限"
    elif gb < SYS_FREE_MIN_GB:
        tag = "  ⚠ 系统可用内存过低"
    print("    [守护] %s 求解器=%d MB 系统可用=%.1f GB%s" % (label, mb, gb, tag))
    if tag:
        print("    ⇒ 触发守护，停掉求解器")
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue"],
                       capture_output=True, timeout=20)
        return False
    return True


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    t0 = time.time()
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 零件 %r" % title)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "MESHER_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        study = get_com_member(mgr, "CreateNewStudy3", name, 0, 0, out_i4())  # 0 = static
        print("[2] 静力学研究 %r" % (study is not None))
        if study is None:
            return 2

        # 材料（RunAnalysis 19 的修法）
        sw_part._select_by_id(model.Extension, "", "SOLIDBODY", append=False, mark=0)
        mc = get_com_member(get_com_member(study, "SolidManager"),
                            "SetFavLibraryMaterialToSelectedEntities",
                            "solidworks materials", "Plain Carbon Steel")
        get_com_member(model, "ClearSelection2", True)
        print("[3] 赋材料返回码 = %r" % (mc,))

        # 夹具 + 载荷
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)

        # ── ★ 本轮的关键：先读 mesher 类型，再显式设成 Standard ──
        print()
        print("=== 读 mesher 类型（默认应是 BCB=2）===")
        for prop in ("MesherType", "MeshType", "MeshQuality"):
            try:
                print("    %-14s = %r" % (prop, get_com_member(study, prop)))
            except Exception as exc:
                print("    %-14s ✗ %s" % (prop, str(exc)[:48]))

        print()
        print("=== 设 MesherType = %d (Standard) ===" % MESHER_STANDARD)
        try:
            set_com_member(study, "MesherType", MESHER_STANDARD)
            print("    设后回读 = %r" % (get_com_member(study, "MesherType"),))
        except Exception as exc:
            print("    ✗ 设 MesherType 失败: %s" % str(exc)[:70])

        # ── 网格：Standard mesher 下 size/tolerance 按其本义 ──
        print()
        print("=== CreateMesh(meshType=0, tolerance, size) —— Standard mesher 下 ===")
        size = 0.008          # 8 mm（板 100×60×20）
        tol = size * 0.05     # 文档：tolerance 默认 = global size 的 5%
        print("    size=%.4f m (%.0f mm)  tolerance=%.5f (5%%)" % (size, size * 1000, tol))
        code = get_com_member(study, "CreateMesh", MESH_SOLID, float(tol), float(size))
        err = {0: "Succeeded", 3: "ElementSizeTooSmall", 4: "ElementSizeTooBig",
               5: "SpecifyPositiveValue"}.get(code, "?")
        print("    CreateMesh 返回 = %r  (%s)" % (code, err))
        if not guard("网格后"):
            return 3

        # ── 求解（带守护轮询）──
        print()
        print("=== RunAnalysis（每 5 秒守护一次，超 %d MB 或系统低于 %.0f GB 即中止）==="
              % (MEM_LIMIT_MB, SYS_FREE_MIN_GB))
        t1 = time.time()
        done = {"v": None}

        import threading
        def _run():
            try:
                done["v"] = get_com_member(study, "RunAnalysis")
            except Exception as exc:
                done["v"] = "EXC:%s" % str(exc)[:60]

        th = threading.Thread(target=_run, daemon=True)
        th.start()
        while th.is_alive():
            time.sleep(5)
            if not guard("求解中 %.0fs" % (time.time() - t1)):
                print("    ⇒ 已中止（守护触发）")
                return 4
            if time.time() - t1 > 600:
                print("    ⇒ 超过 10 分钟，主动中止")
                subprocess.run(["powershell", "-NoProfile", "-Command",
                                "Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue"],
                               capture_output=True, timeout=20)
                return 5
        code = done["v"]
        runerr = {0: "Successful", 19: "MaterialNotDefined", 23: "MeshNotFound",
                  24: "AnalysisFailed"}.get(code, "?")
        print("    RunAnalysis = %r  (%s)  用时 %.0f 秒" % (code, runerr, time.time() - t1))

        results = get_com_member(study, "Results")
        print()
        print("=== 结果 ===")
        print("    study.Results 非空 = %r" % (results is not None))
        if results is not None:
            for p in ("GetPlotCount", "GetPlotNames"):
                try:
                    print("    %s = %r" % (p, str(get_com_member(results, p))[:110]))
                except Exception as exc:
                    print("    %s ✗ %s" % (p, str(exc)[:50]))
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
