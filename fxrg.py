from pathlib import Path
p = Path(r"D:\AI\SW\run_guard.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    print("轮 %d: 填「%s」%s" % (rnd, name,
                                ((r.left, r.top),), flush=True)''',
              '''    print("轮 %d: 填「%s」 at (%d,%d)" % (rnd, name, r.left, r.top), flush=True)''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("fixed")