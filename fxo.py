from pathlib import Path
p = Path(r"D:\AI\SW\opt1.py")
s = p.read_text(encoding="utf-8")
# Edit 只在未到 100% 时才动
s = s.replace('''    pane.refresh()
    for nm, (ed, r) in list(pane.edits.items()):''',
'''    pane.refresh()
    # ⚠ 已经 100% 时**不要**再动 Edit —— 改写已提交的值会触发插件校验失败
    for nm, (ed, r) in (list(pane.edits.items()) if pane.pct() != 100 else []):''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("修正：仅未 100% 时才动 Edit")