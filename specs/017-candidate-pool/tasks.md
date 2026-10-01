# 017 · Tasks（全部完成，轮 97）

- [x] T-1301 查 `collect_model_summary` 为什么没进候选
  ⇒ **只被测试调用**，被两个口径同时排除
- [x] T-1302 写 `tools/probe_testonly_candidates.py` ⇒ 池 C **12 个**
  `→ 验收:` `python tools/probe_testonly_candidates.py`
- [x] T-1303 写 `tools/probe_expose_candidates.py`（池 B，13 个，作对照）
  `→ 验收:` `python tools/probe_expose_candidates.py`
- [x] T-1304 写 `tool_specs_batch8.py`（3 条）→ 接入（钉子 31→34）
- [x] T-1305 契约测试 `tests/test_tool_specs_batch8.py`（**20 passed**）
- [x] T-1306 真机冒烟 `tools/verify_batch8_smoke.py`（**4/4**，特征树 **18 个特征**）
- [x] T-1307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
