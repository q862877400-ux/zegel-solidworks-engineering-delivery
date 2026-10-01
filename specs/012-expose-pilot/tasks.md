# 012 · Tasks（全部完成，轮 90）

- [x] T-801 从 308 里筛签名兼容的 ⇒ 22 个 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-802 挑 5 个只读/低风险
- [x] T-803 写 `mcp-server/tool_specs_batch5.py`
- [x] T-804 接入 `BATCH_MODULES` → `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-805 契约测试 `tests/test_tool_specs_batch5.py`（**18 passed**）
- [x] T-806 更新 `test_expected_batch_size` 20→25（那是它的设计意图）
- [x] T-807 重生成地图/digest + 同步报告数字
- [x] T-808 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）
