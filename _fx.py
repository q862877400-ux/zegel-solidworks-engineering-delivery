import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
old = "TAIL = '''))\n"
new = "TAIL = '''\n"
assert old in s, "未匹配 TAIL 开头"
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("  [ok] TAIL 开头的多余括号已删")
