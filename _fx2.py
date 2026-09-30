import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
lines = p.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines):
    if l.startswith("TAIL = "):
        print("第 %d 行 = %r" % (i+1, l))
        lines[i] = "TAIL = '''"
        print("  改后 = %r" % lines[i])
        break
p.write_text("\n".join(lines) + "\n", encoding="utf-8")
