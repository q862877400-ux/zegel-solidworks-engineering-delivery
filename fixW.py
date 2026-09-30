import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_automation_knowledge.py")
s = p.read_text(encoding="utf-8")
# 删掉编造的 ERROR_NOTIFICATION 块，换成正确成员
s = re.sub(r'#: 反射确认的「错误通知」开关所在接口与成员.*?\n\}\n\n\n', '', s, flags=re.S)
s = s.replace('    "DIALOG_SUPPRESSORS",\n', '    "DIALOG_SUPPRESSORS",\n    "DIALOG_AND_NOTIFY",\n')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 已移除编造的 ERROR_NOTIFICATION")
# 复核：模块里所有成员名都要在反射里（**归一化后**比）
off = set()
for f in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\S+)\s+(\w+)\s*\(", l.strip())
        if m: off.add(m.group(2))
claimed = set(re.findall(r'get_com_member\([^,]+,\s*"(\w+)"', s))
tbl = set(re.findall(r'^    "(\w+)": \d+,\s*$', s, re.M))
bad = sorted((claimed | tbl) - off)
print("  模块声明的成员查不到反射的: %s" % (bad if bad else "无"))
print("  (set_/get_ 前缀已归一化后比对)")