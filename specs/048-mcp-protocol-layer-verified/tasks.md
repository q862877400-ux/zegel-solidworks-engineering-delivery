# 049 · Tasks（全部完成，轮 129）

- [x] T-4401 确认安全边界（不调工具 ⇒ 不碰 COM）
- [x] T-4402 写 `tools/verify_mcp_protocol_layer.py`
  `→ 验收:` `python tools/verify_mcp_protocol_layer.py`（**7/7**）
- [x] T-4403 ★ 打 schema 原文（`_dump_tool_schema.py`）⇒ 发现是**判据爬错层**
- [x] T-4404 修两层判据（`params.$ref` → `$defs.<Model>`；`response_format` 也是 `$ref`）
- [x] T-4405 固化成测试 `tests/test_mcp_protocol_layer.py`（**4 passed**）
- [x] T-4406 已知事实 72 入库（含 86 这个数）
- [x] T-4407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
