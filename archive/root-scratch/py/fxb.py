from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_batch.py")
s = p.read_text(encoding="utf-8")
s = s.replace("import sw_jlcfa_search as SR",
              "import sw_jlcfa_fill as FILL\nimport sw_jlcfa_search as SR")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已加 FILL 导入")