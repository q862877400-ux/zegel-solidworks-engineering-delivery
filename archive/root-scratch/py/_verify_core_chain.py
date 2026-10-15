"""★ 真机验：**核心建模链**（草图→矩形→结束→拉伸）按 ToolSpec 契约调。"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts")); sys.path.insert(0, str(R / "mcp-server"))

import sw_connect
from sw_part import (extrude_boss, sketch_corner_rectangle, start_sketch, end_sketch,
                     current_sketch_name, feature_names)

sw, doc = sw_connect.connect_solidworks(wait_seconds=30)
print("  当前文档：%r" % (doc or ""))
out = {}
try:
    n0 = len(list(feature_names(doc)))
    start_sketch(doc, plane_name="Front Plane")            # ← 补了 inject="model" 的那个
    out["start_sketch"] = "ok"
    sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)  # ← 同族
    sk = current_sketch_name(doc, "")
    out["sketch_name"] = sk
    end_sketch(doc)
    r = extrude_boss(doc, sk, 12.0)                         # ← 补了 inject="model" 的那个
    out["extrude_type"] = type(r).__name__
    n1 = len(list(feature_names(doc)))
    out["tree"] = [n0, n1]
    out["verdict"] = "pass" if n1 > n0 else "fail"
except Exception as e:
    out["verdict"] = "fail"
    out["err"] = "%s: %s" % (type(e).__name__, str(e)[:160])
print("  " + json.dumps(out, ensure_ascii=False, default=str)[:400])
Path(r"D:\AI\SW\output\core-chain-mcp-contract-evidence.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
print("  ⇒ **%s**" % str(out.get("verdict")).upper())
try:
    sw.CommandInProgress = False
except Exception:
    pass
