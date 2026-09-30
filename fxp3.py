from pathlib import Path
p = Path(r"D:\AI\SW\pick_row.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    hwnd, win = ctl.connect()
    cb = combo_of(win, name)
    return hwnd, win, cb.selected_text().strip()''',
'''    hwnd, win = ctl.connect()
    cb = combo_of(win, name)
    if cb is None:
        # ⚠ 点完选项后控件可能因重排而重建 —— 重试一次再判定
        time.sleep(1.2)
        hwnd, win = ctl.connect()
        cb = combo_of(win, name)
        val = "(控件重建,已不在本屏)" if cb is None else cb.selected_text().strip()
    else:
        val = cb.selected_text().strip()
    return hwnd, win, val''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("加了控件重建容错")