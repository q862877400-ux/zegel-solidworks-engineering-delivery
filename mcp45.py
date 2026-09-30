import re, sys
sys.stdout.reconfigure(encoding="utf-8")
s = open(r"C:\swprojects\sw-skill-fork\mcp-server\server.py", encoding="utf-8").read()
names = sorted(set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', s)))
print("  我们的 MCP 工具总数: %d" % len(names))
kw = ("standard", "part_lib", "library", "lcsc", "toolbox", "jlcfa", "misumi")
std = [n for n in names if any(k in n.lower() for k in kw)]
print("  含「标准件/库」语义的: %s" % (std or "无"))
print()
print("  全部 45 个:")
for i, n in enumerate(names, 1):
    print("   %2d. %s" % (i, n))