# 034 · Tasks（全部完成，轮 115）

- [x] T-3001 确认 `convert_entities` 没实现
- [x] T-3002 ★ 查废弃：`SketchUseEdge2` Obsolete ⇒ 取 `SketchUseEdge3`
- [x] T-3003 在 `scripts/sw_sketch_edit.py` 里加 `convert_entities`
- [x] T-3004 契约测试（**16 passed**，其中 6 条是本轮加的）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`
- [x] T-3005 扩 `sketch_edit_ops` 能力条目
- [x] T-3006 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
