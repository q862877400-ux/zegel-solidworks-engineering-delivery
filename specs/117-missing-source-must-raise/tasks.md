# 117 · Tasks（全部完成，轮 197）

- [x] T-11701 ★★ 认出轮 196 的限度属"兜底填不知道"那一族（事实 113–116）
- [x] T-11702 ★★★ `_reflection_has` 缺源 ⇒ **抛**（写明「无从判定」）
- [x] T-11703 ★★ 加 `_require_reflection()` 便携性守卫（沿用既有写法）
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py -q`（**10 passed**）
- [x] T-11704 ★★★ 负例（抛 RuntimeError + 抛 Skipped）
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py::test_reflection_guard_never_turns_unknown_into_false -q`（**passed**）
- [x] T-11705 事实 137
- [x] T-11706 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1260 passed**
