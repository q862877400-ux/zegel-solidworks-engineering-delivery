"""★ 真机：B 组开头两条（链接连接件 · 刚性连接件）—— ★ "把选区一分为二"那条形态。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_connectors_two.py
# 定位:   ★ 2026-10-03（轮 417）24h 计划 v2 **段 5 B 组**的真机探针。
#   ★★ **B 组（多面 / 多顶点）此前做不了** —— ★ 而轮 415/416 把**出厂类型库**读通之后
#     **每个成员的形参表都有了** ⇒ ★ 本轮据此挑出两条**选择方式明确**的：
#     ```
#     AddLinkConnector(VertexPointforFirstLocation, VertexPointforSecondLocation)   ← 两个顶点
#     AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray)                   ← 两组面
#     ```
#   ★ 姿态照**轮 408 那条已验证的设计**：★ **共用一个算例 + 看计数是否单调**；
#     ★ 而算例名照**轮 414 的教训**用**唯一名**。
#   ★★ 而"**算例类型**"这一维照旧**不能一概而论**（★ 事实 323/330）：★ 本探针先用 **static**。
# 官方依据: 出厂类型库（`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）反射出的形参名 ·
#   `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每条 ⇒ **回读计数恰好 +1**（★ 并且**串成单调序列**）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "connectors-two-evidence.json")
STUDY = "DSH-CONN_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts.sw_selection_spec import select_entity_by_index
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study": STUDY}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        #: ★ 诊断：**直接读一次 `manager.Count`**（★ 而不经 `_report`）
        #:   —— ★ 因为前一版回 `count: [-1,-1]`，而那是 `_loads_count` 对
        #:   「**取不到**」的约定 ⇒ ★ 先看原始值。
        _raw_count = None
        _raw_err = None
        try:
            from sw_connect import get_com_member as _gcm
            _raw_count = _gcm(mgr, "Count")
        except Exception as _exc:                          # noqa: BLE001
            _raw_err = "%s: %s" % (type(_exc).__name__, str(_exc)[:120])
        ev["steps"]["static_study"] = {"ok": mgr is not None, "manager": type(mgr).__name__,
                                       "raw_Count": repr(_raw_count), "raw_err": _raw_err}

        def two(kind, i=0, j=1):
            """★ 选两个同类实体（★ 前一个 / 后一个）—— ★ 双实体连接件的共同前置。"""
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            select_entity_by_index(doc, kind, i)
            select_entity_by_index(doc, kind, j, append=True)

        cases = [
            ("link_connector", "VERTEX", lambda m: SL.apply_link_connector_report(m, doc)),
            ("rigid_connector", "FACE", lambda m: SL.apply_rigid_connector_report(m, doc)),
        ]
        for label, kind, fn in cases:
            try:
                two(kind)
                rep = fn(mgr)
                ev["steps"][label] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "error": (rep.get("error") or "")[:110] if isinstance(rep, dict) else None}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}
        hit = [k for k, v in ev["steps"].items() if isinstance(v, dict) and v.get("ok")]
        ev["successes"] = hit
        ev["sequential_counts"] = [ev["steps"][k].get("count") for k, _, _ in cases]
        ev["verdict"] = "pass" if len(hit) >= 2 else "partial"
        ev["note"] = ("★ B 组开头两条：★ 链接连接件（两个**顶点**）· 刚性连接件（两组**面**）。"
                      "★ 判据是回读计数 +1，★ 且看是否串成单调序列。"
                      "⚠ 若中间有一条失败，★ 后面的只当参考（事实 324/325）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1400])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
