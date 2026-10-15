"""★ 验证：草图族修好没有（★ 真机 + 包围盒判据）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/probe_sketch_units_after_fix.py
# 定位:   单位修复的**真机复核**（★ 不靠静态分析）
# 官方依据: ① `output/probe-unit-decisive/decisive.json`（修前的基准读数）
#           ② 本仓事实 71（`GetPartBox` 回毫米）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   sw_sketch_primitives.py 的 9 个图元
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")]

DIR = ROOT / "output" / "probe-sketch-units-fixed"
EV: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}


def case(name: str, **kw) -> None:
    EV["cases"].append({"case": name, **kw})
    print("   %-40s %s" % (name, json.dumps(kw, ensure_ascii=False)[:110]))


def main() -> int:
    import sw_connect
    from scripts import sw_part, sw_sketch_primitives as sp

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    DIR.mkdir(parents=True, exist_ok=True)
    docs: list = []

    def size(d) -> list | None:
        try:
            pd = list(sw_connect.safe_get_com_member(d, "GetPartBox", False))
            if len(pd) < 6:
                return None
            return [round(float(pd[3]) - float(pd[0]), 4),
                    round(float(pd[4]) - float(pd[1]), 4),
                    round(float(pd[5]) - float(pd[2]), 4)]
        except Exception:      # noqa: BLE001
            return None

    try:
        #: ══ ① 3 点矩形（★ 应得 40×30 mm）═════════════════════
        d1 = sw_connect.new_document(sw, "part")
        docs.append(d1)
        sw_part.start_sketch(d1)
        sp.sketch_3point_corner_rectangle(d1, 0.0, 0.0, 40.0, 0.0, 40.0, 30.0)
        sw_part.end_sketch(d1)
        sw_part.extrude_boss(d1, "草图1", sw_connect.mm(10))   #: ★ 显式传米
        case("① 3点矩形 40×30 + 拉伸10mm", size=size(d1),
             expect="≈[40, 30, 10]（★ 修好）")

        #: ══ ② 3 点中心矩形 ═══════════════════════════════════
        d2 = sw_connect.new_document(sw, "part")
        docs.append(d2)
        sw_part.start_sketch(d2)
        sp.sketch_3point_center_rectangle(d2, 0.0, 0.0, 25.0, 0.0, 0.0, 15.0)
        sw_part.end_sketch(d2)
        sw_part.extrude_boss(d2, "草图1", sw_connect.mm(10))
        case("② 3点中心矩形 50×30 + 拉伸10mm", size=size(d2),
             expect="≈[50, 30, 10]")

        #: ══ ③ 平行四边形 ═════════════════════════════════════
        d3 = sw_connect.new_document(sw, "part")
        docs.append(d3)
        sw_part.start_sketch(d3)
        sp.sketch_parallelogram(d3, 0.0, 0.0, 40.0, 0.0, 10.0, 20.0)
        sw_part.end_sketch(d3)
        sw_part.extrude_boss(d3, "草图1", sw_connect.mm(10))
        case("③ 平行四边形 + 拉伸10mm", size=size(d3), expect="X≈50, Y≈20")

        #: ══ ④ 周边圆（★ 三个点在 φ40 圆上）═══════════════════
        d4 = sw_connect.new_document(sw, "part")
        docs.append(d4)
        sw_part.start_sketch(d4)
        sp.sketch_perimeter_circle(d4, 20.0, 0.0, -20.0, 0.0, 0.0, 20.0)
        sw_part.end_sketch(d4)
        sw_part.extrude_boss(d4, "草图1", sw_connect.mm(10))
        case("④ 周边圆 φ40 + 拉伸10mm", size=size(d4), expect="≈[40, 40, 10]")

        #: ══ ⑤ 对比：草图圆（★ 已知正确的那条路）═════════════
        d5 = sw_connect.new_document(sw, "part")
        docs.append(d5)
        sw_part.start_sketch(d5)
        sw_part.sketch_circle(d5, 0.0, 0.0, 20.0)     #: ★ 半径 20 ⇒ φ40
        sw_part.end_sketch(d5)
        sw_part.extrude_boss(d5, "草图1", sw_connect.mm(10))
        case("⑤ 对照：sketch_circle(20) + 拉伸10mm", size=size(d5),
             expect="≈[40, 40, 10]（★ 已知正确，做基准）")

        EV["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out = DIR / "after.json"
        out.write_text(json.dumps(EV, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\n★ 证据 → %s" % out)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in reversed(docs):
            try:
                t = sw_connect.safe_get_com_member(d, "GetTitle")
                if callable(t):
                    t = t()
                if t:
                    sw.CloseDoc(str(t))
            except Exception:      # noqa: BLE001
                pass


if __name__ == "__main__":
    raise SystemExit(main())
