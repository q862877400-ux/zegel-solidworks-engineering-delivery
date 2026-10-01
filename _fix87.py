import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")

# ① importlib 动态导入的模块 → 取别名
pairs = re.findall(r'(\w+)\s*=\s*importlib\.import_module\("scripts\.(\w+)"\)', srv)
print("① importlib 动态导入（别名 → 模块）%d 个:" % len(pairs))
for alias, mod in pairs:
    print("     %-14s → scripts/%s.py" % (alias, mod))

# ② 用别名调用的函数
used = set()
for alias, mod in pairs:
    used |= set(re.findall(r"\b%s\.(\w+)\s*\(" % re.escape(alias), srv))
print()
print("② 通过这些别名调用的函数：**%d** 个" % len(used))

# ③ 与上轮探针的口径合并
DEF = re.compile(r"^def ([a-z_]\w*)\(", re.M)
funcs = {}
for p in sorted((R / "scripts").glob("sw_*.py")):
    for fn in DEF.findall(p.read_text(encoding="utf-8", errors="ignore")):
        funcs.setdefault(fn, p.name)
imp = set()
for m in re.finditer(r"from scripts\.[\w.]+ import ([^\n#]+)", srv):
    for n in m.group(1).split(","):
        n = n.strip().split(" as ")[0].strip()
        if re.fullmatch(r"[a-z_]\w*", n or ""):
            imp.add(n)
bat = set()
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    t = p.read_text(encoding="utf-8", errors="ignore")
    bat |= set(re.findall(r'function="([\w]+)"', t)) | set(re.findall(r'module="([\w]+)"', t))
exposed = (used | imp | bat) & set(funcs)
print()
print("③ 合并三个来源后，**被工具引用的公开函数 = %d**（上轮报的是 24）" % len(exposed))
print("   ⇒ 上轮**低估了 %d 个** —— 因为漏了 `importlib.import_module` 这个来源" % (len(exposed) - 24))
print()
print("   新增被认定已暴露的（前 30）:")
for f in sorted(exposed)[:30]:
    print("      %-40s (%s)" % (f, funcs[f]))
