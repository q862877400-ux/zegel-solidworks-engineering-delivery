"""★ 真机：**换判据前先验判据** —— 在已知成功的场景上同时读「旧判据」与「新判据」。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_judge_alternatives.py
# 定位:   ★ 2026-10-03（轮 418）承**事实 332** 的具体下一步。
#   ★★ 那一轮：B 组两条连接件的探针**拿不到回读** —— `manager.Count` 报
#     `com_error(-2147417851, '服务器出现意外情况')`（= **`0x80010105`**，
#     ★ 与事实 47 记的**同一个错误码**）。
#   ★★ 而**判据取不到 ⇒ 拿不到正例** ⇒ 按硬约束⑥ 不注册。★ 于是下一步是**换判据**。
#   ★ 而**换判据之前必须先验它稳不稳**（★ 事实 325 那条"换判据前先验判据"）：
#     ★ 在一个**已知成功**的场景（`apply_force` —— ★ 它会 +1，★ 那已被真机验过）上，
#     ★ 看**新判据**能不能**复现出 `0 → 1`**。
#   ★ 出厂类型库（**34.4.1.1011**）给出新判据的签名：
#     ```
#     GetLoadsAndRestraints(NIndex:Int32, ErrorCode:Int32&) -> CWLoadsAndRestraints
#     ```
#     ⇒ ★ **按序号取**（★ 数到取不到为止）★ 而 `ErrorCode` 是 **ByRef** ⇒ ★ 要补 `out_i4()`
#       （★ 事实 330 的教训：ByRef 不补就 `DISP_E_PARAMNOTOPTIONAL`）。
#   ★★ 而 `Count` 在类型库里是个**属性**（`P: Count : Int32`）⇒ ★ 走的是 `get_Count()`
#     —— ★ 本轮把**两条路都读一遍**，★ 才好判"到底哪条不稳"。
# 官方依据: 出厂类型库反射（形参名逐字）· `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **新判据能在已知成功的场景上复现 `0 → 1`** ⇒ 它可用；★ 否则它也不可用。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "judge-alternatives-evidence.json"
)
STUDY = "DSH-JUDGE_%s" % time.strftime("%H%M%S")


def _read_count(manager):
    """★ 旧判据：`Count` **属性**。"""
    from sw_connect import get_com_member

    try:
        v = get_com_member(manager, "Count")
        return {"value": int(v) if v is not None else None, "err": None}
    except Exception as exc:  # noqa: BLE001
        return {"value": None, "err": "%s: %s" % (type(exc).__name__, str(exc)[:110])}


def _read_list(manager):
    """★ 新判据：`GetLoadsAndRestraints(i, out_i4())` **按序号数**（★ ByRef 照事实 330 补）。"""
    from sw_connect import get_com_member, out_i4

    n = 0
    errs = []
    for i in range(0, 64):
        try:
            obj = get_com_member(manager, "GetLoadsAndRestraints", int(i), out_i4())
        except Exception as exc:  # noqa: BLE001
            errs.append("%s: %s" % (type(exc).__name__, str(exc)[:80]))
            break
        if obj is None:
            break
        n += 1
    return {"value": n, "err": errs[0] if errs else None}


def main() -> int:
    import sw_connect

    from scripts import sw_simulation as sim
    from scripts import sw_simulation_loads as SL
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

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

        ev["steps"]["count_before"] = _read_count(mgr)
        ev["steps"]["list_before"] = _read_list(mgr)
        #: ★ **已知成功**的场景：`apply_force`（★ 它已被真机验过会 +1）
        try:
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            sim.select_face_at(doc, 0.0, 0.0, 0.0)
            rep = SL.apply_force_report(mgr, doc, 1)
            ev["steps"]["apply_force"] = {
                "ok": bool(isinstance(rep, dict) and rep.get("ok")),
                "count": [rep.get("count_before"), rep.get("count_after")]
                if isinstance(rep, dict)
                else None,
                "error": (rep.get("error") or "")[:100]
                if isinstance(rep, dict)
                else None,
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["apply_force"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
            }
        ev["steps"]["count_after"] = _read_count(mgr)
        ev["steps"]["list_after"] = _read_list(mgr)

        cb = ev["steps"]["count_before"].get("value")
        ca = ev["steps"]["count_after"].get("value")
        lb = ev["steps"]["list_before"].get("value")
        la = ev["steps"]["list_after"].get("value")
        ev["old_judge_works"] = cb is not None and ca == (cb or 0) + 1
        ev["new_judge_works"] = lb is not None and la == (lb or 0) + 1
        ev["verdict"] = "pass" if ev["new_judge_works"] else "partial"
        ev["note"] = (
            "★ 在**已知成功**的场景（`apply_force`）上同时读两个判据："
            "★ 旧= `Count` 属性 · 新= `GetLoadsAndRestraints(i, out_i4())` 数个数。"
            "★ **新判据能复现 0→1 ⇒ 它可用**；★ 否则它也不可用（★ 那就不该换）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
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
