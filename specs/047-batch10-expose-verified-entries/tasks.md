# 047 · Tasks（全部完成，轮 128）

- [x] T-4301 查 MCP 层形态 + 确认 `inject` 支持 `sw_app`（**不新造机制**）
- [x] T-4302 写 `mcp-server/tool_specs_batch10.py`（4 条）
- [x] T-4303 注册进 `BATCH_MODULES`
  `→ 验收:` `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"`（**41**）
- [x] T-4304 守卫测试 `tests/test_tool_specs_batch10.py`（**16 passed**）
- [x] T-4305 ★★ 走声明层的真机冒烟 `tools/verify_batch10_smoke.py`
  `→ 验收:` `python tools/verify_batch10_smoke.py`（**7/7**）
- [x] T-4306 数量守卫测试同步（37 → **41**，保留历史说明）
- [x] T-4307 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
