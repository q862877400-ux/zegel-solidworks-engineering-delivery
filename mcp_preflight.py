import json, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
SRV = r"C:\swprojects\sw-skill-fork\mcp-server\server.py"
p = subprocess.Popen([sys.executable, SRV], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, encoding="utf-8",
                     cwd=r"C:\swprojects\sw-skill-fork", bufsize=1)
def send(obj):
    p.stdin.write(json.dumps(obj) + "\n"); p.stdin.flush()
try:
    send({"jsonrpc":"2.0","id":1,"method":"initialize",
          "params":{"protocolVersion":"2024-11-05","capabilities":{},
                    "clientInfo":{"name":"preflight","version":"1"}}})
    line = p.stdout.readline()
    r = json.loads(line)
    info = r.get("result",{}).get("serverInfo",{})
    print("  ✓ initialize 成功")
    print("      serverInfo:", info)
    print("      protocolVersion:", r.get("result",{}).get("protocolVersion"))
    send({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
    send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
    line = p.stdout.readline()
    r2 = json.loads(line)
    tools = r2.get("result",{}).get("tools",[])
    print("  ✓ tools/list 成功：%d 个工具" % len(tools))
    for t in tools[:6]:
        print("      %-42s %s" % (t["name"], (t.get("title") or "")[:34]))
    print("      … 共 %d 个" % len(tools))
except Exception as e:
    print("  ✗ 失败:", str(e)[:200])
    err = p.stderr.read(2000) if p.stderr else ""
    if err: print("  stderr:", err[-600:])
finally:
    p.terminate()
    try: p.wait(timeout=5)
    except Exception: p.kill()