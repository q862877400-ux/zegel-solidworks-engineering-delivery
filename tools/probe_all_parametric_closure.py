"""★ 真机：★ **全参数式方程式曲线**构成的闭合轮廓（★ 不混直线）—— 决定性判据。

★★★ **已有铁证**（★ `output/_probe_extrude_equation_profile.json`）：
  ```
  ★ ① 4 直线        点=4 拉伸=✓  ⇒ 直线间**自动合并**角点 ✓
  ★ ② 1曲线+3直线   点=5 拉伸=✗  ⇒ 曲线与直线**不合并** ✗
  ★ ③ 2曲线+2直线   点=7 拉伸=✗  ⇒ 同上 ✗
  ★ ④ 4 曲线        点=4 拉伸=✓  ⇒ ★ **曲线之间能合并** ✓（★ 只是我表达式退化了）
  ```
  ★★ **规律**：★ **同类实体之间**会合并端点 · ★ **异类之间**（曲线↔直线）不会 ✗
  ★★★ **⇒ 正解**：★ 让**整条轮廓全部由方程式曲线构成** ✓

★★★ **本探针的三格（★ 全部参数式 · 不混直线）**：
  ★ ① **正方形**：★ 4 条参数式曲线（★ 每条**覆盖整条边**，★ 端点精确落在角上）
  ★ ② **三角形**：★ 3 条参数式曲线
  ★ ③ **圆**：★ 1 条参数式曲线（★ 闭合自环 —— ★ 官方 Remarks 提过闭合曲线）

★ 判据：★ 拉伸返回非 None · ★ 体积 ≈ 解析（★ 正方形 1000 mm³ · 三角形 500 · 圆 π×100×10）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_all_parametric_closure.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 全参数式曲线轮廓的**闭合**判据。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ---------------------------------------------------------------------
from __future__ import annotations

import json
import sys
import time
import traceback as _tb
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402


def _main() -> int:
    rep = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "_": "★ 全参数式方程式曲线构成的闭合轮廓", "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)

    def run(tag, draw, expect_mm3=None):
        doc = None
        row = {"tag": tag, "expect_mm3": expect_mm3}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            draw(doc)
            try:
                sk = C.get_com_member(doc, "GetActiveSketch2")
                row["segments"] = len(list(C.get_com_member(sk, "GetSketchSegments") or []))
                row["points"] = len(list(C.get_com_member(sk, "GetSketchPoints2") or []))
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
                        v = round(float(C.get_com_member(mp, "Volume")) * 1e9, 4)
                        row["volume_mm3"] = v
                        if expect_mm3:
                            row["ratio"] = round(v / expect_mm3, 6)
                    except Exception:                                     # noqa: BLE001
                        pass
            except Exception as exc:                                      # noqa: BLE001
                row["extrude_ok"] = False
                row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
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

    A = 0.01   #: ★ 10 mm

    #: ① 正方形：★ 4 条**参数式**曲线（★ 每条 0→1，★ 端点精确在角上）
    def d1(doc):
        sm = C.get_com_member(doc, "SketchManager")
        #: 底边：★ x = A·t, y = 0        （★ 参数式：X 与 Y 都给 t 的表达式）
        C.get_com_member(sm, "CreateEquationSpline2", "%.9f*t" % A, "0.0", "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
        #: 右边：★ x = A, y = A·t
        C.get_com_member(sm, "CreateEquationSpline2", "%.9f" % A, "%.9f*t" % A, "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
        #: 顶边：★ x = A(1−t), y = A
        C.get_com_member(sm, "CreateEquationSpline2",
                         "%.9f-%.9f*t" % (A, A), "%.9f" % A, "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
        #: 左边：★ x = 0, y = A(1−t)
        C.get_com_member(sm, "CreateEquationSpline2", "0.0",
                         "%.9f-%.9f*t" % (A, A), "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("① 正方形（4 参数式曲线）", d1, 1000.0))

    #: ② 三角形：★ 3 条参数式曲线（★ 直角边 10 mm ⇒ 面积 50 mm² ⇒ 体积 500）
    def d2(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2", "%.9f*t" % A, "0.0", "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2",
                         "%.9f-%.9f*t" % (A, A), "%.9f*t" % A, "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
        C.get_com_member(sm, "CreateEquationSpline2", "0.0",
                         "%.9f-%.9f*t" % (A, A), "",
                         "0", "1", False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("② 三角形（3 参数式曲线）", d2, 500.0))

    #: ③ 圆：★ 1 条参数式曲线（★ 闭合自环 —— ★ 面积 π×100 mm² ⇒ 体积 π×100×10）
    def d3(doc):
        sm = C.get_com_member(doc, "SketchManager")
        C.get_com_member(sm, "CreateEquationSpline2",
                         "%.9f*cos(t)" % A, "%.9f*sin(t)" % A, "",
                         "0", "6.283185307179586", False, 0.0, 0.0, 0.0, True, True)
    rep["cases"].append(run("③ 圆（1 条参数式曲线 · 闭合自环）", d3, 3141.5927))

    p = R / "output" / "_probe_all_parametric_closure.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-34s 段=%-3s 点=%-3s 拉伸=%-6s 体积=%-10s 比值=%s %s"
              % (c.get("tag"), c.get("segments"), c.get("points"), c.get("extrude_ok"),
                 c.get("volume_mm3"), c.get("ratio"),
                 (c.get("extrude_err") or c.get("error") or "")[:56]))
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_allpar_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
