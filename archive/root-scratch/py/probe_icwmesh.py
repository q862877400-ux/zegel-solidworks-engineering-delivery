r"""@brief A9 第七次尝试 —— **在正确的对象上操作**：`study.Mesh`（`ICWMesh`）。

## 前六次为什么失败（逐步查出来的）
| # | 我做的 | 结果 | 学到什么 |
|---|---|---|---|
| 1-4 | 换 `CreateMesh` 的参数组合（5/15/4mm、零参） | 四次同一现象：网格器涨 20–25 GB | **换参数不是办法** |
| 5 | 停下**读文档**（解包 `cworks.chm` 2052 页） | 得知默认 mesher 是 BCB、`Global Size` 只对 Standard 有效、**`Automatic transition` 会导致单元爆炸** | 该关 `AutomaticTransition` |
| 5b | 在 **study** 上 `set MesherType` | 内存一度只涨到 1854 MB（看似有效）但随后仍涨到 16 GB | 我的守护只盖了 `RunAnalysis`，探针卡在 `CreateMesh` |
| 6 | 在 **study** 上设 `AutomaticTransition`/`MesherType` | ✗ **属性不存在**（`<unknown>.…`） | **这些属性不在 `ICWStudy` 上** |
| 7 | 查反射**宿主接口** | ⇒ **全在 `ICWMesh` 上**，入口是 `ICWStudy.get_Mesh()` | **本脚本** |

**`ICWMesh` 的关键成员**（真源 `D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt`）：
    set_MesherType(Int32) / set_AutomaticTransition(Int32) / set_ElementSize(Double) /
    set_Tolerance(Double) / set_Quality(Int32) / set_AutomaticLooping(Int32) /
    **GetDefaultElementSizeAndTolerance(Int32, Double&, Double&)**  ← ★ 用官方建议值
    **GetDefaultMaxAndMinElementSize(Int32, Double&, Double&)**
    get_ElementCount() / get_NodeCount()  ← ★ 回读网格规模，**可判「爆没爆」而不用等内存**

## 本脚本的做法
1. `study.Mesh` 取到 `ICWMesh`
2. **读** 当前 `MesherType` / `AutomaticTransition` / `ElementSize` / `Tolerance`
3. **调 `GetDefaultElementSizeAndTolerance`** 拿官方建议值（**不自编尺寸**）
4. **关掉 `AutomaticTransition`**，`MesherType` 设 Standard
5. `set_ElementSize` / `set_Tolerance` 用官方建议值
6. `CreateMesh` → **立刻回读 `ElementCount`**（若 > 50 万即判爆炸）
7. `RunAnalysis`（带守护）

# ── 来源 ──
# 仓库:   本项目自身（真机判定）+ SolidWorks 官方 Simulation 用户手册（CHM）+ 反射
# 文件:   D:\AI\SW\probe_icwmesh.py
# 定位:   specs/001-topology-result-readout 的 T-002（求解步）；铁律 2 的本机实测。
# 官方签名依据: ICWStudy.get_Mesh() → ICWMesh 的上述成员
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机且会跑网格。守护覆盖 **mesh 与 run 两阶段**（第五次的教训）。
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

MESH_TYPE_SOLID = 0        # swsMeshTypeSolid
MESHER_STANDARD = 0        # swsMesherTypeStandard
LENGTH_UNIT_METER = 0      # swsUnit_e 里米制的基本单位（GetDefault* 的第 1 参）
ELEMENT_EXPLOSION = 500_000
MEM_LIMIT_MB = 6000
SYS_FREE_MIN_GB = 8.0
TOTAL_TIMEOUT_S = 480


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ""


def guard(label: str) -> bool:
    v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
            "Measure-Object WorkingSet64 -Sum).Sum")
    mb = int(int(v) / 1_048_576) if v.isdigit() else 0
    v2 = _ps("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory")
    gb = int(v2) / 1_048_576 if v2.isdigit() else 99.0
    bad = mb > MEM_LIMIT_MB or gb < SYS_FREE_MIN_GB
    print("    [守护 %-16s] 网格器=%5d MB 系统=%.1f GB%s"
          % (label, mb, gb, "  ⚠ 触发" if bad else ""), flush=True)
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
        print("[1] 零件 %r（100×60×20 mm 单实体）" % title, flush=True)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "MESH_%d" % int(time.time())
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

        # ── ★ 关键：拿 ICWMesh ──
        print()
        print("=== study.Mesh（ICWMesh）—— 网格设置的真宿主 ===", flush=True)
        mesh = get_com_member(study, "Mesh")
        print("    study.Mesh = %r" % (mesh is not None), flush=True)
        if mesh is None:
            print("    ⇒ 拿不到 ICWMesh，本路不通", flush=True)
            return 3

        for prop in ("MesherType", "AutomaticTransition", "AutomaticTransition2",
                     "ElementSize", "Tolerance", "Quality", "ElementCount", "NodeCount",
                     "AutomaticLooping"):
            try:
                print("    %-22s = %r" % (prop, get_com_member(mesh, prop)), flush=True)
            except Exception as exc:
                print("    %-22s ✗ %s" % (prop, str(exc)[:44]), flush=True)

        # ── ★ 用**官方建议值**，不自编 ──
        print()
        print("=== 官方建议的单元尺寸与容差（GetDefaultElementSizeAndTolerance）===",
              flush=True)
        sugg = None
        try:
            from win32com.client import VARIANT
            import pythoncom
            v_size = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
            v_tol = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_R8, 0.0)
            get_com_member(mesh, "GetDefaultElementSizeAndTolerance",
                           LENGTH_UNIT_METER, v_size, v_tol)
            print("    建议 size=%r  tolerance=%r" % (v_size.value, v_tol.value), flush=True)
            sugg = (v_size.value, v_tol.value)
        except Exception as exc:
            print("    ✗ 取建议值失败: %s" % str(exc)[:80], flush=True)

        # ── ★ 关 AutomaticTransition + 设 Standard mesher ──
        print()
        print("=== 关 AutomaticTransition + 设 MesherType=Standard ===", flush=True)
        for prop, val in (("AutomaticTransition", 0), ("AutomaticTransition2", False),
                          ("MesherType", MESHER_STANDARD)):
            try:
                set_com_member(mesh, prop, val)
                print("    %-22s ← %r  回读=%r"
                      % (prop, val, get_com_member(mesh, prop)), flush=True)
            except Exception as exc:
                print("    %-22s ✗ %s" % (prop, str(exc)[:60]), flush=True)

        if sugg:
            for prop, val in (("ElementSize", sugg[0]), ("Tolerance", sugg[1])):
                try:
                    set_com_member(mesh, prop, float(val))
                    print("    %-22s ← %.6g  回读=%r"
                          % (prop, val, get_com_member(mesh, prop)), flush=True)
                except Exception as exc:
                    print("    %-22s ✗ %s" % (prop, str(exc)[:60]), flush=True)

        # ── 网格 + 求解：整体后台，主线程守护 ──
        print()
        print("=== CreateMesh + RunAnalysis（守护覆盖两阶段）===", flush=True)
        res = {"mesh": None, "run": None, "exc": None, "count": None}
        t0 = time.time()

        # ⚑⚑ 2026-10-01 真机发现（本轮的关键）：**`CreateMesh` 的尺寸/容差单位是
        #   文档单位（米制模型 = 毫米），不是米。**
        #   证据：官方 `GetDefaultElementSizeAndTolerance` 对一块 100×60×20 mm 的板
        #   给出 `size=4.9339 / tolerance=0.2467` —— 若按米读那是 4.93 米（比零件还大），
        #   按毫米读则 ≈ 板长的 5%，正是文档描述的「软件按体积与表面积建议默认值」。
        #   ⇒ 我前四次传的 `0.008`（自以为是 8 mm）被 API 当成 **0.008 mm = 8 微米**
        #     ⇒ 单元数爆炸 ⇒ 网格器涨到 20–25 GB。**四次失败的真因是单位假设错了。**
        size_val = float(sugg[0]) if sugg else 4.9339
        tol_val = float(sugg[1]) if sugg else 0.2467
        print("    用官方建议值（按**毫米**）：size=%.4f  tolerance=%.4f"
              % (size_val, tol_val), flush=True)

        def _work():
            try:
                res["mesh"] = get_com_member(study, "CreateMesh",
                                             MESH_TYPE_SOLID, tol_val, size_val)
                try:
                    res["count"] = get_com_member(mesh, "ElementCount")
                except Exception:
                    pass
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
                return 4
            if el > TOTAL_TIMEOUT_S:
                print("    ⇒ 超 %ds 主动中止" % TOTAL_TIMEOUT_S, flush=True)
                _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
                return 5
        print("    CreateMesh = %r   ElementCount = %r"
              % (res["mesh"], res["count"]), flush=True)
        print("    RunAnalysis = %r   用时 %.0f 秒"
              % (res["run"], time.time() - t0), flush=True)
        if res["exc"]:
            print("    异常: %s" % res["exc"], flush=True)
        if isinstance(res["count"], int) and res["count"] > ELEMENT_EXPLOSION:
            print("    ⚠ 单元数 %d > %d ⇒ 判定为爆炸" % (res["count"], ELEMENT_EXPLOSION),
                  flush=True)

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
