import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

ENTRY = {
    "id": "sketch_edit_ops",
    "label": "草图编辑（倒角 / 镜像）",
    "level": "stitched",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "pywin32"],
    "limitations": [
        "⚠ **无本机运行证据**（等级 `stitched`，不得标 `verified`）：签名经两源互核，"
        "但本机从未做过草图倒角/镜像。",
        "★★ **枚举两源冲突，按铁律 4 取出厂反射**：`swSketchChamfer_DistanceDistance` "
        "在 `C:\\swapi\\enums\\swSketchChamferType_e.md` 里写 **-1**、在出厂反射里写 **1**。"
        "本模块取 **1**。★ 这是铁律 4「冲突以出厂类型库为准」的**活例**。",
        "倒角走**非废弃**入口：官方明写 `IModelDoc2.SketchChamfer` 是 `Obsolete`，"
        "被 `ISketchManager::CreateChamfer` 取代 ⇒ 本模块用后继。",
        "⚠ **前置条件**（两处都要求「先选中」，本模块**不代选**）：倒角需选中**两条**草图实体；"
        "镜像需按官方标记选中（**线段 mark=1** / **中心线 mark=2**）—— 标记是选中时定的，"
        "不是传参定的（官方签名 0 参）。",
        "⚠ `CreateChamfer` 的第三参 `AngleORdist` **单位随类型变**（距离-距离=第二距离 / "
        "距离-角度=角度 / 距离-相等=忽略），**官方未写单位** ⇒ 本模块**不做换算**、按原样传。",
    ],
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "本项目自建；依据为出厂类型库反射与官方结构化文档（见 `scripts/sw_sketch_edit.py` 的来源块）。"
                       "补的是 `docs/union-gap-triage.md`「真缺」档里的 `sketch_chamfer` 与 `sketch_mirror` 两条。",
}

if any(c.get("id") == ENTRY["id"] for c in d["capabilities"]):
    print("  已存在")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已加 sketch_edit_ops（stitched）")
import collections
print("  能力数 %d · level 分布 %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
