# 083 · Tasks（全部完成，轮 163）

- [x] T-8301 换题 + 第一版扫描判据**弃用**（121/125 假阳性）
- [x] T-8302 ★★★ 核 `sw_toolbox_index` 并**实跑取证**
  `→ 验收:` `python -c "import sw_toolbox_index as tb; print(len(tb.list_standards()), len(tb.load_index()['parts']))"`
  （**19 1844**）
- [x] T-8303 补条目 `standard_parts_toolbox`
- [x] T-8304 修 `source` 枚举 + 更新无人值守基线
  `→ 验收:` `python scripts/check_union_conventions.py`（exit 0）· `pytest tests/test_unattended_equivalence.py`（**7 passed**）
- [x] T-8305 事实 103
- [x] T-8306 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
