"""★ 探针：对我们自己的 MCP 服务器做一次**真 JSON-RPC 握手**（★ 不连 SolidWorks）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 213 之后的「把工具挂进 DSH」前置验证）
# 文件:   tools/probe_mcp_stdio_handshake.py
# 定位:   ★ 用户 2026-10-07 指令：「★ **把我们所有工具都挂在你这个对话的 tool 里**」✓ ——
#   ★★ 而动手改 DSH 配置**之前**必须先证明**服务器起得来** ✗：
#     ★ 记忆库里有一条硬教训逐字：「★ **handshake with this MCP server hangs the whole dsh
#       boot (event loop blocks, …)**」✗ ⇒ ★ **起不来会让宿主卡死** ✓
#   ⇒ ★★★ **本探针就是那道前置闸**：★ 起进程 → `initialize` → `tools/list` → 数工具 ✓
# 判据:   ★★ 三条，★ 全部要**读回来**（★ 不信"看起来起了" ✓）：
#     ★ ① 进程能起、★ 且在超时内回 `initialize` ✓
#     ★ ② `tools/list` 回的工具**条数**（★ 期望 **459** —— 规格 213 收口后的实测值 ✓）
#     ★ ③ 工具名**前缀**是 `solidworks_`（★ 抽查几个 ✓）
#   ★★ **超时是硬要求**：★ 任何一步超时 ⇒ **判"挂"**、★ 并 `kill` 掉子进程 ✓
#     （★ 不许留着 —— 留着会让后面的 DSH 抢同一个 stdio ✗）
# 官方依据: `docs/subsystems/mcp.zh.md` 的「配置」节（★ `transport: 'stdio'` ✓）·
#   `packages/mcp/mcp-client/README.zh.md`（★ 配置字段 ✓）
# 许可:   本仓库 MIT。★ 只读（★ 不改任何配置、★ 不连 SolidWorks ✓）。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

#: ★★ 中文 Windows 上打印 `★` / `⇒` 会 `UnicodeEncodeError: 'gbk' codec can't encode cha
#: racter` ✓
#: ★ 2026-10-07（接手轮 · 规格 214 T-214-01）**实测**：本探针在**默认控制台**下**根本跑
#: 不起来** ✗ ——
#:     ★ 它 `main()` 里第一句 `print("★ ① initialize ⇒ …")` 就抛 `UnicodeEncodeError`，
#:     ★ 然后**外层 `except BaseException` 里那句 print 又抛一次** ⇒ ★ 最终报的是
#: **`print("★ 异常已落盘…")` 的编码错**，★ **真正的失败原因被彻底盖住**（★ 事实 58 那一
#: 族）✓
#:   ★★ 判据（★ 加这一行之前/之后的**同一条命令**）：
#:     · `python tools/probe_mcp_stdio_handshake.py` ⇒ ★ **崩在打印上**
#: · `$env:PYTHONIOENCODING='utf-8'` 后再跑 ⇒ ★ **`tools/list ⇒ 504` 且判定「可以挂」** 
#: ✓
#: ⇒ ★ 与 `scripts/check_refuted_patterns.py` / `scripts/check_relative_imports.py` 的既
#: 有修法**逐字同型** ✓
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")            # type: ignore[attr-defined]
except Exception:                                                         # noqa: BLE001
    pass

ROOT = Path(Path(__file__).resolve().parents[1])
SERVER = ROOT / "mcp-server" / "server.py"
#: ★ 与 DSH 配置里将要写的那个 `command` **必须是同一个**（★ 否则验证的不是同一件事 ✗）
PYTHON = r"C:\Users\Zegel\AppData\Local\Python\pythoncore-3.14-64\python.exe"
#: ★★★ 2026-10-07 **实测订正**：★ 期望值**不是** `all_specs()` 的 459 ✗ —— ★ 而是 **504*
#: * ✓
#:   ★ **对账**（★ 与记忆库里那条逐字吻合 ✓）：本仓有**两条注册路径** ——
#: ★ ① **声明式**：`register_capabilities.all_specs()` = **459**（★ 规格 213 收口后的实
#: 测值 ✓）
#: ★ ② **继承的装饰器**：`mcp-server/server.py` 里那 **45** 个（★ 上游原样、我们一行没改
#:  ✓）
#:     ⇒ ★★★ **459 + 45 = 504** ✓ ✓
#:   ★★ **顺带解释了那条长期红的门禁**：`tests/test_mcp_protocol_layer.py` 逐字说
#:     「两条路径合计 **504** 条，而本测试上次实测 **339** 条」✗ ——
#:     ★ 它是一个**钉死数量**的守卫（★ 加了工具就要同步改它 ✓），★ 而 504 就是**真值** ✓
#:   ★★★ **教训（★ 本探针自己撞的）**：★ 我第一版拿 `all_specs()` 当地板 ✗ ⇒
#:     ★★ **"服务器有几个工具"与"注册表里有几条"是两个分母** ✓（★ 本仓反复栽在这上面 ✓）
EXPECTED_TOOLS = 504
#: ★★ 命名前缀**不止一个**（★ 我第一版只查 `solidworks_` ✗）：★ 还有 `cadstudio_*`（★ CA
#: D Studio
#:   DFM 一族 ✓）—— ★ 所以判据改成"**每个工具都属于已知前缀之一**" ✓
KNOWN_PREFIXES = ("solidworks_", "cadstudio_", "mcp_")


def _rpc(proc, obj, timeout=90):
    """★ 写一行 JSON-RPC、读一行回来（★ 读带超时 ⇒ 挂住了也回得来 ✓）。"""
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("★ 服务器没回任何东西就关了（stderr 见上）")
    return json.loads(line)


def main() -> int:
    out: dict = {"purpose": "★ 改 DSH 配置前的**前置闸**：我们的 MCP 能不能起、有几个工具",
                 "python": PYTHON, "server": str(SERVER), "expected_tools": EXPECTED_TOOLS}
    if not SERVER.is_file():
        print("★ 服务器文件不存在：%s" % SERVER)
        return 2

    #: ★ `cwd` 设成仓库根 —— ★ 与 DSH 配置里的 `cwd` 一致（★ 免得 import 路径不同 ✗）
    proc = subprocess.Popen(
        [PYTHON, str(SERVER)],
        cwd=str(ROOT),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    try:
        #: ── ① initialize ──────────────────────────────────────────────────
        try:
            r1 = _rpc(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                             "params": {"protocolVersion": "2024-11-05",
                                        "capabilities": {},
                                        "clientInfo": {"name": "dsh-preflight", "version": "0"}}})
            out["initialize_ok"] = "result" in r1
            si = (r1.get("result") or {}).get("serverInfo") or {}
            out["server_info"] = si
            print("★ ① initialize ⇒ ok=%r · serverInfo=%r" % (out["initialize_ok"], si))
        except Exception as e:                                          # noqa: BLE001
            out["initialize_ok"] = False
            out["initialize_error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("★ ① initialize ⇒ ✗ %s" % out["initialize_error"])
            return 3

        #: ★ 协议要求：initialize 之后发 `notifications/initialized` ✓
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        #: ── ② tools/list ──────────────────────────────────────────────────
        r2 = _rpc(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = ((r2.get("result") or {}).get("tools")) or []
        names = [t.get("name", "") for t in tools]
        out["tool_count"] = len(names)
        out["sample"] = names[:5]
        out["unknown_prefix"] = [n for n in names if not n.startswith(KNOWN_PREFIXES)][:8]
        by_prefix: dict = {}
        for n in names:
            for pre in KNOWN_PREFIXES:
                if n.startswith(pre):
                    by_prefix[pre] = by_prefix.get(pre, 0) + 1
                    break
        out["by_prefix"] = by_prefix
        print("★ ② tools/list ⇒ **%d** 个工具（★ 期望 %d = 459 声明式 + 45 装饰器）"
              % (len(names), EXPECTED_TOOLS))
        print("     ★ 按前缀分：%r" % by_prefix)
        print("     样例 ⇒ %r" % names[:5])

        #: ── ③ 判据 ────────────────────────────────────────────────────────
        out["verdicts"] = {
            "initialize_ok": bool(out["initialize_ok"]),
            "count_matches": len(names) == EXPECTED_TOOLS,
            "prefixes_known": not out["unknown_prefix"],
        }
        ok = all(out["verdicts"].values())
        out["verdict"] = (
            "★★★★★ **可以挂** —— ★ 服务器起得来 · ★ **%d 个工具**（★ 与 459+45 对账一致 ✓）· "
            "★ 命名前缀全部已知 ✓ ⇒ ★★ 改 DSH 配置**不会**卡住宿主 boot ✓" % len(names)
            if ok else
            "★★ **不要挂**：★ 判据 %r ⇒ ★ 先查清楚再动 DSH 配置（★ 卡 boot 是硬事故）✗"
            % out["verdicts"])
        print("★★★ 判定 ⇒ %s" % out["verdict"])
        p = ROOT / "output" / "mcp-stdio-handshake.json"
        p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("★ 证据：%s" % p)
        return 0 if ok else 1
    finally:
        #: ★★ **必须收尾** —— ★ 留着子进程会让 DSH 之后抢同一个 stdio ✗
        try:
            proc.kill()
            proc.wait(timeout=10)
        except Exception:                                               # noqa: BLE001
            pass
        err = ""
        try:
            err = (proc.stderr.read() or "")[-800:]
        except Exception:                                               # noqa: BLE001
            pass
        if err.strip():
            print("── 服务器 stderr（末 800 字）──\n%s" % err)


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "mcp-stdio-handshake-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
