import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
t = P.read_text(encoding="utf-8")
d = json.loads(t)

ENTRY = {
    "id": "helix_and_spiral",
    "label": "螺旋线与涡旋（定距）",
    "level": "stitched",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "pywin32"],
    "limitations": [
        "⚠ **无本机运行证据**（等级 `stitched`，不得标 `verified`）：签名经**两源互核**"
        "（出厂反射 `iface_sldworks.txt` 的 `IModelDoc2.InsertHelix` 10 参与 "
        "`C:\\swapi\\types\\IModelDoc2\\InsertHelix.md`），并有官方示例的调用形态佐证；"
        "但**本机从未建过螺旋线**。",
        "调用前置条件**未查证**：官方示例先 `SelectByID2` 选一个圆再调 "
        "`InsertHelix`（以该圆为直径基准）；未选圆时的行为未实测。",
        "⚠ **单位：官方只写明两个**——`Height` 是**米**、`Startangle` 是**弧度**"
        "（本模块分别用 `mm()` / `deg()` 换算）。`Pitch` 与 `TaperAngle` **官方未写单位**；"
        "本模块 `pitch_mm` 按米换算、`taper_angle_deg` 按度直传 —— 这是**同类推断，不是查证**。",
        "★ 本模块第一版**把两个枚举值写反了**（凭记忆）：真值 "
        "`swHelixDefinedByHeightAndRevolution = 1` · `swHelixDefinedByHeightAndPitch = 2`，"
        "被两源查证拦下 ⇒ 契约测试现在把枚举值单独钉住。",
        "只覆盖**定距**螺旋线/涡旋；变距（`IFeatureManager.InsertVariablePitchHelix`）未实现。",
    ],
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "本项目自建；依据为出厂类型库反射与官方结构化文档（见 `scripts/sw_helix.py` 的来源块）。"
                       "补的是 `docs/union-gap-triage.md`「真缺」档里的 `helix` 一条"
                       "（`022` 核出该档确实没有实现）。",
}

if any(c.get("id") == ENTRY["id"] for c in d["capabilities"]):
    print("  已存在，不改")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已加能力条目 helix_and_spiral（stitched）")
    print("  现在能力数: %d" % len(d["capabilities"]))

import collections
print("  level 分布: %s" % dict(collections.Counter(c.get("level") for c in d["capabilities"])))
