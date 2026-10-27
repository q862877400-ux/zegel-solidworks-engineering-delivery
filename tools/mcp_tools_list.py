"""★ 一次**真 MCP 握手**取 `tools/list` —— 那是宿主**真正看得见**的那一份工具面。

为什么要有它（一个事实一个家）：
  ★ `tools/measure_lean_catalog.py` 与 `tools/eval_tool_selection.py` 都要「拿真实的工具面」，
    而两处各写一遍 `rpc()` 会被 `scripts/check_repo_uniformity.py` 的
    **跨文件同函数体**判据当场抓出来（实测：`rpc ⇒ eval_tool_selection.py · measure_lean_catalog.py`）
  ⇒ ★ 抽成这一处，两边都**调它**，而不是各自实现一遍 ✓

★ 为什么要走真握手而不是直接 `all_specs()`：
  `all_specs()` 是**声明**；`tools/list` 是**宿主看到的那一份**（含 `server.py` 里
  45 个装饰器工具）★ 两者不是一回事（intake 差异见 `docs/known-facts.md`）✓

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（从 `tools/measure_lean_catalog.py` 的 `rpc()` 抽出，行为逐字不变）
# 文件:   `mcp-server/server.py`（被握手的对象）· `tools/measure_lean_catalog.py`（原实现）
#         `tools/eval_tool_selection.py`（第二个使用者）
# 定位:   ★ 规格 352 P2 —— 评测要的「真实工具面」只许有一个取法。
# 官方依据: MCP 规范 `initialize` → `notifications/initialized` → `tools/list`
#         （stdio 传输，NDJSON；本仓既有实现已用过同一序列）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp-server" / "server.py"


def tools_list(client_name: str = "mcp-tools-list", timeout_s: int = 180) -> list:
    """⇒ `tools/list` 里的工具数组（握手失败时**抛**，不静默回空表）。

    ★ 不静默回空表：空表与「工具面真的是空的」长得一样，那正是本项目反对的形态 ✓
    ★ `timeout_s` 带**白名单内**的单位后缀（`_s`；本仓不认 `_seconds`，
      见 `scripts/check_internal_length_units.py` 的表）✓
    """
    proc = subprocess.Popen(
        [sys.executable or "python", str(SERVER)],
        cwd=str(ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    def rpc(obj: dict) -> dict:
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    try:
        rpc(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": client_name, "version": "0"},
                },
            }
        )
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        proc.stdin.flush()
        result = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    finally:
        try:
            proc.kill()
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            pass
    tools = ((result.get("result") or {}).get("tools")) or []
    if not tools:
        raise RuntimeError("`tools/list` 回了空表（%r）⇒ 这次读数不可用" % (result.get("error"),))
    return tools
