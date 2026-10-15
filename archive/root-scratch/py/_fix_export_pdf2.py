import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")
OLD = "    success = model.Extension.SaveAs(output_path, 0, 1, pdf_data, errors, warnings)"
NEW = ("    #: ⚠⚠ **第二处缺陷**（2026-10-01 轮 158 真机暴露）：`output_path` 可能是 `Path`，\n"
       "    #: 而 `SaveAs` 要**字符串** ⇒ 抛 `TypeError: must be real number, not WindowsPath`\n"
       "    #: （★ 报错完全看不出是路径类型的问题）。\n"
       "    #: ⇒ 与事实 59（`Path(\"D:\")` 不是盘根）**同族**：**路径类型要在边界上settle一次**。\n"
       "    success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)")
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已修第二处（str(output_path)）")
