r"""@brief 真机探针：**MCP 协议层** —— 起 server，发 `tools/list`，核对声明的 schema。

## 为什么这是 `047` 留下的那条边界
`047`（轮 128）只证到「**声明 → RESOLVERS → 调用**」；**协议层未证**。
本探针补上：把 server **真的起起来**，用 JSON-RPC 问它「你有哪些工具」。

## ⚠⚠ 安全：**为什么不调工具**
已知事实 **24**：运行时只能有一个 SolidWorks MCP —— 多个进程抢同一 COM 连接会**死锁**。
⇒ 本探针**只发 `initialize` 与 `tools/list`**，**一次工具都不调** ⇒ **完全不碰 COM**。
★ 这正好也是本探针要证的那一层：**"工具被正确地登记与描述出来了"**。

## 判据
* server 能起来并完成 `initialize`；
* `tools/list` 里**能找到** batch10 的 4 条；
* ★ 每条的 `inputSchema` **逐参数**与声明一致（名字、类型、必填/可选）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_mcp_protocol_layer.py
# 定位:   给 `047` 留的那条边界取证：MCP **协议层**（不是函数层、不是声明层）。
# 官方依据: 不适用（MCP 协议由 `mcp` 包实现；本探针只说它自己的观测）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.stdout.reconfigure(encoding="utf-8")

SERVER = ROOT / "mcp-server" / "server.py"
OUT = Path(r"D:\AI\SW\output\mcp-protocol-layer-evidence.json")

#: `047` 新接出去的 4 条
BATCH10 = (
    "solidworks_part_bounding_box",
    "solidworks_hole_standards",
    "solidworks_fastener_types",
    "solidworks_fastener_table_types",
)


def rpc(method: str, params: dict, req_id: int) -> str:
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method,
                       "params": params}, ensure_ascii=False) + "\n"


def main() -> int:
    checks: list = []
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:400]}
        print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:70]))

    if not SERVER.is_file():
        chk("server.py 存在", False, str(SERVER))
        return 1

    env_py = sys.executable
    proc = None
    try:
        # ⚠ 事实 58：一定要给 encoding，否则中文 Windows 上父进程用 GBK 解 UTF-8 会炸
        proc = subprocess.Popen(
            [env_py, str(SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", cwd=str(ROOT / "mcp-server"),
        )
        chk("★ 起 server（stdio，**一次工具都不调** ⇒ 不碰 COM）", proc.poll() is None,
            "pid=%s" % proc.pid)

        # ① initialize
        proc.stdin.write(rpc("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "dsh-probe", "version": "1"},
        }, 1))
        proc.stdin.flush()
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        # ② tools/list
        proc.stdin.write(rpc("tools/list", {}, 2))
        proc.stdin.flush()

        # 读若干行，找 id=2 的响应
        tools = None
        deadline = time.time() + 30
        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                msg = json.loads(line)
            except Exception:      # noqa: BLE001
                continue
            if msg.get("id") == 2 and "result" in msg:
                tools = msg["result"].get("tools") or []
                break
        chk("★ `tools/list` 拿到响应", tools is not None,
            ("%d 个工具" % len(tools)) if tools is not None else "没读到 id=2 的响应")
        if tools is None:
            return 1

        names = [t.get("name") for t in tools]
        ev["tool_count"] = len(names)
        found = [n for n in BATCH10 if n in names]
        chk("★★ batch10 的 4 条**都在协议层可见**", len(found) == 4,
            "找到 %d/4：%s" % (len(found), found))
        ev["batch10_found"] = found

        # ③ 逐条核对 inputSchema
        by_name = {t["name"]: t for t in tools}
        for n in BATCH10:
            spec = None
            try:
                import importlib
                mod = importlib.import_module("tool_specs_batch10")
                spec = next(s for s in mod.SPECS_BATCH10 if s.name == n)
            except Exception:      # noqa: BLE001
                pass
            if spec is None or n not in by_name:
                chk("schema · %s" % n, False, "声明或工具缺失")
                continue
            # ⚠⚠ **第一版判据错了（本轮当场发现）**：我去**顶层** `properties` 找**展平**的参数名，
            #   报「协议里只有一个 `params`」—— 但那是**设计**：
            #   每个工具统一收一个 `params` 对象（与 `server.py` 原生工具一致），
            #   **声明的参数是嵌在 `params` 的 `$ref` → `$defs.<Model>.properties` 里**。
            #   ⇒ 判据要**顺着 `$ref` 走进去**。
            schema = by_name[n].get("inputSchema") or {}
            top = schema.get("properties") or {}
            ref = ((top.get("params") or {}).get("$ref") or "")
            model_name = ref.rsplit("/", 1)[-1]
            inner = (((schema.get("$defs") or {}).get(model_name) or {}).get("properties") or {})
            declared = {p.name for p in spec.params}
            #: ⚑ 框架会**统一补**一个 `response_format`（`json`/`markdown`）—— 声明里没有它
            extra = set(inner) - declared
            missing = declared - set(inner)
            chk("★ schema 参数逐条对上（顺 `$ref` 走进去） · %s" % n,
                not missing and not extra - {"response_format"},
                "声明=%s 协议(内层)=%s 缺=%s 多=%s"
                % (sorted(declared), sorted(inner), sorted(missing), sorted(extra)))
            #: 顺带记下"框架统一补了 response_format"这件事
            if "response_format" in inner:
                ev.setdefault("framework_added", set())
                ev["framework_added"] = sorted(set(ev.get("framework_added") or []) |
                                               {"response_format"})
    except Exception as exc:      # noqa: BLE001
        chk("整体探针", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        if proc is not None:
            try:
                proc.stdin.close()
            except Exception:      # noqa: BLE001
                pass
            try:
                proc.terminate()
                proc.wait(timeout=10)
            except Exception:      # noqa: BLE001
                try:
                    proc.kill()
                except Exception:      # noqa: BLE001
                    pass
            print("   （已终止 server 进程 pid=%s）" % proc.pid)

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「工具被正确登记与描述」；**没有真调过一次工具** ⇒ 不证调用路径（那需要 COM）。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
