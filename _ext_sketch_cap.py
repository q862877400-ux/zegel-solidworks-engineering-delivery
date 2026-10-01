import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "sketch_edit_ops":
        c["label"] = "草图编辑（倒角 / 镜像 / 转换实体引用）"
        c["limitations"].append(
            "⚑ 2026-10-01（轮 115）**扩了一条**：`convert_entities` —— 走 "
            "`ISketchManager.SketchUseEdge3(Boolean Chain, Boolean InnerLoops)`"
            "（**当前入口**；官方明写 `IModelDoc2.SketchUseEdge2` 是 Obsolete）。"
            "⚠ 官方写明它投影的是「**selected** edges/loops/faces/curves/external contours」"
            "⇒ 调用前必须**先选中**并**进入草图**（本模块不代选）。"
            "⚠ 另有零参的 `ISketchManager.ConvertEntities()`（未废弃）也能用，本模块未采用 —— "
            "选 `SketchUseEdge3` 是因为它**两个参数都有官方说明**，语义更明确。"
        )
        print("  ok 已扩 sketch_edit_ops")
        break
else:
    raise SystemExit("  找不到 sketch_edit_ops")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
