r"""@brief 探针：`InsertCompositeCurve` 到底要选**实体（草图段）**还是**草图特征**？

## 为什么（轮 184）
轮 183 修好样条后，`verify_composite_curve_smoke` 里**样条能建了**，但
`InsertCompositeCurve` **仍返回 False**。
★ 官方 Remarks 的原文是：
```
"To use this method, select the **entities** by calling IModelDocExtension::SelectByID2
 with a mark number of 1."
⇒ ★★ **"entities"（实体）** —— 而那个 smoke 选的是**草图特征**（feature）。
```
⇒ 本探针**对照两种选法**（同一批对象、同一 mark）：**实体 vs 特征**。

## 判据（能被空操作证伪）
```
★ **看 `InsertCompositeCurve` 的返回值 / 是否抛错**，并**回读 `GetFeatureCount`**
  （建成复合曲线会**多一个特征** ⇒ 条数变化；空操作不变）
逐组试（**每次新零件**，避状态污染）：
  ① 选**草图段实体**（每个草图的 `GetSketchSegments` 元素）· mark=1
  ② 选**草图特征**（`FeatureByName`，即现状）· mark=1
  ③ 对照：都不选
```

## ⚠ 安全
只在新零件上；`CommandInProgress` 复位；收尾**轮询 + 查到就点掉**；关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_composite_curve_selection.py
# 定位:   给 Spec Kit `104` 判定「选实体 vs 选特征」是不是 `InsertCompositeCurve` 的成
#           败关键。
# 官方依据: `C:/swapi/types/IModelDoc2/InsertCompositeCurve.md`（Remarks：**select the e
#           ntities**，
#          mark = 1）· 官方样例（两条**样条**草图）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import sketch_relations  # noqa: E402

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "composite-curve-selection.json")


def main() -> int:
    ev: dict = {"trials": []}
    sw = None
    try:
        import sw_connect
        from scripts import sw_part
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        def build_two_spline_sketches():
            """造**两条样条草图**（官方前提）并返回 (doc, [草图特征名])。"""
            doc = sw_connect.new_document(sw, "part")
            for i in range(2):
                sw_part.start_sketch(doc)
                y = float(i) * 30.0
                skm = sw_connect.safe_get_com_member(doc, "SketchManager")
                sketch_relations.create_spline(skm, [
                    (-20.0, y, 0.0), (-7.0, y + 6.0, 0.0), (7.0, y - 6.0, 0.0), (20.0, y, 0.0)])
                sw_part.end_sketch(doc)
            return doc

        def fcount(doc):
            try:
                return int(sw_connect.safe_get_com_member(doc, "GetFeatureCount"))
            except Exception:      # noqa: BLE001
                return -1

        def sketch_segments(doc):
            """取所有草图里的**段实体**（这就是官方说的 entities 候选）。"""
            out = []
            try:
                fm = sw_connect.safe_get_com_member(doc, "FeatureManager")
                f = sw_connect.safe_get_com_member(fm, "GetFirstFeature")
                while f is not None:
                    tn = str(sw_connect.safe_get_com_member(f, "GetTypeName2") or "")
                    if tn == "ProfileFeature":      #: 草图
                        sk = sw_connect.safe_get_com_member(f, "GetSpecificFeature2")
                        segs = sw_connect.safe_get_com_member(sk, "GetSketchSegments")
                        if segs:
                            out.extend(list(segs))
                    f = sw_connect.safe_get_com_member(f, "GetNextFeature")
            except Exception as exc:      # noqa: BLE001
                ev.setdefault("seg_error", str(exc)[:70])
            return out

        #: ① 选**草图段实体**
        doc = build_two_spline_sketches()
        n0 = fcount(doc)
        segs = sketch_segments(doc)
        n_sel = 0
        for s in segs:
            try:
                if s.Select4(True, sw_part._empty_callout()):
                    n_sel += 1
            except Exception:      # noqa: BLE001
                pass
        rec = {"form": "① 选**草图段实体**", "segments": len(segs), "selected": n_sel}
        try:
            r = sw_connect.call_com_member(doc, "InsertCompositeCurve")
            rec["ret"] = repr(r)
        except Exception as exc:      # noqa: BLE001
            rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        rec["features"] = "%s → %s" % (n0, fcount(doc))
        rec["changed"] = fcount(doc) > n0
        print("  ① 选**草图段实体**（%d 段 / 选中 %d）⇒ 特征 %s · 返回 %s"
              % (len(segs), n_sel, rec["features"], rec.get("ret", rec.get("raised", ""))[:30]))
        ev["trials"].append(rec)
        try:
            sw.CloseDoc(str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""))
        except Exception:      # noqa: BLE001
            pass

        #: ② 选**草图特征**（现状）
        doc = build_two_spline_sketches()
        n0 = fcount(doc)
        n_sel = 0
        for nm in ("草图1", "草图2"):
            try:
                if sw_connect.call_com_member(doc, "SelectByID2", nm, "SKETCH", 0, 0, 0,
                                              False, 1, None, 0):
                    n_sel += 1
            except Exception:      # noqa: BLE001
                pass
        rec = {"form": "② 选**草图特征**", "selected": n_sel}
        try:
            r = sw_connect.call_com_member(doc, "InsertCompositeCurve")
            rec["ret"] = repr(r)
        except Exception as exc:      # noqa: BLE001
            rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        rec["features"] = "%s → %s" % (n0, fcount(doc))
        rec["changed"] = fcount(doc) > n0
        print("  ② 选**草图特征**（选中 %d）⇒ 特征 %s · 返回 %s"
              % (n_sel, rec["features"], rec.get("ret", rec.get("raised", ""))[:30]))
        ev["trials"].append(rec)
        try:
            sw.CloseDoc(str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""))
        except Exception:      # noqa: BLE001
            pass

        #: ③ 对照：都不选
        doc = build_two_spline_sketches()
        n0 = fcount(doc)
        try:
            sw_connect.call_com_member(doc, "ClearSelection2", True)
        except Exception:      # noqa: BLE001
            pass
        rec = {"form": "③ 都不选（对照）"}
        try:
            r = sw_connect.call_com_member(doc, "InsertCompositeCurve")
            rec["ret"] = repr(r)
        except Exception as exc:      # noqa: BLE001
            rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
        rec["changed"] = fcount(doc) > n0
        print("  ③ 都不选（对照）⇒ 返回 %s · 特征变了：%s"
              % (rec.get("ret", rec.get("raised", ""))[:30], rec["changed"]))
        ev["trials"].append(rec)
        try:
            sw.CloseDoc(str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""))
        except Exception:      # noqa: BLE001
            pass
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    found, dismissed, scanned = _sc.settle_residual_dialogs(settle_seconds=1.0)
    print("  收尾：发现 %d · 点掉 %d · 扫了 %d 个窗口" % (found, dismissed, scanned))
    ev["cleanup"] = {"found": found, "scanned": scanned}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
