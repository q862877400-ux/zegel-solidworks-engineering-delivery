"""★ 真机验证 `GetActiveSketch2` 的后继 `ISketchManager.ActiveSketch`（★ 属性）能不能替代。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_activesketch_successor.py
# 定位:   ★ T1b：★ 把 `IModelDoc2.GetActiveSketch2`（**方法**）换成
#   `ISketchManager.ActiveSketch`（**属性**）。
#   官方依据:
#     · `C:\\swapi\\types\\IModelDoc2\\GetActiveSketch2.md` 逐字：
#       「**Obsolete. Superseded by [[SketchManager::ActiveSketch]].**」
#     · `C:\\swapi\\types\\ISketchManager\\ActiveSketch.md` 签名逐字：
#       `Sketch ActiveSketch {get;}`   ← ★★ **属性（只读）**，不是方法
#   ★★ 本仓既有的真机读数（`scripts/sw_sketch.py` 的函数文档逐字）：
#     「① 草图**已关闭**时，`SketchManager.ActiveSketch` 与 `model.GetActiveSketch2` **都是 None**」
#     ⇒ ★ 说明两者**行为等价**（★ 但那句话本身也要复核）
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "activesketch-successor-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: ★ 用例 1：**没有活动草图**时两者各是什么
        row0 = {"case": "★ 无活动草图"}
        try:
            row0["GetActiveSketch2"] = repr(_g(doc, "GetActiveSketch2"))
        except Exception as exc:                                          # noqa: BLE001
            row0["GetActiveSketch2"] = "ERR %s" % type(exc).__name__
        try:
            sm = _g(doc, "SketchManager")
            row0["SketchManager.ActiveSketch"] = repr(_g(sm, "ActiveSketch"))
        except Exception as exc:                                          # noqa: BLE001
            row0["SketchManager.ActiveSketch"] = "ERR %s: %s" % (type(exc).__name__, str(exc)[:90])
        R["cases"].append(row0)

        #: ★ 用例 2：**开着草图**时两者各是什么（★ 这才是关键对照）
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.04, -0.03, 0.0, 0.04, 0.03, 0.0)
        row1 = {"case": "★ 草图开着"}
        try:
            row1["GetActiveSketch2"] = repr(_g(doc, "GetActiveSketch2"))
        except Exception as exc:                                          # noqa: BLE001
            row1["GetActiveSketch2"] = "ERR %s" % type(exc).__name__
        try:
            sm = _g(doc, "SketchManager")
            sk = _g(sm, "ActiveSketch")
            row1["SketchManager.ActiveSketch"] = repr(sk)
            #: ★ 两者是不是**同一个对象**：★ 拿它的名字比
            try:
                row1["ActiveSketch.Name"] = repr(_g(sk, "Name") if sk is not None else None)
            except Exception as exc:                                      # noqa: BLE001
                row1["ActiveSketch.Name"] = "ERR %s" % type(exc).__name__
        except Exception as exc:                                          # noqa: BLE001
            row1["SketchManager.ActiveSketch"] = "ERR %s: %s" % (type(exc).__name__, str(exc)[:90])
        R["cases"].append(row1)
        P.end_sketch(doc)

        #: ★ 用例 3：**草图已关闭**时（★ 复核本仓那句"都是 None"）
        row2 = {"case": "★ 草图已关闭"}
        try:
            row2["GetActiveSketch2"] = repr(_g(doc, "GetActiveSketch2"))
        except Exception as exc:                                          # noqa: BLE001
            row2["GetActiveSketch2"] = "ERR %s" % type(exc).__name__
        try:
            row2["SketchManager.ActiveSketch"] = repr(_g(_g(doc, "SketchManager"), "ActiveSketch"))
        except Exception as exc:                                          # noqa: BLE001
            row2["SketchManager.ActiveSketch"] = "ERR %s: %s" % (type(exc).__name__, str(exc)[:90])
        R["cases"].append(row2)
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    #: ★ 判据（★ 先写死）：★ 开草图时**两者都非 None**、★ 关闭时**两者都 None** ⇒ **等价，可换**
    c1 = R["cases"][1] if len(R["cases"]) > 1 else {}
    c2 = R["cases"][2] if len(R["cases"]) > 2 else {}
    open_both = (str(c1.get("GetActiveSketch2", "")).startswith("<")
                 and str(c1.get("SketchManager.ActiveSketch", "")).startswith("<"))
    closed_both_none = (c2.get("GetActiveSketch2") == "None"
                        and c2.get("SketchManager.ActiveSketch") == "None")
    R["verdict"] = ("★ PASS —— 开草图时两者都非 None、关闭时都是 None ⇒ **行为等价，可换**"
                    if open_both and closed_both_none else
                    "★★ 需人工看 —— 两者行为不一致（★ 如实记，★ 不硬换）")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
