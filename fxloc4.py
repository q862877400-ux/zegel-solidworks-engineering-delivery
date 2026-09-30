from pathlib import Path
p = Path(r"D:\AI\SW\locate_sw.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    print("    hwnd=%-9d pid=%-6s %-46s %s" % (h, win32process.GetWindowThreadProcessId(h)[1], t[:44], r))''',
              '''    print("    hwnd=%-9d %-46s %s" % (h, t[:44], r))''')
s = s.replace('cands.append((h, t, win32gui.GetWindowRect(h), name))',
              'cands.append((h, t, win32gui.GetWindowRect(h)))')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  ok")