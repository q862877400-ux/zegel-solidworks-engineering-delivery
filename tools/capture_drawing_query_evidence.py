r"""@brief 真机证据：**当前活动工程图的轻量只读读数 3 个工具**（砌墙 W2 / Spec Kit `132` 的验收②）。

## 它验什么（★ 走工具的真实绑定，不是只看函数在不在）
除了调能力层，它还**逐条核对 batch19 里声明的 `module`/`function` 真的存在且可调用**
（import `tool_specs_batch19` 后按声明去 getattr）—— 即验「AI 点这个按钮会得到什么」。

## 关键用例
```
1. 新建空工程图 ⇒ `list_sheets` 回 {count:1, names:["图纸1"], current:"图纸1"}
2. `get_current_sheet` 回 paper=A4 · **297 × 210 mm**（★ 官方给的是**米**，工具要换算）
3. ★★ `list_views` **必须回空表** —— 官方 `GetFirstView()` 在空图纸上返回的是**图纸本身**
   （`Type == 1`），不滤掉就会列出名叫「图纸1」的**假视图**。这一条是本批最关键的正例。
4. ★ **负例**：在**零件**上调这三个工具 ⇒ 必须**抛错**（GetType() != 3），不得静默回空
5. ★ **负例**：`GetProperties2` 元素不足时 ⇒ 必须抛错（官方返回结构变了要被看见）
```

## ⚠ 安全（照 `tools/probe_drawing_object_routes.py` 的骨架）
**只在新文档上跑**、不改用户文档；`CommandInProgress` 抑制弹窗；收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_drawing_query_evidence.py
# 定位:   砌墙 W2（Spec Kit `132`）的**验收②**：产出 `output/drawing-query-evidence.js
#           on`（`verdict`）。
# 官方依据: `IDrawingDoc.GetCurrentSheet` / `GetSheetCount` / `GetSheetNames` · `ISheet.
#           GetProperties2`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
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
    Path(__file__).resolve().parents[1] / "output" / "drawing-query-evidence.json"
)


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "drawing_query",
        "steps": {},
    }
    sw = None
    docs: list = []
    ok = True
    try:
        import sw_connect
        import tool_specs_batch19 as b19

        from scripts import sw_drawing_query as dq

        #: ① ★ 先核"声明的东西真的存在"（工具层与能力层没断链）
        bindings = {}
        for spec in b19.SPECS_BATCH19:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            fn = getattr(mod, spec.function, None)
            bindings[spec.name] = {
                "module": spec.module,
                "function": spec.function,
                "resolved": callable(fn),
            }
        ev["steps"]["bindings"] = {
            "ok": all(v["resolved"] for v in bindings.values()),
            "detail": bindings,
        }
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ② 空工程图上的三个读数
        drw = sw_connect.new_document(sw, "drawing")
        docs.append(drw)
        summary = dq.sheets_summary(drw)
        info = dq.current_sheet_info(drw)
        views = dq.list_views(drw)
        ev["steps"]["sheets_summary"] = {
            "ok": summary.get("count") == 1 and summary.get("names") == ["图纸1"],
            "got": summary,
        }
        ev["steps"]["current_sheet_info"] = {
            "ok": (
                info.get("paper_size") == "A4"
                and abs(info.get("width_mm", 0) - 297.0) < 1.0
                and abs(info.get("height_mm", 0) - 210.0) < 1.0
            ),
            "got": info,
        }
        #: ★★ 最关键的一条：假视图必须被滤掉
        ev["steps"]["list_views_on_empty_sheet"] = {
            "ok": views == [],
            "got": views,
            "★": "官方 GetFirstView() 在空图纸上返回的是**图纸本身**（Type==1）"
            "⇒ 这一条为真才说明过滤生效；否则会列出名叫「图纸1」的假视图",
        }
        for k in ("sheets_summary", "current_sheet_info", "list_views_on_empty_sheet"):
            ok = ok and ev["steps"][k]["ok"]

        #: ③ ★ 负例：在**零件**上调 ⇒ 必须抛错
        part = sw_connect.new_document(sw, "part")
        docs.append(part)
        neg = {}
        for label, fn in (
            ("sheets_summary", dq.sheets_summary),
            ("current_sheet_info", dq.current_sheet_info),
            ("list_views", dq.list_views),
        ):
            try:
                fn(part)
                neg[label] = "★ **没有抛错** —— 在零件上静默通过了"
            except RuntimeError as exc:  # noqa: PERF203
                neg[label] = "RuntimeError: %s" % str(exc)[:70]
        ev["steps"]["negative_on_part"] = {
            "ok": all("没有抛错" not in v for v in neg.values()),
            "detail": neg,
        }
        ok = ok and ev["steps"]["negative_on_part"]["ok"]

        #: ④ ★ 负例：返回结构不对 ⇒ 必须抛错（不圆整、不猜）
        class _Fake:
            def __init__(self, vals):
                self._v = vals

        real_get = dq.get_com_member

        def _patched(obj, name, *a, **kw):
            if name == "GetProperties2":
                return [6.0, 12.0, 1.0]
            return real_get(obj, name, *a, **kw)

        dq.get_com_member = _patched
        try:
            dq.current_sheet_info(drw)
            ev["steps"]["negative_bad_shape"] = {
                "ok": False,
                "★": "元素不足却**没有抛错**",
            }
            ok = False
        except RuntimeError as exc:  # noqa: BLE001
            ev["steps"]["negative_bad_shape"] = {"ok": True, "msg": str(exc)[:80]}
        finally:
            dq.get_com_member = real_get
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
    print("  ── 工程图轻量读数真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-30s %s" % (k, json.dumps(v, ensure_ascii=False)[:132]))
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
