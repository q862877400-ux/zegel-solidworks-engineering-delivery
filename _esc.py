import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
# TAIL 里的 {what} / {mod} 需要转义
s = s.replace('def _require(obj, what: str = "对象"):', 'def _require(obj, {{what}}: str = "对象"):')
s = s.replace('raise ValueError(f"{what} 为 None")', 'raise ValueError(f"{{what}} 为 None")')
s = s.replace('# 文件:   {mod} —— 本文件自身', '# 文件:   {{mod}} —— 本文件自身')
p.write_text(s, encoding="utf-8")
print("  [ok] TAIL 占位符已转义")
