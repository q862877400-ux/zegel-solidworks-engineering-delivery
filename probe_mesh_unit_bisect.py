r"""@brief A9 单位二分实验：`CreateMesh(meshType, tolerance, size)` 的 size 到底是什么量纲？

## 已知
- `CreateMesh(0, 0.2467, 4.9339)`（取自官方 `GetDefaultElementSizeAndTolerance`）
  **返回 0（成功）**，但网格是 **19,539,399 个单元 / 26,717,520 个节点**
- 零件为 100×60×20 mm（`sw_part.sketch_corner_rectangle(m, -0.05, -0.03, 0.05, 0.03)`
  + `extrude_boss(m, sk, 0.02)`，SolidWorks API 的长度单位是**米**）
- 若 size 是毫米：4.93 mm ⇒ 约 1000 个单元（与实得差约 19,500 倍）
- 若 size 是米：4.93 m ⇒ 比零件还大 ⇒ 约 1 个单元（方向相反）

**两个方向都解释不了 19.5M。**

## 本实验
**二分数量级**：分别用 size = 4.9339 / 0.0049339 / 493.39 各建一次网格，
**每次新建文档与新建研究**（避免上一次的网格残留），立即回读 `ElementCount`。

**⇒ 看单元数随 size 怎么变，反推真实量纲。** 这比继续猜方向可靠。

## 守护
每次网格前中后都查 `cwbcbfmesh` 内存；> 6 GB 或系统 < 8 GB 立即中止整个脚本。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_mesh_unit_bisect.py
# 定位:   specs/001-topology-result-readout 的 T-002；铁律 2「本机实测」。
#         结论回写 `scripts/sw_simulation.py` 的网格参数注释与 ROADMAP 的调整记录。
# 官方签名依据: ICWStudy.CreateMesh(Int32, Double, Double)；
#         ICWMesh.GetDefaultElementSizeAndTolerance(Int32, Double&, Double&) /
#         get_ElementCount() / get_NodeCount()；swsStudyMeshError_e
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格（每次可能数分钟）。带内存守护。
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
from scripts import sw_part  # noqa: E402

MEM_LIMIT_MB = 6000
SYS_FREE_MIN_GB = 8.0
#: 三个数量级（基准是官方建议值 4.9339）
SIZE_CANDIDATES = (4.9339, 0.0049339, 493.39)


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
    print("      [守护 %s] 网格器=%d MB 系统=%.1f GB%s"
          % (tag, mb, gb, "  ⚠" if bad else ""), flush=True)
    if bad:
        _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
    return not bad


MESH_ERR = {0: "Succeeded", 3: "ElementSizeTooSmall", 4: "ElementSizeTooBig",
            5: "SpecifyPositiveValue"}


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    results = []
    for size in SIZE_CANDIDATES:
        title = None
        try:
            model = new_document(sw, doc_type="part")
            title = get_com_member(model, "GetTitle")
            sk = sw_part.sketch(model, "Front Plane")
            sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
            sw_part.extrude_boss(model, sk, 0.02)

            doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                                "CosmosWorks"), "ActiveDoc")
            mgr = get_com_member(doc, "StudyManager")
            nm = "BIS_%d_%s" % (int(time.time()), str(size).replace(".", ""))
            get_com_member(mgr, "DeleteStudy", nm)
            study = get_com_member(mgr, "CreateNewStudy3", nm, 0, 0, out_i4())
            mesh = get_com_member(study, "Mesh")
            # 取官方建议值（同时用作基准对照）
            vs = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
            vt = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
            try:
                get_com_member(mesh, "GetDefaultElementSizeAndTolerance", 0, vs, vt)
                sugg = vs.value
            except Exception:
                sugg = None

            print("── 试 size=%.7g （官方建议=%.7g）──" % (size, sugg or 0), flush=True)
            t0 = time.time()
            code = get_com_member(study, "CreateMesh", 0, size * 0.05, size)
            dt = time.time() - t0
            cnt = get_com_member(mesh, "ElementCount")
            nds = get_com_member(mesh, "NodeCount")
            print("     CreateMesh → %r (%s)  用时 %.0f 秒"
                  % (code, MESH_ERR.get(code, "?"), dt), flush=True)
            print("     ★ ElementCount = %r   NodeCount = %r" % (cnt, nds), flush=True)
            results.append((size, code, cnt, nds, dt))
            if not guard("size=%.4g" % size):
                print("     ⇒ 守护触发，中止整个实验", flush=True)
                break
        finally:
            try:
                if title:
                    sw.CloseDoc(title)
            except Exception:
                pass
    print()
    print("════ 汇总 ════", flush=True)
    print("  %-14s %-6s %-14s %-14s %s" % ("size", "code", "ElementCount", "NodeCount", "用时s"),
          flush=True)
    for size, code, cnt, nds, dt in results:
        print("  %-14.7g %-6r %-14r %-14r %.0f" % (size, code, cnt, nds, dt), flush=True)
    print()
    print("  ⇒ 判读：若 ElementCount 随 size 变小而**剧增**，则 size 是长度量纲且", flush=True)
    print("     真实单位 = 使「ElementCount ≈ 零件体积 / size³」成立的那个。", flush=True)
    print("     零件体积 = 0.1×0.06×0.02 m³ = 1.2e-4 m³ = 1.2e5 mm³", flush=True)
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
