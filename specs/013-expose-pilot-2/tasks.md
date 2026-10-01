# 013 · Tasks（全部完成，轮 93）

- [x] T-901 列出剩下 17 个 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-902 跳过 COM 辅助与需新解析器两类
- [x] T-903 写 `tool_specs_batch6.py`（3 条）
- [x] T-904 接入 `BATCH_MODULES` + 批次钉子 25→28 → `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`
- [x] T-905 契约测试 `tests/test_tool_specs_batch6.py`（**20 passed**）
- [x] T-906 ★ **真机冒烟** ⇒ **抓出第 4 个候选从没跑通过** ⇒ 剔除 + 立档
- [x] T-907 补 `verify_batch6_smoke.py` 的来源块（`check_provenance` 抓的）
- [x] T-908 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）
