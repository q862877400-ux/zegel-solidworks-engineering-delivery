import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
s = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
mods = sorted(set(re.findall(r'from\s+(scripts[\w.]*)\s+import', s)) | set(re.findall(r'import\s+(scripts[\w.]*)', s)))
print("  引用的自家模块 %d 个:" % len(mods))
for m in mods: print("     %s" % m)
# 也看动态导入
dyn = sorted(set(re.findall(r'_load_automation_modules|import_module\(["\']([^"\']+)', s)))
print("  动态导入: %s" % dyn[:6])