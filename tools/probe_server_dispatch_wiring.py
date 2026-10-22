r"""@brief 探针：`server.py` **声明的工具** vs **协议层实际给出的** —— 集合比对。

## 为什么这是第四种「死守卫」形态里最要紧的一处
`053`~`056` 扫了**常量** · **函数** · **注册表**。
★ 还剩一处：**`server.py` 自己声明的工具**（45 个左右）——
若某个 `name="solidworks_xxx"` **声明了却没进协议层**，那它就是**发不出去的工具**。
⚠ 反之（协议层有、源码里找不到声明）则说明**有别的注册路径**没被算进来。

## 判法（**纯集合比对** —— 与 `056` 同类，无解释空间）
```
① 从 server.py 里正则取全部 `name="<tool>"` 字面量
② 起 server（stdio）、发 `initialize` + `tools/list`，取协议层工具名
③ 两边做差 ⇒ 两个方向各自的可疑
```
⚠⚠ **安全**：**只发 `initialize` 与 `tools/list`，一次工具都不调** ⇒ **不碰 COM**
（已知事实 24：多个进程抢同一 COM 会死锁）。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_server_dispatch_wiring.py
# 定位:   给 Spec Kit `057` 取证：`server.py` 声明的工具与协议层是否一一对上。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.stdout.reconfigure(encoding="utf-8")

SERVER = ROOT / "mcp-server" / "server.py"
NAME_LITERAL = re.compile(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')


def protocol_tools(timeout: float = 40.0):
    """起 server、只发 `initialize` + `tools/list`，返回工具名集合（**不碰 COM**）。"""
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(SERVER.parent),
    )
    try:

        def send(method, params, i):
            proc.stdin.write(
                json.dumps(
                    {"jsonrpc": "2.0", "id": i, "method": method, "params": params}
                )
                + "\n"
            )
            proc.stdin.flush()

        send(
            "initialize",
            {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "probe", "version": "1"},
            },
            1,
        )
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        send("tools/list", {}, 2)
        dl = time.time() + timeout
        while time.time() < dl:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if msg.get("id") == 2 and "result" in msg:
                return {t["name"] for t in msg["result"].get("tools") or []}
        return None
    finally:
        try:
            proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            try:
                proc.kill()
            except Exception:  # noqa: BLE001
                pass


def main() -> int:
    declared = set(NAME_LITERAL.findall(SERVER.read_text(encoding="utf-8")))
    live = protocol_tools()
    print('  server.py 里 `name="…"` 字面量: **%d** 个' % len(declared))
    if live is None:
        print("  ⚠ 没在超时内拿到 `tools/list`（环境问题）")
        return 1
    print("  协议层实际给出的: **%d** 个" % len(live))
    print()

    declared_not_live = sorted(declared - live)
    live_not_declared = sorted(live - declared)
    print("  ★ **声明了、却没进协议层**（发不出去的工具）: %d" % len(declared_not_live))
    for x in declared_not_live:
        print("      %s" % x)
    print()
    print(
        "  ★ **协议层有、server.py 里找不到声明**（别的注册路径）: %d"
        % len(live_not_declared)
    )
    for x in live_not_declared[:50]:
        print("      %s" % x)
    if len(live_not_declared) > 50:
        print("      …（还有 %d 个）" % (len(live_not_declared) - 50))
    print()
    print("  参考：`register_capabilities.all_specs()` 贡献 **41** 条（batch1–10）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
