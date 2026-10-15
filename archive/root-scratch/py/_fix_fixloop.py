"""★ 一次性：修 _fix_loop.py 的最后一行（引号），然后跑它。"""
from pathlib import Path

p = Path(r"D:\AI\SW\_fix_loop.py")
s = p.read_text(encoding="utf-8")
bad_start = s.index('print("普查循环已重写')
bad_end = s.index("\n", bad_start)
s = s[:bad_start] + 'print("普查循环已重写（★ 修掉「每组只处理最后一个」的缩进错）")' + s[bad_end:]
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("_fix_loop.py 语法已修")
