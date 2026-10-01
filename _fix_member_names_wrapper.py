import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_names.py")
t = P.read_text(encoding="utf-8")
OLD = 'WRAPPER = re.compile(r"\\bget_com_member\\s*\\(\\s*[^,()]+,\\s*[\\"\']([A-Za-z_]\\w*)[\\"\']")'
NEW = ('#: ⚑⚑ 2026-10-01（轮 145）：原正则**只认 `get_com_member`** ⇒\n'
       '#:   ① 它一直**漏掉了 `safe_get_com_member`**（`\\b` 在 `_` 之后不成立）；\n'
       '#:   ② 本轮把 24 处「故意要调」的调用改名成 `call_com_member` 后，\n'
       '#:      那 24 处**也不再被计数**。\n'
       '#:   ★ 根因是同一个：**"有几个取成员的同义词"这件事没有单一真源**。\n'
       '#:   ⇒ 修法：把三种**都**认上（它们都是"取/调 COM 成员"的调用点）。\n'
       '#:   ⚠ 这是**轮 145 的**修法；若将来再加同义词，**这里要同步**。\n'
       'WRAPPER = re.compile(\n'
       '    r"(?:\\bget_com_member|\\bcall_com_member|\\bsafe_get_com_member)'
       '\\s*\\(\\s*[^,()]+,\\s*[\\"\']([A-Za-z_]\\w*)[\\"\']")')
if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok check_member_names.py 的 WRAPPER 已认全三种")
elif "call_com_member" in t and "WRAPPER" in t:
    print("  · 似乎已修过（含 call_com_member）")
else:
    i = t.find("WRAPPER = re.compile")
    print("  ⚠ 锚点不符，实际是：\n    %s" % t[i:i+220])
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
