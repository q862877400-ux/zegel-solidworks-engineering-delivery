# 011 · 反向全景：我们有多少能力没暴露成 MCP 工具

**Status**: Implemented（轮 87）

## 背景
`010` 从「缺口那一侧」量了 339。本轮从**我们这一侧**量：`scripts/sw_*.py` 的公开函数里，
多少**没被任何工具引用**。那是最便宜的待办 —— 接出去就行。

## 判据
| ID | 判据 |
|---|---|
| SC-701 | `tools/probe_unexposed_functions.py` 可跑，输出三层分类 |
| SC-702 | 工具→函数的映射**三个来源都读**（`function=`/`module=` + `server.py` 的 `import`）|
| SC-703 | 调用者扫描**覆盖 5 个目录**（scripts/subskills/examples/mcp-server/tests）|
| SC-704 | 输出含**判据边界声明**（不判"该不该暴露"）|
| SC-705 | 门禁 + 回归不退化 |

## 明确不做
不判「该不该暴露成工具」（需人判，事实 53）。
