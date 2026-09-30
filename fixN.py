import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
# 1) 构建器不该再生成 describe（用户要求「不要自创的东西」）
s = s.replace('"call_index",\\n           "describe"]', '"call_index"]')
s = s.replace('__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index",\n           "describe"]',
              '__all__ = ["ASSEMBLY", "FAMILIES", "ARITY", "PROPERTIES", "call_index"]')
# 2) 把 describe 的函数体也从 TAIL 里去掉
i = s.find("def describe(")
if i != -1:
    j = s.find("\n'''", i)
    s = s[:i].rstrip() + "\n" + s[j:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 构建器已不再生成 describe")