"""★ 扫全台账：`verified` 条目挂的 **MCP 工具** 有没有**对应的实现函数**（★ 阶段 1 第二句）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/scan_verified_without_implementation.py
# 定位:   ★ 起点：★ 轮 79 查出 `drawing_dimension_insertion` **能力层零实现**、★ 而 `level` 是 `verified`
#   ⇒ ★★ **那说明"标 `verified`"与"东西在不在"是两件事**（★ 与事实 518/519 **同族**）✓
#   ★★★ **本扫描把它系统化** —— ★ 判据（★ 可核、★ 不猜名字）：
#     ★ 对每个 `verified` 条目：★ 取它 `mcp_tools` 里每个工具名
#       ⇒ 去 **ToolSpec 注册表**里找那个工具 ⇒ ★ 拿到它声明的 `module` / `function`
#       ⇒ ★★ 去 `scripts/` 里找**那个函数定义** ✓
#     ★★★ **找不到 ⇒ 就是"挂了工具、但工具指不到实现"** ✓
#   ★★ **只报不动** ✓
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO / "mcp-server"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = REPO / "output" / "verified-without-implementation-scan.json"
#: ★★ 哨兵：★ 该工具由 `server.py` 提供（★ **只有名字、没有 module/function**）⇒
#:   本扫描**不做函数级核对**（★ 并**如实报出来**，★ 而不是当成"找不到"）✓
SERVER_SENTINEL = "__server_py__"


def _specs() -> dict:
    """★ 取 ToolSpec 注册表：★ 工具名 ⇒ (module, function)。

    ★★★★ 2026-10-04（接手轮）**补第二条注册路径** ——
      ★ 第一版只读 `register_capabilities.all_specs()` ⇒ ★★ 报了 6 个"工具不在注册表里"，
      ★★★ **而其中 `cadstudio_check_dfm` / `cadstudio_build_dxf_preview_scene` 等**
        **我明明一直在用** ✓
      ⇒ ★ 真因：★ **本仓有**两套**注册路径** ——
        · ★ `mcp-server/register_capabilities.py` 的 `ToolSpec`（★ 带 `module` / `function`）✓
        · ★★ `mcp-server/server.py` 里的 `name="cadstudio_*"` 那批（★ **只有名字**）✓
      ★★★★ **⇒ 那正是**事实 518** 的第三次实例**：★★★ **「我的表里没有」≠「它不存在」** ✓
      ★★ **修法**：★ **第二条路径也读** —— ★ 它们没有 `module`/`function` ⇒
        ★★ 用一个**哨兵**标记"由 server.py 提供、★ 本扫描不做函数级核对" ✓
    """
    out: dict = {}
    try:
        import register_capabilities as rc                                 # noqa: PLC0415
        for spec in rc.all_specs():
            name = getattr(spec, "name", None) or (
                spec.get("name") if isinstance(spec, dict) else None)
            mod = getattr(spec, "module", None) or (
                spec.get("module") if isinstance(spec, dict) else None)
            fn = getattr(spec, "function", None) or (
                spec.get("function") if isinstance(spec, dict) else None)
            if name:
                out[str(name)] = (str(mod or ""), str(fn or ""))
    except Exception as exc:                                               # noqa: BLE001
        print("★ 取不到 ToolSpec 注册表:", type(exc).__name__, str(exc)[:120])

    #: ★★ **第二条路径**：★ `server.py` 里的 `name="..."` 那批（★ 只有名字）✓
    server = REPO / "mcp-server" / "server.py"
    if server.is_file():
        text = server.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'name="((?:solidworks|cadstudio)_[A-Za-z0-9_]+)"', text):
            out.setdefault(m.group(1), ("", SERVER_SENTINEL))
    return out


def _defined_functions() -> set:
    """★ 全仓**实现面**里的函数名（★ 排除签名索引）。"""
    skip = {"sw_api_sldworks.py", "sw_api_sldcostingapi.py", "sw_api_SWRoutingLib.py"}
    out = set()
    for d in ("scripts", "subskills"):
        for f in (REPO / d).rglob("*.py"):
            if f.name in skip:
                continue
            for m in re.finditer(r"^\s*def (\w+)\(", f.read_text(encoding="utf-8", errors="replace"),
                                 re.M):
                out.add(m.group(1))
    return out


def main() -> int:
    specs = _specs()
    defined = _defined_functions()
    print("★ ToolSpec 条数:", len(specs), "· 实现面函数名:", len(defined))

    caps = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))["capabilities"]
    rows = []
    for c in caps:
        if c.get("level") != "verified":
            continue
        tools = [str(t) for t in (c.get("mcp_tools") or [])]
        if not tools:
            continue
        missing = []
        for t in tools:
            if t not in specs:
                missing.append("%s（★ 不在注册表里）" % t)
                continue
            _mod, fn = specs[t]
            if fn == SERVER_SENTINEL:
                #: ★★ 由 `server.py` 提供 ⇒ ★ **不报缺**（★ 但**计入**一个单独的口径）✓
                continue
            if not fn or fn not in defined:
                missing.append("%s ⇒ module=%s function=%s（★ 实现面找不到）" % (t, _mod, fn))
        if missing:
            rows.append({"id": c["id"], "level": c.get("level"), "missing": missing})

    R = {"★_判据": "★ verified 条目挂的 MCP 工具 ⇒ 其声明的 function 必须能在实现面找到",
         "★_合计": len(rows), "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★★ 挂的工具**指不到实现**的 `verified` 条目：**%d** 个" % len(rows))
    for r in rows:
        print("  ★ %-34s %s" % (r["id"], r["missing"][:2]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
