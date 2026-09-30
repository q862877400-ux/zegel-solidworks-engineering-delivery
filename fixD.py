import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\merge_dims2.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        if r.get("disp_id") is not None:
            disp[f][n] = r["disp_id"]''',
'''        raw = r.get("disp_id")
        if raw is not None:
            # ⚑ 普查里 disp_id 混了 str / int，个别值还带前导 "="（如 "=2150"）
            try:
                disp[f][n] = int(str(raw).lstrip("="))
            except (TypeError, ValueError):
                pass''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  disp_id 转换已加固")