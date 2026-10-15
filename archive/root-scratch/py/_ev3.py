import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
s = p.read_text(encoding="utf-8")
print("索引里 add_ 开头成员 =", len(re.findall(r"'add_\w+':\s*\d+", s)))
print("索引里 remove_ 开头  =", len(re.findall(r"'remove_\w+':\s*\d+", s)))
m = re.search(r"'DSldWorksEvents_Event': \{\n(.*?)\n    \},", s, re.S)
print("DSldWorksEvents_Event 登记 =", len(re.findall(r"'(\w+)':", m.group(1))) if m else 0)
print("样例:", re.findall(r"'(\w+)':", m.group(1))[:4] if m else [])
