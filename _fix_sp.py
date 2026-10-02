import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\check_same_parser.py")
lines = p.read_text(encoding="utf-8").splitlines()
n = 0
for i, l in enumerate(lines):
    s = l.rstrip()
    if "\u4e0d\u662f" in s and "\u4e00\u5b9a\u9519" in s and s.strip().startswith("print("):
        lines[i] = ('        print("  \u26a0\u2605 **%d \u4e2a\u6587\u4ef6\u88ab\u4e24\u79cd\u4ee5\u4e0a\u89e3\u6790\u5668\u8bfb** \u2014\u2014 '
                    '\u2605\u2605 \u800c\u90a3**\u4e0d\u662f\u300c\u4e00\u5b9a\u9519\u300d**\uff0c" % bad)')
        n += 1
    elif "\u540c\u4e00\u6587\u4ef6\u88ab\u4e24\u79cd\u89e3\u6790\u5668\u8bfb" in s and s.strip().startswith("print("):
        lines[i] = ('    print("  \u2713 \u6ca1\u6709\u300c\u540c\u4e00\u6587\u4ef6\u88ab\u4e24\u79cd\u89e3\u6790\u5668\u8bfb\u300d\u7684\u60c5\u5f62'
                    '\uff08\u2605 \u6309\u672c\u5224\u636e\uff09")')
        n += 1
t = "\n".join(lines) + "\n"
p.write_text(t, encoding="utf-8")
print("  重写 %d 行" % n)
try:
    compile(t, str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
    print("     " + str(e.text)[:110])
