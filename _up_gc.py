import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\gate-classification.json")
t = P.read_text(encoding="utf-8")
old = "⚠ **便携性**：转储在工作区 ⇒ 拿不到时它**自己 SKIP 并 exit 0**。"
new = (
    "⚠ **覆盖范围（轮 107 修正）**：转储**不止一份** —— `enum_values_sldworks.txt`"
    "（sldworks 程序集）与 `reflect\\enum_cosworks.txt`（cosworks 程序集，含 `sws*` 的 Simulation 枚举）。"
    "第一版只读前者 ⇒ **75 条 `sws*` 全归「查不到」**；合并后变 **0 条查不到**。"
    "⚠ **便携性**：转储在工作区 ⇒ 全拿不到时它**自己 SKIP 并 exit 0**。"
)
if "轮 107 修正" not in t:
    assert old in t, "锚点不符"
    P.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("  ok gate-classification 已更新")
else:
    print("  已有")
json.loads(P.read_text(encoding="utf-8"))
print("  JSON OK")
