"""★ 真机：★ `CreateEquationSpline2` 的 `RotationAngle` 与 `XOffset/YOffset` 可不可用。

★★★ **为什么必须探**：★ 业主令「**方法要规范**」—— 一个 20 齿的齿轮，
  ★ 若**每个齿都要把相位角编进表达式**，★ 那表达式会**膨胀 20 倍**且极易写错；
  ★★ 而官方签名里**本来就有** `RotationAngle`（★ rad）⇒
    ★★★ **它可用的话，20 个齿 = 同一个方程 × 20 个转角**（★ 那才叫优雅）✓
  ⚠ 但官方 Remarks 逐字说它「**for legacy support only**」⇒ ★ **必须真机判**，★ 不臆造 ✓

★ 判据：★ **段数增加**（★ 事实 436）+ ★ **包围盒随转角变化**（★ 证明真的转了）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_equation_rotation.py
# 定位:   ★ 业主 2026-10-10 指令「方法要规范」—— ★ 判「一个方程 × N 个转角」可不可行。
# 官方依据: `C:\swapi\types\ISketchManager\CreateEquationSpline2.md`（★ RotationAngle 语义）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                   # noqa: E402
from scripts import sw_part as P                                      # noqa: E402

RB = 9.396926208  #: ★ 模数 1 · 齿数 20 · 20° ⇒ rb


def _seg_count(doc):
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        return len(list(C.get_com_member(sk, "GetSketchSegments") or [])) if sk else -1
    except Exception:                                                     # noqa: BLE001
        return -1


def _bbox_of_sketch(doc):
    """★ 草图段端点的包围盒（★ 用它证明"真的转了"）。"""
    try:
        sk = C.get_com_member(doc, "GetActiveSketch2")
        segs = list(C.get_com_member(sk, "GetSketchSegments") or [])
        xs, ys = [], []
        for s in segs:
            for m in ("GetStartPoint2", "GetEndPoint2"):
                pt = C.get_com_member(s, m)
                if pt is None:
                    continue
                arr = list(pt)
                if len(arr) >= 2:
                    xs.append(float(arr[0]) * 1000.0)
                    ys.append(float(arr[1]) * 1000.0)
        if not xs:
            return None
        return {"dx": round(max(xs) - min(xs), 4), "dy": round(max(ys) - min(ys), 4),
                "cx": round((max(xs) + min(xs)) / 2, 4), "cy": round((max(ys) + min(ys)) / 2, 4)}
    except Exception:                                                     # noqa: BLE001
        return None


def _one(sw, tag, rot_rad, xoff=0.0, yoff=0.0):
    row = {"tag": tag, "rot_rad": rot_rad, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        sm = C.get_com_member(doc, "SketchManager")
        before = _seg_count(doc)
        try:
            C.get_com_member(sm, "CreateEquationSpline2",
                             "%.9f*(cos(t)+t*sin(t))" % RB,
                             "%.9f*(sin(t)-t*cos(t))" % RB,
                             "", "0", "0.608517823",
                             False, rot_rad, xoff, yoff, True, True)
        except Exception as exc:                                          # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = _seg_count(doc)
        row["seg"] = [before, after]
        row["ok"] = bool(after >= 0 and before >= 0 and after > before)
        row["bbox_mm"] = _bbox_of_sketch(doc)
        try:
            P.end_sketch(doc)
        except Exception:                                                 # noqa: BLE001
            pass
    except Exception as exc:                                              # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:170])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                             # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "★ 方程式曲线的 RotationAngle / XOffset / YOffset 可用性",
          "why": "★ 判「同一个渐开线方程 × N 个转角」能不能拼出整圈齿轮（★ 优雅做法）",
          "cases": []}
    for tag, rot in (("① 转角 0°", 0.0),
                     ("② 转角 90°", math.pi / 2),
                     ("③ 转角 180°", math.pi),
                     ("④ 转角 18°（★ 齿距角 360/20）", 2 * math.pi / 20)):
        ev["cases"].append(_one(sw, tag, rot))
    #: ★ ⑤ 偏移
    ev["cases"].append(_one(sw, "⑤ XOffset=5mm", 0.0, xoff=5.0))
    ev["rotation_ok"] = all(c.get("ok") for c in ev["cases"][:4])
    ev["offset_ok"] = bool(ev["cases"][4].get("ok"))
    #: ★★ 转角是否**真的转了**（★ 比 90° 那次的重心应明显不同）
    b0 = ev["cases"][0].get("bbox_mm") or {}
    b90 = ev["cases"][1].get("bbox_mm") or {}
    ev["rotation_moved_centroid"] = bool(
        b0 and b90 and (abs(b0.get("cx", 0) - b90.get("cx", 0)) > 0.5
                        or abs(b0.get("cy", 0) - b90.get("cy", 0)) > 0.5))
    p = R / "output" / "equation-rotation-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  ★★ 转角可用=%s · 偏移可用=%s · 转角真的动了=%s"
          % (ev["rotation_ok"], ev["offset_ok"], ev["rotation_moved_centroid"]))
    for c in ev["cases"]:
        print("  %-30s ok=%-6s 段 %s  bbox=%s" % (c.get("tag", "")[:30], c.get("ok"),
                                                  c.get("seg"), c.get("bbox_mm")))
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
