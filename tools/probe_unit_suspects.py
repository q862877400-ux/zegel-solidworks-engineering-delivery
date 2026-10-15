"""★ 单位实测：用「包围盒/体积」回读判据，验证 4 个可疑函数到底是毫米还是米。

★★ 判据（★ 不靠读代码，靠**回读几何**）：
   建一个 40×40×10 mm 的盒 ⇒ 已知正确（`create_basic_part` 每处都调 `mm()`）
   再对它做一次 fillet(R5) / chamfer(2) / shell(2) / dome(5)
   ⇒ ★ 若入参被当**米** ⇒ 结果会大 1000 倍（★ 肉眼可见）
   ⇒ ★ 若入参被当**毫米** ⇒ 结果正常
   ★★ 每条都回读**包围盒**（事实 71：`GetBodyBox` 回毫米）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/probe_unit_suspects.py
# 定位:   规格 315 的 ① 攻关 —— 单位根因的**实测确认**（不是静态分析）
# 官方依据: ① 本仓事实 2（入参毫米 · COM 侧米）· ② 事实 71（GetBodyBox 回毫米）
#           ③ IFeatureManager/FeatureFillet3.md（现行，14 参）
#           ④ IFeatureManager/InsertFeatureChamfer（官方签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   4 个可疑函数的单位口径
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")]

DIR = ROOT / "output" / "probe-unit-suspects"
EV: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}


def case(name: str, **kw) -> None:
    EV["cases"].append({"case": name, **kw})
    print("   %-40s %s" % (name, json.dumps(kw, ensure_ascii=False)[:110]))


def main() -> int:
    import sw_connect
    from scripts import sw_part

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    DIR.mkdir(parents=True, exist_ok=True)
    docs: list = []

    def bbox(doc) -> list | None:
        """★ 事实 71：`GetPartBox(False)` 回 **6 个数** = [xmin,ymin,zmin,xmax,ymax,zmax]（毫米）。

        ⚠ 第一版只取前 3 个（`[:3]`）⇒ 读到的是 **xmin/ymin/zmin**，不是尺寸
        ⇒ 把「尺寸」读成了「起点」，于是 fillet 那条读成 35.07（其实是 xmin）。
        ⇒ ★ 正确做法：**算 max − min**（这才是"尺寸"）。
        """
        try:
            pd = list(sw_connect.safe_get_com_member(doc, "GetPartBox", False))
            if len(pd) < 6:
                return None
            return [round(float(pd[3]) - float(pd[0]), 3),
                    round(float(pd[4]) - float(pd[1]), 3),
                    round(float(pd[5]) - float(pd[2]), 3)]
        except Exception:      # noqa: BLE001
            return None

    def mkbox(w=40.0, h=40.0, d=10.0):
        """★ 用「每处都调 mm()」的那条路建盒（★ 已知正确，作为基准）。"""
        doc = sw_connect.new_document(sw, "part")
        docs.append(doc)
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, w, h)
        sw_part.end_sketch(doc)
        #: ★ `extrude_boss` 收**米**（其 docstring 逐字：「depth: 拉伸深度（米）」
        #:   ⇒ 显式用 mm() 转，作为已知正确基准）
        sw_part.extrude_boss(doc, "草图1", sw_connect.mm(d))
        return doc

    try:
        #: ══ 基准：40×40×10 的盒 ══════════════════════════════
        d0 = mkbox()
        case("基准：40×40×10 盒", bbox=bbox(d0), expect="≈[40, 40, 10]")

        #: ══ ① fillet(R5) ════════════════════════════════════
        d1 = mkbox()
        try:
            #: ★ 选中一条竖直边（index 0）
            from scripts import sw_selection_spec
            sw_selection_spec.select_object(
                d1, sw_selection_spec.resolve_entity(d1, "index:0", "EDGE"))
            r = sw_part.fillet(d1, 5.0)          #: ★ 传 5（意图 5 mm）
            case("fillet(radius=5)", returned=str(r)[:40], bbox=bbox(d1),
                 expect="若毫米 ⇒ 包围盒仍 ≈[40,40,10]")
        except Exception as exc:      # noqa: BLE001
            case("fillet(radius=5)", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))

        #: ══ ② chamfer(distance=2) ═══════════════════════════
        d2 = mkbox()
        try:
            from scripts import sw_selection_spec
            sw_selection_spec.select_object(
                d2, sw_selection_spec.resolve_entity(d2, "index:0", "EDGE"))
            r = sw_part.chamfer(d2, 2.0)         #: ★ 传 2（意图 2 mm）
            case("chamfer(distance=2)", returned=str(r)[:40], bbox=bbox(d2),
                 expect="若毫米 ⇒ 包围盒仍 ≈[40,40,10]")
        except Exception as exc:      # noqa: BLE001
            case("chamfer(distance=2)", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))

        #: ══ ③ shell(thickness=2) ════════════════════════════
        d3 = mkbox()
        try:
            r = sw_part.shell_report(d3, 2.0)    #: ★ 传 2（意图 2 mm）
            case("shell(thickness=2)", returned=str(r)[:40], bbox=bbox(d3),
                 expect="若毫米 ⇒ 抽壳成功、包围盒不变")
        except Exception as exc:      # noqa: BLE001
            case("shell(thickness=2)", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))

        #: ══ ④ dome(height=5) ════════════════════════════════
        d4 = mkbox()
        try:
            r = sw_part.insert_dome_report(d4, 5.0)   #: ★ 传 5（意图 5 mm）
            case("dome(height=5)", returned=str(r)[:40], bbox=bbox(d4),
                 expect="若毫米 ⇒ 高度只多 5 mm")
        except Exception as exc:      # noqa: BLE001
            case("dome(height=5)", err="%s: %s" % (type(exc).__name__, str(exc)[:90]))

        EV["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out = DIR / "probe.json"
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
