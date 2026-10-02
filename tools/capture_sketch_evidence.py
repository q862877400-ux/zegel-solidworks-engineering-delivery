r"""@brief 真机证据：**草图只读族 4 个工具**（砌墙 W1 / Spec Kit `131` 的验收②）。

## 它验什么（★ 与"只调底层函数"不同）
★ **它走工具的真实路径**：import `tool_specs_batch18._sketch_args`，
用一个只带 `sketch_name` 的假 params 去调 ——
即把「留空 ⇒ 取当前草图 / 给名 ⇒ 按名取」那层逻辑**也一起验了**。
⇒ 验的是「**AI 点这个按钮会得到什么**」，不是「底层函数还在不在」。

## 关键用例（★ 都指向真机探针发现的那件事）
```
1. 草图**建完并关闭**后，按名取仍然可用     ← ★ 探针证明 GetActiveSketch2/ActiveSketch 此时都是 None
2. count_lines == 1（画了 1 条线）           ← ★ 底层 get_lines 返回 12 个 float，薄函数要翻译成 1
3. count_arcs  == 0
4. count_segments == 2（线 + 圆）            ← ★ 与 count_lines 不是同一个数（2 ≠ 1）
5. is_3d_sketch is False
6. ★ **负例**：给一个不存在的草图名 ⇒ **必须抛错**（选不中要报错，不静默返回 0）
7. ★ 留空 `sketch_name` ⇒ 草图**已关闭**时也能取到（用 current_sketch_name 兜底）
```

## ⚠ 安全（照 `tools/probe_sketch_object_routes.py` 的骨架）
**只在新零件上跑**、不改用户文档；`CommandInProgress` 抑制弹窗；收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_sketch_evidence.py
# 定位:   砌墙 W1（Spec Kit `131`）的**验收②**：产出 `output/sketch-evidence.json`（`verdict`）。
# 官方依据: `ISketch.GetSketchSegments` / `GetLines2` / `GetArcs2` / `Is3D`
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

OUT = Path(r"D:\AI\SW\output\sketch-evidence.json")


class _P:
    """最小的 params 容器（注册器传进来的那个形状）。"""

    def __init__(self, sketch_name=""):
        self.sketch_name = sketch_name
        self.response_format = "json"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "capability": "sketch_query",
                "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part
        import tool_specs_batch18 as b18
        from scripts.sw_sketch import count_arcs, count_lines, count_segments, is_3d_sketch

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["part"] = {"ok": True,
                               "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}

        #: 建一个已知草图：1 条线 + 1 个圆，然后**关掉**（★ 关键：关掉之后才验）
        sw_part.start_sketch(doc)
        sw_part.sketch_line(doc, -20.0, 0.0, 20.0, 0.0)
        sw_part.sketch_circle(doc, 0.0, 20.0, 5.0)
        name = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        ev["steps"]["sketch"] = {"ok": True, "name": name, "closed": True}

        #: ★ 走工具真实路径：_sketch_args 把 sketch_name 解析成 sketch 对象
        args_named = b18._sketch_args(_P(name))
        args_blank = b18._sketch_args(_P(""))          #: 留空 ⇒ 用 current_sketch_name 兜底
        ev["steps"]["resolve"] = {
            "ok": args_named.get("sketch") is not None and args_blank.get("sketch") is not None,
            "by_name_on_closed_sketch": args_named.get("sketch") is not None,
            "by_blank_on_closed_sketch": args_blank.get("sketch") is not None,
            "★ 说明": "草图已关闭仍可取到 ⇒ 与探针结论一致（GetActiveSketch2/ActiveSketch 此时为 None）",
        }
        sk = args_named["sketch"]

        #: 四个读数
        got = {"count_lines": int(count_lines(sk)), "count_arcs": int(count_arcs(sk)),
               "count_segments": int(count_segments(sk)), "is_3d": bool(is_3d_sketch(sk))}
        #: ⚠⚠ 2026-10-01 轮 222：`count_arcs` 的期望**一开始写成 0 是错的** ——
        #:   我画的是「1 条线 + 1 个圆」，而**一个圆在 SolidWorks 底层几何里就是一段弧（整圆）**
        #:   ⇒ `GetArcs2` 会把它算进去 ⇒ **1 是对的**。
        #:   佐证：`count_segments == 2` 且 `count_lines == 1` ⇒ 剩下那 1 段就是这个圆。
        #:   ★ 所以这里**不是放宽判据**，是改正一个事实性错误（错的在判据那边，不在代码那边）。
        want = {"count_lines": 1, "count_arcs": 1, "count_segments": 2, "is_3d": False}
        ev["steps"]["readings"] = {"ok": got == want, "got": got, "want": want}
        ok = ok and (got == want)

        #: ★ 负例：不存在的草图名 ⇒ 必须抛错
        try:
            b18._sketch_args(_P("不存在的草图_XYZ"))
            ev["steps"]["negative_bad_name"] = {"ok": False, "★": "**没有抛错** —— 选不中却静默通过"}
            ok = False
        except Exception as exc:                               # noqa: BLE001
            ev["steps"]["negative_bad_name"] = {"ok": True, "raised": type(exc).__name__,
                                               "msg": str(exc)[:90]}

        #: ★ 负例：底层薄函数的除数校验（形状变了要报错，不圆整）
        from scripts.sw_sketch import _count_by_divisor
        try:
            _count_by_divisor(None, lambda _s: [0.0] * 13, 12, "fake")
            ev["steps"]["negative_divisor"] = {"ok": False, "★": "**13 不是 12 的整数倍却没抛错**"}
            ok = False
        except RuntimeError as exc:                            # noqa: BLE001
            ev["steps"]["negative_divisor"] = {"ok": True, "msg": str(exc)[:80]}
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
                    sw.CloseDoc(t)
        except Exception:                                      # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 草图只读族真机读数 ──")
    for k, v in ev["steps"].items():
        print("    %-22s %s" % (k, json.dumps(v, ensure_ascii=False)[:150]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
