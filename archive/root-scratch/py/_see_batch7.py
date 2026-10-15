import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch7.py")
t = p.read_text(encoding="utf-8")
print("  batch7 工具名:")
for m in re.finditer(r'name\s*=\s*"([\w]+)"', t):
    print("    %s" % m.group(1))
print()
print("  引用到的模块/函数:")
for m in re.finditer(r'(?m)^\s*(module|function)\s*=\s*"([^"]+)"', t):
    print("    %s = %s" % (m.group(1), m.group(2)))
print()
print("  提到 capture 的行:")
for i, l in enumerate(t.splitlines(), 1):
    if "capture" in l:
        print("    L%-4d %s" % (i, l.strip()[:96]))
