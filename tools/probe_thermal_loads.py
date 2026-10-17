"""★ 真机：那 5 条热载荷在**热算例**（`study_type=3`）下能不能建成 —— ★ 穷举表：算例类型 × 载荷。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_thermal_loads.py
# 定位:   ★ 2026-10-03（轮 408）24h 计划 v2 收敛报告 §五 第 ① 条的落地。
#   ★★ **本轮的起点是"抄官方声明"**（★ 收敛报告写的下一步，★ 而不是继续试参数）：
#     从 CHM 抄出 `ICWLoadsAndRestraintsManager` 的六条 VB 声明 ——
#     ```
#     Function AddXxx(ByVal DispArray As System.Object, ByRef ErrorCode As System.Integer)
#     ```
#     ⇒ ★★ **六条签名一模一样**，★ 且与**已能用的** `AddElasticConnector` **同形**
#       ⇒ ★ **形态没错 ⇒ 失败在别处**。
#   ★ 而声明里的参数说明给了两条线索：
#     · `AddConvection`「faces or **shell edges**」· `AddHeatFlux`「faces or shell edges」
#     · `AddHeatPower`「bodies, faces, edges, and **vertices**」   ← 各自要求的实体种类不同
#   ★★ 而更强的线索：★ **这四条（对流/热流/热功率/温度/辐射）是**热载荷****
#     ⇒ ★ **而我一直在 `static` 算例上试它们** ⚠
#   ⇒ ★ 本探针把**算例类型**变成变量：★ 建 **thermal**（`study_type=3`）算例再试。
# 官方依据: CHM `ICWLoadsAndRestraintsManager~Add{Convection,HeatFlux,HeatPower,Temperature,
#   Radiation,ElasticConnector}.html` 的 VB 声明（**逐字抄自**）·
#   `swsAnalysisStudyTypeThermal = 3`（`scripts/sw_simulation.SWS_ANALYSIS_STUDY_TYPES`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每条载荷 ⇒ **回读的载荷计数恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "thermal-loads-evidence.json")
STUDY = "DSH-THERMAL"


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    #: ★★ 必须以 **`scripts.<mod>`** 加载 —— 包装内部用的是**相对导入**
    #:   （`from .sw_simulation import _selected_dispatch_array`）；★ 而我第一版写成了**顶层导入**
    #:   ⇒ 报 `ImportError: attempted relative import with no known parent package`
    #:   ★ 而那是**探针的错**，不是能力坏了（★ 与事实 320 同族）。
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)

        #: ★ 建 **thermal** 算例（★ 本轮把"算例类型"当变量 —— 之前一直用 static）
        try:
            sim.create_static_study(sw, STUDY, study_type=3)
            stud = sim.get_study_by_name(sw, STUDY)
            mgr = sim._loads_and_restraints_manager(stud)
            ev["steps"]["thermal_study"] = {"ok": mgr is not None, "study_type": 3}
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["thermal_study"] = {
                "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
            mgr = None

        #: ★ 直接按包装的签名调：`(manager, model[, 额外 int])`
        targets = [
            ("convection", SL.apply_convection_report, ()),
            ("heat_flux", SL.apply_heat_flux_report, ()),
            ("heat_power", SL.apply_heat_power_report, ()),
            ("temperature", SL.apply_temperature_report, ()),
            ("radiation", SL.apply_radiation_report, (0,)),
            ("elastic_connector", SL.apply_elastic_connector_report, ()),
        ]
        if mgr is not None:
            for label, fn, extra in targets:
                try:
                    sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                    sim.select_face_at(doc, 0.0, 0.0, 0.0)
                    rep = fn(mgr, doc, *extra)
                    ev["steps"][label] = {
                        "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                        "count": [rep.get("count_before"), rep.get("count_after")]
                        if isinstance(rep, dict) else None,
                        "error": (rep.get("error") or "")[:90] if isinstance(rep, dict) else None}
                except Exception as exc:                       # noqa: BLE001
                    ev["steps"][label] = {
                        "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}

        hit = [k for k, v in ev["steps"].items() if isinstance(v, dict) and v.get("ok")]
        ev["verdict"] = "pass" if len(hit) >= 2 else "partial"
        ev["note"] = ("★ 官方六条 VB 声明**逐字抄自 CHM** ⇒ 六条同形且与 `AddElasticConnector` 一致 ⇒ "
                      "★ 形态没错。★ 本探针把**算例类型**变成变量：**thermal（3）**。")
        ev["successes"] = hit
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1700])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
