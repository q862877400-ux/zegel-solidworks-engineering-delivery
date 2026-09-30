import sys, ast, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("md", r"D:\AI\SW\merge_dims2.py")
md = importlib.util.module_from_spec(spec); sys.modules["md"] = md
try: spec.loader.exec_module(md)
except SystemExit: pass
d = md.DOC
print("  DOC 行数:", len(d.splitlines()), " 字符数:", len(d))
try:
    ast.parse(d); print("  DOC 单独作代码解析: 语法 OK（说明它是纯注释）")
except SyntaxError as e:
    print("  DOC 有语法问题:", e)
    ls = d.splitlines(); a = max(0, e.lineno-3)
    for i in range(a, min(e.lineno+2, len(ls))):
        print("    %s%3d| %s" % (">>" if i+1==e.lineno else "  ", i+1, ls[i][:96]))
# 关键：DOC 里有没有未转义的花括号
import re
for i, l in enumerate(d.splitlines(), 1):
    if "{" in l or "}" in l:
        print("  DOC:%d 含花括号 -> %s" % (i, l[:90]))