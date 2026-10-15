from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_index.py")
s = p.read_text(encoding="utf-8")
s = s.replace('def search(keyword: str, brand: str = "", product: str = "", category: str = "",',
              'def search(keyword: str = "", brand: str = "", product: str = "", category: str = "",')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("keyword 已给默认值")