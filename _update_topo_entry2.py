import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
parts = [
    "⚠⚠⚠ **2026-10-01（轮 179）复跑验收命令：现在是红的，原因在**环境**（不是代码退化）** —— ",
    "`python tools/capture_topology_evidence.py` ⇒ `verdict: fail`，`error` = ",
    "`RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None：Simulation 加载项未加载或本机未安装`。",
    "★ 探针 `tools/probe_simulation_addin_status.py` 分辨了两种可能：",
    "① 加载前 `GetAddInObject('SldWorks.Simulation')` ⇒ **None**；",
    "② `LoadAddIn(<5 个候选名>)` ⇒ **全部返回 3**（⚠ 官方**未给返回码枚举** ⇒ **不猜它是什么**）；",
    "③ 加载后 ⇒ **仍 None**。",
    "⇒ ★ 不是「程序没加载」（那类可修），而是**许可 / 安装**层面（**环境性**）。",
    "★ **为什么仍保持 `verified`**：本条目要的是「**有我们自己的运行证据**」，而证据**在** —— ",
    "`output/topology-evidence.json` 记着当时的完整闭环（`verdict: pass`：建研究 `AnalysisType == 13`、",
    "目标+质量约束 `EndEdit == 0`、夹具选区计数 1、`study.Results` 非空）。",
    "⚠ 但**当前环境复跑不了** ⇒ ★ 这一条**必须写出来**，否则下一个人会以为**随时能跑**。",
    "★ **恢复办法（需要用户，属「只有用户能提供的东西」）**：在 SolidWorks 里确认「Simulation」加载项已启用，",
    "并在 SolidNetWork License Manager 中确认 `SOLIDWORKS Simulation Professional/Premium` 可用",
    "（⚠ 本轮**没有**动任何许可设置）。",
]
ADD = "".join(parts)
n = 0
for c in d["capabilities"]:
    if c.get("id") == "topology_optimization":
        c["limitations"].insert(0, ADD)
        n += 1
print("  ok topology_optimization 已更新（%d 条）" % n)
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
