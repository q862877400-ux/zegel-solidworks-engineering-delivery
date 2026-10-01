# 024 · Tasks（全部完成，轮 105）

- [x] T-2001 确认两条确实没实现
- [x] T-2002 两源取签名
- [x] T-2003 ★ 取枚举 ⇒ **发现两源冲突（-1 vs 1）** ⇒ 按铁律 4 取 **1**
- [x] T-2004 ★ 发现 `SketchChamfer` **已废弃** ⇒ 改走后继 `CreateChamfer`
- [x] T-2005 写 `scripts/sw_sketch_edit.py`
- [x] T-2006 契约测试 `tests/test_sw_sketch_edit_contract.py`（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`
- [x] T-2007 加能力条目（32 → **33**）
- [x] T-2008 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
