import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

NOTE = (
    "⚑⚑ **2026-10-01（轮 202）更正归因**：本条此前把「验收红」归为**环境**"
    "（`GetAddInObject('SldWorks.Simulation')` 返回 None，读成『加载项未加载或未安装，需 Simulation 许可证』）。"
    "★ 实测证明**『需许可证』那半是错的**："
    "① `LoadAddIn(\"SldWorks.Simulation\")` 返回 **3 = swFileNotFound** —— 那是「文件没找到」，"
    "因为官方文档写明该参数要**完整文件路径**（唯一例外是 `LoadAddIn('MBD')`）；"
    "**许可错是 7 = swLicenseError**（读 `C:\\swapi\\enums\\swLoadAddinError_e.md`）；"
    "② 用只读注册表读到的真路径 `…\\SOLIDWORKS\\Simulation\\cosworks.dll` 调 `LoadAddIn` ⇒ **0 = swSuccess**；"
    "③ 之后 `GetAddInObject` ⇒ **非 None**（CDispatch）。"
    "⇒ 真因是「**加载项没启用**」，不是许可。"
    "★ 已把这一改装进正常路径：`scripts/sw_simulation.py` 的 `ensure_simulation_addin()`"
    "（取不到就先 `LoadAddIn` 完整路径），`get_cosmosworks()` 复用它 ⇒ "
    "实测 `get_cosmosworks(sw)` 返回 `CDispatch`。"
    "⚠ **仍未跑求解** —— 求解器不收敛那条**是另一件事**，本更正**没有**解决它。"
)

n = 0
for cid in ("topology_optimization", "simulation_and_fea"):
    c = next(x for x in d["capabilities"] if x["id"] == cid)
    lim = c.setdefault("limitations", [])
    if not any("轮 202" in str(x) for x in lim):
        lim.insert(0, NOTE)
        n += 1
        print("  已给 %s 插更正（现在 %d 条 limitations）" % (cid, len(lim)))

if n:
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d2 = json.loads(P.read_text(encoding="utf-8"))
    ok = any("轮 202" in str(x) for x in next(
        c for c in d2["capabilities"] if c["id"] == "topology_optimization")["limitations"])
    print("  复核: %d 条能力 · topology 含轮 202 = %s" % (len(d2["capabilities"]), ok))
