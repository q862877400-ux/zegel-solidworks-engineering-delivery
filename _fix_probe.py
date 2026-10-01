"""把 011 探针的「工具→函数」映射**换成权威来源**（分发表），替掉脆弱的调用形态扫描。

⚠ 为什么换：前三版靠扫调用形态，接连漏了三种写法（`function=` 字段 / `from … import` /
  `importlib.import_module` + 别名）⇒ 报出的"被引用 24"其实是 72。
★ 已知事实 53：同一启发式补 ≥3 次就该停。**⇒ 不补第 5 种形态，改用权威清单。**
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_unexposed_functions.py")
t = P.read_text(encoding="utf-8")

old_start = t.index("    # ② 工具 → 函数映射")
old_end = t.index("    # ③ 未暴露")
new_block = '''    # ② 工具 → 函数映射（★ **权威来源**，轮 87 改用）
    # ⚠⚠ 前三版都靠**扫调用形态**，接连漏了三种写法：
    #   ① 只认 `function="…"` 字段 ⇒ 报 20
    #   ② 补 `from scripts.X import …` ⇒ 报 17（含 import 的辅助名）
    #   ③ 补 `importlib.import_module("scripts.X")` + 别名调用 ⇒ 仍只有 24
    #   ⚠ 实际 **72**。根因：`server.py` 有一张**分发表**：
    #        `"op_name": alias.function,`
    #     它**本身就是「哪些函数被暴露」的清单** —— 扫调用形态是在**猜**它。
    # ★ 已知事实 53：同一启发式补 ≥3 次就该停 ⇒ **不再加第 5 种形态**，改用权威清单。
    print()
    print("② 工具到函数的映射（**分发表 = 权威来源** + `tool_specs` 的 `function=`）：")
    srv = (ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
    dispatch = re.findall(r'"(\\w+)":\\s*([A-Za-z_]\\w*)\\.([A-Za-z_]\\w*)\\s*,', srv)
    disp_fns = {fn for _, _, fn in dispatch}
    exposed: set = set(disp_fns)
    print("   ① %-30s 分发表 **%d** 条（落到函数名 **%d** 个）"
          % ("server.py", len(dispatch), len(disp_fns)))
    spec_fns: set = set()
    for p in sorted((ROOT / "mcp-server").glob("tool_specs_*.py")):
        spec_fns |= set(FN.findall(p.read_text(encoding="utf-8", errors="ignore")))
    exposed |= spec_fns
    print("   ② %-30s `function=` 字段 **%d** 个" % ("tool_specs_*.py", len(spec_fns)))
    print("   ⚠ **口径不足声明**：分发表只覆盖 `server.py` 里显式登记的那些；")
    print("     本探针**不再为它补第 5 种形态**（事实 53）—— 这个数是**下界**。")

'''
t = t[:old_start] + new_block + t[old_end:]
# 去掉原来那段 srv/imported 的重复读取
t = t.replace('''    srv = (ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
    # ⚠⚠ **第二版修正**（轮 87 当场）：第一版只用了 `function=` 字段 ⇒ 只数到 20 个，
    #   于是算出「未被引用 759」—— **那是高估**。`server.py` 的工具用
    #   `from scripts.X import a, b, c` 的形式引用函数，**第一版完全没读这个来源**。
    #   ⇒ 补上后才是诚实的数（见下 `server.py` 那一行）。
    imported: set = set()
    for m in re.finditer(r"from scripts\\.[\\w.]+ import ([^\\n#]+)", srv):
        for n in m.group(1).split(","):
            n = n.strip().split(" as ")[0].strip()
            if re.fullmatch(r"[a-z_]\\w*", n or ""):
                imported.add(n)
    exposed |= imported
    print("   ② %-26s `from scripts.X import …` **%2d** 个函数名" % ("server.py", len(imported)))
    srv_mods = set(re.findall(r"from scripts\\.(\\w+) import", srv))
    print("      它 import 的模块 **%d** 个：%s" % (len(srv_mods), sorted(srv_mods)[:6]))
''', '')
t = t.replace('    print("   被工具引用的公开函数              : **%d**" % len(exposed & set(funcs)))',
              '    print("   被工具引用的公开函数              : **%d**（下界）" % len(exposed & set(funcs)))')
P.write_text(t, encoding="utf-8")
import ast
ast.parse(t)
print("  ✓ 已改写并语法通过")
