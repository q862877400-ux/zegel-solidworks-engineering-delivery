from pathlib import Path
p = Path(r"D:\AI\SW\heal.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''def out_of_budget(what: str) -> bool:
    if BUDGET["steps"] >= BUDGET["max_steps"] or BUDGET["heals"] >= BUDGET["max_heaseline" if False else "max_heals"]:''',
'''def out_of_budget(what: str) -> bool:
    if (BUDGET["steps"] >= BUDGET["max_steps"]
            or BUDGET["heals"] >= BUDGET["max_heals"]):''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("修好预算判断")