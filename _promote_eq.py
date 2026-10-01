import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "equations":
        continue
    c["level"] = "verified"
    c["verified_versions"] = ["2026"]
    c["evidence"] = [
        "python tools/verify_equation_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：新建临时零件 → 加方程式 → 列 → 求解 → 关件不保存，"
        "**5/5 通过**，证据落 output/equation-smoke-evidence.json）",
        "pytest tests/test_sw_equation_contract.py（**10 条契约测试，无 COM**）",
    ]
    c["limitations"] = [
        "⚑ 2026-10-01（轮 116）**由 `stitched` 升为 `verified`** —— 依据是真机冒烟"
        "`tools/verify_equation_smoke.py`（**5/5**）：`add_equation('\"SMOKE_B\" = 2')` 返回下标 **0**，"
        "`list_equations` 读回 **1 条且内容原样**（`'\"SMOKE_B\" = 2'`）—— "
        "★ **往返一致**证明它真写进去了、不是空操作；`evaluate_equations` 不抛；"
        "**收尾无残留模态框**；临时件已关且未保存。",
        "⚠ **只验了「全局变量方程式」这一种**（官方示例里最简单的一种）。"
        "**维度方程式**（`\"D1@Extrude2\" = …`）与**含 VB `IIf` 的**都**未测**。",
        "⚠ `delete_equation` **未在真机上调过**（冒烟只覆盖 加 / 列 / 求解）。",
        "⚠ 冒烟**不证明「结果正确」**：它只证「这几步没抛异常 + 往返一致」；"
        "例如 **`evaluate_equations` 的返回值语义未核**（只验了它不抛）。",
        "⚠ 走 `Add2` 不走 `Add`：官方 md 明写 `IEquationMgr.Add` 是 "
        "`Obsolete. Superseded by IEquationMgr::Add2.`（`Add` 少一个 `Solve` 参数）。",
        "⚠⚠ **`-1` 有两种语义**：作为**入参** `Index = -1` 表示「追加到末尾」；"
        "作为**返回值** `-1` 表示**失败**。本模块对返回 `-1` **抛异常**，不静默成功。",
        "**方程式字符串必须按 UI 里那样写、维度名带双引号**（官方 Remarks 原文）。"
        "⚠ **未做字符串格式校验**（官方没给可校验的语法，本模块只挡空串）。",
        "⚠ 官方 Remarks 提到「要直接编辑装配体零部件的模型，必须在上下文中编辑该零部件的模型」"
        "—— 本模块**未处理**这种情形。",
        "只覆盖 `GetEquationMgr` / `Add2` / `GetCount` / `Equation[i]` / `Delete` / `EvaluateAll`；"
        "`IEquationMgr` 另有 11 属性 + 14 方法，**未逐一实现**。",
    ]
    print("  ok equations: stitched -> verified")
    break
else:
    raise SystemExit("  找不到 equations")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
