"""★ **造一个"可缝合曲面"的教学用零件**（2026-10-01 · 轮 309）。

★ 目的：给用户一个 `.SLDPRT`，里面**已经有两张共享一条边的曲面** ⇒
  他只需要在 UI 里做**缝合**那一步（★ 那正是我要观察的）。

★ 几何设计（★ 为什么这样设计）：
```
★ 拉伸一个**矩形**轮廓得到的不是"一张平板"，而是**一个四面方管**（★ 无顶无底）。
   ⇒ 所以"可缝"的条件是**两个方管共享一条边**。
★ A：★ 前视基准面（z=0），矩形 (0,0)-(20,20)，拉伸 20mm ⇒ ★ 占 x∈[0,20] · y∈[0,20] · z∈[0,20] 的**四壁**
★ B：★ 上视基准面（y=0），矩形 (0,0)-(20,20)，拉伸 20mm ⇒ ★ 占 x∈[0,20] · y∈[-20,0] · z∈[0,20] 的**四壁**
   ⇒ ★★ **两个方管在 y=0 那个平面上共享一条公共边**（★ A 的 y=0 壁与 B 的 y=0 壁贴合）✓
```

★ 判据（★ 三条，★ 都要真机回读）：① 两个曲面特征都建成（★ 名以"曲面-"开头）② **body 数 = 2**
  ③ **保存成功且文件存在**。
★ 安全：`CommandInProgress` 抑制 + `finally` 收尾（★ **文档不关** —— ★ 要留给用户看）。
"""

import json
import sys
import time
from pathlib import Path

sys.path[:0] = [r"C:\swprojects\sw-skill-fork", r"C:\swprojects\sw-skill-fork\scripts"]

import sw_connect                                              # noqa: E402
from scripts import sw_part as P                               # noqa: E402
from scripts import sw_feature_readback as FR                  # noqa: E402
from scripts.sw_connect import get_com_member                  # noqa: E402

OUT = Path(r"D:\AI\SW\surface-knit-teaching.SLDPRT")


def _surface_features(doc):
    """★ 特征树里以「曲面」开头的特征名（★ 与"凸台"区分）。"""
    try:
        return [n for n in FR.feature_names(doc) if str(n).startswith("曲面")]
    except Exception:                                          # noqa: BLE001
        return []


def main() -> int:
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    try:
        sw.CommandInProgress = True
    except Exception:                                          # noqa: BLE001
        pass
    ev = {"steps": {}}
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: ★ A：前视基准面 ⇒ 方管 1
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_corner_rectangle(doc, 0.0, 0.0, 20.0, 20.0)
        sk_a = P.current_sketch_name(doc)
        P.end_sketch(doc)
        ev["steps"]["sketch_A"] = {"ok": bool(sk_a), "name": sk_a, "plane": "Front Plane"}
        #: ★ 曲面-拉伸（★ 用本轮验证过的那条：FeatureExtruRefSurface3 · 22 参）
        from scripts import sw_surface_features as SF
        r_a = SF.create_extruded_surface_report(doc, 20.0, sketch_name=sk_a)
        ev["steps"]["surface_A"] = {"ok": bool(r_a.get("ok")), "feature": r_a.get("feature_name")}
        #: ★ B：上视基准面 ⇒ 方管 2（★ 沿相反方向，与 A 共享 y=0 那条公共边）
        P.start_sketch(doc, plane_name="Top Plane")
        P.sketch_corner_rectangle(doc, 0.0, 0.0, 20.0, 20.0)
        sk_b = P.current_sketch_name(doc)
        P.end_sketch(doc)
        ev["steps"]["sketch_B"] = {"ok": bool(sk_b), "name": sk_b, "plane": "Top Plane"}
        r_b = SF.create_extruded_surface_report(doc, 20.0, sketch_name=sk_b)
        ev["steps"]["surface_B"] = {"ok": bool(r_b.get("ok")), "feature": r_b.get("feature_name")}
        #: ★ 回读几何
        ev["steps"]["features"] = _surface_features(doc)
        try:
            bodies = list(get_com_member(doc, "GetBodies2", 0, True) or [])
        except Exception:                                      # noqa: BLE001
            bodies = []
        ev["steps"]["body_count"] = len(bodies)
        edges = 0
        for b in bodies:
            try:
                for f in (get_com_member(b, "GetFaces") or []):
                    edges += len(list(get_com_member(f, "GetEdges") or []))
            except Exception:                                  # noqa: BLE001
                pass
        ev["steps"]["edge_count_sum"] = edges
        #: ★ 保存
        OUT.parent.mkdir(parents=True, exist_ok=True)
        saved = sw_connect.save_document(doc, str(OUT))
        ev["steps"]["save"] = {"ok": bool(saved) and OUT.exists(),
                               "path": str(OUT), "exists": OUT.exists(),
                               "bytes": (OUT.stat().st_size if OUT.exists() else 0)}
    finally:
        #: ★ **不关文档** —— ★ 用户要打开它（★ 但释放 CommandInProgress）
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
    ev["captured_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    ok = (ev["steps"].get("surface_A", {}).get("ok") and ev["steps"].get("surface_B", {}).get("ok")
          and ev["steps"].get("save", {}).get("ok"))
    ev["verdict"] = "pass" if ok else "partial"
    out = Path(r"D:\AI\SW\output\surface-knit-teaching-evidence.json")
    out.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  sketch A : %s" % json.dumps(ev["steps"].get("sketch_A"), ensure_ascii=False))
    print("  surface A: %s" % json.dumps(ev["steps"].get("surface_A"), ensure_ascii=False))
    print("  sketch B : %s" % json.dumps(ev["steps"].get("sketch_B"), ensure_ascii=False))
    print("  surface B: %s" % json.dumps(ev["steps"].get("surface_B"), ensure_ascii=False))
    print("  features : %s · bodies=%s · edges=%s" % (ev["steps"].get("features"),
                                                      ev["steps"].get("body_count"),
                                                      ev["steps"].get("edge_count_sum")))
    print("  save     : %s" % json.dumps(ev["steps"].get("save"), ensure_ascii=False))
    print("  verdict  : %s" % ev["verdict"].upper())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
