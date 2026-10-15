import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "geometric_tolerance":
        continue
    c["level"] = "stitched"
    c["evidence"] = [
        "python tools/verify_gtol_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → InsertGtol → 加指示符 → 关件不保存）"
        "—— ⚠ **3/5**：`insert_gtol` **通过**、**`add_gtol_indicator` 失败**"
        "（证据落 output/gtol-smoke-evidence.json）",
        "pytest tests/test_sw_gtol_contract.py（**16 条契约测试，无 COM**）",
    ]
    c["limitations"] = [
        "★★ **2026-10-01（轮 120）真机实测：本能力「一半可用、一半到不了」**：",
        "　 ✅ **`insert_gtol` 真机可用** —— `InsertGtol()`（0 参）返回一个 GTol 对象。",
        "　 ❌ **`add_gtol_indicator` 真机到不了** —— 量到的事实（均在**新零件**上）："
        "`GetFrameCount()` 新建后 = **1**；`AddFrame()` 返回 **False**；"
        "`GetFrame(0)` / `(1)` / `(2)` **全 None**；"
        "`CanConvertFormat()` → True、`ConvertFormat()` → **0（成功）**，"
        "转换后 `GetFrameCount()` **掉到 0**，而 `GetFrame(1)` / `(2)` **仍全 None**。"
        "⇒ **「2022 格式的帧路径」在本机（SW 2026 SP4.1 / pywin32 迟到绑定）上取不到帧。**",
        "⚠ **按已知事实 53 停手**：同一处已试 **3 次**（补帧 / 直接取 / 先 `ConvertFormat`），"
        "**不再变着法试**。本模块**保留** `add_gtol_indicator`（**不删**）—— "
        "它是**可复算的证据**，也便于别的后端（如 `comtypes`）上重试；但它**当前不可用**。",
        "★ **为什么仍走 `AddIndicator` 而不是 `SetFrameSymbols2`**：官方明写后者"
        "「valid only if this Gtol was created in a version of SOLIDWORKS **earlier than 2022**」，"
        "且它的符号参数是 `LibraryName-SymbolName` 形态的**字形串**（官方文档里显示为空）"
        "⇒ **文本协议传不了**。⚠ 但实测表明**前者在本机也到不了** —— 两条路**都不通**。",
        "⚠ **两条枚举**取自出厂反射并逐值核对：`swGtolIndicatorBorderType_e` = 0..3 · "
        "`swGtolGeomCharSymbol_e` = **19 项 / 12..30**。⚠ 枚举本身没问题，"
        "**问题在取不到帧**。",
        "⚠ **未查证**：换后端（`comtypes` / 进程内 C++）能否走通；"
        "`IGtolFrame.SetSymbolXml`（XML 路径）**未试**；"
        "`SetIndicator` / `DeleteFrame` / 取回族**未试**（都要先能拿到帧）。",
        "⚠ 官方 `IGtol.GetFrame` 的 `FrameIndex` 是 **1 基**；"
        "`InsertGtol` 的引线来自**调用前的选中**（没选中则无引线、位于原点）—— 本模块**不代选**。",
    ]
    print("  ok geometric_tolerance 已改为诚实的分裂声明")
    break
else:
    raise SystemExit("  找不到 geometric_tolerance")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))
