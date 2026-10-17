r"""@brief 探针：`ISketchManager.CreateChamfer` 的**可行参数组合** —— 回读线段数当判据。

## 背景（为什么值得再试）
仓库 docstring（轮 122）判它「**架构性限制**」—— 但那**只在 `type=2` 上验过**，
而且当时报的是 `com_error 0x80010105`；**轮 164 真机**换默认 `type=0` 时返回的是 **None**，
⚠ **表现不一样** ⇒ ★ 按「**一条的性质不能推广成整族**」的纪律，**值得逐类型试**。

★ 而且有一个**具体假设**：默认 `chamfer_type=0`（`distance_angle`）时
`angle_or_distance` 是**角度**，而仓库签名给的**默认值是 `0.0`** —— **0° 的倒角不合法**
⇒ 很可能**返回 None 就是因为角度是 0**。

## 判据（能被空操作证伪）
```
每次调用**前后各数一次草图线段数**（`ISketch.GetSketchSegments`）
  ⇒ 倒角成功 ⇒ 两条直线**变成**「两段 + 一个倒角段」⇒ 线段数**应当变**
  ⇒ 空操作时**不变**
```

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_chamfer_forms.py
# 定位:   给 Spec Kit `084` 判定 `create_sketch_chamfer` 是**架构性不可用**还是**参数没给对**。
# 官方依据: `SketchSegment CreateChamfer(Int32 Type, Double Distance, Double AngleORdist)`；
#          `swSketchChamferType_e` = DistanceAngle 0 / DistanceDistance 1 / DistanceEqual 2（**三源一致**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "chamfer-forms.json")
def main() -> int:
    ev: dict = {"trials": []}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_sketch, sw_sketch_edit
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: 每一轮都**重新造一对相接直线**（倒角会消耗掉它们）
        def fresh_pair():
            sw_part.start_sketch(doc)
            sw_part.sketch_line(doc, -0.02, 0.0, 0.0, 0.0)
            sw_part.sketch_line(doc, 0.0, 0.0, 0.0, 0.02)
            skm = sw_connect.safe_get_com_member(doc, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            segs = sw_sketch.get_sketch_segments(sk)
            segs = list(segs) if isinstance(segs, list) else []
            doc.ClearSelection2(True)
            n_sel = 0
            for s in segs[:2]:
                try:
                    if s.Select4(True, sw_part._empty_callout()):
                        n_sel += 1
                except Exception:      # noqa: BLE001
                    pass
            return sk, segs, n_sel

        def count(sk):
            try:
                v = sw_sketch.get_sketch_segments(sk)
                return len(v) if isinstance(v, list) else -1
            except Exception:      # noqa: BLE001
                return -1

        #: (标签, type, distance_mm, angle_or_distance)
        combos = [
            ("type0 默认(角度=0)  d=5", 0, 5.0, 0.0),
            ("type0 角度=45°      d=5", 0, 5.0, 45.0),
            ("type1 距离-距离 5/3", 1, 5.0, 3.0),
            ("type2 距离-相等  d=5", 2, 5.0, 0.0),
        ]
        for label, t, dist, ang in combos:
            sk, segs, n_sel = fresh_pair()
            before = count(sk)
            rec = {"label": label, "type": t, "distance_mm": dist, "angle_or_dist": ang,
                   "selected": n_sel, "segments_before": before}
            try:
                sw_sketch_edit.create_sketch_chamfer(
                    doc, chamfer_type=t, distance_mm=dist, angle_or_distance=ang)
                rec["raised"] = None
            except Exception as exc:      # noqa: BLE001
                rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:90])
                rec["tb"] = traceback.format_exc().strip().splitlines()[-3:]
            rec["segments_after"] = count(sk)
            rec["changed"] = rec["segments_after"] != rec["segments_before"]
            ev["trials"].append(rec)
            print("  %-26s 选中=%d 段数 %s → %s  ⇒ **%s**  %s"
                  % (label, n_sel, rec["segments_before"], rec["segments_after"],
                     "变了 ✚" if rec["changed"] else "没变",
                     (rec["raised"] or "")[:44]))
            if rec["changed"]:
                print("     ★★ **这个组合可行**")
            sw_part.end_sketch(doc)
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print("  收尾：扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
