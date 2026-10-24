"""J 维度观测器：运行装配链现状（只读）。

记录：`mcp-server/server.py` 的装配入口与注册调用、`@mcp.tool` 装饰器数量、
`sw_connect.py` 的连接/护栏/单实例相关符号、`mcp.json` 的服务开关。
不启动服务、不连 SolidWorks。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def grep_count(path: pathlib.Path, pattern: str) -> int:
    if not path.exists():
        return -1
    return len(re.findall(pattern, path.read_text(encoding="utf-8", errors="replace")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    server = ROOT / "mcp-server" / "server.py"
    swconn = ROOT / "scripts" / "sw_connect.py"
    mcpjson = ROOT / "mcp.json"

    data: dict = {}
    if server.exists():
        src = server.read_text(encoding="utf-8", errors="replace")
        data["server"] = {
            "lines": len(src.splitlines()),
            "decorator_tool_count": len(re.findall(r"@mcp\.tool\b", src)),
            "register_capabilities_calls": len(re.findall(r"register_capabilities\(", src)),
            "has_fastmcp": "FastMCP" in src,
            "run_hints": sorted(set(re.findall(r'"([a-z_]+)Hint"', src))),
        }
    if swconn.exists():
        src = swconn.read_text(encoding="utf-8", errors="replace")
        data["sw_connect"] = {
            "lines": len(src.splitlines()),
            "mutex_hits": grep_count(swconn, r"Mutex|mutex|SingleInstance|single_instance"),
            "command_in_progress": src.count("CommandInProgress"),
            "timeout_hits": len(re.findall(r"timeout", src, re.I)),
            "dispatch_ex": src.count("Dispatch"),
            "has_mm_helper": bool(re.search(r"^def mm\(", src, re.M)),
        }
    if mcpjson.exists():
        try:
            cfg = json.loads(mcpjson.read_text(encoding="utf-8"))
            servers = cfg.get("mcpServers") or cfg.get("servers") or {}
            data["mcp_json"] = {
                "top_keys": sorted(cfg.keys()),
                "servers": {k: (v.get("disabled", False) if isinstance(v, dict) else None)
                            for k, v in servers.items()},
                "servers_count": len(servers),
            }
        except Exception as exc:  # noqa: BLE001
            data["mcp_json"] = {"error": f"{type(exc).__name__}: {exc}"}

    # 护栏与单实例脚本
    for name in ("sw_guard.py", "reclaim_solidworks.py"):
        p = ROOT / "tools" / name
        data.setdefault("tools_present", {})[name] = p.exists()

    print(json.dumps(data, ensure_ascii=False, indent=2))

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())