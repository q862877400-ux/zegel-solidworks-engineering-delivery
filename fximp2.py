from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_select.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''def pending_params(w):
    """选型页里还没定的参数下拉。排除只读的「代码」「每页」。"""
    out = []''',
'''def pending_params(w):
    """选型页里还没定的参数下拉。排除只读的「代码」「每页」。"""
    import sw_jlcfa_steps as S          # ★ 同上：本函数内导入
    out = []''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("ok")