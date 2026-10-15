# -*- coding: utf-8 -*-
"""记下 BuildFile 当前基线，后续新生成的件靠它识别。"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")
state = {"baseline": [], "snapshot_at": "2026-09-30"}
if BF.is_dir():
    for p in sorted(BF.iterdir()):
        if p.is_file() and not p.name.startswith("~$"):
            state["baseline"].append({"name": p.name, "size": p.stat().st_size,
                                      "mtime": p.stat().st_mtime})
out = Path(r"D:\AI\SW\bf_state.json")
out.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
print("  基线 %d 个零件" % len(state["baseline"]))
for b in state["baseline"]:
    print("    %s" % b["name"][:70])
