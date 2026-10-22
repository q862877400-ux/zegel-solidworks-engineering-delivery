"""★ 真机：**"第一个载荷"那条规律**的独立确认 —— 换一个载荷当"第一个"，看回读是否照样崩。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_first_load_rule.py
# 定位:   ★ 2026-10-03（轮 419）承**事实 333** 之后**第四个假设也被否**（会话健康、零
#           文档），
#   ★★ 而真机数据指向一条**时序规律**：
# · 轮 418：`force` 是 **static 算例上的第一个**载荷 ⇒ ★ **它的回读崩了**（`0x80010105`
# ）
# · 轮 419：`distributed_mass` **先**、`force` **后** ⇒ ★ **三条全成**（`0→1 · 1→2 · 2→3
# `）
#   ⇒ ★★ **假设：★ "第一个载荷"那一次调用的**回读**会崩** —— ★ 而**载荷本身可能建成了** ⚠
#   ★★ **本探针把它做成"与具体载荷无关"的确认**：★ **换 `distributed_mass` 当"第一个"**
#     ⇒ ★ 若**它的回读也崩** ⇒ ★ 规律成立（★ 与哪个载荷无关，★ 只与"是不是第一个"有关）。
#   ★ 设计照**事实 324/325**：★ **每次都用一个新算例**（★ 唯一名）+ ★ **每格独立**。
# 官方依据: `swsAnalysisStudyTypeStatic = 0` · `ICWLoadsAndRestraintsManager.Count`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **"第一个"那次的回读崩、"第二个"那次的回读正常** ⇒ 规律成立。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "first-load-rule-evidence.json"
)


def main() -> int:
    import sw_connect

    from scripts import sw_simulation as sim
    from scripts import sw_simulation_loads as sl
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)

        #: ★ 两种"当第一个"的载荷（★ 与具体载荷无关才叫规律）
        firsts = [
            (
                "distributed_mass_first",
                lambda m: sl.apply_distributed_mass_report(m, doc, 1.0, 0),
            ),
            ("force_first", lambda m: sl.apply_force_report(m, doc, 1)),
        ]
        for label, fn in firsts:
            study = "%s_%s" % (label, time.strftime("%H%M%S"))
            cell: dict = {"trial": label, "study": study, "order": []}
            try:
                sim.create_static_study(sw, study)
                mgr = sim._loads_and_restraints_manager(
                    sim.get_study_by_name(sw, study)
                )
                #: ① **第一个**载荷
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                sim.select_face_at(doc, 0.0, 0.0, 0.0)
                r1 = fn(mgr)
                cell["order"].append(
                    {
                        "first": True,
                        "ok": bool(r1.get("ok")),
                        "count": [r1.get("count_before"), r1.get("count_after")],
                        "err": (r1.get("error") or "")[:80],
                    }
                )
                #: ② **第二个**载荷（★ 换另一个 —— ★ 只为看"第二个"的回读是否正常）
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                sim.select_face_at(doc, 0.0, 0.0, 0.0)
                r2 = sl.apply_remote_load_report(mgr, doc, 0, 0, 0.0, 0.0, -100.0)
                cell["order"].append(
                    {
                        "first": False,
                        "ok": bool(r2.get("ok")),
                        "count": [r2.get("count_before"), r2.get("count_after")],
                        "err": (r2.get("error") or "")[:80],
                    }
                )
                cell["first_readback_broke"] = not cell["order"][0]["ok"]
                cell["second_readback_ok"] = cell["order"][1]["ok"]
                cell["ok"] = True  #: ★ 这一格"跑完了"就算记录成功
            except Exception as exc:  # noqa: BLE001
                cell["ok"] = False
                cell["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
            ev["trials"].append(cell)
        #: ★ 规律成立 = **两格都**"第一个崩、第二个成"
        ev["rule_confirmed"] = all(
            c.get("first_readback_broke") and c.get("second_readback_ok")
            for c in ev["trials"]
            if c.get("ok")
        )
        ev["verdict"] = "pass" if ev["rule_confirmed"] else "partial"
        ev["note"] = (
            "★ 独立确认「**第一个载荷**那次的**回读**会崩」—— ★ **换两个不同的载荷当「第一个」**"
            "（★ `distributed_mass` 与 `force`）⇒ ★ 若**都**是「第一个崩、第二个成」 ⇒ 规律成立。"
            "★ 每格用**新算例 + 唯一名**（事实 324/325/414）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        for c in ev["trials"]:
            print(
                "  %-24s first=%s second=%s"
                % (
                    c.get("trial"),
                    c.get("first_readback_broke"),
                    c.get("second_readback_ok"),
                )
            )
        print(
            "  规律成立=%s · 产物: %s ⇒ %s"
            % (ev["rule_confirmed"], OUT, str(ev["verdict"]).upper())
        )
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
