"""★ 只读：造零件+算例，然后**只读**网格设置那组数（★ 不写一个字节）—— 用来定单位口径。

（★ 为什么先只读：上一轮我直接写 `MinElementSize` ⇒ 把 SW 留在长计算里、主进程被杀它还烧 CPU）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SOLIDWORKS Simulation 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `scripts/sw_simulation.py`（`mesh_settings_report`）· `scripts/sw_simulation_w
# orker.py`
#         （`mesh_settings_by_name` —— ★ 隔离入口）· `scripts/sw_isolate.py`（可杀的子进程）
# 定位:   ★★★ **要回答的问题**（★ 铁律 5：不猜，去读）：
#     `ICWMesh` 那几个 `Double`（`ElementSize` / `MinElementSize` / `MaxElementSize`）
#     **到底吃什么单位**？—— ★ 上一轮我把 `element_size/2 = 2.465`（毫米）直接写进
#     `MinElementSize`，★ 结果探针在 SW 里卡了 13 分钟且 SW 主线程 `Not Responding`
# ⇒ ★★ 高度怀疑是**单位口径不对**（若它吃**米**，2.465 m 的"最小单元"比零件还大 ⇒ 网格器
# 无从下手）✓
#   ★ 判据：★ 读到的 `ElementSize` 与"官方建议值"比 —— 官方建议 ≈ 零件最大边的 1/20
#     ⇒ ★ 100 mm 的板：4.93 左右 ⇒ **毫米**；0.0049 左右 ⇒ **米** ✓
#   ★★ 全程**只读**，且**每一步都 flush 证据**（★ 崩了/挂了也不丢读数 —— 本仓既有做法）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "mesh-settings-readonly-evidence.json"
STUDY = "SPEC202_MeshSettings_%d" % int(time.time())


def flush(ev: dict) -> None:
    """★ 每一步都落盘（★ 挂住/被杀也不丢读数）。"""
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )


def main() -> int:
    ev: dict = {
        "★_目的": "只读网格设置那一组数 —— 定 `ElementSize`/`MinElementSize` 的**单位口径**",
        "★_前情": "上一轮把 2.465（毫米）写进 MinElementSize ⇒ 探针卡 13 分钟、SW Not Responding",
        "study": STUDY,
        "steps": {},
    }
    flush(ev)
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_isolate import run_isolated

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        sim.ensure_simulation_addin(sw)
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
        if study is None:
            raise RuntimeError("按名字取不到研究 %r" % STUDY)
        ev["steps"]["setup"] = {"study": STUDY, "bbox_mm": [100.0, 60.0, 30.0]}
        flush(ev)  # ★ 落盘
        print("  [1] 零件+算例就绪：%s" % STUDY)

        #: ★★ **只读**，而且走**可杀的子进程**（★ 上一轮就是卡在这里）
        r = run_isolated(
            "scripts.sw_simulation_worker",
            "mesh_settings_by_name",
            args=[STUDY],
            kwargs={},
            timeout=180,
        )
        ev["steps"]["mesh_settings"] = {
            k: r.get(k) for k in ("ok", "timed_out", "wall_seconds", "error")
        }
        ev["steps"]["mesh_settings"]["result"] = r.get("result")
        flush(ev)  # ★ 落盘
        print("  [2] 只读读数: ok=%s timed_out=%s" % (r.get("ok"), r.get("timed_out")))
        print("      result: %s" % str(r.get("result"))[:400])

        #: ★ 单位口径判据（★ 官方：建议单元尺寸 ≈ 零件最大边的 1/20 ⇒ 100 mm 板 ≈ 4.93）
        res = (r.get("result") or {}) if isinstance(r.get("result"), dict) else {}
        size = res.get("ElementSize")
        ev["★_单位口径判据"] = {
            "ElementSize": size,
            "零件最大边_mm": 100.0,
            "官方建议量级_约": "4.93",
            "★_结论": (
                "★ 4.93 量级 ⇒ **毫米**；0.0049 量级 ⇒ **米**；"
                "★ 读不到/为 None ⇒ **不下断言**（照铁律 5 写查不到）"
            ),
        }
        flush(ev)
    except Exception as exc:  # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        flush(ev)
    finally:
        try:
            import sw_connect

            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
        flush(ev)
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
