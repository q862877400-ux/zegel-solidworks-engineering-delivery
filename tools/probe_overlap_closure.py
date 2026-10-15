"""★ 真机：★ **让相邻真曲线轻微交叠** ⇒ 轮廓真闭合（★ 机械 CAD 的通行做法）。

★★★ **真机已证的断点**（★ 证据 `output/_probe_extrude_equation_profile.json`）：
  ```
  ★ ① 4 条**直线**        段=4 点=4 拉伸=**True** 体积=1000.0 mm³  ⇒ ★ 基线好 ✓
  ★ ② 1 曲线 + 3 直线     段=4 点=**5** 拉伸=**False**            ⇒ ★ 混用即失败 ✗
  ★ ③ 2 曲线 + 2 直线     段=4 点=**7** 拉伸=**False**            ⇒ ★ 混用即失败 ✗
  ```
  ★★ **读数含义**：★ 点数是 4 时闭合；★ 变 5/7 ⇒ ★ **接缝处多出孤立点** ⇒ **轮廓有缝** ✗
  ★★★ 根因：★ `CreateEquationSpline2` **按自己的精度离散**方程 ⇒
    ★ 端点落在解析位置 **0.7 ~ 1.7 µm** 外（★ `output/_probe_gear_endpoints.json`）⇒
    ★★ 与**相邻曲线**接不上 ✗

★★★ **规范修法**：★ 让**相邻曲线的参数范围轻微交叠** ⇒
  ★ 两条曲线**真的相交** ⇒ ★ SolidWorks 自动求出**交点** ⇒ **轮廓闭合** ✓
  ★★ 这正是机械 CAD 的通行做法（★ "画长一点再剪"）✓

★ 判据：★ ① 点数回到 4（★ 无孤立点）· ★ ② 拉伸返回非 None · ★ ③ 体积 ≈ 解析 ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_overlap_closure.py
# 定位:   ★ 业主 2026-10-10「方法要规范」—— ★ 真曲线闭合的**交叠**判据。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`
#         `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`
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
           "_": "★ 相邻真曲线轻微交叠 ⇒ 轮廓闭合（★ 10×10 mm 方块）", "cases": []}
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

    #: ★ **正确的 4 条显式曲线**（★ 构成 10×10 mm 方块 · ★ 每条边都交叠一点）
    #:   ★ 底边 y=0, x: −δ → 0.01+δ  ⇒ `""` + `"0.0"`，range 用 x
    #:   ★ 右边 x=0.01, y: −δ → 0.01+δ ⇒ `"0.01"` + `"t"`
    #:   ★ 顶边 y=0.01, x: −δ → 0.01+δ
    #:   ★ 左边 x=0, y: −δ → 0.01+δ
    def mk(delta):
        d = "%.9f" % delta
        lo = "-%s" % d
        hi = "%.9f" % (0.01 + delta)

        def draw(doc):
            sm = C.get_com_member(doc, "SketchManager")
            #: 底边（★ 显式 y=f(x) ⇒ X 给 ""）
            C.get_com_member(sm, "CreateEquationSpline2", "", "0.0", "", lo, hi,
                             False, 0.0, 0.0, 0.0, True, True)
            #: 右边（★ 参数式 x=0.01, y=t）
            C.get_com_member(sm, "CreateEquationSpline2", "0.01", "t", "", lo, hi,
                             False, 0.0, 0.0, 0.0, True, True)
            #: 顶边
            C.get_com_member(sm, "CreateEquationSpline2", "", "0.01", "", lo, hi,
                             False, 0.0, 0.0, 0.0, True, True)
            #: 左边（★ 参数式 x=0, y=t）
            C.get_com_member(sm, "CreateEquationSpline2", "0.0", "t", "", lo, hi,
                             False, 0.0, 0.0, 0.0, True, True)
        return draw

    for tag, delta in (("① 交叠 0（★ 端点相接）", 0.0),
                       ("② 交叠 0.05 mm", 0.00005),
                       ("③ 交叠 0.2 mm", 0.0002),
                       ("④ 交叠 1 mm", 0.001)):
        rep["cases"].append(run(tag, mk(delta)))

    p = R / "output" / "_probe_overlap_closure.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str) + "\n",
                 encoding="utf-8")
    for c in rep["cases"]:
        print("  ★ %-26s 段=%-3s 点=%-3s 拉伸=%-6s 体积=%s %s"
              % (c.get("tag"), c.get("segments"), c.get("points"),
                 c.get("extrude_ok"), c.get("volume_mm3"),
                 (c.get("extrude_err") or c.get("error") or "")[:64]))
    print("  产物：%s" % p)
    return 0


def main() -> int:
    try:
        return _main()
    except BaseException:                                                 # noqa: BLE001
        (R / "output" / "_probe_overlap_tb.txt").write_text(
            _tb.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
