r"""@brief A9 决定性验证（**修正版**）：COM 在主线程，守护在旁路线程。

## 为什么要有这个修正版
上一版（`probe_decisive.py`）把 `CreateMesh`/`RunAnalysis` 放进**后台线程**，
得到 `AttributeError: <unknown>.CreateMesh`。而 `dynamic.py` 的这个异常来自
**`__getattr__`（属性查找）**，不是调用失败。

**⇒ 根因：COM 是 STA + 线程亲和（AGENTS.md 已知事实 4 的同类）。**
**跨线程访问 COM 对象 ⇒ 成员查找失败。**
证据：`probe_createmesh_forms.py` 里**主线程**调 `CreateMesh(0, 0.2467, 4.9339)`
**返回 0（成功）**；凡是放进后台线程的那几次全部报同一个 AttributeError。

**⇒ 正确设计**：**COM 调用留在主线程**，把「守护」放到**旁路线程**——
旁路只做一件事：读内存，超阈值就 `Stop-Process cwbcbfmesh`。
（杀掉网格器进程会让主线程的 COM 调用提前结束或抛错，这正是我们想要的中止方式。）

## 本轮要验的两件事
1. **参数顺序**：VB6 类型库 CHM 的官方签名是
   `CreateMesh(NUnits As Long, DElementSize As Double, DTolerance As Double)`
   —— 前七次我按 `(meshType, tolerance, size)` 传，**size 与 tolerance 颠倒**。
2. **`NUnits` 的合法值**：`swsUnit_e` = SI 0 / English 1 / Metric 2。
   实测 `2` 与 `-1` 都失败过（但**那些失败都在后台线程里，结论作废**）；
   已知**主线程**传 `0` 成功。
   而 `GetDefaultElementSizeAndTolerance(2, …)` 返回**米级**数值（0.0049339），
   `(-1, …)` 返回**毫米级**（4.9339）⇒ 单位参数**确实影响返回值的量纲**。

## 设计
主线程依次试三组（**都按正确顺序**），每组之间**新建文档 + 新建研究**（避免残留）：
    A. (0, 0.0049339, 0.0002467)   SI + 米级数值     ⇒ 期望约 1000 个单元
    B. (0, 4.9339, 0.2467)         SI + 毫米级数值   ⇒ 若单位真是米，这组会给出极少单元
    C. (0, 0.2467, 4.9339)         复现第一次成功的组合（作对照）
**旁路线程**持续读 `cwbcbfmesh` 内存；> 6 GB 或系统 < 8 GB 就杀网格器并置停止标志。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks Simulation **VB6 类型库 CHM**（方法签名页）
# 文件:   D:\AI\SW\probe_createmesh_final.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步）；
#         铁律 4「签名三源互证」—— 本案里 VB6 CHM 是唯一给出**参数名**的源。
# 官方签名依据: cworksapivb6.chm 的 CosmosWorksLib~CWStudy~CreateMesh 页
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格。**内存守护写在旁路线程**（COM 必须在主线程）。
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

MEM_LIMIT_MB = 6000
SYS_FREE_MIN_GB = 8.0
STOP = threading.Event()
MESH_ERR = {0: "Succeeded", 3: "ElementSizeTooSmall", 4: "ElementSizeTooBig",
            5: "SpecifyPositiveValue"}
RUN_ERR = {0: "Successful", 19: "MaterialNotDefined", 23: "MeshNotFound", 24: "AnalysisFailed"}

CASES = [
    ("A  SI + 米级数值", 0, 0.0049339, 0.0002467),
    ("B  SI + 毫米级数值", 0, 4.9339, 0.2467),
    ("C  复现首次成功的组合", 0, 0.2467, 4.9339),
]


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def watchdog() -> None:
    """旁路线程：**只读内存**，超阈值就杀网格器。不碰 COM。"""
    while not STOP.wait(5):
        v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
                "Measure-Object WorkingSet64 -Sum).Sum")
        mb = int(int(v) / 1_048_576) if v.isdigit() else 0
        v2 = _ps("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory")
        gb = int(v2) / 1_048_576 if v2.isdigit() else 99.0
        if mb > 0:
            print("      [旁路守护] 网格器=%d MB 系统=%.1f GB" % (mb, gb), flush=True)
        if mb > MEM_LIMIT_MB or gb < SYS_FREE_MIN_GB:
            print("      [旁路守护] ⚠ 超阈值 ⇒ 杀网格器", flush=True)
            _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
            return


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    threading.Thread(target=watchdog, daemon=True).start()
    for label, units, size, tol in CASES:
        title = None
        print()
        print("════ %s ════" % label, flush=True)
        print("    CreateMesh(NUnits=%d, DElementSize=%.7g, DTolerance=%.7g)"
              % (units, size, tol), flush=True)
        try:
            model = new_document(sw, doc_type="part")          # ← 主线程
            title = get_com_member(model, "GetTitle")
            sk = sw_part.sketch(model, "Front Plane")
            sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
            sw_part.extrude_boss(model, sk, 0.02)
            doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                                "CosmosWorks"), "ActiveDoc")
            mgr = get_com_member(doc, "StudyManager")
            nm = "F_%d" % int(time.time() * 1000 % 1_000_000)
            get_com_member(mgr, "DeleteStudy", nm)
            study = get_com_member(mgr, "CreateNewStudy3", nm, 0, 0, out_i4())
            if study is None:
                print("    研究建不出来 ⇒ 跳过", flush=True)
                continue
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

            t0 = time.time()
            try:
                code = get_com_member(study, "CreateMesh", units, size, tol)  # ← 主线程！
                print("    CreateMesh = %r (%s)   用时 %.0f 秒"
                      % (code, MESH_ERR.get(code, "?"), time.time() - t0), flush=True)
            except Exception as exc:
                print("    CreateMesh ✗ %s   用时 %.0f 秒"
                      % (str(exc)[:70], time.time() - t0), flush=True)
                continue
            mesh = get_com_member(study, "Mesh")
            print("    ★ ElementCount = %r" % get_com_member(mesh, "ElementCount"), flush=True)
            print("    ★ NodeCount    = %r" % get_com_member(mesh, "NodeCount"), flush=True)
            if code == 0:
                t1 = time.time()
                try:
                    rc = get_com_member(study, "RunAnalysis")
                    print("    RunAnalysis = %r (%s)   用时 %.0f 秒"
                          % (rc, RUN_ERR.get(rc, "?"), time.time() - t1), flush=True)
                except Exception as exc:
                    print("    RunAnalysis ✗ %s" % str(exc)[:60], flush=True)
                res = get_com_member(study, "Results")
                print("    ★ study.Results 非空 = %r" % (res is not None), flush=True)
                if res is not None:
                    for p in ("GetPlotCount", "GetPlotNames"):
                        try:
                            print("      %s = %r" % (p, str(get_com_member(res, p))[:100]),
                                  flush=True)
                        except Exception as exc:
                            print("      %s ✗ %s" % (p, str(exc)[:46]), flush=True)
        finally:
            try:
                if title:
                    sw.CloseDoc(title)
            except Exception:
                pass
    STOP.set()
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    print()
    print("收尾完成（文档未保存）", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
