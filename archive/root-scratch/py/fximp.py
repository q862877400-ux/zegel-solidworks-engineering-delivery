from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_select.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''def fill_to_100(h, w, max_rounds=12, pick=1):
    """把选型页参数填到 100%。返回 (h, w, 进度)。"""
    import sw_jlcfa_locate as L''',
'''def fill_to_100(h, w, max_rounds=12, pick=1):
    """把选型页参数填到 100%。返回 (h, w, 进度)。"""
    import sw_jlcfa_locate as L
    import sw_jlcfa_steps as S          # ★ 本文件的旧版没导入 steps''')
s = s.replace('''def select_index(h, w, combo, items, idx):
    """展开下拉并点第 ``idx`` 项（idx 按 combo.texts() 顺序，0 常是占位）。"""
    combo.click_input()''',
'''def select_index(h, w, combo, items, idx):
    """展开下拉并点第 ``idx`` 项（idx 按 combo.texts() 顺序，0 常是占位）。"""
    import sw_jlcfa_steps as S
    combo.click_input()''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已补 steps 导入")