import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
s = T.read_text(encoding="utf-8")
s = s.replace('REFLECT_DIR = Path(r"D:\\AI\\SW\\_raw\\reflect")',
              '# ⚑ 从 _raw 根找 —— 反射清单**散在两个目录**：大部分在 _raw\\reflect\\\，\n'
              '#   最大的 sldworks 在它的兄弟目录 _raw\\reflect_sldworks\\。\n'
              '#   只扫其中一个都会漏（本轮实测漏掉 15,297 条）。\n'
              'REFLECT_DIR = Path(r"D:\\AI\\SW\\_raw")')
T.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 反射搜索根改为 _raw")