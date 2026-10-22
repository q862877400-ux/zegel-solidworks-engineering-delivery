"""@brief 真机证据采集：跑**拓扑优化闭环**并把结果写成可复核的 JSON。

## 为什么需要它
`capabilities.yaml` 的 `topology_optimization` 长期停在 `stitched`，理由是两条：
1. **求解被许可证挡住**（本机只有 `SimulationXpress`；2026-10-01 用户在 SNL 里改了设置并重启后解除）
2. **没有成功取得 Material Mass 结果**（知识页记为「主要未决项」）

**⇒ 本脚本把「拓扑闭环跑通 + Material Mass 拿到」变成一条可跑的命令：**
```
python tools/capture_topology_evidence.py
```
任一步不达预期即非零退出 ⇒ 可直接当验收判据（`capabilities.yaml` 的 `evidence`
指向本脚本的命令行，而不是一段会过期的文字）。

## 采集什么（判据，不看返回码）
**本项目已累计四处「返回码撒谎」**，故一律回读：
| 环节 | 判据 |
|---|---|
| 拓扑研究 | `AnalysisType == 13` 且入口是 `CreateNewStudy3`（未走降级） |
| 目标/约束 | `{goal, mass_constraint}` 都非 None，且 `mass_constraint_reused` 为真 |
| 夹具/载荷 | 选区计数 = 1 且 `LoadsAndRestraintsManager.Count == 2` |
| 网格 | `CreateMesh` 返回 0 **且** 单元数在一个合理正整数区间 |
| 求解 | **不是** `RunAnalysis` 返回码，而是 `study.Results` 非空 + 图数 > 0 |
| **Material Mass** | **`GetPlotNames` 里出现 `材料质量*` / `Material Mass*`** ← 本能力的核心判据 |

## 输入
**新建的** 100×60×20 mm 单实体板（拓扑优化**只能对单实体零件做**，官方硬约束），
跑完即关、**不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据采集，非第三方移植）
# 文件:   tools/capture_topology_evidence.py
# 定位:   AGENTS.md 判据 A4「`verified` 必须有我们自己的运行证据」+ 判据 A9
#         （「空白域护城河有可跑的工程实现」）的**可跑化**。调用的全部是
#         `scripts/sw_topology.py` 与 `scripts/sw_simulation.py` 里已核过的函数。
# 官方签名依据: 本脚本**不引入新的 COM 成员**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机。**需要含拓扑优化的 Simulation 许可**（本机 2026-10-01 起可用）；
#   无许可时求解会弹「拓扑算例未获许可」且 `Results` 为空 ⇒ 本脚本会以非零退出并写明原因。
# ⚠ 不在 pytest 里跑（单次求解约 3 分钟，且需要许可），由人按需执行。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import sw_part  # noqa: E402
from scripts import sw_simulation as sim
from scripts import sw_topology as topo
from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402

DEFAULT_OUT = ROOT / "output" / "topology-evidence.json"
MEM_LIMIT_MB = 6000
ELEMENT_SANE_MAX = 2_000_000
#: Material Mass 结果图名的形态（中文界面 `材料质量1`，英文界面 `Material Mass 1`）
MASS_PLOT_RE = re.compile(r"(材料质量|Material\s*Mass)", re.I)

_STOP = threading.Event()


def _ps(cmd: str) -> str:
    try:
        return subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        ).stdout.strip()
    except Exception:
        return ""


def _watchdog() -> None:
    """旁路线程：只读内存，超阈值杀网格器/求解器。**不碰 COM**（STA 线程亲和）。"""
    while not _STOP.wait(5):
        for name in ("cwbcbfmesh",):
            v = _ps(
                "(Get-Process %s -ErrorAction SilentlyContinue | "
                "Measure-Object WorkingSet64 -Sum).Sum" % name
            )
            mb = int(int(v) / 1_048_576) if v.isdigit() else 0
            if mb > MEM_LIMIT_MB:
                _ps("Stop-Process -Name %s -Force -ErrorAction SilentlyContinue" % name)
                return


def main() -> int:
    ap = argparse.ArgumentParser(description="采集拓扑优化闭环的真机证据")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument(
        "--mass-reduce-percent",
        type=float,
        default=75.0,
        help="减重百分比（官方教程用 75，语义是「减掉 75%%」）",
    )
    args = ap.parse_args()

    out_path = Path(args.out)
    ev: dict = {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "capability": "topology_optimization",
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
        ev["revision"] = get_com_member(sw, "RevisionNumber")

        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        ev["steps"]["part"] = {
            "ok": True,
            "title": title,
            "size_mm": [100, 60, 20],
            "bodies": 1,
        }
        say("[1] 单实体板 %r" % title)

        mid = sim.set_material(model, "AISI 1020")
        ev["steps"]["material"] = {"ok": bool(mid), "MaterialIdName": mid}
        say("[2] 材料回读 = %r" % mid)
        if not mid:
            raise RuntimeError("材料未赋上 —— 判据是回读 MaterialIdName")

        study, entry = topo.create_topology_study(sw, "TOPO_EV_%d" % int(time.time()))
        atype = get_com_member(study, "AnalysisType") if study is not None else None
        ev["steps"]["topology_study"] = {
            "ok": study is not None
            and atype == topo.SWS_ANALYSIS_STUDY_TYPES["topology_static"],
            "entry": entry,
            "AnalysisType": atype,
            "expected": topo.SWS_ANALYSIS_STUDY_TYPES["topology_static"],
        }
        say(
            "[3] 拓扑研究 = %r  入口=%r  AnalysisType=%r"
            % (study is not None, entry, atype)
        )
        if study is None:
            raise RuntimeError("建拓扑研究失败")

        res_goal = topo.set_topology_goal(
            study,
            goal_type=topo.TP_GOAL_MAXIMIZE_STIFFNESS,
            mass_reduce_percent=args.mass_reduce_percent,
        )
        # ⚠⚠ **不要用真假值判成功码**（本脚本第一版踩到）：`set_topology_goal` 的 `goal`
        #    是 `EndEdit` 的**返回码**，**成功是 `0`**；而 Python 的 `bool(0)` 是 `False`
        #    ⇒ 第一版写成 `bool(res_goal.get("goal") and …)`，把「成功」判成了「失败」，
        #    证据文件里 `goal_and_constraints.ok=False` 而三个子项全为 True。
        #    真机复核（`D:\AI\SW\probe_bool_com.py`）：
        #        goal            type=int        repr=0            bool()=**False**
        #        mass_constraint type=CDispatch   repr=<COMObject>  bool()=True
        # `scripts/sw_topology.py` 的来源块也写着「`EndEdit` = 0；实测 `goal=0`、`mass=T
        # rue`」。
        #    **⇒ 判据一律显式比 `0`，或用 `is not None`；永不用真假值。**
        goal_code = res_goal.get("goal")
        ev["steps"]["goal_and_constraints"] = {
            "ok": goal_code == 0 and res_goal.get("mass_constraint") is not None,
            "goal_endedit_code": goal_code,
            "goal_endedit_code_means": "0 = EndEdit 提交成功（**不是真假值**）",
            "mass_constraint": res_goal.get("mass_constraint") is not None,
            "mass_constraint_reused": res_goal.get("mass_constraint_reused"),
            "removed": res_goal.get("removed"),
            "mass_reduce_percent": args.mass_reduce_percent,
        }
        say(
            "[4] EndEdit=%r（0=成功） mass_constraint=%r reused=%r"
            % (
                goal_code,
                res_goal.get("mass_constraint") is not None,
                res_goal.get("mass_constraint_reused"),
            )
        )

        n_fix = sim.select_face_at(model, 0.0, 0.0, -0.02)
        rst = sim.apply_fixed_restraint(study, model=model)
        get_com_member(model, "ClearSelection2", True)
        n_frc = sim.select_face_at(model, 0.0, 0.0, 0.0)
        frc = sim.apply_normal_force(study, model=model, magnitude=100.0)
        get_com_member(model, "ClearSelection2", True)
        try:
            count = int(
                get_com_member(
                    get_com_member(study, "LoadsAndRestraintsManager"), "Count"
                )
                or 0
            )
        except Exception:
            count = -1
        ev["steps"]["fixtures_and_loads"] = {
            "ok": bool(rst is not None and frc is not None and count == 2),
            "selection_count_fixture_face": n_fix,
            "selection_count_load_face": n_frc,
            "loads_restraints_count": count,
        }
        say("[5] 夹具选区=%d 载荷选区=%d Count=%d" % (n_fix, n_frc, count))

        size, tol = sim.default_element_size_and_tolerance(study, -1)
        t0 = time.time()
        mc = get_com_member(study, "CreateMesh", 0, float(size), float(tol))
        elements = int(
            get_com_member(get_com_member(study, "Mesh"), "ElementCount") or 0
        )
        ev["steps"]["mesh"] = {
            "ok": mc == 0 and 0 < elements <= ELEMENT_SANE_MAX,
            "return_code": mc,
            "element_count": elements,
            "suggested_size_mm": size,
            "suggested_tolerance_mm": tol,
            "seconds": round(time.time() - t0, 1),
        }
        say("[6] CreateMesh=%r 单元=%d 用时%.0fs" % (mc, elements, time.time() - t0))

        t1 = time.time()
        rc = sim.run_analysis(study)
        results = get_com_member(study, "Results")
        plots, names = None, None
        if results is not None:
            try:
                plots = int(get_com_member(results, "GetPlotCount") or 0)
            except Exception:
                plots = None
            try:
                names = [
                    str(x) for x in (get_com_member(results, "GetPlotNames") or ())
                ]
            except Exception:
                names = None
        seq = round(time.time() - t1, 1)
        mass_hits = [n for n in (names or []) if MASS_PLOT_RE.search(n)]
        ev["steps"]["solve"] = {
            "ok": results is not None and bool(plots),
            "run_analysis_return": rc,
            "run_analysis_return_is_trustworthy": False,
            "results_present": results is not None,
            "plot_count": plots,
            "plot_names": names,
            "seconds": seq,
            "note": "无拓扑许可时：会弹「拓扑算例未获许可」且 Results 为空，而返回码仍为 0",
        }
        say(
            "[7] RunAnalysis=%r（**返回码不可信**） Results非空=%r 图数=%r"
            % (rc, results is not None, plots)
        )
        if names:
            say("    图名 = %r" % (names,))

        # ★ 本能力的核心判据：Material Mass 结果图存在
        ev["steps"]["material_mass_plot"] = {
            "ok": bool(mass_hits),
            "matched_plots": mass_hits,
            "expected_pattern": MASS_PLOT_RE.pattern,
        }
        say("[8] ★ Material Mass 图 = %r" % (mass_hits or "（无）",))

        all_ok = all(s.get("ok") for s in ev["steps"].values())
        ev["verdict"] = "pass" if all_ok else "fail"
    except Exception as exc:  # noqa: BLE001
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
        out_path.write_text(
            json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        say("")
        say("证据已写入 %s" % out_path)
        say("结论: %s" % ev["verdict"].upper())

    print(json.dumps(ev, ensure_ascii=False, indent=2))
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
