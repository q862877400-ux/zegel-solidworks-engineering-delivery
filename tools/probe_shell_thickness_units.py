r"""@brief 探针：`IModelDoc2.InsertFeatureShell` 的 **`Thickness` 单位**（官方说**米**，模块说**毫米**）。

## ★★★ 要分辨的冲突（两边都有据）
```
★ **官方**：`C:\swapi\types\IModelDoc2\InsertFeatureShell.md`
    「**Thickness**: Shell thickness in **meters**」
★ **本模块头**（`scripts/sw_part.py`，轮 132 **实测校正**）：
    「长度单位：**毫米** … 实测：半径 25 的圆 ⇒ 边界框跨度 50（毫米）；拉伸 10 ⇒ 跨度 10（毫米）
      ⇒ **传进去的就是毫米，不要再换算**」
⇒ ★★ **两者冲突，不能猜** ⇒ ★ **本探针实测**：取**两个不同厚度**各建一次壳，
   量**体积下降**，看它随哪个口径变化。
```

## 判据（★ 事先规定 —— 事实 165 第 12 条）
```
★ 板 100×60×20 mm。抽壳去掉顶面（100×60）后，**理想壁厚 t** 的体积下降 ≈ 侧面 + 底面
  ⇒ ★ **口径是毫米**：`t=2.0` ⇒ 体积下降约为「2 mm 壁」的量级（几百—几千 mm³）
  ★ **口径是米**：`t=2.0` ⇒ **2 米的壁** ⇒ ★ **比零件大 100 倍** ⇒ **壳要么失败、要么把实体吃光**
⇒ ★★ **所以只要它成功且体积下降落在「毫米量级」，就说明口径是毫米**；
   而**两个厚度的下降之比**应 ≈ 厚度之比（★ 那是最硬的判据）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_shell_thickness_units.py
# 定位:   分辨 `InsertFeatureShell` 的 `Thickness` 口径；产物 `output/shell-thickness-
#           units.json`。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertFeatureShell.md`（写着 meters）
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
    Path(__file__).resolve().parents[1] / "output" / "shell-thickness-units.json"
)
T1, T2 = 2.0, 4.0  #: ★ 两个厚度（★ 比值为 2 ⇒ 体积下降之比应 ≈ 2）


def _volume_mm3(model) -> float | None:
    """取体积（★ 毫米³ —— 本项目零件按毫米；`MassProperty` 的面积体积口径见 known-facts）。"""
    try:
        from scripts.sw_connect import safe_get_com_member

        ext = safe_get_com_member(model, "Extension")
        mp = safe_get_com_member(ext, "CreateMassProperty")
        if mp is None:
            return None
        return float(safe_get_com_member(mp, "Volume") or 0.0)
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "unit_conflict": {"official": "meters", "module_header": "millimetres"},
        "steps": {},
    }
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts import sw_feature_readback as fr
        from scripts import sw_part as p_
        from scripts.sw_simulation import select_face_at

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        def _make_plate() -> float | None:
            """建 100×60×20 的板，回体积。"""
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            p_.start_sketch(doc, plane_name="Front Plane")
            p_.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
            sk = p_.current_sketch_name(doc)
            p_.end_sketch(doc)
            p_.extrude_boss(doc, sk, 20.0)
            return _volume_mm3(doc)

        v0 = _make_plate()
        ev["steps"]["plate"] = {"volume_mm3": v0, "features": fr.feature_names(doc)}
        print("  [0] 板体积 = %s" % v0)

        #: ★ 两个厚度各抽一次壳（★ 每次用一个**新板**，避免上一次的壳影响下一次）
        runs = {}
        for t in (T1, T2):
            x = sw_connect.new_document(sw, "part")
            try:
                sw_connect.safe_get_com_member(x, "ClearSelection2", True)
                p_.start_sketch(x, plane_name="Front Plane")
                p_.sketch_corner_rectangle(x, -50.0, -30.0, 50.0, 30.0)
                sk = p_.current_sketch_name(x)
                p_.end_sketch(x)
                p_.extrude_boss(x, sk, 20.0)
                vb = _volume_mm3(x)
                #: 选顶面（★ 官方 Remarks 要求先选要移除的面）
                sw_connect.safe_get_com_member(x, "ClearSelection2", True)
                select_face_at(x, 0.0, 0.0, 0.0)
                r = p_.shell_report(x, t)
                va = _volume_mm3(x)
                runs[str(t)] = {
                    "ok": bool(r.get("ok")),
                    "present": (r.get("readback") or {}).get("present"),
                    "volume_before": vb,
                    "volume_after": va,
                    "drop": (round(vb - va, 3) if (vb and va) else None),
                    "error": r.get("error"),
                }
                print(
                    "  [t=%.1f] ok=%s present=%s 体积 %s → %s（降 %s）"
                    % (
                        t,
                        r.get("ok"),
                        (r.get("readback") or {}).get("present"),
                        vb,
                        va,
                        runs[str(t)]["drop"],
                    )
                )
            finally:
                try:
                    ti = str(sw_connect.safe_get_com_member(x, "GetTitle") or "")
                    if ti:
                        sw.CloseDoc(ti)
                except Exception:  # noqa: BLE001
                    pass

        ev["steps"]["runs"] = runs
        d1 = runs.get(str(T1), {}).get("drop")
        d2 = runs.get(str(T2), {}).get("drop")
        ratio = (d2 / d1) if (d1 and d2) else None
        ev["steps"]["verdict"] = {
            "thicknesses": [T1, T2],
            "drops": [d1, d2],
            "drop_ratio": (round(ratio, 3) if ratio else None),
            "expected_ratio": T2 / T1,
            "★": (
                "★ 事先规定：若两次**都成功**且**下降之比 ≈ 厚度之比** ⇒ "
                "**口径与传入值一致**；★ 再结合「下降是否落在毫米量级」 ⇒ 判它是不是毫米。"
                "★ 若官方口径（米）成立，2.0 的壳会**把实体吃光或失败**。"
            ),
        }
        print("  ── 判读 ──")
        print("     %s" % json.dumps(ev["steps"]["verdict"], ensure_ascii=False)[:280])
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
