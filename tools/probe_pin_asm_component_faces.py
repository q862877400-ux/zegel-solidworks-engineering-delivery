"""★ 真机：销钉连接件的**最后一个候选** —— ★ 装配体 + 「**组件上的面**」。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_pin_asm_component_faces.py
# 定位:   ★ 2026-10-03（轮 427）承**事实 340** 的收窄结论。
#   ★★ 事实 340 试过的组合（★ 逐条都留了干净读数）：
#     ```
#     · 装配体（两零件） + **组件**   ⇒ `0→0` ✗
#     · 多体零件        + **面**      ⇒ `0→0` ✗
#     ⇒ ★★ **只剩一个没试**：★ **装配体 + 「组件上的面」** ✓
#     ```
#   ★★ 而那条链是：★ **`IComponent2.GetBody()`**（★ 0 参，★ 出厂类型库里有；
#     ⚠★ **而 `GetBody2` 不在** —— ★ 按**铁律 5** 用存在的那个）
#     ⇒ ★ 拿到**该组件的体** ⇒ ★ `IBody2.GetFaces()` ⇒ ★ 取面。
#   ★★ 而它**与 rigid 成的那次是同一个形状**（★ "两个东西 + 每侧一个实体"）：
#     ★ rigid 成于 **两个体 + 每侧一个面** ⇒ ★ 两条现在指向同一个形态 ✓
# ⚠ ★ 按**事实 53**：★ pin 这一处已是**第 5 次** —— ★ **若这次也不成，就该停**（★ 记进 l
# imitations）。
# 官方依据: `IComponent2.GetBody()`（★ 出厂类型库反射）· `IBody2.GetFaces()` ·
# `AddPinConnector(DispArrayComp1, DispArrayComp2, ErrorCode&)` · `swsAnalysisStudyTypeS
# tatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个组件都能拿到体与面（★ 入口）★ 且施加后回读计数**恰好 +1**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "pin-asm-component-faces-evidence.json"
)
STUDY = "DSH-PINCF_%s" % time.strftime("%H%M%S")
SAMPLES = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples\tutorial\api"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts import sw_simulation as sim
    from scripts.sw_assembly import add_component
    from scripts import sw_simulation_loads as SL

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "study": STUDY}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "assembly")
        add_component(doc, str(SAMPLES / "block.sldprt"), 0.0, 0.0, 0.0, "", sw)
        add_component(doc, str(SAMPLES / "block20.sldprt"), 0.1, 0.0, 0.0, "", sw)
        raw = get_com_member(doc, "GetComponents", True)
        comps = list(raw) if raw else []

        #: ★ **先验入口**：★ 每个组件都能拿到**体**与**面**
        comp_faces = []
        detail = []
        for i, c in enumerate(comps[:2]):
            rec = {"i": i}
            try:
                body = get_com_member(c, "GetBody")
                rec["has_body"] = body is not None
                faces = (
                    list(get_com_member(body, "GetFaces")) if body is not None else []
                )
                rec["face_count"] = len(faces)
                comp_faces.append(faces[0] if faces else None)
            except Exception as exc:  # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
                comp_faces.append(None)
            detail.append(rec)
        ev["steps"]["entry_check"] = {
            "ok": len(comps) >= 2 and all(f is not None for f in comp_faces[:2]),
            "components": len(comps),
            "detail": detail,
            "note": "★ 先验入口：★ 两个组件各拿到一个面 ⇒ 才继续施加",
        }
        sim.create_static_study(sw, STUDY)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, STUDY))
        if (ev["steps"].get("entry_check") or {}).get("ok"):
            try:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                rep = SL._report(
                    mgr,
                    lambda: SL.add_pin_connector(mgr, [comp_faces[0]], [comp_faces[1]]),
                    "pin_component_faces",
                    doc,
                )
                ev["steps"]["pin_component_faces"] = {
                    "ok": bool(rep.get("ok")),
                    "count": [rep.get("count_before"), rep.get("count_after")],
                    "error": (rep.get("error") or "")[:130],
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["pin_component_faces"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                }
        else:
            ev["steps"]["pin_component_faces"] = {
                "ok": False,
                "skipped": "★ 入口没验过 ⇒ 不施加",
            }
        ev["verdict"] = (
            "pass"
            if (ev["steps"].get("pin_component_faces") or {}).get("ok")
            else "partial"
        )
        ev["note"] = (
            "★ 销钉连接件的**最后一个候选**：★ 装配体 + **组件上的面** —— "
            "★ 即 `IComponent2.GetBody()` 拿体、再 `GetFaces()` 取面。"
            "★ 判据：① 两组件各拿到一个面 ② 施加后计数恰好 +1。"
            "★ 零件用**已在盘上的**自带件 ⇒ ★ 不保存任何东西（硬约束⑦）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
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
