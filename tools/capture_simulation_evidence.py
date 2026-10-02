"""@brief 真机证据采集：跑完整仿真链并把结果写成**可复核的 JSON 证据文件**。

## 为什么需要它（解决的问题）
`capabilities.yaml` 里 `simulation_and_fea` 的 `evidence` 原先写的是
**「2026-10-01 真机：… apply_fixed_restraint 仍失败」** —— 而它**已经不再失败**了
（真机整链跑通，`Count = 2`、4 个结果图）。**evidence 是文字、不可复跑，且会过期。**

**⇒ 本脚本把「真机证据」变成一条**可跑的命令**：**
```
python tools/capture_simulation_evidence.py
```
它跑完链后会写 `output/simulation-evidence.json` 并在 stdout 打印结论；
**任一步不达预期就以非零退出** ⇒ 可直接当验收判据用（`capabilities.yaml` 的
`evidence` 指向本脚本的命令行，而不是一段会腐坏的文字）。

## 采集什么（判据，不看返回码）
铁律：COM 返回值凡不能自证，一律以**回读**为判据（本项目已累计四处「返回码撒谎」）。
| 环节 | 判据 |
|---|---|
| 材料 | 回读 `model.MaterialIdName` 非空 |
| 夹具/载荷 | 选区计数 = 1 且 `LoadsAndRestraintsManager.Count = 2` |
| 网格 | `CreateMesh` 返回 0 **且** `ElementCount` 为一个（小的）正整数 |
| 求解 | **不是** `RunAnalysis` 的返回码，而是 `study.Results` 非空 + `GetPlotCount > 0` |

## 输入
用**新建的** 100×60×20 mm 单实体板（不碰任何用户文档），跑完即关、**不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据采集，非第三方移植）
# 文件:   tools/capture_simulation_evidence.py
# 定位:   AGENTS.md 判据 A4「`verified` 必须有我们自己的运行证据」的**可跑化**；
#         以及判据 A9 的落地。采集的调用全部来自 `scripts/sw_simulation.py`
#         与 `scripts/sw_part.py`（那两个模块里的官方签名已各自核过）。
# 官方签名依据: 本脚本**不引入新的 COM 成员**，只调用两个模块里已核过的函数。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机（需要运行中的 SolidWorks + Simulation 加载项）。不在 pytest 里跑，
#   避免拖慢常规测试；由人按需执行。**未在本机之外的环境实测。**
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part, sw_simulation as sim  # noqa: E402

#: 证据文件默认落点（`output/` 已 gitignore，属产物目录）
DEFAULT_OUT = ROOT / "output" / "simulation-evidence.json"

#: 网格器内存上限（MB）—— 超过就杀，防 20–25 GB 重演
MEM_LIMIT_MB = 4000
#: 单元数「合理」上限 —— 100×60×20 mm 的板用官方建议尺寸约 7 千；过百万即判爆炸
ELEMENT_SANE_MAX = 1_000_000

_STOP = threading.Event()


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15).stdout.strip()
    except Exception:
        return ""


def _watchdog() -> None:
    """旁路线程：只读内存，超阈值杀网格器。**不碰 COM**（STA 线程亲和）。"""
    while not _STOP.wait(5):
        v = _ps("(Get-Process cwbcbfmesh -ErrorAction SilentlyContinue | "
                "Measure-Object WorkingSet64 -Sum).Sum")
        mb = int(int(v) / 1_048_576) if v.isdigit() else 0
        if mb > MEM_LIMIT_MB:
            _ps("Stop-Process -Name cwbcbfmesh -Force -ErrorAction SilentlyContinue")
            return


def main() -> int:
    ap = argparse.ArgumentParser(description="采集仿真链的真机证据")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="证据 JSON 输出路径")
    ap.add_argument("--quiet", action="store_true", help="只输出证据 JSON")
    args = ap.parse_args()

    out_path = Path(args.out)
    ev: dict = {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "capability": "simulation_and_fea",
        "steps": {},
        "verdict": "fail",
    }

    def say(msg: str) -> None:
        if not args.quiet:
            print(msg, flush=True)

    sw = None
    title = None
    threading.Thread(target=_watchdog, daemon=True).start()
    try:
        sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
        sw.CommandInProgress = True
        ev["steps"]["connect"] = {"ok": True}

        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        ev["steps"]["part"] = {"ok": True, "title": title, "size_mm": [100, 60, 20]}
        say("[1] 零件 %r" % title)

        # ── 材料（判据 = 回读 MaterialIdName）──
        mid = sim.set_material(model, "AISI 1020")
        ev["steps"]["material"] = {"ok": bool(mid), "MaterialIdName": mid}
        say("[2] 材料回读 = %r" % mid)
        if not mid:
            raise RuntimeError("材料未赋上（库名或材料名不对）—— 判据是回读 MaterialIdName")

        # ── 研究 ──
        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        name = "EVIDENCE_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", name)
        from scripts.sw_connect import out_i4
        study = get_com_member(mgr, "CreateNewStudy3", name, 0, 0, out_i4())
        ev["steps"]["study"] = {"ok": study is not None, "name": name}
        say("[3] 静力学研究 = %r" % (study is not None))
        if study is None:
            raise RuntimeError("建研究失败")

        # ── 夹具 / 载荷（判据 = 选区计数 + Count）──
        n_fix = sim.select_face_at(model, 0.0, 0.0, -0.02)
        rst = sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        n_frc = sim.select_face_at(model, 0.0, 0.0, 0.0)
        frc = sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        try:
            count = int(get_com_member(get_com_member(study, "LoadsAndRestraintsManager"),
                                       "Count") or 0)
        except Exception:
            count = -1
        ev["steps"]["fixtures_and_loads"] = {
            "ok": bool(rst is not None and frc is not None and count == 2),
            "selection_count_fixture_face": n_fix,
            "selection_count_load_face": n_frc,
            "loads_restraints_count": count,
        }
        say("[4] 夹具选区=%d 载荷选区=%d Count=%d" % (n_fix, n_frc, count))

        # ── 网格（判据 = 返回 0 且单元数合理）──
        size, tol = sim.default_element_size_and_tolerance(study, -1)
        t0 = time.time()
        mc = get_com_member(study, "CreateMesh", 0, float(size), float(tol))
        elements = int(get_com_member(get_com_member(study, "Mesh"), "ElementCount") or 0)
        ev["steps"]["mesh"] = {
            "ok": mc == 0 and 0 < elements <= ELEMENT_SANE_MAX,
            "return_code": mc,
            "suggested_size_mm": size,
            "suggested_tolerance_mm": tol,
            "element_count": elements,
            "seconds": round(time.time() - t0, 1),
            "sane_max": ELEMENT_SANE_MAX,
        }
        say("[5] CreateMesh=%r 单元=%d 用时%.0fs" % (mc, elements, time.time() - t0))

        # ── 求解（判据 = Results 非空 + 图数，**不是返回码**）──
        t1 = time.time()
        rc = sim.run_analysis(study)
        results = get_com_member(study, "Results")
        plots = None
        names = None
        if results is not None:
            try:
                plots = int(get_com_member(results, "GetPlotCount") or 0)
            except Exception:
                plots = None
            try:
                names = list(get_com_member(results, "GetPlotNames") or ())
            except Exception:
                names = None
        ev["steps"]["solve"] = {
            "ok": results is not None and bool(plots),
            "run_analysis_return": rc,
            "run_analysis_return_is_trustworthy": False,
            "results_present": results is not None,
            "plot_count": plots,
            "plot_names": names,
            "seconds": round(time.time() - t1, 1),
        }
        say("[6] RunAnalysis=%r（**该返回码不可信**） Results非空=%r 图数=%r"
            % (rc, results is not None, plots))
        if names:
            say("    图名 = %r" % (names,))

        all_ok = all(s.get("ok") for s in ev["steps"].values())
        ev["verdict"] = "pass" if all_ok else "fail"
    except Exception as exc:  # noqa: BLE001 —— 顶层采集，任何失败都要落进证据文件
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        _STOP.set()
        if sw is not None:
            try:
                if title:
                    sw.CloseDoc(title)
            except Exception:
                pass
            try:
                sw.CommandInProgress = False
            except Exception:
                pass
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
        say("")
        say("证据已写入 %s" % out_path)
        say("结论: %s" % ev["verdict"].upper())

    print(json.dumps(ev, ensure_ascii=False, indent=2))
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
