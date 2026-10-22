"""★ 触发用：建件 → 设材料 → 建网格 → **跑求解**（★ 没有夹具/载荷 ⇒ 求解失败 ⇒ 会弹那两级弹窗）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/trigger_analysis_dialogs.py
# 定位:   ★ 2026-10-02（轮 377）**用户要求"再触发一次那两级弹窗"**，用来验 `sw_guard`
#           的自动处置。
# 官方依据: `C:\swapi\types\ICWStudy\RunAnalysis.md`（★ 零参；★ 返回码不可信，要读 `Resu
#           lts`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
# ★ 为什么它会弹窗（★ 上次的现场就是它）：
#   ★ 求解器要求"有夹具 + 有有效载荷"；而本脚本**故意不设载荷** ⇒
# ★★ 求解报「**未定义载荷或规定的位移**」⇒ **弹一个模态框**（★ 屏幕上无人点 ⇒ 会话冻住）
# 。
# ★ 而用户上次看到的是**两级**：先 `零件NN-… : 失败`（红 X）⇒ 点掉 ⇒ 再 `零件NN-… : 失败
# `（黄 !）。
# ★ 本脚本**不做处置** —— ★ 处置是 `sw_guard` 哨兵的事（★ 那正是要验的）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "trigger-analysis-dialogs.json"
)


def main() -> int:
    import sw_connect
    import sw_simulation as SIM
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        title = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        ev["doc"] = title
        #: ★ ① 材料（★ 让"材料未定义"这条不再是失败点）
        try:
            ev["steps"]["material"] = {
                "ok": True,
                "name": str(SIM.set_material(doc, "AISI 1020") or "")[:48],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["material"] = {"ok": False, "err": str(exc)[:100]}
        #: ★ ② 建研究（★ 静态）—— `create_static_study(sw_app, name)` 回 **`(study, entr
        #: y, err)`**，
        #: ★ 接着用 `get_study_by_name(sw, name)` **按名字取回 study 对象**（★ 契约，抄
        #: 前人
        #: `tools/capture_mesh_solve_evidence.py:95-96` 的用法；★ 直接拿元组当 study 会
        #: 报
        #:   `'tuple' object has no attribute 'CreateMesh'`）。
        SIM.create_static_study(sw, "DSH-TRIGGER")
        study = SIM.get_study_by_name(sw, "DSH-TRIGGER")
        ev["steps"]["study"] = {"ok": study is not None, "type": type(study).__name__}
        #: ★★ **故意不设夹具、不载荷** —— 复现用户的现场：★ 求解器报
        #: 「**未定义载荷或规定的位移**」⇒ **弹模态框**（★ 而这正是要验 `sw_guard` 的地
        #: 方）
        #: ★ ③ 建网格（★ 这一般能成）
        try:
            m = (
                SIM.create_mesh_report(study)
                if hasattr(SIM, "create_mesh_report")
                else None
            )
            ev["steps"]["mesh"] = {
                "ok": bool(m and m.get("ok")),
                "detail": str(m)[:120],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["mesh"] = {"ok": False, "err": str(exc)[:100]}
        #: ★★ ④ **跑求解** —— ★ **故意不设夹具/载荷** ⇒ ★ **这里会弹窗**（★ 而 `sw_guard
        #: ` 的哨兵该点掉它）
        try:
            r = SIM.run_analysis_report(study)
            ev["steps"]["run_analysis"] = {
                "ok": bool(r.get("ok")),
                "detail": str(r)[:200],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["run_analysis"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
            }
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:900])
        print("  ⇒ 落盘 %s" % OUT)
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
