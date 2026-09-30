import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
SRV = r"C:\swprojects\sw-skill-fork\mcp-server\server.py"
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
    r = json.loads(p.stdout.readline())
    tools = r["result"]["tools"]
    payload = json.dumps(r["result"], ensure_ascii=False)
    print("  工具数: %d" % len(tools))
    print("  tools/list 整体 JSON: %d 字节 (%.1f KB)" % (len(payload.encode()), len(payload.encode())/1024))
    print("  估算 token（/4）: 约 %d" % (len(payload.encode())//4))
    print()
    rows = []
    for t in tools:
        desc = t.get("description") or ""
        schema = json.dumps(t.get("inputSchema") or {}, ensure_ascii=False)
        rows.append((len(desc), len(schema), len(desc)+len(schema), t["name"]))
    rows.sort(reverse=True)
    print("  最长的 6 个（描述+schema 字符数）:")
    for d, s, tot, n in rows[:6]:
        print("     %-42s desc=%-5d schema=%-5d" % (n, d, s))
    over = [r for r in rows if r[0] >= 1500]
    print()
    print("  描述 ≥1500 字符的工具: %d 个" % len(over))
finally:
    p.terminate()
    try: p.wait(timeout=5)
    except Exception: p.kill()