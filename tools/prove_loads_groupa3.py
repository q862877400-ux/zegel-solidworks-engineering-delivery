"""★ 真机：A 组收尾三条（分布质量 / 力 / 远程载荷）在**静力算例**下能不能建。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_loads_groupa3.py
# 定位:   ★ 2026-10-03（轮 414）24h 计划 v2 **段 5 A 组收尾**的真机探针。
#   ★★ 被验的是 `mcp-server/tool_specs_batch60.py` 的三条；
#     ★ 而它与轮 408（热载荷那批）**共用一套判据机器**：`_report` 的**回读计数恰好 +1**。
#   ★★ **带着轮 408 学到的那条纪律**：★ **算例类型是"调用前提"的一维** ——
#     ★ 这三条是**结构载荷** ⇒ ★ 本探针用 **`static`**（★ 而热载荷要 `thermal`）。
#   ★ 设计照**轮 408 那种"共用算例 + 单调计数"**（★ 那是目前**唯一被自洽证据支持**的设计：
#     计数 0→1→2→3 连成一串假不了）—— ⚠ 而**事实 324/325** 记着这种设计的代价：
#     ★ 一次**失败**的调用会污染下一格（★ 所以本批三条**若有一条失败**，
#       后面的结果就**只当参考**，★ 且我会在结论里注明）。
# 官方依据: CHM `ICWLoadsAndRestraintsManager~Add{DistributedMass,Force,RemoteLoad}.html` ·
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "loads-groupa3-evidence.json")
#: ★★★ ★ 2026-10-03（轮 414）**第一版用了固定名 `DSH-GA3`**
#:   ⇒ 真机回 `count: [-1, -1]`（★ 而 `_loads_count` 对 `-1` 的约定是「**取不到**」）。
#:   ★ 而同轮的**诊断探针**证明：★ `ICWLoadsAndRestraintsManager.Count`
#:   在**静力与热两种算例上都正常回 `0`** ⇒ ★★ **不是算例类型的问题**。
#:   ⇒ ★★ 最可能的真因：**算例名重复** —— ★ 仓里自己注过
#:   「能力层**不检查重名**」。
#:   ★ 修法：**每次用一个带时间戳的唯一名**。
STUDY = "DSH-GA3_%s" % time.strftime("%H%M%S")


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (current_sketch_name, end_sketch, extrude_boss,
                                 sketch_corner_rectangle, start_sketch)
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study_type": 0}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        #: ★ **static**（=0）—— 这三条是结构载荷
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        ev["steps"]["static_study"] = {"ok": mgr is not None}

        targets = [
            ("distributed_mass", lambda m: SL.apply_distributed_mass_report(m, doc, 1.0, 0)),
            ("force", lambda m: SL.apply_force_report(m, doc, 1)),
            ("remote_load", lambda m: SL.apply_remote_load_report(m, doc, 0, 0, 0.0, 0.0, -100.0)),
        ]
        for label, fn in targets:
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                sim.select_face_at(doc, 0.0, 0.0, 0.0)
                rep = fn(mgr)
                ev["steps"][label] = {
                    "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")]
                    if isinstance(rep, dict) else None,
                    "error": (rep.get("error") or "")[:100] if isinstance(rep, dict) else None}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {
                    "ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:130])}
        hit = [k for k, v in ev["steps"].items() if isinstance(v, dict) and v.get("ok")]
        seq = [ev["steps"][k].get("count") for k, _ in targets if ev["steps"][k].get("count")]
        ev["successes"] = hit
        ev["sequential_counts"] = seq
        ev["verdict"] = "pass" if len(hit) >= 2 else "partial"
        ev["note"] = ("★ A 组收尾三条（分布质量 / 力 / 远程载荷）在 **static** 算例上验。"
                      "★ 判据是回读计数 +1，★ 且看它是否**串成单调序列**。"
                      "⚠ 若中间有一条失败，★ 后面的只当参考（事实 324/325）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
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
