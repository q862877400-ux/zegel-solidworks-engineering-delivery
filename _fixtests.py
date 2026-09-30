import re, sys, io
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests")
# 契约测试里从反射数 arity 的那几处，统一排除 by-ref 出参
PATS = [
 (r'len\(\[a for a in args\.split\(","\) if a\.strip\(\)\]\)',
  'len([a for a in args.split(",") if a.strip() and not a.strip().endswith("&")])'),
 (r'len\(\[a for a in line\.split\(","\) if a\.strip\(\)\]\)',
  'len([a for a in line.split(",") if a.strip() and not a.strip().endswith("&")])'),
]
n = 0
for p in sorted(T.glob("test_*.py")):
    s = p.read_text(encoding="utf-8")
    o = s
    for pat, rep in PATS:
        s = re.sub(pat, rep, s)
    if s != o:
        p.write_text(s, encoding="utf-8")
        print("  [ok]", p.name)
        n += 1
print("改了", n, "个测试文件")
