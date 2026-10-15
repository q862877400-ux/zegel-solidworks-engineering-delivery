import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
old = 'LITERAL = re.compile(r"[\\"\']([A-Za-z_]\\w{2,})[\\"\']\\s*[,:}]")'
new = ('# ⚑⚑ ``\\w{2,}`` 要求**至少 3 个字符** ⇒ 单字母成员 `X` / `Y` / `Z`\n'
       '#   与双字母的 `ID` 全被漏掉（本机实测 6 个族因此永远差 14 个成员）。\n'
       'LITERAL = re.compile(r"[\\"\']([A-Za-z_]\\w+)[\\"\']\\s*[,:}]")')
assert old in t, "未匹配 LITERAL 正则"
t = t.replace(old, new, 1)
g.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  [ok] LITERAL 已允许 1~2 字符的成员名")