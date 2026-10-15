"""量 SolidWorks MCP 的「工具描述长度」，一次打印三个口径的对照。

用途
    `~/.dsh/profiles/web/cordis.patch.yml` 里 preset-solidworks 的注释写了一个实测数字
    （「工具描述最长 102 字符」）。那个数字换源或改工具后会过期，而且**不同口径量出不同的数**
    —— 102 是 `tools/list` 返回的 `description` 字段（注入 prompt 的就是这个），
    303 是 `server.py` 第 1 行的模块 docstring（跨行三引号块，**不注入 prompt**）。
    谁对那个数字有疑问就跑这个脚本，一次看到三个口径分别量的是什么、各是多少。
    它是**草稿工具**，故意不接进技能仓的门禁（`check_union_conventions.py`）。

COM 安全
    **不碰 SolidWorks。** 它把 MCP server 当子进程起起来，只发 initialize + tools/list
    两个只读协议调用，然后立刻终止。`server.py` 的 `_coinitialize()` 只在 `_run_locked()`
    里被调 —— 也就是**只有真正调用工具时**才初始化 COM，这两个协议调用不进那条路径。
    实测：跑前跑后 `Get-Process SLDWORKS` 均为 1；且用 PID 比对确认脚本自身无子进程残留。
    ⚠ 但它读的是 `C:/swprojects/sw-skill-fork/mcp-server/server.py` —— 换了路径要改下面 SRV。
"""
import ast, io, json, re, subprocess, sys, tokenize
sys.stdout.reconfigure(encoding="utf-8")
SRV = r"C:\swprojects\sw-skill-fork\mcp-server\server.py"
src = open(SRV, encoding="utf-8").read()

# ── 口径 A：工具描述（MCP 协议真正注入 prompt 的那个）──
p = subprocess.Popen([sys.executable, SRV], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8",
                     cwd=r"C:\swprojects\sw-skill-fork", bufsize=1)
def send(o):
    p.stdin.write(json.dumps(o) + "\n"); p.stdin.flush()
try:
    send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05",
          "capabilities":{},"clientInfo":{"name":"m","version":"1"}}})
    p.stdout.readline()
    send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
    send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
    tools = json.loads(p.stdout.readline())["result"]["tools"]
finally:
    p.terminate()
    try: p.wait(timeout=5)
    except Exception: p.kill()

desc = sorted(((len(t.get("description") or ""), t["name"]) for t in tools), reverse=True)
print("口径 A｜工具描述（tools/list 实测）")
print("   最长 %d 字符 → %s" % desc[0])
for n, nm in desc[:3]: print("      %4d  %s" % (n, nm))
print()

# ── 口径 B：server.py 里所有三引号字符串块（含 docstring / 注释性文本）──
blocks = []
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if node.end_lineno and node.end_lineno > node.lineno:   # 跨行 = 三引号块
            blocks.append((len(node.value), node.lineno))
blocks.sort(reverse=True)
print("口径 B｜server.py 里的跨行三引号块（AST 实测）")
print("   共 %d 个；最长 %d 字符（第 %d 行起）" % (len(blocks), blocks[0][0], blocks[0][1]))
for n, ln in blocks[:3]: print("      %4d 字符  L%d" % (n, ln))
print()

# ── 口径 C：文件里最长的三引号块（正则，含未解析成 AST 常量的）──
raw = [(len(m.group(1)), src[:m.start()].count("\n")+1)
       for m in re.finditer(r'"""(.*?)"""', src, re.S)]
raw.sort(reverse=True)
print("口径 C｜正则扫 \"\"\"...\"\"\"（最宽口径）")
print("   共 %d 个；最长 %d 字符（第 %d 行起）" % (len(raw), raw[0][0], raw[0][1]))
print()
print("⇒ 三个口径分别是 %d / %d / %d" % (desc[0][0], blocks[0][0], raw[0][0]))