# 025 · Tasks（全部完成，轮 106）

- [x] T-2101 写 `scripts/check_enum_values_vs_reflection.py`
- [x] T-2102 ★ 首跑即发现**自己的正则漏了带尾注的行** ⇒ 修
  `→ 验收:` `python scripts/check_enum_values_vs_reflection.py`
- [x] T-2103 重构出 `compare()`（为负例可测）
- [x] T-2104 负例测试 `tests/test_enum_values_gate.py`（**8 passed**）
  `→ 验收:` `python -m pytest tests/test_enum_values_gate.py -q`
- [x] T-2105 接进 `release_check.py`（硬门禁）
- [x] T-2106 登记 `docs/gate-classification.json`
  `→ 验收:` `python scripts/check_gate_wiring.py`（**16 个门禁全部已接线**）
- [x] T-2107 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
