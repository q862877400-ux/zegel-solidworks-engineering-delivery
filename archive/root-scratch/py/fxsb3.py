from pathlib import Path
p = Path(r"D:\AI\SW\sb3.py")
s = p.read_text(encoding="utf-8")
s = s.replace('    return (cr.left + cx, cr.top + cy), {"boxes": boxes, "pane": pane.size}',
              '    return (cr.left + cx, cr.top + cy), {"boxes": boxes, "pane_w": pane.size[0], "pane_h": pane.size[1]}')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("fixed")