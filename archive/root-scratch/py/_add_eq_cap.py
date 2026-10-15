import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

ENTRY = {
    "id": "equations",
    "label": "方程式（增 / 列 / 删 / 求解）",
    "level": "stitched",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "pywin32"],
    "limitations": [
        "⚠ **无本机运行证据**（等级 `stitched`，不得标 `verified`）：签名经两源互核，"
        "但本机从未读写过方程式。",
        "⚠ **走 `Add2` 不走 `Add`**：官方 md 明写 `IEquationMgr.Add` 是 "
        "`Obsolete. Superseded by IEquationMgr::Add2.`（`Add` 少一个 `Solve` 参数）。",
        "⚠⚠ **`-1` 有两种语义，必须分清**：作为**入参** `Index = -1` 表示「追加到末尾」；"
        "作为**返回值** `-1` 表示**失败**。本模块对返回 `-1` **抛异常**，不静默成功。",
        "**方程式字符串必须按 UI 里那样写、维度名带双引号**（官方 Remarks 原文）："
        "`\"B\" = 2` · `\"N_SPOKES@CirPattern\" = \"BARLENGTH@Sketch2\" /10` · "
        "`\"D1@Extrude2\" = (IIf(\"D1@Extrude3\">20, 15, 6))+5`。"
        "⚠ **未做字符串格式校验**（官方没有给出可校验的语法，本模块只挡空串）。",
        "调用前置条件**未查证**：官方 Remarks 提到「要直接编辑装配体零部件的模型，"
        "必须在上下文中编辑该零部件的模型」—— 本模块**未处理**这种情形。",
        "只覆盖 `GetEquationMgr` / `Add2` / `GetCount` / `Equation[i]` / `Delete` / `EvaluateAll`；"
        "`IEquationMgr` 另有 11 属性 + 14 方法，**未逐一实现**。",
    ],
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "本项目自建；依据为出厂类型库反射与官方结构化文档"
                       "（见 `scripts/sw_equation.py` 的来源块）。"
                       "补的是 `docs/union-gap-triage.md`「真缺」档里的 `equation` 一条。",
}

if any(c.get("id") == ENTRY["id"] for c in d["capabilities"]):
    print("  已存在")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已加 equations（stitched）")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
