"""按「权威来源」重算暴露面：server.py 的分发表 + tool_specs 的 function= 字段。

⚠ 为什么要换来源：前几版靠**扫调用形态**，接连漏了三种写法
   （`function=` 字段 / `from … import` / `importlib.import_module` + 别名）。
   ★ 已知事实 53：同一个启发式补 ≥3 次就该停。
   ⇒ 这次不补，改用**权威来源** —— `server.py` 里那张**分发表本身就是"哪些函数被暴露"的清单**。
"""
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")

# ① 分发表：  "op_name": module.function,
disp = re.findall(r'"([\w]+)":\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*,', srv)
print("① server.py 分发表条目：**%d** 条" % len(disp))
by_mod = {}
for op, alias, fn in disp:
    by_mod.setdefault(alias, set()).add(fn)
for a in sorted(by_mod):
    print("     %-16s %2d 个函数" % (a, len(by_mod[a])))

# ② tool_specs 的 function= 字段
bat = set()
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    bat |= set(re.findall(r'function="([\w]+)"', p.read_text(encoding="utf-8", errors="ignore")))
print()
print("② tool_specs 的 `function=` 字段：**%d** 个" % len(bat))

# ③ 我们的公开函数
DEF = re.compile(r"^def ([a-z_]\w*)\(", re.M)
funcs = {}
for p in sorted((R / "scripts").glob("sw_*.py")):
    for fn in DEF.findall(p.read_text(encoding="utf-8", errors="ignore")):
        funcs.setdefault(fn, p.name)

disp_fns = {fn for _, _, fn in disp}
exposed = (disp_fns | bat) & set(funcs)
print()
print("③ 合并后**被引用的公开函数 = %d**（前三版分别报 20 / 17 / 24）" % len(exposed))
print("   仅分发表就贡献：%d 个（其中落在我们公开函数上的 %d 个）"
      % (len(disp_fns), len(disp_fns & set(funcs))))
print()
print("   ⚠ **仍不完整**（本轮不再补）：分发表只覆盖 `server.py` 里显式登记的那些；")
print("     本探针**不再给判据加第 5 种形态** —— 按事实 53 停下，如实报告口径不足。")
