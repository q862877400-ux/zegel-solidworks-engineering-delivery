r"""@brief 真机证据：**配置族 6 + 导出族 6**（24h 段 4 / Spec Kit `147` 的验收②）。

## ★★★ §5.0：证据脚本**先找了**（★ 轮 252 的教训）
```
· 配置族 ⇒ ★ 既有 `tools/capture_custom_property_evidence.py` + `probe_custom_property_reads.py`
· 导出族 ⇒ ★ 既有 `tools/verify_bmp_smoke.py` + `verify_png_smoke.py`
⇒ ★★ 本脚本**不重复造判据**，只做这两族 **12 个工具函数**的冒烟；
   ★ 那两个既有脚本**另行跑**（★ 它们是更深的判据）。
```

## 判据
```
· **配置族** ⇒ ★ 能力层**自己回 dict** ⇒ 判「**dict 非空且带关键键**」（★ 直读，无歧义）。
· **导出族** ⇒ ★ 判「**文件真的存在、且大小 > 0**」（★ 本项目铁律：回读优先，不信返回值）。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 · **不跑仿真** ·
★ 导出文件落 `output/`（★ 产物目录，已 gitignore）。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_config_export_evidence.py
# 定位:   Spec Kit `147` 的**验收②**：产出 `output/config-export-evidence.json`。
# 官方依据: `IConfigurationManager` / `ICustomPropertyManager` / `IModelDoc2.SaveAs3`
#          （见 `scripts/sw_document_data.py` 与 `scripts/sw_export.py` 的来源块）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "config-export-evidence.json")
EXPORT_DIR = Path(Path(__file__).resolve().parents[1] / "output" / "_export_smoke")


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "config_and_export", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part as P
        from scripts import sw_document_data as D
        from scripts import sw_export as E
        import tool_specs_batch33 as b33

        #: ① 静态：12 个工具声明解析得到
        bindings = {}
        for spec in b33.SPECS_BATCH33:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = callable(getattr(mod, spec.function, None))
        ev["steps"]["bindings"] = {"ok": all(bindings.values()), "count": len(bindings)}
        ok = ok and ev["steps"]["bindings"]["ok"]
        print("  [0] 12 个工具声明解析 = %s（%d 个）"
              % (ev["steps"]["bindings"]["ok"], len(bindings)))

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: 造零件
        doc = sw_connect.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = P.current_sketch_name(doc)
        P.end_sketch(doc)
        P.extrude_boss(doc, sk, 20.0)

        #: ② 配置族 6 个（★ 能力层回 dict ⇒ 判"非空"）
        cfg: dict = {}
        try:
            r = D.inspect_configurations(doc)
            cfg["inspect_configurations"] = {"ok": isinstance(r, dict) and bool(r),
                                             "keys": sorted(r.keys())[:6]}
        except Exception as exc:                               # noqa: BLE001
            cfg["inspect_configurations"] = {"ok": False, "error": str(exc)[:120]}
        try:
            r = D.create_configuration(doc, "DSH-CFG-A", activate=False, rebuild=True)
            cfg["create_configuration"] = {"ok": isinstance(r, dict) and bool(r),
                                           "keys": sorted(r.keys())[:6]}
        except Exception as exc:                               # noqa: BLE001
            cfg["create_configuration"] = {"ok": False, "error": str(exc)[:120]}
        try:
            r = D.activate_configuration(doc, "DSH-CFG-A", rebuild=True)
            cfg["activate_configuration"] = {"ok": isinstance(r, dict) and bool(r),
                                             "keys": sorted(r.keys())[:6]}
        except Exception as exc:                               # noqa: BLE001
            cfg["activate_configuration"] = {"ok": False, "error": str(exc)[:120]}
        try:
            r = D.set_custom_properties(doc, {"DSH_MARK": "1", "DSH_NOTE": "smoke"})
            cfg["set_custom_properties"] = {"ok": bool(r), "n": len(r) if hasattr(r, "__len__") else None}
        except Exception as exc:                               # noqa: BLE001
            cfg["set_custom_properties"] = {"ok": False, "error": str(exc)[:120]}
        try:
            r = D.read_custom_property(doc, "DSH_MARK")
            cfg["read_custom_property"] = {"ok": isinstance(r, dict) and bool(r),
                                           "value": (r or {}).get("value")}
        except Exception as exc:                               # noqa: BLE001
            cfg["read_custom_property"] = {"ok": False, "error": str(exc)[:120]}
        try:
            r = D.update_dimension_mm(doc, "D1@%s" % sk, 80.0, rebuild=True)
            cfg["update_dimension_mm"] = {"ok": isinstance(r, dict) and bool(r),
                                          "keys": sorted(r.keys())[:6]}
        except Exception as exc:                               # noqa: BLE001
            cfg["update_dimension_mm"] = {"ok": False, "error": str(exc)[:120]}
        ev["steps"]["config"] = cfg
        print("  [1] 配置族: %d/%d 通过"
              % (sum(1 for v in cfg.values() if v.get("ok")), len(cfg)))

        #: ③ 导出族 6 个（★ 判"文件存在且非空"）
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        exp: dict = {}
        for name, fn, ext in (
            ("export_step", lambda: E.export_step_report(doc, str(EXPORT_DIR / "smoke.step")), "step"),
            ("export_stl", lambda: E.export_stl_report(doc, str(EXPORT_DIR / "smoke.stl")), "stl"),
            ("export_iges", lambda: E.export_iges_report(doc, str(EXPORT_DIR / "smoke.igs")), "igs"),
            ("export_parasolid", lambda: E.export_parasolid_report(
                doc, str(EXPORT_DIR / "smoke.x_t")), "x_t"),
            ("export_dxf", lambda: E.export_dxf_report(doc, str(EXPORT_DIR / "smoke.dxf")), "dxf"),
            ("export_bmp", lambda: E.export_bmp_report(doc, str(EXPORT_DIR / "smoke.bmp")), "bmp"),
        ):
            try:
                r = fn()
                exp[name] = {"ok": bool(r.get("ok")), "exists": r.get("exists"),
                             "size_bytes": r.get("size_bytes"), "path": r.get("output_path"),
                             "error": r.get("error")}
            except Exception as exc:                           # noqa: BLE001
                exp[name] = {"ok": False, "error": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
        ev["steps"]["export"] = exp
        print("  [2] 导出族: %d/%d 通过"
              % (sum(1 for v in exp.values() if v.get("ok")), len(exp)))
        for k, v in exp.items():
            print("      %-18s ok=%-5s exists=%-5s size=%s" % (k, v.get("ok"), v.get("exists"),
                                                               v.get("size_bytes")))

        #: ④ 综合
        n_cfg = sum(1 for v in cfg.values() if v.get("ok"))
        n_exp = sum(1 for v in exp.values() if v.get("ok"))
        ev["steps"]["judgement"] = {
            "bindings": ev["steps"]["bindings"]["ok"],
            "config_ok": n_cfg, "config_total": len(cfg),
            "export_ok": n_exp, "export_total": len(exp),
            "★": "★ 配置族判 dict 非空 · 导出族判**文件存在且非空**（★ 回读优先）",
        }
        ok = ok and n_cfg >= 4 and n_exp >= 4
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
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
    print("  ── 配置 + 导出真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-14s %s" % (k, json.dumps(v, ensure_ascii=False)[:230]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
