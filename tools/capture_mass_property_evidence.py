r"""@brief 真机证据：**读质量属性 1 个工具**（砌墙 W5 / Spec Kit `138` 的验收②）。

## ★★ 验证方式：**数字断言**（盒 40×20×10 mm ⇒ 已知答案）
```
新建零件 → batch21 建草图（矩形 40×20）→ batch22 拉伸 10mm
  ⇒ ★ 用本批的工具（走 `sw_mass_property.mass_properties`）回读，断言：
     · `volume`        == **8000**（mm³）      —— 容差 1e-6 相对
     · `surface_area`  == **2800**（mm²）      —— 2×(40·20 + 40·10 + 20·10)
     · `center_of_mass`== **[0, 0, −5]**（mm） —— 盒 z 从 −10 到 0
⇒ ★ 三个断言**都是已知几何推出的数**，不是从读数抄来的。
```

## 另外验的
```
· ★ **核声明解析得到**（工具层与能力层没断链）
· ★ **取法：当属性取就拿到对象** —— 证据里记录 `hasattr(mp,'Mass')` 为真
  （★ 与 `CustomPropertyManager` 相反，那是**必须当方法调**的那个 —— 事实 161）
· ⚠ **如实记录 `Mass` 与 `Density` 的原始值**，并**算出 `volume × density` 与 `mass` 的比**，
  让"量纲不成立"这件事**留在证据里**（★ 不猜单位）
· ⚠ **如实记录 `AccuracyLevel` 读不到**
· **负例**：在**非零件**（工程图）上调 ⇒ 必须**报错**（不是零件就没有质量属性）
```

## ⚠ 安全
**只在新零件上跑**、`CommandInProgress` 抑制弹窗、收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_mass_property_evidence.py
# 定位:   砌墙 W5（Spec Kit `138`）的**验收②**：产出 `output/mass-property-evidence.js
#           on`。
# 官方依据: `IModelDocExtension.CreateMassProperty` · `IMassProperty2` 的 Mass/Volume/Su
#           rfaceArea/
#          CenterOfMass/Density
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

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "mass-property-evidence.json"
)

EXPECT = {"volume": 8000.0, "surface_area": 2800.0, "center_of_mass": [0.0, 0.0, -5.0]}


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "mass_property_read",
        "steps": {},
    }
    sw = None
    docs: list = []
    ok = True
    try:
        import sw_connect
        from scripts import sw_part
        from scripts.sw_mass_property import mass_properties, mass_property_object
        import tool_specs_batch24 as b24

        #: ① 核声明解析得到
        bindings = {}
        for spec in b24.SPECS_BATCH24:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = callable(getattr(mod, spec.function, None))
        ev["steps"]["bindings"] = {"ok": all(bindings.values()), "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        part = sw_connect.new_document(sw, "part")
        docs.append(part)

        #: ② 造已知盒：40 × 20 × 10 mm
        sw_part.start_sketch(part, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(part, -20.0, -10.0, 20.0, 10.0)
        sk = sw_part.current_sketch_name(part)
        sw_part.end_sketch(part)
        sw_part.extrude_boss(part, sk, 10.0)

        #: ③ 取法：★ 当属性取就拿到对象？
        mp = mass_property_object(part)
        ev["steps"]["getter"] = {
            "ok": hasattr(mp, "Mass") and hasattr(mp, "Volume"),
            "has_Mass": hasattr(mp, "Mass"),
            "has_Volume": hasattr(mp, "Volume"),
            "★": "★ 记录『当属性取即可』——与 `CustomPropertyManager`（必须当方法调）**相反**",
        }

        #: ④ ★★ 数字断言
        got = mass_properties(part)

        def _close(a, b, tol=1e-6):
            try:
                return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(b)))
            except Exception:  # noqa: BLE001
                return False

        com_ok = (
            isinstance(got.get("center_of_mass"), list)
            and len(got["center_of_mass"]) == 3
            and all(
                _close(got["center_of_mass"][i], EXPECT["center_of_mass"][i], 1e-6)
                for i in range(3)
            )
        )
        ev["steps"]["numeric_assertions"] = {
            "ok": (
                _close(got.get("volume"), EXPECT["volume"])
                and _close(got.get("surface_area"), EXPECT["surface_area"])
                and com_ok
            ),
            "got": got,
            "expect": EXPECT,
            "check": {
                "volume": _close(got.get("volume"), EXPECT["volume"]),
                "surface_area": _close(got.get("surface_area"), EXPECT["surface_area"]),
                "center_of_mass": com_ok,
            },
        }
        ok = ok and ev["steps"]["numeric_assertions"]["ok"]

        #: ⑤ ⚠ 如实记录 `Mass` 的量纲疑点（★ 不猜单位）
        try:
            v = float(got.get("volume") or 0.0)
            d = float(got.get("density") or 0.0)
            m = float(got.get("mass") or 0.0)
            ev["steps"]["mass_unit_puzzle"] = {
                "volume": v,
                "density": d,
                "mass": m,
                "volume_times_density": v * d,
                "mass_over_that": (m / (v * d)) if (v and d) else None,
                "★": "★ 如实记录：mass 恰好等于 volume(mm³) × density ⇒ **量纲不成立** ⇒ "
                "mass 的物理单位**未确证**，★ 不猜、不给它安一个单位",
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["mass_unit_puzzle"] = {"note": "算不出: %s" % str(exc)[:60]}

        #: ⑥ ⚠ 如实记录 `AccuracyLevel` 读不到
        try:
            from scripts.sw_connect import get_com_member as _g

            _g(mp, "AccuracyLevel")
            ev["steps"]["accuracy_level"] = {
                "readable": True,
                "★": "★ 与探针那次不同了 —— 要更新说明",
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["accuracy_level"] = {
                "readable": False,
                "err": str(exc)[:70],
                "★": "★ 与探针一致：读不到 ⇒ 不暴露它",
            }

        #: ⑦ 负例：在**工程图**上调 ⇒ 必须报错
        drw = sw_connect.new_document(sw, "drawing")
        docs.append(drw)
        try:
            mass_properties(drw)
            ev["steps"]["negative_on_drawing"] = {
                "ok": False,
                "★": "★ **没有抛错** —— 在工程图上静默通过了",
            }
            ok = False
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["negative_on_drawing"] = {
                "ok": True,
                "raised": type(exc).__name__,
                "msg": str(exc)[:90],
            }
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        for d in docs:  #: ★ 关件不保存
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t and sw is not None:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 质量属性读数 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-24s %s" % (k, json.dumps(v, ensure_ascii=False)[:230]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
