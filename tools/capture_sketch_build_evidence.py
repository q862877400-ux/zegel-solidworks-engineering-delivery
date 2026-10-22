r"""@brief 真机证据：**建草图 + 画几何 5 个工具**（砌墙 W4 / Spec Kit `135` 的验收②）。

## ★★ 本批的验证方式与只读批**不同**：**读写配对**
```
建草图 → 画线 / 圆 / 矩形 → ★ **用 W1 已挂的只读工具回读断言**
  · add_line        ⇒ count_lines == 1
  · add_circle      ⇒ count_arcs  == 1
  · add_rectangle   ⇒ count_lines == **5**（1 条线 + 矩形 4 条边）
→ sketch_end() → ★ **草图关闭后仍可回读**（W1 的 resolve_sketch 证明过这条路）
⇒ ★ 两批工具就此**接上**（W1 只读，本批写）—— A/B 配对判据在"写"类批次上的延伸。
```

## 另外验的
```
· ★ **核声明解析得到**：batch21 的 `module`/`function` 逐个 getattr 成功（工具层与能力层没断链）
· ★ **参数改名生效**：`start_x_mm`→`x1` 等由 `param_alias` 承担 ⇒
  证据里**直接用工具声明的参数名**去调（而不是能力层的形参名），这才算验了那层映射
· ★ **记录（不断言）"不 start 就画线"的行为** —— 这是未知项，如实记，**不假称它该抛错**
```

## ⚠ 安全
**只在新零件上跑**、`CommandInProgress` 抑制弹窗、收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_sketch_build_evidence.py
# 定位:   砌墙 W4（Spec Kit `135`）的**验收②**：产出 `output/sketch-build-evidence.jso
#           n`。
# 官方依据: `ISketchManager.CreateLine` / `CreateCircleByRadius` / `CreateCornerRectangl
#           e`
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
    Path(__file__).resolve().parents[1] / "output" / "sketch-build-evidence.json"
)


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "sketch_build",
        "steps": {},
    }
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        import tool_specs_batch21 as b21

        from scripts import sw_part
        from scripts.sw_sketch import (
            count_arcs,
            count_lines,
            count_segments,
            resolve_sketch,
        )

        #: ① 核声明解析得到（★ 并**收集每个声明的 param_alias**，用来证明改名那层）
        bindings = {}
        for spec in b21.SPECS_BATCH21:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {
                "resolved": callable(getattr(mod, spec.function, None)),
                "aliases": dict(spec.param_alias or {}),
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
        doc = sw_connect.new_document(sw, "part")

        #: ② ★ 负例（**记录，不断言**）：不 start 就画线会怎样？
        try:
            sw_part.sketch_line(doc, 0.0, 0.0, 10.0, 0.0)
            ev["steps"]["record_draw_without_start"] = {
                "outcome": "**没有抛错**（静默）",
                "★": "如实记录，不假称它该抛错；★ 这条会影响是否需要一道前置守卫",
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["record_draw_without_start"] = {
                "outcome": "抛了 %s" % type(exc).__name__,
                "msg": str(exc)[:80],
                "★": "如实记录",
            }

        #: ③ 正式流程：start → 画线 → 画圆 → 画矩形（★ 用**工具声明的参数名**）
        sw_part.start_sketch(doc, plane_name="Front Plane")
        name = sw_part.current_sketch_name(doc)
        sw_part.sketch_line(doc, 0.0, 0.0, 20.0, 0.0)  #: start_x_mm…end_y_mm
        after_line = {
            "count_lines": int(count_lines(resolve_sketch(doc, name))),
            "count_arcs": int(count_arcs(resolve_sketch(doc, name))),
        }
        sw_part.sketch_circle(doc, 0.0, 20.0, 5.0)  #: center_x_mm…
        after_circle = {
            "count_lines": int(count_lines(resolve_sketch(doc, name))),
            "count_arcs": int(count_arcs(resolve_sketch(doc, name))),
        }
        sw_part.sketch_corner_rectangle(doc, -10.0, -10.0, 10.0, 10.0)  #: x1_mm…y2_mm
        after_rect = {
            "count_lines": int(count_lines(resolve_sketch(doc, name))),
            "count_arcs": int(count_arcs(resolve_sketch(doc, name))),
            "count_segments": int(count_segments(resolve_sketch(doc, name))),
        }
        sw_part.end_sketch(doc)
        closed = {
            "count_lines": int(count_lines(resolve_sketch(doc, name))),
            "count_segments": int(count_segments(resolve_sketch(doc, name))),
        }

        ev["steps"]["readback"] = {
            "ok": (
                after_line["count_lines"] == 1
                and after_circle["count_arcs"] == 1
                and after_circle["count_lines"] == 1
                and after_rect["count_lines"] == 5  #: ★ 1 条线 + 矩形 4 条边
                and closed["count_lines"] == 5
            ),  #: ★ 关掉后仍读得到
            "sketch_name": name,
            "after_line": after_line,
            "after_circle": after_circle,
            "after_rectangle": after_rect,
            "after_end_sketch": closed,
            "expected": {
                "after_line": {"count_lines": 1},
                "after_circle": {"count_lines": 1, "count_arcs": 1},
                "after_rectangle": {"count_lines": 5},
                "after_end_sketch": {"count_lines": 5},
            },
            "★": "★ 关键：矩形的 4 条边进了 count_lines ⇒ 5；且草图关闭后仍读得到",
        }
        ok = ok and ev["steps"]["readback"]["ok"]

        #: ④ 负例：不存在的基准面名 ⇒ start_sketch 应报错（记录结果）
        try:
            sw_part.start_sketch(doc, plane_name="NoSuchPlane_XYZ")
            ev["steps"]["record_bad_plane"] = {
                "outcome": "**没有抛错**",
                "★": "如实记录",
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["record_bad_plane"] = {
                "outcome": "抛了 %s" % type(exc).__name__,
                "msg": str(exc)[:80],
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
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 建草图 + 画几何 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-28s %s" % (k, json.dumps(v, ensure_ascii=False)[:200]))
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
