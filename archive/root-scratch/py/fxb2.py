from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_batch.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    def _code_ok(ww) -> bool:
        line = FILL.model_line(ww)
        key = code.split("-")[0][:8]
        return bool(line) and key.lower() in line.lower()''',
'''    def _code_ok(ww) -> bool:
        return FILL.code_present(ww, code)''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("batch 校验改用 code_present")