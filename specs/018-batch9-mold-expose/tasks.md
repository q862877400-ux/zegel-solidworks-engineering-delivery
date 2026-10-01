# 018 · Tasks（轮 98–99）

- [x] T-1401 查 `tooling_split` ⇒ 发现 `insert_core_cavity_solids` 已实现且有测试
- [x] T-1402 写 `tool_specs_batch9.py` → 接入（钉子 34→37）
- [x] T-1403 契约测试 `tests/test_tool_specs_batch9.py`
- [x] T-1404 ★ 真机冒烟 ⇒ **模态框卡住会话**（用户两次截图）
- [x] T-1405 ★ 改设计：冒烟改**前置条件感知**，那 2 个**一个都不调**
  `→ 验收:` `python tools/verify_batch9_smoke.py`（5/5，且**不弹框**）
- [x] T-1406 记录事实 64/65（`known-facts.md`）· 批次 7 三条 doc 加警告 · 清理临时件
- [x] T-1407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
