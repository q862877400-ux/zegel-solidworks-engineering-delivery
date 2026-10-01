r"""@brief 端到端实测：**接线后的 MCP 工具真的能被调用吗**。

## 为什么这是缺口（我一直如实记着）
`docs/T-011-expose-capabilities-assessment.md` 里两次写着：
> ⚠ 接线本身未在本机跑 MCP 客户端

**⇒ 「工具出现在表里」与「工具能调通」是两件事。** 本探针补后者。

## ⚠⚠ 安全：**绝不启动第二个 MCP server**
AGENTS.md 已知事实 24：多个进程抢同一 COM 连接**会死锁**。
**⇒ 本探针**不启动 server、不起子进程**，而是：
1. `import server`（它会在 import 时注册 65 个工具 —— 但**不 `mcp.run()`**）；
2. 从 `FastMCP` 的工具表里**取出**某个工具的函数；
3. **在进程内直接调它**（与 MCP 客户端调用走的是**同一个函数对象**）。

**⇒ 这验证的是「注册出来的函数可用」，不验证 stdio 传输层** —— 后者由 `test_server_wiring.py`
的静态断言覆盖（工具数 / 命名 / 注入 / 描述）。**两层合起来才是完整证据。**

## 测什么
对**每个批次抽一条**（覆盖 `inject` 的三种取值），调它并检查返回：
* `solidworks_topology_evidence` —— `inject="sw_app"`，**只读**，最安全
* `solidworks_mold_evidence` —— `inject="model"`，只读
* `solidworks_sheet_metal_evidence` —— `inject="model"`，只读
**⇒ 本轮只调**只读**工具**（不建特征、不改模型）—— 实测纪律的第 3 条：收尾必做。**

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_wired_tools_e2e.py
# 定位:   T-011 的**最后一层验收**：`register_capabilities` 注册出来的函数**能不能调**。
# 官方签名依据: 不适用（调的是本仓库自己的工具函数）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只调只读工具**、不建特征、不改模型、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = r"C:\swprojects\sw-skill-fork"
MCP = REPO + r"\mcp-server"

# ⚠⚠ **必须先剔除脚本所在目录**：Python 把**脚本的目录**（不是 CWD）放在 `sys.path[0]`，
#   而本脚本在 `D:\AI\SW` —— 那里有一个 `mcp.py`（历史脚本）会**遮蔽真的 mcp 包**
#   ⇒ `from mcp.server.fastmcp import FastMCP` 报
#     `No module named 'mcp.server'; 'mcp' is not a package`。
#   **这个错误信息指向不了真因**（看不出是「被本地同名文件遮蔽」）。
#   ⇒ 已把这条做成可查项：`scripts/check_workspace_shadowing.py`。
_SCRIPT_DIR = str(Path(__file__).resolve().parent)
sys.path[:] = [q for q in sys.path if q and str(Path(q).resolve()) != _SCRIPT_DIR]
sys.path.insert(0, REPO)
sys.path.insert(0, MCP)
sys.path.insert(0, REPO + r"\scripts")
sys.stdout.reconfigure(encoding="utf-8")

#: 本轮要调的工具（**全部只读**）与其输入
TARGETS = (
    ("solidworks_topology_evidence", {}),
    ("solidworks_mold_evidence", {}),
    ("solidworks_sheet_metal_evidence", {}),
)


def tool_table(mcp):
    tm = getattr(mcp, "_tool_manager", None)
    if tm is None:
        return None
    return getattr(tm, "_tools", None) or getattr(tm, "tools", None)


def main() -> int:
    real_out = sys.stdout
    try:
        import server                     # noqa: F401 —— import 即注册，**不 run**
    finally:
        sys.stdout = real_out             # server 会劫持 stdout，复原
    print("  [0] import server 成功（**未启动 server**）")

    table = tool_table(server.mcp)
    if table is None:
        print("  ✗ 取不到工具表 ⇒ FastMCP 版本变了")
        return 2
    print("  [1] 工具表 %d 个" % len(table))

    # 先确认有一个活动文档（工具多数需要它）
    from scripts.sw_connect import connect_solidworks, new_document, get_com_member
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        print("  [2] 已新建参照文档 %r（只读工具需要它）" % title)

        print()
        print("=== 逐条调**只读**工具（与 MCP 客户端调用的是同一个函数对象）===")
        ok = fail = 0
        for name, payload in TARGETS:
            entry = table.get(name)
            if entry is None:
                print("  ✗ %-40s 不在工具表里" % name)
                fail += 1
                continue
            # ⚠ 用 `Tool.run(arguments)` —— 这是 FastMCP 里**最接近 MCP 客户端**的入口：
            #   它自己负责按 input schema 校参与构造输入模型，
            #   而直接调 `entry.fn(params)` 需要我先手搓那个 Pydantic 模型（第一版就卡在这）。
            try:
                import anyio
                # ⚠ 传参形状 = `{"params": {...}}`：
                #   本仓库（上游 45 个 + 我接线进来的）**全部**是
                #   `def tool(params: XxxInput)` ⇒ FastMCP 的 schema 是
                #   `{"properties": {"params": {...}}, "required": ["params"]}`。
                #   **第一版直接传 `{...}` ⇒ 校验错 `params Field required`。**
                #   ⇒ 已核实**两类工具同形**（`cadstudio_resolve_backend` 也一样），
                #     所以这是**调用方**的错，不是注册器的结构问题。
                out = anyio.run(entry.run, {"params": dict(payload)})
                text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False, default=str)
                mark = "✗" if '"isError": true' in text or text.startswith("Error") else "✓"
                if mark == "✓":
                    ok += 1
                else:
                    fail += 1
                print("  %s %-40s → %d 字符：%s" % (mark, name, len(text), text[:96].replace("\n", " ")))
            except Exception as exc:  # noqa: BLE001
                fail += 1
                print("  ✗ %-40s → %s: %s" % (name, type(exc).__name__, str(exc)[:80]))

        print()
        print("=== 结论 ===")
        print("  成功 %d / 失败 %d" % (ok, fail))
        print("  ⚠ 本探针验证的是**注册出来的函数可用**；stdio 传输层由")
        print("     `tests/test_server_wiring.py` 的静态断言覆盖。两层合起来才是完整证据。")
        print("  ⚠ 只调了**只读**工具（不建特征、不改模型）。")
    finally:
        try:
            if title:
                sw.CloseDoc(title)
                print("  [收尾] 文档已关闭（未保存）")
        except Exception:  # noqa: BLE001
            pass
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
