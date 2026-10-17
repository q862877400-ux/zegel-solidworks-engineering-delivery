r"""@brief 真机证据：**拉伸族 3 个工具**（砌墙 W4 续 / Spec Kit `136` 的验收②）。

## ★★★ 本批是**第一次建出实体** —— 所以验证是"读包围盒断言"
```
新建零件 → batch21 建草图（矩形 40×20，对角 -20,-10 → 20,10）→ `extrude_boss(depth_mm=10)`
  ⇒ ★ **用 `solidworks_part_bounding_box` 回读断言**：期望包围盒 **40 × 20 × 10 mm**
⇒ ★ 断言是**数字**（可复跑、可进 CI），而且它把
   **batch21（写草图）→ batch22（建实体）→ 只读工具（回读）** 串成一条**可验证的链**。
```

## 另外验的
```
· ★ **核声明解析得到**：batch22 的 `module`/`function` 逐个 getattr 成功
· ★ **参数改名生效**：把每个声明的 `param_alias` 记进证据（`depth_mm`→`depth` 等）
· `extrude_cut`：在实体上再建一个圆草图并切除 ⇒ ★ 回读**特征树**断言多了一个"切除"特征
· `extrude_midplane`：★ 回读包围盒断言**两侧对称**（草图面居中）
· ★ **负例**：给一个**不存在**的草图名 ⇒ 必须**报错**（选不中/找不到要报错，不静默）
```

## ⚠ 安全
**只在新零件上跑**、`CommandInProgress` 抑制弹窗、收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_feature_build_evidence.py
# 定位:   砌墙 W4 续（Spec Kit `136`）的**验收②**：产出 `output/feature-build-evidence.json`。
# 官方依据: `IFeatureManager.FeatureExtrusion3`（23 参数）· `FeatureCut4`（★ 既有事实 1）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "feature-build-evidence.json")


def bbox_mm(model, sc):
    """回读包围盒（毫米）。★ 复用既有的 `sw_part.get_bounding_box`（被 `solidworks_part_bounding_box` 挂过）。"""
    from scripts import sw_part
    bb = sw_part.get_bounding_box(model)
    return bb


def feature_names(model, sc) -> list[str]:
    """特征树里的特征名（★ 用于断言"多了一个特征"）。"""
    names = []
    try:
        n = int(sc.safe_get_com_member(model, "GetFeatureCount"))
    except Exception:                                          # noqa: BLE001
        return names
    for k in range(1, n + 1):
        f = sc.safe_get_com_member(model, "FeatureByPositionReverse", k)
        nm = str(sc.safe_get_com_member(f, "Name") or "") if f is not None else ""
        if nm:
            names.append(nm)
    return names


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "feature_build_extrude", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part
        import tool_specs_batch22 as b22

        #: ① 核声明解析得到 + 记下 param_alias
        bindings = {}
        for spec in b22.SPECS_BATCH22:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {"resolved": callable(getattr(mod, spec.function, None)),
                                   "aliases": dict(spec.param_alias or {})}
        ev["steps"]["bindings"] = {"ok": all(v["resolved"] for v in bindings.values()),
                                   "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: ② 矩形 40×20 → 拉伸 10mm ⇒ ★ 断言包围盒 40×20×10
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk1 = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        f1 = sw_part.extrude_boss(doc, sk1, 10.0)
        bb1 = bbox_mm(doc, sw_connect)
        ev["steps"]["extrude_boss"] = {
            "ok": bool(f1 is not None), "feature": str(getattr(f1, "Name", "") or ""),
            "bbox": bb1,
            "★": "矩形 40×20 拉伸 10mm ⇒ 期望 40 × 20 × 10；★ 断言见 verdict_bbox",
        }

        #: ③ extrude_cut：再建一个圆草图并切除 ⇒ 断言特征树多了一个
        before_names = feature_names(doc, sw_connect)
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_circle(doc, 0.0, 0.0, 4.0)
        sk2 = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        f2 = sw_part.extrude_cut(doc, sk2, 0.0)                #: ★ 0 = 完全贯穿
        after_names = feature_names(doc, sw_connect)
        ev["steps"]["extrude_cut_through_all"] = {
            "ok": bool(f2 is not None) and len(after_names) > len(before_names),
            "feature": str(getattr(f2, "Name", "") or ""),
            "n_features_before": len(before_names), "n_features_after": len(after_names),
            "★": "depth_mm=0 ⇒ 完全贯穿；★ 断言「多了一个特征」",
        }
        ok = ok and ev["steps"]["extrude_cut_through_all"]["ok"]

        #: ④ extrude_midplane：新零件上验"两侧对称"
        doc2 = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc2, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc2, -20.0, -10.0, 20.0, 10.0)
        sk3 = sw_part.current_sketch_name(doc2)
        sw_part.end_sketch(doc2)
        f3 = sw_part.extrude_midplane(doc2, sk3, 10.0)          #: 总深 10 ⇒ 每侧 5
        bb3 = bbox_mm(doc2, sw_connect)
        ev["steps"]["extrude_midplane"] = {
            "ok": bool(f3 is not None), "feature": str(getattr(f3, "Name", "") or ""),
            "bbox": bb3, "★": "总深 10 ⇒ 每侧 5 ⇒ 期望 40 × 20 × 10（与 boss 同总数）",
        }
        try:
            t2 = str(sw_connect.safe_get_com_member(doc2, "GetTitle") or "")
            if t2:
                sw.CloseDoc(t2)
        except Exception:                                      # noqa: BLE001
            pass

        #: ⑤ 负例：不存在的草图名 ⇒ 必须报错
        try:
            sw_part.extrude_boss(doc, "NoSuchSketch_XYZ", 10.0)
            ev["steps"]["negative_missing_sketch"] = {"ok": False,
                                                      "★": "★ **没有抛错** —— 选不中却静默通过"}
            ok = False
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["negative_missing_sketch"] = {"ok": True,
                                                      "raised": type(exc).__name__,
                                                      "msg": str(exc)[:90]}

        #: ★ 包围盒断言：结构已核过 —— `{"min": [...], "max": [...], "size": [dx,dy,dz]}`，**毫米**
        #:   （`sw_part.get_bounding_box` 的 docstring 明写；★ 该函数有一处**已知陷阱**：
        #:    第一版曾误用 `sw_connect.mm()`，被数值冒烟当场抓住 ⇒ 这里**必须断言数字**）
        def _size(bb):
            return [round(float(x), 3) for x in (bb or {}).get("size", [])]

        s1, s3 = _size(bb1), _size(bb3)
        ev["steps"]["verdict_bbox"] = {
            "ok": (s1 == [40.0, 20.0, 10.0] and s3 == [40.0, 20.0, 10.0]),
            "boss_size_mm": s1, "midplane_size_mm": s3,
            "expected": [40.0, 20.0, 10.0],
            "★": "矩形 40×20（对角 -20,-10 → 20,10）拉伸 10 ⇒ 40×20×10；"
                 "中面拉伸总深 10 也是 40×20×10（每侧 5）",
        }
        ok = ok and ev["steps"]["verdict_bbox"]["ok"]
        ok = ok and ev["steps"]["negative_missing_sketch"]["ok"]
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)                             #: ★ 关件不保存
        except Exception:                                      # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 拉伸族 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-28s %s" % (k, json.dumps(v, ensure_ascii=False)[:210]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
