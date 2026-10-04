"""★ 有界的**网格档位对照**：同一零件、四种设置各建一次网格，看谁成、谁卡、吃多少内存。

（★ 目的：★ 定下"安全档"到底该是什么 —— 实测说话，不猜）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SOLIDWORKS Simulation 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `scripts/sw_simulation.py`（`configure_mesh_settings` · `mesh_settings_report`）·
#         `scripts/sw_simulation_worker.py`（★ 隔离入口 + 忙检）· `scripts/sw_isolate.py`（可杀）
# 定位:   ★★★★ **为什么做这个对照**（2026-10-04 真机）：
#   · ★ 出厂设置（只读实测）：`Quality=1(High)` · **`MesherType=2(AlternateCB=曲率自适应)`** ·
#     `MinElementSize=0`（★ 没有加密下界）⇒ ★ **网格规模不受全局 `element_size` 约束** ✓
#   · ★ 我把安全档设成 `Quality=0(Draft)` + **`MesherType=0(Standard)`** ⇒
#     ★★ **建网格 300 秒没回来**（有界超时杀掉了它、会话完好、内存平稳）✓
#   · ★ 而**出厂设置**那次同样的 `create_mesh` **27 秒就返回**了（回 `rc=8` / 0 单元）✓
#   ⇒ ★★ **所以"安全档"里对 `MesherType` 的那一改**看起来**正是卡住的原因** ——
#     ★ 但**不能凭一次观察下结论** ⇒ ★ 做**四档对照**（同一零件、逐个重设、每个**有界**）：
#       V1 出厂（什么都不改）· V2 **只改 Quality=Draft** ·
#       V3 **只改 MesherType=Standard** · V4 两个都改（★ 我上一版的安全档）✓
#   ★ 判据（★ 每档记）：★ `CreateMesh` 的返回码/单元数/节点数 · 墙钟 · **有没有超时** ·
#     ★ 以及**全程内存**（看门狗另跑）✓
#   ⚠ ★ **每档之间把设置还原**（★ 免得互相污染 —— ★ 那正是"对照"的意义）✓
#   ⚠ ★ **有界**：每档 240 s（★ 超时就杀、如实记，不无限等 —— 事实 526 的纪律）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "mesh-profile-matrix-evidence.json"
STUDY = "SPEC202_MeshProfile_%d" % int(time.time())
T_EACH = 240.0

#: ★ 四档（★ 每档只写"要改的键"；★ 空 = 什么都不改）
VARIANTS: list[tuple[str, dict]] = [
    ("V1_出厂(不改)", {}),
    ("V2_只改Quality=Draft", {"quality": 0}),
    ("V3_只改MesherType=Standard", {"mesher_type": 0}),
    ("V4_两个都改(上一版安全档)", {"quality": 0, "mesher_type": 0}),
]


def flush(ev: dict) -> None:
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def main() -> int:
    ev: dict = {
        "★_目的": "四种网格设置各建一次网格 ⇒ 定下'安全档'到底是什么（★ 实测，不猜）",
        "★_前情": "出厂=Quality1+MesherType2+MinElementSize0（无下界）· 我上一版改成 Draft+Standard ⇒ 300s 超时",
        "study": STUDY, "每档上限_s": T_EACH, "variants": [],
    }
    flush(ev)
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_busy import wait_until_idle
        from scripts.sw_isolate import run_isolated

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                             # noqa: BLE001
            pass

        def iso(fn: str, args: list, kwargs: dict, timeout: float) -> dict:
            t0 = time.time()
            r = run_isolated("scripts.sw_simulation_worker", fn, args=args, kwargs=kwargs,
                             timeout=timeout)
            r["wall_seconds"] = round(time.time() - t0, 1)
            return r

        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        sim.ensure_simulation_addin(sw)
        sim.create_static_study(sw, STUDY)
        ev["steps_setup"] = {"study": STUDY, "bbox_mm": [100.0, 60.0, 30.0]}
        flush(ev)
        print("  [1] 零件+算例就绪：%s" % STUDY)

        #: ★ 单位口径：上一轮已实测 `units=2` 回毫米（4.9305）⇒ ★ 这里**明确用 2**（★ 不再自校准）
        ms = iso("mesh_size_by_name", [STUDY], {"units": 2}, 120)
        size = ((ms.get("result") or {}) if isinstance(ms.get("result"), dict) else {})
        element_size = float(size.get("element_size") or 0.0)
        tolerance = float(size.get("tolerance") or 0.0)
        ev["element_size_mm"] = element_size
        ev["tolerance_mm"] = tolerance
        flush(ev)
        print("  [2] units=2 ⇒ element_size=%s tolerance=%s" % (element_size, tolerance))
        if element_size <= 0:
            raise RuntimeError("拿不到毫米口径的建议值 ⇒ 停（%r）" % size)

        #: ★ 量预算前置闸（★ 用**零件文档**，不是 study —— 这一点上一版栽过）
        gate = sim.check_mesh_size_sane(doc, element_size)
        ev["size_gate"] = gate
        flush(ev)
        print("  [2b] 量闸: ok=%s est_elements=%.3g est_ram_gb=%.4g"
              % (gate.get("ok"), gate.get("est_elements") or 0, gate.get("est_ram_gb") or 0))
        if not gate.get("ok"):
            raise RuntimeError("量闸不放行 ⇒ 停：%s" % gate.get("reason"))

        before = ((iso("mesh_settings_by_name", [STUDY], {}, 120).get("result")) or {})
        ev["settings_before"] = {k: before.get(k) for k in
                                 ("Quality", "MesherType", "ElementSize", "MinElementSize",
                                  "MaxElementSize", "MinElementsInCircle", "NumberOfLoops")}
        flush(ev)
        print("  [3] 出厂设置：%s" % ev["settings_before"])

        for name, knobs in VARIANTS:
            wait_until_idle(timeout=60, interval=3)
            row: dict = {"variant": name, "knobs": knobs}
            if knobs:
                cfg = iso("configure_mesh_settings_by_name", [STUDY], knobs, 180)
                row["configure"] = {k: cfg.get(k) for k in ("ok", "timed_out", "wall_seconds")}
                row["configure_result"] = cfg.get("result")
            mr = iso("create_mesh_by_name", [STUDY],
                     {"units": 2, "element_size": element_size, "tolerance": tolerance}, T_EACH)
            row["mesh"] = {k: mr.get(k) for k in ("ok", "timed_out", "wall_seconds", "error")}
            row["mesh_result"] = mr.get("result")
            after = ((iso("mesh_settings_by_name", [STUDY], {}, 120).get("result")) or {})
            row["settings_after"] = {k: after.get(k) for k in
                                     ("Quality", "MesherType", "ElementCount", "NodeCount")}
            ev["variants"].append(row)
            flush(ev)
            print("  [%s] timed_out=%s wall=%ss element=%s node=%s"
                  % (name, mr.get("timed_out"), mr.get("wall_seconds"),
                     (mr.get("result") or {}).get("element_count")
                     if isinstance(mr.get("result"), dict) else None,
                     after.get("NodeCount")))
            #: ★ 还原（★ 免得污染下一档）
            if knobs:
                back = iso("configure_mesh_settings_by_name", [STUDY],
                           {"quality": before.get("Quality"),
                            "mesher_type": before.get("MesherType")}, 180)
                row["restored"] = {k: back.get(k) for k in ("ok", "timed_out")}
                flush(ev)
        ev["★_结论"] = "见 variants 逐档读数（★ 谁成/谁卡/单元数）"
        flush(ev)
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        flush(ev)
    finally:
        try:
            if doc is not None:
                import sw_connect as sc
                sc.safe_get_com_member(doc, "ClearSelection2", True)
                t = str(sc.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:                                             # noqa: BLE001
            pass
        flush(ev)
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
