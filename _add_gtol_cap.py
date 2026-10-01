import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))

ENTRY = {
    "id": "geometric_tolerance",
    "label": "形位公差（新建 + 加公差指示符）",
    "level": "stitched",
    "backends": ["solidworks-com-pywin32"],
    "verified_versions": [],
    "dependencies": ["SolidWorks", "pywin32"],
    "limitations": [
        "⚠ **无本机运行证据**（等级 `stitched`，不得标 `verified`）：签名两源互核，"
        "但本机从未建过形位公差。",
        "★★ **关键查证：旧路径在新版 SolidWorks 上无效**。官方 `IGtol.SetFrameSymbols2` 的 Remarks "
        "**原文**写着「**This method is valid only if this Gtol was created in a version of "
        "SOLIDWORKS earlier than 2022.**」—— 而本机是 **SW 2026**，那条路**不可用**。"
        "⚠ 而且它的符号参数是 `LibraryName-SymbolName` 形态的**字形串**"
        "（官方文档里那些符号**显示为空**，是特殊字体的字形）⇒ **文本协议传不了**。",
        "⇒ 本模块走 **2022 格式**的路径：`IGtolFrame.AddIndicator(Int32 BorderType, "
        "Int32 TolType, String Datum)` —— ★ **收枚举 + 字符串，两样都是文本能传的**。"
        "（另有 `SetSymbolXml(String)` 走 XML，官方有独立 Schema 文档，**本模块未采用**。）",
        "⚠ **两条枚举都取自出厂反射**并逐值核对：`swGtolIndicatorBorderType_e` = 0..3 · "
        "`swGtolGeomCharSymbol_e` = **19 项 / 12..30**。",
        "⚠ 官方 `IGtol.GetFrame` 的 `FrameIndex` 是 **1 基**。",
        "⚠ `IGtolFrame.AddIndicator` 的失败原因是**推断**的（官方只说「返回 True 成功 / False 失败」）："
        "本模块把「不是 2022 格式」与「枚举取值不在范围内」列为常见原因，**未实测**。",
        "⚠ 只覆盖 **新建 + 加指示符**；`SetSymbolXml`（XML 路径）/ `SetIndicator`（改已有指示符）/ "
        "`DeleteFrame` / `AddFrame` / 取回（`GetFrameSymbols*` / `GetFrameValues`）**都未实现**。",
        "⚠ 官方 Remarks 说 `InsertGtol` 的**引线连接点来自调用前的选中**；没选中则无引线、"
        "位于模型/工程图**原点** —— 本模块**不代选**。",
    ],
    "allowed_modes": ["interactive", "reviewed"],
    "source": "original",
    "source_evidence": "本项目自建；依据为出厂类型库反射与官方结构化文档"
                       "（见 `scripts/sw_gtol.py` 的来源块）。"
                       "补的是 `docs/union-gap-triage.md`「真缺」档里的 `gdt` 一条。",
}

if any(c.get("id") == ENTRY["id"] for c in d["capabilities"]):
    print("  已存在")
else:
    d["capabilities"].append(ENTRY)
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已加 geometric_tolerance（stitched）")
import collections
print("  能力数 %d · level %s"
      % (len(d["capabilities"]), dict(collections.Counter(c.get("level") for c in d["capabilities"]))))
