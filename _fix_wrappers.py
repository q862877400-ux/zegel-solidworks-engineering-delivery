import ast
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
P = ROOT / "scripts" / "audit_call_arity.py"
t = P.read_text(encoding="utf-8")
OLD = 'WRAPPERS = {"_safe_member", "get_com_member", "get_com_member"}'
NEW = ('#: ⚑⚑ 2026-10-01（轮 145）：原集合是 `{"_safe_member", "get_com_member", "get_com_member"}`\n'
       '#:   ——★ **第三项是重复的**（显然是 `safe_get_com_member` 写错了）\n'
       '#:   ⇒ **`safe_get_com_member` 的调用点一直被漏计**（与 `check_member_names.py` 同一个根因：\n'
       '#:      "有几个取成员的同义词"没有单一真源）。\n'
       '#:   ⚑ 本轮再加 `call_com_member`（轮 145 为"故意要调"的站点新起的名字）。\n'
       '#:   ⇒ 这三种**都是**"取/调 COM 成员"的调用点，都要算。\n'
       'WRAPPERS = {"_safe_member", "get_com_member", "safe_get_com_member", "call_com_member"}')
assert OLD in t, "WRAPPERS 锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok WRAPPERS 已修（去重复 + 加 call_com_member）")

#: 重跑审计，看总数变化
r = subprocess.run([sys.executable, str(ROOT / "scripts" / "audit_call_arity.py"),
                    str(ROOT / "scripts"), *(str(x) for x in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"))],
                   capture_output=True, text=True, encoding="utf-8", errors="replace",
                   cwd=str(ROOT))
out = (r.stdout or "") + (r.stderr or "")
for line in out.splitlines()[:8]:
    print("     %s" % line.strip()[:96])
