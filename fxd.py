from pathlib import Path
p = Path(r"D:\AI\SW\demo_alu.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''            if c.element_info.control_type == "Edit" and c.rectangle().top < 260 \\
                    and c.rectangle().left > 1500:
                sb = c
                break''',
'''            if c.element_info.control_type != "Edit":
                continue
            r = c.rectangle()
            # 搜索框：无标题、位于插件顶部（top<300）、横向较宽
            if r.top < 300 and r.left > 1400 and r.width() > 200:
                sb = c
                break''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("搜索框判定已修正：top<300 & left>1400 & width>200")