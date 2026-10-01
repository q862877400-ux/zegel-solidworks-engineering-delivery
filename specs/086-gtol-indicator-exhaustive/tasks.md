# 086 · Tasks（全部完成，轮 166）

- [x] T-8601 读 Remarks 找出取值限制（只允许 5 个 tol type）
- [x] T-8602 加清单校验（错值当场 `ValueError`）
- [x] T-8603 ★★★ 穷尽矩阵 `→ 验收:` `python tools/probe_gtol_indicator_matrix.py`（**20 组全 False**）
- [x] T-8604 拆出 `gtol_insert`（verified）
- [x] T-8605 改契约测试 `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`（**16 passed**）
- [x] T-8606 事实 106 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
