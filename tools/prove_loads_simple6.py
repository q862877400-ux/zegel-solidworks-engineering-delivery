"""★ 真机验：段 5 的 6 个简单载荷（对流/弹性连接/热流/热功率/温度/辐射）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_loads_simple6.py
# 定位:   ★ 2026-10-03（轮 402）24h 计划 v2 **段 5** 第一批的真机探针（见
#   `mcp-server/tool_specs_batch58.py`）。
#   ★★ **调用姿势照既有脚本 `capture_simulation_loads_evidence.py` 的 `call_via_tool`** ——
#   ★ 它与注册器**同一顺序**（`inject` → `pre_call` → `derived_args`）⇒
#   ★ 这才是 AGENTS.md 说的「**按 ToolSpec 的契约调**」。
#   ★★ 而那条脚本里还留着一条**先例警告**：★「必须先 `ClearSelection2(True)` 再选下一个面」——
#   ★ 因为 `select_face_at` 的 `append=False` **只表示"不追加"、不清空** ⇒ 漏了这步会让
#   选区里**留着上一个面** ⇒ 回读计数变 2 ⇒ **判据假红**。★ 本探针照做。
# 官方依据: `ICWLoadsAndRestraintsManager` 的 `AddConvection` / `AddElasticConnector` /
#   `AddHeatFlux` / `AddHeatPower` / `AddTemperature` / `AddRadiation`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量）：★ 每个工具 ⇒ **回读的载荷计数恰好 +1**（★ 那正是 `_report` 的判据）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "mcp-server"))

OUT = Path(r"D:\AI\SW\output\loads-simple6-evidence.json")
STUDY = "DSH-LOADS6"


class _P:
    """★ 最小 params 容器（★ 与注册器传给解析器的形状一致）。"""

    def __init__(self, study_name="", selection="", radiation_type=0):
        self.study_name = study_name
        self.selection = selection
        self.radiation_type = radiation_type
        self.response_format = "json"


def main() -> int:
    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_simulation as sim
        import register_capabilities as rc
        import tool_specs_batch58 as b58

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        doc = sw_connect.new_document(sw, "part")
        from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                     sketch_corner_rectangle, start_sketch)
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sim.create_static_study(sw, STUDY)
        ev["steps"]["setup"] = {"ok": True,
                                "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
                                "study": STUDY}

        def call_via_tool(spec_name: str, params: _P):
            """★ 与注册器 L409-432 同一顺序：inject → pre_call → derived_args。"""
            spec = next(s for s in b58.SPECS_BATCH58 if s.name == spec_name)
            kwargs = {}
            for p in spec.params:
                if p.name in (spec.param_alias or {}) and spec.param_alias[p.name] is None:
                    continue
                kwargs[(spec.param_alias or {}).get(p.name, p.name)] = getattr(params, p.name)
            kwargs[spec.inject] = rc.RESOLVERS[spec.inject](params)
            if spec.pre_call is not None:
                spec.pre_call(params)
            kwargs.update(spec.derived_args(params) or {})
            fn = getattr(__import__("scripts.%s" % spec.module, fromlist=[spec.function]),
                         spec.function)
            return fn(**kwargs)

        #: ★ 每个载荷都：清空选区 ⇒ 选顶面 ⇒ 调工具（★ 顺序照先例警告）
        load_specs = (
            ("solidworks_simulation_apply_convection", {}),
            ("solidworks_simulation_apply_elastic_connector", {}),
            ("solidworks_simulation_apply_heat_flux", {}),
            ("solidworks_simulation_apply_heat_power", {}),
            ("solidworks_simulation_apply_temperature", {}),
            ("solidworks_simulation_apply_radiation", {"radiation_type": 0}),
        )
        for spec_name, extra in load_specs:
            label = spec_name.replace("solidworks_simulation_apply_", "")
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                n_sel = sim.select_face_at(doc, 0.0, 0.0, 0.0)
                params = _P(study_name=STUDY, selection="__current_selection__", **extra)
                rep = call_via_tool(spec_name, params)
                ev["steps"][label] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "selected": n_sel,
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "report_keys": sorted(rep)[:8] if isinstance(rep, dict) else None,
                }
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {"ok": False,
                                      "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 段 5 第一批 6 条简单载荷；★ 判据是**回读计数恰好 +1**。"
                      "★ 调用走**工具层同序**（inject → pre_call → derived_args），"
                      "★ 且每次**先 ClearSelection2**（★ 先例：select_face_at 不清空选区）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1800])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if sw is not None and doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
