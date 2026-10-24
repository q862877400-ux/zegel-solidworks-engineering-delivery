# J 维度 · 运行装配链现状

> 观测时间 **2026-10-24** · 观测方式：静态读 `mcp-server/server.py`、`scripts/sw_connect.py`、宿主 `mcp.json`（只读）
> **本次未启动 MCP 服务、未连 SolidWorks** —— 以下全部是静态读数，不是运行结果
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_runtime.py --json docs/state/inventory-j.json
> ```

---

### J-01 `server.py` 3,537 行；AST 里真装饰器 **45** 个

- **读数**：`mcp-server/server.py` **3,537 行** · `FastMCP` 出现 ✓ · `register_capabilities(` 调用 **1** 处
- **读数（装饰器）**：AST 统计「函数装饰器里含 `mcp.tool`」⇒ **45** 个（与正则 `@mcp.tool` 的 45 处一致）
- **证据**：`docs/state/inventory-j.json` 的 `server`
- **未确认**：这 45 个是否全部实际注册成功——未启动服务

### J-02 `tool_registry.py` 的 docstring 里写着 `server.py` 的行数，与实测不同

- **docstring 原文（逐字）**：`mcp-server/server.py` 现在 **2455 行 / 45 个 `@mcp.tool` / 46 个 `BaseInput` 类`
  （`mcp-server/tool_registry.py:4`）
- **实测**：`server.py` **3,537 行**；装饰器 **45** 个（与 docstring 一致）
- **未确认**：`BaseInput` 类的实际数量——未统计
- **未确认**：该 docstring 写于何时——未查 `git log -S'2455 行'`

### J-03 两条注册路径的规模：装饰器 45 + 声明式 501

| 路径 | 数量 | 证据 |
|---|---|---|
| `@mcp.tool` 装饰器（`server.py`）| **45** | AST 统计；正则同值 |
| `ToolSpec` 声明式（`register_capabilities`）| **501** | `docs/state/facts/B-tools.md` B-01 |

- **交叉核对**：`AGENTS.md` 记「工具 529（497 ToolSpec + 32 decorators）」⇒ 与实测两组数都不同
- **记录员注（陈述）**：若两路都注册成功，工具面合计 546；但 B-11 记录 `register()` 当前因 5 条问题**整体拒绝**注册
- **未确认**：装饰器路在 `register()` 拒绝时是否仍会注册——两条路的调用顺序未逐行读

### J-04 `scripts/sw_connect.py` 1,466 行：连接/护栏相关符号计数

| 符号 / 模式 | 出现次数 |
|---|---|
| `Mutex` / `mutex` / `SingleInstance` / `single_instance` | **3** |
| `CommandInProgress` | **2** |
| `timeout`（不区分大小写）| **5** |
| `Dispatch` | **7** |
| 定义 `def mm(`（单位换算边界）| **有** |

- **证据**：`inventory-j.json` 的 `sw_connect`
- **交叉核对**：`AGENTS.md` 铁律 2 要求「先置 `CommandInProgress = True`」「每个 COM 调用设超时」——本读数只统计出现次数，不判断是否覆盖每个调用
- **未确认**：上述计数是「文本出现次数」还是「有效调用点」——本次是纯文本计数

### J-05 仓库根**没有** `mcp.json`；`"solidworks": false` 在 DSH 宿主侧

- **读数**：`<仓库根>/mcp.json` **不存在**（`Test-Path` = False）
- **读数**：`$env:DSH_HOME/mcp.json` **存在**，其中 `"solidworks": false`（同文件另有 `openalex` / `context7` / `chrome-devtools` / `codebase-memory` 均 `true`）
- **证据**：`D:\Agent-Studio\Deepseek-Harness\DSH-Portable\home\mcp.json`
- **未确认**：该键的语义（是「禁用这个 MCP 服务」还是「未启用」）——未读 DSH 侧对该键的解释
- **记录员注（陈述）**：本仓库内不含 MCP 客户端配置；它与宿主的连接点在仓库之外

### J-06 两个运行期工具存在

- **读数**：`tools/sw_guard.py` **存在** · `tools/reclaim_solidworks.py` **存在**
- **交叉核对**：`AGENTS.md` §十五/§十九 把这两个作为真机命令的强制入口
- **未确认**：两者的实际行为——未运行

### J-07 `server.py` 里显式出现的 `*Hint` 只有 2 种

- **读数**：源码里出现的 `"...Hint"` 字符串：`destructive` · `idempotent`
- **交叉核对**：`ToolSpec` 字段里有 `read_only`（对应 `readOnlyHint`）；本读数未在 `server.py` 里找到 `readOnlyHint` 字面量
- **未确认**：`readOnlyHint` 是否由注册器侧（`tool_registry.build_input_model`）拼出——未读该函数全文

---

## 本节未覆盖（留给后续补充）

- 服务实际启动时的装配顺序与失败点（需运行，不在本次范围）
- `sw_connect.py` 的连接重试/回收策略
- 桌面端（`apps/`）与 MCP 服务的关系
- 45 个装饰器工具与 501 条声明之间是否有功能重叠（需按实现函数比对）
