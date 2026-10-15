import io, sys, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = Path(r"D:\AI\SW\build_complete_index.py").read_text(encoding="utf-8")
# 单独渲染 TAIL 看是否成语法
m = re.search(r"TAIL = '''(.*?)'''", src, re.S)
tail = m.group(1)
out = tail.format(asm="sldworks", mod="scripts/sw_api_sldworks.py")
lines = out.splitlines()
print("TAIL 行数 =", len(lines))
for l in lines[:6]: print("  |", l)
print("  ...")
for l in lines[-12:]: print("  |", l)
import ast
try:
    ast.parse("x = 1\n" + out)
    print("TAIL 语法 OK")
except SyntaxError as e:
    print("TAIL 语法错:", e)
