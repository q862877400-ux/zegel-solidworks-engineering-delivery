r"""@brief 探针：**读质量属性** —— 怎么取 `IMassProperty2`、成员可达性、以及**单位**。

## 为什么要有这个探针（2026-10-01 轮 233，砌墙 W5 的前置）
本仓库**能改**质量属性覆盖值（`sw_export.set_mass_property_override`）却**读不出实际值**
⇒ 而"这个零件多重 / 体积多少 / 重心在哪"是**最常被问的问题之一**（见事实 166）。

## 三个未知（都要真机答）
```
① **怎么取？** 候选：
     a) `model.Extension.CreateMassProperty`       ← 官方入口（`IModelDocExtension`）
     b) `model.Extension.CreateMassProperty2`      ← ⚠ 可能有后继
     c) `model.GetMassProperties`                  ← ★ 后备：官方返回 **12 个 double 的数组**
   ⚠⚠ **照 W3 的教训（事实 161）**：`Extension.CustomPropertyManager` **当属性取会拿到一个
     **method 对象**、必须**当方法调用** ⇒ ★ 这里**两种取法都要试**，
     而且**判据要用"行为"**（它有没有 `Mass`/`Volume`），**不用类型**（事实 161 的假阳性就是这么来的）。
② **成员可达性**：`Mass` / `Volume` / `SurfaceArea` / `CenterOfMass` / `Density` / `AccuracyLevel`
     —— `IMassProperty2` 的这 11 个成员在 swapi 里**全是 `kind: property`**（★ 无 out 参数）
     ⇒ 预期好读；**但实测才算**。
③ ★★ **单位！** 这是本探针**最要紧的一问**：
     · 官方质量属性惯用 **SI（米 / 千克）**；
     · ★★ **更正（2026-10-05，标定实测）**：本行原先写「`IBody2.GetBodyBox` 实测是**毫米**」——
       ★ **那句是错的**，且属于「把没量过的口径写成实测」那一类（本仓吃过它的亏）✓✗
       · 真机标定（**40 × 40 × 10 mm** 盒）：`GetBodyBox` 原始值 **`[0.04, 0.04, 0.01]`** ⇒ **米**，
         与质量属性体积 `1.6e-5`（= 16000 mm³）**交叉一致**；证据 `output/bbox-unit-levels-evidence.json`
       · ★★ 更关键：它有**混口径**记录 —— `scripts/sw_feature_readback.py` 记着另一次读回
         `[-0.05, -0.03, -20.0, 0.05, 0.03, 0.0]`（X/Y 像米、Z 像毫米）
         ⇒ ★ **同一个成员的六个分量里混了两套口径 ⇒ 它不可当单位锚点** ✓
     ⇒ ★ 该探针的**老判据「拿它当锚点」不成立**；★ 单位一律以**独立可交叉验证的量**为准
       （体积 mm³ 与 `GetPartBox` 各自算一遍、互相印证），**不要**再拿 `GetBodyBox` 当尺子 ✓
     ⇒ ★ 本探针要问的问题**仍然成立**：建一个**已知体积**的盒（**40 × 20 × 10 mm = 8000 mm³**）去问真机：
        读回来的 `Volume` 是 **8000**（毫米³）还是 **8e-6**（米³）？**只能实测** ✓
        （★ 已定案的旁证：质量属性**体积**实测是 **m³** —— 40×40×10 盒回 `1.6e-5`）
```

## ⚠ 安全
**只在新零件上跑**、`CommandInProgress` 抑制弹窗、收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/probe_mass_property_reads.py
# 定位:   给砌墙 W5 定包装层与单位；产出 `output/mass-property-reads.json`。
# 官方依据: `IModelDocExtension.CreateMassProperty` · `IMassProperty` / `IMassProperty2`
#          （`Mass`/`Volume`/`SurfaceArea`/`CenterOfMass`/`Density`/`AccuracyLevel`）· `IModelDoc2.GetMassProperties`
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mass-property-reads.json")

#: ★ 已知体积：40 × 20 × 10 mm = **8000 mm³** = 8e-6 m³
BOX = {"x1": -20.0, "y1": -10.0, "x2": 20.0, "y2": 10.0, "depth": 10.0}
EXPECT_VOLUME_MM3 = 8000.0
EXPECT_AREA_MM2 = 2 * (40 * 20 + 40 * 10 + 20 * 10)      #: = 2800 mm²
EXPECT_AREA_M2 = EXPECT_AREA_MM2 / 1e6


def _is_mass_prop(obj) -> bool:
    """★ **行为判据**（照事实 161）：它得像一个质量属性对象才有意义。

    ⚠ 不用 `isinstance(..., (str,int,float))` 那种类型判据 —— 它**判不出 method 对象**，
    而那正是事实 161 里假阳性的来源。
    """
    return obj is not None and (hasattr(obj, "Mass") or hasattr(obj, "Volume"))


def _try(fn, *a, **kw):
    try:
        return True, fn(*a, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:80])


def probe_getters(model, sc) -> dict:
    """① 三条取法各试一次（★ 属性形态与**调用**形态都试）。"""
    out: dict = {}
    ext = sc.safe_get_com_member(model, "Extension")
    out["model.Extension"] = "拿到" if ext is not None else None
    if ext is not None:
        for name in ("CreateMassProperty", "CreateMassProperty2"):
            ok, v = _try(lambda n=name: sc.safe_get_com_member(ext, n))
            out["A_%s（当属性取）" % name] = (
                "★ 是质量属性对象" if (ok and _is_mass_prop(v))
                else ("拿到的是 %s" % type(v).__name__ if ok else str(v)[:60]))
            if ok and callable(v) and not _is_mass_prop(v):
                ok2, v2 = _try(lambda f=v: f())
                out["B_%s()（把它当方法调用）" % name] = (
                    "★ 是质量属性对象" if (ok2 and _is_mass_prop(v2))
                    else ("拿到的是 %s" % type(v2).__name__ if ok2 else str(v2)[:60]))
    #: 后备：`IModelDoc2.GetMassProperties`（官方返回 12 个 double）
    ok, arr = _try(lambda: sc.safe_get_com_member(model, "GetMassProperties"))
    if ok:
        try:
            vals = [float(x) for x in arr]
            out["C_model.GetMassProperties（12 double 后备）"] = {
                "len": len(vals), "values": [round(v, 12) for v in vals[:12]]}
        except TypeError:
            out["C_model.GetMassProperties（12 double 后备）"] = {"raw": str(arr)[:120]}
    else:
        out["C_model.GetMassProperties（12 double 后备）"] = arr
    return out


def probe_members(mp, sc) -> dict:
    """② 成员可达性 + ★ 单位（把读数与已知的 8000 mm³ 对比）。"""
    out: dict = {}
    for m in ("Mass", "Volume", "SurfaceArea", "Density", "AccuracyLevel"):
        ok, v = _try(lambda n=m: sc.safe_get_com_member(mp, n))
        out[m] = v if ok else v
    ok, com = _try(lambda: sc.safe_get_com_member(mp, "CenterOfMass"))
    if ok:
        try:
            out["CenterOfMass"] = [round(float(x), 12) for x in com]
        except TypeError:
            out["CenterOfMass"] = {"raw": str(com)[:120]}
    else:
        out["CenterOfMass"] = com
    return out


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: 造一个**已知体积**的盒：40 × 20 × 10 mm
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, BOX["x1"], BOX["y1"], BOX["x2"], BOX["y2"])
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, BOX["depth"])
        ev["steps"]["box"] = {"built": True, "expect_volume_mm3": EXPECT_VOLUME_MM3,
                              "expect_surface_area_mm2": EXPECT_AREA_MM2}

        ev["steps"]["getters"] = probe_getters(doc, sw_connect)

        #: 取一个可用的 mass property 对象用于读成员
        mp = None
        ext = sw_connect.safe_get_com_member(doc, "Extension")
        if ext is not None:
            for name in ("CreateMassProperty", "CreateMassProperty2"):
                cand = sw_connect.safe_get_com_member(ext, name)
                if _is_mass_prop(cand):
                    mp = cand
                    break
                if callable(cand):
                    try:
                        c2 = cand()
                        if _is_mass_prop(c2):
                            mp = c2
                            break
                    except Exception:                          # noqa: BLE001
                        pass
        ev["steps"]["mp_obtained"] = mp is not None
        if mp is not None:
            reads = probe_members(mp, sw_connect)
            ev["steps"]["members"] = reads
            #: ★★ 单位判定（本探针最要紧的一问）
            vol = reads.get("Volume")
            area = reads.get("SurfaceArea")
            def _close(a, b, tol=1e-6):
                try:
                    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
                except Exception:                              # noqa: BLE001
                    return False
            ev["steps"]["unit_verdict"] = {
                "volume_raw": vol, "surface_area_raw": area,
                "volume_matches_mm3": _close(vol, EXPECT_VOLUME_MM3, 1e-6),
                "volume_matches_m3": _close(vol, EXPECT_VOLUME_MM3 / 1e9, 1e-6),
                "area_matches_mm2": _close(area, EXPECT_AREA_MM2, 1e-6),
                "area_matches_m2": _close(area, EXPECT_AREA_M2, 1e-6),
                "★": "盒 40×20×10 mm ⇒ 体积 8000 mm³ = 8e-6 m³；★ 看哪个命中 ⇒ 这就是单位",
            }
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
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

    print("  ── 质量属性探针 ──")
    for k, v in ev["steps"].items():
        print("  ══ %s ══" % k)
        print("     %s" % json.dumps(v, ensure_ascii=False)[:400])
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
