# 063 · Tasks（全部完成，轮 144）

- [x] T-5901 写结构审计 `tools/audit_get_com_member_semantics.py`
  `→ 验收:` `python tools/audit_get_com_member_semantics.py`
- [x] T-5902 ★★ 零参重载对照 ⇒ **471 / 193 / 24**
- [x] T-5903 ★★ **逐条读 8 处** ⇒ **改判**为「被依赖的特性」
- [x] T-5904 正式语义入 docstring + 危险面
- [x] T-5905 新增 `get_com_member_raw`（只取不调）+ 6 条测试
  `→ 验收:` `python -m pytest tests/test_get_com_member_semantics.py -q`（**6 passed**）
- [x] T-5906 ★ **就地更正事实 84** + 已知事实 85
- [x] T-5907 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
