r"""@brief 真机证据：**建模闭环补全 4 个工具**（24h 段 3 / Spec Kit `146` 的验收②）。

## 判据（★ 规则 6，且**先验判据本身**）
```
★ 每个建特征的调用都回**回读报告**，三条判据：**特征在树里 + `EditRebuild3` 真 + 查错数 0**。
★★ 而那个判据助手（`scripts/sw_feature_readback.py`）**本脚本先自验一遍**：
     `'草图1'` ⇒ ok=True（★ 有判别力）· 不存在的名字 / 容器名 ⇒ ok=False
   ⇒ ★ **判据不自证，就不能拿它判别人**。
```

## ⚠ 安全
只在新零件上跑 · `CommandInProgress` 抑制弹窗 · 关件不保存 · **本批不跑仿真/求解**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_modeling_readback_evidence.py
# 定位:   Spec Kit `146` 的**验收②**：产出 `output/modeling-readback-evidence.json`。
# 官方依据: `IFeatureManager.InsertFeatureShell` / `InsertRib` / `InsertDome` ·
#          `IModelDoc2.InsertCompositeCurve` · `EditRebuild3` ·
#          `IModelDocExtension.GetWhatsWrongCount`
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
    Path(__file__).resolve().parents[1] / "output" / "modeling-readback-evidence.json"
)


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "modeling_readback",
        "steps": {},
    }
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part as P, sw_feature_readback as FR
        from scripts import (
            sw_simulation as S,
        )  #: ★ select_face_at 在这里（不在 sw_part）
        import tool_specs_batch32 as b32

        #: ① 静态：4 个工具声明解析得到
        bindings = {}
        for spec in b32.SPECS_BATCH32:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {
                "resolved": callable(getattr(mod, spec.function, None)),
                "inject": spec.inject,
                "params": [p.name for p in spec.params],
            }
        ev["steps"]["bindings"] = {
            "ok": all(v["resolved"] for v in bindings.values()),
            "count": len(bindings),
            "detail": bindings,
        }

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ② 先造板（★ 100×60×20）+ 一块要抽壳的实体
        doc = sw_connect.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk1 = P.current_sketch_name(doc)
        P.end_sketch(doc)
        P.extrude_boss(doc, sk1, 20.0)
        ev["steps"]["base"] = {"sketch": sk1, "features": FR.feature_names(doc)}

        #: ③ ★★ 先自验判据（★ 不自证就不能判别人）
        r_ok = FR.feature_readback(doc, sk1)
        r_bad = FR.feature_readback(doc, "绝不存在的特征XYZ")
        ev["steps"]["criterion_selfcheck"] = {
            "ok": bool(r_ok.get("ok")) and not bool(r_bad.get("ok")),
            "existing_feature": {
                "ok": r_ok.get("ok"),
                "present": r_ok.get("present"),
                "wrong": r_ok.get("whats_wrong_count"),
            },
            "missing_feature": {"ok": r_bad.get("ok"), "present": r_bad.get("present")},
            "★": "★ 判据有判别力才可用（★ 两边都要对）",
        }
        print(
            "  [自验] 存在的特征 ok=%s · 不存在的 ok=%s ⇒ %s"
            % (
                r_ok.get("ok"),
                r_bad.get("ok"),
                "判据可用"
                if ev["steps"]["criterion_selfcheck"]["ok"]
                else "★ 判据不可用",
            )
        )

        #: ④ 四个工具逐个试（★ 每个都如实记）
        results: dict = {}

        def _try(label: str, fn):
            try:
                r = fn()
                results[label] = {"ok": bool(r.get("ok")), "report": r}
                print(
                    "  [%s] ok=%s present=%s wrong=%s err=%s"
                    % (
                        label,
                        r.get("ok"),
                        (r.get("readback") or {}).get("present"),
                        (r.get("readback") or {}).get("whats_wrong_count"),
                        (r.get("error") or "")[:52],
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results[label] = {
                    "ok": False,
                    "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                }
                print("  [%s] ★ 异常: %s" % (label, str(exc)[:80]))

        #: 抽壳（★ 需要选一个面；用面坐标选）
        _try(
            "shell",
            lambda: (
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True),
                S.select_face_at(doc, 0.0, 0.0, 0.0),
                P.shell_report(doc, 2.0),
            )[-1],
        )
        #: 圆顶（★ 官方 Remarks 要求先选面）
        _try(
            "insert_dome",
            lambda: (
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True),
                S.select_face_at(doc, 0.0, 0.0, 0.0, mark=1),
                P.insert_dome_report(doc, 5.0),
            )[-1],
        )

        #: 筋（★ 要一个草图 —— 建一个新草图当轮廓）
        def _rib():
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            P.start_sketch(doc, plane_name="Front Plane")
            P.sketch_rectangle(doc, 0.0, 0.0, 20.0, 10.0)
            sk2 = P.current_sketch_name(doc)
            P.end_sketch(doc)
            return P.rib_report(doc, sk2, 2.0)

        _try("rib", _rib)

        #: 复合曲线（★ 要 mark=1 选实体 ⇒ 用声明式选择试一次）
        def _comp():
            sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
            from scripts.sw_selection_spec import resolve_selection

            resolve_selection(doc, "index:0", "EDGE")
            return P.insert_composite_curve_report(doc)

        _try("insert_composite_curve", _comp)

        ev["steps"]["tools"] = results
        n_ok = sum(1 for v in results.values() if v.get("ok"))
        ev["steps"]["judgement"] = {
            "selfcheck": ev["steps"]["criterion_selfcheck"]["ok"],
            "tools_ok": n_ok,
            "tools_total": len(results),
            "★": "★ 判据自验通过 + 至少一个建特征工具回读三真 ⇒ 本批算过",
        }
        #: ★ 判据自验必须过；工具部分如实报（不达标不算 pass —— 硬约束③）
        ev["_ok"] = (
            ev["steps"]["bindings"]["ok"]
            and ev["steps"]["criterion_selfcheck"]["ok"]
            and n_ok >= 1
        )
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["_ok"] = False
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
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if ev.pop("_ok", False) and not ev.get("error") else "fail"
    print("  ── 建模回读真机证据 ──")
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
