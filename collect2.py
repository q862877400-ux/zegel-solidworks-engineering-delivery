import re, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
PROJ = {
 "Eduardof0nt":    r"C:\swprojects\Eduardof0nt",
 "andrewbartels1": r"C:\swprojects\andrewbartels1",
 "vespo92":        r"C:\swprojects\SolidworksMCP-TS",
 "Slacker-LLC":    r"C:\swprojects\Slacker-LLC",
 "我们(上游)":      r"C:\swprojects\sw-skill-fork\mcp-server",
}
def names(path):
    out = set()
    for f in Path(path).rglob("*"):
        if not f.is_file() or f.suffix not in (".py",".ts",".cs"): continue
        if any(x in str(f) for x in (".venv","node_modules","site-packages",".git","__pycache__","dist","build",".ci")): continue
        try: t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        # ① @mcp.tool(name="x") / @mcp.tool(\n name="x")
        out |= set(re.findall(r'@mcp\.tool\([^)]*?name\s*=\s*["\']([a-z][\w]*)["\']', t))
        # ② @mcp.tool() 紧跟 def/async def  → 取函数名
        out |= set(re.findall(r'@mcp\.tool\([^)]*\)\s*\n\s*(?:async\s+)?def\s+([a-z]\w+)', t))
        # ③ 其它框架
        out |= set(re.findall(r'@tool\(\s*["\']([a-z][\w]*)["\']', t))
        out |= set(re.findall(r'\{\s*name:\s*["\']([a-z][\w]*)["\']', t))
    return out
res = {}
for k, p in PROJ.items():
    n = sorted(names(p)); res[k] = n
    print("%-16s %4d 个工具" % (k, len(n)))
Path(r"D:\AI\SW\toolsets.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
u = set()
for v in res.values(): u |= set(v)
print()
print("并集 %d 个不同工具名" % len(u))
print()
print("=== 各家相对「其余四家的并集」独有多少 ===")
for k, v in res.items():
    others = set()
    for k2, v2 in res.items():
        if k2 != k: others |= set(v2)
    uniq = sorted(set(v) - others)
    print("  %-16s 独有 %3d 个: %s" % (k, len(uniq), ", ".join(uniq[:8]) + (" …" if len(uniq)>8 else "")))