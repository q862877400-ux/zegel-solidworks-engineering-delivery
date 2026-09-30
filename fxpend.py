from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_select.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''            if t in ("代码", "每页"):
                continue
            items = c.texts()
            cur = c.selected_text().strip()
            if items and len(items) > 1 and cur != items[-1]:
                out.append((t, c, items, cur))''',
'''            if t == "每页":          # 分页，不是选型参数
                continue
            items = c.texts()
            cur = c.selected_text().strip()
            # ⚠「代码」**也是必填下拉**（实测：只剩它时进度 84% → 100%），
            #   不能当只读排除 —— 我先前排除了它，导致永远到不了 100%。
            # 判据：还停在**第 0 项**（占位「请选择」）就算待填。
            if items and len(items) > 1 and cur == items[0]:
                out.append((t, c, items, cur))''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("pending 判定已修：代码纳入，判据=停在第0项")