# 057 · Tasks（全部完成，轮 138）

- [x] T-5301 写 `tools/probe_server_dispatch_wiring.py`
  `→ 验收:` `python tools/probe_server_dispatch_wiring.py`（45 / 86 / 双向）
- [x] T-5302 ★★ 量第 4 个方向：**两条路径之间重名** ⇒ 0，但**此前无人检查**
- [x] T-5303 补 4 条结构判据进 `tests/test_mcp_protocol_layer.py`
  `→ 验收:` `python -m pytest tests/test_mcp_protocol_layer.py -q`（**8 passed**）
- [x] T-5304 ★★★ 故障注入 ⇒ 查出**"套 fixture 导致故障时静默 skip"** ⇒ 修（去掉 fixture）
- [x] T-5305 ★ 修完再注入（注**对**名字）⇒ **1 failed** ⇒ 复原 2 passed
- [x] T-5306 文档（并入 `docs/dead-guards.md`）+ 已知事实 79
- [x] T-5307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
