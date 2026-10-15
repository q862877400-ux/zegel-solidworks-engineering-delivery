"""把协议层返回的 schema 原样打出来（只看，不改）。"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\swprojects\sw-skill-fork")
sys.stdout.reconfigure(encoding="utf-8")

p = subprocess.Popen([sys.executable, str(ROOT / "mcp-server" / "server.py")],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     text=True, encoding="utf-8", errors="replace",
                     cwd=str(ROOT / "mcp-server"))
try:
    def send(m, params, i):
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": m, "params": params}) + "\n")
        p.stdin.flush()

    send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "x", "version": "1"}}, 1)
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    p.stdin.flush()
    send("tools/list", {}, 2)

    tools = None
    dl = time.time() + 30
    while time.time() < dl:
        line = p.stdout.readline()
        if not line:
            break
        try:
            msg = json.loads(line)
        except Exception:      # noqa: BLE001
            continue
        if msg.get("id") == 2 and "result" in msg:
            tools = msg["result"]["tools"]
            break
    want = "solidworks_hole_standards"
    t = next((x for x in (tools or []) if x["name"] == want), None)
    print("  ── %s 的协议层定义 ──" % want)
    print(json.dumps(t, ensure_ascii=False, indent=2)[:1600])
    # 对照：一个 server.py 原生工具
    n2 = "solidworks_collect_model_summary"
    t2 = next((x for x in (tools or []) if x["name"] == n2), None)
    print()
    print("  ── 对照：%s（server.py 原生）──" % n2)
    print(json.dumps(t2, ensure_ascii=False, indent=2)[:900] if t2 else "  （没有这个工具）")
finally:
    try:
        p.stdin.close()
    except Exception:      # noqa: BLE001
        pass
    try:
        p.terminate(); p.wait(timeout=10)
    except Exception:      # noqa: BLE001
        try:
            p.kill()
        except Exception:      # noqa: BLE001
            pass
    print("  （已终止 server）")
