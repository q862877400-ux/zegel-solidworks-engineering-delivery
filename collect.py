import re, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
PROJ = {
 "Eduardof0nt":      r"C:\swprojects\Eduardof0nt",
 "andrewbartels1":   r"C:\swprojects\andrewbartels1",
 "vespo92":          r"C:\swprojects\SolidworksMCP-TS",
 "Slacker-LLC":      r"C:\swprojects\Slacker-LLC",
 "我们(上游)":        r"C:\swprojects\sw-skill-fork\mcp-server",
}
def names(path):
    out = set()
    for f in Path(path).rglob("*"):
        if not f.is_file() or f.suffix not in (".py",".ts",".cs"): continue
        if any(x in str(f) for x in (".venv","node_modules","site-packages",".git","__pycache__","/test","\\test","dist","build")): continue
        try: t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        out |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', t))
        out |= set(re.findall(r'@mcp\.tool\s*\n\s*(?:async\s+)?def\s+([a-z]\w+)', t))
        out |= set(re.findall(r'\{\s*name:\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
        out |= set(re.findall(r'@tool\(\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
        out |= set(re.findall(r'name="([a-z][a-z0-9_]{3,})"\s*,?\s*\n\s*title=', t))
        out |= set(re.findall(r"name='([a-z][a-z0-9_]{3,})'\s*,?\s*\n\s*title=", t))
    return out
res = {}
for k, p in PROJ.items():
    n = names(p)
    res[k] = sorted(n)
    print("%-16s %4d 个工具" % (k, len(n)))
Path(r"D:\AI\SW\toolsets.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print()
print("已存 D:\\AI\\SW\\toolsets.json")
# 并集
u = set()
for v in res.values(): u |= set(v)
print("四家 + 我们 的并集: %d 个不同工具名" % len(u))