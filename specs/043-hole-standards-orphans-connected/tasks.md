# 043 · Tasks（全部完成，轮 124）

- [x] T-3901 确认 4 个包装是孤儿（把出参甩给调用方）
- [x] T-3902 ★ 先量：出参里装的是 `tuple`，两组各 15 元
- [x] T-3903 写 `_out_container` / `_out_value` / `_as_list` / `list_hole_standards`
- [x] T-3904 真机验证 ⇒ **15 条真实标准名**
  `→ 验收:` `python tools/verify_hole_standards_smoke.py`（**6/6**）
- [x] T-3905 冒烟脚本 + 6 条契约测试
  `→ 验收:` `python -m pytest tests/test_sw_hole_features.py -q`（**14 passed**）
- [x] T-3906 补两处来源块（测试文件 `覆盖: 全文件` + 模块新段另起一块）
- [x] T-3907 能力条目 + 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
