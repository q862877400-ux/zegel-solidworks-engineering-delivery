# 039 · Tasks（全部完成，轮 120）

- [x] T-3501 写 `tools/verify_gtol_smoke.py`
  `→ 验收:` `python tools/verify_gtol_smoke.py`（**3/5**）
- [x] T-3502 ★ 冒烟抓到 `add_gtol_indicator` **第一步就不通**
- [x] T-3503 ★ 补 `add_gtol_frame` / `ensure_gtol_frame` ⇒ **仍不通**
- [x] T-3504 ★ 查 `CanConvertFormat` / `ConvertFormat` ⇒ **转换成功但仍不通**
- [x] T-3505 ★ **按事实 53 停手**，如实分裂声明（源码头 / docstring / 能力条目 / 事实 66）
- [x] T-3506 更新测试（**16 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`
- [x] T-3507 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
