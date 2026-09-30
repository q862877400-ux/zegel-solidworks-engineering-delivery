import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
s = T.read_text(encoding="utf-8")
old = re.search(r"REFLECTIONS = \[.*?\n\]", s, re.S).group(0)
new = ('''#: ⚑⚑ **自动发现**，不写死 —— 写死的清单每加一个程序集就会漏一次，
#:   而漏了的表现是「测试报某个成员不在官方反射里」，看起来像数据错、实则是清单旧。
#:   本轮已经因此栽了两次（漏 swmotionstudy、漏 swdimxpert 等 5 个）。
REFLECT_DIR = Path(r"D:\\AI\\SW\\_raw\\reflect")
REFLECTIONS = sorted(REFLECT_DIR.glob("iface_*.txt")) if REFLECT_DIR.is_dir() else []''')
s = s.replace(old, new, 1)
T.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 门禁的反射清单改为自动发现")