"""★ 真机：★ **最小闭合轮廓能不能拉伸** —— 隔离「方程式曲线」与「拉伸」两件事。

★★★ **为什么要隔离**（★ 本仓的「一次只证伪一个假设」）：
  ★ 齿轮那边有 **6 条曲线 + 一个齿 + 轴孔**，★ 太多变量 ⇒ ★★ 失败时说不清是哪一环 ✗
  ★★ 本探针用**最小闭合轮廓**逐格加变量：
    ★ ① **4 条直线**（★ 基线：★ 证明 `extrude_boss` 在**本会话**可用）
    ★ ② **1 条方程式曲线 + 3 条直线**
    ★ ③ **2 条方程式曲线 + 2 条直线**
    ★ ④ **4 条方程式曲线**（★ 全真曲线闭合）
  ★★★ **判据**：★ 哪一格开始 `extrude` 回 `None` ⇒ ★ **那就是断点** ✓

★ 走 `sw_guard` ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_extrude_equation_profile.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 隔离"方程式曲线能否构成可拉伸轮廓"。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
#         `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
import traceback as _tb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


def _main() -> int:
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 最小闭合轮廓：★ 直线 vs 方程式曲线（★ 隔离拉伸断点）", "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)

    def run(tag, draw):
        doc = None
        row = {"tag": tag}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            draw(doc)
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                row["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
                row["points"] = len(list(C.get_com_member(sk, "GetSketchPoints2") or []))
                row["constrained_status"] = int(C.get_com_member(sk, "GetConstrainedStatus"))
            except Exception:                                             # noqa: BLE001
                pass
            try:
                P.end_sketch(doc)
                f = P.extrude_boss(doc, "草图1", 0.010)
                row["extrude_ok"] = f is not None
                if f is not None:
                    try:
                        mp = C.get_com_member(C.get_com_member(doc, "Extension"),
                                              "CreateMassProperty")
                        row["volume_mm3"] = round(
                            float(C.get_com_member(mp, "Volume")) * 1e9, 4)
                    except Exception:                                     # noqa: BLE001
                        pass
            except Exception as exc:                                      # noqa: BLE001
                row["extrude_ok"] = False
                row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        except Exception as exc:                                          # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:                                         # noqa: BLE001
                    pass
        return row

    #: ★ ① 4 条直线（★ 10×10 mm 方块）—— ★ 基线
    def d1(doc):
        P.sketch_line(doc, 0, 0, 10, 0)
        P.sketch_line(doc, 10, 0, 10, 10)
        P.sketch_line(doc, 10, 10, 0, 10)
        P.sketch_line(doc, 0, 10, 0, 0)
    rep["cases"].append(run("① 4 条直线（基线）", d1))

    #: ★ ② 1 条方程式曲线 + 3 条直线（★ 上边换成 y=0.01 的常值曲线）
    def d2(doc):
        sm = C.get_com_member(doc, "SketchManager")
        #: ★ 显式曲线：★ X 给 ""、Y 以 x 表达 ⇒ y = 0（★ 单位米）
        C.get_com_member(sm, "CreateEquationSpline2", "", "0.0", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        P.sketch_line(doc, 10, 0, 10, 10)
        P.sketch_line(doc, 10, 10, 0, 10)
        P.sketch_line(doc, 0, 10, 0, 0)
    rep["cases"].append(run("② 1 条方程式曲线 + 3 直线", d2))

    #: ★ ③ 2 条方程式曲线 + 2 条直线
    def d3(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2", "", "0.0", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2", "", "0.01", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        P.sketch_line(doc, 10, 0, 10, 10)
        P.sketch_line(doc, 0, 10, 0, 0)
    rep["cases"].append(run("③ 2 条方程式曲线 + 2 直线", d3))

    #: ★ ④ 4 条方程式曲线（★ 全真曲线闭合的 10×10 方块）
    def d4(doc):
        sm = C.get_com_member(doc, "SketchManager")
        #: 下边 y=0（x: 0→0.01）· 上边 y=0.01（x: 0.01→0）· 右边 x=0.01（y: 0→0.01）· 左边 x=0（y: 0.01→0）
        C.get_com_member(sm, "CreateEquationSpline2", "", "0.0", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2", "0.01", "t", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2", "", "0.01", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2", "0.0", "t", "",
                         "0.0", "0.01", False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("④ 4 条方程式曲线", d4))

    p = R / "output" / "_probe_extrude_equation_profile.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-28s 段=%-3s 点=%-3s 约束=%s 拉伸=%-6s 体积=%s %s"
              % (c.get("tag"), c.get("segments"), c.get("points"),
                 c.get("constrained_status"), c.get("extrude_ok"),
                 c.get("volume_mm3"), (c.get("extrude_err") or c.get("error") or "")[:70]))
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_extrude_eq_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
