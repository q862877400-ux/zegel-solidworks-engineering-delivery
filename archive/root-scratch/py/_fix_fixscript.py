import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\_fix_get_com_member.py")
t = P.read_text(encoding="utf-8")
OLD = 'print("  ok get_com_member 已修（DISP_E_PARAMNOTOPTIONAL 纳入"返回成员不调用"）")'
NEW = 'print("  ok get_com_member 已修（DISP_E_PARAMNOTOPTIONAL 纳入：返回成员、不调用）")'
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 修脚本已修（用「」代替嵌套引号）")
