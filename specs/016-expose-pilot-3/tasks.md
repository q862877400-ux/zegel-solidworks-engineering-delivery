# 016 · Tasks（全部完成，轮 96）

- [x] T-1201 从剩余 7 个候选里筛出 3 个
- [x] T-1202 写 `tool_specs_batch7.py`
- [x] T-1203 接入 `BATCH_MODULES` + 钉子 28→31
  `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-1204 契约测试 `tests/test_tool_specs_batch7.py`（**20 passed**）
- [x] T-1205 真机冒烟 `tools/verify_batch7_smoke.py`（**4/4**）
  `→ 验收:` `python tools/verify_batch7_smoke.py`
- [x] T-1206 重生成地图/审计/digest + 同步报告数字
- [x] T-1207 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
